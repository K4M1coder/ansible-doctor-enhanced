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
from ansibledoctor.config.loader import find_config_file, load_config, merge_config
from ansibledoctor.config.models import ConfigModel
from ansibledoctor.exceptions import AnsibleDoctorError, ParsingError, ValidationError
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.generator.renderers.rst import RstRenderer
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
    
    \b
    Available Commands:
        parse      - Parse role and extract documentation
        generate   - Generate formatted documentation
        watch      - Watch role directory and auto-regenerate docs
        templates  - Manage custom templates
        config     - Configuration file management
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
    "--output-dir",
    "-d",
    type=click.Path(path_type=Path),
    help="Output directory for recursive generation (one file per role)",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively generate documentation for all roles in directory",
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
    "--sphinx-compat/--no-sphinx-compat",
    default=True,
    help="Use Sphinx directives in RST output (default: use)",
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
def generate(role_path, format, output, output_dir, recursive, template, embed_css, generate_toc, sphinx_compat, verbose, log_level):
    """
    Generate documentation for an Ansible role or multiple roles recursively.
    
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
    logger.debug(f"Format: {format}, Output: {output}, Template: {template}, Recursive: {recursive}")
    
    try:
        # T013: Load config file and merge with CLI arguments
        config_file_path = find_config_file(role_path)
        file_config = None
        
        if config_file_path:
            logger.info(f"Found config file: {config_file_path}")
            file_config = load_config(config_file_path)
        else:
            logger.debug("No config file found, using defaults")
        
        # Build CLI config from arguments
        cli_config = ConfigModel(
            output=str(output) if output else None,
            output_format=format.lower() if format else None,
            template=str(template) if template else None,
            recursive=recursive,
            output_dir=str(output_dir) if output_dir else None,
        )
        
        # Merge configs with priority: CLI > file > defaults
        merged_config = merge_config(file_config, cli_config)
        
        # Use merged config values
        format = merged_config.output_format or "markdown"
        if merged_config.output and not output:
            output = Path(merged_config.output)
        if merged_config.template and not template:
            template = Path(merged_config.template)
        if merged_config.output_dir and not output_dir:
            output_dir = Path(merged_config.output_dir)
        recursive = merged_config.recursive
        
        logger.debug(f"Merged config - Format: {format}, Output: {output}, Recursive: {recursive}")
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        click.echo(f"Config error: {e}", err=True)
        sys.exit(1)
    
    try:
        # Handle recursive generation
        if recursive:
            _generate_recursive(
                role_path, format, output_dir, template,
                embed_css, generate_toc, sphinx_compat
            )
            return
        
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
        elif format.lower() == "rst":
            renderer = RstRenderer(
                sphinx_compat=sphinx_compat,
                template_path=str(template) if template else None
            )
            output_format = OutputFormat.RST
        else:
            raise ValidationError(
                f"Format '{format}' not yet implemented",
                "Use 'markdown', 'html', or 'rst' format.",
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


def _generate_recursive(
    roles_dir: Path,
    format: str,
    output_dir: Path | None,
    template: str | None,
    embed_css: bool,
    generate_toc: bool,
    sphinx_compat: bool,
) -> None:
    """Generate documentation recursively for all roles in directory.
    
    Args:
        roles_dir: Directory containing multiple role directories
        format: Output format (markdown, html, rst)
        output_dir: Output directory for generated files (required for recursive)
        template: Custom template path
        embed_css: Embed CSS in HTML output
        generate_toc: Generate table of contents in HTML
        sphinx_compat: Use Sphinx directives in RST
        
    Raises:
        ValidationError: If output_dir not provided for recursive mode
    """
    if not output_dir:
        raise ValidationError(
            message="Output directory (--output-dir) is required for recursive generation",
            context={"roles_dir": str(roles_dir)},
            suggestion="Use --output-dir to specify where to save generated documentation files"
        )
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Discover roles
    role_paths = []
    for potential_role in roles_dir.iterdir():
        if not potential_role.is_dir():
            continue
        
        # Check if it's a valid role (has tasks/ or meta/ directory)
        if (potential_role / "tasks").exists() or (potential_role / "meta").exists():
            role_paths.append(potential_role)
            logger.debug(f"Discovered role: {potential_role.name}")
    
    if not role_paths:
        logger.warning(f"No roles found in {roles_dir}")
        click.echo(f"No roles found in {roles_dir}", err=True)
        return
    
    total_roles = len(role_paths)
    successful = 0
    failed = 0
    
    logger.info(f"Processing {total_roles} roles from {roles_dir}")
    click.echo(f"Processing {total_roles} roles...", err=True)
    
    # Process each role
    for idx, role_path in enumerate(role_paths, 1):
        try:
            logger.info(f"Processing role {idx}/{total_roles}: {role_path.name}")
            click.echo(f"[{idx}/{total_roles}] Generating {role_path.name}...", err=True)
            
            # Parse role
            role = _parse_role_for_generation(role_path)
            
            # Select renderer based on format
            if format.lower() == "markdown":
                renderer = MarkdownRenderer(template_path=template)
                output_format = OutputFormat.MARKDOWN
                ext = ".md"
            elif format.lower() == "html":
                renderer = HtmlRenderer(
                    embed_css=embed_css,
                    generate_toc=generate_toc,
                    template_path=template
                )
                output_format = OutputFormat.HTML
                ext = ".html"
            elif format.lower() == "rst":
                renderer = RstRenderer(
                    sphinx_compat=sphinx_compat,
                    template_path=template
                )
                output_format = OutputFormat.RST
                ext = ".rst"
            else:
                raise ValidationError(
                    f"Format '{format}' not yet implemented",
                    "Use 'markdown', 'html', or 'rst' format.",
                    {"requested_format": format}
                )
            
            # Create template context
            context = TemplateContext(
                role=role,
                generator_version=__version__,
                output_format=output_format,
            )
            
            # Render documentation
            rendered_content = renderer.render(context)
            
            # Write to file
            output_file = output_dir / f"{role_path.name}{ext}"
            output_file.write_text(rendered_content, encoding="utf-8")
            
            logger.info(f"Generated: {output_file}")
            successful += 1
            
        except Exception as e:
            logger.error(f"Failed to process {role_path.name}: {e}")
            click.echo(f"  [FAILED] {e}", err=True)
            failed += 1
            # Continue with next role
    
    # Summary
    click.echo(f"\nComplete: {successful} successful, {failed} failed", err=True)
    logger.info(f"Recursive generation complete: {successful}/{total_roles} successful")
    
    if failed > 0:
        sys.exit(1)


@cli.group()
def templates():
    """
    Manage documentation templates.
    
    List, show, or validate Jinja2 templates for documentation generation.
    """
    pass


@templates.command("list")
def templates_list():
    """
    List all available template formats.
    
    Shows the built-in template formats (markdown, html, rst) and their
    characteristics. Use 'templates show <format>' to view template content.
    
    \b
    Example:
        $ ansible-doctor templates list
    """
    click.echo("Available template formats:\n")
    
    formats = [
        ("markdown", "Markdown (.md)", "GitHub Flavored Markdown with fenced code blocks"),
        ("html", "HTML (.html)", "HTML5 with embedded CSS and responsive design"),
        ("rst", "reStructuredText (.rst)", "Sphinx-compatible RST documentation"),
    ]
    
    for format_name, extension, description in formats:
        click.echo(f"  {format_name:12} {extension:20} - {description}")
    
    click.echo("\nUse 'ansible-doctor templates show <format>' to view template content.")


@templates.command("show")
@click.argument("format", type=click.Choice(["markdown", "html", "rst"], case_sensitive=False))
def templates_show(format):
    """
    Display the default template for a given format.
    
    Shows the built-in Jinja2 template content for the specified format.
    Useful for understanding template structure or creating custom templates.
    
    \b
    FORMAT: Template format (markdown, html, or rst)
    
    \b
    Examples:
        $ ansible-doctor templates show markdown
        $ ansible-doctor templates show html > custom-template.html.j2
    """
    from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
    from ansibledoctor.generator.models import OutputFormat
    
    try:
        loader = EmbeddedTemplateLoader()
        output_format = OutputFormat.from_string(format.lower())
        
        # Read template content
        template_content = loader._read_template("default", output_format)
        
        if template_content is None:
            click.echo(f"Error: Default template for {format} not found", err=True)
            sys.exit(1)
        
        click.echo(f"# Default {format.upper()} Template\n")
        click.echo(template_content)
        
    except Exception as e:
        logger.error(f"Failed to load template: {e}")
        click.echo(f"Error: Failed to load {format} template: {e}", err=True)
        sys.exit(1)


@templates.command("validate")
@click.argument("template_path", type=click.Path(exists=True, path_type=Path))
def templates_validate(template_path):
    """
    Validate a custom Jinja2 template file.
    
    Checks template syntax and ensures it can be parsed by the Jinja2 engine.
    Does not validate template variable usage (role.name, role.variables, etc.),
    only Jinja2 syntax correctness.
    
    \b
    TEMPLATE_PATH: Path to the Jinja2 template file to validate
    
    \b
    Examples:
        $ ansible-doctor templates validate my-template.md.j2
        $ ansible-doctor templates validate templates/custom-role.html.j2
    
    \b
    Exit Codes:
        0: Template is valid
        1: Template has syntax errors
    """
    from jinja2 import Environment, TemplateSyntaxError
    
    try:
        # Read template content
        template_content = template_path.read_text(encoding="utf-8")
        
        # Try to parse template with Jinja2
        env = Environment()
        env.parse(template_content)
        
        click.echo(f"[VALID] Template is valid: {template_path}", err=True)
        click.echo(f"  Lines: {len(template_content.splitlines())}")
        click.echo(f"  Size: {len(template_content)} bytes")
        sys.exit(0)
        
    except TemplateSyntaxError as e:
        click.echo(f"[ERROR] Template syntax error in {template_path}:", err=True)
        click.echo(f"  Line {e.lineno}: {e.message}", err=True)
        sys.exit(1)
        
    except Exception as e:
        click.echo(f"[ERROR] Error reading template: {e}", err=True)
        sys.exit(1)


@cli.group()
def config():
    """
    Configuration file management commands.
    
    Manage .ansibledoctor.yml configuration files for persistent settings.
    Configuration files can be placed in the role directory or any parent
    directory, with the nearest file taking precedence.
    
    \b
    Examples:
        # Show effective configuration
        $ ansible-doctor config show
        
        # Validate config file
        $ ansible-doctor config validate
    """
    pass


@config.command()
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    default=Path.cwd(),
    help="Starting directory for config search (default: current directory)",
)
def show(path: Path):
    """
    Display effective configuration with merged settings.
    
    Shows the configuration that would be used when running commands,
    including values from config file, CLI defaults, and where each
    value comes from.
    
    \b
    PATH: Starting directory for config file search (default: current directory)
    
    \b
    Exit Codes:
        0: Success - configuration displayed
        1: Error - failed to load configuration
    """
    setup_logging("INFO")
    
    try:
        # Find config file
        config_file_path = find_config_file(path)
        
        if config_file_path:
            click.echo(f"Config file: {config_file_path}\n", err=True)
            file_config = load_config(config_file_path)
        else:
            click.echo("No config file found, showing defaults\n", err=True)
            file_config = None
        
        # Merge with empty CLI config to show effective config
        cli_config = ConfigModel()
        merged_config = merge_config(file_config, cli_config)
        
        # Display as YAML with resolved paths
        click.echo("Effective configuration:")
        click.echo("---")
        config_dict = merged_config.model_dump(exclude_none=True)
        
        # Resolve relative paths to absolute if present
        if 'output' in config_dict and config_dict['output']:
            output_path = Path(config_dict['output'])
            if not output_path.is_absolute():
                config_dict['output'] = str(output_path.resolve())
        
        from ruamel.yaml import YAML
        from io import StringIO
        yaml = YAML()
        yaml.default_flow_style = False
        stream = StringIO()
        yaml.dump(config_dict, stream)
        click.echo(stream.getvalue())
        
        # Show which settings come from file vs defaults
        if file_config:
            file_dict = file_config.model_dump(exclude_none=True)
            if file_dict:
                click.echo("Settings from config file:", err=True)
                for key in file_dict.keys():
                    click.echo(f"  - {key}", err=True)
        
    except Exception as e:
        logger.error(f"Error displaying config: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command()
@click.option(
    "--path",
    type=click.Path(exists=True, path_type=Path),
    default=Path.cwd(),
    help="Starting directory for config search (default: current directory)",
)
def validate(path: Path):
    """
    Validate configuration file syntax and schema.
    
    Finds and validates the .ansibledoctor.yml config file, checking:
    - YAML syntax correctness
    - Schema validation (valid fields and types)
    - Value constraints (e.g., output_format must be markdown/html/rst)
    
    \b
    PATH: Starting directory for config file search (default: current directory)
    
    \b
    Exit Codes:
        0: Success - configuration is valid
        1: Error - configuration has errors
    """
    setup_logging("INFO")
    
    try:
        # Find config file
        config_file_path = find_config_file(path)
        
        if not config_file_path:
            click.echo("[NOT FOUND] No config file found", err=True)
            click.echo(f"  Searched from: {path}", err=True)
            click.echo("  Looking for: .ansibledoctor.yml or .ansibledoctor.yaml", err=True)
            sys.exit(1)
        
        # Try to load and validate
        try:
            config = load_config(config_file_path)
            # Use ASCII-safe characters for Windows compatibility
            click.echo(f"[VALID] Config valid: {config_file_path}")
            click.echo(f"  Format: {config.output_format or 'not specified'}")
            click.echo(f"  Recursive: {config.recursive}")
            click.echo(f"  Exclude patterns: {len(config.exclude_patterns)} patterns")
            sys.exit(0)
            
        except Exception as e:
            click.echo(f"[INVALID] Config invalid: {config_file_path}", err=True)
            
            # Enhanced error reporting
            from ruamel.yaml import YAMLError
            from pydantic import ValidationError
            
            if isinstance(e, YAMLError):
                # YAML syntax error - extract line/column info
                click.echo(f"  YAML Syntax Error: {e.problem}", err=True)
                if hasattr(e, 'problem_mark') and e.problem_mark:
                    mark = e.problem_mark
                    click.echo(f"  Line {mark.line + 1}, Column {mark.column + 1}", err=True)
                click.echo("  Check YAML syntax (quotes, indentation, colons)", err=True)
                
            elif isinstance(e, ValidationError):
                # Pydantic validation error - extract field info
                click.echo(f"  Schema Validation Error:", err=True)
                for error in e.errors():
                    field = '.'.join(str(x) for x in error['loc'])
                    msg = error['msg']
                    click.echo(f"    Field '{field}': {msg}", err=True)
                click.echo("  Valid output_format values: markdown, html, rst", err=True)
                
            else:
                # Generic error
                click.echo(f"  Error: {e}", err=True)
            
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("role_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--format",
    type=click.Choice(["markdown", "html", "rst"], case_sensitive=False),
    default="markdown",
    help="Output format for generated documentation (default: markdown)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (optional, prints to stdout if not specified)",
)
def watch(role_path: str, format: str, output: str | None):
    """
    Watch role directory and auto-regenerate documentation on changes.
    
    Monitors the role directory for file changes and automatically regenerates
    documentation when files are modified. Useful for real-time preview during
    role development.
    
    \b
    Monitored paths:
        - meta/
        - defaults/
        - vars/
        - tasks/
        - handlers/
        - .ansibledoctor.yml (config file)
    
    \b
    Examples:
        # Watch role with markdown output
        ansible-doctor-enhanced watch ./my-role
        
        # Watch with HTML output to file
        ansible-doctor-enhanced watch ./my-role --format html --output docs/index.html
        
        # Watch and auto-update README
        ansible-doctor-enhanced watch . --output README.md
    
    Press Ctrl+C to stop watching.
    """
    import signal
    import time
    from datetime import datetime
    
    from ansibledoctor.watcher.monitor import WatchMonitor
    
    role_path_obj = Path(role_path).resolve()
    
    # Load config if present
    config_file_path = find_config_file(role_path_obj)
    file_config = None
    if config_file_path:
        logger.info(f"Found config file: {config_file_path}")
        file_config = load_config(config_file_path)
    
    # Build CLI config
    cli_config = ConfigModel(
        output=str(output) if output else None,
        output_format=format.lower() if format else None,
    )
    
    # Merge configs
    merged_config = merge_config(file_config, cli_config)
    output_format = merged_config.output_format or "markdown"
    output_path = Path(merged_config.output) if merged_config.output else None
    
    # Regeneration callback
    def regenerate_docs():
        """Regenerate documentation (called by file watcher)."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] Regenerating documentation...")
            
            # Parse role
            role = _parse_role_for_generation(role_path_obj)
            
            # Select renderer based on format
            if output_format == "markdown":
                renderer = MarkdownRenderer()
            elif output_format == "html":
                renderer = HtmlRenderer()
            elif output_format == "rst":
                renderer = RstRenderer()
            else:
                raise ValidationError(f"Unsupported format: {output_format}")
            
            # Create template context and render
            context = TemplateContext(
                role=role,
                generator_version=__version__,
                output_format=OutputFormat[output_format.upper()],
            )
            content = renderer.render(context)
            
            # Write output
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content, encoding="utf-8")
                logger.info(f"[{timestamp}] [SUCCESS] Documentation updated: {output_path}")
            else:
                click.echo("\n" + "="*60)
                click.echo(content)
                click.echo("="*60 + "\n")
                logger.info(f"[{timestamp}] [SUCCESS] Documentation generated")
                
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.error(f"[{timestamp}] [ERROR] Generation failed: {e}")
            click.echo(f"[{timestamp}] [ERROR] {e}", err=True)
            # Don't propagate - watch should continue
    
    # Initial generation
    click.echo(f"Watching {role_path_obj}")
    click.echo(f"Output format: {output_format}")
    if output_path:
        click.echo(f"Output file: {output_path}")
    click.echo("\nGenerating initial documentation...")
    regenerate_docs()
    click.echo("\nMonitoring for changes... (Press Ctrl+C to stop)")
    
    # Create and start monitor
    monitor = WatchMonitor(
        role_path_obj,
        callback=regenerate_docs,
        debounce_delay=0.5,
        exclude_patterns=["*.pyc", "__pycache__", ".git", "*.swp", "*.tmp"]
    )
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        click.echo("\n\nStopping watch mode...")
        monitor.stop()
        click.echo("Watch stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring
    monitor.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\nStopping watch mode...")
        monitor.stop()
        click.echo("Watch stopped.")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
