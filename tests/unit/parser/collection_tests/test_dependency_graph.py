"""
Unit tests for collection dependency graph analysis.

Tests role dependency discovery, circular dependency detection,
and topological sorting for US10.
"""

from pathlib import Path

import pytest

from ansibledoctor.parser.dependency_graph import CircularDependencyError, DependencyGraph


class TestDependencyGraphConstruction:
    """Test building dependency graphs from collection roles (T173)."""

    def test_empty_graph(self):
        """Test creating an empty dependency graph."""
        graph = DependencyGraph()

        assert graph.node_count() == 0
        assert graph.edge_count() == 0
        assert list(graph.get_all_nodes()) == []

    def test_single_role_no_dependencies(self):
        """Test graph with single role without dependencies."""
        graph = DependencyGraph()
        graph.add_role("webserver", dependencies=[])

        assert graph.node_count() == 1
        assert graph.edge_count() == 0
        assert "webserver" in graph
        assert graph.get_dependencies("webserver") == []

    def test_two_roles_with_dependency(self):
        """Test graph with two roles where one depends on another."""
        graph = DependencyGraph()
        graph.add_role("database", dependencies=[])
        graph.add_role("webserver", dependencies=["database"])

        assert graph.node_count() == 2
        assert graph.edge_count() == 1
        assert graph.get_dependencies("webserver") == ["database"]
        assert graph.get_dependencies("database") == []

    def test_multiple_dependencies(self):
        """Test role with multiple dependencies."""
        graph = DependencyGraph()
        graph.add_role("common", dependencies=[])
        graph.add_role("database", dependencies=["common"])
        graph.add_role("webserver", dependencies=["common", "database"])

        assert graph.node_count() == 3
        assert graph.edge_count() == 3
        assert set(graph.get_dependencies("webserver")) == {"common", "database"}

    def test_complex_dependency_chain(self):
        """Test complex dependency chain A → B → C → D."""
        graph = DependencyGraph()
        graph.add_role("role_d", dependencies=[])
        graph.add_role("role_c", dependencies=["role_d"])
        graph.add_role("role_b", dependencies=["role_c"])
        graph.add_role("role_a", dependencies=["role_b"])

        assert graph.node_count() == 4
        assert graph.edge_count() == 3


class TestDependencyDetection:
    """Test detecting role dependencies from meta/main.yml (T174)."""

    def test_parse_empty_meta_file(self, tmp_path: Path):
        """Test parsing meta/main.yml with no dependencies."""
        role_path = tmp_path / "roles" / "webserver"
        meta_dir = role_path / "meta"
        meta_dir.mkdir(parents=True)

        meta_file = meta_dir / "main.yml"
        meta_file.write_text("---\n# No dependencies\n")

        graph = DependencyGraph.from_collection_path(tmp_path)

        assert "webserver" in graph
        assert graph.get_dependencies("webserver") == []

    def test_parse_meta_with_dependencies(self, tmp_path: Path):
        """Test parsing meta/main.yml with dependencies list."""
        # Create database role (no dependencies)
        db_role = tmp_path / "roles" / "database"
        (db_role / "meta").mkdir(parents=True)
        (db_role / "meta" / "main.yml").write_text("---\ndependencies: []\n")

        # Create webserver role (depends on database)
        web_role = tmp_path / "roles" / "webserver"
        (web_role / "meta").mkdir(parents=True)
        (web_role / "meta" / "main.yml").write_text(
            "---\n" "dependencies:\n" "  - role: database\n"
        )

        graph = DependencyGraph.from_collection_path(tmp_path)

        assert graph.get_dependencies("webserver") == ["database"]

    def test_parse_meta_with_collection_fqcn(self, tmp_path: Path):
        """Test parsing dependencies with collection FQCN format."""
        role_path = tmp_path / "roles" / "app"
        (role_path / "meta").mkdir(parents=True)
        (role_path / "meta" / "main.yml").write_text(
            "---\n" "dependencies:\n" "  - role: my_namespace.my_collection.common\n"
        )

        graph = DependencyGraph.from_collection_path(tmp_path)

        assert "app" in graph
        deps = graph.get_dependencies("app")
        assert "my_namespace.my_collection.common" in deps


