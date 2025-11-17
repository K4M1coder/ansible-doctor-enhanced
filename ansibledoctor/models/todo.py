"""
TodoItem value object for @todo annotations.

Represents a TODO comment found in Ansible role files with file location
and optional priority information.

This is a Value Object in DDD terms - immutable and defined by its attributes.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TodoItem(BaseModel):
    """
    Represents a @todo annotation found in role files.

    TODOs document planned improvements, known limitations, or technical debt.
    This model captures the todo description and its location for documentation.

    Attributes:
        description: The TODO description text
        file_path: Relative path to the file containing the TODO
        line_number: Line number where the TODO appears
        priority: Optional priority level (low, medium, high, critical)
    """

    description: str = Field(..., min_length=1, description="TODO description text")
    file_path: str = Field(..., min_length=1, description="File path relative to role root")
    line_number: int = Field(..., ge=1, description="Line number in file (1-indexed)")
    priority: Optional[Literal["low", "medium", "high", "critical"]] = Field(
        None, description="Priority level for the TODO"
    )

    model_config = {
        "frozen": True,  # Immutable value object
        "str_strip_whitespace": True,  # Clean up string inputs
    }

    @field_validator("description", "file_path")
    @classmethod
    def string_cannot_be_empty(cls, v: str) -> str:
        """Validate that string fields are not empty after stripping."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v: Optional[str]) -> Optional[str]:
        """Normalize priority to lowercase if provided."""
        if v is not None and isinstance(v, str):
            return v.lower()
        return v

    def get_location(self) -> str:
        """Get formatted file location as file:line."""
        return f"{self.file_path}:{self.line_number}"

    def __str__(self) -> str:
        """Readable string representation."""
        location = self.get_location()
        if self.priority:
            return f"[{self.priority.upper()}] {self.description} ({location})"
        return f"{self.description} ({location})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"TodoItem({self.file_path}:{self.line_number}, priority={self.priority})"
