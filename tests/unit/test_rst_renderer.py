"""Tests for RstRenderer implementation."""
import pytest
from ansibledoctor.generator.renderers import RstRenderer
from ansibledoctor.generator.protocols import DocumentRenderer


class TestRstRenderer:
    """Test suite for RstRenderer."""

    @pytest.fixture
    def renderer(self):
        """Create RstRenderer instance for testing."""
        return RstRenderer()

    def test_renderer_implements_protocol(self, renderer):
        """Test that RstRenderer implements DocumentRenderer protocol."""
        assert isinstance(renderer, DocumentRenderer)

    def test_render_returns_content_unchanged(self, renderer):
        """Test that render returns content as-is for RST."""
        content = "Title\n=====\n\nThis is **bold** text."
        result = renderer.render(content)
        assert result == content

    def test_render_handles_empty_content(self, renderer):
        """Test render with empty string."""
        result = renderer.render("")
        assert result == ""

    def test_escape_special_rst_chars(self, renderer):
        """Test escaping RST special characters."""
        text = "Text with *asterisks* and `backticks` and _underscores_"
        result = renderer.escape(text)
        # RST special chars should be escaped with backslash
        assert r"\*" in result or "*" not in result
        assert r"\`" in result or "`" not in result

    def test_escape_backslashes(self, renderer):
        """Test escaping backslashes."""
        text = r"C:\Users\path"
        result = renderer.escape(text)
        assert isinstance(result, str)
        # Backslashes should be escaped
        assert r"\\" in result or "\\\\" in result

    def test_escape_empty_string(self, renderer):
        """Test escape with empty string."""
        result = renderer.escape("")
        assert result == ""

    def test_code_block_with_language(self, renderer):
        """Test code block with language specification."""
        code = "def hello():\n    print('world')"
        result = renderer.code_block(code, "python")
        assert ".. code-block:: python" in result
        # Code should be indented (4 spaces added to each line)
        assert "    def hello():" in result
        assert "print('world')" in result

    def test_code_block_without_language(self, renderer):
        """Test code block without language."""
        code = "some generic code"
        result = renderer.code_block(code)
        assert "::" in result
        assert code in result

    def test_code_block_preserves_indentation(self, renderer):
        """Test that code block preserves indentation."""
        code = "line1\n    indented\n        more"
        result = renderer.code_block(code, "text")
        assert "line1" in result
        assert "indented" in result

    def test_heading_level_1(self, renderer):
        """Test heading level 1 with equals underline."""
        result = renderer.heading("Title", level=1)
        assert "Title" in result
        assert "=" in result
        lines = result.split("\n")
        assert len(lines) == 2
        assert lines[0] == "Title"
        assert lines[1] == "=" * len("Title")

    def test_heading_level_2(self, renderer):
        """Test heading level 2 with hyphens."""
        result = renderer.heading("Subtitle", level=2)
        assert "Subtitle" in result
        assert "-" in result
        lines = result.split("\n")
        assert lines[0] == "Subtitle"
        assert lines[1] == "-" * len("Subtitle")

    def test_heading_level_3(self, renderer):
        """Test heading level 3 with tildes."""
        result = renderer.heading("Section", level=3)
        assert "Section" in result
        assert "~" in result

    def test_heading_level_4(self, renderer):
        """Test heading level 4 with carets."""
        result = renderer.heading("Subsection", level=4)
        assert "Subsection" in result
        assert "^" in result

    def test_heading_level_5_6(self, renderer):
        """Test heading levels 5 and 6."""
        result5 = renderer.heading("Level 5", level=5)
        assert "Level 5" in result5
        
        result6 = renderer.heading("Level 6", level=6)
        assert "Level 6" in result6

    def test_heading_invalid_level(self, renderer):
        """Test heading with invalid level."""
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            renderer.heading("Title", level=0)
        
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            renderer.heading("Title", level=7)

    def test_list_item_unordered(self, renderer):
        """Test unordered list item generation."""
        result = renderer.list_item("Item text")
        assert result == "- Item text"

    def test_list_item_ordered(self, renderer):
        """Test ordered list item generation."""
        result = renderer.list_item("Item text", ordered=True, number=1)
        assert result == "1. Item text"
        
        result = renderer.list_item("Second", ordered=True, number=2)
        assert result == "2. Second"

    def test_link_generation(self, renderer):
        """Test RST link generation."""
        result = renderer.link("Click here", "https://example.com")
        assert "`Click here <https://example.com>`_" == result

    def test_link_with_title(self, renderer):
        """Test RST link with title (ignored in RST)."""
        result = renderer.link("Click", "https://example.com", "Title")
        # RST doesn't support title attribute, should be same as without title
        assert "`Click <https://example.com>`_" == result

    def test_bold_text(self, renderer):
        """Test bold text formatting."""
        result = renderer.bold("Important")
        assert result == "**Important**"

    def test_italic_text(self, renderer):
        """Test italic text formatting."""
        result = renderer.italic("Emphasized")
        assert result == "*Emphasized*"

    def test_inline_code(self, renderer):
        """Test inline code formatting."""
        result = renderer.inline_code("variable_name")
        assert result == "``variable_name``"

    def test_inline_code_with_spaces(self, renderer):
        """Test inline code with leading/trailing spaces."""
        result = renderer.inline_code("  code  ")
        assert "``" in result
