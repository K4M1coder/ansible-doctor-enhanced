"""Index generator for creating component indexes and navigation structures."""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

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
        # collections -> roles/plugins/playbooks

        collections = [item for item in items if item.type == "collection"]
        roles = [item for item in items if item.type == "role"]
        plugins = [item for item in items if item.type in ("plugin", "module")]
        playbooks = [item for item in items if item.type == "playbook"]

        # Build tree by matching items to their parent collection
        # An item belongs to a collection if its path starts with the collection's path
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

            # Find playbooks belonging to this specific collection
            collection_playbooks = [
                playbook
                for playbook in playbooks
                if str(playbook.path).startswith(str(collection.path))
            ]
            collection.children.extend(collection_playbooks)

        # Return root items (collections + standalone items)
        root_items = collections.copy()

        # Add standalone roles (not under any collection)
        standalone_roles = [
            role
            for role in roles
            if not any(str(role.path).startswith(str(c.path)) for c in collections)
        ]
        root_items.extend(standalone_roles)

        # Add standalone playbooks (not under any collection)
        standalone_playbooks = [
            playbook
            for playbook in playbooks
            if not any(str(playbook.path).startswith(str(c.path)) for c in collections)
        ]
        root_items.extend(standalone_playbooks)

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

    def write_index_files(
        self,
        pages: list[IndexPage],
        component_type: str,
        logger: object | None = None,
    ) -> list[Path]:
        """Write index pages to output directory.

        Args:
            pages: List of IndexPage objects to write
            component_type: Type of components (e.g., 'roles', 'plugins')
            logger: Optional structured logger for observability

        Returns:
            List of Path objects for written files

        Raises:
            IOError: If unable to write files
        """
        import time

        start_time = time.time()
        written_files: list[Path] = []

        # Create index directory if it doesn't exist
        index_dir = self.output_dir / component_type
        index_dir.mkdir(parents=True, exist_ok=True)

        for page in pages:
            # Determine filename based on page number
            if page.page_number == 1:
                filename = "index.md"
            else:
                filename = f"index-{page.page_number}.md"

            file_path = index_dir / filename

            # Handle empty collections (T024)
            if not page.items:
                # Generate empty state message
                content = f"# {page.title}\n\n*No {component_type} found.*\n"
                if logger:
                    logger.info(
                        "index_empty_collection",
                        component_type=component_type,
                        page_number=page.page_number,
                    )
            else:
                # Render page using template
                if self._engine:
                    content = self.render_index_page(page)
                else:
                    # Fallback to simple format
                    content = f"# {page.title}\n\n"
                    for item in page.items:
                        content += f"- [{item.name}]({item.doc_link})\n"

            # Write file
            file_path.write_text(content, encoding="utf-8")
            written_files.append(file_path)

            # Logging (T026)
            if logger:
                logger.info(
                    "index_page_written",
                    file_path=str(file_path),
                    page_number=page.page_number,
                    item_count=len(page.items),
                    component_type=component_type,
                )

        # Summary logging (T026)
        duration_ms = (time.time() - start_time) * 1000
        if logger:
            logger.info(
                "index_generation_complete",
                component_type=component_type,
                total_pages=len(pages),
                total_files=len(written_files),
                duration_ms=round(duration_ms, 2),
            )

        return written_files

    def generate_and_write_indexes(
        self,
        components: dict[str, list[IndexItem]],
        index_style: str = "list",
        max_depth: int | None = None,
        filters: list["IndexFilter"] | None = None,
        logger: object | None = None,
    ) -> dict[str, list[Path]]:
        """Generate and write index pages for all component types.

        High-level method that orchestrates index generation for multiple
        component types (roles, plugins, modules, etc.).

        Args:
            components: Dict mapping component type to list of IndexItems
            index_style: Visualization style (list, table, tree, etc.)
            max_depth: Maximum depth for tree visualization (None = unlimited)
            filters: Optional list of IndexFilter to apply to items
            logger: Optional structured logger

        Returns:
            Dict mapping component type to list of written file paths
        """
        import time

        start_time = time.time()
        all_files: dict[str, list[Path]] = {}

        for component_type, items in components.items():
            # Apply filters if provided
            filtered_items = items
            if filters:
                for filter_obj in filters:
                    filtered_items = [item for item in filtered_items if filter_obj.matches(item)]

            if logger:
                logger.info(
                    "index_generation_start",
                    component_type=component_type,
                    item_count=len(filtered_items),
                    original_count=len(items),
                    style=index_style,
                    filters_applied=len(filters) if filters else 0,
                )

            # Generate index pages
            pages = self.generate_index_page(
                component_type=component_type,
                items=filtered_items,
                format=index_style,
            )

            # Write to files
            files = self.write_index_files(
                pages=pages,
                component_type=component_type,
                logger=logger,
            )

            all_files[component_type] = files

        # Overall summary logging
        total_duration_ms = (time.time() - start_time) * 1000
        if logger:
            logger.info(
                "all_indexes_generated",
                component_types=list(components.keys()),
                total_component_types=len(components),
                total_files=sum(len(files) for files in all_files.values()),
                duration_ms=round(total_duration_ms, 2),
            )

        return all_files

    def generate_alphabetical_index(
        self,
        items: list[IndexItem] | list[dict[str, Any]],
    ) -> dict[str, list[dict[str, str]]]:
        """Generate alphabetical index grouping items by first letter.

        Groups items by the first letter of their name (case-insensitive).
        Special characters and numbers are normalized to appropriate buckets.

        Args:
            items: List of IndexItem objects or dicts to index

        Returns:
            Dictionary mapping letter to list of item dicts with name, path, type

        Example:
            {
                "A": [{"name": "apache", "path": "./apache/README.md", "type": "role"}],
                "B": [{"name": "backup", "path": "./backup/README.md", "type": "role"}],
                "#": [{"name": "123_test", "path": "./123_test/README.md", "type": "role"}],
            }
        """
        import unicodedata

        index: dict[str, list[dict[str, str]]] = {}

        for item in items:
            # Handle both IndexItem objects and dicts
            if isinstance(item, dict):
                name = str(item.get("name", "")).strip()
                doc_link = str(item.get("doc_link", item.get("path", "#")))
                item_type = str(item.get("type", "unknown"))
            else:
                name = item.name.strip()
                doc_link = item.doc_link
                item_type = item.type

            if not name:
                first_char = "#"
            else:
                first_char = name[0].upper()

                # Normalize special characters
                if first_char == "_":
                    # Get letter after underscore (common in private roles)
                    if len(name) > 1:
                        first_char = name[1].upper()
                    else:
                        first_char = "#"

                # Handle numbers
                if first_char.isdigit():
                    first_char = "#"

                # Normalize unicode characters (e.g., ñ -> N, ü -> U)
                if not first_char.isascii():
                    # Remove diacritics
                    normalized = unicodedata.normalize("NFD", first_char)
                    first_char = "".join(
                        char for char in normalized if unicodedata.category(char) != "Mn"
                    )
                    if not first_char or not first_char.isalpha():
                        first_char = "#"
                    else:
                        first_char = first_char.upper()

                # Fallback for other special characters
                if not first_char.isalnum():
                    first_char = "#"

            # Add to index
            if first_char not in index:
                index[first_char] = []

            index[first_char].append(
                {
                    "name": name,
                    "path": doc_link,
                    "type": item_type,
                }
            )

        # Sort items within each letter group
        for letter in index:
            index[letter].sort(key=lambda x: x["name"].lower())

        # Sort the index by letter (# comes last)
        sorted_index = {}
        for letter in sorted(index.keys()):
            if letter == "#":
                continue
            sorted_index[letter] = index[letter]

        # Add # at the end if it exists
        if "#" in index:
            sorted_index["#"] = index["#"]

        return sorted_index

    def generate_category_index(
        self,
        items: list[IndexItem] | list[dict[str, Any]],
    ) -> dict[str, dict[str, list[dict[str, str]] | int]]:
        """Generate category index grouping items by type.

        Groups items by their type (role, module, filter, lookup, etc.)
        and includes navigation metadata.

        Args:
            items: List of IndexItem objects or dicts to index

        Returns:
            Dictionary mapping category to metadata dict with items and count

        Example:
            {
                "role": {
                    "items": [{"name": "apache", "path": "./apache/README.md"}],
                    "count": 1
                },
                "module": {
                    "items": [{"name": "file_copy", "path": "./file_copy.md"}],
                    "count": 1
                }
            }
        """
        index: dict[str, dict[str, list[dict[str, str]] | int]] = {}

        for item in items:
            # Handle both IndexItem objects and dicts
            if isinstance(item, dict):
                category = str(item.get("type", "other"))
                name = str(item.get("name", ""))
                doc_link = str(item.get("doc_link", item.get("path", "#")))
                description = str(item.get("description", ""))
            else:
                category = item.type or "other"
                name = item.name
                doc_link = item.doc_link
                description = item.description or ""

            if category not in index:
                index[category] = {"items": [], "count": 0}

            items_list = index[category]["items"]
            if isinstance(items_list, list):
                items_list.append(
                    {
                        "name": name,
                        "path": doc_link,
                        "description": description,
                    }
                )
                index[category]["count"] = len(items_list)

        # Sort items within each category
        for category in index:
            items_list = index[category]["items"]
            if isinstance(items_list, list):
                items_list.sort(key=lambda x: x["name"].lower())

        # Sort categories alphabetically
        return dict(sorted(index.items()))

    def generate_tag_index(
        self,
        items: list[IndexItem] | list[dict[str, Any]],
    ) -> dict[str, dict[str, list[dict[str, str]] | int]]:
        """Generate tag index grouping items by their tags.

        Groups items by their tags (one item can appear in multiple groups).
        Includes "untagged" category for items without tags.
        Tags are sorted by popularity (number of items).

        Args:
            items: List of IndexItem objects or dicts to index

        Returns:
            Dictionary mapping tag to metadata dict with items and count

        Example:
            {
                "database": {
                    "items": [{"name": "mysql", "path": "./mysql/README.md"}],
                    "count": 1
                },
                "web": {
                    "items": [{"name": "apache", "path": "./apache/README.md"}],
                    "count": 2
                },
                "untagged": {
                    "items": [{"name": "util", "path": "./util/README.md"}],
                    "count": 1
                }
            }
        """
        tag_index: dict[str, dict[str, list[dict[str, str]] | int]] = {}
        untagged_items: list[dict[str, str]] = []

        for item in items:
            # Handle both IndexItem objects and dicts
            if isinstance(item, dict):
                tags = item.get("tags", [])
                name = str(item.get("name", ""))
                doc_link = str(item.get("doc_link", item.get("path", "#")))
                item_type = str(item.get("type", "unknown"))
            else:
                tags = item.tags
                name = item.name
                doc_link = item.doc_link
                item_type = item.type

            if not tags:
                # Add to untagged
                untagged_items.append(
                    {
                        "name": name,
                        "path": doc_link,
                        "type": item_type,
                    }
                )
            else:
                # Add to each tag group
                for tag in tags:
                    if tag not in tag_index:
                        tag_index[tag] = {"items": [], "count": 0}

                    items_list = tag_index[tag]["items"]
                    if isinstance(items_list, list):
                        items_list.append(
                            {
                                "name": name,
                                "path": doc_link,
                                "type": item_type,
                            }
                        )
                        tag_index[tag]["count"] = len(items_list)

        # Add untagged category if there are untagged items
        if untagged_items:
            tag_index["untagged"] = {"items": untagged_items, "count": len(untagged_items)}

        # Sort items within each tag
        for tag in tag_index:
            items_list = tag_index[tag]["items"]
            if isinstance(items_list, list):
                items_list.sort(key=lambda x: x["name"].lower())

        # Sort tags by popularity (count) descending, then alphabetically
        sorted_index = dict(
            sorted(
                tag_index.items(),
                key=lambda x: (-x[1]["count"] if isinstance(x[1]["count"], int) else 0, x[0]),
            )
        )

        return sorted_index

    def generate_search_index(
        self,
        items: list[IndexItem] | list[dict[str, Any]],
    ) -> dict[str, list[dict[str, str | int]]]:
        """Generate search index with inverted index for term lookup.

        Tokenizes item names, descriptions, and docstrings to build an
        inverted index mapping terms to items. Supports partial matching
        and relevance scoring.

        Args:
            items: List of IndexItem objects or dicts to index

        Returns:
            Dictionary mapping term to list of item dicts with name, path, type, score

        Example:
            {
                "apache": [
                    {"name": "apache", "path": "./apache/README.md", "type": "role", "score": 10},
                    {"name": "web_apache", "path": "./web_apache/README.md", "type": "role", "score": 5}
                ],
                "database": [
                    {"name": "mysql", "path": "./mysql/README.md", "type": "role", "score": 8}
                ]
            }
        """
        import re

        # Stop words to filter out
        stop_words = {
            "the",
            "and",
            "or",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
        }

        search_index: dict[str, dict[str, dict[str, str | int]]] = {}

        for item in items:
            # Handle both IndexItem objects and dicts
            if isinstance(item, dict):
                name = str(item.get("name", ""))
                description = str(item.get("description", ""))
                tags = item.get("tags", [])
                doc_link = str(item.get("doc_link", item.get("path", "#")))
                item_type = str(item.get("type", "unknown"))
            else:
                name = item.name
                description = item.description or ""
                tags = item.tags
                doc_link = item.doc_link
                item_type = item.type

            # Tokenize name, description, and tags
            text_parts = [
                name,
                description,
                " ".join(tags),
            ]

            # Combine and tokenize
            text = " ".join(text_parts).lower()

            # Split into tokens (alphanumeric sequences)
            tokens = re.findall(r"\w+", text)

            # Filter stop words and short tokens
            tokens = [t for t in tokens if t not in stop_words and len(t) >= 2]

            # Calculate term frequency for scoring
            term_freq: dict[str, int] = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1

            # Add to search index
            for term, freq in term_freq.items():
                if term not in search_index:
                    search_index[term] = {}

                # Calculate score (higher for name matches, boost by frequency)
                score = freq
                if term in name.lower():
                    score += 10  # Name match bonus
                if term == name.lower():
                    score += 20  # Exact name match bonus

                # Store item reference
                item_key = f"{name}:{item_type}"
                if item_key not in search_index[term]:
                    search_index[term][item_key] = {
                        "name": name,
                        "path": doc_link,
                        "type": item_type,
                        "score": score,
                    }
                else:
                    # Update score if higher
                    existing_score = search_index[term][item_key].get("score", 0)
                    if isinstance(existing_score, int) and score > existing_score:
                        search_index[term][item_key]["score"] = score

        # Convert to final format (list of items per term)
        final_index: dict[str, list[dict[str, str | int]]] = {}
        for term, items_dict in search_index.items():
            # Sort by score descending
            sorted_items = sorted(
                items_dict.values(),
                key=lambda x: -x["score"] if isinstance(x.get("score"), int) else 0,
            )
            final_index[term] = sorted_items

        return final_index

    def search(
        self,
        index: dict[str, list[dict[str, str | int]]],
        query: str,
    ) -> list[dict[str, str | int | list[str]]]:
        """Search the inverted index with a query.

        Tokenizes the query and looks up each term in the index.
        Merges results with combined relevance scoring.

        Args:
            index: Search index from generate_search_index
            query: Search query string

        Returns:
            List of item dicts with name, path, type, score, matched_terms
            Sorted by relevance score descending

        Example:
            >>> index = generator.generate_search_index(items)
            >>> results = generator.search(index, "apache web server")
            [
                {
                    "name": "apache",
                    "path": "./apache/README.md",
                    "type": "role",
                    "score": 25,
                    "matched_terms": ["apache", "web", "server"]
                }
            ]
        """
        import re

        # Tokenize query
        tokens = re.findall(r"\w+", query.lower())
        tokens = [t for t in tokens if len(t) >= 2]

        if not tokens:
            return []

        # Aggregate results across all terms
        result_map: dict[str, dict[str, str | int | list[str]]] = {}

        for term in tokens:
            # Direct lookup
            if term in index:
                for item in index[term]:
                    item_key = f"{item['name']}:{item['type']}"

                    if item_key not in result_map:
                        result_map[item_key] = {
                            "name": item["name"],
                            "path": item["path"],
                            "type": item["type"],
                            "score": 0,
                            "matched_terms": [],
                        }

                    # Add score
                    current_score = result_map[item_key]["score"]
                    item_score = item.get("score", 0)
                    if isinstance(current_score, int) and isinstance(item_score, int):
                        result_map[item_key]["score"] = current_score + item_score

                    # Add matched term
                    matched_terms = result_map[item_key]["matched_terms"]
                    if isinstance(matched_terms, list) and term not in matched_terms:
                        matched_terms.append(term)

            # Partial matching (substring search)
            else:
                for index_term, items in index.items():
                    if term in index_term or index_term in term:
                        for item in items:
                            item_key = f"{item['name']}:{item['type']}"

                            if item_key not in result_map:
                                result_map[item_key] = {
                                    "name": item["name"],
                                    "path": item["path"],
                                    "type": item["type"],
                                    "score": 0,
                                    "matched_terms": [],
                                }

                            # Add partial match score (lower weight)
                            current_score = result_map[item_key]["score"]
                            item_score = item.get("score", 0)
                            if isinstance(current_score, int) and isinstance(item_score, int):
                                result_map[item_key]["score"] = current_score + (item_score // 2)

                            # Add matched term
                            matched_terms = result_map[item_key]["matched_terms"]
                            if isinstance(matched_terms, list) and index_term not in matched_terms:
                                matched_terms.append(index_term)

        # Sort by score descending
        results = sorted(
            result_map.values(),
            key=lambda x: -x["score"] if isinstance(x.get("score"), int) else 0,
        )

        return results
