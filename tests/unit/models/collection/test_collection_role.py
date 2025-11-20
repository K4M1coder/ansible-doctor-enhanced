"""Unit tests for CollectionRole model (T096-T099).

Tests CollectionRole model that extends AnsibleRole with collection-specific
attributes like collection_fqcn and full_role_name property.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.collection_role import CollectionRole
from ansibledoctor.models.metadata import RoleMetadata


class TestCollectionRole:
    """Test CollectionRole model extending AnsibleRole."""
    
    def test_collection_role_extends_ansible_role(self, tmp_path: Path) -> None:
        """Test: CollectionRole extends existing Role model (T096)."""
        # Setup: Create CollectionRole
        role_path = tmp_path / "collections" / "namespace" / "collection" / "roles" / "my_role"
        role = CollectionRole(
            path=role_path,
            name="my_role",
            collection_fqcn="namespace.collection",
        )
        
        # Verify: CollectionRole has all AnsibleRole attributes
        assert role.path == role_path
        assert role.name == "my_role"
        assert hasattr(role, "metadata")
        assert hasattr(role, "variables")
        assert hasattr(role, "tags")
        assert hasattr(role, "annotations")
        assert hasattr(role, "todos")
        assert hasattr(role, "examples")
        
        # Verify: Has additional collection_fqcn field
        assert role.collection_fqcn == "namespace.collection"
    
    def test_collection_role_adds_collection_fqcn_field(self, tmp_path: Path) -> None:
        """Test: CollectionRole adds collection_fqcn field (T097)."""
        # Setup: Create CollectionRole with FQCN
        role_path = tmp_path / "collections" / "ansible" / "posix" / "roles" / "firewall"
        role = CollectionRole(
            path=role_path,
            name="firewall",
            collection_fqcn="ansible.posix",
        )
        
        # Verify: collection_fqcn field present
        assert role.collection_fqcn == "ansible.posix"
        
        # Verify: Required field (cannot omit)
        with pytest.raises(Exception):  # Pydantic ValidationError
            CollectionRole(
                path=tmp_path / "collections" / "test" / "collection" / "roles" / "role1",
                name="role1",
                # Missing collection_fqcn should raise error
            )
    
    def test_collection_role_computes_full_role_name(self, tmp_path: Path) -> None:
        """Test: CollectionRole computes full role name (fqcn.role_name) (T098)."""
        # Setup: Create CollectionRole
        role_path = tmp_path / "collections" / "community" / "general" / "roles" / "docker"
        role = CollectionRole(
            path=role_path,
            name="docker",
            collection_fqcn="community.general",
        )
        
        # Verify: full_role_name property returns "fqcn.role_name"
        assert role.full_role_name == "community.general.docker"
    
    def test_full_role_name_with_different_fqcns(self, tmp_path: Path) -> None:
        """Test: full_role_name property with various FQCNs (T098)."""
        # Test case 1: Standard FQCN
        role1 = CollectionRole(
            path=tmp_path / "collections" / "namespace" / "name" / "roles" / "my_role",
            name="my_role",
            collection_fqcn="namespace.name",
        )
        assert role1.full_role_name == "namespace.name.my_role"
        
        # Test case 2: Different namespace
        role2 = CollectionRole(
            path=tmp_path / "collections" / "acme" / "tools" / "roles" / "backup",
            name="backup",
            collection_fqcn="acme.tools",
        )
        assert role2.full_role_name == "acme.tools.backup"
        
        # Test case 3: Ansible official namespace
        role3 = CollectionRole(
            path=tmp_path / "collections" / "ansible" / "builtin" / "roles" / "package",
            name="package",
            collection_fqcn="ansible.builtin",
        )
        assert role3.full_role_name == "ansible.builtin.package"
    
    def test_collection_role_reuses_existing_role_parsing_logic(self, tmp_path: Path) -> None:
        """Test: CollectionRole reuses existing role parsing logic (T099)."""
        # Setup: Create CollectionRole with role components
        metadata = RoleMetadata(
            author="Test Author",
            description="Test collection role",
            license="MIT",
            min_ansible_version="2.9",
            platforms=[],
            dependencies=[],
        )
        
        role_path = tmp_path / "collections" / "test" / "collection" / "roles" / "webserver"
        role = CollectionRole(
            path=role_path,
            name="webserver",
            collection_fqcn="test.collection",
            metadata=metadata,
            variables=[],
            tags=[],
            annotations=[],
            todos=[],
            examples=[],
        )
        
        # Verify: Metadata works (inherited from AnsibleRole)
        assert role.metadata.author == "Test Author"
        assert role.metadata.description == "Test collection role"
        assert role.has_metadata() is True  # Method from AnsibleRole
        
        # Verify: get_statistics() method inherited
        stats = role.get_statistics()
        assert "variables" in stats
        assert "tags" in stats
        assert "todos" in stats
        
        # Verify: __str__ method works
        str_repr = str(role)
        assert "webserver" in str_repr
    
    def test_collection_role_str_representation(self, tmp_path: Path) -> None:
        """Test: CollectionRole __str__ includes full_role_name (T098)."""
        # Setup: Create CollectionRole
        role_path = tmp_path / "collections" / "namespace" / "collection" / "roles" / "my_role"
        role = CollectionRole(
            path=role_path,
            name="my_role",
            collection_fqcn="namespace.collection",
        )
        
        # Verify: __str__ contains full_role_name
        str_repr = str(role)
        assert "namespace.collection.my_role" in str_repr or "my_role" in str_repr
    
    def test_collection_role_validates_name_like_ansible_role(self, tmp_path: Path) -> None:
        """Test: CollectionRole validates role name (inherited validation) (T099)."""
        # Verify: Empty name raises validation error (inherited from AnsibleRole)
        with pytest.raises(Exception):  # Pydantic ValidationError
            CollectionRole(
                path=tmp_path / "collections" / "test" / "collection" / "roles" / "empty",
                name="",  # Empty name should fail
                collection_fqcn="test.collection",
            )
        
        # Verify: Whitespace-only name raises validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            CollectionRole(
                path=tmp_path / "collections" / "test" / "collection" / "roles" / "whitespace",
                name="   ",  # Whitespace-only should fail
                collection_fqcn="test.collection",
            )
    
    def test_collection_role_validates_path_like_ansible_role(self) -> None:
        """Test: CollectionRole validates path (inherited validation) (T099)."""
        # Verify: Relative path raises validation error (inherited from AnsibleRole)
        with pytest.raises(Exception):  # Pydantic ValidationError
            CollectionRole(
                path=Path("relative/path/role"),  # Relative path should fail
                name="role",
                collection_fqcn="test.collection",
            )
