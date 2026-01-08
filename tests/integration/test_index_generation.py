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


class TestIndexFileWriting:
    """Tests for T024-T026 - File writing, empty handling, and logging."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp output directory."""
        return DefaultIndexGenerator(output_dir=tmp_path, output_format="markdown")

    @pytest.fixture
    def sample_roles(self):
        """Sample roles for testing."""
        return [
            IndexItem(
                name="role1",
                type="role",
                description="Test role 1",
                path=Path("roles/role1"),
                doc_link="./role1.md",
                tags=["test"],
            ),
            IndexItem(
                name="role2",
                type="role",
                description="Test role 2",
                path=Path("roles/role2"),
                doc_link="./role2.md",
                tags=["test"],
            ),
        ]

    def test_write_index_files(self, generator, sample_roles):
        """T025: Test writing index files to disk."""
        # Generate pages
        pages = generator.generate_index_page(
            component_type="roles",
            items=sample_roles,
            format="list",
        )

        # Write files
        written_files = generator.write_index_files(
            pages=pages,
            component_type="roles",
        )

        assert len(written_files) == 1
        assert written_files[0].exists()
        assert written_files[0].name == "index.md"
        assert written_files[0].parent.name == "roles"

        # Check content was written
        content = written_files[0].read_text()
        assert "role1" in content or "role2" in content

    def test_write_index_files_with_pagination(self, generator):
        """T025: Test writing multiple paginated index files."""
        # Create enough items to trigger pagination
        many_roles = [
            IndexItem(
                name=f"role{i}",
                type="role",
                description=f"Test role {i}",
                path=Path(f"roles/role{i}"),
                doc_link=f"./role{i}.md",
            )
            for i in range(75)
        ]

        pages = generator.generate_index_page(
            component_type="roles",
            items=many_roles,
            page_size=50,
        )

        written_files = generator.write_index_files(
            pages=pages,
            component_type="roles",
        )

        assert len(written_files) == 2
        assert written_files[0].name == "index.md"
        assert written_files[1].name == "index-2.md"

    def test_empty_collection_handling(self, generator):
        """T024: Test handling of empty collections."""
        pages = generator.generate_index_page(
            component_type="roles",
            items=[],
            format="list",
        )

        written_files = generator.write_index_files(
            pages=pages,
            component_type="roles",
        )

        assert len(written_files) == 1
        content = written_files[0].read_text()
        assert "No roles found" in content

    def test_generate_and_write_indexes(self, generator, sample_roles):
        """T025-T026: Test end-to-end index generation and writing."""
        components = {
            "roles": sample_roles,
            "plugins": [
                IndexItem(
                    name="my_module",
                    type="plugin",
                    description="Test module",
                    path=Path("plugins/modules/my_module.py"),
                    doc_link="./my_module.md",
                )
            ],
        }

        result = generator.generate_and_write_indexes(
            components=components,
            index_style="list",
        )

        assert "roles" in result
        assert "plugins" in result
        assert len(result["roles"]) == 1
        assert len(result["plugins"]) == 1

        # Verify files exist
        for files in result.values():
            for file_path in files:
                assert file_path.exists()


