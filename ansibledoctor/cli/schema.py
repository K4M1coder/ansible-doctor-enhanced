"""CLI commands for schema operations.

Provides commands for schema validation, export, conversion, and documentation.
"""

import json
from pathlib import Path

import click

from ansibledoctor.serialization import FormatConverter, SchemaExporter
from ansibledoctor.validation import ConfigurationValidator


@click.group()
def schema():
    """Schema validation, export, and documentation commands."""
    pass


@schema.command("validate")
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--strict", is_flag=True, help="Treat warnings as errors")
@click.option("--verbose", is_flag=True, help="Show detailed error messages")
def validate_config(config_file: Path, strict: bool, verbose: bool):
    """Validate a configuration file against JSON Schema.

    Args:
        config_file: Path to .ansibledoctor.yml file
        strict: Treat warnings as errors
        verbose: Show detailed error messages with suggestions
    """
    validator = ConfigurationValidator()
    result = validator.validate_file(config_file, strict=strict)

    # Print report
    report = result.format_report(verbose=verbose)
    click.echo(report)

    # Exit with appropriate code
    if not result.is_valid:
        raise click.Abort()
    elif strict and result.warnings:
        raise click.Abort()
    # Default: success (exit code 0)


# T040-T042: Schema export command
@schema.command("export")
@click.argument("schema_type", type=click.Choice(["config", "role", "collection"]))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json-schema", "openapi"]),
    default="json-schema",
    help="Output format: json-schema or openapi",
)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
def export_schema(schema_type: str, output_format: str, output: Path | None):
    """Export JSON Schema for ansible-doctor data models.

    Generates JSON Schema or OpenAPI 3.1 specifications for configuration,
    role, and collection data models. Useful for IDE autocomplete integration.

    Examples:
        \b
        # Export config schema to stdout
        ansible-doctor schema export config

        \b
        # Export as OpenAPI spec to file
        ansible-doctor schema export config --format openapi -o schema.yaml

        \b
        # Export role schema
        ansible-doctor schema export role --output role-schema.json

    Args:
        schema_type: Type of schema to export (config, role, collection)
        output_format: Output format (json-schema, openapi)
        output: Output file path (stdout if not specified)
    """
    exporter = SchemaExporter()

    try:
        # T040: Export based on schema type
        if schema_type == "config":
            schema = exporter.export_config_schema(format_type=output_format)
        elif schema_type in ("role", "collection"):
            # Placeholder for future implementation
            click.echo(f"Schema export for {schema_type} not yet implemented", err=True)
            raise click.Abort()
        else:
            click.echo(f"Unknown schema type: {schema_type}", err=True)
            raise click.Abort()

        # T042: Output to file or stdout
        if output:
            # Write to file
            exporter.export_to_file(schema_type, output, format_type=output_format)
            click.echo(f"✓ Schema exported to {output}")
        else:
            # Print to stdout with pretty formatting
            click.echo(json.dumps(schema, indent=2, ensure_ascii=False))

    except Exception as e:
        click.echo(f"Error exporting schema: {e}", err=True)
        raise click.Abort()


@schema.command("convert")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--to", "to_format", required=True, type=click.Choice(["json", "yaml", "xml", "mermaid"]))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.option("--pretty", is_flag=True, help="Pretty-print output")
def convert_format(input_file: Path, to_format: str, output: Path, pretty: bool):
    """Convert between data formats (YAML, JSON, XML, Mermaid).

    Examples:
        ansible-doctor schema convert config.yml --to json
        ansible-doctor schema convert config.json --to yaml --pretty
        ansible-doctor schema convert config.yml --to xml --output config.xml
        ansible-doctor schema convert config.yml --to mermaid --output diagram.mmd

    Args:
        input_file: Input file path
        to_format: Target format (json, yaml, xml, mermaid)
        output: Output file path (stdout if not specified)
        pretty: Pretty-print output for readability
    """
    try:
        converter = FormatConverter()
        
        # Convert the file
        result = converter.convert_file(
            input_file,
            to_format=to_format,
            pretty=pretty
        )
        
        # Output to file or stdout
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result, encoding="utf-8")
            click.echo(f"Converted {input_file} to {to_format}: {output}")
        else:
            click.echo(result)
            
    except Exception as e:
        click.echo(f"Error converting format: {e}", err=True)
        raise click.Abort()


@schema.command("docs")
@click.argument("schema_type", type=click.Choice(["config", "role", "collection"]))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output markdown file")
def generate_docs(schema_type: str, output: Path):
    """Generate human-readable schema documentation.

    Args:
        schema_type: Type of schema to document
        output: Output markdown file path
    """
    click.echo("Schema documentation not yet implemented (Spec 012 Phase 7)")
    click.echo(f"Would generate docs for {schema_type} schema")
    raise click.Exit(1)
