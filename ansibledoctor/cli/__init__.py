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
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models import AnsibleRole
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.example_parser import ExampleParser
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.task_parser import TaskParser
from ansibledoctor.parser.todo_parser import TodoParser
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
    task_parser = TaskParser(yaml_loader)
    todo_parser = TodoParser()
    example_parser = ExampleParser()

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

    # Parse task tags (Phase 8 - US3)
    try:
        tags = task_parser.parse_tasks(role_path)
        result["tags"] = [
            {
                "name": t.name,
                "description": t.description,
                "usage_count": t.usage_count,
                "file_locations": t.file_locations,
            }
            for t in tags
        ]
        logger.debug("tags_parsed", count=len(tags))
    except Exception as e:
        logger.warning("tags_parse_failed", error=str(e))
        result["tags"] = []

    # Parse TODO annotations (Phase 8 - US4)
    try:
        todos = todo_parser.parse_role(role_path)
        result["todos"] = [
            {
                "description": t.description,
                "file_path": t.file_path,
                "line_number": t.line_number,
                "priority": t.priority,
            }
            for t in todos
        ]
        logger.debug("todos_parsed", count=len(todos))
    except Exception as e:
        logger.warning("todos_parse_failed", error=str(e))
        result["todos"] = []

    # Parse example code blocks (Phase 8 - US4)
    try:
        examples = example_parser.parse_role(role_path)
        result["examples"] = [
            {
                "title": ex.title,
                "code": ex.code,
                "description": ex.description,
                "language": ex.language,
            }
            for ex in examples
        ]
        logger.debug("examples_parsed", count=len(examples))
    except Exception as e:
        logger.warning("examples_parse_failed", error=str(e))
        result["examples"] = []

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


@cli.command()
@click.argument("role_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "html", "rst"], case_sensitive=False),
    default="markdown",
    help="Output format (default: markdown)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "--template",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    help="Custom template file path",
)
@click.option(
    "--embed-css/--no-embed-css",
    default=True,
    help="Embed CSS in HTML output (default: embed)",
)
@click.option(
    "--generate-toc/--no-generate-toc",
    default=True,
    help="Generate table of contents in HTML output (default: generate)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    help="Set logging level (default: INFO)",
)
def generate(role_path, format, output, template, embed_css, generate_toc, verbose, log_level):
    """
    Generate documentation for an Ansible role.
    
    Parses the role structure (metadata, variables, tasks, tags, TODOs, examples)
    and generates formatted documentation in your choice of output format:
    Markdown (.md), HTML (.html), or reStructuredText (.rst).
    
    The generator uses Jinja2 templates with custom filters optimized for
    documentation rendering. Default templates are provided for all formats,
    or you can specify custom templates for branded documentation.
    
    \b
    ROLE_PATH: Path to the Ansible role directory (must contain tasks/ or meta/)
    
    \b
    Common Usage Examples:
    
        \b
        # Generate Markdown README to stdout (default)
        $ ansible-doctor generate my-role/
        
        \b
        # Generate Markdown and save to file
        $ ansible-doctor generate my-role/ --output README.md
        
        \b
        # Generate HTML documentation with CSS
        $ ansible-doctor generate my-role/ --format html --output docs/index.html
        
        \b
        # Generate RST for Sphinx documentation
        $ ansible-doctor generate my-role/ --format rst --output docs/role.rst
        
        \b
        # Use custom Jinja2 template
        $ ansible-doctor generate my-role/ --template custom-readme.md.j2
        
        \b
        # Debug with verbose logging
        $ ansible-doctor generate my-role/ --verbose --log-level DEBUG
        
        \b
        # Complete example with all options
        $ ansible-doctor generate my-role/ \\
            --format markdown \\
            --output docs/README.md \\
            --template templates/custom.j2 \\
            --verbose
    
    \b
    Template Variables Available:
        - role_name: Role directory name
        - metadata: RoleMetadata object (author, description, license, etc.)
        - variables: List of Variable objects with annotations
        - tags: List of Tag objects with usage counts
        - todos: List of TodoItem objects with priorities
        - examples: List of Example code blocks
        - has_variables, has_tags, has_todos, has_examples: Boolean flags
    
    \b
    Output Formats:
        - markdown: GitHub Flavored Markdown with fenced code blocks
        - html: HTML5 with embedded CSS and responsive design
        - rst: reStructuredText compatible with Sphinx documentation
    
    \b
    Exit Codes:
        0: Success - documentation generated successfully
        1: Error - role parsing or rendering failed (check logs)
    """
    # Setup logging
    if verbose:
        log_level = "DEBUG"
    setup_logging(log_level)
    
    logger.info(f"Generating documentation for role: {role_path}")
    logger.debug(f"Format: {format}, Output: {output}, Template: {template}")
    
    try:
        # Validate role path - raises ValidationError if invalid
        RolePathValidator.validate_role_structure(role_path)
        
        # Parse role
        logger.info("Parsing role structure...")
        role = _parse_role_for_generation(role_path)
        
        # Select renderer based on format
        if format.lower() == "markdown":
            renderer = MarkdownRenderer(template_path=str(template) if template else None)
            output_format = OutputFormat.MARKDOWN
        elif format.lower() == "html":
            renderer = HtmlRenderer(
                embed_css=embed_css,
                generate_toc=generate_toc,
                template_path=str(template) if template else None
            )
            output_format = OutputFormat.HTML
        else:
            raise ValidationError(
                f"Format '{format}' not yet implemented",
                "Use 'markdown' or 'html' format for now. RST coming soon.",
                {"requested_format": format}
            )
        
        # Create template context
        context = TemplateContext(
            role=role,
            generator_version=__version__,
            output_format=output_format,
        )
        
        # Render documentation
        logger.info(f"Rendering documentation in {format} format...")
        rendered_content = renderer.render(context)
        
        # Write output
        if output:
            logger.info(f"Writing output to {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered_content, encoding="utf-8")
            click.echo(f"Documentation generated: {output}", err=True)
        else:
            # Output to stdout
            click.echo(rendered_content)
        
        logger.info("Documentation generation complete")
        
    except (ParsingError, ValidationError, AnsibleDoctorError) as e:
        logger.error(f"Error generating documentation: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def _parse_role_for_generation(role_path: Path) -> AnsibleRole:
    """Parse role for documentation generation.
    
    Args:
        role_path: Path to Ansible role directory
        
    Returns:
        Parsed AnsibleRole object
        
    Raises:
        ParsingError: If role parsing fails
    """
    yaml_loader = RuamelYAMLLoader()
    annotation_extractor = AnnotationExtractor()
    
    # Parse metadata
    metadata_parser = MetadataParser(yaml_loader)
    metadata = metadata_parser.parse_metadata(role_path / "meta")
    
    # Parse variables
    variable_parser = VariableParser(yaml_loader, annotation_extractor)
    variables = variable_parser.parse_role_variables(role_path)
    
    # Parse tags
    task_parser = TaskParser(yaml_loader)
    tags = task_parser.parse_tasks(role_path)
    
    # Parse TODOs
    todo_parser = TodoParser()
    todos = todo_parser.parse_directory(role_path)
    
    # Parse examples
    example_parser = ExampleParser()
    examples = example_parser.parse_directory(role_path)
    
    # Create AnsibleRole aggregate
    role = AnsibleRole(
        name=role_path.name,
        path=role_path.resolve(),
        metadata=metadata,
        variables=variables,
        tags=tags,
        todos=todos,
        examples=examples,
    )
    
    return role


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
