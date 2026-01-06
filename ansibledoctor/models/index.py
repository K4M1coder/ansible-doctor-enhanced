"""Index and navigation models for component discovery."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class IndexItem(BaseModel):
    """Single component entry in an index with metadata and navigation.

    Represents a discoverable component (collection, role, plugin, etc.)
    with its metadata, documentation links, and hierarchical relationships.
    """

    name: str = Field(description="Component name (role name, collection name)")
    type: Literal["collection", "role", "plugin", "module", "playbook"] = Field(
        description="Component type"
    )
    description: str | None = Field(default=None, description="Component description (may be None)")
    path: Path = Field(description="Relative path to component from project root")
    doc_link: str | None = Field(
        default=None, description="Relative link to generated documentation"
    )
    tags: list[str] = Field(
        default_factory=list, description="Tags for filtering and categorization"
    )
    namespace: str | None = Field(
        default=None, description="Collection namespace (for collections and roles)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields")
    children: list["IndexItem"] = Field(
        default_factory=list, description="Child components (for hierarchical items)"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Names of components this depends on"
    )
    used_by: list[str] = Field(
        default_factory=list, description="Names of components that use this"
    )

    @property
    def depth(self) -> int:
        """Calculate depth in hierarchy (root=0, direct children=1, etc.)."""
        if not self.children:
            return 0
        return 1 + max(child.depth for child in self.children)

    @property
    def total_descendants(self) -> int:
        """Count all descendants recursively."""
        if not self.children:
            return 0
        return len(self.children) + sum(child.total_descendants for child in self.children)

    def find_child(self, name: str) -> "IndexItem | None":
        """Find direct child by name.

        Args:
            name: Name of child component to find

        Returns:
            Child IndexItem if found, None otherwise
        """
        for child in self.children:
            if child.name == name:
                return child
        return None

    def find_descendant(self, name: str) -> "IndexItem | None":
        """Find descendant at any level by name (depth-first search).

        Args:
            name: Name of descendant component to find

        Returns:
            Descendant IndexItem if found, None otherwise
        """
        if self.name == name:
            return self
        for child in self.children:
            result = child.find_descendant(name)
            if result:
                return result
        return None


class IndexPage(BaseModel):
    """Standalone index page listing components of a specific type.

    Represents a dedicated index page (e.g., roles/index.md) with
    pagination, filtering, and multiple visualization styles.
    """

    title: str = Field(description="Page title (e.g., 'Role Index', 'Collection Index')")
    component_type: str = Field(description="Type of components indexed (roles, collections, etc.)")
    items: list[IndexItem] = Field(description="Components to display on this page")
    format: Literal["list", "table", "tree", "nested-table", "diagram"] = Field(
        default="list", description="Visualization style"
    )
    total_count: int = Field(description="Total number of components (across all pages)")
    filtered_count: int | None = Field(
        default=None, description="Number of components after filtering (if filter applied)"
    )
    page_number: int = Field(default=1, ge=1, description="Current page number (1-indexed)")
    total_pages: int = Field(default=1, ge=1, description="Total number of pages")
    filters_applied: list[str] = Field(
        default_factory=list, description="Human-readable filter descriptions"
    )

    @property
    def has_pagination(self) -> bool:
        """Check if pagination is needed."""
        return self.total_pages > 1

    @property
    def has_previous(self) -> bool:
        """Check if previous page exists."""
        return self.page_number > 1

    @property
    def has_next(self) -> bool:
        """Check if next page exists."""
        return self.page_number < self.total_pages

    @property
    def previous_page_link(self) -> str | None:
        """Generate link to previous page."""
        if not self.has_previous:
            return None
        if self.page_number == 2:
            return "./index.md"
        prev_num = self.page_number - 1 if self.page_number else 1
        return f"./index-{prev_num}.md"

    @property
    def next_page_link(self) -> str | None:
        """Generate link to next page."""
        if not self.has_next:
            return None
        next_num = self.page_number + 1 if self.page_number else 2
        return f"./index-{next_num}.md"

    def render(self, template_engine: Any) -> str:
        """Render index page using appropriate template.

        Args:
            template_engine: Template engine with render() method

        Returns:
            Rendered index page content
        """
        template_name = f"index/{self.format}.j2"
        return template_engine.render(template_name, page=self)  # type: ignore[no-any-return]


class SectionIndex(BaseModel):
    """Embedded index section for use within documentation templates.

    Represents an inline index (via {{ index('roles') }} marker) that
    can be embedded within a parent document like README.md.
    """

    component_type: str = Field(description="Type of components to index (roles, plugins, etc.)")
    items: list[IndexItem] = Field(description="Components to display in this section")
    format: Literal["list", "table", "tree"] = Field(
        default="list", description="Visualization style (limited set for inline display)"
    )
    limit: int | None = Field(
        default=None, ge=1, description="Maximum items to show (None = show all)"
    )
    group_by: str | None = Field(
        default=None, description="Field to group by (e.g., 'type' for plugins)"
    )
    filter_expression: str | None = Field(
        default=None, description="Filter expression (e.g., 'tag:database')"
    )

    @property
    def is_limited(self) -> bool:
        """Check if item limit is active."""
        return self.limit is not None and len(self.items) > self.limit

    @property
    def visible_items(self) -> list[IndexItem]:
        """Get items to display (respecting limit)."""
        if self.limit is None:
            return self.items
        return self.items[: self.limit]

    @property
    def hidden_count(self) -> int:
        """Count of items hidden by limit."""
        if not self.is_limited or self.limit is None:
            return 0
        return len(self.items) - self.limit

    def render_inline(self, template_engine: Any | None = None) -> str:
        """Render section index for inline embedding.

        Args:
            template_engine: Template engine with render() method (optional)

        Returns:
            Rendered section content (without header/footer)
        """
        # If template engine provided, use it
        if template_engine is not None:
            template_name = f"index/section_{self.format}.j2"
            return template_engine.render(template_name, section=self)  # type: ignore[no-any-return]

        # Otherwise, generate simple inline representation
        return self._render_simple_inline()

    def _render_simple_inline(self) -> str:
        """Generate simple inline representation without template engine."""
        # Apply filter if specified
        items = self.items
        if self.filter_expression:
            try:
                filter_obj = IndexFilter.parse(self.filter_expression)
                items = [item for item in items if filter_obj.matches(item)]
            except ValueError:
                pass  # Invalid filter, use all items

        # Apply limit
        visible = items[: self.limit] if self.limit else items
        hidden = len(items) - len(visible) if self.limit and len(items) > self.limit else 0

        # Group items if specified
        grouped: dict[str, list[IndexItem]] = {}
        if self.group_by:
            for item in visible:
                # Extract group key from item
                group_key = self._extract_group_key(item, self.group_by)
                if group_key not in grouped:
                    grouped[group_key] = []
                grouped[group_key].append(item)
        else:
            grouped["_default"] = visible

        # Render based on format
        lines: list[str] = []

        for group_name, group_items in grouped.items():
            # Add group header if grouped
            if self.group_by and group_name != "_default":
                lines.append(f"\n### {group_name}\n")

            # Render items based on format
            if self.format == "table":
                lines.append("| Name | Description |")
                lines.append("|------|-------------|")
                for item in group_items:
                    desc = item.description or ""
                    lines.append(f"| {item.name} | {desc} |")
            elif self.format == "tree":
                for item in group_items:
                    lines.append(f"  - {item.name}")
            else:  # list format
                for item in group_items:
                    desc = f" - {item.description}" if item.description else ""
                    lines.append(f"- [{item.name}]({item.doc_link}){desc}")

        # Add "and X more..." if limited
        if hidden > 0:
            lines.append(f"\nand {hidden} more...")

        return "\n".join(lines)

    def _extract_group_key(self, item: IndexItem, group_by: str) -> str:
        """Extract grouping key from item.

        Args:
            item: IndexItem to extract key from
            group_by: Field path (e.g., 'metadata.plugin_type')

        Returns:
            String key for grouping
        """
        # Handle nested paths like "metadata.plugin_type"
        parts = group_by.split(".")
        value: Any = item

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return "Other"

        return str(value) if value else "Other"


class IndexFilter(BaseModel):
    """Filter criteria for index queries.

    Represents a single filter condition (e.g., tag:database, namespace:my_ns)
    that can be applied to index items.
    """

    field: str = Field(description="Field to filter on (tag, namespace, type, etc.)")
    operator: Literal["equals", "contains", "startswith", "in"] = Field(
        default="equals", description="Comparison operator"
    )
    value: str | list[str] = Field(description="Value(s) to match against")

    def matches(self, item: IndexItem) -> bool:
        """Check if an item matches this filter.

        Args:
            item: IndexItem to test against filter

        Returns:
            True if item matches filter criteria, False otherwise
        """
        # Get field value from item
        if self.field == "tag":
            item_values = item.tags
        elif self.field == "namespace":
            item_values = [item.namespace] if item.namespace else []
        elif self.field == "type":
            item_values = [item.type]
        elif self.field in item.metadata:
            item_value = item.metadata[self.field]
            item_values = [item_value] if not isinstance(item_value, list) else item_value
        else:
            return False

        # Apply operator
        if self.operator == "equals":
            return self.value in item_values
        elif self.operator == "contains":
            return any(str(self.value) in str(v) for v in item_values)
        elif self.operator == "startswith":
            return any(str(v).startswith(str(self.value)) for v in item_values)
        elif self.operator == "in":
            filter_values = self.value if isinstance(self.value, list) else [self.value]
            return any(v in filter_values for v in item_values)

        return False

    @classmethod
    def parse(cls, filter_string: str) -> "IndexFilter":
        """Parse filter string into IndexFilter.

        Examples:
            "tag:database" -> IndexFilter(field="tag", value="database")
            "namespace:my_ns" -> IndexFilter(field="namespace", value="my_ns")
            "type:role" -> IndexFilter(field="type", value="role")

        Args:
            filter_string: Filter string in format "field:value"

        Returns:
            Parsed IndexFilter

        Raises:
            ValueError: If filter string format is invalid
        """
        if ":" not in filter_string:
            raise ValueError(f"Invalid filter format: {filter_string}. Expected 'field:value'")

        field, value = filter_string.split(":", 1)
        return cls(field=field.strip(), value=value.strip())
