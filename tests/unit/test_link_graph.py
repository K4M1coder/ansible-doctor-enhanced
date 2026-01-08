"""
Unit tests for LinkGraph: Bidirectional relationship tracking.

Tests the graph data structure for managing relationships between
documentation entities with support for:
- Bidirectional link tracking (A→B implies B←A)
- Multiple relationship types (depends_on, similar_to, replaces, uses)
- Cycle detection for circular dependencies
- Graph visualization (Mermaid diagrams)
- Relationship filtering and querying
"""

import pytest

from ansibledoctor.utils.link_graph import LinkGraph, RelationshipType


class TestLinkGraphBasics:
    """Test basic LinkGraph operations."""

    def test_add_relationship_creates_bidirectional_links(self) -> None:
        """Test that adding a relationship creates both outgoing and incoming links."""
        graph = LinkGraph()

        graph.add_relationship("node_a", "node_b", RelationshipType.DEPENDS_ON)

        # Check outgoing from node_a
        outgoing = graph.get_outgoing("node_a")
        assert len(outgoing) == 1
        assert outgoing[0]["target"] == "node_b"
        assert outgoing[0]["type"] == RelationshipType.DEPENDS_ON

        # Check incoming to node_b
        incoming = graph.get_incoming("node_b")
        assert len(incoming) == 1
        assert incoming[0]["source"] == "node_a"
        assert incoming[0]["type"] == RelationshipType.DEPENDS_ON

    def test_add_multiple_relationships_from_same_node(self) -> None:
        """Test that a node can have multiple outgoing relationships."""
        graph = LinkGraph()

        graph.add_relationship("web_server", "database", RelationshipType.DEPENDS_ON)
        graph.add_relationship("web_server", "cache", RelationshipType.USES)
        graph.add_relationship("web_server", "auth_service", RelationshipType.DEPENDS_ON)

        outgoing = graph.get_outgoing("web_server")
        assert len(outgoing) == 3

        targets = [rel["target"] for rel in outgoing]
        assert "database" in targets
        assert "cache" in targets
        assert "auth_service" in targets

    def test_add_multiple_relationships_to_same_node(self) -> None:
        """Test that a node can have multiple incoming relationships."""
        graph = LinkGraph()

        graph.add_relationship("web_server", "database", RelationshipType.DEPENDS_ON)
        graph.add_relationship("api_gateway", "database", RelationshipType.DEPENDS_ON)
        graph.add_relationship("worker_service", "database", RelationshipType.USES)

        incoming = graph.get_incoming("database")
        assert len(incoming) == 3

        sources = [rel["source"] for rel in incoming]
        assert "web_server" in sources
        assert "api_gateway" in sources
        assert "worker_service" in sources

    def test_get_all_nodes_returns_unique_nodes(self) -> None:
        """Test that all nodes in the graph can be retrieved."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.USES)
        graph.add_relationship("c", "a", RelationshipType.SIMILAR_TO)

        nodes = graph.get_all_nodes()
        assert len(nodes) == 3
        assert "a" in nodes
        assert "b" in nodes
        assert "c" in nodes

    def test_remove_relationship_removes_both_directions(self) -> None:
        """Test that removing a relationship removes both outgoing and incoming links."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.remove_relationship("a", "b", RelationshipType.DEPENDS_ON)

        assert len(graph.get_outgoing("a")) == 0
        assert len(graph.get_incoming("b")) == 0


