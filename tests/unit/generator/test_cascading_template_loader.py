"""Unit tests for CascadingTemplateLoader.

Feature 008 - Template Customization & Theming
T334: TDD unit tests for template discovery order and caching behavior
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from ansibledoctor.generator.cascading_loader import (
    CascadingTemplateLoader,
    TemplateNotFoundError,
    TemplateSource,
)


class TestTemplateSource:
    """Test TemplateSource dataclass."""

    def test_template_source_creation(self):
        """TemplateSource should hold path, level, and discovery time."""
        now = datetime.now()
        source = TemplateSource(
            path=Path("/test/templates/role.html.j2"),
            level="role",
            discovered_at=now,
        )
        assert source.path == Path("/test/templates/role.html.j2")
        assert source.level == "role"
        assert source.discovered_at == now

    def test_template_source_is_frozen(self):
        """TemplateSource should be immutable."""
        source = TemplateSource(
            path=Path("/test/templates/role.html.j2"),
            level="role",
            discovered_at=datetime.now(),
        )
        with pytest.raises(AttributeError):  # pydantic frozen model raises AttributeError
            source.level = "collection"  # type: ignore[misc]

    def test_template_source_str_format(self):
        """TemplateSource string should show level:path."""
        source = TemplateSource(
            path=Path("/test/templates/role.html.j2"),
            level="role",
            discovered_at=datetime.now(),
        )
        # Note: On Windows, Path uses backslashes
        result = str(source)
        assert result.startswith("role:")
        assert "role.html.j2" in result

    def test_template_source_equality(self):
        """Two TemplateSource with same values should be equal."""
        now = datetime.now()
        source1 = TemplateSource(
            path=Path("/test/role.html.j2"),
            level="role",
            discovered_at=now,
        )
        source2 = TemplateSource(
            path=Path("/test/role.html.j2"),
            level="role",
            discovered_at=now,
        )
        assert source1 == source2


class TestCascadingTemplateLoaderInit:
    """Test CascadingTemplateLoader initialization."""

    def test_default_cache_ttl(self):
        """Default cache TTL should be 300 seconds."""
        loader = CascadingTemplateLoader()
        assert loader.cache_ttl == 300

    def test_custom_cache_ttl(self):
        """Cache TTL can be customized."""
        loader = CascadingTemplateLoader(cache_ttl=600)
        assert loader.cache_ttl == 600

    def test_empty_search_paths_by_default(self):
        """Search paths should be empty by default."""
        loader = CascadingTemplateLoader()
        assert loader.search_paths == []

    def test_custom_search_paths(self):
        """Custom search paths can be provided."""
        paths = [Path("/custom/templates"), Path("/other/templates")]
        loader = CascadingTemplateLoader(search_paths=paths)
        assert loader.search_paths == paths


class TestDiscoveryOrder:
    """Test template discovery priority order."""

    @pytest.fixture
    def loader(self):
        """Create a CascadingTemplateLoader instance."""
        return CascadingTemplateLoader()

    def test_role_templates_highest_priority(self, loader, tmp_path):
        """Role-level templates should have highest priority."""
        # Create role template
        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Role</html>")

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "role"
        assert source.path == role_templates / "role.html.j2"

    def test_collection_templates_second_priority(self, loader, tmp_path):
        """Collection-level templates should override project/user/embedded."""
        # Create collection structure
        collection_dir = tmp_path / "my_collection"
        collection_dir.mkdir()
        (collection_dir / "galaxy.yml").write_text("namespace: test")

        roles_dir = collection_dir / "roles"
        roles_dir.mkdir()
        role_dir = roles_dir / "my_role"
        role_dir.mkdir()

        # Create collection template (not role template)
        coll_templates = collection_dir / ".ansibledoctor" / "templates"
        coll_templates.mkdir(parents=True)
        (coll_templates / "role.html.j2").write_text("<html>Collection</html>")

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "collection"
        assert source.path == coll_templates / "role.html.j2"

    def test_project_templates_third_priority(self, loader, tmp_path):
        """Project-level templates should override user/embedded."""
        # Create project structure with ansible.cfg
        project_dir = tmp_path / "ansible_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]")

        roles_dir = project_dir / "roles"
        roles_dir.mkdir()
        role_dir = roles_dir / "my_role"
        role_dir.mkdir()

        # Create project template
        proj_templates = project_dir / ".ansibledoctor" / "templates"
        proj_templates.mkdir(parents=True)
        (proj_templates / "role.html.j2").write_text("<html>Project</html>")

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "project"
        assert source.path == proj_templates / "role.html.j2"

    def test_user_templates_fourth_priority(self, loader, tmp_path, monkeypatch):
        """User-level templates should override embedded."""
        # Mock home directory
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        user_templates = fake_home / ".ansibledoctor" / "templates"
        user_templates.mkdir(parents=True)
        (user_templates / "role.html.j2").write_text("<html>User</html>")

        # Create a role without any local templates
        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "user"
        assert source.path == user_templates / "role.html.j2"

    def test_embedded_templates_fallback(self, loader, tmp_path):
        """Embedded templates should be used as fallback."""
        # Create a role without any templates
        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        # Should fall back to embedded templates
        # Use actual embedded template name (html/role.j2)
        template, source = loader.find_template("html/role.j2", role_dir)
        assert source.level == "embedded"

    def test_role_overrides_collection(self, loader, tmp_path):
        """Role template should override collection template."""
        # Create collection structure
        collection_dir = tmp_path / "my_collection"
        collection_dir.mkdir()
        (collection_dir / "galaxy.yml").write_text("namespace: test")

        roles_dir = collection_dir / "roles"
        roles_dir.mkdir()
        role_dir = roles_dir / "my_role"
        role_dir.mkdir()

        # Create BOTH role and collection templates
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Role wins</html>")

        coll_templates = collection_dir / ".ansibledoctor" / "templates"
        coll_templates.mkdir(parents=True)
        (coll_templates / "role.html.j2").write_text("<html>Collection loses</html>")

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "role"

    def test_custom_search_paths_included(self, tmp_path):
        """Custom search paths should be included in discovery."""
        custom_path = tmp_path / "custom_templates"
        custom_path.mkdir()
        (custom_path / "role.html.j2").write_text("<html>Custom</html>")

        loader = CascadingTemplateLoader(search_paths=[custom_path])

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        template, source = loader.find_template("role.html.j2", role_dir)
        assert source.level == "custom"
        assert source.path == custom_path / "role.html.j2"


class TestCaching:
    """Test template caching behavior."""

    def test_template_is_cached(self, tmp_path):
        """Templates should be cached after first access."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Role</html>")

        # First access
        template1, source1 = loader.find_template("role.html.j2", role_dir)

        # Second access should return cached
        template2, source2 = loader.find_template("role.html.j2", role_dir)

        # Should be same objects (cached)
        assert template1 is template2
        assert source1 is source2

    def test_cache_key_includes_context_path(self, tmp_path):
        """Cache should be keyed by both template name and context path."""
        loader = CascadingTemplateLoader()

        # Create two roles with different templates
        role1_dir = tmp_path / "role1"
        role1_dir.mkdir()
        role1_templates = role1_dir / ".ansibledoctor" / "templates"
        role1_templates.mkdir(parents=True)
        (role1_templates / "role.html.j2").write_text("<html>Role 1</html>")

        role2_dir = tmp_path / "role2"
        role2_dir.mkdir()
        role2_templates = role2_dir / ".ansibledoctor" / "templates"
        role2_templates.mkdir(parents=True)
        (role2_templates / "role.html.j2").write_text("<html>Role 2</html>")

        template1, source1 = loader.find_template("role.html.j2", role1_dir)
        template2, source2 = loader.find_template("role.html.j2", role2_dir)

        # Should be different templates
        assert source1.path != source2.path

    def test_cache_expires_after_ttl(self, tmp_path):
        """Cache should expire after TTL seconds."""
        loader = CascadingTemplateLoader(cache_ttl=1)  # 1 second TTL

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Original</html>")

        # First access
        template1, source1 = loader.find_template("role.html.j2", role_dir)

        # Modify template
        (role_templates / "role.html.j2").write_text("<html>Modified</html>")

        # Mock time passing
        with patch("ansibledoctor.generator.cascading_loader.datetime") as mock_dt:
            mock_dt.now.return_value = datetime.now() + timedelta(seconds=2)

            # Access again after TTL
            template2, source2 = loader.find_template("role.html.j2", role_dir)

        # Should have re-discovered (new template content)
        # Note: Discovery time should be different
        assert source1.discovered_at != source2.discovered_at

    def test_clear_cache(self, tmp_path):
        """clear_cache() should invalidate all cached templates."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Original</html>")

        # First access
        template1, source1 = loader.find_template("role.html.j2", role_dir)

        # Clear cache
        loader.clear_cache()

        # Access again
        template2, source2 = loader.find_template("role.html.j2", role_dir)

        # Should have re-discovered (different discovered_at)
        assert source1.discovered_at != source2.discovered_at


class TestEnvironment:
    """Test Jinja2 environment creation."""

    def test_environment_includes_filters(self, tmp_path):
        """Jinja2 environment should include custom filters."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        env = loader.get_environment(role_dir)

        # Should have our custom filters from FILTERS dict
        assert "markdown_escape" in env.filters
        assert "code_fence" in env.filters

    def test_environment_autoescape_enabled(self, tmp_path):
        """Jinja2 environment should have autoescape enabled for HTML."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        env = loader.get_environment(role_dir)

        # Autoescape should be enabled
        assert env.autoescape is True

    def test_environment_uses_choice_loader(self, tmp_path):
        """Jinja2 environment should use ChoiceLoader."""
        from jinja2 import ChoiceLoader

        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)

        env = loader.get_environment(role_dir)

        assert isinstance(env.loader, ChoiceLoader)


class TestTemplateNotFoundError:
    """Test TemplateNotFoundError exception."""

    def test_error_raised_when_template_not_found(self, tmp_path):
        """TemplateNotFoundError should be raised when template doesn't exist."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.find_template("nonexistent.html.j2", role_dir)

        assert "nonexistent.html.j2" in str(exc_info.value)

    def test_error_includes_searched_paths(self, tmp_path):
        """TemplateNotFoundError should list searched paths."""
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()

        with pytest.raises(TemplateNotFoundError) as exc_info:
            loader.find_template("nonexistent.html.j2", role_dir)

        error = exc_info.value
        assert hasattr(error, "searched_paths")
        assert len(error.searched_paths) > 0


