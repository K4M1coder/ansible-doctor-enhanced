"""Tests for AnsibleCollection model.

Following Constitution Article III (TDD - RED Phase):
These tests are written FIRST and MUST FAIL before implementation.
"""

import pytest

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.plugin import PluginType


class TestAnsibleCollectionModel:
    """Test AnsibleCollection model creation (T026)."""

    def test_create_with_metadata_roles_plugins(self):
        """Test creating AnsibleCollection with metadata, roles, and plugins (T026)."""
        # Arrange
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )
        roles = ["web_server", "database"]
        plugins = {
            PluginType.MODULE: ["my_module.py", "other_module.py"],
            PluginType.FILTER: ["my_filter.py"],
        }

        # Act
        collection = AnsibleCollection(metadata=metadata, roles=roles, plugins=plugins)

        # Assert
        assert collection.metadata == metadata
        assert collection.roles == roles
        assert collection.plugins == plugins


class TestAnsibleCollectionFQCN:
    """Test AnsibleCollection FQCN property (T027)."""

    def test_fqcn_delegates_to_metadata(self):
        """Test that collection.fqcn delegates to metadata.fqcn (T027)."""
        # Arrange
        metadata = GalaxyMetadata(
            namespace="my_namespace",
            name="my_collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )
        collection = AnsibleCollection(metadata=metadata, roles=[], plugins={})

        # Act
        fqcn = collection.fqcn

        # Assert
        assert fqcn == "my_namespace.my_collection"
        assert fqcn == metadata.fqcn


class TestAnsibleCollectionRoleListing:
    """Test listing role names (T028)."""

    def test_lists_role_names(self):
        """Test that collection can list role names (T028)."""
        # Arrange
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )
        roles = ["role1", "role2", "role3"]
        collection = AnsibleCollection(metadata=metadata, roles=roles, plugins={})

        # Act
        role_list = collection.list_roles()

        # Assert
        assert role_list == roles
        assert len(role_list) == 3


class TestAnsibleCollectionPluginListing:
    """Test listing plugins by type (T029)."""

    def test_lists_plugins_by_type(self):
        """Test that collection can list plugin names by type (T029)."""
        # Arrange
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )
        plugins = {
            PluginType.MODULE: ["module1.py", "module2.py"],
            PluginType.FILTER: ["filter1.py"],
        }
        collection = AnsibleCollection(metadata=metadata, roles=[], plugins=plugins)

        # Act
        modules = collection.list_plugins_by_type(PluginType.MODULE)
        filters = collection.list_plugins_by_type(PluginType.FILTER)
        lookups = collection.list_plugins_by_type(PluginType.LOOKUP)

        # Assert
        assert modules == ["module1.py", "module2.py"]
        assert filters == ["filter1.py"]
        assert lookups == []  # No lookups defined


class TestAnsibleCollectionDependencyValidation:
    """Test dependency validation (T030)."""

    def test_validates_no_self_dependency(self):
        """Test that collection validates no circular self-reference (T030)."""
        # Arrange
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["Author"],
            dependencies={"test_ns.test_coll": ">=1.0.0"},  # Self-dependency!
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            AnsibleCollection(metadata=metadata, roles=[], plugins={})

        # Verify error mentions self-dependency
        error_msg = str(exc_info.value).lower()
        assert "self" in error_msg or "circular" in error_msg or "dependency" in error_msg
