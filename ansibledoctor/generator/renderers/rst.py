"""RST (reStructuredText) renderer for Ansible role documentation.

This module provides the RstRenderer class that renders role documentation
in reStructuredText format using Jinja2 templates, with optional Sphinx directives.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.protocols import DocumentRenderer


class RstRenderer(DocumentRenderer):
    """Renders role documentation in reStructuredText format using Jinja2 templates.
    
    This renderer produces well-structured RST documents compatible with Sphinx
    documentation system. It properly escapes RST special characters to prevent
    formatting issues.
    
    Attributes:
        sphinx_compat: Whether to use Sphinx directives (default: True)
    """
    
    def __init__(self, sphinx_compat: bool = True, template_path: Optional[str] = None):
        """Initialize RST renderer.
        
        Args:
            sphinx_compat: Use Sphinx directives like .. note:: (default: True)
            template_path: Optional custom template path. If None, uses default.
        """
        self.sphinx_compat = sphinx_compat
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
            OutputFormat.RST
        """
        return OutputFormat.RST
    
    def escape(self, text: str | None) -> str | None:
        """Escape RST special characters to prevent formatting issues.
        
        Escapes: * (emphasis), ` (inline code), _ (emphasis), \\ (escape), | (table)
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text with RST special characters preceded by backslash,
            or None if input is None
        """
        if text is None:
            return None
        if not text:
            return text
        
        # Escape RST special characters
        # Order matters: escape backslash first to avoid double-escaping
        result = text.replace("\\", "\\\\")  # Backslash must be first
        result = result.replace("*", "\\*")   # Emphasis
        result = result.replace("`", "\\`")   # Inline code
        result = result.replace("_", "\\_")   # Emphasis/references
        result = result.replace("|", "\\|")   # Table separator
        
        return result
    
    def code_block(self, code: str, language: str | None = None) -> str:
        """Generate RST code-block directive.
        
        Creates a code block using the .. code-block:: directive with proper
        indentation (3 spaces as per RST convention).
        
        Args:
            code: Code content to display
            language: Language identifier (python, yaml, bash, etc.). 
                     Defaults to "text" if not provided.
            
        Returns:
            RST code-block directive with indented code
            
        Example:
            >>> renderer.code_block("print('hello')", "python")
            ".. code-block:: python\\n\\n   print('hello')"
        """
        lang = language or "text"
        
        # RST code-block directive format:
        # .. code-block:: <language>
        # <blank line>
        #    <indented code>
        
        lines = [f".. code-block:: {lang}", ""]  # Directive + blank line
        
        # Indent each line of code with 3 spaces (RST standard)
        for line in code.split("\n"):
            lines.append(f"   {line}")
        
        return "\n".join(lines)
    
    def render(self, context: TemplateContext, **options: Any) -> str:
        """Render role documentation in RST format.
        
        Args:
            context: Template context with role data and metadata
            **options: Additional rendering options (overrides instance attributes)
            
        Returns:
            Rendered RST documentation as string
            
        Raises:
            TemplateError: If template loading or rendering fails
        """
        # Merge options with instance defaults
        render_options = {
            "sphinx_compat": options.get("sphinx_compat", self.sphinx_compat),
        }
        
        # Validate options
        self.validate_options(render_options)
        
        # Load template
        loader = self._get_embedded_loader()
        template = loader.load_template("role", OutputFormat.RST)
        
        # Prepare template variables
        template_vars = context.to_dict()
        template_vars["sphinx_compat"] = render_options["sphinx_compat"]
        
        # Render template
        return template.render(**template_vars)
    
    def validate_options(self, options: Dict[str, Any]) -> None:
        """Validate rendering options.
        
        Args:
            options: Dictionary of option names to values
            
        Raises:
            ValueError: If options contain invalid values
            TypeError: If options have incorrect types
        """
        if "sphinx_compat" in options:
            value = options["sphinx_compat"]
            if not isinstance(value, bool):
                raise TypeError(
                    f"sphinx_compat must be bool, got {type(value).__name__}"
                )