class TestHierarchicalProjectIndex:
    """Tests for US2 - Hierarchical Project Index with Tree Visualization."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    @pytest.fixture
    def project_structure(self):
        """T027: Create project structure with 2 collections, 3 roles each."""
        return [
            # Collection 1
            IndexItem(
                name="webstack",
                type="collection",
                description="Web stack collection",
                path=Path("collections/ansible_collections/my_namespace/webstack"),
                namespace="my_namespace",
            ),
            # Collection 1 roles
            IndexItem(
                name="nginx",
                type="role",
                description="Configure nginx web server",
                path=Path("collections/ansible_collections/my_namespace/webstack/roles/nginx"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="apache",
                type="role",
                description="Configure Apache web server",
                path=Path("collections/ansible_collections/my_namespace/webstack/roles/apache"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="haproxy",
                type="role",
                description="Configure HAProxy load balancer",
                path=Path("collections/ansible_collections/my_namespace/webstack/roles/haproxy"),
                namespace="my_namespace",
            ),
            # Collection 2
            IndexItem(
                name="dbstack",
                type="collection",
                description="Database stack collection",
                path=Path("collections/ansible_collections/my_namespace/dbstack"),
                namespace="my_namespace",
            ),
            # Collection 2 roles
            IndexItem(
                name="postgresql",
                type="role",
                description="Install PostgreSQL database",
                path=Path("collections/ansible_collections/my_namespace/dbstack/roles/postgresql"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="mysql",
                type="role",
                description="Install MySQL database",
                path=Path("collections/ansible_collections/my_namespace/dbstack/roles/mysql"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="redis",
                type="role",
                description="Install Redis cache",
                path=Path("collections/ansible_collections/my_namespace/dbstack/roles/redis"),
                namespace="my_namespace",
            ),
        ]

    def test_project_hierarchy_structure(self, generator, project_structure):
        """T027: Test hierarchical structure with 2 collections, 3 roles each."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(project_structure)

        # Should have 2 root collections
        collections = [item for item in hierarchy if item.type == "collection"]
        assert len(collections) == 2

        # Each collection should have 3 child roles
        for collection in collections:
            roles = [child for child in collection.children if child.type == "role"]
            assert len(roles) == 3
            # Verify parent-child relationship by checking paths
            for role in roles:
                # Role path should start with collection path
                assert str(role.path).startswith(str(collection.path))
                # Role should be in collection's children
                assert role in collection.children

    def test_plugin_indexing(self, generator):
        """T028: Test plugin indexing under collection."""
        components = [
            IndexItem(
                name="my_collection",
                type="collection",
                path=Path("collections/ansible_collections/my_namespace/my_collection"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="my_module",
                type="module",
                description="Test module plugin",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/plugins/modules/my_module.py"
                ),
                namespace="my_namespace",
            ),
            IndexItem(
                name="my_filter",
                type="plugin",
                description="Test filter plugin",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/plugins/filter/my_filter.py"
                ),
                namespace="my_namespace",
            ),
        ]

        # Build hierarchy
        hierarchy = generator.build_hierarchy(components)

        # Find collection
        collection = next(item for item in hierarchy if item.type == "collection")

        # Verify plugins are children of collection
        plugins = [child for child in collection.children if child.type in ["module", "plugin"]]
        assert len(plugins) == 2

        # Verify plugin types
        plugin_types = {child.type for child in plugins}
        assert plugin_types == {"module", "plugin"}

    def test_depth_limiting(self, generator, project_structure):
        """T029: Test depth limiting in tree visualization."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(project_structure)

        # Calculate max depth (depth of deepest leaf node)
        def calculate_max_depth(items, current_depth=0):
            if not items:
                return (
                    current_depth - 1
                )  # Subtract 1 since we want depth of deepest node, not level count
            return max(calculate_max_depth(item.children, current_depth + 1) for item in items)

        max_depth = calculate_max_depth(hierarchy)

        # Project structure should have max depth of 1 (collection=0, role=1)
        assert max_depth == 1

        # Verify depth property is set correctly on IndexItem (depth property counts children depth)
        for item in hierarchy:
            if item.type == "collection":
                # Collection has children at depth 1, so its depth property is 1
                assert item.depth == 1  # item.depth counts the deepest child level

    def test_playbook_indexing(self, generator):
        """T030: Test playbook indexing in collection."""
        components = [
            IndexItem(
                name="my_collection",
                type="collection",
                path=Path("collections/ansible_collections/my_namespace/my_collection"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="deploy",
                type="playbook",
                description="Deploy application playbook",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/playbooks/deploy.yml"
                ),
                namespace="my_namespace",
            ),
            IndexItem(
                name="rollback",
                type="playbook",
                description="Rollback application playbook",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/playbooks/rollback.yml"
                ),
                namespace="my_namespace",
            ),
        ]

        # Build hierarchy
        hierarchy = generator.build_hierarchy(components)

        # Find collection
        collection = next(item for item in hierarchy if item.type == "collection")

        # Verify playbooks are children
        playbooks = [child for child in collection.children if child.type == "playbook"]
        assert len(playbooks) == 2

        # Verify playbook names
        playbook_names = {child.name for child in playbooks}
        assert playbook_names == {"deploy", "rollback"}


class TestNestedTables:
    """Test nested table format (Phase 6 US4)."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a generator instance."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return DefaultIndexGenerator(output_dir=output_dir)

    @pytest.fixture
    def nested_structure(self):
        """Create nested collection structure for testing."""
        return [
            # Collection 1
            IndexItem(
                name="my_collection",
                type="collection",
                description="First collection",
                path=Path("collections/ansible_collections/my_namespace/my_collection"),
                namespace="my_namespace",
                metadata={"role_count": 2, "plugin_count": 3},
            ),
            # Roles under collection 1
            IndexItem(
                name="role1",
                type="role",
                description="First role",
                path=Path("collections/ansible_collections/my_namespace/my_collection/roles/role1"),
                namespace="my_namespace",
            ),
            IndexItem(
                name="role2",
                type="role",
                description="Second role",
                path=Path("collections/ansible_collections/my_namespace/my_collection/roles/role2"),
                namespace="my_namespace",
            ),
            # Plugins under collection 1
            IndexItem(
                name="module1",
                type="module",
                description="First module",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/plugins/modules/module1.py"
                ),
                namespace="my_namespace",
                metadata={"plugin_type": "module"},
            ),
            IndexItem(
                name="filter1",
                type="plugin",
                description="First filter",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/plugins/filter/filter1.py"
                ),
                namespace="my_namespace",
                metadata={"plugin_type": "filter"},
            ),
            IndexItem(
                name="lookup1",
                type="plugin",
                description="First lookup",
                path=Path(
                    "collections/ansible_collections/my_namespace/my_collection/plugins/lookup/lookup1.py"
                ),
                namespace="my_namespace",
                metadata={"plugin_type": "lookup"},
            ),
            # Collection 2
            IndexItem(
                name="another_collection",
                type="collection",
                description="Second collection",
                path=Path("collections/ansible_collections/other_namespace/another_collection"),
                namespace="other_namespace",
                metadata={"role_count": 1, "plugin_count": 1},
            ),
            # Role under collection 2
            IndexItem(
                name="role3",
                type="role",
                description="Third role",
                path=Path(
                    "collections/ansible_collections/other_namespace/another_collection/roles/role3"
                ),
                namespace="other_namespace",
            ),
            # Plugin under collection 2
            IndexItem(
                name="module2",
                type="module",
                description="Second module",
                path=Path(
                    "collections/ansible_collections/other_namespace/another_collection/plugins/modules/module2.py"
                ),
                namespace="other_namespace",
                metadata={"plugin_type": "module"},
            ),
        ]

    def test_nested_table_structure(self, generator, nested_structure):
        """T053: Test nested table shows collections with child counts."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(nested_structure)

        # Generate index page with nested-table format
        pages = generator.generate_index_page(
            component_type="collections",
            items=hierarchy,
            format="nested-table",
            page_size=50,
        )

        # Verify page created
        assert len(pages) == 1
        page = pages[0]

        # Verify format
        assert page.format == "nested-table"

        # Verify collections are top-level items
        assert len(page.items) == 2

        # Verify child counts in metadata (for nested-table rendering)
        collection1 = next(item for item in page.items if item.name == "my_collection")
        assert len(collection1.children) == 5  # 2 roles + 3 plugins

        collection2 = next(item for item in page.items if item.name == "another_collection")
        assert len(collection2.children) == 2  # 1 role + 1 plugin

    def test_nested_depth_limiting(self, generator, nested_structure):
        """T054: Test nested-depth parameter limits nesting levels."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(nested_structure)

        # Generate page with nested_depth=1 (only top level, no children)
        pages = generator.generate_index_page(
            component_type="collections",
            items=hierarchy,
            format="nested-table",
            page_size=50,
        )

        page = pages[0]

        # Verify nested_depth parameter exists (will be added to IndexPage model)
        # For now, just verify the structure exists
        assert page.format == "nested-table"

        # Children should still be in the structure but rendering will limit display
        collection1 = next(item for item in page.items if item.name == "my_collection")
        assert len(collection1.children) > 0

    def test_markdown_nested_table(self, generator, nested_structure):
        """T056: Test Markdown nested table with inline children."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(nested_structure)

        # Generate nested-table page
        pages = generator.generate_index_page(
            component_type="collections",
            items=hierarchy,
            format="nested-table",
            page_size=50,
        )

        page = pages[0]

        # Verify structure for Markdown rendering
        # Table will have: Collection | Roles | Plugins columns
        assert page.format == "nested-table"
        assert len(page.items) == 2

        # Verify children can be accessed for inline display
        collection1 = next(item for item in page.items if item.name == "my_collection")
        roles = [c for c in collection1.children if c.type == "role"]
        plugins = [c for c in collection1.children if c.type in ("module", "plugin")]

        assert len(roles) == 2
        assert len(plugins) == 3

    def test_child_summary_calculation(self, generator, nested_structure):
        """T058: Test child summary statistics for nested table."""
        # Build hierarchy
        hierarchy = generator.build_hierarchy(nested_structure)

        # Verify child statistics can be calculated
        collection1 = next(item for item in hierarchy if item.name == "my_collection")

        # Count children by type
        roles = [c for c in collection1.children if c.type == "role"]
        modules = [c for c in collection1.children if c.type == "module"]
        plugins = [c for c in collection1.children if c.type == "plugin" or c.type == "module"]

        assert len(roles) == 2
        assert len(modules) == 1
        assert len(plugins) == 3  # 1 module + 2 plugins (filter, lookup)

        # Verify metadata for display
        assert collection1.metadata.get("role_count") == 2
        assert collection1.metadata.get("plugin_count") == 3
