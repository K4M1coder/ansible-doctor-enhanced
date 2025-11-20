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
from ansibledoctor.parser.collection_parser import CollectionParser
from ansibledoctor.utils.logging import get_logger

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
def parse(collection_path: Path, output: Path | None, pretty: bool, validate: bool) -> None:
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
    
    Arguments:
        COLLECTION_PATH: Path to the collection directory
    """
    try:
        # Parse the collection
        parser = CollectionParser()
        logger.debug(f"Parsing collection at {collection_path}")
        ansible_collection = parser.parse(collection_path)
        
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
        json_output = json.dumps(output_data, indent=2 if pretty else None)
        
        # Write to file or stdout
        if output:
            output.write_text(json_output, encoding='utf-8')
            click.echo(f"Output written to {output}", err=True)
            logger.info(f"Collection data written to {output}")
        else:
            click.echo(json_output)
        
    except ParsingError as e:
        # User-facing parsing errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Parsing error: {e}")
        raise SystemExit(1)
    except AnsibleDoctorError as e:
        # Other ansible-doctor errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Error: {e}")
        raise SystemExit(1)
    except Exception as e:
        # Unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception(f"Unexpected error during collection parsing: {e}")
        raise SystemExit(1)


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
def generate(
    collection_path: Path,
    output_dir: Path,
    format: str,
    template: Path | None,
    config: Path | None,
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
        from ansibledoctor.generator.collection_generator import (
            CollectionDocumentationGenerator,
        )
        from ansibledoctor.parser.plugin_discovery import PluginDiscovery
        
        # Parse the collection
        click.echo(f"Parsing collection at {collection_path}...", err=True)
        parser = CollectionParser()
        ansible_collection = parser.parse(collection_path)
        click.echo(
            f"✓ Parsed {ansible_collection.metadata.fqcn} v{ansible_collection.metadata.version}",
            err=True,
        )
        
        # Discover plugins
        plugins_path = collection_path / "plugins"
        if plugins_path.exists():
            click.echo("Discovering plugins...", err=True)
            discovery = PluginDiscovery(plugins_path)
            plugins = discovery.discover_plugins()
            click.echo(f"✓ Discovered {len(plugins)} plugins", err=True)
        else:
            plugins = []
            click.echo("⚠ No plugins directory found, skipping plugin discovery", err=True)
        
        # Generate documentation
        click.echo(f"Generating {format.upper()} documentation...", err=True)
        generator = CollectionDocumentationGenerator(
            collection=ansible_collection,
            plugins=plugins,
        )
        
        # Determine output file path
        output_dir_path = Path(output_dir)
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
        
    except ParsingError as e:
        # User-facing parsing errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Parsing error: {e}")
        raise SystemExit(1)
    except AnsibleDoctorError as e:
        # Other ansible-doctor errors
        click.echo(f"Error: {e}", err=True)
        logger.error(f"Error: {e}")
        raise SystemExit(1)
    except Exception as e:
        # Unexpected errors
        click.echo(f"Unexpected error: {e}", err=True)
        logger.exception(f"Unexpected error during collection documentation generation: {e}")
        raise SystemExit(1)
