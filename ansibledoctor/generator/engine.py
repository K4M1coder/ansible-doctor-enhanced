"""Jinja2 template engine configuration and builder."""
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from ansibledoctor.generator.filters import FILTERS


class TemplateEngine:
    """Jinja2 template engine with custom filters and configuration.
    
    Provides a pre-configured Jinja2 environment with:
    - Custom filters for Markdown, RST, HTML rendering
    - Strict undefined variable handling (fails on missing vars)
    - Optimized for documentation generation
    
    Example:
        >>> engine = TemplateEngine.create(template_dir="templates")
        >>> template = engine.get_template("role.md.j2")
        >>> output = template.render(role=role_data)
    """

    def __init__(self, environment: Environment):
        """Initialize template engine with Jinja2 environment.
        
        Args:
            environment: Configured Jinja2 Environment
        """
        self._env = environment

    @classmethod
    def create(
        cls,
        template_dir: str | Path | None = None,
        autoescape: bool = False,
        strict_undefined: bool = True,
        translation_provider: object | None = None,
        **jinja_options: Any,
    ) -> "TemplateEngine":
        """Create template engine with default configuration.
        
        Args:
            template_dir: Directory containing templates (optional)
            autoescape: Enable auto-escaping for HTML safety
            strict_undefined: Raise error on undefined variables
            **jinja_options: Additional Jinja2 Environment options
            
        Returns:
            Configured TemplateEngine instance
            
        Example:
            >>> engine = TemplateEngine.create(template_dir="templates")
            >>> engine = TemplateEngine.create(autoescape=True)  # For HTML
        """
        # Configure loader if template directory provided
        loader = None
        if template_dir is not None:
            template_path = Path(template_dir)
            if not template_path.exists():
                raise FileNotFoundError(f"Template directory not found: {template_dir}")
            loader = FileSystemLoader(str(template_path))

        # Create Jinja2 environment with options
        env_options = {
            "loader": loader,
            "autoescape": autoescape,
            "undefined": StrictUndefined if strict_undefined else None,
            "trim_blocks": True,
            "lstrip_blocks": True,
            **jinja_options,
        }
        
        # Remove None values
        env_options = {k: v for k, v in env_options.items() if v is not None}
        
        environment = Environment(**env_options)
        
        # Register custom filters
        environment.filters.update(FILTERS)
        # Register translation function if provided
        if translation_provider is not None:
            try:
                # Provide 't' function in template context
                environment.globals["t"] = getattr(translation_provider, "t")
            except Exception:
                # Ignore silently if provider not as expected
                pass
        
        return cls(environment)

    def get_template(self, template_name: str):
        """Load template by name.
        
        Args:
            template_name: Name of template file (e.g., "role.md.j2")
            
        Returns:
            Jinja2 Template object
            
        Raises:
            TemplateNotFound: If template doesn't exist
        """
        return self._env.get_template(template_name)

    def render_string(self, template_str: str, **context: Any) -> str:
        """Render template from string.
        
        Useful for inline templates or testing.
        
        Args:
            template_str: Template content as string
            **context: Variables to pass to template
            
        Returns:
            Rendered template output
            
        Example:
            >>> engine = TemplateEngine.create()
            >>> result = engine.render_string("Hello {{ name }}", name="World")
            >>> result
            'Hello World'
        """
        template = self._env.from_string(template_str)
        return template.render(**context)

    @property
    def environment(self) -> Environment:
        """Access underlying Jinja2 environment.
        
        Returns:
            Jinja2 Environment instance
        """
        return self._env

    @property
    def filters(self) -> dict[str, Any]:
        """Get registered filters.
        
        Returns:
            Dictionary of filter name -> filter function
        """
        return dict(self._env.filters)
