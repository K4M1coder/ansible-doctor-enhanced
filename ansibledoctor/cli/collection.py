"""CLI commands for Ansible collection operations.

Provides commands for parsing, validating, and documenting Ansible collections.
"""

import json
import logging
import sys
from pathlib import Path

import click
import structlog

from ansibledoctor.exceptions import AnsibleDoctorError, ParsingError
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.parser.collection_parser import CollectionParser
from ansibledoctor.utils.logging import get_logger
from ansibledoctor.utils.slug import build_context_path, collection_slug

logger = get_logger(__name__)

# Suppress all logging output for CLI to keep stdout clean for JSON output
# Structlog and standard logging both need to be silenced
logging.getLogger().setLevel(logging.CRITICAL)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
)


@click.group()
def collection() -> None:
    """
    Manage Ansible collections.

    Parse, validate, and document Ansible collections.
    """
    pass


@collection.command()
@click.argument("collection_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--pretty",
    "-p",
    is_flag=True,
    help="Pretty-print JSON output with indentation.",
)
@click.option(
    "--validate",
    "-v",
    is_flag=True,
    help="Validate collection structure only (no output).",
)
@click.option(
    "--deep",
    "-d",
    is_flag=True,
    help="Enable deep parsing (full role/plugin details).",
)
def parse(
    collection_path: Path, output: Path | None, pretty: bool, validate: bool, deep: bool
) -> None:
    """
    Parse an Ansible collection and extract metadata.

    Parses galaxy.yml metadata and discovers collection structure (roles, plugins).

    \b
    Examples:
        # Parse collection and output JSON to stdout
        ansible-doctor-enhanced collection parse ./my_namespace.my_collection

        # Parse and save to file
        ansible-doctor-enhanced collection parse ./community.general --output collection.json

        # Parse with pretty-printed JSON
        ansible-doctor-enhanced collection parse ./ansible.posix --pretty

        # Validate collection structure only
        ansible-doctor-enhanced collection parse ./my_collection --validate

        # Deep parse (full role/plugin details)
        ansible-doctor-enhanced collection parse ./my_collection --deep

    Arguments:
        COLLECTION_PATH: Path to the collection directory
    """
    try:
        # Parse the collection
        parser = CollectionParser()
        logger.debug(f"Parsing collection at {collection_path}")
        ansible_collection = parser.parse(collection_path, deep_parse=deep)

        # Validation-only mode: exit with success
        if validate:
            click.echo("Collection is valid", err=True)
            logger.info(f"Collection {ansible_collection.metadata.fqcn} validated successfully")
            return

        # Build output data
        output_data = {
            "fqcn": ansible_collection.metadata.fqcn,
            "version": ansible_collection.metadata.version,
            "namespace": ansible_collection.metadata.namespace,
            "name": ansible_collection.metadata.name,
            "authors": ansible_collection.metadata.authors,
            "dependencies": ansible_collection.metadata.dependencies,
            "roles": ansible_collection.roles,
            "plugins": {
                plugin_type.value: plugins
                for plugin_type, plugins in ansible_collection.plugins.items()
            },
        }

        # Format JSON
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if hasattr(obj, "model_dump"):
                return obj.model_dump()
            if hasattr(obj, "dict"):
                return obj.dict()
            if isinstance(obj, Path):
                return str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        json_output = json.dumps(output_data, indent=2 if pretty else None, default=json_serial)

        # Write to file or stdout
        if output:
            output.write_text(json_output, encoding="utf-8")
            click.echo(f"Output written to {output}", err=True)
            logger.info(f"Collection data written to {output}")
        else:
            click.echo(json_output)

    except ParsingError as e:
        # User-facing parsing errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Parsing error: {e}")
        raise SystemExit(1) from e
    except AnsibleDoctorError as e:
        # Other ansible-doctor errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Error: {e}")
        raise SystemExit(1) from e
    except Exception as e:
        # Unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception(f"Unexpected error during collection parsing: {e}")
        raise SystemExit(1) from e


