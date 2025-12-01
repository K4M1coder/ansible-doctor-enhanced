"""Protocols for documentation generator components."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Import types for static type-checking only to satisfy linters/types
    from jinja2 import Template

    from ansibledoctor.generator.models import OutputFormat


@runtime_checkable
class DocumentRenderer(Protocol):
    """Protocol for rendering content in different output formats.

    Implementations must provide methods to render content, escape special
    characters, and format code blocks according to the target format's
    syntax rules.

    Example:
        >>> class MarkdownRenderer:
        ...     def render(self, content: str) -> str:
        ...         return content
        ...     def escape(self, text: str) -> str:
        ...         return text.replace('[', r'\\[')
        ...     def code_block(self, code: str, language: str = "") -> str:
        ...         return f"```{language}\\n{code}\\n```"
    """

    def render(self, content: str) -> str:
        """Render content in the target format.

        Args:
            content: Raw content to render

        Returns:
            Rendered content as string

        Example:
            >>> renderer.render("# Hello World")
            '<h1>Hello World</h1>'
        """
        ...

    def escape(self, text: str) -> str:
        """Escape special characters for the target format.

        Args:
            text: Text containing special characters

        Returns:
            Escaped text safe for inclusion in rendered output

        Example:
            >>> renderer.escape("<tag>")
            '&lt;tag&gt;'
        """
        ...

    def code_block(self, code: str, language: str = "") -> str:
        """Format code block in the target format.

        Args:
            code: Source code to format
            language: Programming language for syntax highlighting

        Returns:
            Formatted code block

        Example:
            >>> renderer.code_block("print('hi')", "python")
            '```python\\nprint(\\'hi\\')\\n```'
        """
        ...


@runtime_checkable
class TemplateLoader(Protocol):
    """Protocol for loading and managing templates.

    Implementations must provide template discovery across multiple
    levels (custom, project, user, embedded) and validation.

    Example:
        >>> loader = FileSystemTemplateLoader()
        >>> template = loader.load_template("role.md.j2", OutputFormat.MARKDOWN)
        >>> template.render(context)
    """

    def load_template(self, template_name: str, output_format: "OutputFormat") -> "Template":
        """Load template by name and format.

        Args:
            template_name: Name of template file (e.g., 'role.md.j2')
            output_format: Target output format

        Returns:
            Loaded template object ready for rendering

        Raises:
            TemplateNotFoundError: If template not found in any search path
            TemplateValidationError: If template has syntax errors
        """
        ...

    def discover_templates(self, output_format: "OutputFormat") -> list[str]:
        """Discover all available templates for a format.

        Args:
            output_format: Target output format

        Returns:
            List of template names
        """
        ...

    def validate_template(self, template_name: str) -> bool:
        """Validate template syntax without rendering.

        Args:
            template_name: Template to validate

        Returns:
            True if template is valid

        Raises:
            TemplateValidationError: If template has syntax errors
        """
        ...
