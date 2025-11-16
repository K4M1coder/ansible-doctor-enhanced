"""
Command-line interface for ansible-doctor-enhanced.

Provides parse command for extracting role documentation.
Following Constitution Article IV (CLI Interface Mandate) and Article III (TDD).
"""

import json
import sys
from pathlib import Path

import click

from ansibledoctor import __version__
from ansibledoctor.exceptions import AnsibleDoctorError, ParsingError, ValidationError
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.utils.logging import get_logger, setup_logging
from ansibledoctor.utils.paths import RolePathValidator

logger = get_logger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    ansible-doctor-enhanced - Enhanced Ansible role documentation generator.
    
    Extract metadata, variables, tags, and annotations from Ansible roles
    following KISS, SMART, and SOLID principles.
    """
    pass


@cli.command()
@click.argument("role_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively parse all roles in directory",
)
@click.option(
    "--validate",
    is_flag=True,
    help="Validate role structure before parsing",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--json-output/--no-json-output",
    default=True,
    help="Output in JSON format (default: True)",
)
def parse(
    role_path: Path,
    output: Path | None,
    recursive: bool,
    validate: bool,
    log_level: str,
    json_output: bool,
):
    """
    Parse Ansible role and extract documentation.
    
    ROLE_PATH: Path to Ansible role directory or roles parent directory (with --recursive)
    
    Examples:
    
        # Parse single role
        ansible-doctor-enhanced parse /path/to/role
        
        # Parse and save to file
        ansible-doctor-enhanced parse /path/to/role --output role-doc.json
        
        # Parse multiple roles recursively
        ansible-doctor-enhanced parse /path/to/roles --recursive
        
        # Validate role structure
        ansible-doctor-enhanced parse /path/to/role --validate
    """
    # Setup logging
    setup_logging(level=log_level, json_output=False)
    
    logger.info(
        "cli_parse_started",
        role_path=str(role_path),
        recursive=recursive,
        validate=validate,
    )

    try:
        if recursive:
            result = _parse_roles_recursive(role_path, validate)
        else:
            result = _parse_single_role(role_path, validate)

        # Output result
        if json_output:
            output_data = json.dumps(result, indent=2, default=str)
        else:
            output_data = str(result)

        if output:
            output.write_text(output_data, encoding="utf-8")
            logger.info("output_written", output_file=str(output))
            click.echo(f"Documentation written to {output}", err=True)
        else:
            click.echo(output_data)

        logger.info("cli_parse_completed", success=True)
        sys.exit(0)

    except ValidationError as e:
        logger.error("validation_failed", error=str(e), context=e.context)
        click.echo(f"Validation Error: {e.message}", err=True)
        if e.suggestion:
            click.echo(f"Suggestion: {e.suggestion}", err=True)
        sys.exit(2)

    except ParsingError as e:
        logger.error("parsing_failed", error=str(e), context=e.context)
        click.echo(f"Parsing Error: {e.message}", err=True)
        if e.suggestion:
            click.echo(f"Suggestion: {e.suggestion}", err=True)
        sys.exit(1)

    except AnsibleDoctorError as e:
        logger.error("ansible_doctor_error", error=str(e))
        click.echo(f"Error: {e.message}", err=True)
        sys.exit(1)

    except Exception as e:
        logger.exception("unexpected_error", error=str(e))
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


def _parse_single_role(role_path: Path, validate: bool) -> dict:
    """
    Parse a single Ansible role.
    
    Args:
        role_path: Path to role directory
        validate: Whether to validate role structure first
        
    Returns:
        dict: Parsed role documentation
    """
    logger.info("parsing_single_role", role_path=str(role_path))

    # Validate role structure if requested
    if validate:
        validator = RolePathValidator()
        if not validator.validate_role_structure(role_path):
            raise ValidationError(
                message=f"Invalid role structure: {role_path}",
                context={"role_path": str(role_path)},
                suggestion="Ensure role has required directories (tasks/) and files.",
            )

    # Initialize parsers
    yaml_loader = RuamelYAMLLoader()
    annotation_extractor = AnnotationExtractor()
    metadata_parser = MetadataParser(yaml_loader)
    variable_parser = VariableParser(yaml_loader, annotation_extractor)

    # Parse role components
    result = {
        "name": role_path.name,
        "path": str(role_path),
    }

    # Parse metadata
    meta_dir = role_path / "meta"
    if meta_dir.exists():
        try:
            metadata = metadata_parser.parse_metadata(meta_dir)
            result["metadata"] = {
                "author": metadata.author,
                "description": metadata.description,
                "company": metadata.company,
                "license": metadata.license,
                "min_ansible_version": metadata.min_ansible_version,
                "platforms": [
                    {"name": p.name, "versions": p.versions} for p in metadata.platforms
                ],
                "galaxy_tags": metadata.galaxy_tags,
                "dependencies": [
                    {
                        "name": d.name,
                        "version": d.version,
                        "source": d.source,
                    }
                    for d in metadata.dependencies
                ],
                "has_dependencies": metadata.has_dependencies(),
            }
            logger.debug("metadata_parsed", author=metadata.author)
        except Exception as e:
            logger.warning("metadata_parse_failed", error=str(e))
            result["metadata"] = None

    # Parse variables
    try:
        variables = variable_parser.parse_role_variables(role_path)
        result["variables"] = [
            {
                "name": v.name,
                "value": v.value,
                "type": v.type.value,
                "source": v.source,
                "description": v.description,
                "required": v.required,
                "deprecated": v.deprecated,
                "example": v.example,
            }
            for v in variables
        ]
        
        # Variable statistics
        result["variable_stats"] = {
            "total": len(variables),
            "documented": sum(1 for v in variables if v.is_documented()),
            "required": sum(1 for v in variables if v.required),
            "deprecated": sum(1 for v in variables if v.is_deprecated()),
            "by_source": {
                "defaults": sum(1 for v in variables if v.source == "defaults"),
                "vars": sum(1 for v in variables if v.source == "vars"),
            },
            "by_type": {},
        }
        
        # Count by type
        for v in variables:
            type_name = v.type.value
            result["variable_stats"]["by_type"][type_name] = (
                result["variable_stats"]["by_type"].get(type_name, 0) + 1
            )
        
        logger.debug("variables_parsed", count=len(variables))
    except Exception as e:
        logger.warning("variables_parse_failed", error=str(e))
        result["variables"] = []
        result["variable_stats"] = {}

    logger.info("role_parsed_successfully", role_name=result["name"])
    return result


def _parse_roles_recursive(roles_dir: Path, validate: bool) -> dict:
    """
    Parse multiple roles recursively.
    
    Args:
        roles_dir: Directory containing multiple roles
        validate: Whether to validate role structures
        
    Returns:
        dict: Dictionary of parsed roles by name
    """
    logger.info("parsing_roles_recursive", roles_dir=str(roles_dir))

    results = {
        "roles_dir": str(roles_dir),
        "roles": {},
    }

    # Find potential role directories
    validator = RolePathValidator()
    
    for potential_role in roles_dir.iterdir():
        if not potential_role.is_dir():
            continue
        
        # Check if it's a valid role (has tasks/ directory at minimum)
        if not (potential_role / "tasks").exists():
            logger.debug("skipping_non_role", path=str(potential_role))
            continue
        
        try:
            role_data = _parse_single_role(potential_role, validate)
            results["roles"][potential_role.name] = role_data
            logger.info("role_parsed_in_recursive", role_name=potential_role.name)
        except Exception as e:
            logger.warning(
                "role_parse_failed_in_recursive",
                role_name=potential_role.name,
                error=str(e),
            )
            results["roles"][potential_role.name] = {
                "error": str(e),
                "path": str(potential_role),
            }

    results["summary"] = {
        "total_roles": len(results["roles"]),
        "successful": sum(
            1 for r in results["roles"].values() if "error" not in r
        ),
        "failed": sum(
            1 for r in results["roles"].values() if "error" in r
        ),
    }

    logger.info(
        "recursive_parse_completed",
        total=results["summary"]["total_roles"],
        successful=results["summary"]["successful"],
    )

    return results


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
