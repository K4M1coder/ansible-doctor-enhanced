"""Integration tests for embedded section indexes ({{ index() }} template markers)."""

from pathlib import Path

import pytest

from ansibledoctor.generator.indexes import DefaultIndexGenerator
from ansibledoctor.models.index import IndexItem


class TestEmbeddedIndexes:
    """Test embedded section index generation via {{ index() }} markers."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    @pytest.fixture
    def sample_roles(self):
        """Create sample role items for testing."""
        return [
            IndexItem(
                name="webserver",
                type="role",
                description="Configure web server with nginx",
                path=Path("roles/webserver"),
                doc_link="roles/webserver.md",
                tags=["web", "nginx"],
                namespace="my_namespace",
            ),
            IndexItem(
                name="database",
                type="role",
                description="Set up PostgreSQL database",
                path=Path("roles/database"),
                doc_link="roles/database.md",
                tags=["database", "postgresql"],
                namespace="my_namespace",
            ),
            IndexItem(
                name="loadbalancer",
                type="role",
                description="Configure HAProxy load balancer",
                path=Path("roles/loadbalancer"),
                doc_link="roles/loadbalancer.md",
                tags=["web", "haproxy"],
                namespace="my_namespace",
            ),
        ]

    @pytest.fixture
    def sample_plugins(self):
        """Create sample plugin items for testing."""
        return [
            IndexItem(
                name="my_module",
                type="module",
                description="Test module plugin",
                path=Path("plugins/modules/my_module.py"),
                doc_link="plugins/my_module.md",
                tags=["automation"],
                namespace="my_namespace",
                metadata={"plugin_type": "module"},
            ),
            IndexItem(
                name="my_filter",
                type="plugin",
                description="Test filter plugin",
                path=Path("plugins/filter/my_filter.py"),
                doc_link="plugins/my_filter.md",
                tags=["formatting"],
                namespace="my_namespace",
                metadata={"plugin_type": "filter"},
            ),
            IndexItem(
                name="my_lookup",
                type="plugin",
                description="Test lookup plugin",
                path=Path("plugins/lookup/my_lookup.py"),
                doc_link="plugins/my_lookup.md",
                tags=["data"],
                namespace="my_namespace",
                metadata={"plugin_type": "lookup"},
            ),
        ]

    def test_template_marker_parsing(self, generator, sample_roles):
        """T041: Test that {{ index('roles') }} template marker is parsed correctly."""
        # Generate section index
        section_index = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
        )

        # Should return SectionIndex with correct component type
        assert section_index.component_type == "roles"
        assert len(section_index.items) == 3
        assert section_index.format == "list"  # default format

    def test_embedded_table_format(self, generator, sample_roles):
        """T042: Test embedded table format rendering."""
        # Generate section index with table format
        section_index = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            format="table",
        )

        # Should have table format
        assert section_index.format == "table"

        # Render inline should produce table markdown
        output = section_index.render_inline()
        assert "| Name |" in output
        assert "| webserver |" in output
        assert "| database |" in output

    def test_group_by_plugin_type(self, generator, sample_plugins):
        """T043: Test group_by parameter for grouping plugins by type."""
        # Generate section index grouped by plugin_type
        section_index = generator.generate_section_index(
            component_type="plugins",
            items=sample_plugins,
            group_by="metadata.plugin_type",
        )

        # Should group plugins by type
        assert section_index.group_by == "metadata.plugin_type"

        # Render should show grouped sections
        output = section_index.render_inline()
        assert "module" in output.lower()
        assert "filter" in output.lower()
        assert "lookup" in output.lower()

    def test_limit_parameter(self, generator, sample_roles):
        """T044: Test limit parameter with 'and X more...' hidden count."""
        # Generate section index with limit=2
        section_index = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            limit=2,
        )

        # Should limit to 2 items
        assert section_index.limit == 2
        assert len(section_index.items) == 3  # All items stored

        # Render should show only 2 items + "and 1 more..."
        output = section_index.render_inline()
        assert "webserver" in output
        assert "database" in output
        # Third item should not be in visible output (before "more" link)
        lines_before_more = output.split("and 1 more")[0] if "and 1 more" in output else output
        assert "loadbalancer" not in lines_before_more
        assert "and 1 more" in output

    def test_filter_parameter(self, generator, sample_roles):
        """T045: Test filter parameter with tag filtering."""
        # Generate section index filtered by tag
        section_index = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            filter_expression="tag:web",
        )

        # Should apply filter
        assert section_index.filter_expression == "tag:web"

        # Render should show only items with 'web' tag
        output = section_index.render_inline()
        assert "webserver" in output
        assert "loadbalancer" in output
        assert "database" not in output  # No 'web' tag

    def test_combined_parameters(self, generator, sample_roles):
        """Test combining multiple parameters: filter + limit + format."""
        # Filter web roles, limit to 1, table format
        section_index = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            filter_expression="tag:web",
            limit=1,
            format="table",
        )

        # Should have all parameters set
        assert section_index.filter_expression == "tag:web"
        assert section_index.limit == 1
        assert section_index.format == "table"

        # Render should show table with 1 web role + "and 1 more..."
        output = section_index.render_inline()
        assert "| Name |" in output  # Table format
        assert ("webserver" in output or "loadbalancer" in output)
        assert "and 1 more" in output
