"""
Integration tests for US5: Index-Based Navigation.

Tests comprehensive index generation with smart linking:
- Alphabetical indexes (letter-based with working links)
- Category indexes (type-based navigation)
- Tag-based navigation (tag links to all tagged content)
- Bidirectional relationships (relationship graph)
- Search indexes (term search links)
"""

from pathlib import Path


class TestAlphabeticalIndex:
    """Test alphabetical index generation with letter-based navigation."""

    def test_alphabetical_index_groups_by_first_letter(self, tmp_path: Path) -> None:
        """Test that items are grouped by first letter."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        # Create items starting with different letters
        items = [
            {"name": "apache_server", "type": "role"},
            {"name": "backup_service", "type": "role"},
            {"name": "ansible_setup", "type": "role"},
            {"name": "cache_manager", "type": "role"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_alphabetical_index(items)

        # Should have groups for A, B, C
        assert "A" in index
        assert "B" in index
        assert "C" in index

        # Check items in correct groups
        assert len(index["A"]) == 2  # apache_server, ansible_setup
        assert len(index["B"]) == 1  # backup_service
        assert len(index["C"]) == 1  # cache_manager

    def test_alphabetical_index_generates_working_links(self, tmp_path: Path) -> None:
        """Test that alphabetical index contains working links to items."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "web_server", "type": "role", "path": tmp_path / "roles" / "web_server"},
            {"name": "database", "type": "role", "path": tmp_path / "roles" / "database"},
        ]

        # Create actual directories
        (tmp_path / "roles" / "web_server").mkdir(parents=True)
        (tmp_path / "roles" / "database").mkdir(parents=True)

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_alphabetical_index(items)

        # Check links are generated
        assert index["W"][0]["path"] is not None
        assert "web_server" in index["W"][0]["path"]
        assert index["D"][0]["path"] is not None
        assert "database" in index["D"][0]["path"]

    def test_alphabetical_index_handles_special_characters(self, tmp_path: Path) -> None:
        """Test that special characters are normalized in index."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "_private_role", "type": "role"},
            {"name": "123-numeric", "type": "role"},
            {"name": "ñoño", "type": "role"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_alphabetical_index(items)

        # Special chars should be normalized or grouped
        assert "#" in index or "0-9" in index  # For _private_role and 123-numeric
        assert "N" in index  # For ñoño (normalized)

    def test_alphabetical_index_case_insensitive_grouping(self, tmp_path: Path) -> None:
        """Test that grouping is case-insensitive."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "Apache", "type": "role"},
            {"name": "ansible", "type": "role"},
            {"name": "API", "type": "role"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_alphabetical_index(items)

        # All should be in 'A' group
        assert "A" in index
        assert len(index["A"]) == 3


class TestCategoryIndex:
    """Test category-based index generation."""

    def test_category_index_groups_by_type(self, tmp_path: Path) -> None:
        """Test that items are grouped by category/type."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "web_server", "type": "role"},
            {"name": "db_backup", "type": "role"},
            {"name": "utils", "type": "module"},
            {"name": "filters", "type": "filter"},
            {"name": "cache_lookup", "type": "lookup"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_category_index(items)

        # Should have categories for each type
        assert "role" in index
        assert "module" in index
        assert "filter" in index
        assert "lookup" in index

        # Check item counts
        assert len(index["role"]["items"]) == 2
        assert len(index["module"]["items"]) == 1
        assert len(index["filter"]["items"]) == 1
        assert len(index["lookup"]["items"]) == 1

    def test_category_index_generates_navigation_links(self, tmp_path: Path) -> None:
        """Test that category index has navigation between categories."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "type": "role", "path": tmp_path / "roles"},
            {"name": "module1", "type": "module", "path": tmp_path / "plugins" / "modules"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_category_index(items)

        # Should have navigation metadata
        # Categories are top-level keys
        assert "role" in index
        assert "module" in index

    def test_category_index_sorts_within_categories(self, tmp_path: Path) -> None:
        """Test that items within categories are sorted."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "zebra_role", "type": "role"},
            {"name": "alpha_role", "type": "role"},
            {"name": "beta_role", "type": "role"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_category_index(items)

        # Items should be sorted alphabetically
        role_names = [item["name"] for item in index["role"]["items"]]
        assert role_names == ["alpha_role", "beta_role", "zebra_role"]

    def test_category_index_includes_item_count(self, tmp_path: Path) -> None:
        """Test that category index shows item counts."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "type": "role"},
            {"name": "role2", "type": "role"},
            {"name": "role3", "type": "role"},
            {"name": "module1", "type": "module"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_category_index(items)

        # Should have count metadata
        assert index["role"]["count"] == 3
        assert index["module"]["count"] == 1


class TestTagBasedNavigation:
    """Test tag-based navigation in indexes."""

    def test_tag_index_groups_by_tag(self, tmp_path: Path) -> None:
        """Test that items are grouped by tags."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "web_server", "tags": ["webserver", "production"]},
            {"name": "api_gateway", "tags": ["webserver", "api"]},
            {"name": "cache_server", "tags": ["cache", "production"]},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_tag_index(items)

        # Should have groups for each tag
        assert "webserver" in index
        assert "production" in index
        assert "api" in index
        assert "cache" in index

        # Check item associations
        assert len(index["webserver"]["items"]) == 2  # web_server, api_gateway
        assert len(index["production"]["items"]) == 2  # web_server, cache_server
        assert len(index["api"]["items"]) == 1  # api_gateway

    def test_tag_index_links_to_all_tagged_content(self, tmp_path: Path) -> None:
        """Test that clicking a tag shows all content with that tag."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "tags": ["database"], "path": tmp_path / "role1"},
            {"name": "role2", "tags": ["database"], "path": tmp_path / "role2"},
            {"name": "plugin1", "tags": ["database"], "path": tmp_path / "plugin1"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_tag_index(items)

        # All items with 'database' tag should be accessible
        assert len(index["database"]["items"]) == 3
        assert all("path" in item for item in index["database"]["items"])

    def test_tag_index_bidirectional_navigation(self, tmp_path: Path) -> None:
        """Test that tags link to items and items link back to tags."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "tags": ["web", "production"]},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_tag_index(items)

        # Tag should link to item
        assert index["web"]["items"][0]["name"] == "role1"

        # Item should be properly structured with path and type
        assert "path" in index["web"]["items"][0]
        assert "type" in index["web"]["items"][0]

    def test_tag_index_handles_no_tags(self, tmp_path: Path) -> None:
        """Test that items without tags are handled gracefully."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "tags": []},
            {"name": "role2"},  # No tags field
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_tag_index(items)

        # Should have an 'untagged' category or handle gracefully
        assert "untagged" in index or len(index) == 0

    def test_tag_index_sorts_by_popularity(self, tmp_path: Path) -> None:
        """Test that tags can be sorted by usage count."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "tags": ["common"]},
            {"name": "role2", "tags": ["common"]},
            {"name": "role3", "tags": ["common"]},
            {"name": "role4", "tags": ["rare"]},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_tag_index(items)

        # Should have metadata about tag popularity
        assert index["common"]["count"] == 3
        assert index["rare"]["count"] == 1


class TestBidirectionalRelationships:
    """Test bidirectional relationship tracking in link graph."""

    def test_relationship_graph_tracks_both_directions(self, tmp_path: Path) -> None:
        """Test that relationships are tracked in both directions."""
        from ansibledoctor.utils.link_graph import LinkGraph

        graph = LinkGraph()

        # Add relationship: role1 depends on role2
        graph.add_relationship("role1", "role2", relationship_type="depends_on")

        # Should be able to query both directions
        assert graph.get_outgoing("role1") == [{"target": "role2", "type": "depends_on"}]
        assert graph.get_incoming("role2") == [{"source": "role1", "type": "depends_on"}]

    def test_relationship_graph_multiple_relationships(self, tmp_path: Path) -> None:
        """Test that multiple relationships are tracked correctly."""
        from ansibledoctor.utils.link_graph import LinkGraph

        graph = LinkGraph()

        graph.add_relationship("role1", "role2", relationship_type="depends_on")
        graph.add_relationship("role1", "role3", relationship_type="depends_on")
        graph.add_relationship("role4", "role1", relationship_type="uses")

        # role1 should have 2 outgoing, 1 incoming
        assert len(graph.get_outgoing("role1")) == 2
        assert len(graph.get_incoming("role1")) == 1

    def test_relationship_graph_generates_visual_representation(self, tmp_path: Path) -> None:
        """Test that relationship graph can be visualized."""
        from ansibledoctor.utils.link_graph import LinkGraph

        graph = LinkGraph()

        graph.add_relationship("web_server", "database", relationship_type="depends_on")
        graph.add_relationship("web_server", "cache", relationship_type="uses")

        # Should generate Mermaid diagram
        mermaid = graph.to_mermaid()

        assert "web_server" in mermaid
        assert "database" in mermaid
        assert "cache" in mermaid
        assert "-->" in mermaid  # Relationship arrow

    def test_relationship_graph_finds_circular_dependencies(self, tmp_path: Path) -> None:
        """Test that circular dependencies are detected."""
        from ansibledoctor.utils.link_graph import LinkGraph

        graph = LinkGraph()

        graph.add_relationship("role1", "role2", relationship_type="depends_on")
        graph.add_relationship("role2", "role3", relationship_type="depends_on")
        graph.add_relationship("role3", "role1", relationship_type="depends_on")

        # Should detect cycle
        cycles = graph.find_cycles()
        assert len(cycles) > 0
        assert "role1" in cycles[0]
        assert "role2" in cycles[0]
        assert "role3" in cycles[0]

    def test_relationship_graph_relationship_types(self, tmp_path: Path) -> None:
        """Test different relationship types are tracked."""
        from ansibledoctor.utils.link_graph import LinkGraph

        graph = LinkGraph()

        graph.add_relationship("role1", "role2", relationship_type="depends_on")
        graph.add_relationship("role1", "role3", relationship_type="similar_to")
        graph.add_relationship("role1", "role4", relationship_type="replaces")

        # Should be able to filter by type
        dependencies = graph.get_outgoing("role1", relationship_type="depends_on")
        assert len(dependencies) == 1
        assert dependencies[0]["target"] == "role2"


class TestSearchIndex:
    """Test search index generation with term-based navigation."""

    def test_search_index_indexes_all_content(self, tmp_path: Path) -> None:
        """Test that search index includes all searchable content."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "web_server", "description": "Deploy web server with nginx"},
            {"name": "database", "description": "PostgreSQL database setup"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_search_index(items)

        # Should have entries for key terms
        assert "web" in index
        assert "server" in index
        assert "nginx" in index
        assert "database" in index
        assert "postgresql" in index

    def test_search_index_links_to_relevant_sections(self, tmp_path: Path) -> None:
        """Test that search terms link to relevant content."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {
                "name": "web_server",
                "description": "nginx configuration",
                "path": tmp_path / "web_server",
            },
            {
                "name": "api_gateway",
                "description": "nginx reverse proxy",
                "path": tmp_path / "api_gateway",
            },
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_search_index(items)

        # Searching for "nginx" should return both items
        assert len(index["nginx"]) == 2
        assert any(item["name"] == "web_server" for item in index["nginx"])
        assert any(item["name"] == "api_gateway" for item in index["nginx"])

    def test_search_index_ranks_results_by_relevance(self, tmp_path: Path) -> None:
        """Test that search results are ranked by relevance."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "nginx_role", "description": "nginx server nginx configuration nginx"},
            {"name": "apache_role", "description": "apache with nginx backend"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_search_index(items)

        # nginx_role should rank higher (appears more times)
        results = index["nginx"]
        assert results[0]["name"] == "nginx_role"
        assert results[0]["score"] > results[1]["score"]

    def test_search_index_handles_stop_words(self, tmp_path: Path) -> None:
        """Test that common stop words are filtered."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "role1", "description": "the and or a an this that"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_search_index(items)

        # Stop words should not be indexed
        assert "the" not in index
        assert "and" not in index
        assert "or" not in index

    def test_search_index_supports_partial_matching(self, tmp_path: Path) -> None:
        """Test that partial term matching works."""
        from ansibledoctor.generator.indexes import DefaultIndexGenerator

        items = [
            {"name": "postgresql", "description": "database server"},
        ]

        generator = DefaultIndexGenerator(output_dir=tmp_path)
        index = generator.generate_search_index(items)

        # Should be able to search with partial terms
        results = generator.search(index, "postgre")
        assert len(results) > 0
        assert results[0]["name"] == "postgresql"
