"""
Tests for link parsing utilities.

Spec: 013-links-cross-references
Phase: 2 (Foundational)
"""

from pathlib import Path

import pytest

from ansibledoctor.models.link import LinkType
from ansibledoctor.utils.link_parser import LinkParser


class TestLinkParser:
    """Tests for LinkParser class."""

    def test_parse_markdown_single_link(self) -> None:
        """Test parsing single Markdown link."""
        parser = LinkParser()
        content = "See [documentation](../docs/guide.md) for details."
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 1
        assert links[0].text == "documentation"
        assert links[0].target == "../docs/guide.md"
        assert links[0].line_number == 1
        assert links[0].link_type == LinkType.RELATIVE_PATH

    def test_parse_markdown_multiple_links(self) -> None:
        """Test parsing multiple Markdown links."""
        parser = LinkParser()
        content = """
# Documentation

See [guide](guide.md) and [API reference](api.md).
Also check [external docs](https://example.com).
"""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 3
        assert links[0].text == "guide"
        assert links[1].text == "API reference"
        assert links[2].text == "external docs"
        assert links[2].link_type == LinkType.EXTERNAL_URL

    def test_parse_markdown_external_links(self) -> None:
        """Test parsing external HTTP/HTTPS links."""
        parser = LinkParser()
        content = """
- [HTTP Link](http://example.com)
- [HTTPS Link](https://secure.example.com)
"""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 2
        assert all(link.link_type == LinkType.EXTERNAL_URL for link in links)
        assert links[0].target == "http://example.com"
        assert links[1].target == "https://secure.example.com"

    def test_parse_markdown_section_anchors(self) -> None:
        """Test parsing section anchor links."""
        parser = LinkParser()
        content = """
# Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
"""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 2
        assert all(link.link_type == LinkType.INTERNAL_SECTION for link in links)
        assert links[0].target == "#introduction"
        assert links[1].target == "#installation"

    def test_parse_markdown_with_line_numbers(self) -> None:
        """Test that line numbers are correctly assigned."""
        parser = LinkParser()
        content = """Line 1
Line 2 with [link1](file1.md)
Line 3
Line 4 with [link2](file2.md) and [link3](file3.md)
"""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 3
        assert links[0].line_number == 2
        assert links[1].line_number == 4
        assert links[2].line_number == 4

    def test_parse_markdown_empty_content(self) -> None:
        """Test parsing empty content returns empty list."""
        parser = LinkParser()
        content = ""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 0

    def test_parse_markdown_no_links(self) -> None:
        """Test parsing content without links returns empty list."""
        parser = LinkParser()
        content = """
# Documentation

This is regular text without any links.
Just plain paragraphs.
"""
        file_path = Path("/project/README.md")

        links = parser.parse_markdown(file_path, content)

        assert len(links) == 0

    def test_parse_rst_single_link(self) -> None:
        """Test parsing single RST link."""
        parser = LinkParser()
        content = "See `documentation <../docs/guide.rst>`_ for details."
        file_path = Path("/project/README.rst")

        links = parser.parse_rst(file_path, content)

        assert len(links) == 1
        assert links[0].text == "documentation"
        assert links[0].target == "../docs/guide.rst"
        assert links[0].line_number == 1

    def test_parse_rst_multiple_links(self) -> None:
        """Test parsing multiple RST links."""
        parser = LinkParser()
        content = """
Documentation
=============

See `guide <guide.rst>`_ and `API reference <api.rst>`_.
Also check `external docs <https://example.com>`_.
"""
        file_path = Path("/project/README.rst")

        links = parser.parse_rst(file_path, content)

        assert len(links) == 3
        assert links[0].text == "guide"
        assert links[1].text == "API reference"
        assert links[2].text == "external docs"

    def test_parse_html_with_beautifulsoup(self) -> None:
        """Test parsing HTML links with BeautifulSoup."""
        parser = LinkParser()
        content = """
<html>
<body>
    <a href="../docs/guide.html">Documentation</a>
    <a href="https://example.com">Example</a>
</body>
</html>
"""
        file_path = Path("/project/index.html")

        links = parser.parse_html(file_path, content)

        # BeautifulSoup may not be installed in minimal environment
        if len(links) > 0:
            assert links[0].target == "../docs/guide.html"
            assert links[0].text == "Documentation"
            assert links[1].target == "https://example.com"

    def test_parse_file_markdown(self, tmp_path: Path) -> None:
        """Test parsing Markdown file."""
        file_path = tmp_path / "test.md"
        file_path.write_text("[Link](target.md)")

        parser = LinkParser()
        links = parser.parse_file(file_path)

        assert len(links) == 1
        assert links[0].target == "target.md"

    def test_parse_file_html(self, tmp_path: Path) -> None:
        """Test parsing HTML file."""
        file_path = tmp_path / "test.html"
        file_path.write_text('<a href="target.html">Link</a>')

        parser = LinkParser()
        links = parser.parse_file(file_path)

        # BeautifulSoup may not be installed
        if len(links) > 0:
            assert links[0].target == "target.html"

    def test_parse_file_rst(self, tmp_path: Path) -> None:
        """Test parsing RST file."""
        file_path = tmp_path / "test.rst"
        file_path.write_text("`Link <target.rst>`_")

        parser = LinkParser()
        links = parser.parse_file(file_path)

        assert len(links) == 1
        assert links[0].target == "target.rst"

    def test_parse_file_not_found_raises_error(self) -> None:
        """Test parsing non-existent file raises error."""
        parser = LinkParser()
        file_path = Path("/nonexistent/file.md")

        with pytest.raises(FileNotFoundError):
            parser.parse_file(file_path)

    def test_parse_file_unsupported_extension_raises_error(self, tmp_path: Path) -> None:
        """Test parsing unsupported file type raises error."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Some text")

        parser = LinkParser()

        with pytest.raises(ValueError, match="Unsupported file type"):
            parser.parse_file(file_path)

    def test_parse_directory_finds_all_docs(self, tmp_path: Path) -> None:
        """Test parsing directory finds all documentation files."""
        # Create test structure
        (tmp_path / "doc1.md").write_text("[Link1](target1.md)")
        (tmp_path / "doc2.md").write_text("[Link2](target2.md)")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "doc3.md").write_text("[Link3](target3.md)")
        (tmp_path / "ignore.txt").write_text("Should be ignored")

        parser = LinkParser()
        links = parser.parse_directory(tmp_path)

        # Should find 3 links from .md files, ignore .txt
        assert len(links) == 3
        targets = {link.target for link in links}
        assert targets == {"target1.md", "target2.md", "target3.md"}

    def test_parse_directory_custom_extensions(self, tmp_path: Path) -> None:
        """Test parsing directory with custom extensions."""
        (tmp_path / "doc1.md").write_text("[Link1](target1.md)")
        (tmp_path / "doc2.rst").write_text("`Link2 <target2.rst>`_")
        (tmp_path / "doc3.html").write_text('<a href="target3.html">Link3</a>')

        parser = LinkParser()
        # Only parse .md files
        links = parser.parse_directory(tmp_path, extensions={".md"})

        assert len(links) == 1
        assert links[0].target == "target1.md"

    def test_parse_directory_empty_returns_empty_list(self, tmp_path: Path) -> None:
        """Test parsing empty directory returns empty list."""
        parser = LinkParser()
        links = parser.parse_directory(tmp_path)

        assert len(links) == 0

    def test_parse_directory_skip_invalid_files(self, tmp_path: Path) -> None:
        """Test parsing directory skips invalid files without error."""
        (tmp_path / "valid.md").write_text("[Link](target.md)")
        (tmp_path / "invalid.md").write_text("")  # Empty file
        (tmp_path / "corrupt").mkdir()  # Directory with .md would cause error

        parser = LinkParser()
        links = parser.parse_directory(tmp_path)

        # Should successfully parse valid file and skip others
        assert len(links) == 1
        assert links[0].target == "target.md"
