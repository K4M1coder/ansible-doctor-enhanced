"""CLI commands for schema operations.

Provides commands for schema validation, export, conversion, and documentation.
"""

import json
from pathlib import Path

import click

from ansibledoctor.serialization import FormatConverter, SchemaExporter
from ansibledoctor.serialization.schema_documenter import SchemaDocumenter
from ansibledoctor.validation import ConfigurationValidator, DataModelValidator


@click.group()
def schema():
    """Schema validation, export, conversion, and documentation.

    Comprehensive schema operations for configuration files and data models:

    \b
    - validate: Validate .ansibledoctor.yml against JSON Schema
    - validate-model: Validate role/collection data against pydantic models
    - export: Export JSON Schema definitions for IDE integration
    - convert: Convert configs between YAML, JSON, XML, Mermaid formats
    - docs: Generate human-readable Markdown from JSON Schema

    Examples:

    \b
      # Validate config with strict mode
      ansible-doctor schema validate .ansibledoctor.yml --strict

    \b
      # Export schema for VS Code autocomplete
      ansible-doctor schema export config --output config-schema.json

    \b
      # Convert config to JSON
      ansible-doctor schema convert .ansibledoctor.yml --to json --pretty

    \b
      # Generate schema documentation
      ansible-doctor schema docs config --output schema-docs.md
    """
    pass


@schema.command("validate")
@click.argument("config_file", type=click.Path(exists=True, path_type=Path))
@click.option("--strict", is_flag=True, help="Treat warnings as errors (for CI/CD)")
@click.option("--verbose", is_flag=True, help="Show detailed error messages with suggestions")
def validate_config(config_file: Path, strict: bool, verbose: bool):
    """Validate .ansibledoctor.yml against JSON Schema.

    Validates configuration files to catch errors early. Use --strict in CI/CD
    to fail on warnings. Use --verbose for detailed error messages with
    actionable suggestions.

    Examples:

        \b
        # Basic validation
        ansible-doctor schema validate .ansibledoctor.yml

        \b
        # Strict mode for CI/CD (fail on warnings)
        ansible-doctor schema validate .ansibledoctor.yml --strict

        \b
        # Verbose output with suggestions
        ansible-doctor schema validate .ansibledoctor.yml --verbose

    Exit Codes:
        0: Validation passed
        1: Validation failed (or warnings in strict mode)

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


@schema.command("validate-model")
@click.argument("model_type", type=click.Choice(["role", "collection"]))
@click.argument("data_file", type=click.Path(exists=True, path_type=Path))
@click.option("--strict-validation", is_flag=True, help="Treat validation warnings as errors")
@click.option("--verbose", is_flag=True, help="Show detailed error messages with field context")
def validate_model(model_type: str, data_file: Path, strict_validation: bool, verbose: bool):
    """Validate role or collection data against pydantic models.

    Validates YAML/JSON data files containing role or collection metadata
    against pydantic data models, ensuring type correctness, required field
    presence, and format compliance (e.g., FQCN for dependencies).

    Checks:
    - Required fields are present
    - Field types match schema (string, list, dict)
    - Dependency format follows FQCN (namespace.name)
    - Platform definitions are valid
    - Version strings follow semver

    Examples:
        \b
        # Validate role metadata
        ansible-doctor schema validate-model role roles/webserver/meta/main.yml

        \b
        # Validate collection with strict mode
        ansible-doctor schema validate-model collection galaxy.yml --strict-validation

        \b
        # Verbose output for debugging
        ansible-doctor schema validate-model role role.yml --verbose

    Exit Codes:
        0: Validation passed (no errors)
        1: Validation failed (or warnings in strict mode)

    Args:
        model_type: Type of model to validate (role, collection)
        data_file: Path to YAML/JSON data file
        strict_validation: Treat warnings as errors
        verbose: Show detailed error messages
    """
    import yaml


    validator = DataModelValidator()

    # Load data from file
    try:
        with data_file.open("r", encoding="utf-8") as f:
            if data_file.suffix in (".yml", ".yaml"):
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
    except Exception as e:
        click.echo(f"Error loading data file: {e}", err=True)
        raise click.Abort() from e

    # Validate based on model type
    try:
        if model_type == "role":
            result = validator.validate_role(data, strict=strict_validation)
        elif model_type == "collection":
            result = validator.validate_collection(data, strict=strict_validation)
        else:
            click.echo(f"Unknown model type: {model_type}", err=True)
            raise click.Abort()

        # Print validation results
        if result.is_valid:
            click.echo(f"✓ {model_type.capitalize()} data is valid")
            if result.warnings and not strict_validation:
                click.echo(f"  {len(result.warnings)} warning(s):")
                for warning in result.warnings:
                    click.echo(f"    - {warning.path}: {warning.message}")
        else:
            click.echo(f"✗ {model_type.capitalize()} data validation failed", err=True)
            click.echo(f"  {len(result.errors)} error(s):")
            for error in result.errors:
                click.echo(f"    - {error.path}: {error.message}")
                if verbose and error.suggestion:
                    click.echo(f"      Suggestion: {error.suggestion}")

        # Exit with appropriate code
        if not result.is_valid:
            raise click.Abort()
        elif strict_validation and result.warnings:
            click.echo("  Strict mode: Warnings treated as errors", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"Error validating model: {e}", err=True)
        raise click.Abort() from e


# T040-T042: Schema export command
@schema.command("export")
@click.argument("schema_type", type=click.Choice(["config", "role", "collection"]))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json-schema", "openapi"]),
    default="json-schema",
    help="Output format: json-schema (default) or openapi",
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path (stdout if omitted)"
)
def export_schema(schema_type: str, output_format: str, output: Path | None):
    """Export JSON Schema or OpenAPI spec for IDE integration.

    Generates JSON Schema Draft 2020-12 or OpenAPI 3.1 specifications for
    configuration, role, and collection data models. Use exported schemas to
    enable autocomplete and validation in VS Code, IntelliJ IDEA, or PyCharm.

    IDE Integration:

        \b
        # VS Code: Add to .vscode/settings.json
        {
          "yaml.schemas": {
            "./config-schema.json": ".ansibledoctor.yml"
          }
        }

        \b
        # IntelliJ IDEA: Settings → Languages & Frameworks →
        # Schemas and DTDs → JSON Schema Mappings → Add mapping

    Examples:
        \b
        # Export config schema to stdout
        ansible-doctor schema export config

        \b
        # Export to file for VS Code
        ansible-doctor schema export config --output config-schema.json

        \b
        # Export as OpenAPI spec (YAML)
        ansible-doctor schema export config --format openapi -o openapi.yaml

        \b
        # Export role schema (future)
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
            # Cast to literal type for type checker
            fmt: str = output_format
            schema = exporter.export_config_schema(format_type=fmt)  # type: ignore[arg-type]
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
            fmt_type: str = output_format
            exporter.export_to_file(schema_type, output, format_type=fmt_type)  # type: ignore[arg-type]
            click.echo(f"✓ Schema exported to {output}")
        else:
            # Print to stdout with pretty formatting
            click.echo(json.dumps(schema, indent=2, ensure_ascii=False))

    except Exception as e:
        click.echo(f"Error exporting schema: {e}", err=True)
        raise click.Abort() from e