class TestCircularDependencyDetection:
    """Test detecting circular dependencies (T175)."""

    def test_no_circular_dependencies(self):
        """Test graph without circular dependencies."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=[])
        graph.add_role("b", dependencies=["a"])
        graph.add_role("c", dependencies=["b"])

        assert not graph.has_circular_dependencies()
        assert graph.find_circular_dependencies() == []

    def test_simple_circular_dependency(self):
        """Test detecting simple circular dependency A → B → A."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["a"])

        assert graph.has_circular_dependencies()
        cycles = graph.find_circular_dependencies()
        assert len(cycles) == 1
        assert set(cycles[0]) == {"a", "b"}

    def test_three_way_circular_dependency(self):
        """Test detecting three-way circular dependency A → B → C → A."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["c"])
        graph.add_role("c", dependencies=["a"])

        assert graph.has_circular_dependencies()
        cycles = graph.find_circular_dependencies()
        assert len(cycles) == 1
        assert set(cycles[0]) == {"a", "b", "c"}

    def test_self_dependency(self):
        """Test detecting self-dependency A → A."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["a"])

        assert graph.has_circular_dependencies()
        cycles = graph.find_circular_dependencies()
        assert len(cycles) == 1
        assert cycles[0] == ["a"]

    def test_multiple_circular_dependencies(self):
        """Test detecting multiple separate circular dependencies."""
        graph = DependencyGraph()
        # First cycle: A → B → A
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["a"])
        # Second cycle: C → D → C
        graph.add_role("c", dependencies=["d"])
        graph.add_role("d", dependencies=["c"])

        assert graph.has_circular_dependencies()
        cycles = graph.find_circular_dependencies()
        assert len(cycles) == 2


class TestMissingDependencies:
    """Test handling missing dependencies gracefully (T176)."""

    def test_dependency_on_nonexistent_role(self):
        """Test handling dependency on role that doesn't exist."""
        graph = DependencyGraph()
        graph.add_role("webserver", dependencies=["database"])

        # Should not raise, but should report missing
        missing = graph.get_missing_dependencies()
        assert "database" in missing["webserver"]

    def test_no_missing_dependencies(self):
        """Test graph with all dependencies satisfied."""
        graph = DependencyGraph()
        graph.add_role("database", dependencies=[])
        graph.add_role("webserver", dependencies=["database"])

        missing = graph.get_missing_dependencies()
        assert missing == {} or all(len(deps) == 0 for deps in missing.values())

    def test_multiple_missing_dependencies(self):
        """Test role with multiple missing dependencies."""
        graph = DependencyGraph()
        graph.add_role("app", dependencies=["db", "cache", "queue"])

        missing = graph.get_missing_dependencies()
        assert set(missing["app"]) == {"db", "cache", "queue"}


class TestTopologicalSort:
    """Test topological sorting for dependency order (T177)."""

    def test_topological_sort_linear_chain(self):
        """Test topological sort on linear dependency chain."""
        graph = DependencyGraph()
        graph.add_role("d", dependencies=[])
        graph.add_role("c", dependencies=["d"])
        graph.add_role("b", dependencies=["c"])
        graph.add_role("a", dependencies=["b"])

        sorted_roles = graph.topological_sort()

        # d should come before c, c before b, b before a
        assert sorted_roles.index("d") < sorted_roles.index("c")
        assert sorted_roles.index("c") < sorted_roles.index("b")
        assert sorted_roles.index("b") < sorted_roles.index("a")

    def test_topological_sort_diamond_dependency(self):
        """Test topological sort on diamond-shaped dependency."""
        graph = DependencyGraph()
        graph.add_role("base", dependencies=[])
        graph.add_role("left", dependencies=["base"])
        graph.add_role("right", dependencies=["base"])
        graph.add_role("top", dependencies=["left", "right"])

        sorted_roles = graph.topological_sort()

        # base must come first
        assert sorted_roles[0] == "base"
        # top must come last
        assert sorted_roles[-1] == "top"
        # left and right can be in any order but after base
        assert sorted_roles.index("left") > sorted_roles.index("base")
        assert sorted_roles.index("right") > sorted_roles.index("base")

    def test_topological_sort_no_dependencies(self):
        """Test topological sort with roles that have no dependencies."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=[])
        graph.add_role("b", dependencies=[])
        graph.add_role("c", dependencies=[])

        sorted_roles = graph.topological_sort()

        # All roles should be present, order doesn't matter
        assert set(sorted_roles) == {"a", "b", "c"}

    def test_topological_sort_with_circular_dependency(self):
        """Test that topological sort raises error on circular dependency."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["a"])

        with pytest.raises(CircularDependencyError):
            graph.topological_sort()


