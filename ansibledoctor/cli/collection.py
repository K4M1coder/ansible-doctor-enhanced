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