class TestProjectRootDetection:
    """Test project root detection logic."""

    def test_finds_project_root_with_ansible_cfg(self, tmp_path):
        """Should find project root by looking for ansible.cfg."""
        loader = CascadingTemplateLoader()

        # Create project structure
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]")

        roles_dir = project_dir / "roles"
        roles_dir.mkdir()
        role_dir = roles_dir / "webserver"
        role_dir.mkdir()

        # Internal method test
        root = loader._find_project_root(role_dir)
        assert root == project_dir

    def test_finds_project_root_with_pyproject_toml(self, tmp_path):
        """Should find project root by looking for pyproject.toml."""
        loader = CascadingTemplateLoader()

        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text("[tool.ansibledoctor]")

        roles_dir = project_dir / "roles"
        roles_dir.mkdir()
        role_dir = roles_dir / "webserver"
        role_dir.mkdir()

        root = loader._find_project_root(role_dir)
        assert root == project_dir

    def test_returns_none_when_no_project_root(self):
        """Should return None when no project markers found."""
        import tempfile

        loader = CascadingTemplateLoader()

        # Use system temp dir to ensure we're outside any git/project structure
        with tempfile.TemporaryDirectory() as tmpdir:
            role_dir = Path(tmpdir) / "orphan_role"
            role_dir.mkdir()

            root = loader._find_project_root(role_dir)
            assert root is None


class TestLogging:
    """Test logging behavior during template discovery."""

    def test_logs_template_discovery(self, tmp_path, caplog):
        """Should log when a template is discovered."""
        import logging

        caplog.set_level(logging.DEBUG)
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Role</html>")

        loader.find_template("role.html.j2", role_dir)

        # Check log message contains key info
        assert any(
            "Template discovered" in record.message or "role.html.j2" in record.message
            for record in caplog.records
        )

    def test_logs_cache_hit(self, tmp_path, caplog):
        """Should log when template is served from cache."""
        import logging

        caplog.set_level(logging.DEBUG)
        loader = CascadingTemplateLoader()

        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        role_templates = role_dir / ".ansibledoctor" / "templates"
        role_templates.mkdir(parents=True)
        (role_templates / "role.html.j2").write_text("<html>Role</html>")

        # First access
        loader.find_template("role.html.j2", role_dir)
        caplog.clear()

        # Second access (should be cached)
        loader.find_template("role.html.j2", role_dir)

        # Should log cache hit
        assert any("cache" in record.message.lower() for record in caplog.records)