class TestMermaidExport:
    """Test exporting dependency graph to Mermaid format (T178)."""

    def test_export_empty_graph_to_mermaid(self):
        """Test exporting empty graph to Mermaid format."""
        graph = DependencyGraph()
        mermaid = graph.to_mermaid()

        assert "graph TD" in mermaid or "graph LR" in mermaid

    def test_export_simple_dependency_to_mermaid(self):
        """Test exporting simple dependency to Mermaid format."""
        graph = DependencyGraph()
        graph.add_role("database", dependencies=[])
        graph.add_role("webserver", dependencies=["database"])

        mermaid = graph.to_mermaid()

        assert "graph" in mermaid
        assert "webserver" in mermaid
        assert "database" in mermaid
        assert "-->" in mermaid or "--->" in mermaid

    def test_mermaid_shows_circular_dependencies(self):
        """Test that Mermaid export highlights circular dependencies."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["a"])

        mermaid = graph.to_mermaid()

        # Should mark circular dependencies visually
        assert "style" in mermaid.lower() or "class" in mermaid.lower()


class TestASCIITreeExport:
    """Test exporting dependency graph to ASCII tree format (T179)."""

    def test_export_empty_graph_to_ascii(self):
        """Test exporting empty graph to ASCII tree."""
        graph = DependencyGraph()
        ascii_tree = graph.to_ascii_tree()

        assert isinstance(ascii_tree, str)

    def test_export_simple_dependency_to_ascii(self):
        """Test exporting simple dependency to ASCII tree."""
        graph = DependencyGraph()
        graph.add_role("database", dependencies=[])
        graph.add_role("webserver", dependencies=["database"])

        ascii_tree = graph.to_ascii_tree()

        assert "webserver" in ascii_tree
        assert "database" in ascii_tree
        # Should show tree structure with characters like ├── or └──
        assert any(char in ascii_tree for char in ["├", "└", "│", "─"])

    def test_ascii_tree_shows_hierarchy(self):
        """Test that ASCII tree shows dependency hierarchy."""
        graph = DependencyGraph()
        graph.add_role("base", dependencies=[])
        graph.add_role("middle", dependencies=["base"])
        graph.add_role("top", dependencies=["middle"])

        ascii_tree = graph.to_ascii_tree()

        # Check indentation increases with depth
        lines = ascii_tree.split("\n")
        assert len(lines) >= 3


class TestJSONExport:
    """Test exporting dependency graph to JSON format (T180)."""

    def test_export_empty_graph_to_json(self):
        """Test exporting empty graph to JSON format."""
        graph = DependencyGraph()
        json_data = graph.to_json()

        assert "nodes" in json_data or "roles" in json_data
        assert "edges" in json_data or "dependencies" in json_data

    def test_export_simple_dependency_to_json(self):
        """Test exporting simple dependency to JSON format."""
        graph = DependencyGraph()
        graph.add_role("database", dependencies=[])
        graph.add_role("webserver", dependencies=["database"])

        json_data = graph.to_json()

        # Should contain role information
        assert any("webserver" in str(v) for v in json_data.values())
        assert any("database" in str(v) for v in json_data.values())

    def test_json_includes_circular_dependency_info(self):
        """Test that JSON export includes circular dependency information."""
        graph = DependencyGraph()
        graph.add_role("a", dependencies=["b"])
        graph.add_role("b", dependencies=["a"])

        json_data = graph.to_json()

        # Should have field indicating circular dependencies
        assert "circular_dependencies" in json_data or "cycles" in json_data

    def test_json_structure_is_valid(self):
        """Test that JSON export has valid structure."""
        graph = DependencyGraph()
        graph.add_role("role1", dependencies=[])
        graph.add_role("role2", dependencies=["role1"])

        json_data = graph.to_json()

        # Should be serializable
        import json

        json_str = json.dumps(json_data)
        assert isinstance(json_str, str)
