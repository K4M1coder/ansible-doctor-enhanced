"""Tests for HtmlRenderer implementation."""
import pytest
from ansibledoctor.generator.renderers import HtmlRenderer
from ansibledoctor.generator.protocols import DocumentRenderer


class TestHtmlRenderer:
    """Test suite for HtmlRenderer."""

    @pytest.fixture
    def renderer(self):
        """Create HtmlRenderer instance for testing."""
        return HtmlRenderer()

    def test_renderer_implements_protocol(self, renderer):
        """Test that HtmlRenderer implements DocumentRenderer protocol."""
        assert isinstance(renderer, DocumentRenderer)

    def test_render_returns_content_unchanged(self, renderer):
        """Test that render returns content as-is for HTML."""
        content = "<h1>Hello World</h1><p>This is <strong>bold</strong> text.</p>"
        result = renderer.render(content)
        assert result == content
        assert isinstance(result, str)

    def test_render_handles_empty_content(self, renderer):
        """Test render with empty string."""
        result = renderer.render("")
        assert result == ""

    def test_escape_html_special_chars(self, renderer):
        """Test escaping HTML special characters."""
        text = "<tag>content & \"quotes\" with 'apostrophes'"
        result = renderer.escape(text)
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result
        assert "&#x27;" in result or "&apos;" in result

    def test_escape_less_than_greater_than(self, renderer):
        """Test escaping < and > characters."""
        text = "<script>alert('xss')</script>"
        result = renderer.escape(text)
        assert "<" not in result
        assert ">" not in result
        assert "&lt;script&gt;" in result

    def test_escape_ampersand(self, renderer):
        """Test escaping ampersand."""
        text = "Tom & Jerry"
        result = renderer.escape(text)
        assert "&amp;" in result
        assert text != result

    def test_escape_quotes(self, renderer):
        """Test escaping double quotes."""
        text = 'She said "hello"'
        result = renderer.escape(text)
        assert "&quot;" in result

    def test_escape_empty_string(self, renderer):
        """Test escape with empty string."""
        result = renderer.escape("")
        assert result == ""

    def test_code_block_with_language(self, renderer):
        """Test code block with language specification."""
        code = "def hello():\n    print('world')"
        result = renderer.code_block(code, "python")
        assert result.startswith("<pre>")
        assert result.endswith("</pre>")
        assert "<code" in result
        assert "language-python" in result
        # Code should be escaped (single quotes become &#x27;)
        assert "&#x27;" in result or "&quot;" in result or "'" not in code

    def test_code_block_without_language(self, renderer):
        """Test code block without language."""
        code = "some generic code"
        result = renderer.code_block(code)
        assert result.startswith("<pre>")
        assert result.endswith("</pre>")
        assert "<code>" in result
        assert code in result

    def test_code_block_escapes_html(self, renderer):
        """Test that code block escapes HTML characters."""
        code = "<div>HTML content</div>"
        result = renderer.code_block(code, "html")
        assert "&lt;div&gt;" in result
        assert "<div>" not in result or result.count("<div>") == 0

    def test_code_block_preserves_indentation(self, renderer):
        """Test that code block preserves indentation."""
        code = "    indented line\n        more indented"
        result = renderer.code_block(code, "text")
        assert "indented line" in result
        assert "more indented" in result

    def test_heading_generation(self, renderer):
        """Test heading generation."""
        result = renderer.heading("My Title", level=1)
        assert result == "<h1>My Title</h1>"
        
        result = renderer.heading("Subtitle", level=2)
        assert result == "<h2>Subtitle</h2>"
        
        result = renderer.heading("Section", level=6)
        assert result == "<h6>Section</h6>"

    def test_heading_escapes_html(self, renderer):
        """Test that headings escape HTML."""
        result = renderer.heading("<script>alert('xss')</script>", level=1)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_heading_invalid_level(self, renderer):
        """Test heading with invalid level."""
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            renderer.heading("Title", level=0)
        
        with pytest.raises(ValueError, match="level must be between 1 and 6"):
            renderer.heading("Title", level=7)

    def test_list_item_unordered(self, renderer):
        """Test unordered list item generation."""
        result = renderer.list_item("Item text")
        assert result == "<li>Item text</li>"

    def test_list_item_ordered(self, renderer):
        """Test ordered list item generation (same as unordered in HTML)."""
        result = renderer.list_item("Item text", ordered=True, number=1)
        assert result == "<li>Item text</li>"

    def test_list_item_escapes_html(self, renderer):
        """Test that list items escape HTML."""
        result = renderer.list_item("<tag>content</tag>")
        assert "&lt;tag&gt;" in result

    def test_link_generation(self, renderer):
        """Test HTML link generation."""
        result = renderer.link("Click here", "https://example.com")
        assert result == '<a href="https://example.com">Click here</a>'

    def test_link_with_title(self, renderer):
        """Test HTML link with title attribute."""
        result = renderer.link("Click", "https://example.com", "Example Site")
        assert result == '<a href="https://example.com" title="Example Site">Click</a>'

    def test_link_escapes_url(self, renderer):
        """Test that link escapes URL special characters."""
        result = renderer.link("Link", "https://example.com?a=1&b=2")
        assert "&amp;" in result

    def test_link_escapes_text(self, renderer):
        """Test that link text is escaped."""
        result = renderer.link("<script>", "https://example.com")
        assert "&lt;script&gt;" in result

    def test_bold_text(self, renderer):
        """Test bold text formatting."""
        result = renderer.bold("Important")
        assert result == "<strong>Important</strong>"

    def test_bold_escapes_html(self, renderer):
        """Test that bold escapes HTML."""
        result = renderer.bold("<tag>")
        assert "&lt;tag&gt;" in result

    def test_italic_text(self, renderer):
        """Test italic text formatting."""
        result = renderer.italic("Emphasized")
        assert result == "<em>Emphasized</em>"

    def test_italic_escapes_html(self, renderer):
        """Test that italic escapes HTML."""
        result = renderer.italic("<tag>")
        assert "&lt;tag&gt;" in result

    def test_inline_code(self, renderer):
        """Test inline code formatting."""
        result = renderer.inline_code("variable_name")
        assert result == "<code>variable_name</code>"

    def test_inline_code_escapes_html(self, renderer):
        """Test that inline code escapes HTML."""
        result = renderer.inline_code("<div>")
        assert "&lt;div&gt;" in result

    def test_paragraph(self, renderer):
        """Test paragraph generation."""
        result = renderer.paragraph("This is a paragraph.")
        assert result == "<p>This is a paragraph.</p>"

    def test_paragraph_escapes_html(self, renderer):
        """Test that paragraph escapes HTML."""
        result = renderer.paragraph("<script>alert()</script>")
        assert "&lt;script&gt;" in result
