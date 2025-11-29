"""CLI group for project-level commands.

Provides commands for parsing and generating project-level documentation.
"""
from __future__ import annotations

from pathlib import Path
import click
import json

from ansibledoctor.parser.project_parser import ProjectParser
from ansibledoctor.parser.playbook_analyzer import PlaybookAnalyzer
from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.utils.logging import get_logger
from ansibledoctor.utils.slug import project_slug

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
@click.option("--playbook", "playbook", type=str, default=None, help="Analyze specific playbook (filename) for task flow")
@click.option("--format", "output_format", type=click.Choice(["mermaid", "json"]), default="mermaid")
@click.option("--redact-values/--no-redact-values", "redact_values", default=True, help="Redact sensitive variable values in output (default: True)")
def analyze(project_path: Path, playbook: str | None, output_format: str, redact_values: bool):
    """Analyze a project and output analysis results.

    Performs analysis on the project structure, dependencies, and potential issues,
    then outputs the analysis as JSON to stdout.
    """
    try:
        parser = ProjectParser(redact_sensitive=redact_values)
        project = parser.parse(project_path)
        # If playbook requested, run playbook analyzer
        if playbook:
            analyzer = PlaybookAnalyzer(project)
            res = analyzer.analyze_playbook(playbook)
            if output_format == "mermaid":
                click.echo(res["mermaid"])
            else:
                click.echo(json.dumps(res, indent=2))
            return

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
@click.option("--language", "language", type=str, default=None, help="Language code for translations; specify to enable translations (default: unset)")
@click.option("--languages", "languages", type=str, default=None, help="Comma-separated list of language codes to generate for; overrides config and --language")
@click.option("--legacy-output/--no-legacy-output", "legacy_output", default=False, help="Use legacy output path (docs/README.md instead of docs/ansibleproject_{slug}/)")
@click.option("--redact-values/--no-redact-values", "redact_values", default=True, help="Redact sensitive variable values in generated docs (default: True)")
def generate(project_path: Path, output_dir: Path | None, format: str, template: Path | None, legacy_output: bool, redact_values: bool, language: str | None, languages: str | None):
    """Generate documentation for a project.

    Writes documentation to the project's docs subdirectory with project slug by default.
    """
    try:
        parser = ProjectParser(redact_sensitive=redact_values)
        project = parser.parse(project_path)
        # Create translation provider if language specified
        from ansibledoctor.translation.loader import TranslationLoader

        loader = TranslationLoader()
        # If output_dir is relative, write it under the project path; compute once
        if output_dir is not None:
            out_dir_path = Path(output_dir)
            if not out_dir_path.is_absolute():
                out_dir_path = Path(project_path) / out_dir_path
        else:
            out_dir_path = None
        # Normalize languages: --languages takes precedence over --language
        langs_list = None
        if languages:
            langs_list = [l.strip() for l in languages.split(',') if l.strip()]
        elif language:
            langs_list = [language]

        # If multiple languages specified, generate per language under docs/lang/{code}/
        if langs_list and len(langs_list) > 1:
            # Use MultiLanguageGenerator to render multiple languages using a
            # single parsed Project instance. This keeps parsing costs down.
            from ansibledoctor.generator.multi_language import MultiLanguageGenerator

            mgen = MultiLanguageGenerator(loader=loader)
            mgen.generate(project, langs_list, output_dir=out_dir_path, format=format, template_path=str(template) if template else None, legacy_output=legacy_output)
            click.echo(f"Documentation generated for languages: {', '.join(langs_list)}", err=True)
            return

        # Single language case
        provider = None
        if langs_list:
            provider = loader.load(langs_list[0], Path(project_path))
        gen = ProjectDocumentationGenerator(project=project, translation_provider=provider)
        # If output_dir is relative, write it under the project path
        if output_dir is not None:
            out_dir_path = Path(output_dir)
            if not out_dir_path.is_absolute():
                out_dir_path = Path(project_path) / out_dir_path
        else:
            out_dir_path = None
        out_file = gen.generate(format=format, output_dir=out_dir_path, template_path=str(template) if template else None, legacy_output=legacy_output)
        click.echo(f"Documentation generated: {out_file}", err=True)
    except Exception as e:
        logger.exception("project_generate_failed", error=str(e))
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)
