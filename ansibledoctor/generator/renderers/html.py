"""HTML renderer for Ansible role documentation.

This module provides the HtmlRenderer class that renders role documentation
in HTML format using Jinja2 templates with embedded CSS and responsive design.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader
from markupsafe import escape

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.filters import FILTERS
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.protocols import DocumentRenderer


class HtmlRenderer(DocumentRenderer):
    """Renders role documentation in HTML format using Jinja2 templates.

    This renderer produces well-structured HTML5 documents with embedded CSS
    styling and responsive design. It properly escapes HTML entities to prevent
    XSS vulnerabilities using markupsafe.

    Attributes:
        embed_css: Whether to embed CSS in <style> tag (default: True)
        generate_toc: Whether to generate table of contents (default: True)
    """

    def __init__(
        self, embed_css: bool = True, generate_toc: bool = True, template_path: Optional[str] = None
    ):
        """Initialize HTML renderer.

        Args:
            embed_css: Embed CSS in document (default: True)
            generate_toc: Generate table of contents (default: True)
            template_path: Optional custom template path. If None, uses default.
        """
        self.embed_css = embed_css
        self.generate_toc = generate_toc
        self._template_path = template_path
        self._engine: Optional[TemplateEngine] = None
        self._embedded_loader: Optional[EmbeddedTemplateLoader] = None

    def _get_engine(self) -> TemplateEngine:
        """Get or create template engine instance (lazy initialization)."""
        if not self._engine:
            self._engine = TemplateEngine.create()
        return self._engine

    def _get_embedded_loader(self) -> EmbeddedTemplateLoader:
        """Get or create embedded template loader (lazy initialization)."""
        if not self._embedded_loader:
            self._embedded_loader = EmbeddedTemplateLoader()
        return self._embedded_loader

    @property
    def format(self) -> OutputFormat:
        """Return the output format for this renderer.

        Returns:
            OutputFormat.HTML
        """
        return OutputFormat.HTML

    def escape(self, text: Optional[str]) -> str:
        """Escape HTML entities in text.

        Uses markupsafe.escape to safely escape HTML special characters
        (<, >, &, ", ') to prevent XSS attacks.

        Args:
            text: Text to escape (None returns empty string)

        Returns:
            HTML-escaped string
        """
        if text is None:
            return ""
        return str(escape(text))

    def code_block(self, code: Optional[str], language: Optional[str] = None) -> str:
        """Format code in HTML <pre><code> block.

        Args:
            code: Code content (None returns empty block)
            language: Language hint for syntax highlighting (optional)

        Returns:
            HTML pre/code block with escaped content
        """
        if code is None:
            code = ""

        escaped_code = self.escape(code)

        if language:
            return (
                f'<pre><code class="language-{self.escape(language)}">{escaped_code}</code></pre>'
            )
        return f"<pre><code>{escaped_code}</code></pre>"

    def render(self, context: TemplateContext, **options: Any) -> str:  # type: ignore[override]
        """Render role documentation to HTML format using Jinja2 template.

        Args:
            context: Template context with role data
            **options: Additional rendering options (overrides instance settings)

        Returns:
            Rendered HTML documentation string

        Raises:
            TemplateNotFoundError: If html template not found
            TemplateRenderError: If rendering fails
        """
        # Merge instance settings with options
        render_options = {
            "embed_css": options.get("embed_css", self.embed_css),
            "generate_toc": options.get("generate_toc", self.generate_toc),
        }

        # Validate options before rendering
        self.validate_options(render_options)

        # Determine template to use
        if self._template_path:
            # Custom template provided - use FileSystemLoader for include support
            template_file = Path(self._template_path)
            template_dir = template_file.parent
            fs_loader = FileSystemLoader(str(template_dir))
            env = Environment(
                loader=fs_loader,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            env.filters.update(FILTERS)
            template = env.get_template(template_file.name)
        else:
            # Use default embedded template
            from ansibledoctor.generator.loaders import EmbeddedTemplateLoader

            loader: EmbeddedTemplateLoader = self._get_embedded_loader()
            template = loader.load_template("role", OutputFormat.HTML)

        # Add HTML-specific context variables
        template_vars = context.to_dict()
        template_vars["embed_css"] = render_options["embed_css"]
        template_vars["generate_toc"] = render_options["generate_toc"]

        # Render template with context
        return template.render(**template_vars)

    def validate_options(self, options: Dict[str, Any]) -> None:
        """Validate rendering options.

        Args:
            options: Options dictionary to validate

        Raises:
            TypeError: If option types are invalid
            ValueError: If option values are invalid
        """
        if "embed_css" in options and not isinstance(options["embed_css"], bool):
            raise TypeError(f"embed_css must be bool, got {type(options['embed_css'])}")

        if "generate_toc" in options and not isinstance(options["generate_toc"], bool):
            raise TypeError(f"generate_toc must be bool, got {type(options['generate_toc'])}")