class TestRelationshipTypes:
    """Test different relationship types and filtering."""

    def test_filter_by_relationship_type(self) -> None:
        """Test filtering relationships by type."""
        graph = LinkGraph()

        graph.add_relationship("role1", "role2", RelationshipType.DEPENDS_ON)
        graph.add_relationship("role1", "role3", RelationshipType.SIMILAR_TO)
        graph.add_relationship("role1", "role4", RelationshipType.USES)

        # Filter by DEPENDS_ON
        dependencies = graph.get_outgoing("role1", relationship_type=RelationshipType.DEPENDS_ON)
        assert len(dependencies) == 1
        assert dependencies[0]["target"] == "role2"

        # Filter by SIMILAR_TO
        similar = graph.get_outgoing("role1", relationship_type=RelationshipType.SIMILAR_TO)
        assert len(similar) == 1
        assert similar[0]["target"] == "role3"

    def test_relationship_type_enum_values(self) -> None:
        """Test that all expected relationship types exist."""
        assert hasattr(RelationshipType, "DEPENDS_ON")
        assert hasattr(RelationshipType, "SIMILAR_TO")
        assert hasattr(RelationshipType, "REPLACES")
        assert hasattr(RelationshipType, "USES")
        assert hasattr(RelationshipType, "INCLUDES")
        assert hasattr(RelationshipType, "REFERENCES")

    def test_relationship_metadata(self) -> None:
        """Test that relationships can have additional metadata."""
        graph = LinkGraph()

        graph.add_relationship(
            "web_server",
            "database",
            RelationshipType.DEPENDS_ON,
            metadata={"required": True, "version": ">=10.0"},
        )

        outgoing = graph.get_outgoing("web_server")
        assert outgoing[0]["metadata"]["required"] is True
        assert outgoing[0]["metadata"]["version"] == ">=10.0"