@collection.command()
@click.argument("collection_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="docs",
    help="Output directory for generated documentation. Default: docs/",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "html", "rst"], case_sensitive=False),
    default="markdown",
    help="Output format: markdown, html, or rst. Default: markdown",
)
@click.option(
    "--template",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    help="Custom Jinja2 template file path. If not specified, uses default embedded template.",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Configuration file path (future: template variables, output options).",
)
@click.option(
    "--legacy-output",
    is_flag=True,
    help="Use legacy output path structure (docs/README.md) instead of slug-based hierarchy.",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=False,
    help="Continue processing remaining files if errors occur (for partial success)",
)
@click.option(
    "--include-index/--no-include-index",
    default=False,
    help="Generate index pages for roles, plugins, etc. (default: False)",
)
@click.option(
    "--index-style",
    type=click.Choice(["list", "table", "tree", "nested-table", "diagram"], case_sensitive=False),
    default="list",
    help="Index visualization style (default: list)",
)
@click.option(
    "--index-format",
    type=click.Choice(["full", "section"], case_sensitive=False),
    default="full",
    help="Index page format: full (standalone pages) or section (embedded) (default: full)",
)
@click.option(
    "--index-depth",
    type=int,
    default=5,
    help="Maximum depth for hierarchical tree visualization (default: 5, use 0 for unlimited)",
)
@click.option(
    "--nested-depth",
    type=int,
    default=2,
    help="Maximum nesting depth for nested-table format (default: 2)",
)
@click.option(
    "--filter",
    "filters",
    multiple=True,
    type=str,
    help="Filter index items by field:value (e.g., tag:database, namespace:my_ns). Multiple filters use AND logic.",
)
def generate(
    collection_path: Path,
    output_dir: Path,
    format: str,
    template: Path | None,
    config: Path | None,
    legacy_output: bool,
    continue_on_error: bool,
    include_index: bool,
    index_style: str,
    index_format: str,
    index_depth: int,
    nested_depth: int,
    filters: tuple[str, ...],
) -> None:
    """
    Generate documentation for an Ansible collection.

    Parses collection metadata, discovers plugins and roles, and generates
    comprehensive documentation in Markdown, HTML, or RST format.

    \b
    Examples:
        # Generate Markdown documentation (default)
        ansible-doctor-enhanced collection generate ./my_namespace.my_collection

        # Generate HTML documentation in custom directory
        ansible-doctor-enhanced collection generate ./community.general --output-dir build/docs --format html

        # Generate RST documentation with custom template
        ansible-doctor-enhanced collection generate ./ansible.posix --format rst --template custom.j2

        # Generate with all options
        ansible-doctor-enhanced collection generate ./my_collection -o docs -f markdown -t template.j2

    Arguments:
        COLLECTION_PATH: Path to the collection directory containing galaxy.yml
    """
    try:
        # Import here to avoid circular dependencies
        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator
        from ansibledoctor.parser.plugin_discovery import PluginDiscovery

        # Parse the collection
        click.echo(f"Parsing collection at {collection_path}...", err=True)
        parser = CollectionParser()
        ansible_collection = parser.parse(collection_path)
        click.echo(
            f"✓ Parsed {ansible_collection.metadata.fqcn} v{ansible_collection.metadata.version}",
            err=True,
        )

        # Discover plugins using PluginDiscovery
        click.echo("Discovering plugins...", err=True)
        discovery = PluginDiscovery(collection_path)
        plugins = discovery.discover_plugins()
        click.echo(f"✓ Discovered {len(plugins)} plugins", err=True)

        # Generate documentation
        click.echo(f"Generating {format.upper()} documentation...", err=True)
        generator = CollectionDocumentationGenerator(
            collection=ansible_collection,
            plugins=plugins,
        )

        # Determine output file path
        output_dir_path = Path(output_dir)

        if not legacy_output:
            # Use slug-based path hierarchy (T225)
            slug = collection_slug(
                ansible_collection.metadata.namespace, ansible_collection.metadata.name
            )
            # Default to 'en' for now as we don't have language support yet
            # build_context_path returns "docs/lang/en/collection_slug"
            rel_path = build_context_path("en", collection=slug)

            # If output_dir is default "docs", we use the full path from build_context_path
            # If output_dir is custom, we treat it as the root instead of "docs"
            if str(output_dir) == "docs":
                output_dir_path = Path(collection_path) / rel_path
            else:
                # Strip "docs/" prefix from rel_path if custom output dir is used
                # rel_path is like "docs/lang/en/..."
                parts = Path(rel_path).parts
                if parts[0] == "docs":
                    rel_path_stripped = Path(*parts[1:])
                    output_dir_path = output_dir_path / rel_path_stripped
                else:
                    output_dir_path = output_dir_path / rel_path

            if not output_dir_path.is_absolute():
                if str(output_dir) != "docs":
                    # If custom output dir, it's relative to CWD or collection path?
                    # Usually relative to CWD if run from CLI, but here we might want relative to collection
                    output_dir_path = Path(collection_path) / output_dir_path
                elif str(output_dir) == "docs" and not str(output_dir_path).startswith(
                    str(collection_path)
                ):
                    # If we constructed it from collection_path above, it's absolute.
                    pass
        else:
            # Legacy behavior
            # Ensure relative output_dir is relative to collection path
            if not output_dir_path.is_absolute():
                output_dir_path = Path(collection_path) / output_dir_path

        output_dir_path.mkdir(parents=True, exist_ok=True)

        extensions = {"markdown": "md", "html": "html", "rst": "rst"}
        output_file = output_dir_path / f"README.{extensions[format.lower()]}"

        # Generate documentation
        generator.generate(
            format=format.lower(),
            output_path=output_file,
            template_path=str(template) if template else None,
        )

        click.echo(f"✓ Documentation generated: {output_file}", err=True)
        logger.info(
            f"Generated {format} documentation for {ansible_collection.metadata.fqcn} at {output_file}"
        )

        # Generate index pages if requested (T023)
        if include_index:
            click.echo(f"Generating {index_style} index pages...", err=True)

            # Import index generator
            # Create template engine for indexes
            # Find the template directory for the current output format
            import ansibledoctor.generator.templates as templates_module
            from ansibledoctor.generator.engine import TemplateEngine
            from ansibledoctor.generator.indexes import DefaultIndexGenerator
            from ansibledoctor.models.index import IndexItem

            templates_dir = Path(templates_module.__file__).parent
            template_engine = TemplateEngine.create(template_dir=templates_dir)

            # Create index generator
            index_generator = DefaultIndexGenerator(
                output_dir=output_dir_path,
                language_code="en",  # Default to English for now
                template_engine=template_engine,
                output_format=format.lower(),
            )

            # Build IndexItems from parsed roles
            role_items: list[IndexItem] = []
            for role_name in ansible_collection.roles:
                # Create IndexItem with basic metadata
                # Extract role name as string (handle both str and AnsibleRole)
                role_name_str: str = (
                    role_name.name if isinstance(role_name, AnsibleRole) else str(role_name)
                )
                item = IndexItem(
                    name=role_name_str,
                    type="role",
                    path=collection_path / "roles" / role_name_str,
                    description=f"Role: {role_name}",  # TODO: Parse role metadata for description
                    tags=[],
                    namespace=ansible_collection.metadata.namespace,
                )
                role_items.append(item)

            # Build IndexItems from plugins
            plugin_items: list[IndexItem] = []
            for plugin in plugins:
                # Cast plugin type to expected Literal type
                plugin_type_str: str = (
                    plugin.type.value if hasattr(plugin.type, "value") else str(plugin.type)
                )
                item = IndexItem(
                    name=plugin.name,
                    type=plugin_type_str,  # type: ignore[arg-type]
                    path=plugin.path,
                    description=plugin.short_description or f"Plugin: {plugin.name}",
                    tags=[],
                    namespace=ansible_collection.metadata.namespace,
                )
                plugin_items.append(item)

            # Generate and write indexes
            components = {}
            if role_items:
                components["roles"] = role_items
            if plugin_items:
                components["plugins"] = plugin_items

            if components:
                # Parse filters if provided
                from ansibledoctor.models.index import IndexFilter

                parsed_filters = []
                if filters:
                    try:
                        parsed_filters = [IndexFilter.parse(f) for f in filters]
                    except ValueError as e:
                        click.echo(f"Error: Invalid filter format: {e}", err=True)
                        raise SystemExit(1) from e

                written_files = index_generator.generate_and_write_indexes(
                    components=components,
                    index_style=index_style,
                    max_depth=index_depth if index_depth > 0 else None,
                    filters=parsed_filters if parsed_filters else None,
                    logger=logger,
                )

                # Report generated index files
                total_files = sum(len(files) for files in written_files.values())
                click.echo(f"✓ Generated {total_files} index file(s)", err=True)
                for _, files in written_files.items():
                    for file_path in files:
                        logger.info(f"Generated index: {file_path}")
            else:
                click.echo("⚠ No components found for index generation", err=True)

    except ParsingError as e:
        # User-facing parsing errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Parsing error: {e}")
        raise SystemExit(1) from e
    except AnsibleDoctorError as e:
        # Other ansible-doctor errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Error: {e}")
        raise SystemExit(1) from e
    except Exception as e:
        # Unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception(f"Unexpected error during collection documentation generation: {e}")
        raise SystemExit(1) from e


