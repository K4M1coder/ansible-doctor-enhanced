"""
Integration tests for external link validation.

Tests HTTP link validation including 404 detection, timeouts, and network errors.
Following TDD approach - these tests should fail until LinkValidator external validation is implemented.

Spec: 013-links-cross-references
Phase: 4 (User Story 2 - Detect Broken Links)
Task: T033
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ansibledoctor.models.link import Link, LinkStatus, LinkType


class TestExternalLinkValidation:
    """Tests for external HTTP link validation (T033)."""

    def test_external_404_shows_warning_with_http_status(self, tmp_path: Path) -> None:
        """Test that external 404 links show warning with HTTP status code.
        
        Scenario:
            - Documentation contains link to external URL
            - URL returns 404 Not Found
            - Warning shows HTTP status code
        """
        source_file = tmp_path / "README.md"
        source_file.write_text("See [docs](https://example.com/missing).")
        
        link = Link(
            source_file=source_file,
            target="https://example.com/missing",
            link_type=LinkType.EXTERNAL_URL,
            text="docs",
            line_number=1,
        )
        
        # Mock HTTP response to return 404
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.ok = False
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.BROKEN
            assert "404" in result.error_message
    
    def test_external_link_timeout(self, tmp_path: Path) -> None:
        """Test that external link timeouts are handled gracefully."""
        from requests.exceptions import Timeout
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://slow-site.example.com",
            link_type=LinkType.EXTERNAL_URL,
            text="slow site",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_head.side_effect = Timeout("Connection timeout")
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, timeout=2.0)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.WARNING
            assert "timeout" in result.error_message.lower()
    
    def test_external_link_connection_error(self, tmp_path: Path) -> None:
        """Test that connection errors are handled."""
        from requests.exceptions import ConnectionError
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://nonexistent-domain-12345.com",
            link_type=LinkType.EXTERNAL_URL,
            text="missing",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_head.side_effect = ConnectionError("Failed to connect")
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert not result.is_valid
            assert result.status == LinkStatus.WARNING
            assert "connection" in result.error_message.lower() or "failed" in result.error_message.lower()
    
    def test_valid_external_link(self, tmp_path: Path) -> None:
        """Test that valid external links pass validation."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://www.ansible.com",
            link_type=LinkType.EXTERNAL_URL,
            text="Ansible",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            assert result.is_valid
            assert result.status == LinkStatus.VALID
            assert result.error_message is None
    
    def test_external_link_redirect_followed(self, tmp_path: Path) -> None:
        """Test that HTTP redirects (301/302) are followed."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://example.com/old-url",
            link_type=LinkType.EXTERNAL_URL,
            text="redirected",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            # First response is redirect
            mock_response = Mock()
            mock_response.status_code = 301
            mock_response.ok = True
            mock_response.headers = {"Location": "https://example.com/new-url"}
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            # Should be valid since redirect is followed
            assert result.is_valid
            assert result.status == LinkStatus.VALID
    
    def test_external_link_with_custom_user_agent(self, tmp_path: Path) -> None:
        """Test that custom user agent is sent with requests."""
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://example.com/docs",
            link_type=LinkType.EXTERNAL_URL,
            text="docs",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path)
            
            result = validator.validate(link)
            
            # Verify user agent was set
            mock_head.assert_called_once()
            call_kwargs = mock_head.call_args[1]
            assert "headers" in call_kwargs
            assert "User-Agent" in call_kwargs["headers"]
            assert "ansible-doctor" in call_kwargs["headers"]["User-Agent"].lower()


class TestExternalLinkBatchValidation:
    """Tests for batch validation of external links."""

    def test_batch_validation_with_caching(self, tmp_path: Path) -> None:
        """Test that duplicate external links are only validated once.
        
        Scenario:
            - Multiple files link to same external URL
            - Validation should only check URL once
            - Results cached and reused
        """
        # Create multiple files with same external link
        file1 = tmp_path / "file1.md"
        file1.write_text("[Ansible](https://www.ansible.com)")
        
        file2 = tmp_path / "file2.md"
        file2.write_text("See [Ansible docs](https://www.ansible.com).")
        
        links = [
            Link(
                source_file=file1,
                target="https://www.ansible.com",
                link_type=LinkType.EXTERNAL_URL,
                text="Ansible",
                line_number=1,
            ),
            Link(
                source_file=file2,
                target="https://www.ansible.com",
                link_type=LinkType.EXTERNAL_URL,
                text="Ansible docs",
                line_number=1,
            ),
        ]
        
        with patch("requests.head") as mock_head:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.ok = True
            mock_head.return_value = mock_response
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, enable_cache=True)
            
            results = [validator.validate(link) for link in links]
            
            # Both should be valid
            assert all(r.is_valid for r in results)
            
            # Should only make one HTTP request (cached on second)
            assert mock_head.call_count == 1


class TestExternalLinkRetry:
    """Tests for retry logic on transient failures."""

    def test_retry_on_transient_error(self, tmp_path: Path) -> None:
        """Test that transient errors trigger retry with exponential backoff."""
        from requests.exceptions import RequestException
        
        source_file = tmp_path / "README.md"
        link = Link(
            source_file=source_file,
            target="https://flaky-site.example.com",
            link_type=LinkType.EXTERNAL_URL,
            text="flaky",
            line_number=1,
        )
        
        with patch("requests.head") as mock_head:
            # Fail twice, succeed on third try
            mock_head.side_effect = [
                RequestException("Temporary error"),
                RequestException("Still failing"),
                Mock(status_code=200, ok=True),
            ]
            
            from ansibledoctor.links.link_validator import LinkValidator
            validator = LinkValidator(base_path=tmp_path, max_retries=3)
            
            result = validator.validate(link)
            
            # Should eventually succeed after retries
            assert result.is_valid
            assert result.status == LinkStatus.VALID
            assert mock_head.call_count == 3
