"""Integration tests for index generation functionality."""

from pathlib import Path

import pytest

from ansibledoctor.generator.indexes import DefaultIndexGenerator
from ansibledoctor.models.index import IndexFilter, IndexItem


class TestRoleIndexGeneration:
    """Tests for US1 - Generate Role Index Page."""

    @pytest.fixture
    def sample_roles(self):
        """Create sample role items for testing."""
        return [
            IndexItem(
                name="webserver",
                type="role",
                description="Configure web servers with nginx",
                path=Path("roles/webserver"),
                doc_link="./roles/webserver.md",
                tags=["web", "nginx"],
                namespace="my_namespace",
                dependencies=["common"],
            ),
            IndexItem(
                name="database",
                type="role",
                description="Install and configure PostgreSQL",
                path=Path("roles/database"),
                doc_link="./roles/database.md",
                tags=["database", "postgres"],
                namespace="my_namespace",
                dependencies=["common"],
            ),
            IndexItem(
                name="monitoring",
                type="role",
                description="Setup monitoring with Prometheus",
                path=Path("roles/monitoring"),
                doc_link="./roles/monitoring.md",
                tags=["monitoring", "prometheus"],
                namespace="my_namespace",
                dependencies=[],
            ),
            IndexItem(
                name="common",
                type="role",
                description="Common configuration for all servers",
                path=Path("roles/common"),
                doc_link="./roles/common.md",
                tags=["base", "common"],
                namespace="my_namespace",
                dependencies=[],
            ),
            IndexItem(
                name="backup",
                type="role",
                description="Configure backup systems",
                path=Path("roles/backup"),
                doc_link="./roles/backup.md",
                tags=["backup", "storage"],
                namespace="my_namespace",
                dependencies=[],
            ),
        ]

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    def test_basic_role_index_generation(self, generator, sample_roles):
        """T012: Test generating basic role index with 5 roles."""
        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            format="list",
        )

        assert len(pages) == 1  # All roles fit on one page
        page = pages[0]

        assert page.title == "Roles Index"
        assert page.component_type == "roles"
        assert len(page.items) == 5
        assert page.total_count == 5
        assert page.format == "list"
        assert not page.has_pagination

    def test_role_index_with_tags(self, generator, sample_roles):
        """T013: Test role index displays tags correctly."""
        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
        )

        page = pages[0]

        # Check that tags are preserved in items
        webserver_role = [r for r in page.items if r.name == "webserver"][0]
        assert "web" in webserver_role.tags
        assert "nginx" in webserver_role.tags

        database_role = [r for r in page.items if r.name == "database"][0]
        assert "database" in database_role.tags
        assert "postgres" in database_role.tags

    def test_role_index_with_dependencies(self, generator, sample_roles):
        """T014: Test role index shows dependencies."""
        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
        )

        page = pages[0]

        # Check dependencies
        webserver_role = [r for r in page.items if r.name == "webserver"][0]
        assert "common" in webserver_role.dependencies

        database_role = [r for r in page.items if r.name == "database"][0]
        assert "common" in database_role.dependencies

        monitoring_role = [r for r in page.items if r.name == "monitoring"][0]
        assert len(monitoring_role.dependencies) == 0

    def test_empty_role_collection(self, generator):
        """T015: Test index generation with no roles."""
        pages = generator.generate_index_page(
            component_type="roles",
            items=[],
        )

        assert len(pages) == 1
        page = pages[0]

        assert page.total_count == 0
        assert len(page.items) == 0
        assert page.title == "Roles Index"

    def test_multiple_index_formats(self, generator, sample_roles):
        """T016: Test generating indexes in different formats."""
        # Test list format
        list_pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            format="list",
        )
        assert list_pages[0].format == "list"

        # Test table format
        table_pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            format="table",
        )
        assert table_pages[0].format == "table"

        # Test tree format
        tree_pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            format="tree",
        )
        assert tree_pages[0].format == "tree"

    def test_index_pagination(self, generator):
        """Test pagination when items exceed page size."""
        # Create 75 roles to test pagination (page_size=50)
        roles = [
            IndexItem(
                name=f"role{i}",
                type="role",
                description=f"Test role {i}",
                path=Path(f"roles/role{i}"),
                doc_link=f"./roles/role{i}.md",
            )
            for i in range(75)
        ]

        pages = generator.generate_index_page(
            component_type="roles",
            items=roles,
            page_size=50,
        )

        assert len(pages) == 2  # 75 roles / 50 per page = 2 pages

        # First page
        assert pages[0].page_number == 1
        assert len(pages[0].items) == 50
        assert pages[0].has_next
        assert not pages[0].has_previous
        assert pages[0].next_page_link == "./index-2.md"

        # Second page
        assert pages[1].page_number == 2
        assert len(pages[1].items) == 25
        assert not pages[1].has_next
        assert pages[1].has_previous
        assert pages[1].previous_page_link == "./index.md"

    def test_index_with_filters(self, generator, sample_roles):
        """Test filtering roles by tag."""
        # Filter by "web" tag
        web_filter = IndexFilter(field="tag", operator="equals", value="web")

        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            filters=[web_filter],
        )

        page = pages[0]

        assert page.total_count == 5  # Total roles before filtering
        assert page.filtered_count == 1  # Only webserver has "web" tag
        assert len(page.items) == 1
        assert page.items[0].name == "webserver"
        assert "tag:web" in page.filters_applied

    def test_index_with_multiple_filters(self, generator, sample_roles):
        """Test applying multiple filters (AND logic)."""
        # Filter by namespace AND tag
        namespace_filter = IndexFilter(field="namespace", operator="equals", value="my_namespace")
        tag_filter = IndexFilter(field="tag", operator="equals", value="database")

        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            filters=[namespace_filter, tag_filter],
        )

        page = pages[0]

        assert page.filtered_count == 1  # Only database role
        assert len(page.items) == 1
        assert page.items[0].name == "database"


