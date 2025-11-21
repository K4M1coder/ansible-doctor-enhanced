"""CollectionRole model for roles within Ansible collections (T129-T135).

This module defines CollectionRole, extending AnsibleRole with collection-
specific attributes like collection FQCN and full role name computation.

Following Constitution Article X (DDD): CollectionRole is an Entity within
the Collection aggregate, extending the Role aggregate root with collection
context.
"""

from pathlib import Path

from pydantic import Field

from ansibledoctor.models.role import AnsibleRole


class CollectionRole(AnsibleRole):
    """
    Role within an Ansible collection.
    
    Extends AnsibleRole with collection-specific attributes. A collection
    role is identical to a standalone role but belongs to a collection and
    has a fully-qualified collection name (FQCN).
    
    The full role name format is: namespace.collection.role_name
    This format is used in playbooks to reference collection roles:
        roles:
          - namespace.collection.role_name
    
    Attributes:
        collection_fqcn: Fully-qualified collection name (namespace.name)
        full_role_name: Computed property returning "fqcn.role_name"
    
    Example:
        >>> role = CollectionRole(
        ...     path=Path("/collections/community/general/roles/docker"),
        ...     name="docker",
        ...     collection_fqcn="community.general",
        ... )
        >>> print(role.full_role_name)
        community.general.docker
    """
    
    # Collection-specific field
    collection_fqcn: str = Field(
        ...,
        description="Fully-qualified collection name (namespace.collection_name)",
        examples=["community.general", "ansible.posix", "namespace.collection"],
    )
    
    @property
    def full_role_name(self) -> str:
        """
        Compute full role name in collection FQCN format.
        
        Returns the role's fully-qualified name used in playbooks and
        dependencies: "namespace.collection.role_name"
        
        Returns:
            Full role name string (e.g., "community.general.docker")
        
        Example:
            >>> role = CollectionRole(
            ...     path=Path("/collections/ansible/posix/roles/firewall"),
            ...     name="firewall",
            ...     collection_fqcn="ansible.posix",
            ... )
            >>> role.full_role_name
            'ansible.posix.firewall'
        """
        return f"{self.collection_fqcn}.{self.name}"
    
    def __str__(self) -> str:
        """
        Human-readable CollectionRole representation.
        
        Returns:
            String showing full role name and statistics
        
        Example:
            >>> role = CollectionRole(...)
            >>> print(role)
            CollectionRole(full_name=community.general.docker, variables=10, tags=5)
        """
        stats = self.get_statistics()
        return (
            f"CollectionRole(full_name={self.full_role_name}, "
            f"variables={stats['variables']}, "
            f"tags={stats['tags']}, "
            f"todos={stats['todos']})"
        )
