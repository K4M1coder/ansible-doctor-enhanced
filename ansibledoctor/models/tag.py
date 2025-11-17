"""
Domain model for Ansible task tags.

Following Constitution Article X (Domain-Driven Design):
- Value Object: Tag (immutable)
- Ubiquitous Language: Ansible task tag terminology

Phase 8 US3: Enhanced with file location tracking and improved validation.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Tag(BaseModel):
    """
    Value Object: Ansible task tag.
    
    Immutable representation of a tag used in task definitions.
    Tags enable selective playbook execution.
    
    Attributes:
        name: The tag identifier (e.g., 'install', 'configure', 'deploy')
        description: Optional description from @tag annotation
        usage_count: Number of times this tag appears in the role
        file_locations: List of file:line references where tag is used
    """

    name: str = Field(
        ..., min_length=1, description="Tag name (e.g., 'install', 'configure')"
    )
    description: Optional[str] = Field(
        None, description="Tag description from @tag annotation"
    )
    usage_count: int = Field(
        default=1, description="Number of tasks using this tag", ge=1
    )
    file_locations: list[str] = Field(
        default_factory=list,
        description="File:line references where tag appears (e.g., 'tasks/main.yml:10')",
    )

    model_config = {"frozen": True, "str_strip_whitespace": True}

    @field_validator("name")
    @classmethod
    def name_cannot_be_empty(cls, v: str) -> str:
        """Validate that tag name is not empty after stripping."""
        if not v or not v.strip():
            raise ValueError("Tag name cannot be empty")
        return v.strip()

    def is_documented(self) -> bool:
        """Check if tag has description from @tag annotation."""
        return self.description is not None

    def __eq__(self, other: object) -> bool:
        """Tags are equal if they have the same name."""
        if not isinstance(other, Tag):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        """Hash based on name for set operations."""
        return hash(self.name)

    def __str__(self) -> str:
        """Readable string representation."""
        if self.description:
            return f"{self.name}: {self.description}"
        return self.name

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Tag(name={self.name!r}, usage_count={self.usage_count})"
