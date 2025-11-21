"""
Dependency graph analysis for Ansible collection roles.

Provides functionality to:
- Build dependency graphs from role metadata
- Detect circular dependencies
- Perform topological sorting
- Export graphs in multiple formats (Mermaid, ASCII tree, JSON)
"""

import logging
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when circular dependencies are detected in the role graph."""

    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        cycle_str = " → ".join(cycle)
        super().__init__(f"Circular dependency detected: {cycle_str}")


class DependencyNode:
    """Represents a role node in the dependency graph."""

    def __init__(self, name: str):
        self.name = name
        self.dependencies: List[str] = []
        self.dependents: List[str] = []

    def __repr__(self) -> str:
        return f"DependencyNode(name={self.name}, dependencies={self.dependencies})"


class DependencyGraph:
    """
    Dependency graph for collection roles.

    Tracks role dependencies and provides analysis capabilities including
    circular dependency detection and topological sorting.

    Example:
        >>> graph = DependencyGraph()
        >>> graph.add_role("database", dependencies=[])
        >>> graph.add_role("webserver", dependencies=["database"])
        >>> sorted_roles = graph.topological_sort()
        >>> print(sorted_roles)
        ['database', 'webserver']
    """

    def __init__(self):
        """Initialize an empty dependency graph."""
        self._nodes: Dict[str, DependencyNode] = {}
        self._edges: List[tuple[str, str]] = []
        self._explicit_roles: Set[str] = set()  # Track explicitly added roles

    def add_role(self, name: str, dependencies: Optional[List[str]] = None) -> None:
        """
        Add a role to the dependency graph.

        Args:
            name: Role name
            dependencies: List of role names this role depends on
        """
        if name not in self._nodes:
            self._nodes[name] = DependencyNode(name)

        # Mark this role as explicitly added
        self._explicit_roles.add(name)

        if dependencies:
            self._nodes[name].dependencies = dependencies
            for dep in dependencies:
                self._edges.append((name, dep))
                # Create node for dependency if it doesn't exist
                if dep not in self._nodes:
                    self._nodes[dep] = DependencyNode(dep)
                self._nodes[dep].dependents.append(name)

        logger.debug(f"Added role '{name}' with {len(dependencies or [])} dependencies")

    def node_count(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self._nodes)

    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        return len(self._edges)

    def __contains__(self, role_name: str) -> bool:
        """Check if a role exists in the graph."""
        return role_name in self._nodes

    def get_all_nodes(self) -> List[str]:
        """Return list of all role names in the graph."""
        return list(self._nodes.keys())

    def get_dependencies(self, role_name: str) -> List[str]:
        """
        Get direct dependencies of a role.

        Args:
            role_name: Name of the role

        Returns:
            List of role names that this role depends on
        """
        if role_name not in self._nodes:
            return []
        return self._nodes[role_name].dependencies

    def get_missing_dependencies(self) -> Dict[str, List[str]]:
        """
        Find dependencies that are declared but don't exist in the graph.

        A dependency is considered missing if it wasn't explicitly added
        via add_role() - meaning it only exists as a reference.

        Returns:
            Dictionary mapping role names to lists of missing dependencies
        """
        missing: Dict[str, List[str]] = {}

        for role_name, node in self._nodes.items():
            missing_deps = []
            for dep in node.dependencies:
                # Dependency is missing if it wasn't explicitly added
                if dep not in self._explicit_roles:
                    missing_deps.append(dep)

            if missing_deps:
                missing[role_name] = missing_deps

        return missing

    def has_circular_dependencies(self) -> bool:
        """
        Check if the graph contains any circular dependencies.

        Returns:
            True if circular dependencies exist, False otherwise
        """
        return len(self.find_circular_dependencies()) > 0

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find all circular dependency cycles in the graph.

        Uses depth-first search to detect cycles.

        Returns:
            List of cycles, where each cycle is a list of role names
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self._nodes.get(node, DependencyNode(node)).dependencies:
                if dep not in visited:
                    dfs(dep)
                elif dep in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    # Remove duplicate at end for cleaner display
                    cycles.append(cycle[:-1])

            path.pop()
            rec_stack.remove(node)

        for node_name in self._nodes:
            if node_name not in visited:
                dfs(node_name)

        return cycles

    def topological_sort(self) -> List[str]:
        """
        Perform topological sort on the dependency graph.

        Returns roles in dependency order (dependencies before dependents).

        Returns:
            List of role names in topological order

        Raises:
            CircularDependencyError: If circular dependencies exist
        """
        if self.has_circular_dependencies():
            cycles = self.find_circular_dependencies()
            raise CircularDependencyError(cycles[0])

        # Kahn's algorithm - calculate in-degree based on dependencies
        in_degree: Dict[str, int] = {name: len(node.dependencies) for name, node in self._nodes.items()}

        # Start with nodes that have no dependencies
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result: List[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # For each node that depends on current node
            for dependent in self._nodes[node].dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result

    def to_mermaid(self) -> str:
        """
        Export dependency graph to Mermaid diagram format.

        Returns:
            Mermaid diagram as string
        """
        lines = ["graph TD"]

        if not self._nodes:
            lines.append("    empty[No roles]")
            return "\n".join(lines)

        # Add all nodes
        for name in self._nodes:
            safe_name = name.replace(".", "_").replace("-", "_")
            lines.append(f"    {safe_name}[{name}]")

        # Add edges
        for src, dst in self._edges:
            safe_src = src.replace(".", "_").replace("-", "_")
            safe_dst = dst.replace(".", "_").replace("-", "_")
            lines.append(f"    {safe_src} --> {safe_dst}")

        # Highlight circular dependencies
        cycles = self.find_circular_dependencies()
        if cycles:
            for cycle in cycles:
                for node in cycle:
                    safe_node = node.replace(".", "_").replace("-", "_")
                    lines.append(f"    style {safe_node} fill:#f99,stroke:#f00,stroke-width:2px")

        return "\n".join(lines)

    def to_ascii_tree(self) -> str:
        """
        Export dependency graph to ASCII tree format.

        Shows hierarchy with box-drawing characters.

        Returns:
            ASCII tree as string
        """
        if not self._nodes:
            return "(empty graph)"

        lines: List[str] = []

        # Find root nodes (no dependencies)
        roots = [name for name, node in self._nodes.items() if not node.dependencies]

        if not roots:
            # All nodes have dependencies - might be circular
            roots = list(self._nodes.keys())[:1]  # Just start with first node

        visited: Set[str] = set()

        def build_tree(node_name: str, prefix: str = "", is_last: bool = True) -> None:
            if node_name in visited:
                lines.append(f"{prefix}{'└── ' if is_last else '├── '}{node_name} (circular)")
                return

            visited.add(node_name)
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{node_name}")

            dependents = self._nodes[node_name].dependents
            for i, dep in enumerate(dependents):
                is_last_dep = i == len(dependents) - 1
                extension = "    " if is_last else "│   "
                build_tree(dep, prefix + extension, is_last_dep)

        for i, root in enumerate(roots):
            build_tree(root, "", i == len(roots) - 1)

        return "\n".join(lines)

    def to_json(self) -> Dict[str, Any]:
        """
        Export dependency graph to JSON-serializable dictionary.

        Returns:
            Dictionary with nodes, edges, and circular dependency information
        """
        return {
            "nodes": [
                {
                    "name": name,
                    "dependencies": node.dependencies,
                    "dependents": node.dependents
                }
                for name, node in self._nodes.items()
            ],
            "edges": [
                {"from": src, "to": dst}
                for src, dst in self._edges
            ],
            "circular_dependencies": self.find_circular_dependencies(),
            "has_cycles": self.has_circular_dependencies()
        }

    @classmethod
    def from_collection_path(cls, collection_path: Path) -> "DependencyGraph":
        """
        Build dependency graph from a collection directory.

        Scans roles/ directory and parses meta/main.yml files.

        Args:
            collection_path: Path to collection root directory

        Returns:
            DependencyGraph instance with parsed dependencies
        """
        graph = cls()
        roles_dir = collection_path / "roles"

        if not roles_dir.exists():
            logger.warning(f"No roles/ directory found in {collection_path}")
            return graph

        # Discover all roles
        for role_dir in roles_dir.iterdir():
            if not role_dir.is_dir():
                continue

            role_name = role_dir.name
            meta_file = role_dir / "meta" / "main.yml"

            dependencies: List[str] = []

            if meta_file.exists():
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        meta_data = yaml.safe_load(f) or {}

                    # Extract dependencies
                    deps = meta_data.get("dependencies", [])
                    if deps:
                        for dep in deps:
                            if isinstance(dep, str):
                                dependencies.append(dep)
                            elif isinstance(dep, dict) and "role" in dep:
                                dependencies.append(dep["role"])

                    logger.debug(f"Parsed role '{role_name}' with dependencies: {dependencies}")

                except Exception as e:
                    logger.warning(f"Failed to parse meta file for role '{role_name}': {e}")

            graph.add_role(role_name, dependencies)

        return graph
