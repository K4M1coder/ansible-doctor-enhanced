"""Tests for Markdown renderer.

Following TDD - these tests are written FIRST before implementation.
T216: MarkdownRenderer unit tests covering all methods and edge cases.
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable


class TestMarkdownRendererBasics:
    """Test basic MarkdownRenderer properties and initialization."""

    def test_format_property_returns_markdown(self):
        """Test format property returns OutputFormat.MARKDOWN."""
        renderer = MarkdownRenderer()
        assert renderer.format == OutputFormat.MARKDOWN

    def test_renderer_initializes_successfully(self):
        """Test renderer can be instantiated without errors."""
        renderer = MarkdownRenderer()
        assert renderer is not None
        assert hasattr(renderer, "render")
        assert hasattr(renderer, "escape")
        assert hasattr(renderer, "code_block")


class TestMarkdownEscape:
    """Test Markdown special character escaping."""

    def test_escape_asterisks(self):
        """Test escaping * characters."""
        renderer = MarkdownRenderer()
        assert renderer.escape("*bold*") == r"\*bold\*"

    def test_escape_underscores(self):
        """Test escaping _ characters."""
        renderer = MarkdownRenderer()
        assert renderer.escape("_italic_") == r"\_italic\_"

    def test_escape_square_brackets(self):
        """Test escaping [ and ] characters."""
        renderer = MarkdownRenderer()
        assert renderer.escape("[link]") == r"\[link\]"

    def test_escape_backticks(self):
        """Test escaping ` characters."""
        renderer = MarkdownRenderer()
        assert renderer.escape("`code`") == r"\`code\`"

    def test_escape_hashes(self):
        """Test escaping # characters."""
        renderer = MarkdownRenderer()
        assert renderer.escape("# heading") == r"\# heading"

    def test_escape_mixed_special_chars(self):
        """Test escaping multiple special characters."""
        renderer = MarkdownRenderer()
        text = "*bold* _italic_ [link] `code` # heading"
        expected = r"\*bold\* \_italic\_ \[link\] \`code\` \# heading"
        assert renderer.escape(text) == expected

    def test_escape_empty_string(self):
        """Test escaping empty string."""
        renderer = MarkdownRenderer()
        assert renderer.escape("") == ""

    def test_escape_none_returns_empty(self):
        """Test escaping None returns empty string."""
        renderer = MarkdownRenderer()
        assert renderer.escape(None) == ""


class TestMarkdownCodeBlock:
    """Test Markdown code block generation."""

    def test_code_block_with_language(self):
        """Test code block with language hint."""
        renderer = MarkdownRenderer()
        code = "def hello():\n    print('world')"
        result = renderer.code_block(code, language="python")
        assert result.startswith("```python\n")
        assert result.endswith("\n```")
        assert "def hello():" in result

    def test_code_block_without_language(self):
        """Test code block without language hint."""
        renderer = MarkdownRenderer()
        code = "some code"
        result = renderer.code_block(code)
        assert result.startswith("```\n")
        assert result.endswith("\n```")
        assert "some code" in result

    def test_code_block_empty_code(self):
        """Test code block with empty code."""
        renderer = MarkdownRenderer()
        result = renderer.code_block("")
        assert result == "```\n\n```"

    def test_code_block_multiline(self):
        """Test code block with multiple lines."""
        renderer = MarkdownRenderer()
        code = "line1\nline2\nline3"
        result = renderer.code_block(code, language="yaml")
        assert "```yaml\n" in result
        assert "line1\nline2\nline3\n```" in result


