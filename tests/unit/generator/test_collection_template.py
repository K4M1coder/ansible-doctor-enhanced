"""Unit tests for Collection template rendering (T100-T105).

Tests the collection documentation template (collection.md.j2) rendering
with metadata, installation instructions, role index, plugin lists,
dependencies, and examples.
"""

from pathlib import Path

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.plugin import Plugin, PluginType


class TestCollectionTemplate:
    """Test collection template rendering."""

    def test_render_collection_template_with_metadata(self, tmp_path: Path) -> None:
        """Test: Render collection template with metadata (T100)."""
        # Setup: Create minimal collection with metadata
        metadata = GalaxyMetadata(
            namespace="test_namespace",
            name="test_collection",
            version="1.0.0",
            authors=["Test Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        # Setup: Template context
        context = {
            "collection": collection,
            "metadata": metadata,
            "fqcn": "test_namespace.test_collection",
            "version": "1.0.0",
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Output contains metadata
        assert "test_namespace.test_collection" in output
        assert "1.0.0" in output
        assert "Test Author" in output

    def test_template_includes_installation_instructions(self, tmp_path: Path) -> None:
        """Test: Template includes installation instructions (T101)."""
        # Setup: Create collection
        metadata = GalaxyMetadata(
            namespace="community",
            name="general",
            version="2.5.0",
            authors=["Ansible Community"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        context = {
            "collection": collection,
            "metadata": metadata,
            "fqcn": "community.general",
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Installation section present with ansible-galaxy command
        assert "## Installation" in output or "# Installation" in output
        assert "ansible-galaxy collection install" in output
        assert "community.general" in output

    def test_template_includes_role_index_with_descriptions(self, tmp_path: Path) -> None:
        """Test: Template includes role index with descriptions (T102).

        Format is configurable: table or list format (decided by template).
        """
        # Setup: Create collection with roles
        metadata = GalaxyMetadata(
            namespace="namespace",
            name="collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )

        # Mock role data (in real implementation, roles would be CollectionRole objects)
        roles_data = [
            {"name": "webserver", "description": "Configure web server"},
            {"name": "database", "description": "Setup database"},
            {"name": "monitoring", "description": "Install monitoring tools"},
        ]

        collection = AnsibleCollection(
            metadata=metadata,
            roles=["webserver", "database", "monitoring"],
            plugins={},
        )

        context = {
            "collection": collection,
            "metadata": metadata,
            "roles": roles_data,  # Template gets enriched role data
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Role section present (table OR list format)
        assert "## Roles" in output or "# Roles" in output
        assert "webserver" in output
        assert "database" in output
        assert "monitoring" in output

        # Verify: Descriptions included (in table or list)
        assert "Configure web server" in output
        assert "Setup database" in output
        assert "Install monitoring tools" in output

    def test_template_includes_plugin_list_grouped_by_type(self, tmp_path: Path) -> None:
        """Test: Template includes plugin list grouped by type (T103)."""
        # Setup: Create collection with plugins
        metadata = GalaxyMetadata(
            namespace="namespace",
            name="collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )

        # Create plugin instances
        module1 = Plugin(
            name="my_module",
            type=PluginType.MODULE,
            path=Path("/collection/plugins/modules/my_module.py"),
            short_description="Example module",
        )

        module2 = Plugin(
            name="another_module",
            type=PluginType.MODULE,
            path=Path("/collection/plugins/modules/another_module.py"),
            short_description="Another module",
        )

        filter1 = Plugin(
            name="custom_filter",
            type=PluginType.FILTER,
            path=Path("/collection/plugins/filters/custom_filter.py"),
            short_description="Custom Jinja2 filter",
        )

        lookup1 = Plugin(
            name="data_lookup",
            type=PluginType.LOOKUP,
            path=Path("/collection/plugins/lookups/data_lookup.py"),
            short_description="Data lookup plugin",
        )

        plugins_list = [module1, module2, filter1, lookup1]

        # Group plugins by type
        plugins_by_type = {
            PluginType.MODULE: [module1, module2],
            PluginType.FILTER: [filter1],
            PluginType.LOOKUP: [lookup1],
        }

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={
                PluginType.MODULE: ["my_module", "another_module"],
                PluginType.FILTER: ["custom_filter"],
                PluginType.LOOKUP: ["data_lookup"],
            },
        )

        context = {
            "collection": collection,
            "metadata": metadata,
            "plugins": plugins_list,
            "plugins_by_type": plugins_by_type,
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Plugin section present
        assert "## Plugins" in output or "# Plugins" in output

        # Verify: Plugin types as subsections
        assert "### Modules" in output or "Modules" in output
        assert "### Filters" in output or "Filters" in output
        assert "### Lookups" in output or "Lookups" in output

        # Verify: Plugin names listed
        assert "my_module" in output
        assert "another_module" in output
        assert "custom_filter" in output
        assert "data_lookup" in output

        # Verify: Short descriptions included
        assert "Example module" in output
        assert "Custom Jinja2 filter" in output

    def test_template_includes_dependencies_section(self, tmp_path: Path) -> None:
        """Test: Template includes dependencies section (T104)."""
        # Setup: Create collection with dependencies
        metadata = GalaxyMetadata(
            namespace="myorg",
            name="mycollection",
            version="1.0.0",
            authors=["My Org"],
            dependencies={
                "community.general": ">=3.0.0",
                "ansible.posix": ">=1.5.0,<2.0.0",
                "community.docker": "*",
            },
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        context = {
            "collection": collection,
            "metadata": metadata,
            "dependencies": metadata.dependencies,
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Dependencies section present
        assert "## Dependencies" in output or "# Dependencies" in output

        # Verify: Dependencies listed with version constraints
        assert "community.general" in output
        assert ">=3.0.0" in output
        assert "ansible.posix" in output
        assert ">=1.5.0,<2.0.0" in output
        assert "community.docker" in output

    def test_template_includes_examples_playbooks_section(self, tmp_path: Path) -> None:
        """Test: Template includes examples/playbooks section (T105)."""
        # Setup: Create collection with example playbooks
        metadata = GalaxyMetadata(
            namespace="example",
            name="demos",
            version="1.0.0",
            authors=["Demo Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=["setup", "deploy"],
            plugins={},
        )

        # Example playbook data
        examples = [
            {
                "title": "Basic Setup",
                "description": "Setup basic infrastructure",
                "code": "- hosts: all\n  roles:\n    - example.demos.setup",
            },
            {
                "title": "Full Deployment",
                "description": "Complete deployment workflow",
                "code": "- hosts: webservers\n  roles:\n    - example.demos.setup\n    - example.demos.deploy",
            },
        ]

        context = {
            "collection": collection,
            "metadata": metadata,
            "examples": examples,
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Examples section present
        assert "## Examples" in output or "# Examples" in output or "## Usage" in output

        # Verify: Example playbooks included
        assert "Basic Setup" in output
        assert "Full Deployment" in output
        assert "example.demos.setup" in output
        assert "example.demos.deploy" in output

    def test_template_handles_empty_collection(self, tmp_path: Path) -> None:
        """Test: Template handles empty collection gracefully (T100)."""
        # Setup: Create minimal empty collection
        metadata = GalaxyMetadata(
            namespace="empty",
            name="collection",
            version="0.1.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        context = {
            "collection": collection,
            "metadata": metadata,
            "roles": [],
            "plugins": [],
            "plugins_by_type": {},
            "examples": [],
        }

        # Execute: Render template
        engine = TemplateEngine.create(
            template_dir=Path("ansibledoctor/generator/templates/markdown")
        )
        template = engine.get_template("collection.j2")
        output = template.render(**context)

        # Verify: Template renders without errors
        assert output is not None
        assert len(output) > 0

        # Verify: Metadata still present
        assert "empty.collection" in output
        assert "0.1.0" in output
