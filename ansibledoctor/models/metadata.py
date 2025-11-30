"""
Domain models for Ansible role metadata.

Following Constitution Article X (Domain-Driven Design):
- Value Objects: RoleMetadata, Platform, Dependency, ArgumentSpec (immutable)
- Ubiquitous Language: Uses Ansible terminology (galaxy_info, platforms, argument_specs)
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Platform(BaseModel):
    """
    Value Object: Supported platform from meta/main.yml galaxy_info.

    Immutable representation of an OS platform and versions supported by the role.
    """

    name: str = Field(..., description="Platform name (e.g., 'Ubuntu', 'EL')")
    versions: list[str] = Field(
        default_factory=list, description="Supported versions (e.g., ['20.04', '22.04'])"
    )

    model_config = {"frozen": True}  # Value Object immutability


class Dependency(BaseModel):
    """
    Value Object: Role dependency from meta/main.yml.

    Immutable representation of a dependency on another Ansible role.
    """

    name: str = Field(..., description="Dependency role name")
    version: Optional[str] = Field(None, description="Required version or version constraint")
    source: Optional[str] = Field(None, description="Source (galaxy, git, etc.)")

    model_config = {"frozen": True}


class ArgumentSpec(BaseModel):
    """
    Value Object: Argument specification from meta/argument_specs.yml (Ansible 2.11+).

    Immutable representation of role parameters following Ansible argument_specs schema.
    """

    entry_point: str = Field(
        default="main", description="Entry point name (main or alternate entry points)"
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Argument options with type, required, default, description",
    )
    short_description: Optional[str] = Field(None, description="Brief description of entry point")
    description: Optional[list[str]] = Field(None, description="Detailed multi-line description")

    model_config = {"frozen": True}


class RoleMetadata(BaseModel):
    """
    Value Object: Ansible Galaxy metadata from meta/main.yml.

    Immutable representation of role identification, authorship, and compatibility info.
    Core entity in the Parsing Context bounded context.
    """

    # Raw galaxy_info for extensibility
    galaxy_info: dict[str, Any] = Field(
        default_factory=dict, description="Raw galaxy_info dict from meta/main.yml"
    )

    # Galaxy Info (from galaxy_info section)
    author: Optional[str] = Field(None, description="Role author name")
    description: Optional[str] = Field(None, description="Role description")
    license: Optional[str] = Field(None, description="License (e.g., MIT, BSD)")
    company: Optional[str] = Field(None, description="Company or organization")

    min_ansible_version: Optional[str] = Field(
        None, description="Minimum Ansible version required (e.g., '2.9')"
    )

    platforms: list[Platform] = Field(
        default_factory=list, description="Supported platforms and versions"
    )

    galaxy_tags: list[str] = Field(default_factory=list, description="Galaxy search tags")

    # Dependencies
    dependencies: list[Dependency] = Field(default_factory=list, description="Role dependencies")

    # Argument Specs (Ansible 2.11+)
    argument_specs: dict[str, ArgumentSpec] = Field(
        default_factory=dict,
        description="Argument specifications by entry point (main, alternate)",
    )

    # Source tracking
    meta_file_path: Optional[str] = Field(None, description="Path to meta/main.yml for context")

    model_config = {"frozen": True}

    def has_dependencies(self) -> bool:
        """Check if role has any dependencies."""
        return len(self.dependencies) > 0

    def has_argument_specs(self) -> bool:
        """Check if role defines argument specifications."""
        return len(self.argument_specs) > 0

    def get_supported_platforms_summary(self) -> list[str]:
        """
        Get human-readable list of supported platforms.

        Returns:
            List like ["Ubuntu (20.04, 22.04)", "EL (8, 9)"]
        """
        return [
            f"{p.name} ({', '.join(p.versions)})" if p.versions else p.name for p in self.platforms
        ]
