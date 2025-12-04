"""Project documentation generator.

Minimal ProjectDocumentationGenerator to produce a project README listing roles
and collections. This is intentionally lightweight for initial tests and will be
expanded by the T206 tasks in the spec.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.errors import TemplateNotFoundError
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat
from ansibledoctor.models.project import Project
from ansibledoctor.utils.slug import project_slug


class ProjectDocumentationGenerator:
    """Simple generator for project-level documentation.

    The generator supports markdown/html/rst outputs and writes a core README
    including the project's name and enumerates discovered roles and
    collections.
    """

    def __init__(self, project: Project, translation_provider=None):
        self.project = project
        self.translation_provider = translation_provider

    def _get_engine(self) -> TemplateEngine:
        """Get template engine instance."""
        # Use a provided translation provider when present. Previously the
        # engine defaulted to loading package 'en' translations even when
        # the CLI didn't explicitly request translations; this caused the
        # project title to be replaced by 'Project' by default (unexpected
        # for users) so translations are now only enabled when a provider is
        # explicitly provided (e.g. --language passed to CLI).
        provider = self.translation_provider
        return TemplateEngine.create(translation_provider=provider)

    def _get_embedded_loader(self) -> EmbeddedTemplateLoader:
        """Get embedded template loader."""
        return EmbeddedTemplateLoader()

    def build_context(self) -> dict:
        """Build template context for project."""
        title = self.project.name or Path(self.project.path).name
        # Compute license badge URL if license type is known
        license_badge_url = None
        try:
            license_type = getattr(self.project.existing_docs, "license_type", None)
            if license_type:
                # Basic shields.io license badge using common colors
                color_map = {
                    "MIT": "yellow",
                    "Apache-2.0": "blue",
                    "GPL-3.0": "red",
                    "BSD-3-Clause": "orange",
                }
                color = color_map.get(license_type, "lightgrey")
                license_badge_url = f"https://img.shields.io/badge/license-{license_type}-{color}"
        except Exception:
            license_badge_url = None

        return {
            "project": self.project,
            "roles": self.project.roles,
            "collections": self.project.collections,
            "title": title,
            "license_badge_url": license_badge_url,
        }

    def generate(
        self,
        format: str = OutputFormat.MARKDOWN.value,
        output_dir: Optional[Path] = None,
        template_path: Optional[str] = None,
        legacy_output: bool = False,
    ) -> Path:
        """Generate documentation for a project.

        Args:
            format: Output format: 'markdown', 'html', 'rst'
            output_dir: Directory to write docs to. Defaults to './docs/ansibleproject_{projectname}'
            template_path: Optional template path (not used in minimal implementation)

        Returns:
            Path: The path to the generated file.
        """
        if output_dir is None:
            if legacy_output:
                out_dir = Path(self.project.path) / "docs"
            else:
                slug = project_slug(self.project.name)
                out_dir = Path(self.project.path) / "docs" / slug
        else:
            out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        ext = {
            OutputFormat.MARKDOWN.value: "md",
            OutputFormat.HTML.value: "html",
            OutputFormat.RST.value: "rst",
        }.get(format.lower(), "md")

        output_file = out_dir / f"README.{ext}"

        # Build template context
        context = self.build_context()

        # Get template engine
        engine = self._get_engine()

        # Determine template to use
        if template_path:
            # Custom template provided
            template_path_obj = Path(template_path)
            if not template_path_obj.exists():
                raise FileNotFoundError(f"Custom template not found: {template_path}")
            try:
                template_content = template_path_obj.read_text(encoding="utf-8")
                template = engine.environment.from_string(template_content)
            except Exception as e:
                raise ValueError(
                    f"Failed to load custom template: {template_path}\nError: {str(e)}"
                ) from e
        else:
            # Use default embedded template
            loader = self._get_embedded_loader()
            try:
                output_format = OutputFormat[format.upper()]
            except KeyError:
                supported_formats = ", ".join([f.name.lower() for f in OutputFormat])
                raise ValueError(
                    f"Unsupported output format: '{format}'\nSupported formats: {supported_formats}"
                ) from None
            try:
                # Load the template content using the loader, but compile it with
                # the engine instance created above so the translation provider
                # (and the 't' global) is available in the template namespace.
                content = loader._read_template("project", output_format)
                if content is None:
                    raise TemplateNotFoundError(
                        "project",
                        [
                            f"{loader.package}.{loader.templates_path}/{output_format.value}/project.j2"
                        ],
                    )
                template = engine.environment.from_string(content)
            except Exception as e:
                raise ValueError(
                    f"Failed to load embedded project template for format '{format}'\nError: {str(e)}"
                ) from e

        # Render template with context
        try:
            output = template.render(**context)
        except Exception as e:
            raise ValueError(
                f"Failed to render project documentation template\nError: {str(e)}"
            ) from e

        # Write to file
        try:
            output_file.write_text(output, encoding="utf-8")
        except Exception as e:
            raise IOError(
                f"Failed to write documentation to file: {output_file}\nError: {str(e)}"
            ) from e

        return output_file