@collection.command()
@click.argument("collection_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--show-dependencies",
    "-d",
    is_flag=True,
    help="Display the role dependency graph.",
)
@click.option(
    "--check-circular",
    "-c",
    is_flag=True,
    help="Check for circular dependencies and exit with code 1 if found.",
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["text", "json", "mermaid"], case_sensitive=False),
    default="text",
    help="Output format for dependency graph: text (ASCII tree), json, or mermaid. Default: text",
)
def analyze(
    collection_path: Path,
    show_dependencies: bool,
    check_circular: bool,
    output_format: str,
) -> None:
    """
    Analyze an Ansible collection for role dependencies.

    Analyzes role dependencies within the collection, detects circular dependencies,
    and visualizes the dependency graph in various formats.

    \b
    Examples:
        # Check for circular dependencies
        ansible-doctor-enhanced collection analyze ./my_namespace.my_collection --check-circular

        # Show dependency graph as ASCII tree
        ansible-doctor-enhanced collection analyze ./community.general --show-dependencies

        # Export dependency graph as Mermaid diagram
        ansible-doctor-enhanced collection analyze ./ansible.posix -d -f mermaid

        # Export dependency graph as JSON
        ansible-doctor-enhanced collection analyze ./my_collection --show-dependencies --output-format json

    Arguments:
        COLLECTION_PATH: Path to the collection directory containing galaxy.yml
    """
    try:
        from ansibledoctor.parser.dependency_graph import CircularDependencyError, DependencyGraph

        # Build dependency graph
        click.echo(f"Analyzing collection at {collection_path}...", err=True)
        graph = DependencyGraph.from_collection_path(collection_path)

        # Check for circular dependencies
        has_circular = graph.has_circular_dependencies()

        if has_circular:
            circular_deps = graph.find_circular_dependencies()
            # Display warning with colored output
            warning_msg = click.style(
                "⚠ Warning: Circular dependencies detected!", fg="red", bold=True
            )
            click.echo(warning_msg, err=True)

            for cycle in circular_deps:
                cycle_str = " → ".join(cycle)
                click.echo(click.style(f"  • {cycle_str}", fg="red"), err=True)

            # If check-circular flag is set, exit with error code
            if check_circular:
                click.echo("\nCircular dependency check failed.", err=True)
                raise SystemExit(1)
        else:
            success_msg = click.style("✓ No circular dependencies found", fg="green")
            click.echo(success_msg, err=True)

        # Display dependency graph if requested
        if show_dependencies:
            click.echo(f"\nDependency Graph ({output_format.upper()} format):", err=True)
            click.echo("=" * 60, err=True)

            if output_format.lower() == "text":
                # ASCII tree format - use UTF-8 encoding for box-drawing characters
                text_output = graph.to_ascii_tree()
                # Write to stdout with UTF-8 encoding to support box-drawing characters
                sys.stdout.buffer.write(text_output.encode("utf-8"))
                sys.stdout.buffer.write(b"\n")
                sys.stdout.flush()
            elif output_format.lower() == "json":
                # JSON format
                import json

                json_output = graph.to_json()
                click.echo(json.dumps(json_output, indent=2))
            elif output_format.lower() == "mermaid":
                # Mermaid diagram format
                mermaid_output = graph.to_mermaid()
                click.echo(mermaid_output)

        # If circular dependencies exist but we're not in check mode, exit normally
        if has_circular and not check_circular:
            click.echo(
                "\n⚠ Collection has circular dependencies but continuing (use --check-circular to fail).",
                err=True,
            )

        logger.info(f"Completed dependency analysis for collection at {collection_path}")

    except CircularDependencyError as e:
        # Circular dependency error (shouldn't normally reach here due to explicit checks)
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Circular dependency error: {e}")
        raise SystemExit(1) from e
    except ParsingError as e:
        # User-facing parsing errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Parsing error: {e}")
        raise SystemExit(1) from e
    except AnsibleDoctorError as e:
        # Other ansible-doctor errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Error: {e}")
        raise SystemExit(1) from e
    except Exception as e:
        # Unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception(f"Unexpected error during collection analysis: {e}")
        raise SystemExit(1) from e
