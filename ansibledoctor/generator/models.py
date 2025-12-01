"""Data models for documentation generator."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.models.role import AnsibleRole


@runtime_checkable
class HasBreadcrumb(Protocol):
    """Protocol for objects that can provide breadcrumb navigation."""

    def get_breadcrumb(self) -> list[Any]:
        """Get breadcrumb trail."""
        ...

    def get_siblings(self) -> list[Any]:
        """Get sibling components."""
        ...


@dataclass
class RenderResult:
    """Result of a documentation rendering operation.

    Contains the rendered content along with metadata about the
    rendering process (format, timestamp, source file, etc.).

    Attributes:
        content: Rendered documentation as string
        output_format: Format of rendered content (MARKDOWN, HTML, RST)
        source_file: Path to source role directory
        rendered_at: Timestamp when rendering completed
        template_name: Name of template used for rendering
        metadata: Additional metadata as key-value pairs

    Example:
        >>> result = RenderResult(
        ...     content="# My Role\\n\\nDocumentation...",
        ...     output_format=OutputFormat.MARKDOWN,
        ...     source_file="/path/to/role",
        ...     template_name="role.md.j2"
        ... )
        >>> result.file_extension
        '.md'
    """

    content: str
    output_format: OutputFormat
    source_file: str
    rendered_at: datetime = field(default_factory=datetime.now)
    template_name: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def file_extension(self) -> str:
        """Get file extension for this output format.

        Returns:
            File extension with leading dot (e.g., '.md')
        """
        return self.output_format.file_extension

    @property
    def size_bytes(self) -> int:
        """Get size of rendered content in bytes.

        Returns:
            Size in bytes (UTF-8 encoding)
        """
        return len(self.content.encode("utf-8"))

    @property
    def line_count(self) -> int:
        """Get number of lines in rendered content.

        Returns:
            Number of lines
        """
        return self.content.count("\n") + 1 if self.content else 0

    def save_to_file(self, output_path: str) -> None:
        """Save rendered content to file.

        Args:
            output_path: Path where content should be saved

        Raises:
            IOError: If file cannot be written
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.content)


@dataclass
class TemplateContext:
    """Context data passed to templates for rendering.

    Contains all information needed to render role documentation,
    including role data, configuration, and computed properties.

    Attributes:
        role: Parsed Ansible role data
        output_format: Target output format
        generation_date: Date of documentation generation
        generator_version: Version of ansible-doctor-enhanced
        custom_data: Additional custom data for templates

    Example:
        >>> from ansibledoctor import __version__
        >>> context = TemplateContext(
        ...     role=my_role,
        ...     output_format=OutputFormat.MARKDOWN,
        ...     generator_version=__version__
        ... )
        >>> context.has_variables
        True
        >>> context.variable_count
        5
    """

    role: AnsibleRole
    output_format: OutputFormat
    generator_version: str  # Must be passed explicitly from __version__
    generation_date: datetime = field(default_factory=datetime.now)
    custom_data: dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    hierarchical_context: HasBreadcrumb | None = None

    @property
    def role_name(self) -> str:
        """Get role name from role.

        Returns:
            Role name or 'Unnamed Role' if not set
        """
        return self.role.name or "Unnamed Role"

    @property
    def role_description(self) -> str:
        """Get role description from metadata.

        Returns:
            Role description or empty string if not set
        """
        return self.role.metadata.description or ""

    @property
    def has_variables(self) -> bool:
        """Check if role has any variables.

        Returns:
            True if role has variables
        """
        return len(self.role.variables) > 0

    @property
    def variable_count(self) -> int:
        """Get number of variables in role.

        Returns:
            Number of variables
        """
        return len(self.role.variables)

    @property
    def has_tags(self) -> bool:
        """Check if role has any tags.

        Returns:
            True if role has tags
        """
        return len(self.role.tags) > 0

    @property
    def tag_count(self) -> int:
        """Get number of unique tags in role.

        Returns:
            Number of tags
        """
        return len(self.role.tags)

    @property
    def has_todos(self) -> bool:
        """Check if role has any TODO items.

        Returns:
            True if role has TODOs
        """
        return len(self.role.todos) > 0

    @property
    def todo_count(self) -> int:
        """Get number of TODO items in role.

        Returns:
            Number of TODOs
        """
        return len(self.role.todos)

    @property
    def has_examples(self) -> bool:
        """Check if role has any example code blocks.

        Returns:
            True if role has examples
        """
        return len(self.role.examples) > 0

    @property
    def example_count(self) -> int:
        """Get number of example code blocks in role.

        Returns:
            Number of examples
        """
        return len(self.role.examples)

    @property
    def format_name(self) -> str:
        """Get human-readable format name.

        Returns:
            Format name (e.g., 'Markdown', 'HTML', 'RST')
        """
        format_names = {
            OutputFormat.MARKDOWN: "Markdown",
            OutputFormat.HTML: "HTML",
            OutputFormat.RST: "reStructuredText",
        }
        return format_names.get(self.output_format, self.output_format.value)

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for template rendering.

        Returns:
            Dictionary with all context data and computed properties
        """
        result = {
            "role": self.role,
            "role_name": self.role_name,
            "role_description": self.role_description,
            "output_format": self.output_format,
            "format_name": self.format_name,
            "generation_date": self.generation_date,
            "generator_version": self.generator_version,
            "has_variables": self.has_variables,
            "variable_count": self.variable_count,
            "has_tags": self.has_tags,
            "tag_count": self.tag_count,
            "has_todos": self.has_todos,
            "todo_count": self.todo_count,
            "has_examples": self.has_examples,
            "example_count": self.example_count,
            "custom_data": self.custom_data,
            "language": self.language,
        }

        # Add hierarchical context for breadcrumb and sibling navigation
        if self.hierarchical_context is not None:
            result["context"] = {
                "breadcrumb": self.hierarchical_context.get_breadcrumb(),
                "siblings": self.hierarchical_context.get_siblings(),
            }

        return result
