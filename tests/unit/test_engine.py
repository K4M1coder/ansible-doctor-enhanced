"""Tests for TemplateEngine."""
import pytest
from jinja2 import Environment, StrictUndefined, TemplateNotFound, UndefinedError

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.filters import FILTERS


class TestTemplateEngineCreation:
    """Tests for TemplateEngine.create() factory method."""

    def test_create_without_template_dir(self):
        """Test creating engine without template directory."""
        engine = TemplateEngine.create()
        
        assert isinstance(engine, TemplateEngine)
        assert isinstance(engine.environment, Environment)

    def test_create_with_template_dir(self, tmp_path):
        """Test creating engine with template directory."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        engine = TemplateEngine.create(template_dir=template_dir)
        
        assert engine.environment.loader is not None

    def test_create_with_nonexistent_dir(self):
        """Test creating engine with non-existent directory raises error."""
        with pytest.raises(FileNotFoundError, match="Template directory not found"):
            TemplateEngine.create(template_dir="/nonexistent/path")

    def test_create_with_autoescape(self):
        """Test creating engine with autoescape enabled."""
        engine = TemplateEngine.create(autoescape=True)
        
        assert engine.environment.autoescape is True

    def test_create_with_strict_undefined(self):
        """Test creating engine with strict undefined handling."""
        engine = TemplateEngine.create(strict_undefined=True)
        
        assert engine.environment.undefined is StrictUndefined

    def test_create_with_custom_jinja_options(self):
        """Test passing custom Jinja2 options."""
        engine = TemplateEngine.create(
            trim_blocks=False,
            lstrip_blocks=False,
        )
        
        assert engine.environment.trim_blocks is False
        assert engine.environment.lstrip_blocks is False

    def test_create_registers_custom_filters(self):
        """Test that custom filters are registered."""
        engine = TemplateEngine.create()
        
        for filter_name in FILTERS.keys():
            assert filter_name in engine.filters


class TestTemplateEngineRendering:
    """Tests for template rendering methods."""

    def test_render_string_simple(self):
        """Test rendering simple template string."""
        engine = TemplateEngine.create()
        result = engine.render_string("Hello {{ name }}", name="World")
        
        assert result == "Hello World"

    def test_render_string_with_filter(self):
        """Test rendering with custom filter."""
        engine = TemplateEngine.create()
        template_str = "{{ text | markdown_escape }}"
        result = engine.render_string(template_str, text="*bold*")
        
        assert result == "\\*bold\\*"

    def test_render_string_with_multiple_filters(self):
        """Test rendering with multiple custom filters."""
        engine = TemplateEngine.create()
        template_str = """
        {{ code | code_fence("python") }}
        {{ priority | format_priority }}
        """
        result = engine.render_string(
            template_str,
            code="print('hello')",
            priority="high"
        )
        
        assert "```python" in result
        assert "print('hello')" in result
        assert "🔴 High" in result

    def test_render_string_strict_undefined(self):
        """Test that strict undefined raises error."""
        engine = TemplateEngine.create(strict_undefined=True)
        
        with pytest.raises(UndefinedError):
            engine.render_string("{{ undefined_var }}")

    def test_render_string_with_trim_blocks(self):
        """Test that trim_blocks removes trailing newlines."""
        engine = TemplateEngine.create(trim_blocks=True, lstrip_blocks=True)
        template_str = """
        {% if true %}
        Content
        {% endif %}
        """
        result = engine.render_string(template_str)
        
        # Should not have excessive whitespace
        assert result.strip() == "Content"

    def test_get_template(self, tmp_path):
        """Test getting template from file."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        template_file = template_dir / "test.j2"
        template_file.write_text("Hello {{ name }}")
        
        engine = TemplateEngine.create(template_dir=template_dir)
        template = engine.get_template("test.j2")
        result = template.render(name="World")
        
        assert result == "Hello World"

    def test_get_template_not_found(self, tmp_path):
        """Test getting non-existent template raises error."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        engine = TemplateEngine.create(template_dir=template_dir)
        
        with pytest.raises(TemplateNotFound):
            engine.get_template("nonexistent.j2")


class TestTemplateEngineProperties:
    """Tests for TemplateEngine properties."""

    def test_environment_property(self):
        """Test accessing environment property."""
        engine = TemplateEngine.create()
        
        assert isinstance(engine.environment, Environment)

    def test_filters_property(self):
        """Test accessing filters property."""
        engine = TemplateEngine.create()
        filters = engine.filters
        
        assert isinstance(filters, dict)
        assert "markdown_escape" in filters
        assert "code_fence" in filters
        assert "format_priority" in filters

    def test_filters_property_is_copy(self):
        """Test that filters property returns a copy."""
        engine = TemplateEngine.create()
        filters1 = engine.filters
        filters2 = engine.filters
        
        # Should be equal but different objects
        assert filters1 == filters2
        assert filters1 is not filters2


class TestTemplateEngineIntegration:
    """Integration tests for complete rendering workflows."""

    def test_full_rendering_workflow(self, tmp_path):
        """Test complete workflow from template file to output."""
        # Create template directory and file
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        
        template_content = """
        # {{ role_name }}
        
        {{ description | markdown_escape }}
        
        ## Variables
        
        {{ variables | list_items }}
        """
        
        (template_dir / "role.md.j2").write_text(template_content)
        
        # Create engine and render
        engine = TemplateEngine.create(template_dir=template_dir)
        template = engine.get_template("role.md.j2")
        
        result = template.render(
            role_name="my-role",
            description="A *test* role",
            variables=["var1", "var2", "var3"]
        )
        
        # Verify output
        assert "# my-role" in result
        assert "A \\*test\\* role" in result
        assert "- var1" in result
        assert "- var2" in result
        assert "- var3" in result

    def test_rendering_with_all_filters(self):
        """Test rendering using all custom filters."""
        engine = TemplateEngine.create()
        
        template_str = """
        Markdown: {{ md_text | markdown_escape }}
        RST: {{ rst_text | rst_escape }}
        Code: {{ code | code_fence("python") }}
        Priority: {{ priority | format_priority }}
        Attrs: <div {{ attrs | html_attrs }}>
        List: {{ items | list_items(ordered=True) }}
        """
        
        result = engine.render_string(
            template_str,
            md_text="**bold**",
            rst_text="*emphasis*",
            code="print('hello')",
            priority="critical",
            attrs={"class": "container", "id": "main"},
            items=["first", "second"]
        )
        
        assert "\\*\\*bold\\*\\*" in result
        assert "\\*emphasis\\*" in result
        assert "```python" in result
        assert "🚨 Critical" in result
        assert 'class="container"' in result
        assert "1. first" in result
