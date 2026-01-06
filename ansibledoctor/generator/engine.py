"""Jinja2 template engine configuration and builder."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template

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
        index_generator: object | None = None,
        **jinja_options: Any,
    ) -> "TemplateEngine":
        """Create template engine with default configuration.

        Args:
            template_dir: Directory containing templates (optional)
            autoescape: Enable auto-escaping for HTML safety
            strict_undefined: Raise error on undefined variables
            translation_provider: Provider for translation function
            index_generator: IndexGenerator for {{ index() }} template markers
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
                environment.globals["t"] = translation_provider.t
                # Also provide 't' as a filter to be used in templates like: {{ 'key' | t }}
                environment.filters["t"] = translation_provider.t
            except Exception:
                # Ignore silently if provider not as expected
                pass

        # Register index() function if index_generator provided
        if index_generator is not None:
            # Store generator in globals so templates can access it
            environment.globals["_index_generator"] = index_generator

            # Create index() function that uses the generator
            def index_func(
                component_type: str,
                format: str = "list",
                limit: int | None = None,
                filter: str | None = None,
                group_by: str | None = None,
                **kwargs: Any,
            ) -> str:
                """Generate embedded section index.

                This function is available in templates as {{ index('roles') }}.

                Args:
                    component_type: Type of components (roles, plugins, etc.)
                    format: Visualization style (list, table, tree)
                    limit: Maximum items to show
                    filter: Filter expression (e.g., 'tag:database')
                    group_by: Field to group by (e.g., 'metadata.plugin_type')
                    **kwargs: Additional context variables (items, etc.)

                Returns:
                    Rendered section index HTML/Markdown
                """
                # Get items from kwargs (passed from template context)
                items = kwargs.get("items", [])

                # Generate section index using the generator
                section_index = index_generator.generate_section_index(
                    component_type=component_type,
                    items=items,
                    format=format,
                    limit=limit,
                    group_by=group_by,
                    filter_expression=filter,
                )

                # Render inline (without template engine to avoid recursion)
                return section_index.render_inline()

            environment.globals["index"] = index_func

        return cls(environment)

    def get_template(self, template_name: str) -> "Template":
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
