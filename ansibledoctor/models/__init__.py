"""
Models package for Pydantic domain models.

Following Constitution Article X (Domain-Driven Design):
- Aggregate Root: AnsibleRole, AnsibleCollection
- Value Objects: Variable, Tag, Annotation, Example, RoleMetadata, GalaxyMetadata
- Entities: TodoItem (identity by location)
"""

from ansibledoctor.models.annotation import Annotation, AnnotationType
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.example import Example
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.metadata import ArgumentSpec, Dependency, Platform, RoleMetadata
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.models.tag import Tag
from ansibledoctor.models.todo import TodoItem
from ansibledoctor.models.variable import Variable, VariableType

__all__ = [
    # Aggregate Roots
    "AnsibleRole",
    "AnsibleCollection",
    # Metadata
    "RoleMetadata",
    "GalaxyMetadata",
    "Platform",
    "Dependency",
    "ArgumentSpec",
    # Variables
    "Variable",
    "VariableType",
    # Annotations
    "Annotation",
    "AnnotationType",
    "TodoItem",
    "Example",
    # Tags
    "Tag",
]
