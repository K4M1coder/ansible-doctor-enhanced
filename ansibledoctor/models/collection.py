"""Ansible collection model.

This module defines the AnsibleCollection aggregate root following
Domain-Driven Design principles. It coordinates GalaxyMetadata,
roles, and plugins within a collection.

Following Constitution Article X (DDD): Aggregate Root pattern with
GalaxyMetadata, roles, and plugins as children.
"""

from typing import Dict, List, Union

from pydantic import BaseModel, Field, field_validator

from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.plugin import Plugin, PluginType
from ansibledoctor.models.role import AnsibleRole


class PlaybookInfo(BaseModel):
    """
    Playbook metadata.

    Represents a discovered playbook within the collection.

    Attributes:
        name: Playbook name (derived from filename or content)
        path: Absolute path to the playbook file
        description: Optional description extracted from playbook
        tags: List of tags found in the playbook
    """

    name: str = Field(..., description="Playbook name")
    path: str = Field(..., description="Absolute path to playbook file")
    description: str | None = Field(None, description="Optional description")
    tags: List[str] = Field(default_factory=list, description="Tags found in playbook")


class AnsibleCollection(BaseModel):
    """
    Ansible Collection aggregate root.

    Represents a complete Ansible collection with metadata, roles, and plugins.
    This is the aggregate root in DDD terms - all modifications to roles and
    plugins go through this collection model.

    Attributes:
        metadata: Galaxy metadata (namespace, name, version, etc.)
        roles: List of role names within the collection
        plugins: Dictionary mapping plugin types to lists of plugin file names

    Example:
        >>> metadata = GalaxyMetadata(
        ...     namespace="my_ns",
        ...     name="my_coll",
        ...     version="1.0.0",
        ...     authors=["Author"],
        ...     dependencies={}
        ... )
        >>> collection = AnsibleCollection(
        ...     metadata=metadata,
        ...     roles=["web_server", "database"],
        ...     plugins={PluginType.MODULE: ["my_module.py"]}
        ... )
        >>> collection.fqcn
        'my_ns.my_coll'
    """

    metadata: GalaxyMetadata = Field(
        ..., description="Galaxy metadata (namespace, name, version, authors, dependencies)"
    )
    roles: List[Union[str, AnsibleRole]] = Field(
        default_factory=list, description="List of role names or full role objects"
    )
    plugins: Dict[PluginType, List[Union[str, Plugin]]] = Field(
        default_factory=dict,
        description="Dictionary mapping plugin types to plugin file paths or objects",
    )
    playbooks: List[PlaybookInfo] = Field(
        default_factory=list, description="List of discovered playbooks"
    )
    existing_docs: ExistingDocs | None = Field(
        None, description="Existing documentation files (README, CHANGELOG, etc.)"
    )

    @field_validator("metadata")
    @classmethod
    def validate_no_self_dependency(cls, metadata: GalaxyMetadata) -> GalaxyMetadata:
        """
        Validate that collection doesn't depend on itself (circular reference).

        Args:
            metadata: GalaxyMetadata to validate

        Returns:
            Validated metadata

        Raises:
            ValueError: If collection has self-dependency
        """
        fqcn = metadata.fqcn
        if fqcn in metadata.dependencies:
            raise ValueError(
                f"Collection cannot depend on itself: {fqcn} found in dependencies. "
                "Remove self-reference from galaxy.yml dependencies."
            )
        return metadata

    @property
    def fqcn(self) -> str:
        """
        Get Fully Qualified Collection Name (delegates to metadata).

        Returns:
            FQCN in format "namespace.name"
        """
        return self.metadata.fqcn

    def list_roles(self) -> List[str]:
        """
        Get list of role names in collection.

        Returns:
            List of role names
        """
        return [r.name if isinstance(r, AnsibleRole) else r for r in self.roles]

    def list_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """
        Get list of plugin names for a specific type.

        Args:
            plugin_type: Type of plugin to list

        Returns:
            List of plugin names for the given type, empty list if none
        """
        plugins = self.plugins.get(plugin_type, [])
        return [p.name if isinstance(p, Plugin) else p for p in plugins]

    def __str__(self) -> str:
        """Return human-readable representation."""
        role_count = len(self.roles)
        plugin_count = sum(len(plugins) for plugins in self.plugins.values())
        return (
            f"Collection {self.fqcn} v{self.metadata.version} "
            f"({role_count} roles, {plugin_count} plugins)"
        )

    def __repr__(self) -> str:
        """Return detailed representation."""
        return (
            f"AnsibleCollection(fqcn='{self.fqcn}', "
            f"version='{self.metadata.version}', "
            f"roles={len(self.roles)}, plugins={len(self.plugins)})"
        )
