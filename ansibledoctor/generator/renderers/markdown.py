"""Markdown renderer for GitHub Flavored Markdown format.

T217: Implementation to pass T216 tests.
"""
from pathlib import Path
from typing import Any, Dict, Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat, TemplateContext


class MarkdownRenderer:
    """Renderer for GitHub Flavored Markdown (GFM) format.
    
    Provides rendering of role documentation to Markdown format using
    Jinja2 templates with escaping and code block formatting.
    
    Attributes:
        format: OutputFormat.MARKDOWN constant
    
    Example:
        >>> renderer = MarkdownRenderer()
        >>> from ansibledoctor import __version__
        >>> context = TemplateContext(role=role, generator_version=__version__, ...)
        >>> markdown = renderer.render(context)
    """
    
    format = OutputFormat.MARKDOWN
    
    def __init__(self, template_path: Optional[str] = None):
        """Initialize Markdown renderer.
        
        Args:
            template_path: Optional custom template path. If None, uses default.
        """
        self._template_path = template_path
        self._engine: Optional[TemplateEngine] = None
        self._embedded_loader: Optional[EmbeddedTemplateLoader] = None
    
    def _get_engine(self) -> TemplateEngine:
        """Get or create template engine instance (lazy initialization)."""
        if self._engine is None:
            self._engine = TemplateEngine.create()
        return self._engine
    
    def _get_embedded_loader(self) -> EmbeddedTemplateLoader:
        """Get or create embedded template loader (lazy initialization)."""
        if self._embedded_loader is None:
            self._embedded_loader = EmbeddedTemplateLoader()
        return self._embedded_loader
    
    def render(self, context: TemplateContext) -> str:
        """Render role documentation to Markdown format.
        
        Args:
            context: Template context containing role data and metadata
            
        Returns:
            Rendered Markdown documentation
        """
        engine = self._get_engine()
        
        # Determine template to use
        if self._template_path:
            # Custom template provided
            template_content = Path(self._template_path).read_text(encoding="utf-8")
            template = engine.environment.from_string(template_content)
        else:
            # Use default embedded template
            loader = self._get_embedded_loader()
            template = loader.load_template("role", OutputFormat.MARKDOWN)
        
        # Render template with context
        return template.render(**context.to_dict())
    
    def escape(self, text: Optional[str]) -> str:
        """Escape special Markdown characters.
        
        Escapes characters that have special meaning in Markdown:
        - Asterisk (*)
        - Underscore (_)
        - Brackets ([ ])
        - Backtick (`)
        - Hash (#)
        
        Args:
            text: Text potentially containing special characters
            
        Returns:
            Text with special characters escaped using backslash
            
        Example:
            >>> renderer.escape("*bold* _italic_")
            '\\*bold\\* \\_italic\\_'
        """
        if text is None:
            return ""
        if not text:
            return text
        
        # Characters that need escaping in Markdown
        special_chars = "*_[]`#"
        
        # Escape each special character with backslash
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        
        return text

    def code_block(self, code: str, language: str = "") -> str:
        """Format code block with optional syntax highlighting.
        
        Uses GitHub Flavored Markdown fenced code blocks with triple backticks.
        
        Args:
            code: Source code to format
            language: Programming language for syntax highlighting (e.g., 'python', 'yaml')
            
        Returns:
            Formatted code block with language hint
            
        Example:
            >>> renderer.code_block("x = 42", "python")
            '```python\\nx = 42\\n```'
        """
        return f"```{language}\n{code}\n```"
    
    def validate_options(self, options: Dict[str, Any]) -> None:
        """Validate renderer options.
        
        Args:
            options: Options dictionary to validate
            
        Raises:
            TypeError: If gfm_mode is not a boolean
        """
        if "gfm_mode" in options and not isinstance(options["gfm_mode"], bool):
            raise TypeError(f"gfm_mode must be bool, got {type(options['gfm_mode']).__name__}")
