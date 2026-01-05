"""Index generator for creating component indexes and navigation structures."""

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from ansibledoctor.models.index import IndexFilter, IndexItem, IndexPage, SectionIndex

if TYPE_CHECKING:
    from ansibledoctor.generator.engine import TemplateEngine


class IndexGenerator(Protocol):
    """Protocol for index generation implementations.

    This protocol defines the interface for generating various types of
    indexes (role indexes, collection indexes, hierarchical views, etc.).
    """

    def generate_index_page(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        filters: list[IndexFilter] | None = None,
        page_size: int = 50,
    ) -> list[IndexPage]:
        """Generate standalone index page(s) for a component type.

        Args:
            component_type: Type of components (roles, collections, etc.)
            items: All available items of this type
            format: Visualization style (list, table, tree, etc.)
            filters: Optional filters to apply
            page_size: Items per page for pagination

        Returns:
            List of IndexPage objects (multiple if pagination needed)
        """
        ...

    def generate_section_index(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        limit: int | None = None,
        group_by: str | None = None,
        filter_expression: str | None = None,
    ) -> SectionIndex:
        """Generate embedded section index for template marker.

        Args:
            component_type: Type of components to index
            items: Available items
            format: Visualization style
            limit: Maximum items to show
            group_by: Field to group items by
            filter_expression: Filter string (e.g., 'tag:database')

        Returns:
            SectionIndex for inline rendering
        """
        ...

    def build_hierarchy(
        self,
        items: list[IndexItem],
        max_depth: int | None = None,
    ) -> list[IndexItem]:
        """Build hierarchical tree structure from flat item list.

        Args:
            items: Flat list of items to organize
            max_depth: Maximum depth to build (None = unlimited)

        Returns:
            Root items with children populated
        """
        ...

    def extract_component_metadata(
        self,
        component: object,
    ) -> IndexItem:
        """Extract metadata from parsed component to create IndexItem.

        Args:
            component: Parsed component (AnsibleRole, AnsibleCollection, etc.)

        Returns:
            IndexItem with extracted metadata
        """
        ...

    def resolve_dependency_links(
        self,
        items: list[IndexItem],
    ) -> None:
        """Resolve dependency names to documentation links.

        Mutates items in-place to add doc_link values for dependencies.

        Args:
            items: Items to resolve links for
        """
        ...


