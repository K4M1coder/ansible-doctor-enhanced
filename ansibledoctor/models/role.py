"""
Domain model for Ansible Role aggregate root.

Following Constitution Article X (Domain-Driven Design):
- Aggregate Root: AnsibleRole contains all role components
- Enforces consistency boundaries and invariants
- All modifications go through the root
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ansibledoctor.models.annotation import Annotation
from ansibledoctor.models.example import Example
from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.models.handler import Handler
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.tag import Tag
from ansibledoctor.models.todo import TodoItem
from ansibledoctor.models.variable import Variable


class AnsibleRole(BaseModel):
    """
    Aggregate Root: Complete Ansible role with all components.

    This is the root entity in the Parsing Context bounded context.
    All role components (metadata, variables, tasks, annotations) are accessed
    through this aggregate to maintain consistency.

    Invariants enforced:
    - Variable names are unique within the role
    - Path must be a valid directory
    - Role name matches directory name
    """

    # Identity
    path: Path = Field(..., description="Absolute path to role directory")
    name: str = Field(..., description="Role name (directory name)")

    # Components (Value Objects and Entities)
    metadata: RoleMetadata = Field(
        default_factory=RoleMetadata, description="Galaxy metadata from meta/main.yml"
    )

    variables: list[Variable] = Field(
        default_factory=list, description="Variables from defaults/ and vars/"
    )

    tags: list[Tag] = Field(default_factory=list, description="Task tags discovered in tasks/")

    annotations: list[Annotation] = Field(
        default_factory=list, description="All annotations found in role files"
    )

    todos: list[TodoItem] = Field(
        default_factory=list, description="TODO items from @todo annotations"
    )

    examples: list[Example] = Field(
        default_factory=list, description="Code examples from @example annotations"
    )

    handlers: list[Handler] = Field(
        default_factory=list, description="Handler definitions from handlers/"
    )

    existing_docs: ExistingDocs = Field(
        default_factory=ExistingDocs,
        description="Existing documentation (README, CHANGELOG, LICENSE, etc.)"
    )

    # Parsing metadata
    parse_errors: list[str] = Field(
        default_factory=list, description="Non-fatal errors encountered during parsing"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure role name is not empty."""
        if not v or not v.strip():
            raise ValueError("Role name cannot be empty")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path_exists(cls, v: Path) -> Path:
        """Ensure role path is absolute."""
        if not v.is_absolute():
            raise ValueError(f"Role path must be absolute: {v}")
        return v

    # Rich behavior methods (not anemic model)

    def get_variable_by_name(self, name: str) -> Optional[Variable]:
        """Find variable by name."""
        for var in self.variables:
            if var.name == name:
                return var
        return None

    def get_variables_by_source(self, source: str) -> list[Variable]:
        """Get all variables from specific source (defaults or vars)."""
        return [v for v in self.variables if v.source == source]

    def get_documented_variables(self) -> list[Variable]:
        """Get variables that have @var annotation documentation."""
        return [v for v in self.variables if v.is_documented()]

    def get_deprecated_variables(self) -> list[Variable]:
        """Get variables marked as deprecated."""
        return [v for v in self.variables if v.is_deprecated()]

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Find tag by name."""
        for tag in self.tags:
            if tag.name == name:
                return tag
        return None

    def get_documented_tags(self) -> list[Tag]:
        """Get tags with @tag annotation descriptions."""
        return [t for t in self.tags if t.is_documented()]

    def has_metadata(self) -> bool:
        """Check if role has metadata (author or description)."""
        return bool(self.metadata.author or self.metadata.description)

    def has_dependencies(self) -> bool:
        """Check if role has dependencies."""
        return self.metadata.has_dependencies()

    def get_statistics(self) -> dict[str, int]:
        """
        Get role statistics summary.

        Returns:
            Dictionary with counts of variables, tags, todos, examples, etc.
        """
        return {
            "variables": len(self.variables),
            "documented_variables": len(self.get_documented_variables()),
            "deprecated_variables": len(self.get_deprecated_variables()),
            "tags": len(self.tags),
            "documented_tags": len(self.get_documented_tags()),
            "todos": len(self.todos),
            "examples": len(self.examples),
            "annotations": len(self.annotations),
            "dependencies": len(self.metadata.dependencies),
            "parse_errors": len(self.parse_errors),
        }

    def __str__(self) -> str:
        """Human-readable role representation."""
        stats = self.get_statistics()
        return (
            f"AnsibleRole(name={self.name}, "
            f"variables={stats['variables']}, "
            f"tags={stats['tags']}, "
            f"todos={stats['todos']})"
        )
