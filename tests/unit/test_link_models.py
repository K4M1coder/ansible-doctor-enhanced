"""
Tests for Link models (Link, LinkType, LinkStatus).

Spec: 013-links-cross-references
Phase: 2 (Foundational)
"""

import re
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from ansibledoctor.models.link import Link, LinkStatus, LinkType


class TestLinkType:
    """Tests for LinkType enum."""

    def test_all_link_types_defined(self) -> None:
        """Test that all expected link types are defined."""
        expected_types = {
            "INTERNAL_FILE",
            "INTERNAL_SECTION",
            "CROSS_REFERENCE",
            "EXTERNAL_URL",
            "RELATIVE_PATH",
            "ABSOLUTE_PATH",
        }
        actual_types = set(LinkType.__members__)
        assert actual_types == expected_types

    def test_link_type_values(self) -> None:
        """Test that link type enum values are correct."""
        assert LinkType.INTERNAL_FILE.value == "internal_file"
        assert LinkType.INTERNAL_SECTION.value == "internal_section"
        assert LinkType.CROSS_REFERENCE.value == "cross_reference"
        assert LinkType.EXTERNAL_URL.value == "external_url"
        assert LinkType.RELATIVE_PATH.value == "relative_path"
        assert LinkType.ABSOLUTE_PATH.value == "absolute_path"


class TestLinkStatus:
    """Tests for LinkStatus enum."""

    def test_all_link_statuses_defined(self) -> None:
        """Test that all expected link statuses are defined."""
        expected_statuses = {
            "VALID",
            "BROKEN",
            "REDIRECT",
            "TIMEOUT",
            "INVALID_SYNTAX",
            "NOT_CHECKED",
        }
        actual_statuses = set(LinkStatus.__members__)
        assert actual_statuses == expected_statuses

    def test_link_status_values(self) -> None:
        """Test that link status enum values are correct."""
        assert LinkStatus.VALID.value == "valid"
        assert LinkStatus.BROKEN.value == "broken"
        assert LinkStatus.REDIRECT.value == "redirect"
        assert LinkStatus.TIMEOUT.value == "timeout"
        assert LinkStatus.INVALID_SYNTAX.value == "invalid_syntax"
        assert LinkStatus.NOT_CHECKED.value == "not_checked"


