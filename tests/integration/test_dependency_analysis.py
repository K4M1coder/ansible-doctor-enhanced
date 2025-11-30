"""Integration tests for collection dependency analysis.

Tests for analyzing role dependencies, detecting circular dependencies,
and exporting dependency graphs in various formats.
"""

from pathlib import Path

import pytest

from ansibledoctor.parser.dependency_graph import CircularDependencyError, DependencyGraph


@pytest.fixture
def collection_with_dependencies(tmp_path: Path) -> Path:
    """Create a mock collection with role dependencies.

    Structure:
        - app (depends on: database, cache)
        - database (no dependencies)
        - cache (no dependencies)
        - webserver (depends on: app)
    """
    collection_path = tmp_path / "test_namespace.test_collection"
    collection_path.mkdir()

    # Create galaxy.yml
    galaxy_yml = collection_path / "galaxy.yml"
    galaxy_yml.write_text(
        """
namespace: test_namespace
name: test_collection
version: 1.0.0
authors:
  - Test Author
dependencies: {}
"""
    )

    # Create roles directory
    roles_path = collection_path / "roles"
    roles_path.mkdir()

    # Create role: database (no dependencies)
    database_role = roles_path / "database"
    database_role.mkdir()
    (database_role / "meta").mkdir()
    (database_role / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Database role
dependencies: []
"""
    )

    # Create role: cache (no dependencies)
    cache_role = roles_path / "cache"
    cache_role.mkdir()
    (cache_role / "meta").mkdir()
    (cache_role / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Cache role
dependencies: []
"""
    )

    # Create role: app (depends on database and cache)
    app_role = roles_path / "app"
    app_role.mkdir()
    (app_role / "meta").mkdir()
    (app_role / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Application role
dependencies:
  - role: database
  - role: cache
"""
    )

    # Create role: webserver (depends on app)
    webserver_role = roles_path / "webserver"
    webserver_role.mkdir()
    (webserver_role / "meta").mkdir()
    (webserver_role / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Web server role
dependencies:
  - role: app
"""
    )

    return collection_path


@pytest.fixture
def collection_with_circular_deps(tmp_path: Path) -> Path:
    """Create a mock collection with circular role dependencies.

    Structure:
        - role_a (depends on: role_b)
        - role_b (depends on: role_c)
        - role_c (depends on: role_a)  # Creates cycle: A → B → C → A
    """
    collection_path = tmp_path / "circular_namespace.circular_collection"
    collection_path.mkdir()

    # Create galaxy.yml
    galaxy_yml = collection_path / "galaxy.yml"
    galaxy_yml.write_text(
        """
namespace: circular_namespace
name: circular_collection
version: 1.0.0
authors:
  - Test Author
dependencies: {}
"""
    )

    # Create roles directory
    roles_path = collection_path / "roles"
    roles_path.mkdir()

    # Create role: role_a (depends on role_b)
    role_a = roles_path / "role_a"
    role_a.mkdir()
    (role_a / "meta").mkdir()
    (role_a / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Role A
dependencies:
  - role: role_b
"""
    )

    # Create role: role_b (depends on role_c)
    role_b = roles_path / "role_b"
    role_b.mkdir()
    (role_b / "meta").mkdir()
    (role_b / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Role B
dependencies:
  - role: role_c
"""
    )

    # Create role: role_c (depends on role_a) - creates cycle
    role_c = roles_path / "role_c"
    role_c.mkdir()
    (role_c / "meta").mkdir()
    (role_c / "meta" / "main.yml").write_text(
        """
galaxy_info:
  author: Test Author
  description: Role C
dependencies:
  - role: role_a
"""
    )

    return collection_path


class TestDependencyAnalysis:
    """Integration tests for dependency analysis on real collections."""

    def test_analyze_collection_with_dependencies(self, collection_with_dependencies: Path) -> None:
        """Test analyzing a collection with role dependencies."""
        # Build dependency graph
        graph = DependencyGraph.from_collection_path(collection_with_dependencies)

        # Verify roles are discovered
        assert "app" in graph._nodes
        assert "database" in graph._nodes
        assert "cache" in graph._nodes
        assert "webserver" in graph._nodes

        # Verify dependencies are detected
        app_deps = graph.get_dependencies("app")
        assert "database" in app_deps
        assert "cache" in app_deps

        webserver_deps = graph.get_dependencies("webserver")
        assert "app" in webserver_deps

        # Verify no circular dependencies
        assert not graph.has_circular_dependencies()
        assert graph.find_circular_dependencies() == []

    def test_topological_sort_respects_dependencies(
        self, collection_with_dependencies: Path
    ) -> None:
        """Test that topological sort returns roles in dependency order."""
        graph = DependencyGraph.from_collection_path(collection_with_dependencies)

        # Get topological sort
        sorted_roles = graph.topological_sort()

        # Verify dependencies come before dependents
        # database and cache have no dependencies, should come first
        assert sorted_roles.index("database") < sorted_roles.index("app")
        assert sorted_roles.index("cache") < sorted_roles.index("app")

        # app depends on database and cache, should come before webserver
        assert sorted_roles.index("app") < sorted_roles.index("webserver")


