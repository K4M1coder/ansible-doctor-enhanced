"""Tree visualization utilities for index generation.

Provides ASCII and Unicode tree rendering for hierarchical index structures.
"""

from typing import List

from ansibledoctor.models.index import IndexItem


class TreeVisualizer:
    """Visualize hierarchical index structures as ASCII/Unicode trees.

    Renders tree structures using box-drawing characters for hierarchical
    display of collections, roles, plugins, and playbooks.

    Attributes:
        use_unicode: Use Unicode box-drawing characters (default: True)
        max_depth: Maximum depth to render (None = unlimited)
        show_description: Include item descriptions in output
        indent_size: Number of spaces per indentation level

    Example:
        >>> visualizer = TreeVisualizer()
        >>> output = visualizer.render_tree(hierarchy)
        >>> print(output)
        my_collection
        ├── webserver (Configure web servers)
        ├── database (PostgreSQL setup)
        └── monitoring (Prometheus metrics)
    """

    def __init__(
        self,
        use_unicode: bool = True,
        max_depth: int | None = None,
        show_description: bool = False,
        indent_size: int = 4,
    ):
        """Initialize tree visualizer.

        Args:
            use_unicode: Use Unicode box-drawing characters instead of ASCII
            max_depth: Maximum depth to render (None for unlimited)
            show_description: Include item descriptions
            indent_size: Spaces per indentation level
        """
        self.use_unicode = use_unicode
        self.max_depth = max_depth
        self.show_description = show_description
        self.indent_size = indent_size

        # Define tree characters based on Unicode preference
        if use_unicode:
            self.branch = "├── "
            self.last_branch = "└── "
            self.vertical = "│   "
            self.space = "    "
        else:
            self.branch = "├── "
            self.last_branch = "└── "
            self.vertical = "│   "
            self.space = "    "

    def render_tree(self, items: List[IndexItem]) -> str:
        """Render hierarchical tree structure.

        Args:
            items: List of root IndexItem objects with children

        Returns:
            Formatted tree string with box-drawing characters

        Example:
            >>> hierarchy = [collection_item, standalone_role]
            >>> visualizer.render_tree(hierarchy)
            'my_collection\\n├── role1\\n└── role2\\nstandalone_role\\n'
        """
        if not items:
            return ""

        lines: list[str] = []
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            self._render_node(item, "", is_last, lines, current_depth=0)

        return "\n".join(lines)

    def _render_node(
        self,
        item: IndexItem,
        prefix: str,
        is_last: bool,
        lines: List[str],
        current_depth: int,
    ) -> None:
        """Recursively render a node and its children.

        Args:
            item: IndexItem to render
            prefix: Current line prefix (tree structure characters)
            is_last: Whether this is the last sibling
            lines: Output lines list (mutated)
            current_depth: Current depth in tree (0 = root)
        """
        # Check depth limit - stop if current depth exceeds max_depth
        if self.max_depth is not None and current_depth > self.max_depth:
            return

        # Build node line
        if current_depth == 0:
            # Root node - no prefix
            node_str = item.name
        else:
            # Child node - add tree characters
            connector = self.last_branch if is_last else self.branch
            node_str = f"{prefix}{connector}{item.name}"

        # Add description if enabled
        if self.show_description and item.description:
            node_str += f" ({item.description})"

        lines.append(node_str)

        # Render children
        if item.children:
            # Update prefix for children
            if current_depth == 0:
                # Root level - start with empty prefix
                child_prefix = ""
            else:
                # Add vertical bar or space depending on whether parent is last
                extension = self.space if is_last else self.vertical
                child_prefix = prefix + extension

            # Render each child
            for i, child in enumerate(item.children):
                child_is_last = i == len(item.children) - 1
                self._render_node(
                    child,
                    child_prefix,
                    child_is_last,
                    lines,
                    current_depth + 1,
                )

    def render_compact(self, items: List[IndexItem]) -> str:
        """Render compact tree without vertical connectors.

        Uses simpler indentation without vertical lines for cleaner output.

        Args:
            items: List of root IndexItem objects

        Returns:
            Compact tree string
        """
        if not items:
            return ""

        lines: list[str] = []
        for item in items:
            self._render_compact_node(item, 0, lines)

        return "\n".join(lines)

    def _render_compact_node(self, item: IndexItem, depth: int, lines: List[str]) -> None:
        """Render node in compact format.

        Args:
            item: IndexItem to render
            depth: Current depth (for indentation)
            lines: Output lines list (mutated)
        """
        # Check depth limit
        if self.max_depth is not None and depth > self.max_depth:
            return

        # Build indented line
        indent = "  " * depth
        node_str = f"{indent}{item.name}"

        if self.show_description and item.description:
            node_str += f" - {item.description}"

        lines.append(node_str)

        # Render children
        for child in item.children:
            self._render_compact_node(child, depth + 1, lines)

    def get_stats(self, items: List[IndexItem]) -> dict:
        """Calculate tree statistics.

        Args:
            items: List of root IndexItem objects

        Returns:
            Dictionary with statistics:
                - total_nodes: Total number of nodes
                - max_depth: Maximum depth in tree
                - leaf_nodes: Number of leaf nodes (no children)
                - root_nodes: Number of root nodes
        """
        total_nodes = 0
        max_depth = 0
        leaf_nodes = 0

        def traverse(item: IndexItem, depth: int) -> None:
            nonlocal total_nodes, max_depth, leaf_nodes

            total_nodes += 1
            max_depth = max(max_depth, depth)

            if not item.children:
                leaf_nodes += 1

            for child in item.children:
                traverse(child, depth + 1)

        for item in items:
            traverse(item, 0)

        return {
            "total_nodes": total_nodes,
            "max_depth": max_depth,
            "leaf_nodes": leaf_nodes,
            "root_nodes": len(items),
        }