class TestHierarchicalIndexGeneration:
    """Tests for US2 - Hierarchical Project Index."""

    @pytest.fixture
    def hierarchical_items(self):
        """Create hierarchical structure for testing."""
        # Create collections
        collection1 = IndexItem(
            name="namespace1.collection1",
            type="collection",
            description="First collection",
            path=Path("collections/namespace1/collection1"),
            namespace="namespace1",
        )

        collection2 = IndexItem(
            name="namespace1.collection2",
            type="collection",
            description="Second collection",
            path=Path("collections/namespace1/collection2"),
            namespace="namespace1",
        )

        # Create roles for collection1
        roles1 = [
            IndexItem(
                name=f"role{i}",
                type="role",
                description=f"Role {i} in collection1",
                path=Path(f"collections/namespace1/collection1/roles/role{i}"),
                namespace="namespace1",
            )
            for i in range(1, 4)
        ]

        # Create roles for collection2
        roles2 = [
            IndexItem(
                name=f"role{i}",
                type="role",
                description=f"Role {i} in collection2",
                path=Path(f"collections/namespace1/collection2/roles/role{i}"),
                namespace="namespace1",
            )
            for i in range(4, 7)
        ]

        return {
            "collections": [collection1, collection2],
            "roles": roles1 + roles2,
            "all_items": [collection1, collection2] + roles1 + roles2,
        }

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    def test_build_hierarchy(self, generator, hierarchical_items):
        """T027: Test building hierarchical tree from flat items."""
        all_items = hierarchical_items["all_items"]

        hierarchy = generator.build_hierarchy(all_items)

        # Should return root items (collections)
        assert len(hierarchy) == 2
        assert all(item.type == "collection" for item in hierarchy)

        # Check children are populated
        collection1 = [c for c in hierarchy if c.name == "namespace1.collection1"][0]
        assert len(collection1.children) == 3  # 3 roles

        collection2 = [c for c in hierarchy if c.name == "namespace1.collection2"][0]
        assert len(collection2.children) == 3  # 3 roles


class TestEmbeddedIndexes:
    """Tests for US3 - Embedded Section Indexes."""

    @pytest.fixture
    def sample_roles(self):
        """Create sample roles."""
        return [
            IndexItem(
                name=f"role{i}",
                type="role",
                description=f"Test role {i}",
                path=Path(f"roles/role{i}"),
                tags=["tag1"] if i % 2 == 0 else ["tag2"],
            )
            for i in range(10)
        ]

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    def test_section_index_with_limit(self, generator, sample_roles):
        """T044: Test section index respects limit parameter."""
        section = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            limit=5,
        )

        assert section.limit == 5
        assert len(section.visible_items) == 5
        assert section.hidden_count == 5
        assert section.is_limited

    def test_section_index_with_filter(self, generator, sample_roles):
        """T045: Test section index applies filters."""
        section = generator.generate_section_index(
            component_type="roles",
            items=sample_roles,
            filter_expression="tag:tag1",
        )

        assert section.filter_expression == "tag:tag1"
        assert len(section.items) == 5  # Only even-numbered roles have tag1
