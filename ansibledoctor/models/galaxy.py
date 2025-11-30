"""Galaxy metadata model for Ansible collections.

This module defines the GalaxyMetadata model following Ansible Galaxy
schema version 1.0.0 (Ansible 2.9+ standard). Only required fields are
included in v0.5.0; optional fields deferred to v0.6.0.

Following Constitution Article X (DDD): Value Object pattern for immutable
collection metadata.
"""

from typing import Dict, List

from packaging.version import Version
from pydantic import BaseModel, Field, field_validator


class GalaxyMetadata(BaseModel):
    """
    Galaxy metadata from galaxy.yml (schema 1.0.0).

    Represents required fields only per v0.5.0 scope. Optional fields
    (tags, license, repository, readme, homepage, issues, documentation)
    are deferred to v0.6.0.

    This is a Value Object (DDD pattern): immutable and compared by value.

    Attributes:
        namespace: Collection namespace (lowercase alphanumeric with underscores)
        name: Collection name (lowercase alphanumeric with underscores)
        version: Semantic version string
        authors: List of author names/emails
        dependencies: Dict mapping collection FQCN to version constraint

    Example:
        >>> metadata = GalaxyMetadata(
        ...     namespace="my_namespace",
        ...     name="my_collection",
        ...     version="1.0.0",
        ...     authors=["Author Name <author@example.com>"],
        ...     dependencies={}
        ... )
        >>> metadata.fqcn
        'my_namespace.my_collection'
    """

    namespace: str = Field(
        ...,
        description="Collection namespace (lowercase alphanumeric with underscores)",
        pattern=r"^[a-z0-9_]+$",
    )
    name: str = Field(
        ...,
        description="Collection name (lowercase alphanumeric with underscores)",
        pattern=r"^[a-z0-9_]+$",
    )
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
    authors: List[str] = Field(default_factory=list, description="List of author names/emails")
    dependencies: Dict[str, str] = Field(
        default_factory=dict, description="Collection dependencies with version constraints"
    )

    model_config = {"frozen": True}  # Immutable value object

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """
        Validate version follows semantic versioning.

        Args:
            v: Version string

        Returns:
            Validated version string

        Raises:
            ValueError: If version is not valid semantic version
        """
        try:
            Version(v)  # Validate using packaging.version
        except Exception as e:
            raise ValueError(f"Invalid semantic version '{v}': {e}") from e
        return v

    @property
    def fqcn(self) -> str:
        """
        Get Fully Qualified Collection Name (FQCN).

        Returns:
            FQCN in format "namespace.name"

        Example:
            >>> metadata.fqcn
            'my_namespace.my_collection'
        """
        return f"{self.namespace}.{self.name}"

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.fqcn} v{self.version}"

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"GalaxyMetadata(namespace='{self.namespace}', "
            f"name='{self.name}', version='{self.version}')"
        )
