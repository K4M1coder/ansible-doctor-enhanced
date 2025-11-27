"""CLI group for project-level commands.

Provides commands for parsing and generating project-level documentation.
"""
from __future__ import annotations

from pathlib import Path
import click
import json

from ansibledoctor.parser.project_parser import ProjectParser
from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


@click.group()
def project():
    """Manage Ansible projects."""
    pass


@project.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--redact-values/--no-redact-values", "redact_values", default=True, help="Redact sensitive variable values in output (default: True)")
def parse(project_path: Path, redact_values: bool):
    """Parse a project and output JSON representation.

    Parses the project structure, inventory, roles, collections, and variables,
    then outputs the complete project model as JSON to stdout.
    """
    try:
        parser = ProjectParser(redact_sensitive=redact_values)
        project = parser.parse(project_path)
        # Output as JSON
        output = project.model_dump_json(indent=2)
        click.echo(output)
    except Exception as e:
        logger.exception("project_parse_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@project.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--redact-values/--no-redact-values", "redact_values", default=True, help="Redact sensitive variable values in output (default: True)")
def analyze(project_path: Path, redact_values: bool):
    """Analyze a project and output analysis results.

    Performs analysis on the project structure, dependencies, and potential issues,
    then outputs the analysis as JSON to stdout.
    """
    try:
        parser = ProjectParser(redact_sensitive=redact_values)
        project = parser.parse(project_path)
        # Perform basic analysis
        analysis = {
            "project": project.name,
            "analysis": {
                "total_roles": len(project.roles),
                "total_collections": len(project.collections),
                "total_playbooks": len(project.playbooks),
                "total_inventory_items": len(project.inventory)
            }
        }
        # Output as JSON
        output = json.dumps(analysis, indent=2)
        click.echo(output)
    except Exception as e:
        logger.exception("project_analyze_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@project.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "output_format", type=click.Choice(["mermaid", "json"]), default="mermaid")
def visualize(project_path: Path, output_format: str):
    """Visualize a project architecture.

    Generates a visualization of the project architecture, such as Mermaid diagrams,
    showing relationships between components.
    """
    try:
        parser = ProjectParser()
        project = parser.parse(project_path)
        if output_format == "mermaid":
            # Generate simple Mermaid diagram
            diagram = f"""graph TD
    A[{project.name}] --> B[Roles ({len(project.roles)})]
    A --> C[Collections ({len(project.collections)})]
    A --> D[Playbooks ({len(project.playbooks)})]
    A --> E[Inventory ({len(project.inventory)})]
"""
            click.echo(diagram)
        else:
            # JSON output
            vis_data = {
                "project": project.name,
                "nodes": [
                    {"id": "project", "label": project.name, "type": "project"},
                    {"id": "roles", "label": f"Roles ({len(project.roles)})", "type": "component"},
                    {"id": "collections", "label": f"Collections ({len(project.collections)})", "type": "component"},
                    {"id": "playbooks", "label": f"Playbooks ({len(project.playbooks)})", "type": "component"},
                    {"id": "inventory", "label": f"Inventory ({len(project.inventory)})", "type": "component"}
                ],
                "edges": [
                    {"from": "project", "to": "roles"},
                    {"from": "project", "to": "collections"},
                    {"from": "project", "to": "playbooks"},
                    {"from": "project", "to": "inventory"}
                ]
            }
            output = json.dumps(vis_data, indent=2)
            click.echo(output)
    except Exception as e:
        logger.exception("project_visualize_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@project.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--output-dir", "output_dir", type=click.Path(path_type=Path), default=None)
@click.option("--format", "format", type=click.Choice(["markdown", "html", "rst"]), default="markdown")
@click.option("--template", "template", type=click.Path(exists=True, path_type=Path), default=None)
@click.option("--redact-values/--no-redact-values", "redact_values", default=True, help="Redact sensitive variable values in generated docs (default: True)")
def generate(project_path: Path, output_dir: Path | None, format: str, template: Path | None, redact_values: bool):
    """Generate documentation for a project.

    Writes documentation to the project's docs subdirectory with project slug by default.
    """
    try:
        parser = ProjectParser(redact_sensitive=redact_values)
        project = parser.parse(project_path)
        gen = ProjectDocumentationGenerator(project=project)
        # If output_dir is relative, write it under the project path
        if output_dir is not None:
            out_dir_path = Path(output_dir)
            if not out_dir_path.is_absolute():
                out_dir_path = Path(project_path) / out_dir_path
        else:
            out_dir_path = None
        out_file = gen.generate(format=format, output_dir=out_dir_path, template_path=str(template) if template else None)
        click.echo(f"Documentation generated: {out_file}", err=True)
    except Exception as e:
        logger.exception("project_generate_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)