class TestMarkdownRendererWithMinimalData:
    """Test rendering with minimal role data."""

    @pytest.fixture
    def minimal_role(self):
        """Create minimal role with required fields only."""
        return AnsibleRole(
            name="test-role",
            path=Path("E:/tmp/test-role").resolve(),
            metadata=RoleMetadata(
                author="Test Author",
                description="Test role description",
                license="MIT",
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_render_minimal_role(self, minimal_role):
        """Test rendering minimal role with only required fields."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        assert "test-role" in result
        assert "Test Author" in result
        assert "Test role description" in result
        assert "MIT" in result

    def test_render_minimal_role_no_variables_section(self, minimal_role):
        """Test minimal role doesn't render empty Variables section."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=minimal_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        # Should mention no variables, not render empty section
        assert "## Variables" not in result or "No variables defined" in result.lower()


class TestMarkdownRendererWithCompleteData:
    """Test rendering with complete role data."""

    @pytest.fixture
    def complete_role(self):
        """Create complete role with all fields populated."""
        return AnsibleRole(
            name="complete-role",
            path=Path("E:/tmp/complete-role").resolve(),
            metadata=RoleMetadata(
                author="Complete Author",
                description="Complete role description",
                license="Apache-2.0",
                company="Test Company",
            ),
            variables=[
                Variable(
                    name="app_port",
                    value=8080,
                    type="number",
                    description="Application port",
                    source="defaults/main.yml",
                ),
                Variable(
                    name="app_debug",
                    value=False,
                    type="boolean",
                    description="Enable debug mode",
                    source="defaults/main.yml",
                ),
            ],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_render_complete_role_has_all_sections(self, complete_role):
        """Test complete role renders all populated sections."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        # Check role name and metadata
        assert "complete-role" in result
        assert "Complete Author" in result
        assert "Complete role description" in result
        
        # Check variables section exists (names are escaped in Markdown)
        assert "app_port" in result or "app\\_port" in result
        assert "app_debug" in result or "app\\_debug" in result
        assert "Application port" in result
        assert "Enable debug mode" in result

    def test_render_complete_role_includes_metadata(self, complete_role):
        """Test complete role includes generation metadata."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        # Check generation metadata appears
        assert "0.3.0" in result


class TestMarkdownRendererWithMissingFields:
    """Test rendering with missing optional fields."""

    @pytest.fixture
    def role_without_examples(self):
        """Create role without examples."""
        return AnsibleRole(
            name="no-examples-role",
            path=Path("E:/tmp/no-examples-role").resolve(),
            metadata=RoleMetadata(
                author="Test Author",
                description="Role without examples",
                license="MIT",
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],  # Empty examples
        )

    def test_render_without_examples(self, role_without_examples):
        """Test rendering role without examples."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=role_without_examples,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        # Should not crash, should mention role name
        assert "no-examples-role" in result
        assert "Test Author" in result


class TestMarkdownRendererCustomTemplate:
    """Test rendering with custom template path."""

    def test_render_with_custom_template_path(self, tmp_path):
        """Test rendering with custom template path."""
        # Create custom template
        custom_template = tmp_path / "custom.j2"
        custom_template.write_text(
            "# {{ role.name }}\nCustom template by {{ role.metadata.author }}"
        )
        
        role = AnsibleRole(
            name="custom-role",
            path=Path("E:/tmp/custom-role").resolve(),
            metadata=RoleMetadata(
                author="Custom Author",
                description="Custom description",
                license="MIT",
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )
        
        renderer = MarkdownRenderer(template_path=str(custom_template))
        context = TemplateContext(
            role=role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        result = renderer.render(context)
        
        assert "custom-role" in result
        assert "Custom template by Custom Author" in result


class TestMarkdownRendererValidation:
    """Test renderer validation methods."""

    def test_validate_options_accepts_valid_options(self):
        """Test validate_options accepts valid gfm_mode option."""
        renderer = MarkdownRenderer()
        # Should not raise
        renderer.validate_options({"gfm_mode": True})
        renderer.validate_options({"gfm_mode": False})
        renderer.validate_options({})

    def test_validate_options_rejects_invalid_gfm_mode(self):
        """Test validate_options rejects invalid gfm_mode type."""
        renderer = MarkdownRenderer()
        with pytest.raises((TypeError, ValueError)):
            renderer.validate_options({"gfm_mode": "yes"})


class TestMarkdownRendererThreadSafety:
    """Test thread safety for concurrent rendering."""

    def test_concurrent_renders_dont_interfere(self):
        """Test multiple concurrent renders don't interfere with each other."""
        from concurrent.futures import ThreadPoolExecutor
        
        renderer = MarkdownRenderer()
        
        def render_role(name):
            role = AnsibleRole(
                name=name,
                path=Path(f"E:/tmp/{name}").resolve(),
                metadata=RoleMetadata(
                    author=f"Author {name}",
                    description=f"Description {name}",
                    license="MIT",
                ),
                variables=[],
                tags=[],
                todos=[],
                examples=[],
            )
            context = TemplateContext(
                role=role,
                generator_version="0.3.0",
                generation_date=datetime(2024, 1, 1, 12, 0, 0),
                output_format=OutputFormat.MARKDOWN,
            )
            return renderer.render(context)
        
        # Render 10 roles concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(render_role, [f"role{i}" for i in range(10)]))
        
        # Each result should contain its own role name
        for i, result in enumerate(results):
            assert f"role{i}" in result
            assert f"Author role{i}" in result
