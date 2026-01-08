"""Link graph utilities for tracking bidirectional relationships.

This module provides data structures and algorithms for managing link relationships
between documentation items, including cycle detection, graph traversal, and visualization.
"""

from __future__ import annotations

from collections import defaultdict, deque
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class RelationshipType(Enum):
    """Types of relationships between documentation items."""

    DEPENDS_ON = "depends_on"  # Item depends on another item
    SIMILAR_TO = "similar_to"  # Item is similar to another item
    REPLACES = "replaces"  # Item replaces deprecated item
    USES = "uses"  # Item uses another item
    INCLUDES = "includes"  # Item includes another item
    REFERENCES = "references"  # Item references another item


class LinkGraph:
    """Graph structure for tracking bidirectional relationships between items.

    This class maintains a directed graph where nodes represent documentation items
    and edges represent typed relationships. The graph automatically maintains
    bidirectional tracking (both outgoing and incoming edges).

    Attributes:
        _outgoing: Maps (node, relationship_type) → set of target nodes
        _incoming: Maps (node, relationship_type) → set of source nodes
        _metadata: Maps (source, target, type) → relationship metadata
    """

    def __init__(self) -> None:
        """Initialize an empty link graph."""
        # Maps (node, rel_type) → {target_nodes}
        self._outgoing: Dict[Tuple[str, RelationshipType], Set[str]] = defaultdict(set)
        # Maps (node, rel_type) → {source_nodes}
        self._incoming: Dict[Tuple[str, RelationshipType], Set[str]] = defaultdict(set)
        # Maps (source, target, rel_type) → metadata dict
        self._metadata: Dict[Tuple[str, str, RelationshipType], Dict[str, Any]] = {}

    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: RelationshipType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a relationship between two nodes.

        Args:
            source: Source node identifier
            target: Target node identifier
            relationship_type: Type of relationship
            metadata: Optional metadata about the relationship
        """
        # Add to outgoing edges
        self._outgoing[(source, relationship_type)].add(target)
        # Add to incoming edges (bidirectional tracking)
        self._incoming[(target, relationship_type)].add(source)

        # Store metadata if provided
        if metadata:
            self._metadata[(source, target, relationship_type)] = metadata

    def remove_relationship(
        self, source: str, target: str, relationship_type: RelationshipType
    ) -> None:
        """Remove a relationship between two nodes.

        Args:
            source: Source node identifier
            target: Target node identifier
            relationship_type: Type of relationship
        """
        # Remove from outgoing edges
        key_out = (source, relationship_type)
        if key_out in self._outgoing:
            self._outgoing[key_out].discard(target)
            if not self._outgoing[key_out]:
                del self._outgoing[key_out]

        # Remove from incoming edges
        key_in = (target, relationship_type)
        if key_in in self._incoming:
            self._incoming[key_in].discard(source)
            if not self._incoming[key_in]:
                del self._incoming[key_in]

        # Remove metadata
        meta_key = (source, target, relationship_type)
        if meta_key in self._metadata:
            del self._metadata[meta_key]

    def get_outgoing(
        self, node: str, relationship_type: Optional[RelationshipType] = None
    ) -> List[Dict[str, Any]]:
        """Get all relationships where the given node is the source.

        Args:
            node: Node identifier
            relationship_type: Optional filter by relationship type

        Returns:
            List of relationship dictionaries with 'target', 'type', and optional 'metadata'
        """
        results = []

        for (source, rel_type), targets in self._outgoing.items():
            if source == node:
                if relationship_type is None or rel_type == relationship_type:
                    for target in targets:
                        rel_dict = {"target": target, "type": rel_type}
                        # Add metadata if present
                        meta_key = (source, target, rel_type)
                        if meta_key in self._metadata:
                            rel_dict["metadata"] = self._metadata[meta_key]
                        results.append(rel_dict)

        return results

    def get_incoming(
        self, node: str, relationship_type: Optional[RelationshipType] = None
    ) -> List[Dict[str, Any]]:
        """Get all relationships where the given node is the target.

        Args:
            node: Node identifier
            relationship_type: Optional filter by relationship type

        Returns:
            List of relationship dictionaries with 'source', 'type', and optional 'metadata'
        """
        results = []

        for (target, rel_type), sources in self._incoming.items():
            if target == node:
                if relationship_type is None or rel_type == relationship_type:
                    for source in sources:
                        rel_dict = {"source": source, "type": rel_type}
                        # Add metadata if present
                        meta_key = (source, node, rel_type)
                        if meta_key in self._metadata:
                            rel_dict["metadata"] = self._metadata[meta_key]
                        results.append(rel_dict)

        return results

    def get_all_nodes(self) -> Set[str]:
        """Get all nodes in the graph.

        Returns:
            Set of all node identifiers
        """
        nodes = set()
        for node, _ in self._outgoing:
            nodes.add(node)
        for node, _ in self._incoming:
            nodes.add(node)
        return nodes

    def find_cycles(self, relationship_type: Optional[RelationshipType] = None) -> List[List[str]]:
        """Find all cycles in the graph using DFS.

        Args:
            relationship_type: Optional filter by relationship type

        Returns:
            List of cycles, where each cycle is a list of node identifiers
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> None:
            """Depth-first search to detect cycles."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Get outgoing edges
            outgoing_rels = self.get_outgoing(node, relationship_type)

            for rel in outgoing_rels:
                neighbor = rel["target"]
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        # Check all nodes
        for node in self.get_all_nodes():
            if node not in visited:
                dfs(node)

        return cycles

    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find a path between two nodes using BFS.

        Args:
            start: Start node identifier
            end: End node identifier

        Returns:
            List of node identifiers forming the path, or None if no path exists
        """
        if start == end:
            return [start]

        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            node, path = queue.popleft()

            # Get all outgoing neighbors (across all relationship types)
            outgoing_rels = self.get_outgoing(node)
            for rel in outgoing_rels:
                neighbor = rel["target"]
                if neighbor == end:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_descendants(self, node: str) -> Set[str]:
        """Get all nodes reachable from the given node.

        Args:
            node: Node identifier

        Returns:
            Set of descendant node identifiers
        """
        descendants = set()
        visited = set()
        queue = deque([node])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            # Get outgoing neighbors
            outgoing_rels = self.get_outgoing(current)
            for rel in outgoing_rels:
                neighbor = rel["target"]
                if neighbor != node:  # Don't include the start node
                    descendants.add(neighbor)
                if neighbor not in visited:
                    queue.append(neighbor)

        return descendants

    def get_ancestors(self, node: str) -> Set[str]:
        """Get all nodes that can reach the given node.

        Args:
            node: Node identifier

        Returns:
            Set of ancestor node identifiers
        """
        ancestors = set()
        visited = set()
        queue = deque([node])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            # Get incoming neighbors
            incoming_rels = self.get_incoming(current)
            for rel in incoming_rels:
                neighbor = rel["source"]
                if neighbor != node:  # Don't include the start node
                    ancestors.add(neighbor)
                if neighbor not in visited:
                    queue.append(neighbor)

        return ancestors

    def topological_sort(self) -> List[str]:
        """Perform topological sort on the graph.

        For DEPENDS_ON relationships, this returns nodes in dependency order:
        dependencies before dependents. If A depends on B, then B comes before A.

        Returns:
            List of nodes in topologically sorted order

        Raises:
            ValueError: If the graph contains cycles
        """
        # Check for cycles first
        cycles = self.find_cycles()
        if cycles:
            raise ValueError(f"Graph contains cycles: {cycles}")

        # Kahn's algorithm for topological sort
        # For DEPENDS_ON: if A depends on B, edge is A→B, so we want B before A
        # This means we start with nodes that have no outgoing edges (no dependencies)
        out_degree = defaultdict(int)
        nodes = self.get_all_nodes()

        # Calculate out-degrees (how many things this node depends on)
        for node in nodes:
            out_degree[node] = len(self.get_outgoing(node))

        # Start with nodes that have no outgoing edges (no dependencies)
        queue = deque([node for node in nodes if out_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Process incoming edges (nodes that depend on this node)
            incoming_rels = self.get_incoming(node)
            for rel in incoming_rels:
                source = rel["source"]
                out_degree[source] -= 1
                if out_degree[source] == 0:
                    queue.append(source)

        return result

    def to_mermaid(self) -> str:
        """Export the graph as a Mermaid diagram.

        Returns:
            Mermaid diagram syntax as a string
        """
        lines = ["graph TD"]

        # Define arrow styles for different relationship types
        arrow_styles = {
            RelationshipType.DEPENDS_ON: "-->",
            RelationshipType.SIMILAR_TO: "-.->",
            RelationshipType.REPLACES: "==>",
            RelationshipType.USES: "-.->",
            RelationshipType.INCLUDES: "==>",
            RelationshipType.REFERENCES: "-->",
        }

        # Add edges with labels
        for (source, rel_type), targets in self._outgoing.items():
            arrow = arrow_styles.get(rel_type, "-->")
            for target in targets:
                # Sanitize node names for Mermaid
                safe_source = source.replace(".", "_").replace("-", "_")
                safe_target = target.replace(".", "_").replace("-", "_")
                # Handle both enum and string relationship types
                rel_label = (
                    rel_type.value if isinstance(rel_type, RelationshipType) else str(rel_type)
                )
                lines.append(f"    {safe_source} {arrow}|{rel_label}| {safe_target}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Export the graph as a dictionary.

        Returns:
            Dictionary representation with nodes and edges
        """
        edges: List[Dict[str, Any]] = []
        for (source, rel_type), targets in self._outgoing.items():
            for target in targets:
                edge: Dict[str, Any] = {
                    "source": source,
                    "target": target,
                    "type": rel_type.value,
                }
                # Add metadata if present
                meta_key = (source, target, rel_type)
                if meta_key in self._metadata:
                    edge["metadata"] = self._metadata[meta_key]
                edges.append(edge)

        return {"nodes": list(self.get_all_nodes()), "edges": edges}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LinkGraph:
        """Import a graph from a dictionary.

        Args:
            data: Dictionary with 'nodes' and 'edges' keys

        Returns:
            New LinkGraph instance
        """
        graph = cls()

        for edge in data.get("edges", []):
            source = edge["source"]
            target = edge["target"]
            # Handle both lowercase and uppercase enum names
            type_str = edge["type"]
            try:
                rel_type = RelationshipType(type_str.lower())
            except ValueError:
                # Try uppercase name as enum attribute
                rel_type = RelationshipType[type_str]
            metadata = edge.get("metadata")

            graph.add_relationship(source, target, rel_type, metadata)

        return graph
