"""Integration tests for documentation generator."""
import pytest
from pathlib import Path
from datetime import datetime

from ansibledoctor.generator import (
    TemplateEngine,
    FileSystemTemplateLoader,
    TemplateContext,
    OutputFormat,
)
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable, Tag, TodoItem, Example


@pytest.fixture
def complete_role(tmp_path):
    """Create a complete role with all features."""
    role_path = tmp_path / "complete-role"
    role_path.mkdir()
    
    # Create role with full metadata
    role = AnsibleRole(name="complete-role", path=role_path)
    role.metadata = RoleMetadata(
        author="Test Author",
        description="A complete test role with all features",
        license="MIT",
        min_ansible_version="2.14",
        platforms=[{"name": "Ubuntu", "versions": ["20.04", "22.04"]}],
        dependencies=[{"name": "geerlingguy.docker", "version": ">=6.0.0"}],
    )
    
    # Add variables
    role.variables = [
        Variable(
            name="app_port",
            value=8080,
            type="number",
            source="defaults",
            description="Application HTTP port",
            required=True,
        ),
        Variable(
            name="app_name",
            value="myapp",
            type="string",
            source="defaults",
            description="Application name",
            required=False,
        ),
        Variable(
            name="enable_ssl",
            value=True,
            type="boolean",
            source="vars",
            description="Enable SSL/TLS",
            required=False,
        ),
    ]
    
    # Add tags
    role.tags = [
        Tag(name="install", description="Installation tasks", usage_count=5),
        Tag(name="config", description="Configuration tasks", usage_count=3),
        Tag(name="service", description="Service management", usage_count=2),
    ]
    
    # Add TODOs
    role.todos = [
        TodoItem(
            description="Add support for custom SSL certificates",
            file_path=str(role_path / "tasks" / "main.yml"),
            line_number=45,
            priority="high",
        ),
        TodoItem(
            description="Improve error handling in service restart",
            file_path=str(role_path / "handlers" / "main.yml"),
            line_number=12,
            priority="medium",
        ),
        TodoItem(
            description="Add more configuration examples",
            file_path=str(role_path / "README.md"),
            line_number=89,
            priority="low",
        ),
    ]
    
    # Add examples
    role.examples = [
        Example(
            title="Basic Usage",
            code="""- hosts: webservers
  roles:
    - role: complete-role
      vars:
        app_port: 8080
        app_name: myapp""",
            description="Basic role usage with default settings",
            language="yaml",
        ),
        Example(
            title="With SSL Enabled",
            code="""- hosts: webservers
  roles:
    - role: complete-role
      vars:
        app_port: 443
        enable_ssl: true""",
            description="Enable SSL/TLS for secure connections",
            language="yaml",
        ),
    ]
    
    return role


@pytest.fixture
def templates_dir():
    """Get path to default templates."""
    return Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"


class TestEndToEndGeneration:
    """End-to-end tests for complete generation pipeline."""

    def test_markdown_generation_complete_workflow(self, complete_role, templates_dir):
        """Test complete Markdown generation workflow."""
        # Setup
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        template = engine.get_template("markdown/role.j2")
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        # Render
        content = template.render(**context.to_dict())
        
        # Validate result
        assert content
        assert "# complete-role" in content
        assert "## Variables" in content
        assert "## Tags" in content
        assert "## TODOs" in content
        assert "## Examples" in content
        
        # Check variables rendered
        assert "app_port" in content
        assert "8080" in content
        assert "Application HTTP port" in content
        
        # Check tags rendered
        assert "install" in content
        assert "5" in content  # usage count
        
        # Check TODOs rendered
        assert "custom SSL certificates" in content
        
        # Check examples rendered
        assert "Basic Usage" in content
        assert "- hosts: webservers" in content

    def test_html_generation_complete_workflow(self, complete_role, templates_dir):
        """Test complete HTML generation workflow."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        template = engine.get_template("html/role.j2")
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.HTML,
        )
        
        content = template.render(**context.to_dict())
        
        assert content
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<h1>complete-role" in content or ">complete-role<" in content
        
        # Check generation metadata
        assert "0.3.0" in content

    def test_rst_generation_complete_workflow(self, complete_role, templates_dir):
        """Test complete RST generation workflow."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        template = engine.get_template("rst/role.j2")
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.RST,
        )
        
        content = template.render(**context.to_dict())
        
        assert content
        assert "complete-role" in content
        assert "Variables" in content
        assert "========" in content  # RST heading underlines
        
        # Check generation metadata
        assert "0.3.0" in content


