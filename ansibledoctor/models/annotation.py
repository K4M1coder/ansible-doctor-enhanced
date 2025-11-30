"""
Domain models for annotations, TODOs, and examples.

Following Constitution Article X (Domain-Driven Design):
- Value Objects: Annotation, TodoItem, Example (immutable)
- Ubiquitous Language: @var, @tag, @todo, @example annotation types from ansible-doctor
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnnotationType(str, Enum):
    """
    Enumeration of supported annotation types.

    Follows ansible-doctor annotation syntax conventions.
    """

    VAR = "var"  # Variable documentation: @var name: description
    TAG = "tag"  # Task tag description: @tag install: Installs packages
    TODO = "todo"  # TODO item: @todo: Implement feature X
    EXAMPLE = "example"  # Code example: @example: > ... @end
    META = "meta"  # Meta information: @meta: author: John Doe


class Annotation(BaseModel):
    """
    Value Object: Inline documentation annotation.

    Immutable representation of a comment-based annotation in Ansible files.
    Can be associated with variables, tags, or standalone.
    """

    type: AnnotationType = Field(..., description="Annotation type (@var, @tag, etc.)")
    key: Optional[str] = Field(None, description="Associated key (variable name, tag name, etc.)")
    content: str = Field(..., description="Annotation content/description")

    # Context for traceability
    file_path: str = Field(..., description="Source file path")
    line_number: int = Field(..., description="Line number in file")

    # Parsed attributes (for JSON-format annotations)
    parsed_attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured attributes from JSON annotations",
    )

    model_config = {"frozen": True}

    def has_attribute(self, attr: str) -> bool:
        """Check if annotation has a parsed attribute."""
        return attr in self.parsed_attributes

    def get_attribute(self, attr: str, default: Any = None) -> Any:
        """Get parsed attribute value with optional default."""
        return self.parsed_attributes.get(attr, default)


class TodoItem(BaseModel):
    """
    Entity: TODO item with location tracking.

    Tracked by location (file_path + line_number) for identity.
    """

    description: str = Field(..., description="TODO description")
    file_path: str = Field(..., description="Source file path")
    line_number: int = Field(..., description="Line number in file")
    priority: Optional[str] = Field(None, description="Priority (high, medium, low)")

    model_config = {"frozen": True}

    def __hash__(self) -> int:
        """Hash based on location for set operations."""
        return hash((self.file_path, self.line_number))


class Example(BaseModel):
    """
    Value Object: Usage example code block.

    Immutable representation of example code with context.
    """

    title: Optional[str] = Field(None, description="Example title or description")
    code: str = Field(..., description="Example code content")
    language: str = Field(default="yaml", description="Code language (yaml, jinja2, etc.)")
    file_path: str = Field(..., description="Source file for context")
    line_number: int = Field(..., description="Starting line number")

    model_config = {"frozen": True}

    def get_preview(self, max_lines: int = 3) -> str:
        """
        Get preview of example code (first N lines).

        Args:
            max_lines: Maximum lines to include in preview

        Returns:
            Truncated code preview
        """
        lines = self.code.split("\n")
        if len(lines) <= max_lines:
            return self.code
        return "\n".join(lines[:max_lines]) + "\n..."
