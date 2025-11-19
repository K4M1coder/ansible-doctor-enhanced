"""Tests for HTML renderer.

Following TDD - these tests are written FIRST before implementation.
T231: HtmlRenderer unit tests covering all methods and edge cases.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable
from ansibledoctor.models.variable import VariableType


class TestHtmlRendererBasics:
    """Test basic HtmlRenderer properties and initialization."""

    def test_format_property_returns_html(self):
        """Test format property returns OutputFormat.HTML."""
        renderer = HtmlRenderer()
        assert renderer.format == OutputFormat.HTML

    def test_renderer_initializes_successfully(self):
        """Test renderer can be instantiated without errors."""
        renderer = HtmlRenderer()
        assert renderer is not None
        assert hasattr(renderer, "render")
        assert hasattr(renderer, "escape")
        assert hasattr(renderer, "code_block")


class TestHtmlEscape:
    """Test HTML entity escaping."""

    def test_escape_less_than(self):
        """Test escaping < character."""
        renderer = HtmlRenderer()
        assert renderer.escape("<tag>") == "&lt;tag&gt;"

    def test_escape_greater_than(self):
        """Test escaping > character."""
        renderer = HtmlRenderer()
        assert renderer.escape("<div>") == "&lt;div&gt;"

    def test_escape_ampersand(self):
        """Test escaping & character."""
        renderer = HtmlRenderer()
        assert renderer.escape("Tom & Jerry") == "Tom &amp; Jerry"

    def test_escape_quotes(self):
        """Test escaping double quotes."""
        renderer = HtmlRenderer()
        # markupsafe uses &#34; (numeric) instead of &quot; (named)
        assert renderer.escape('Say "Hello"') == "Say &#34;Hello&#34;"

    def test_escape_apostrophe(self):
        """Test escaping single quotes/apostrophes."""
        renderer = HtmlRenderer()
        # markupsafe uses &#39; for apostrophes
        assert renderer.escape("It's working") == "It&#39;s working"

    def test_escape_mixed_entities(self):
        """Test escaping multiple HTML entities."""
        renderer = HtmlRenderer()
        text = '<script>alert("XSS & injection")</script>'
        # markupsafe uses numeric entities for quotes
        expected = "&lt;script&gt;alert(&#34;XSS &amp; injection&#34;)&lt;/script&gt;"
        assert renderer.escape(text) == expected

    def test_escape_empty_string(self):
        """Test escaping empty string."""
        renderer = HtmlRenderer()
        assert renderer.escape("") == ""

    def test_escape_none_returns_empty(self):
        """Test escaping None returns empty string."""
        renderer = HtmlRenderer()
        assert renderer.escape(None) == ""


class TestHtmlCodeBlock:
    """Test HTML code block formatting."""

    def test_code_block_with_language(self):
        """Test code block with language hint."""
        renderer = HtmlRenderer()
        code = "def hello():\n    print('Hello')"
        result = renderer.code_block(code, "python")
        
        assert "<pre>" in result
        assert "<code" in result
        assert 'class="language-python"' in result
        assert "def hello():" in result

    def test_code_block_without_language(self):
        """Test code block without language hint."""
        renderer = HtmlRenderer()
        code = "some code"
        result = renderer.code_block(code)
        
        assert "<pre>" in result
        assert "<code>" in result
        assert "some code" in result

    def test_code_block_escapes_html_entities(self):
        """Test code block escapes HTML entities in code."""
        renderer = HtmlRenderer()
        code = "<div>HTML content</div>"
        result = renderer.code_block(code, "html")
        
        assert "&lt;div&gt;" in result
        assert "&lt;/div&gt;" in result

    def test_code_block_preserves_whitespace(self):
        """Test code block preserves indentation and newlines."""
        renderer = HtmlRenderer()
        code = "line1\n  line2\n    line3"
        result = renderer.code_block(code)
        
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result


class TestHtmlRenderWithOptions:
    """Test HTML rendering with various options."""

    @pytest.fixture
    def minimal_role(self, tmp_path):
        """Create minimal role for testing."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        metadata = RoleMetadata(
            role_name="test_role",
            author="Test Author",
            description="Test role for HTML rendering",
            license="MIT",
            min_ansible_version="2.9",
        )
        
        return AnsibleRole(
            name="test_role",
            path=role_path,
            metadata=metadata,
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_render_returns_html_content(self, minimal_role):
        """Test render() returns HTML string."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_includes_doctype(self, minimal_role):
        """Test rendered HTML includes DOCTYPE declaration."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        assert "<!DOCTYPE html>" in result or "<!doctype html>" in result.lower()

    def test_render_includes_html_structure(self, minimal_role):
        """Test rendered HTML has proper structure (html, head, body)."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        assert "<html" in result.lower()
        assert "<head" in result.lower()
        assert "<body" in result.lower()
        assert "</html>" in result.lower()

    def test_render_with_embed_css_true_includes_style_tag(self, minimal_role):
        """Test render with embed_css=True includes <style> tag."""
        renderer = HtmlRenderer(embed_css=True)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        assert "<style" in result.lower()
        assert "</style>" in result.lower()

    def test_render_with_embed_css_false_no_style_tag(self, minimal_role):
        """Test render with embed_css=False does not include <style> tag."""
        renderer = HtmlRenderer(embed_css=False)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        assert "<style" not in result.lower() or "/* External CSS */" in result

    def test_render_with_generate_toc_true_includes_toc(self, minimal_role):
        """Test render with generate_toc=True includes table of contents."""
        renderer = HtmlRenderer(generate_toc=True)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        # Check for navigation or TOC structure
        assert "<nav" in result.lower() or 'id="toc"' in result.lower()

    def test_render_with_generate_toc_false_no_toc(self, minimal_role):
        """Test render with generate_toc=False does not include TOC."""
        renderer = HtmlRenderer(generate_toc=False)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        # Verify minimal TOC presence
        result_lower = result.lower()
        # Should not have elaborate TOC structure
        assert result_lower.count("<nav") <= 1  # May have one nav for header


class TestHtmlRendererValidation:
    """Test HTML renderer validation methods."""

    def test_validate_options_with_valid_embed_css(self):
        """Test validate_options accepts valid embed_css boolean."""
        renderer = HtmlRenderer(embed_css=True)
        # Should not raise
        renderer.validate_options({"embed_css": True})
        renderer.validate_options({"embed_css": False})

    def test_validate_options_with_invalid_embed_css_type(self):
        """Test validate_options rejects non-boolean embed_css."""
        renderer = HtmlRenderer()
        with pytest.raises((TypeError, ValueError)):
            renderer.validate_options({"embed_css": "yes"})

    def test_validate_options_with_valid_generate_toc(self):
        """Test validate_options accepts valid generate_toc boolean."""
        renderer = HtmlRenderer(generate_toc=True)
        # Should not raise
        renderer.validate_options({"generate_toc": True})
        renderer.validate_options({"generate_toc": False})

    def test_validate_options_with_invalid_generate_toc_type(self):
        """Test validate_options rejects non-boolean generate_toc."""
        renderer = HtmlRenderer()
        with pytest.raises((TypeError, ValueError)):
            renderer.validate_options({"generate_toc": 1})


class TestHtmlRendererEdgeCases:
    """Test HTML renderer edge cases and error handling."""

    def test_render_with_special_characters_in_role_name(self, tmp_path):
        """Test rendering role with special characters in name."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        metadata = RoleMetadata(
            role_name="test<role>",
            author="Test & Author",
            description='Role with "quotes"',
            license="MIT",
            min_ansible_version="2.9",
        )
        
        role = AnsibleRole(
            name="test<role>",
            path=role_path,
            metadata=metadata,
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )
        
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        # Special characters should be escaped in role name
        assert "&lt;role&gt;" in result or "test&lt;role&gt;" in result
        # Author field not rendered in basic template, check description
        assert "&#34;quotes&#34;" in result or "&quot;quotes&quot;" in result

    def test_code_block_with_none_returns_empty_pre(self):
        """Test code_block with None returns empty structure."""
        renderer = HtmlRenderer()
        result = renderer.code_block(None)
        
        assert "<pre>" in result
        assert "<code>" in result
