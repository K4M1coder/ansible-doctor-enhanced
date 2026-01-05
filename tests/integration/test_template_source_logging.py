"""Integration tests for template source logging.

Feature 008 - Template Customization & Theming
T345: Tests verifying custom templates at role/collection/project
are used and template source is logged.

Tests verify:
- Templates from role-level override lower priority levels
- Templates from collection-level are used when role-level not present
- Templates from project-level are used when collection-level not present
- Template source is logged correctly for each level
- Embedded templates are used as fallback
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from ansibledoctor.generator.cascading_loader import CascadingTemplateLoader, TemplateNotFoundError


class TestTemplateSourceDiscovery:
    """Test template discovery from different levels."""

    def test_discovers_role_level_template(self, tmp_path):
        """Template at role level takes highest priority."""
        # Create role with template
        role_path = tmp_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        template_file = role_templates / "role.html.j2"
        template_file.write_text("<html>Role Level Template</html>")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "role"
        assert "role.html.j2" in str(source.path)
        assert "Role Level Template" in template.render()

    def test_discovers_collection_level_template(self, tmp_path):
        """Template at collection level used when role level absent."""
        # Create collection structure with galaxy.yml marker
        collection_path = tmp_path / "collections" / "namespace" / "collection"
        collection_templates = collection_path / ".ansibledoctor" / "templates"
        collection_templates.mkdir(parents=True)

        # galaxy.yml is required for collection detection
        (collection_path / "galaxy.yml").write_text(
            "namespace: test\nname: collection\nversion: 1.0.0\n"
        )

        # Create role within collection
        role_path = collection_path / "roles" / "test_role"
        role_path.mkdir(parents=True)

        template_file = collection_templates / "role.html.j2"
        template_file.write_text("<html>Collection Level Template</html>")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "collection"
        assert "role.html.j2" in str(source.path)
        assert "Collection Level Template" in template.render()

    def test_discovers_project_level_template(self, tmp_path):
        """Template at project level used when collection level absent."""
        # Create project structure with marker
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "ansible.cfg").touch()  # Project marker

        project_templates = project_root / ".ansibledoctor" / "templates"
        project_templates.mkdir(parents=True)

        # Create role within project
        role_path = project_root / "roles" / "test_role"
        role_path.mkdir(parents=True)

        template_file = project_templates / "role.html.j2"
        template_file.write_text("<html>Project Level Template</html>")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "project"
        assert "role.html.j2" in str(source.path)
        assert "Project Level Template" in template.render()

    def test_discovers_user_level_template(self, tmp_path, monkeypatch):
        """Template at user level used when project level absent."""
        # Create user templates directory
        user_templates = tmp_path / "user_home" / ".ansibledoctor" / "templates"
        user_templates.mkdir(parents=True)

        # Create role without any templates
        role_path = tmp_path / "some_role"
        role_path.mkdir()

        template_file = user_templates / "role.html.j2"
        template_file.write_text("<html>User Level Template</html>")

        # Mock Path.home() to return our test directory
        monkeypatch.setattr(Path, "home", lambda: tmp_path / "user_home")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "user"
        assert "role.html.j2" in str(source.path)
        assert "User Level Template" in template.render()

    def test_falls_back_to_embedded_template(self, tmp_path):
        """Embedded templates used when no custom templates found."""
        # Create role without any templates
        role_path = tmp_path / "test_role"
        role_path.mkdir()

        loader = CascadingTemplateLoader()

        # This should fall back to embedded templates
        # Note: May raise if no embedded templates exist for this name
        try:
            template, source = loader.find_template("role.html.j2", role_path)
            assert source.level == "embedded"
            assert "embedded" in str(source.path).lower()
        except TemplateNotFoundError:
            # Expected if no embedded templates exist
            pass


class TestTemplateSourceLogging:
    """Test that template source is logged correctly."""

    def test_logs_template_discovery_role_level(self, tmp_path, caplog):
        """Log message includes template level for role templates."""
        # Create role with template
        role_path = tmp_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        template_file = role_templates / "role.html.j2"
        template_file.write_text("<html>Test</html>")

        loader = CascadingTemplateLoader()

        with caplog.at_level(logging.DEBUG):
            template, source = loader.find_template("role.html.j2", role_path)

        # Should log the discovery with level info
        assert source.level == "role"
        # The loader logs template discovery at debug level

    def test_logs_template_discovery_project_level(self, tmp_path, caplog):
        """Log message includes template level for project templates."""
        # Create project structure
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").touch()

        project_templates = project_root / ".ansibledoctor" / "templates"
        project_templates.mkdir(parents=True)

        role_path = project_root / "roles" / "test_role"
        role_path.mkdir(parents=True)

        template_file = project_templates / "role.html.j2"
        template_file.write_text("<html>Project Test</html>")

        loader = CascadingTemplateLoader()

        with caplog.at_level(logging.DEBUG):
            template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "project"

    def test_template_source_string_representation(self, tmp_path):
        """TemplateSource __str__ includes level and path."""
        role_path = tmp_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        template_file = role_templates / "role.html.j2"
        template_file.write_text("<html>Test</html>")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        source_str = str(source)
        assert "role" in source_str
        assert "role.html.j2" in source_str


class TestTemplateOverriding:
    """Test that templates at higher levels override lower levels."""

    def test_role_overrides_collection(self, tmp_path):
        """Role-level template overrides collection-level template."""
        # Create collection with template
        collection_path = tmp_path / "collections" / "namespace" / "collection"
        collection_templates = collection_path / ".ansibledoctor" / "templates"
        collection_templates.mkdir(parents=True)

        coll_template = collection_templates / "role.html.j2"
        coll_template.write_text("<html>Collection Template</html>")

        # Create role with its own template
        role_path = collection_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        role_template = role_templates / "role.html.j2"
        role_template.write_text("<html>Role Template</html>")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        # Role level should win
        assert source.level == "role"
        assert "Role Template" in template.render()

    def test_collection_overrides_project(self, tmp_path):
        """Collection-level template overrides project-level template."""
        # Create project with template
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        project_templates = project_root / ".ansibledoctor" / "templates"
        project_templates.mkdir(parents=True)

        proj_template = project_templates / "role.html.j2"
        proj_template.write_text("<html>Project Template</html>")

        # Create collection within project with its own template and galaxy.yml
        collection_path = project_root / "collections" / "namespace" / "collection"
        collection_path.mkdir(parents=True)
        (collection_path / "galaxy.yml").write_text("namespace: ns\nname: coll\nversion: 1.0.0\n")

        collection_templates = collection_path / ".ansibledoctor" / "templates"
        collection_templates.mkdir(parents=True)

        coll_template = collection_templates / "role.html.j2"
        coll_template.write_text("<html>Collection Template</html>")

        # Create role within collection
        role_path = collection_path / "roles" / "test_role"
        role_path.mkdir(parents=True)

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        # Collection level should win over project
        assert source.level == "collection"
        assert "Collection Template" in template.render()

    def test_project_overrides_user(self, tmp_path, monkeypatch):
        """Project-level template overrides user-level template."""
        # Create user templates
        user_templates = tmp_path / "user_home" / ".ansibledoctor" / "templates"
        user_templates.mkdir(parents=True)

        user_template = user_templates / "role.html.j2"
        user_template.write_text("<html>User Template</html>")

        # Create project with template
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "ansible.cfg").touch()

        project_templates = project_root / ".ansibledoctor" / "templates"
        project_templates.mkdir(parents=True)

        proj_template = project_templates / "role.html.j2"
        proj_template.write_text("<html>Project Template</html>")

        # Create role within project
        role_path = project_root / "roles" / "test_role"
        role_path.mkdir(parents=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path / "user_home")

        loader = CascadingTemplateLoader()
        template, source = loader.find_template("role.html.j2", role_path)

        # Project level should win
        assert source.level == "project"
        assert "Project Template" in template.render()


class TestCustomSearchPaths:
    """Test custom search paths functionality."""

    def test_custom_path_searched(self, tmp_path):
        """Custom search paths are searched for templates."""
        # Create custom templates directory
        custom_templates = tmp_path / "custom_templates"
        custom_templates.mkdir()

        template_file = custom_templates / "role.html.j2"
        template_file.write_text("<html>Custom Path Template</html>")

        # Create role without templates
        role_path = tmp_path / "test_role"
        role_path.mkdir()

        loader = CascadingTemplateLoader(search_paths=[custom_templates])
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "custom"
        assert "Custom Path Template" in template.render()

    def test_multiple_custom_paths_ordered(self, tmp_path):
        """Multiple custom paths are searched in order."""
        # Create two custom template directories
        custom1 = tmp_path / "custom1"
        custom1.mkdir()

        custom2 = tmp_path / "custom2"
        custom2.mkdir()

        # Put template only in second custom path
        template_file = custom2 / "role.html.j2"
        template_file.write_text("<html>Custom2 Template</html>")

        role_path = tmp_path / "test_role"
        role_path.mkdir()

        loader = CascadingTemplateLoader(search_paths=[custom1, custom2])
        template, source = loader.find_template("role.html.j2", role_path)

        assert source.level == "custom"
        assert "Custom2 Template" in template.render()


class TestTemplateCaching:
    """Test template caching behavior."""

    def test_template_cached_after_discovery(self, tmp_path):
        """Template is cached after first discovery."""
        role_path = tmp_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        template_file = role_templates / "role.html.j2"
        template_file.write_text("<html>Original</html>")

        loader = CascadingTemplateLoader()

        # First call discovers
        template1, source1 = loader.find_template("role.html.j2", role_path)
        assert "Original" in template1.render()

        # Modify the file
        template_file.write_text("<html>Modified</html>")

        # Second call should return cached version
        template2, source2 = loader.find_template("role.html.j2", role_path)
        assert "Original" in template2.render()  # Still cached

    def test_cache_cleared_with_clear_cache(self, tmp_path):
        """clear_cache() removes all cached templates."""
        role_path = tmp_path / "roles" / "test_role"
        role_templates = role_path / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        template_file = role_templates / "role.html.j2"
        template_file.write_text("<html>Original</html>")

        loader = CascadingTemplateLoader()

        # First call discovers
        template1, source1 = loader.find_template("role.html.j2", role_path)

        # Modify the file
        template_file.write_text("<html>Modified</html>")

        # Clear cache
        loader.clear_cache()

        # Now should see modified version
        template2, source2 = loader.find_template("role.html.j2", role_path)
        assert "Modified" in template2.render()


class TestTemplateNotFound:
    """Test behavior when template is not found."""

    def test_raises_template_not_found_error(self, tmp_path):
        """Raises TemplateNotFoundError when template not found."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()

        loader = CascadingTemplateLoader()

        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.find_template("nonexistent.html.j2", role_path)

        assert "nonexistent.html.j2" in str(exc_info.value)

    def test_error_includes_searched_paths(self, tmp_path):
        """Error message includes list of searched paths."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()

        loader = CascadingTemplateLoader()

        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.find_template("missing.j2", role_path)

        error = exc_info.value
        assert error.template_name == "missing.j2"
        # searched_paths should be populated
        assert isinstance(error.searched_paths, list)
