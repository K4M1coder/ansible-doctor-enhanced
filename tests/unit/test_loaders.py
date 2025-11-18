"""Tests for template loaders."""
import pytest
from jinja2 import Template

from ansibledoctor.generator.errors import TemplateNotFoundError
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader, FileSystemTemplateLoader
from ansibledoctor.generator.output_format import OutputFormat


class TestFileSystemTemplateLoader:
    """Tests for FileSystemTemplateLoader."""

    @pytest.fixture
    def template_dir(self, tmp_path):
        """Create test template directory structure."""
        templates = tmp_path / "templates"
        templates.mkdir()
        
        # Create format-specific directories
        (templates / "markdown").mkdir()
        (templates / "html").mkdir()
        (templates / "rst").mkdir()
        
        # Create templates in format directories
        (templates / "markdown" / "role.j2").write_text("# {{ role_name }}")
        (templates / "html" / "role.j2").write_text("<h1>{{ role_name }}</h1>")
        (templates / "rst" / "role.j2").write_text("{{ role_name }}\n==========")
        
        # Create format-suffixed templates in root
        (templates / "collection.md.j2").write_text("# Collection: {{ name }}")
        (templates / "collection.html.j2").write_text("<h1>Collection: {{ name }}</h1>")
        
        # Create generic template in root
        (templates / "project.j2").write_text("Project: {{ name }}")
        
        return templates

    def test_init_with_existing_dir(self, template_dir):
        """Test initializing with existing directory."""
        loader = FileSystemTemplateLoader(template_dir)
        
        assert loader.template_dir == template_dir

    def test_init_with_nonexistent_dir(self):
        """Test initializing with non-existent directory raises error."""
        with pytest.raises(FileNotFoundError, match="Template directory not found"):
            FileSystemTemplateLoader("/nonexistent/path")

    def test_init_with_file_not_dir(self, tmp_path):
        """Test initializing with file instead of directory raises error."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        
        with pytest.raises(NotADirectoryError, match="Not a directory"):
            FileSystemTemplateLoader(file_path)

    def test_load_template_from_format_dir(self, template_dir):
        """Test loading template from format-specific directory."""
        loader = FileSystemTemplateLoader(template_dir)
        
        template = loader.load_template("role", OutputFormat.MARKDOWN)
        
        assert isinstance(template, Template)
        result = template.render(role_name="test-role")
        assert result == "# test-role"

    def test_load_template_format_suffix(self, template_dir):
        """Test loading template with format suffix."""
        loader = FileSystemTemplateLoader(template_dir)
        
        template = loader.load_template("collection", OutputFormat.MARKDOWN)
        
        result = template.render(name="my-collection")
        assert result == "# Collection: my-collection"

    def test_load_template_generic(self, template_dir):
        """Test loading generic template."""
        loader = FileSystemTemplateLoader(template_dir)
        
        template = loader.load_template("project", OutputFormat.MARKDOWN)
        
        result = template.render(name="my-project")
        assert result == "Project: my-project"

    def test_load_template_not_found(self, template_dir):
        """Test loading non-existent template raises error."""
        loader = FileSystemTemplateLoader(template_dir)
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.load_template("nonexistent", OutputFormat.MARKDOWN)
        
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.search_paths is not None

    def test_load_template_priority_format_dir(self, template_dir):
        """Test that format directory has priority over root."""
        # Create conflicting templates
        (template_dir / "test.j2").write_text("generic")
        (template_dir / "markdown" / "test.j2").write_text("format-specific")
        
        loader = FileSystemTemplateLoader(template_dir)
        template = loader.load_template("test", OutputFormat.MARKDOWN)
        
        result = template.render()
        assert result == "format-specific"

    def test_discover_templates_format_dir(self, template_dir):
        """Test discovering templates in format directory."""
        loader = FileSystemTemplateLoader(template_dir)
        
        templates = loader.discover_templates(OutputFormat.MARKDOWN)
        
        assert "role" in templates
        assert "collection" in templates
        assert "project" in templates

    def test_discover_templates_multiple_formats(self, template_dir):
        """Test discovering templates for different formats."""
        loader = FileSystemTemplateLoader(template_dir)
        
        md_templates = loader.discover_templates(OutputFormat.MARKDOWN)
        html_templates = loader.discover_templates(OutputFormat.HTML)
        
        assert "role" in md_templates
        assert "role" in html_templates
        assert "collection" in md_templates
        assert "collection" in html_templates

    def test_discover_templates_empty_format(self, tmp_path):
        """Test discovering templates for format with no templates."""
        templates = tmp_path / "templates"
        templates.mkdir()
        
        loader = FileSystemTemplateLoader(templates)
        discovered = loader.discover_templates(OutputFormat.MARKDOWN)
        
        assert discovered == []

    def test_validate_template_exists(self, template_dir):
        """Test validating existing template."""
        loader = FileSystemTemplateLoader(template_dir)
        
        assert loader.validate_template("role", OutputFormat.MARKDOWN) is True
        assert loader.validate_template("collection", OutputFormat.HTML) is True

    def test_validate_template_not_exists(self, template_dir):
        """Test validating non-existent template."""
        loader = FileSystemTemplateLoader(template_dir)
        
        assert loader.validate_template("nonexistent", OutputFormat.MARKDOWN) is False

    def test_search_paths_order(self, template_dir):
        """Test that search paths are in correct priority order."""
        loader = FileSystemTemplateLoader(template_dir)
        
        paths = loader._get_search_paths("test", OutputFormat.MARKDOWN)
        
        assert len(paths) == 3
        assert paths[0] == template_dir / "markdown" / "test.j2"
        assert paths[1] == template_dir / "test.md.j2"
        assert paths[2] == template_dir / "test.j2"


class TestEmbeddedTemplateLoader:
    """Tests for EmbeddedTemplateLoader."""

    def test_init_default_package(self):
        """Test initializing with default package."""
        loader = EmbeddedTemplateLoader()
        
        assert loader.package == "ansibledoctor.generator"
        assert loader.templates_path == "templates"

    def test_init_custom_package(self):
        """Test initializing with custom package."""
        loader = EmbeddedTemplateLoader(package="custom.package")
        
        assert loader.package == "custom.package"

    def test_load_template_not_found(self):
        """Test loading non-existent embedded template."""
        loader = EmbeddedTemplateLoader()
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.load_template("nonexistent", OutputFormat.MARKDOWN)
        
        assert "nonexistent" in str(exc_info.value)

    def test_discover_templates_no_resources(self):
        """Test discovering templates when package has no resources."""
        loader = EmbeddedTemplateLoader(package="nonexistent.package")
        
        templates = loader.discover_templates(OutputFormat.MARKDOWN)
        
        assert templates == []

    def test_validate_template_not_found(self):
        """Test validating non-existent embedded template."""
        loader = EmbeddedTemplateLoader()
        
        result = loader.validate_template("nonexistent", OutputFormat.MARKDOWN)
        
        assert result is False

    def test_read_template_not_found(self):
        """Test reading non-existent template returns None."""
        loader = EmbeddedTemplateLoader()
        
        content = loader._read_template("nonexistent", OutputFormat.MARKDOWN)
        
        assert content is None

    def test_read_template_invalid_package(self):
        """Test reading template from invalid package returns None."""
        loader = EmbeddedTemplateLoader(package="nonexistent.package")
        
        content = loader._read_template("test", OutputFormat.MARKDOWN)
        
        assert content is None

    def test_loader_with_valid_package(self):
        """Test loader initialization with valid package."""
        loader = EmbeddedTemplateLoader(package="ansibledoctor.generator")
        
        assert loader.package == "ansibledoctor.generator"
        assert loader.templates_path == "templates"

    def test_discover_returns_empty_for_missing_resources(self):
        """Test that discover returns empty list when resources are missing."""
        loader = EmbeddedTemplateLoader(package="ansibledoctor.generator")
        
        # Package exists but templates directory doesn't
        templates = loader.discover_templates(OutputFormat.MARKDOWN)
        
        # Should return empty list, not crash
        assert isinstance(templates, list)
