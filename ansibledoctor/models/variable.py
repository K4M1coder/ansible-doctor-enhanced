"""
Domain models for Ansible role variables.

Following Constitution Article X (Domain-Driven Design):
- Value Object: Variable (immutable)
- Type inference: Automatic detection of variable types from YAML values
- Ubiquitous Language: Uses Ansible variable terminology
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class VariableType(str, Enum):
    """
    Enumeration of variable types inferred from YAML values.

    Follows Ansible/YAML type system.
    """

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    NULL = "null"


class Variable(BaseModel):
    """
    Value Object: Ansible role variable definition.

    Immutable representation of a variable from defaults/main.yml or vars/main.yml.
    Part of the AnsibleRole aggregate.
    """

    name: str = Field(..., description="Variable name")
    value: Any = Field(..., description="Variable value (can be any YAML type)")
    type: VariableType = Field(..., description="Inferred variable type")

    source: str = Field(..., description="Source file (defaults or vars)")

    # Annotation attributes (from @var annotations)
    description: Optional[str] = Field(None, description="Variable description from @var")
    example: Optional[Any] = Field(None, description="Usage example from annotation")
    required: Optional[bool] = Field(None, description="Whether variable is required")
    deprecated: Optional[Any] = Field(
        None, description="Deprecation message if variable is deprecated"
    )
    default: Optional[str] = Field(
        None, description="Default value description (may differ from actual value)"
    )

    # Context for debugging
    file_path: Optional[str] = Field(None, description="Full file path for context")
    line_number: Optional[int] = Field(None, description="Line number in file")

    model_config = {"frozen": True}

    def is_complex(self) -> bool:
        """Check if variable is a complex type (dict or list)."""
        return self.type in (VariableType.DICT, VariableType.LIST)

    def is_deprecated(self) -> bool:
        """Check if variable is marked as deprecated."""
        return self.deprecated is not None

    def is_documented(self) -> bool:
        """Check if variable has annotation documentation."""
        return self.description is not None

    @staticmethod
    def infer_type(value: Any) -> VariableType:
        """
        Infer variable type from Python/YAML value.

        Args:
            value: Variable value from YAML

        Returns:
            VariableType enum value

        Examples:
            >>> Variable.infer_type("hello")
            VariableType.STRING
            >>> Variable.infer_type(42)
            VariableType.NUMBER
            >>> Variable.infer_type([1, 2, 3])
            VariableType.LIST
        """
        if value is None:
            return VariableType.NULL
        elif isinstance(value, bool):  # Must check bool before int (bool is subclass of int)
            return VariableType.BOOLEAN
        elif isinstance(value, (int, float)):
            return VariableType.NUMBER
        elif isinstance(value, str):
            return VariableType.STRING
        elif isinstance(value, list):
            return VariableType.LIST
        elif isinstance(value, dict):
            return VariableType.DICT
        else:
            # Fallback for unknown types
            return VariableType.STRING