@schema.command("convert")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--to",
    "to_format",
    required=True,
    type=click.Choice(["json", "yaml", "xml", "mermaid"]),
    help="Target format",
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path (stdout if omitted)"
)
@click.option("--pretty", is_flag=True, help="Pretty-print output for readability")
def convert_format(input_file: Path, to_format: str, output: Path, pretty: bool):
    """Convert configuration files between formats.

    Convert between YAML, JSON, XML, and Mermaid diagram formats. Use --pretty
    for human-readable output. Mermaid diagrams visualize configuration structure.

    Supported Conversions:
        YAML → JSON, XML, Mermaid
        JSON → YAML, XML, Mermaid
        XML → YAML, JSON

    Use Cases:
        - Convert YAML configs to JSON for APIs
        - Generate XML for legacy systems
        - Create Mermaid diagrams for documentation
        - Validate config by round-trip conversion

    Examples:
        \b
        # YAML to JSON (compact)
        ansible-doctor schema convert config.yml --to json

        \b
        # YAML to JSON (pretty-printed)
        ansible-doctor schema convert config.yml --to json --pretty

        \b
        # YAML to XML file
        ansible-doctor schema convert config.yml --to xml --output config.xml

        \b
        # Generate Mermaid diagram
        ansible-doctor schema convert config.yml --to mermaid --output diagram.mmd

    Args:
        input_file: Input file path (.yml, .json, .xml)
        to_format: Target format (json, yaml, xml, mermaid)
        output: Output file path (stdout if not specified)
        pretty: Pretty-print output for readability
    """
    try:
        converter = FormatConverter()

        # Convert the file
        result = converter.convert_file(input_file, to_format=to_format, pretty=pretty)

        # Output to file or stdout
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result, encoding="utf-8")
            click.echo(f"Converted {input_file} to {to_format}: {output}")
        else:
            click.echo(result)

    except Exception as e:
        click.echo(f"Error converting format: {e}", err=True)
        raise click.Abort() from e


@schema.command("docs")
@click.argument("schema_type", type=click.Choice(["config", "role", "collection"]))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output markdown file (stdout if omitted)",
)
def generate_docs(schema_type: str, output: Path):
    """Generate human-readable Markdown documentation from JSON Schema.

    Creates comprehensive Markdown documentation from JSON Schema definitions
    with property descriptions, types, defaults, constraints, and examples.
    Perfect for team onboarding, documentation websites, or README files.

    Generated Documentation Includes:
        - Schema title and description
        - Property sections with types
        - Required vs optional fields
        - Default values
        - Enum constraints with all allowed values
        - Nested object properties (unlimited depth)
        - Deprecation warnings
        - Usage examples

    Examples:
        \b
        # Generate config schema docs to stdout
        ansible-doctor schema docs config

        \b
        # Save docs to file
        ansible-doctor schema docs config --output docs/config-schema.md

        \b
        # Generate role schema docs (future)
        ansible-doctor schema docs role --output docs/role-schema.md

        \b
        # Generate collection schema docs (future)
        ansible-doctor schema docs collection --output docs/collection-schema.md

    Use Cases:
        - Team documentation for config options
        - Onboarding guides for new developers
        - README sections with property references
        - Documentation websites with schema details

    Args:
        schema_type: Type of schema to document (config, role, collection)
        output: Output markdown file path (stdout if not specified)
    """
    try:
        exporter = SchemaExporter()
        documenter = SchemaDocumenter()

        # Export schema first
        if schema_type == "config":
            schema = exporter.export_config_schema(format_type="json-schema")
        elif schema_type in ("role", "collection"):
            # For now, role/collection not fully implemented in exporter
            click.echo(f"Schema documentation for {schema_type} coming in future release", err=True)
            raise click.Abort()
        else:
            click.echo(f"Unknown schema type: {schema_type}", err=True)
            raise click.Abort()

        # Generate documentation
        docs = documenter.generate_docs(schema)

        # Output to file or stdout
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(docs, encoding="utf-8")
            click.echo(f"✓ Documentation written to {output}")
        else:
            click.echo(docs)

    except Exception as e:
        click.echo(f"Error generating documentation: {e}", err=True)
        raise click.Abort() from e
