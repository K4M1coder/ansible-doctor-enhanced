"""
Unit tests for ExternalLinkIntegrator configuration support.

Tests configuration loading from .ansibledoctor.yml including:
- Custom module documentation URL overrides
- Custom best practices keyword mappings
- Feature enable/disable flags
- Configuration validation
"""

from pathlib import Path

from ansibledoctor.links.external_link_integrator import ExternalLinkIntegrator
from ansibledoctor.models.link import Link


class TestConfigurationLoading:
    """Test loading configuration from .ansibledoctor.yml."""

    def test_from_config_loads_ansible_version(self, tmp_path: Path) -> None:
        """Test that ansible_version is loaded from config."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
ansible_version: "2.14"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        assert integrator.ansible_version == "2.14"

    def test_from_config_loads_base_urls(self, tmp_path: Path) -> None:
        """Test that base URLs are loaded from config."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  ansible_docs_base: "https://custom-docs.example.com"
  galaxy_base: "https://custom-galaxy.example.com"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        assert integrator.ansible_docs_base == "https://custom-docs.example.com"
        assert integrator.galaxy_base == "https://custom-galaxy.example.com"

    def test_from_config_loads_module_docs_overrides(self, tmp_path: Path) -> None:
        """Test that module_docs overrides are loaded from config."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  module_docs:
    ansible.builtin.copy: "https://example.com/copy"
    community.general.docker_container: "https://example.com/docker"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        assert integrator.module_docs_override["ansible.builtin.copy"] == "https://example.com/copy"
        assert (
            integrator.module_docs_override["community.general.docker_container"]
            == "https://example.com/docker"
        )

    def test_from_config_loads_best_practices_keywords(self, tmp_path: Path) -> None:
        """Test that custom best practices keywords are loaded from config."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  best_practices:
    custom_keyword: "https://example.com/custom"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        # Should include both default and custom keywords
        assert "custom_keyword" in integrator.best_practices_keywords
        assert integrator.best_practices_keywords["custom_keyword"] == "https://example.com/custom"
        # Should still have defaults
        assert "security" in integrator.best_practices_keywords

    def test_from_config_loads_feature_flags(self, tmp_path: Path) -> None:
        """Test that feature flags are loaded from config."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  features:
    module_docs: false
    galaxy_links: false
    best_practices: false
    new_tab: false
    version_specific: false
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        assert integrator.enable_module_docs is False
        assert integrator.enable_galaxy_links is False
        assert integrator.enable_best_practices is False
        assert integrator.new_tab_external is False
        assert integrator.version_specific is False

    def test_from_config_defaults_when_missing(self, tmp_path: Path) -> None:
        """Test that default values are used when config is missing."""
        config_file = tmp_path / ".ansibledoctor.yml"
        # Empty config file
        config_file.write_text("")

        integrator = ExternalLinkIntegrator.from_config(config_file)

        # Should use defaults
        assert integrator.ansible_version == "latest"
        assert integrator.ansible_docs_base == "https://docs.ansible.com"
        assert integrator.galaxy_base == "https://galaxy.ansible.com"
        assert integrator.enable_module_docs is True
        assert integrator.enable_galaxy_links is True
        assert integrator.enable_best_practices is True
        assert integrator.new_tab_external is True


class TestFeatureFlagBehavior:
    """Test that feature flags correctly control functionality."""

    def test_disable_module_docs_returns_empty_list(self, tmp_path: Path) -> None:
        """Test that disabling module docs returns empty list."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  features:
    module_docs: false
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)
        role_dir = tmp_path / "test_role"
        role_dir.mkdir()
        tasks_dir = role_dir / "tasks"
        tasks_dir.mkdir()

        # Create a task file with module usage
        task_file = tasks_dir / "main.yml"
        task_file.write_text(
            """
- name: Copy file
  ansible.builtin.copy:
    src: /tmp/test
    dest: /tmp/dest
"""
        )

        links = integrator.extract_module_links(role_dir)

        assert links == []

    def test_disable_best_practices_returns_empty_list(self, tmp_path: Path) -> None:
        """Test that disabling best practices returns empty list."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  features:
    best_practices: false
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        content = """
        This document discusses security and testing best practices.
        Vault encryption is important for secrets.
        """

        links = integrator.extract_best_practice_links(content)

        assert links == []

    def test_disable_galaxy_returns_none(self, tmp_path: Path) -> None:
        """Test that disabling Galaxy links returns None."""
        from ansibledoctor.models.collection import AnsibleCollection
        from ansibledoctor.models.galaxy import GalaxyMetadata

        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  features:
    galaxy_links: false
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        metadata = GalaxyMetadata(
            namespace="test", name="collection", version="1.0.0", authors=["Test"], dependencies={}
        )
        collection = AnsibleCollection(metadata=metadata)

        link = integrator.generate_galaxy_link(collection)

        assert link is None

    def test_disable_new_tab_removes_target_attribute(self, tmp_path: Path) -> None:
        """Test that disabling new tab feature removes target attribute."""
        from ansibledoctor.models.link import LinkType

        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  features:
    new_tab: false
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        link = Link(
            source_file=Path.cwd() / "test.md",
            target="https://docs.ansible.com/",
            link_type=LinkType.EXTERNAL_URL,
            text="Docs",
            line_number=1,
        )

        html = integrator.render_link_html(link)

        assert 'target="_blank"' not in html
        assert 'rel="noopener noreferrer"' not in html
        assert '<a href="https://docs.ansible.com/">Docs</a>' == html


class TestCustomOverrides:
    """Test custom URL overrides work correctly."""

    def test_module_docs_override_used(self, tmp_path: Path) -> None:
        """Test that module_docs override URLs are used."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  module_docs:
    ansible.builtin.copy: "https://custom-docs.example.com/copy"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        link = integrator.generate_module_doc_link("ansible.builtin.copy")

        assert link.target == "https://custom-docs.example.com/copy"

    def test_module_docs_override_fallback_to_default(self, tmp_path: Path) -> None:
        """Test that modules without override use default URL."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  module_docs:
    ansible.builtin.copy: "https://custom-docs.example.com/copy"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        link = integrator.generate_module_doc_link("ansible.builtin.file")

        # Should use default URL pattern
        assert "https://docs.ansible.com/" in link.target
        assert "file_module.html" in link.target

    def test_custom_best_practices_keywords_work(self, tmp_path: Path) -> None:
        """Test that custom best practices keywords are detected."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  best_practices:
    custom_pattern: "https://example.com/custom-guide"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        content = "This document discusses custom_pattern in detail."

        links = integrator.extract_best_practice_links(content)

        # Should find custom keyword
        assert len(links) > 0
        assert any("custom-guide" in link.target for link in links)

    def test_custom_best_practices_override_defaults(self, tmp_path: Path) -> None:
        """Test that custom keywords can override default mappings."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text(
            """
external_links:
  best_practices:
    security: "https://custom-security-guide.example.com"
"""
        )

        integrator = ExternalLinkIntegrator.from_config(config_file)

        content = "This document discusses security best practices."

        links = integrator.extract_best_practice_links(content)

        # Should use custom URL for "security" keyword
        assert len(links) > 0
        assert any("custom-security-guide.example.com" in link.target for link in links)
