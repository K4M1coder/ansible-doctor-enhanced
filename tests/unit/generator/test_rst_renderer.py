"""Unit tests for RstRenderer.

T241: TDD RED phase - Write tests FIRST before implementing RstRenderer.
Tests verify reStructuredText output with Sphinx compatibility.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.rst import RstRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable


class TestRstRendererBasics:
    """Test basic RstRenderer functionality."""

    def test_format_property_returns_rst(self):
        """Test that format property returns OutputFormat.RST."""
        renderer = RstRenderer()
        assert renderer.format == OutputFormat.RST

    def test_rst_renderer_initialization(self):
        """Test RstRenderer can be initialized with options."""
        renderer = RstRenderer(sphinx_compat=True)
        assert renderer.sphinx_compat is True
        
        renderer = RstRenderer(sphinx_compat=False)
        assert renderer.sphinx_compat is False


class TestRstEscape:
    """Test RST special character escaping."""

    def test_escape_asterisk(self):
        """Test escaping asterisks used for emphasis."""
        renderer = RstRenderer()
        result = renderer.escape("*bold* text")
        assert "\\*bold\\*" in result

    def test_escape_backtick(self):
        """Test escaping backticks used for inline code."""
        renderer = RstRenderer()
        result = renderer.escape("`code` text")
        assert "\\`code\\`" in result

    def test_escape_underscore(self):
        """Test escaping underscores used for emphasis."""
        renderer = RstRenderer()
        result = renderer.escape("_italic_ text")
        assert "\\_italic\\_" in result

    def test_escape_backslash(self):
        """Test escaping backslashes."""
        renderer = RstRenderer()
        result = renderer.escape("path\\to\\file")
        assert "path\\\\to\\\\file" in result

    def test_escape_pipe(self):
        """Test escaping pipes used in tables."""
        renderer = RstRenderer()
        result = renderer.escape("column | separator")
        assert "column \\| separator" in result

    def test_escape_mixed_special_chars(self):
        """Test escaping mixed RST special characters."""
        renderer = RstRenderer()
        result = renderer.escape("*bold* with _italic_ and `code`")
        assert "\\*bold\\*" in result
        assert "\\_italic\\_" in result
        assert "\\`code\\`" in result

    def test_escape_empty_string(self):
        """Test escaping empty string returns empty."""
        renderer = RstRenderer()
        result = renderer.escape("")
        assert result == ""

    def test_escape_none(self):
        """Test escaping None returns None."""
        renderer = RstRenderer()
        result = renderer.escape(None)
        assert result is None


class TestRstCodeBlock:
    """Test RST code block generation."""

    def test_code_block_with_language(self):
        """Test code block with language specifier."""
        renderer = RstRenderer()
        result = renderer.code_block("print('hello')", "python")
        
        assert ".. code-block:: python" in result
        assert "print('hello')" in result
        assert result.startswith(".. code-block::")

    def test_code_block_without_language(self):
        """Test code block without language defaults to text."""
        renderer = RstRenderer()
        result = renderer.code_block("some code")
        
        assert ".. code-block:: text" in result
        assert "some code" in result

    def test_code_block_indentation(self):
        """Test code block content is properly indented."""
        renderer = RstRenderer()
        result = renderer.code_block("line1\nline2", "yaml")
        
        lines = result.split("\n")
        # First line is directive
        assert lines[0] == ".. code-block:: yaml"
        # Second line is blank (RST requirement)
        assert lines[1] == ""
        # Code lines are indented with 3 spaces
        assert lines[2].startswith("   ")
        assert lines[3].startswith("   ")

    def test_code_block_preserves_content(self):
        """Test code block preserves exact content."""
        renderer = RstRenderer()
        code = "key: value\nlist:\n  - item1\n  - item2"
        result = renderer.code_block(code, "yaml")
        
        # All original lines should be present (indented)
        assert "key: value" in result
        assert "list:" in result
        assert "- item1" in result
        assert "- item2" in result


class TestRstRenderWithSphinx:
    """Test RST rendering with Sphinx compatibility."""

    @pytest.fixture
    def minimal_role(self):
        """Create minimal role for testing."""
        return AnsibleRole(
            name="test-role",
            path=Path("E:/tmp/test-role").resolve(),
            metadata=RoleMetadata(
                author="Test Author",
                description="Test description",
                license="MIT",
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_render_with_sphinx_compat_true(self, minimal_role):
        """Test rendering with Sphinx directives enabled."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Should contain Sphinx directives
        assert isinstance(result, str)
        assert len(result) > 0
        # RST should have proper structure
        assert "test-role" in result or "Test Role" in result

    def test_render_with_sphinx_compat_false(self, minimal_role):
        """Test rendering without Sphinx directives."""
        renderer = RstRenderer(sphinx_compat=False)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Should render plain RST
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_includes_role_name(self, minimal_role):
        """Test that rendered RST includes role name."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Role name should appear somewhere
        assert "test-role" in result.lower()


class TestRstRendererValidation:
    """Test RstRenderer option validation."""

    def test_validate_options_accepts_valid_sphinx_compat(self):
        """Test validation accepts valid sphinx_compat boolean."""
        renderer = RstRenderer()
        
        # Should not raise
        renderer.validate_options({"sphinx_compat": True})
        renderer.validate_options({"sphinx_compat": False})

    def test_validate_options_rejects_invalid_sphinx_compat_type(self):
        """Test validation rejects non-boolean sphinx_compat."""
        renderer = RstRenderer()
        
        with pytest.raises((ValueError, TypeError)):
            renderer.validate_options({"sphinx_compat": "yes"})
        
        with pytest.raises((ValueError, TypeError)):
            renderer.validate_options({"sphinx_compat": 1})

    def test_validate_options_accepts_empty_dict(self):
        """Test validation accepts empty options dict."""
        renderer = RstRenderer()
        
        # Should not raise
        renderer.validate_options({})

    def test_validate_options_accepts_unknown_options(self):
        """Test validation ignores unknown options."""
        renderer = RstRenderer()
        
        # Should not raise - unknown options ignored
        renderer.validate_options({"unknown_option": "value"})


class TestRstRendererEdgeCases:
    """Test RstRenderer edge cases."""

    def test_escape_with_special_unicode(self):
        """Test escaping with special Unicode characters."""
        renderer = RstRenderer()
        result = renderer.escape("café with émoji 🎉")
        
        # Should preserve Unicode but escape RST chars
        assert "café" in result
        assert "🎉" in result

    def test_code_block_with_empty_code(self):
        """Test code block with empty code."""
        renderer = RstRenderer()
        result = renderer.code_block("", "python")
        
        # Should still generate directive structure
        assert ".. code-block:: python" in result