class TestTemplateEngineIntegration:
    """Tests for TemplateEngine integration."""

    def test_load_and_render_markdown_template(self, complete_role, templates_dir):
        """Test loading and rendering Markdown template."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        template = engine.get_template("markdown/role.j2")
        
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        )
        
        content = template.render(**context.to_dict())
        
        assert content
        assert "complete-role" in content
        assert "Variables" in content

    def test_custom_filters_available(self, templates_dir):
        """Test that custom filters are available in engine."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        
        # Check filters registered
        assert "markdown_escape" in engine.environment.filters
        assert "rst_escape" in engine.environment.filters
        assert "code_fence" in engine.environment.filters
        assert "format_priority" in engine.environment.filters
        assert "html_attrs" in engine.environment.filters
        assert "list_items" in engine.environment.filters

    def test_loader_discovery(self, templates_dir):
        """Test that loader can discover templates."""
        loader = FileSystemTemplateLoader(templates_dir)
        
        # Discover Markdown templates
        md_templates = loader.discover_templates(OutputFormat.MARKDOWN)
        assert "role" in md_templates
        
        # Discover HTML templates
        html_templates = loader.discover_templates(OutputFormat.HTML)
        assert "role" in html_templates
        
        # Discover RST templates
        rst_templates = loader.discover_templates(OutputFormat.RST)
        assert "role" in rst_templates


class TestAllFormatsConsistency:
    """Tests for consistency across all output formats."""

    def test_all_formats_render_same_role(self, complete_role, templates_dir):
        """Test that all formats can render the same role."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        
        # Render in all formats
        md_template = engine.get_template("markdown/role.j2")
        html_template = engine.get_template("html/role.j2")
        rst_template = engine.get_template("rst/role.j2")
        
        context_data = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 1, 12, 0, 0),
            output_format=OutputFormat.MARKDOWN,
        ).to_dict()
        
        md_content = md_template.render(**context_data)
        html_content = html_template.render(**context_data)
        rst_content = rst_template.render(**context_data)
        
        # All should have content
        assert md_content
        assert html_content
        assert rst_content
        
        # All should contain role name
        assert "complete-role" in md_content
        assert "complete-role" in html_content
        assert "complete-role" in rst_content

    def test_all_formats_handle_empty_role(self, tmp_path, templates_dir):
        """Test that all formats handle minimal role."""
        role_path = tmp_path / "minimal-role"
        role_path.mkdir()
        
        role = AnsibleRole(name="minimal-role", path=role_path)
        role.metadata = RoleMetadata(description="Minimal role")
        
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        md_template = engine.get_template("markdown/role.j2")
        html_template = engine.get_template("html/role.j2")
        rst_template = engine.get_template("rst/role.j2")
        
        context_data = TemplateContext(
            role=role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        ).to_dict()
        
        # All formats should handle empty collections
        md_content = md_template.render(**context_data)
        html_content = html_template.render(**context_data)
        rst_content = rst_template.render(**context_data)
        
        assert md_content
        assert html_content
        assert rst_content


class TestErrorHandling:
    """Tests for error handling in generation pipeline."""

    def test_missing_template_handled(self, templates_dir):
        """Test handling of missing template."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        
        with pytest.raises(Exception):  # Could be TemplateNotFoundError or Jinja2 error
            engine.get_template("nonexistent/template.j2")

    def test_template_validation(self, templates_dir):
        """Test template validation."""
        from ansibledoctor.generator.validator import TemplateValidator
        
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        validator = TemplateValidator(engine.environment)
        
        # Test valid template
        template_path = templates_dir / "markdown" / "role.j2"
        validator.validate_file(template_path)  # Should not raise


class TestMetadataGeneration:
    """Tests for metadata in generated content."""

    def test_generation_metadata_appears(self, complete_role, templates_dir):
        """Test that generation metadata appears in output."""
        engine = TemplateEngine.create(template_dir=str(templates_dir))
        template = engine.get_template("markdown/role.j2")
        
        gen_date = datetime(2024, 1, 1, 12, 0, 0)
        context = TemplateContext(
            role=complete_role,
            generator_version="0.3.0",
            generation_date=gen_date,
            output_format=OutputFormat.MARKDOWN,
        )
        
        content = template.render(**context.to_dict())
        
        # Check that generation metadata appears in content
        assert "0.3.0" in content
        assert "2024-01-01" in content

    def test_output_format_extensions(self):
        """Test that output formats have correct file extensions."""
        assert OutputFormat.MARKDOWN.file_extension == ".md"
        assert OutputFormat.HTML.file_extension == ".html"
        assert OutputFormat.RST.file_extension == ".rst"
