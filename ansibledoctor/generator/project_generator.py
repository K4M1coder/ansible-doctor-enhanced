"""Project documentation generator.

Minimal ProjectDocumentationGenerator to produce a project README listing roles
and collections. This is intentionally lightweight for initial tests and will be
expanded by the T206 tasks in the spec.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ansibledoctor.models.project import Project
from ansibledoctor.generator.models import OutputFormat


class ProjectDocumentationGenerator:
    """Simple generator for project-level documentation.

    The generator supports markdown/html/rst outputs and writes a core README
    including the project's name and enumerates discovered roles and
    collections.
    """

    def __init__(self, project: Project):
        self.project = project

    def generate(
        self,
        format: str = OutputFormat.MARKDOWN.value,
        output_dir: Optional[Path] = None,
        template_path: Optional[str] = None,
    ) -> Path:
        """Generate documentation for a project.

        Args:
            format: Output format: 'markdown', 'html', 'rst'
            output_dir: Directory to write docs to. Defaults to './doc'
            template_path: Optional template path (not used in minimal implementation)

        Returns:
            Path: The path to the generated file.
        """
        out_dir = Path(output_dir) if output_dir else Path(self.project.path) / "doc"
        out_dir.mkdir(parents=True, exist_ok=True)

        ext = {
            OutputFormat.MARKDOWN.value: "md",
            OutputFormat.HTML.value: "html",
            OutputFormat.RST.value: "rst",
        }.get(format.lower(), "md")

        output_file = out_dir / f"README.{ext}"

        # Build content depending on format
        title = self.project.name or Path(self.project.path).name

        if format.lower() == OutputFormat.HTML.value:
            # Basic HTML wrapper
            html_lines = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                f"  <meta charset=\"utf-8\" />",
                f"  <title>{title}</title>",
                "</head>",
                "<body>",
                f"  <h1>{title}</h1>",
            ]
            if self.project.roles:
                html_lines.append("  <h2>Roles</h2>")
                html_lines.append("  <ul>")
                for r in self.project.roles:
                    html_lines.append(f"    <li>{r.name}</li>")
                html_lines.append("  </ul>")
            if self.project.collections:
                html_lines.append("  <h2>Collections</h2>")
                html_lines.append("  <ul>")
                for c in self.project.collections:
                    html_lines.append(f"    <li>{c.name}</li>")
                html_lines.append("  </ul>")
            html_lines.extend(["</body>", "</html>"])
            output_file.write_text("\n".join(html_lines), encoding="utf-8")

        elif format.lower() == OutputFormat.RST.value:
            # Simple RST formatting: Title underline and subheaders
            rst_lines = [title, "=" * len(title), ""]
            if self.project.roles:
                rst_lines.append("Roles")
                rst_lines.append("-" * 5)
                for r in self.project.roles:
                    rst_lines.append(f"- {r.name}")
                rst_lines.append("")
            if self.project.collections:
                rst_lines.append("Collections")
                rst_lines.append("-" * 11)
                for c in self.project.collections:
                    rst_lines.append(f"- {c.name}")
                rst_lines.append("")
            output_file.write_text("\n".join(rst_lines), encoding="utf-8")

        else:
            # Default: markdown
            content_lines = [f"# {title}", ""]
            if self.project.roles:
                content_lines.append("## Roles")
                for r in self.project.roles:
                    content_lines.append(f"- {r.name}")
                content_lines.append("")
            if self.project.collections:
                content_lines.append("## Collections")
                for c in self.project.collections:
                    content_lines.append(f"- {c.name}")
                content_lines.append("")
            output_file.write_text("\n".join(content_lines), encoding="utf-8")
        return output_file
