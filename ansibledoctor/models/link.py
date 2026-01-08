"""
Link models for documentation cross-references.

Provides data models for links, link types, and link validation status.

Spec: 013-links-cross-references
"""

import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class LinkType(str, Enum):
    """Types of links in documentation."""

    INTERNAL_FILE = "internal_file"  # Link to another doc file
    INTERNAL_SECTION = "internal_section"  # Anchor link within same file
    CROSS_REFERENCE = "cross_reference"  # Link to related content
    EXTERNAL_URL = "external_url"  # External HTTP/HTTPS link
    RELATIVE_PATH = "relative_path"  # Relative file path
    ABSOLUTE_PATH = "absolute_path"  # Absolute file path


class LinkStatus(str, Enum):
    """Link validation status."""

    VALID = "valid"  # Link target exists and is reachable
    BROKEN = "broken"  # Link target not found (404, file missing)
    REDIRECT = "redirect"  # Link redirects to another URL (3xx)
    TIMEOUT = "timeout"  # Link validation timed out
    INVALID_SYNTAX = "invalid_syntax"  # Malformed link syntax
    NOT_CHECKED = "not_checked"  # Link not yet validated


class Link(BaseModel):
    """
    Represents a link in documentation.

    Attributes:
        source_file: File containing the link
        target: Link target (URL, file path, or anchor)
        link_type: Type of link (internal/external/section/cross-ref)
        text: Link text/title (display text)
        line_number: Line number in source file (for error reporting)
        status: Current validation status
        http_status: HTTP status code for external links (200, 404, etc.)
        redirect_url: Final URL after redirects (if status=REDIRECT)
        error_message: Error message if broken
        last_checked: Last validation timestamp

    Examples:
        >>> link = Link(
        ...     source_file=Path("/docs/index.md"),
        ...     target="../roles/demo.md",
        ...     link_type=LinkType.RELATIVE_PATH,
        ...     text="Demo Role",
        ...     line_number=42
        ... )
        >>> link.is_internal
        True
        >>> link.is_external
        False
    """

    source_file: Path = Field(description="File containing the link")
    target: str = Field(description="Link target (URL, file path, or anchor)")
    link_type: LinkType = Field(description="Type of link")
    text: str | None = Field(default=None, description="Link text/title")
    line_number: int | None = Field(default=None, ge=1, description="Line number in source file")
    status: LinkStatus = Field(default=LinkStatus.NOT_CHECKED, description="Validation status")
    http_status: int | None = Field(default=None, ge=100, le=599, description="HTTP status code")
    redirect_url: str | None = Field(default=None, description="Final URL after redirects")
    error_message: str | None = Field(default=None, description="Error message if broken")
    last_checked: datetime | None = Field(default=None, description="Last validation timestamp")

    @property
    def is_valid(self) -> bool:
        """Check if link is valid."""
        return self.status == LinkStatus.VALID

    @property
    def is_external(self) -> bool:
        """Check if link is external (HTTP/HTTPS)."""
        return self.link_type == LinkType.EXTERNAL_URL

    @property
    def is_internal(self) -> bool:
        """Check if link is internal (file or section)."""
        return self.link_type in (
            LinkType.INTERNAL_FILE,
            LinkType.INTERNAL_SECTION,
            LinkType.RELATIVE_PATH,
            LinkType.ABSOLUTE_PATH,
        )

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        """Validate target is not empty."""
        if not v or not v.strip():
            msg = "Link target cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("source_file")
    @classmethod
    def validate_source_file(cls, v: Path) -> Path:
        """Ensure source_file is absolute path."""
        if not v.is_absolute():
            msg = f"source_file must be absolute path, got: {v}"
            raise ValueError(msg)
        return v

    @classmethod
    def from_markdown(cls, source: Path, match: re.Match[str], line_number: int) -> "Link":
        """
        Parse link from Markdown regex match.

        Args:
            source: Source file path
            match: Regex match object from pattern `[text](url)`
            line_number: Line number in source file

        Returns:
            Link instance

        Example:
            >>> import re
            >>> pattern = r'\\[([^\\]]+)\\]\\(([^\\)]+)\\)'
            >>> text = '[Guide](../roles/demo.md)'
            >>> match = re.search(pattern, text)
            >>> if match:
            ...     link = Link.from_markdown(Path('/docs/index.md'), match, 42)
            ...     print(link.text, link.target)
            Guide ../roles/demo.md
        """
        text = match.group(1)
        target = match.group(2)
        link_type = cls._infer_link_type(target)

        return cls(
            source_file=source.resolve(),
            target=target,
            link_type=link_type,
            text=text,
            line_number=line_number,
        )

    @classmethod
    def from_html(cls, source: Path, element: Any, line_number: int | None) -> "Link":
        """
        Parse link from HTML anchor element.

        Args:
            source: Source file path
            element: BeautifulSoup anchor element (<a href="...">)
            line_number: Line number in source file

        Returns:
            Link instance
        """
        target = element.get("href", "")
        text = element.get_text(strip=True) or None
        link_type = cls._infer_link_type(target)

        return cls(
            source_file=source.resolve(),
            target=target,
            link_type=link_type,
            text=text,
            line_number=line_number,
        )

    @staticmethod
    def _infer_link_type(target: str) -> LinkType:
        """Infer link type from target string."""
        if target.startswith(("http://", "https://")):
            return LinkType.EXTERNAL_URL
        if target.startswith("#"):
            return LinkType.INTERNAL_SECTION
        if target.startswith("/"):
            return LinkType.ABSOLUTE_PATH
        return LinkType.RELATIVE_PATH

    def resolve_target_path(self, base_dir: Path | None = None) -> Path | None:
        """
        Resolve relative link target to absolute path.

        Args:
            base_dir: Base directory for relative path resolution (optional)

        Returns:
            Absolute path or None if external link
        """
        if self.is_external:
            return None

        if self.link_type == LinkType.ABSOLUTE_PATH:
            return Path(self.target.lstrip("/"))

        # Remove anchor from target (e.g., "file.md#section" → "file.md")
        target_clean = self.target.split("#")[0]

        # Resolve relative to source file's parent directory
        source_dir = self.source_file.parent
        target_path = (source_dir / target_clean).resolve()

        return target_path

    def extract_anchor(self) -> str | None:
        """
        Extract anchor from link target.

        Returns:
            Anchor string (without #) or None if no anchor

        Examples:
            >>> link = Link(
            ...     source_file=Path("/docs/index.md"),
            ...     target="file.md#section",
            ...     link_type=LinkType.RELATIVE_PATH
            ... )
            >>> link.extract_anchor()
            'section'
        """
        if "#" not in self.target:
            return None
        return self.target.split("#", 1)[1]
