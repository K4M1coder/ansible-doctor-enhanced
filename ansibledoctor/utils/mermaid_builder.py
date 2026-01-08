"""Mermaid diagram builder for visualizing project structure."""

from ansibledoctor.models.index import IndexItem


class MermaidBuilder:
    """Generate Mermaid diagrams for index visualization.

    Supports flowcharts and mindmaps showing project structure,
    dependencies, and relationships between components.
    """

    def __init__(self, use_clickable_nodes: bool = True):
        """Initialize Mermaid builder.

        Args:
            use_clickable_nodes: Include click directives for navigation
        """
        self.use_clickable_nodes = use_clickable_nodes

    def build_flowchart(self, items: list[IndexItem], direction: str = "TD") -> str:
        """Build Mermaid flowchart showing component relationships.

        Args:
            items: Components to visualize
            direction: Flow direction (TD=top-down, LR=left-right)

        Returns:
            Mermaid flowchart syntax

        Example:
            >>> builder = MermaidBuilder()
            >>> mermaid = builder.build_flowchart(items, direction="TD")
            >>> print(mermaid)
            graph TD
                collection1[my_collection]
                role1[webserver]
                collection1 --> role1
                click collection1 "./collections/my_collection.md"
        """
        lines = [f"graph {direction}"]

        # Collect all items (including children recursively)
        all_items = []
        self._collect_all_items(items, all_items)

        # Define nodes
        for item in all_items:
            node_id = self._sanitize_id(item.name)
            node_label = item.name
            node_shape = self._get_node_shape(item.type)

            lines.append(f"    {node_id}{node_shape[0]}{node_label}{node_shape[1]}")

            # Add click directive if enabled
            if self.use_clickable_nodes and item.doc_link:
                lines.append(f'    click {node_id} "{item.doc_link}"')

        # Add relationships (parent-child and dependencies)
        for item in all_items:
            node_id = self._sanitize_id(item.name)

            # Children relationships
            for child in item.children:
                child_id = self._sanitize_id(child.name)
                lines.append(f"    {node_id} --> {child_id}")

            # Dependency relationships
            if item.dependencies:
                for dep in item.dependencies:
                    dep_id = self._sanitize_id(dep)
                    lines.append(f"    {node_id} -.depends.-> {dep_id}")

        return "\n".join(lines)

    def _collect_all_items(self, items: list[IndexItem], collected: list[IndexItem]) -> None:
        """Recursively collect all items including children.

        Args:
            items: Items to collect
            collected: Output list
        """
        for item in items:
            if item not in collected:
                collected.append(item)
                self._collect_all_items(item.children, collected)

    def build_mindmap(self, items: list[IndexItem]) -> str:
        """Build Mermaid mindmap showing hierarchical structure.

        Args:
            items: Components to visualize (hierarchical)

        Returns:
            Mermaid mindmap syntax

        Example:
            >>> builder = MermaidBuilder()
            >>> mermaid = builder.build_mindmap(items)
            >>> print(mermaid)
            mindmap
              root((Project))
                my_collection
                  webserver
                  database
        """
        lines = ["mindmap", "  root((Project))"]

        for item in items:
            self._add_mindmap_node(item, lines, indent=2)

        return "\n".join(lines)

    def _add_mindmap_node(self, item: IndexItem, lines: list[str], indent: int) -> None:
        """Recursively add mindmap nodes.

        Args:
            item: Item to add
            lines: Output lines list
            indent: Current indentation level
        """
        indent_str = " " * indent
        lines.append(f"{indent_str}{item.name}")

        for child in item.children:
            self._add_mindmap_node(child, lines, indent + 2)

    def _sanitize_id(self, name: str) -> str:
        """Sanitize name for use as Mermaid node ID.

        Args:
            name: Original name

        Returns:
            Sanitized ID (alphanumeric + underscore)
        """
        # Replace non-alphanumeric with underscore
        return "".join(c if c.isalnum() else "_" for c in name)

    def _get_node_shape(self, item_type: str) -> tuple[str, str]:
        """Get Mermaid node shape for component type.

        Args:
            item_type: Component type

        Returns:
            Tuple of (opening, closing) shape syntax
        """
        shapes = {
            "collection": ("[", "]"),  # Rectangle
            "role": ("(", ")"),  # Rounded rectangle
            "plugin": ("[[", "]]"),  # Subroutine
            "module": ("[[", "]]"),  # Subroutine
            "playbook": ("{", "}"),  # Rhombus
        }
        return shapes.get(item_type, ("[", "]"))
