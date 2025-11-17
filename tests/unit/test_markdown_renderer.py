"""Tests for MarkdownRenderer implementation."""
import pytest
from ansibledoctor.generator.renderers import MarkdownRenderer
from ansibledoctor.generator.protocols import DocumentRenderer


class TestMarkdownRenderer:
    """Test suite for MarkdownRenderer."""

    @pytest.fixture
    def renderer(self):
        """Create MarkdownRenderer instance for testing."""
        return MarkdownRenderer()

    def test_renderer_implements_protocol(self, renderer):
        """Test that MarkdownRenderer implements DocumentRenderer protocol."""
        assert isinstance(renderer, DocumentRenderer)

    def test_render_returns_content_unchanged(self, renderer):
        """Test that render returns content as-is for Markdown."""
        content = "# Hello World\n\nThis is **bold** text."
        result = renderer.render(content)
        assert result == content
        assert isinstance(result, str)

    def test_render_handles_empty_content(self, renderer):
        """Test render with empty string."""
        result = renderer.render("")
        assert result == ""

    def test_render_handles_multiline_content(self, renderer):
        """Test render preserves multiline content."""
        content = """# Title

## Subtitle

- Item 1
- Item 2

```python
print('hello')
```"""
        result = renderer.render(content)
        assert result == content

    def test_escape_special_markdown_chars(self, renderer):
        """Test escaping Markdown special characters."""
        text = "Text with [links] and *asterisks* and _underscores_"
        result = renderer.escape(text)
        assert r"\[" in result or "[" not in result
        assert r"\*" in result or result.count("*") < text.count("*")
        assert r"\_" in result or result.count("_") < text.count("_")

    def test_escape_backslashes(self, renderer):
        """Test escaping backslashes."""
        text = r"C:\Users\path\to\file"
        result = renderer.escape(text)
        assert isinstance(result, str)
        # Backslashes should be escaped or handled
        assert "\\" in result or r"\\" in result

    def test_escape_brackets(self, renderer):
        """Test escaping square brackets (link syntax)."""
        text = "[text](url)"
        result = renderer.escape(text)
        assert r"\[" in result or r"\]" in result

    def test_escape_empty_string(self, renderer):
        """Test escape with empty string."""
        result = renderer.escape("")
        assert result == ""

    def test_code_block_with_language(self, renderer):
        """Test code block with language specification."""
        code = "def hello():\n    print('world')"
        result = renderer.code_block(code, "python")
        assert result.startswith("```python")
        assert result.endswith("```")
        assert code in result

    def test_code_block_without_language(self, renderer):
        """Test code block without language."""
        code = "some generic code"
        result = renderer.code_block(code)
        assert result.startswith("```")
        assert result.endswith("```")
        assert code in result

    def test_code_block_preserves_indentation(self, renderer):
        """Test that code block preserves indentation."""
        code = "    indented line\n        more indented"
        result = renderer.code_block(code, "text")
        assert "    indented line" in result
        assert "        more indented" in result

    def test_code_block_handles_empty_code(self, renderer):
        """Test code block with empty string."""
        result = renderer.code_block("")
        assert result.startswith("```")
        assert result.endswith("```")

    def test_code_block_handles_special_chars(self, renderer):
        """Test code block with special Markdown characters."""
        code = "# Not a heading\n* Not a list\n[Not a link]"
        result = renderer.code_block(code, "text")
        assert code in result
        # Should not need escaping inside code blocks
        assert "```" in result

    def test_heading_generation(self, renderer):
        """Test heading generation."""
        result = renderer.heading("My Title", level=1)
        assert result == "# My Title"
        
        result = renderer.heading("Subtitle", level=2)
        assert result == "## Subtitle"
        
        result = renderer.heading("Section", level=3)
        assert result == "### Section"

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
        
        result = renderer.list_item("Second item", ordered=True, number=2)
        assert result == "2. Second item"

    def test_link_generation(self, renderer):
        """Test Markdown link generation."""
        result = renderer.link("Click here", "https://example.com")
        assert result == "[Click here](https://example.com)"

    def test_link_with_title(self, renderer):
        """Test Markdown link with title attribute."""
        result = renderer.link("Click", "https://example.com", "Example Site")
        assert result == '[Click](https://example.com "Example Site")'

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
        assert result == "`variable_name`"

    def test_inline_code_with_backticks(self, renderer):
        """Test inline code containing backticks."""
        result = renderer.inline_code("`inner`")
        # Should use double backticks
        assert "``" in result or result.count("`") > 2