class TestLink:
    """Tests for Link model."""

    def test_create_link_minimal(self) -> None:
        """Test creating link with minimal required fields."""
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="../roles/demo.md",
            link_type=LinkType.RELATIVE_PATH,
        )
        assert link.source_file == Path("/docs/index.md").resolve()
        assert link.target == "../roles/demo.md"
        assert link.link_type == LinkType.RELATIVE_PATH
        assert link.text is None
        assert link.line_number is None
        assert link.status == LinkStatus.NOT_CHECKED

    def test_create_link_full(self) -> None:
        """Test creating link with all fields."""
        now = datetime.now()
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="https://example.com",
            link_type=LinkType.EXTERNAL_URL,
            text="Example Site",
            line_number=42,
            status=LinkStatus.VALID,
            http_status=200,
            redirect_url=None,
            error_message=None,
            last_checked=now,
        )
        assert link.source_file == Path("/docs/index.md").resolve()
        assert link.target == "https://example.com"
        assert link.link_type == LinkType.EXTERNAL_URL
        assert link.text == "Example Site"
        assert link.line_number == 42
        assert link.status == LinkStatus.VALID
        assert link.http_status == 200
        assert link.last_checked == now

    def test_is_valid_property(self) -> None:
        """Test is_valid property returns correct value."""
        link_valid = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="file.md",
            link_type=LinkType.RELATIVE_PATH,
            status=LinkStatus.VALID,
        )
        assert link_valid.is_valid is True

        link_broken = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="missing.md",
            link_type=LinkType.RELATIVE_PATH,
            status=LinkStatus.BROKEN,
        )
        assert link_broken.is_valid is False

    def test_is_external_property(self) -> None:
        """Test is_external property identifies external links."""
        link_external = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="https://example.com",
            link_type=LinkType.EXTERNAL_URL,
        )
        assert link_external.is_external is True

        link_internal = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="file.md",
            link_type=LinkType.RELATIVE_PATH,
        )
        assert link_internal.is_external is False

    def test_is_internal_property(self) -> None:
        """Test is_internal property identifies internal links."""
        internal_types = [
            LinkType.INTERNAL_FILE,
            LinkType.INTERNAL_SECTION,
            LinkType.RELATIVE_PATH,
            LinkType.ABSOLUTE_PATH,
        ]

        for link_type in internal_types:
            link = Link(
                source_file=Path("/docs/index.md").resolve(),
                target="file.md",
                link_type=link_type,
            )
            assert link.is_internal is True, f"Failed for {link_type}"

        link_external = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="https://example.com",
            link_type=LinkType.EXTERNAL_URL,
        )
        assert link_external.is_internal is False

    def test_validate_empty_target_raises_error(self) -> None:
        """Test that empty target raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Link(
                source_file=Path("/docs/index.md").resolve(),
                target="",
                link_type=LinkType.RELATIVE_PATH,
            )
        assert "Link target cannot be empty" in str(exc_info.value)

    def test_validate_whitespace_target_raises_error(self) -> None:
        """Test that whitespace-only target raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Link(
                source_file=Path("/docs/index.md").resolve(),
                target="   ",
                link_type=LinkType.RELATIVE_PATH,
            )
        assert "Link target cannot be empty" in str(exc_info.value)

    def test_validate_relative_source_file_raises_error(self) -> None:
        """Test that relative source_file raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Link(
                source_file=Path("docs/index.md"),  # Relative path
                target="file.md",
                link_type=LinkType.RELATIVE_PATH,
            )
        assert "source_file must be absolute path" in str(exc_info.value)

    def test_from_markdown_basic_link(self) -> None:
        """Test parsing link from Markdown regex match."""
        pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        text = "[Documentation](../docs/guide.md)"
        match = pattern.search(text)
        assert match is not None

        source_path = Path("/project/README.md")
        link = Link.from_markdown(
            source=source_path,
            match=match,
            line_number=10,
        )

        assert link.source_file == source_path.resolve()
        assert link.target == "../docs/guide.md"
        assert link.text == "Documentation"
        assert link.line_number == 10
        assert link.link_type == LinkType.RELATIVE_PATH

    def test_from_markdown_external_link(self) -> None:
        """Test parsing external link from Markdown."""
        pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        text = "[Example](https://example.com)"
        match = pattern.search(text)
        assert match is not None

        link = Link.from_markdown(
            source=Path("/project/README.md"),
            match=match,
            line_number=20,
        )

        assert link.target == "https://example.com"
        assert link.text == "Example"
        assert link.link_type == LinkType.EXTERNAL_URL

    def test_infer_link_type_external_http(self) -> None:
        """Test link type inference for HTTP URLs."""
        assert Link._infer_link_type("http://example.com") == LinkType.EXTERNAL_URL
        assert Link._infer_link_type("https://example.com") == LinkType.EXTERNAL_URL

    def test_infer_link_type_internal_section(self) -> None:
        """Test link type inference for section anchors."""
        assert Link._infer_link_type("#section") == LinkType.INTERNAL_SECTION
        assert Link._infer_link_type("#heading-one") == LinkType.INTERNAL_SECTION

    def test_infer_link_type_absolute_path(self) -> None:
        """Test link type inference for absolute paths."""
        assert Link._infer_link_type("/docs/guide.md") == LinkType.ABSOLUTE_PATH
        assert Link._infer_link_type("/path/to/file") == LinkType.ABSOLUTE_PATH

    def test_infer_link_type_relative_path(self) -> None:
        """Test link type inference for relative paths."""
        assert Link._infer_link_type("../docs/guide.md") == LinkType.RELATIVE_PATH
        assert Link._infer_link_type("./file.md") == LinkType.RELATIVE_PATH
        assert Link._infer_link_type("file.md") == LinkType.RELATIVE_PATH

    def test_resolve_target_path_relative(self, tmp_path: Path) -> None:
        """Test resolving relative link target to absolute path."""
        # Create test structure
        source_file = tmp_path / "docs" / "index.md"
        source_file.parent.mkdir(parents=True)
        source_file.touch()

        target_file = tmp_path / "docs" / "guide.md"
        target_file.touch()

        link = Link(
            source_file=source_file,
            target="guide.md",
            link_type=LinkType.RELATIVE_PATH,
        )

        resolved = link.resolve_target_path()
        assert resolved == target_file

    def test_resolve_target_path_external_returns_none(self) -> None:
        """Test that external links return None for target path."""
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="https://example.com",
            link_type=LinkType.EXTERNAL_URL,
        )

        resolved = link.resolve_target_path()
        assert resolved is None

    def test_extract_anchor_with_anchor(self) -> None:
        """Test extracting anchor from link target."""
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="file.md#section-one",
            link_type=LinkType.RELATIVE_PATH,
        )

        anchor = link.extract_anchor()
        assert anchor == "section-one"

    def test_extract_anchor_without_anchor(self) -> None:
        """Test extracting anchor when no anchor present."""
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="file.md",
            link_type=LinkType.RELATIVE_PATH,
        )

        anchor = link.extract_anchor()
        assert anchor is None

    def test_extract_anchor_section_link(self) -> None:
        """Test extracting anchor from section link."""
        link = Link(
            source_file=Path("/docs/index.md").resolve(),
            target="#heading",
            link_type=LinkType.INTERNAL_SECTION,
        )

        anchor = link.extract_anchor()
        assert anchor == "heading"
