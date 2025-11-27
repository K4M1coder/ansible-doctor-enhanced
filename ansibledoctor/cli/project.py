"""CLI group for project-level commands.

Provides commands for parsing and generating project-level documentation.
"""
from __future__ import annotations

from pathlib import Path
import click

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
@click.option("--output-dir", "output_dir", type=click.Path(path_type=Path), default="doc")
@click.option("--format", "format", type=click.Choice(["markdown", "html", "rst"]), default="markdown")
@click.option("--template", "template", type=click.Path(exists=True, path_type=Path), default=None)
def generate(project_path: Path, output_dir: Path, format: str, template: Path | None):
    """Generate documentation for a project.

    Writes documentation to the project's `doc` subdirectory by default.
    """
    try:
        parser = ProjectParser()
        project = parser.parse(project_path)
        gen = ProjectDocumentationGenerator(project=project)
        # If output_dir is relative, write it under the project path
        out_dir_path = Path(output_dir)
        if not out_dir_path.is_absolute():
            out_dir_path = Path(project_path) / out_dir_path
        out_file = gen.generate(format=format, output_dir=out_dir_path, template_path=str(template) if template else None)
        click.echo(f"Documentation generated: {out_file}", err=True)
    except Exception as e:
        logger.exception("project_generate_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)