class TestCircularDependencyDetection:
    """Integration tests for circular dependency detection."""

    def test_detect_circular_dependencies(self, collection_with_circular_deps: Path) -> None:
        """Test detecting circular dependencies in a collection."""
        # Build dependency graph
        graph = DependencyGraph.from_collection_path(collection_with_circular_deps)

        # Verify circular dependencies are detected
        assert graph.has_circular_dependencies()

        # Get circular dependencies
        circular_deps = graph.find_circular_dependencies()
        assert len(circular_deps) > 0

        # Verify the cycle is detected (should contain role_a, role_b, role_c)
        cycle = circular_deps[0]
        assert "role_a" in cycle
        assert "role_b" in cycle
        assert "role_c" in cycle

    def test_topological_sort_fails_with_circular_deps(
        self, collection_with_circular_deps: Path
    ) -> None:
        """Test that topological sort raises error for circular dependencies."""
        graph = DependencyGraph.from_collection_path(collection_with_circular_deps)

        # Topological sort should raise CircularDependencyError
        with pytest.raises(CircularDependencyError) as exc_info:
            graph.topological_sort()

        # Verify error message contains cycle information
        assert "Circular dependency detected" in str(exc_info.value)


class TestExportFormats:
    """Integration tests for exporting dependency graphs in various formats."""

    def test_export_to_ascii_tree(self, collection_with_dependencies: Path) -> None:
        """Test exporting dependency graph as ASCII tree."""
        graph = DependencyGraph.from_collection_path(collection_with_dependencies)

        # Export to ASCII tree
        ascii_tree = graph.to_ascii_tree()

        # Verify output contains role names
        assert "app" in ascii_tree
        assert "database" in ascii_tree
        assert "cache" in ascii_tree
        assert "webserver" in ascii_tree

        # Verify tree structure characters are present
        assert "├──" in ascii_tree or "└──" in ascii_tree or "│" in ascii_tree

    def test_export_to_json(self, collection_with_dependencies: Path) -> None:
        """Test exporting dependency graph as JSON."""
        graph = DependencyGraph.from_collection_path(collection_with_dependencies)

        # Export to JSON
        json_output = graph.to_json()

        # Verify structure
        assert "nodes" in json_output
        assert "edges" in json_output
        assert "circular_dependencies" in json_output
        assert "has_cycles" in json_output

        # Verify nodes contain all roles
        node_names = [node["name"] for node in json_output["nodes"]]
        assert "app" in node_names
        assert "database" in node_names
        assert "cache" in node_names
        assert "webserver" in node_names

        # Verify edges exist
        assert len(json_output["edges"]) > 0

        # Verify no cycles
        assert json_output["has_cycles"] is False
        assert json_output["circular_dependencies"] == []

    def test_export_to_mermaid(self, collection_with_dependencies: Path) -> None:
        """Test exporting dependency graph as Mermaid diagram."""
        graph = DependencyGraph.from_collection_path(collection_with_dependencies)

        # Export to Mermaid
        mermaid_output = graph.to_mermaid()

        # Verify Mermaid syntax
        assert "graph TD" in mermaid_output

        # Verify role nodes are present
        assert "app" in mermaid_output
        assert "database" in mermaid_output
        assert "cache" in mermaid_output
        assert "webserver" in mermaid_output

        # Verify arrows for dependencies
        assert "-->" in mermaid_output

    def test_mermaid_highlights_circular_dependencies(
        self, collection_with_circular_deps: Path
    ) -> None:
        """Test that Mermaid export highlights circular dependencies in red."""
        graph = DependencyGraph.from_collection_path(collection_with_circular_deps)

        # Export to Mermaid
        mermaid_output = graph.to_mermaid()

        # Verify Mermaid syntax
        assert "graph TD" in mermaid_output

        # Verify red styling for circular dependencies
        # The implementation should add style classes for cycles
        assert "style" in mermaid_output or "classDef" in mermaid_output

    def test_json_export_includes_circular_deps(self, collection_with_circular_deps: Path) -> None:
        """Test that JSON export includes circular dependency information."""
        graph = DependencyGraph.from_collection_path(collection_with_circular_deps)

        # Export to JSON
        json_output = graph.to_json()

        # Verify has_cycles is True
        assert json_output["has_cycles"] is True

        # Verify circular_dependencies list is not empty
        assert len(json_output["circular_dependencies"]) > 0

        # Verify the cycle contains the expected roles
        cycle = json_output["circular_dependencies"][0]
        assert "role_a" in cycle
        assert "role_b" in cycle
        assert "role_c" in cycle