class TestCycleDetection:
    """Test circular dependency detection."""

    def test_find_simple_cycle(self) -> None:
        """Test detection of a simple 3-node cycle."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "a", RelationshipType.DEPENDS_ON)

        cycles = graph.find_cycles()
        assert len(cycles) > 0

        # Should find cycle a -> b -> c -> a
        cycle = cycles[0]
        assert len(cycle) == 3
        assert "a" in cycle
        assert "b" in cycle
        assert "c" in cycle

    def test_find_self_cycle(self) -> None:
        """Test detection of a self-referential cycle."""
        graph = LinkGraph()

        graph.add_relationship("node", "node", RelationshipType.DEPENDS_ON)

        cycles = graph.find_cycles()
        assert len(cycles) > 0
        assert cycles[0] == ["node"]

    def test_no_cycles_in_dag(self) -> None:
        """Test that directed acyclic graph returns no cycles."""
        graph = LinkGraph()

        # Create a DAG: a -> b -> c, a -> d
        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.DEPENDS_ON)
        graph.add_relationship("a", "d", RelationshipType.DEPENDS_ON)

        cycles = graph.find_cycles()
        assert len(cycles) == 0

    def test_find_multiple_cycles(self) -> None:
        """Test detection of multiple independent cycles."""
        graph = LinkGraph()

        # Cycle 1: a -> b -> a
        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "a", RelationshipType.DEPENDS_ON)

        # Cycle 2: x -> y -> z -> x
        graph.add_relationship("x", "y", RelationshipType.DEPENDS_ON)
        graph.add_relationship("y", "z", RelationshipType.DEPENDS_ON)
        graph.add_relationship("z", "x", RelationshipType.DEPENDS_ON)

        cycles = graph.find_cycles()
        assert len(cycles) >= 2

    def test_cycle_only_in_depends_on_type(self) -> None:
        """Test that cycles are only detected for DEPENDS_ON relationships."""
        graph = LinkGraph()

        # Create cycle with SIMILAR_TO (should not count as dependency cycle)
        graph.add_relationship("a", "b", RelationshipType.SIMILAR_TO)
        graph.add_relationship("b", "c", RelationshipType.SIMILAR_TO)
        graph.add_relationship("c", "a", RelationshipType.SIMILAR_TO)

        cycles = graph.find_cycles(relationship_type=RelationshipType.DEPENDS_ON)
        assert len(cycles) == 0


class TestGraphVisualization:
    """Test graph visualization and export."""

    def test_to_mermaid_generates_valid_syntax(self) -> None:
        """Test that Mermaid diagram syntax is generated correctly."""
        graph = LinkGraph()

        graph.add_relationship("web_server", "database", RelationshipType.DEPENDS_ON)
        graph.add_relationship("web_server", "cache", RelationshipType.USES)

        mermaid = graph.to_mermaid()

        # Check for Mermaid graph declaration
        assert "graph" in mermaid or "flowchart" in mermaid

        # Check for nodes
        assert "web_server" in mermaid
        assert "database" in mermaid
        assert "cache" in mermaid

        # Check for relationships
        assert "-->" in mermaid

    def test_to_mermaid_different_relationship_styles(self) -> None:
        """Test that different relationship types have different visual styles."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "d", RelationshipType.SIMILAR_TO)
        graph.add_relationship("e", "f", RelationshipType.REPLACES)

        mermaid = graph.to_mermaid()

        # Different relationship types should have different arrows or styles
        # DEPENDS_ON: solid arrow -->
        # SIMILAR_TO: dotted arrow -.->
        # REPLACES: thick arrow ==>
        assert "-->" in mermaid or "--->" in mermaid
        assert ".->" in mermaid or "-..->" in mermaid or "===>" in mermaid

    def test_to_dict_exports_full_graph(self) -> None:
        """Test that graph can be exported to dictionary."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.USES)

        data = graph.to_dict()

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2

    def test_from_dict_imports_graph(self) -> None:
        """Test that graph can be imported from dictionary."""
        data = {
            "nodes": ["a", "b", "c"],
            "edges": [
                {"source": "a", "target": "b", "type": "DEPENDS_ON"},
                {"source": "b", "target": "c", "type": "USES"},
            ],
        }

        graph = LinkGraph.from_dict(data)

        assert len(graph.get_all_nodes()) == 3
        assert len(graph.get_outgoing("a")) == 1
        assert len(graph.get_outgoing("b")) == 1


class TestGraphTraversal:
    """Test graph traversal and path finding."""

    def test_find_path_between_nodes(self) -> None:
        """Test finding a path between two nodes."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "d", RelationshipType.DEPENDS_ON)

        path = graph.find_path("a", "d")
        assert path == ["a", "b", "c", "d"]

    def test_find_path_no_connection(self) -> None:
        """Test that None is returned when no path exists."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "d", RelationshipType.DEPENDS_ON)

        path = graph.find_path("a", "d")
        assert path is None

    def test_get_descendants_returns_all_reachable_nodes(self) -> None:
        """Test getting all nodes reachable from a starting node."""
        graph = LinkGraph()

        graph.add_relationship("root", "child1", RelationshipType.DEPENDS_ON)
        graph.add_relationship("root", "child2", RelationshipType.DEPENDS_ON)
        graph.add_relationship("child1", "grandchild", RelationshipType.DEPENDS_ON)

        descendants = graph.get_descendants("root")
        assert len(descendants) == 3
        assert "child1" in descendants
        assert "child2" in descendants
        assert "grandchild" in descendants

    def test_get_ancestors_returns_all_incoming_paths(self) -> None:
        """Test getting all nodes that lead to a target node."""
        graph = LinkGraph()

        graph.add_relationship("a", "target", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "target", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "b", RelationshipType.DEPENDS_ON)

        ancestors = graph.get_ancestors("target")
        assert len(ancestors) == 3
        assert "a" in ancestors
        assert "b" in ancestors
        assert "c" in ancestors

    def test_topological_sort_orders_dependencies(self) -> None:
        """Test that topological sort provides valid dependency order."""
        graph = LinkGraph()

        graph.add_relationship("build", "compile", RelationshipType.DEPENDS_ON)
        graph.add_relationship("compile", "lint", RelationshipType.DEPENDS_ON)
        graph.add_relationship("test", "build", RelationshipType.DEPENDS_ON)

        order = graph.topological_sort()

        # lint should come before compile, compile before build, build before test
        assert order.index("lint") < order.index("compile")
        assert order.index("compile") < order.index("build")
        assert order.index("build") < order.index("test")

    def test_topological_sort_fails_on_cycle(self) -> None:
        """Test that topological sort raises error on cyclic graph."""
        graph = LinkGraph()

        graph.add_relationship("a", "b", RelationshipType.DEPENDS_ON)
        graph.add_relationship("b", "c", RelationshipType.DEPENDS_ON)
        graph.add_relationship("c", "a", RelationshipType.DEPENDS_ON)

        with pytest.raises(ValueError, match="cycle"):
            graph.topological_sort()
