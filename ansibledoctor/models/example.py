"""
Example value object for @example code blocks.

Represents an example code block found in Ansible role files, typically
demonstrating usage patterns or configuration examples.

This is a Value Object in DDD terms - immutable and defined by its attributes.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Example(BaseModel):
    """
    Represents a @example code block found in role files.

    Examples demonstrate role usage, configuration patterns, or specific
    implementation details. They are extracted from @example...@end blocks.

    Attributes:
        title: Brief title describing the example
        code: The example code content
        description: Optional detailed description of the example
        language: Programming/markup language (yaml, jinja2, bash, python, json)
    """

    title: str = Field(..., min_length=1, description="Example title")
    code: str = Field(..., min_length=1, description="Example code content")
    description: Optional[str] = Field(None, description="Detailed example description")
    language: str = Field(
        default="yaml", description="Code language (yaml, jinja2, bash, python, json)"
    )

    model_config = {
        "frozen": True,  # Immutable value object
    }

    @field_validator("title")
    @classmethod
    def title_cannot_be_empty(cls, v: str) -> str:
        """Validate that title is not empty after stripping."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty")
        return stripped

    @field_validator("code")
    @classmethod
    def code_cannot_be_empty(cls, v: str) -> str:
        """Validate that code is not empty, preserve internal whitespace."""
        if not v or not v.strip():
            raise ValueError("Code cannot be empty")
        # Keep code as-is to preserve indentation and formatting
        return v

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language(cls, v: str) -> str:
        """Normalize language identifier to lowercase and handle aliases."""
        if v is not None and isinstance(v, str):
            lang = v.lower().strip()
            # Normalize yml to yaml for consistency
            if lang == "yml":
                return "yaml"
            return lang
        return "yaml"  # default

    def __str__(self) -> str:
        """Readable string representation."""
        if self.description:
            return f"{self.title}: {self.description}"
        return self.title

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Example(title={self.title!r}, language={self.language!r})"
