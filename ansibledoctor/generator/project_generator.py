"""Project documentation generator.

Minimal ProjectDocumentationGenerator to produce a project README listing roles
and collections. This is intentionally lightweight for initial tests and will be
expanded by the T206 tasks in the spec.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.translation.loader import TranslationLoader
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
        # Use a provided translation provider when present, otherwise try to load
        # a default provider for 'en' from the project root.
        if self.translation_provider is not None:
            provider = self.translation_provider
        else:
            try:
                loader = TranslationLoader()
                provider = loader.load("en", Path(self.project.path))
            except Exception:
                provider = None
        return TemplateEngine.create(translation_provider=provider)

    def _get_embedded_loader(self) -> EmbeddedTemplateLoader:
        """Get embedded template loader."""
        return EmbeddedTemplateLoader()

    def build_context(self) -> dict:
        """Build template context for project."""
        title = self.project.name or Path(self.project.path).name
        return {
            "project": self.project,
            "roles": self.project.roles,
            "collections": self.project.collections,
            "title": title,
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
                raise ValueError(f"Failed to load custom template: {template_path}\nError: {str(e)}")
        else:
            # Use default embedded template
            loader = self._get_embedded_loader()
            try:
                output_format = OutputFormat[format.upper()]
            except KeyError:
                supported_formats = ", ".join([f.name.lower() for f in OutputFormat])
                raise ValueError(f"Unsupported output format: '{format}'\nSupported formats: {supported_formats}")
            try:
                template = loader.load_template("project", output_format)
            except Exception as e:
                raise ValueError(f"Failed to load embedded project template for format '{format}'\nError: {str(e)}")

        # Render template with context
        try:
            output = template.render(**context)
        except Exception as e:
            raise ValueError(f"Failed to render project documentation template\nError: {str(e)}")

        # Write to file
        try:
            output_file.write_text(output, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to write documentation to file: {output_file}\nError: {str(e)}")

        return output_file
