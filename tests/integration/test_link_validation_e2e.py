"""
End-to-end tests for link validation.

Tests the complete link validation workflow from parsing through validation reporting.
Following TDD approach - these tests should fail until LinkValidator is implemented.

Spec: 013-links-cross-references
Phase: 4 (User Story 2 - Detect Broken Links)
Tasks: T030-T032, T034
"""

import tempfile
from pathlib import Path

import pytest

from ansibledoctor.models.link import Link, LinkStatus, LinkType


class TestBrokenInternalLinkDetection:
    """Tests for broken internal link detection (T030)."""

    def test_broken_internal_link_reports_error_with_location(self, tmp_path: Path) -> None:
        """Test that broken internal file links report error with file and line number.
        
        Scenario:
            - Documentation file contains link to non-existent file
            - Link validator runs
            - Error reported with source file and line number
        """
        # Create source file with broken link
        source_file = tmp_path / "README.md"
        source_file.write_text(
            "# Documentation\n\n"
            "See [missing file](missing.md) for details.\n"
        )
        
        # Parse link from file
        link = Link(
            source_file=source_file,
            target="../roles/nonexistent/README.md",
            link_type=LinkType.RELATIVE_PATH,
            text="missing file",
            line_number=3,
        )
        
        # This will fail until LinkValidator is implemented
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        # Verify error is reported
        assert not result.is_valid
        assert result.status == LinkStatus.BROKEN
        assert result.error_message is not None
        assert "not found" in result.error_message.lower()
        assert result.line_number == 3
        assert str(result.source_file) == str(source_file)
    
    def test_broken_link_in_multiple_files(self, tmp_path: Path) -> None:
        """Test validation of multiple files with broken links."""
        # Create multiple files with broken links
        file1 = tmp_path / "file1.md"
        file1.write_text("[broken](nonexistent1.md)")
        
        file2 = tmp_path / "file2.md"
        file2.write_text("[also broken](nonexistent2.md)")
        
        links = [
            Link(
                source_file=file1,
                target="nonexistent1.md",
                link_type=LinkType.RELATIVE_PATH,
                text="broken",
                line_number=1,
            ),
            Link(
                source_file=file2,
                target="nonexistent2.md",
                link_type=LinkType.RELATIVE_PATH,
                text="also broken",
                line_number=1,
            ),
        ]
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        results = [validator.validate(link) for link in links]
        
        # Both links should be broken
        assert len(results) == 2
        assert all(not r.is_valid for r in results)
        assert all(r.status == LinkStatus.BROKEN for r in results)


class TestMissingRoleDocumentation:
    """Tests for missing role documentation detection (T031)."""

    def test_missing_role_shows_warning(self, tmp_path: Path) -> None:
        """Test that links to missing role documentation show appropriate warning.
        
        Scenario:
            - Role documentation links to another role
            - Target role doesn't exist
            - Warning shows "Target role not found"
        """
        # Create source role
        source_role = tmp_path / "roles" / "web"
        source_role.mkdir(parents=True)
        readme = source_role / "README.md"
        readme.write_text("Depends on [common role](../common/README.md)")
        
        # Don't create target role (common)
        link = Link(
            source_file=readme,
            target="../common/README.md",
            link_type=LinkType.RELATIVE_PATH,
            text="common role",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert not result.is_valid
        assert result.status == LinkStatus.BROKEN
        assert "role not found" in result.error_message.lower() or "not found" in result.error_message.lower()


class TestInvalidSectionAnchor:
    """Tests for invalid section anchor detection (T032)."""

    def test_invalid_anchor_reports_error(self, tmp_path: Path) -> None:
        """Test that invalid section anchors report 'Anchor not found' error.
        
        Scenario:
            - Documentation links to section anchor in another file
            - Target file exists but anchor doesn't
            - Error shows "Anchor not found"
        """
        # Create target file with some sections
        target_file = tmp_path / "guide.md"
        target_file.write_text(
            "# Guide\n\n"
            "## Installation\n\n"
            "## Configuration\n\n"
        )
        
        # Create source file linking to non-existent section
        source_file = tmp_path / "README.md"
        source_file.write_text("See [usage](guide.md#usage) section.")
        
        link = Link(
            source_file=source_file,
            target="guide.md#usage",
            link_type=LinkType.INTERNAL_SECTION,
            text="usage",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert not result.is_valid
        assert result.status == LinkStatus.BROKEN
        assert "anchor not found" in result.error_message.lower() or "section not found" in result.error_message.lower()
    
    def test_valid_anchor_passes(self, tmp_path: Path) -> None:
        """Test that valid anchors pass validation."""
        # Create target file with sections
        target_file = tmp_path / "guide.md"
        target_file.write_text(
            "# Guide\n\n"
            "## Installation\n\n"
            "Content here.\n"
        )
        
        source_file = tmp_path / "README.md"
        source_file.write_text("See [installation](guide.md#installation).")
        
        link = Link(
            source_file=source_file,
            target="guide.md#installation",
            link_type=LinkType.INTERNAL_SECTION,
            text="installation",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert result.is_valid
        assert result.status == LinkStatus.VALID


class TestValidLinks:
    """Tests for valid link detection (T034)."""

    def test_valid_internal_file_link(self, tmp_path: Path) -> None:
        """Test that valid internal file links report success.
        
        Scenario:
            - Documentation links to existing file
            - Validation passes
            - Success message returned
        """
        # Create target file
        target = tmp_path / "guide.md"
        target.write_text("# Guide\n\nContent here.")
        
        # Create source file with valid link
        source = tmp_path / "README.md"
        source.write_text("See [guide](guide.md).")
        
        link = Link(
            source_file=source,
            target="guide.md",
            link_type=LinkType.RELATIVE_PATH,
            text="guide",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert result.is_valid
        assert result.status == LinkStatus.VALID
        assert result.error_message is None
    
    def test_valid_relative_path_link(self, tmp_path: Path) -> None:
        """Test validation of relative path links."""
        # Create nested structure
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "guide.md").write_text("# Guide")
        
        source = tmp_path / "README.md"
        source.write_text("See [guide](docs/guide.md).")
        
        link = Link(
            source_file=source,
            target="docs/guide.md",
            link_type=LinkType.RELATIVE_PATH,
            text="guide",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert result.is_valid
        assert result.status == LinkStatus.VALID
    
    def test_absolute_path_link(self, tmp_path: Path) -> None:
        """Test validation of absolute path links."""
        target = tmp_path / "guide.md"
        target.write_text("# Guide")
        
        source = tmp_path / "README.md"
        
        link = Link(
            source_file=source,
            target=str(target),
            link_type=LinkType.ABSOLUTE_PATH,
            text="guide",
            line_number=1,
        )
        
        from ansibledoctor.links.link_validator import LinkValidator
        validator = LinkValidator(base_path=tmp_path)
        
        result = validator.validate(link)
        
        assert result.is_valid
        assert result.status == LinkStatus.VALID