class DefaultIndexGenerator:
    """Default implementation of IndexGenerator protocol."""

    def __init__(
        self,
        output_dir: Path,
        language_code: str = "en",
        template_engine: "TemplateEngine | None" = None,
        output_format: str = "markdown",
    ):
        """Initialize index generator.

        Args:
            output_dir: Output directory for generated indexes
            language_code: Language code for i18n support
            template_engine: Optional TemplateEngine for rendering
            output_format: Output format (markdown, html, rst)
        """
        self.output_dir = output_dir
        self.language_code = language_code
        self._engine = template_engine
        self.output_format = output_format

    def generate_index_page(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        filters: list[IndexFilter] | None = None,
        page_size: int = 50,
    ) -> list[IndexPage]:
        """Generate standalone index page(s) for a component type."""
        # Apply filters if provided
        filtered_items = items
        filters_applied = []

        if filters:
            for filter_obj in filters:
                filtered_items = [item for item in filtered_items if filter_obj.matches(item)]
                filters_applied.append(f"{filter_obj.field}:{filter_obj.value}")

        # Calculate pagination
        total_count = len(items)
        filtered_count = len(filtered_items) if filters else None
        total_pages = (len(filtered_items) + page_size - 1) // page_size if filtered_items else 1

        # Create pages
        pages = []
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * page_size
            end_idx = min(start_idx + page_size, len(filtered_items))
            page_items = filtered_items[start_idx:end_idx]

            page = IndexPage(
                title=f"{component_type.capitalize()} Index",
                component_type=component_type,
                items=page_items,
                format=format,  # type: ignore[arg-type]
                total_count=total_count,
                filtered_count=filtered_count,
                page_number=page_num,
                total_pages=total_pages,
                filters_applied=filters_applied,
            )
            pages.append(page)

        return pages

    def render_index_page(self, page: IndexPage) -> str:
        """Render an IndexPage using the configured template engine.

        Args:
            page: IndexPage to render

        Returns:
            Rendered template content

        Raises:
            ValueError: If template engine not configured or template not found
        """
        if self._engine is None:
            raise ValueError("Template engine not configured. Pass template_engine to __init__.")

        # Determine template path based on format and output_format
        template_name = f"{self.output_format}/index/{page.format}.j2"

        try:
            template = self._engine.get_template(template_name)
        except Exception as e:
            raise ValueError(f"Template not found: {template_name}") from e

        # Render template with page data
        return template.render(**page.model_dump())

    def generate_section_index(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        limit: int | None = None,
        group_by: str | None = None,
        filter_expression: str | None = None,
    ) -> SectionIndex:
        """Generate embedded section index for template marker."""
        # Apply filter if provided
        filtered_items = items
        if filter_expression:
            try:
                filter_obj = IndexFilter.parse(filter_expression)
                filtered_items = [item for item in items if filter_obj.matches(item)]
            except ValueError:
                # Invalid filter, use all items
                pass

        return SectionIndex(
            component_type=component_type,
            items=filtered_items,
            format=format,  # type: ignore[arg-type]
            limit=limit,
            group_by=group_by,
            filter_expression=filter_expression,
        )

    def build_hierarchy(
        self,
        items: list[IndexItem],
        max_depth: int | None = None,
    ) -> list[IndexItem]:
        """Build hierarchical tree structure from flat item list."""
        # Simple implementation: group by type hierarchy
        # collections -> roles -> plugins

        collections = [item for item in items if item.type == "collection"]
        roles = [item for item in items if item.type == "role"]
        plugins = [item for item in items if item.type in ("plugin", "module")]
        playbooks = [item for item in items if item.type == "playbook"]

        # Build tree by matching roles to their parent collection
        # A role belongs to a collection if the role's path starts with the collection's path
        for collection in collections:
            # Find roles belonging to this specific collection
            collection_roles = [
                role for role in roles if str(role.path).startswith(str(collection.path))
            ]
            collection.children.extend(collection_roles)

            # Find plugins belonging to this specific collection
            collection_plugins = [
                plugin for plugin in plugins if str(plugin.path).startswith(str(collection.path))
            ]
            collection.children.extend(collection_plugins)

        # Return root items (collections + standalone items)
        root_items = collections.copy()

        # Add standalone roles (not under any collection)
        standalone_roles = [
            role
            for role in roles
            if not any(str(role.path).startswith(str(c.path)) for c in collections)
        ]
        root_items.extend(standalone_roles)

        # Add playbooks (typically at root level)
        root_items.extend(playbooks)

        return root_items

    def extract_component_metadata(
        self,
        component: object,
    ) -> IndexItem:
        """Extract metadata from parsed component to create IndexItem.

        Supports AnsibleRole, AnsibleCollection, Plugin, and PlaybookInfo.

        Args:
            component: Parsed component (Role, Collection, Plugin, Playbook)

        Returns:
            IndexItem representing the component
        """
        from ansibledoctor.models.collection import AnsibleCollection, PlaybookInfo
        from ansibledoctor.models.plugin import Plugin
        from ansibledoctor.models.role import AnsibleRole

        if isinstance(component, AnsibleRole):
            # Extract role metadata
            description = ""
            if hasattr(component.metadata, "description"):
                description = component.metadata.description or ""

            tags = []
            if component.tags:
                tags = [tag.name for tag in component.tags]

            dependencies = []
            if hasattr(component.metadata, "dependencies") and component.metadata.dependencies:
                dependencies = [str(dep) for dep in component.metadata.dependencies]

            # Build doc link (relative path from output dir)
            doc_link = f"./{component.name}/README.md"

            metadata = {}
            if hasattr(component.metadata, "author") and component.metadata.author:
                metadata["author"] = component.metadata.author
            if hasattr(component.metadata, "license") and component.metadata.license:
                metadata["license"] = component.metadata.license

            return IndexItem(
                name=component.name,
                type="role",
                description=description,
                path=component.path,
                doc_link=doc_link,
                tags=tags,
                dependencies=dependencies,
                metadata=metadata,
            )

        elif isinstance(component, AnsibleCollection):
            # Extract collection metadata
            description = ""
            if hasattr(component.metadata, "description"):
                description = component.metadata.description or ""

            namespace = component.metadata.namespace

            # FQCN as doc link
            doc_link = f"./{namespace}.{component.metadata.name}/README.md"

            metadata = {
                "version": component.metadata.version,
                "authors": ", ".join(component.metadata.authors or []),
            }

            return IndexItem(
                name=f"{namespace}.{component.metadata.name}",
                type="collection",
                description=description,
                path=Path(str(component.metadata)),  # Collections don't have a direct path
                doc_link=doc_link,
                namespace=namespace,
                metadata=metadata,
            )

        elif isinstance(component, Plugin):
            # Extract plugin metadata
            description = ""
            if hasattr(component, "description"):
                description = component.description or ""

            doc_link = f"./{component.name}.md"

            return IndexItem(
                name=component.name,
                type="plugin",
                description=description,
                path=component.path,
                doc_link=doc_link,
                metadata={
                    "plugin_type": component.type.value if hasattr(component, "type") else "unknown"
                },
            )

        elif isinstance(component, PlaybookInfo):
            # Extract playbook metadata
            doc_link = f"./{component.name}.md"

            return IndexItem(
                name=component.name,
                type="playbook",
                description=component.description or "",
                path=Path(component.path),
                doc_link=doc_link,
                tags=component.tags or [],
            )

        else:
            # Fallback for unknown types - use role as safe default
            return IndexItem(
                name=str(component),
                type="role",
                description="Unknown component type",
                path=Path("."),
                doc_link="#",
            )

    def resolve_dependency_links(
        self,
        items: list[IndexItem],
    ) -> None:
        """Resolve dependency names to documentation links.

        Mutates items in-place to update dependency strings with links.

        Args:
            items: Items to resolve links for
        """
        # Build name -> item lookup for quick resolution
        item_map: dict[str, IndexItem] = {}

        # Build map with all possible name formats
        for item in items:
            item_map[item.name] = item

            # For collections, also index by namespace.name format
            if item.type == "collection" and item.namespace:
                fqcn = f"{item.namespace}.{item.name.split('.')[-1]}"
                item_map[fqcn] = item

        # Resolve dependency links
        for item in items:
            resolved_deps = []
            for dep_name in item.dependencies:
                # Clean up dependency name (remove version specs, etc.)
                clean_name = dep_name.split(":")[0].split("==")[0].split(">=")[0].strip()

                # Try to find matching item
                if clean_name in item_map:
                    dep_item = item_map[clean_name]
                    # Create markdown link
                    resolved_deps.append(f"[{dep_name}]({dep_item.doc_link})")
                else:
                    # No match found, keep as plain text
                    resolved_deps.append(dep_name)

            # Update dependencies with resolved links
            item.dependencies = resolved_deps
