"""
Domain model for Ansible task tags.

Following Constitution Article X (Domain-Driven Design):
- Value Object: Tag (immutable)
- Ubiquitous Language: Ansible task tag terminology
"""

from typing import Optional

from pydantic import BaseModel, Field


class Tag(BaseModel):
    """
    Value Object: Ansible task tag.
    
    Immutable representation of a tag used in task definitions.
    Tags enable selective playbook execution.
    """

    name: str = Field(..., description="Tag name (e.g., 'install', 'configure')")
    description: Optional[str] = Field(
        None, description="Tag description from @tag annotation"
    )
    usage_count: int = Field(
        default=1, description="Number of tasks using this tag", ge=1
    )

    model_config = {"frozen": True}

    def is_documented(self) -> bool:
        """Check if tag has description from @tag annotation."""
        return self.description is not None

    def __hash__(self) -> int:
        """Hash based on name for set operations."""
        return hash(self.name)
