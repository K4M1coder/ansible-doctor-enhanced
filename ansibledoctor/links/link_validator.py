"""
Link validation for Ansible Doctor documentation.

Validates internal file links, section anchors, and external HTTP links.
Part of Spec 013 User Story 2 (Detect Broken Links).

Architecture:
- Library-First: Pure Python validation logic separate from CLI
- Validation results use LinkStatus enum from ansibledoctor.models.link
- External link validation uses requests library with timeout/retry
- Caching prevents duplicate external link checks (in-memory + persistent)
- Anchor validation parses Markdown headers

Spec: 013-links-cross-references
Phase: 4 (User Story 2 - Detect Broken Links)
Tasks: T035-T039, T043
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from ansibledoctor.models.link import Link, LinkStatus, LinkType
from ansibledoctor.utils.logging import get_logger


logger = get_logger(__name__)


class ValidationResult:
    """Result of link validation."""

    def __init__(
        self,
        link: Link,
        is_valid: bool,
        status: LinkStatus,
        error_message: str | None = None,
        resolved_path: Path | None = None,
    ) -> None:
        """Initialize validation result.
        
        Args:
            link: The link that was validated
            is_valid: Whether validation passed
            status: Link status (VALID, BROKEN, WARNING)
            error_message: Error message if validation failed
            resolved_path: Resolved absolute path for internal links
        """
        self.link = link
        self.is_valid = is_valid
        self.status = status
        self.error_message = error_message
        self.resolved_path = resolved_path
        self.source_file = link.source_file
        self.line_number = link.line_number

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ValidationResult(is_valid={self.is_valid}, "
            f"status={self.status}, "
            f"error='{self.error_message}')"
        )


class LinkValidator:
    """Validates documentation links.
    
    Features:
    - Internal file link validation (checks file existence)
    - Section anchor validation (parses headers from target file)
    - External HTTP link validation (HEAD requests with timeout/retry)
    - Caching for external links (avoid duplicate checks)
    - Configurable timeout and retry behavior
    
    Example:
        >>> validator = LinkValidator(base_path=Path("/docs"))
        >>> result = validator.validate(link)
        >>> if not result.is_valid:
        ...     print(f"Broken: {result.error_message}")
    """

    def __init__(
        self,
        base_path: Path,
        timeout: float = 5.0,
        max_retries: int = 3,
        enable_cache: bool = True,
        cache_file: Path | None = None,
        cache_ttl: int = 86400,  # 24 hours in seconds
    ) -> None:
        """Initialize link validator.
        
        Args:
            base_path: Base directory for resolving relative paths
            timeout: HTTP request timeout in seconds
            max_retries: Maximum retry attempts for external links
            enable_cache: Whether to cache external link validation results
            cache_file: Path to persistent cache file (default: .ansibledoctor-link-cache.json)
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        self.base_path = base_path
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        
        # Set default cache file location
        if cache_file is None:
            cache_file = base_path / ".ansibledoctor-link-cache.json"
        self.cache_file = cache_file
        
        # In-memory cache
        self._external_cache: dict[str, ValidationResult] = {}
        
        # Load persistent cache
        if enable_cache:
            self._load_cache()

    def validate(self, link: Link) -> ValidationResult:
        """Validate a link.
        
        Args:
            link: The link to validate
            
        Returns:
            ValidationResult with status and error details
        """
        # Route to appropriate validator based on link type
        if link.link_type == LinkType.EXTERNAL_URL:
            return self._validate_external(link)
        elif link.link_type == LinkType.INTERNAL_SECTION:
            return self._validate_section_anchor(link)
        else:
            # RELATIVE_PATH, ABSOLUTE_PATH, INTERNAL_FILE, CROSS_REFERENCE
            return self._validate_internal_file(link)

    def _validate_internal_file(self, link: Link) -> ValidationResult:
        """Validate internal file link (T036).
        
        Checks if target file exists, resolving relative paths from source file.
        
        Args:
            link: Link with internal file target
            
        Returns:
            ValidationResult indicating if file exists
        """
        try:
            # Resolve target path
            if link.link_type == LinkType.ABSOLUTE_PATH:
                target_path = Path(link.target)
            else:
                # Relative path - resolve from source file's directory
                source_dir = link.source_file.parent
                target_path = (source_dir / link.target).resolve()

            # Check if file exists
            if not target_path.exists():
                return ValidationResult(
                    link=link,
                    is_valid=False,
                    status=LinkStatus.BROKEN,
                    error_message=f"Target file not found: {target_path}",
                )

            # Check if it's a file (not directory)
            if not target_path.is_file():
                return ValidationResult(
                    link=link,
                    is_valid=False,
                    status=LinkStatus.BROKEN,
                    error_message=f"Target is not a file: {target_path}",
                )

            return ValidationResult(
                link=link,
                is_valid=True,
                status=LinkStatus.VALID,
                resolved_path=target_path,
            )

        except Exception as e:
            return ValidationResult(
                link=link,
                is_valid=False,
                status=LinkStatus.BROKEN,
                error_message=f"Error resolving path: {e}",
            )

    def _validate_section_anchor(self, link: Link) -> ValidationResult:
        """Validate section anchor link (T037).
        
        Parses target Markdown file to extract headers and verify anchor exists.
        
        Args:
            link: Link with section anchor (e.g., "file.md#section")
            
        Returns:
            ValidationResult indicating if anchor exists in target file
        """
        try:
            # Split target into file and anchor
            target_parts = link.target.split("#", 1)
            if len(target_parts) != 2:
                return ValidationResult(
                    link=link,
                    is_valid=False,
                    status=LinkStatus.BROKEN,
                    error_message="Invalid anchor format (missing #)",
                )

            file_part, anchor = target_parts

            # Resolve file path
            source_dir = link.source_file.parent
            if file_part:
                target_path = (source_dir / file_part).resolve()
            else:
                # Same-file anchor (e.g., "#section")
                target_path = link.source_file

            # Check if file exists
            if not target_path.exists():
                return ValidationResult(
                    link=link,
                    is_valid=False,
                    status=LinkStatus.BROKEN,
                    error_message=f"Target file not found: {target_path}",
                )

            # Extract anchors from file
            anchors = self._extract_markdown_anchors(target_path)

            # Normalize anchor (GitHub style: lowercase, spaces to hyphens)
            normalized_anchor = anchor.lower().replace(" ", "-")

            if normalized_anchor not in anchors:
                return ValidationResult(
                    link=link,
                    is_valid=False,
                    status=LinkStatus.BROKEN,
                    error_message=f"Anchor not found: #{anchor}",
                )

            return ValidationResult(
                link=link,
                is_valid=True,
                status=LinkStatus.VALID,
                resolved_path=target_path,
            )

        except Exception as e:
            return ValidationResult(
                link=link,
                is_valid=False,
                status=LinkStatus.BROKEN,
                error_message=f"Error validating anchor: {e}",
            )

    def _extract_markdown_anchors(self, file_path: Path) -> set[str]:
        """Extract anchor IDs from Markdown headers.
        
        Converts headers like "## My Section" to anchor "my-section".
        Follows GitHub Markdown anchor generation rules.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            Set of anchor IDs found in file
        """
        anchors = set()

        try:
            content = file_path.read_text(encoding="utf-8")

            # Find Markdown headers (# Header, ## Header, etc.)
            header_pattern = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
            for match in header_pattern.finditer(content):
                header_text = match.group(1).strip()

                # Convert to anchor ID (GitHub style)
                # 1. Lowercase
                # 2. Remove special chars except hyphens
                # 3. Replace spaces with hyphens
                anchor = header_text.lower()
                anchor = re.sub(r"[^\w\s-]", "", anchor)
                anchor = re.sub(r"\s+", "-", anchor)
                anchor = re.sub(r"-+", "-", anchor)  # Collapse multiple hyphens
                anchor = anchor.strip("-")

                anchors.add(anchor)

        except Exception as e:
            logger.warning(f"Failed to extract anchors from {file_path}: {e}")

        return anchors

    def _validate_external(self, link: Link) -> ValidationResult:
        """Validate external HTTP link (T038-T039).
        
        Makes HEAD request to check if URL is accessible.
        Includes retry logic for transient failures and caching for performance.
        
        Args:
            link: Link with external HTTP/HTTPS URL
            
        Returns:
            ValidationResult with HTTP status information
        """
        url = link.target

        # Check cache first
        if self.enable_cache and url in self._external_cache:
            cached_result = self._external_cache[url]
            # Return new result with current link's metadata
            return ValidationResult(
                link=link,
                is_valid=cached_result.is_valid,
                status=cached_result.status,
                error_message=cached_result.error_message,
            )

        # Validate with retry logic
        result = self._validate_external_with_retry(link, url)

        # Cache result
        if self.enable_cache:
            self._external_cache[url] = result

        return result

    def _validate_external_with_retry(self, link: Link, url: str) -> ValidationResult:
        """Validate external URL with exponential backoff retry.
        
        Args:
            link: Link object
            url: URL to validate
            
        Returns:
            ValidationResult
        """
        last_error = None
        backoff = 0.5  # Start with 0.5 second delay

        for attempt in range(self.max_retries):
            try:
                # Make HEAD request (lighter than GET)
                response = requests.head(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    headers={"User-Agent": "ansible-doctor/link-validator"},
                )

                # Check status
                if response.ok:
                    return ValidationResult(
                        link=link,
                        is_valid=True,
                        status=LinkStatus.VALID,
                    )
                else:
                    return ValidationResult(
                        link=link,
                        is_valid=False,
                        status=LinkStatus.BROKEN,
                        error_message=f"HTTP {response.status_code}: {url}",
                    )

            except Timeout as e:
                last_error = f"Connection timeout: {url}"
                logger.debug(f"Timeout on attempt {attempt + 1}/{self.max_retries}: {url}")

            except ConnectionError as e:
                last_error = f"Connection failed: {url}"
                logger.debug(f"Connection error on attempt {attempt + 1}/{self.max_retries}: {url}")

            except RequestException as e:
                last_error = f"Request failed: {e}"
                logger.debug(f"Request exception on attempt {attempt + 1}/{self.max_retries}: {url}")

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                time.sleep(backoff)
                backoff *= 2  # Double the delay for next attempt

        # All retries failed
        return ValidationResult(
            link=link,
            is_valid=False,
            status=LinkStatus.TIMEOUT,  # TIMEOUT for network issues vs BROKEN for 404
            error_message=last_error or f"Failed to validate: {url}",
        )
    def _load_cache(self) -> None:
        """Load persistent cache from disk (T043).
        
        Loads cached external link validation results from JSON file.
        Validates cache entries against TTL and removes expired entries.
        """
        if not self.cache_file.exists():
            logger.debug(f"Cache file not found: {self.cache_file}")
            return
        
        try:
            cache_data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            now = datetime.now()
            
            for url, entry in cache_data.items():
                # Check if entry is expired
                checked_at = datetime.fromisoformat(entry["checked_at"])
                age = (now - checked_at).total_seconds()
                
                if age < self.cache_ttl:
                    # Reconstruct ValidationResult from cache
                    # Note: We don't have the original Link object, so create a dummy one
                    dummy_link = Link(
                        source_file=Path(entry["source_file"]),
                        target=url,
                        link_type=LinkType.EXTERNAL_URL,
                    )
                    
                    result = ValidationResult(
                        link=dummy_link,
                        is_valid=entry["is_valid"],
                        status=LinkStatus(entry["status"]),
                        error_message=entry.get("error_message"),
                    )
                    
                    self._external_cache[url] = result
                    logger.debug(f"Loaded cached result for: {url} (age: {age:.0f}s)")
                else:
                    logger.debug(f"Expired cache entry for: {url} (age: {age:.0f}s)")
            
            logger.info(f"Loaded {len(self._external_cache)} cached link validations")
        
        except Exception as e:
            logger.warning(f"Failed to load cache file: {e}")
            self._external_cache = {}

    def save_cache(self) -> None:
        """Save persistent cache to disk (T043).
        
        Writes external link validation results to JSON file for reuse
        across multiple validation runs.
        """
        if not self.enable_cache or not self._external_cache:
            return
        
        try:
            cache_data = {}
            now = datetime.now()
            
            for url, result in self._external_cache.items():
                cache_data[url] = {
                    "url": url,
                    "is_valid": result.is_valid,
                    "status": result.status.value,
                    "error_message": result.error_message,
                    "source_file": str(result.source_file),
                    "checked_at": now.isoformat(),
                }
            
            self.cache_file.write_text(
                json.dumps(cache_data, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Saved {len(cache_data)} link validations to cache: {self.cache_file}")
        
        except Exception as e:
            logger.warning(f"Failed to save cache file: {e}")

    def clear_cache(self) -> None:
        """Clear all cached validation results (T043).
        
        Removes both in-memory cache and persistent cache file.
        Useful for forcing fresh validation of all links.
        """
        self._external_cache = {}
        
        if self.cache_file.exists():
            try:
                self.cache_file.unlink()
                logger.info(f"Cleared cache file: {self.cache_file}")
            except Exception as e:
                logger.warning(f"Failed to clear cache file: {e}")