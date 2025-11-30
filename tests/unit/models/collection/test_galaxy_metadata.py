"""Tests for GalaxyMetadata model.

Following Constitution Article III (TDD - RED Phase):
These tests are written FIRST and MUST FAIL before implementation.
"""

import pytest
from pydantic import ValidationError

from ansibledoctor.models.galaxy import GalaxyMetadata


class TestGalaxyMetadataValidData:
    """Test GalaxyMetadata with valid required fields (T009)."""

    def test_create_with_required_fields(self):
        """Test creating GalaxyMetadata with all required fields (schema 1.0.0)."""
        # Arrange
        data = {
            "namespace": "test_namespace",
            "name": "test_collection",
            "version": "1.0.0",
            "authors": ["Test Author <test@example.com>"],
            "dependencies": {},
        }

        # Act
        metadata = GalaxyMetadata(**data)

        # Assert
        assert metadata.namespace == "test_namespace"
        assert metadata.name == "test_collection"
        assert metadata.version == "1.0.0"
        assert metadata.authors == ["Test Author <test@example.com>"]
        assert metadata.dependencies == {}


class TestGalaxyMetadataNamespaceValidation:
    """Test GalaxyMetadata namespace validation (T010, T012)."""

    def test_valid_namespace_lowercase_alphanumeric(self):
        """Test namespace with valid lowercase alphanumeric format (T010)."""
        # Arrange
        data = {
            "namespace": "test_namespace123",
            "name": "test_collection",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }

        # Act
        metadata = GalaxyMetadata(**data)

        # Assert
        assert metadata.namespace == "test_namespace123"

    def test_namespace_with_underscores(self):
        """Test namespace with underscores is valid (T010)."""
        # Arrange
        data = {
            "namespace": "test_name_space",
            "name": "collection",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }

        # Act
        metadata = GalaxyMetadata(**data)

        # Assert
        assert metadata.namespace == "test_name_space"

    def test_reject_uppercase_namespace(self):
        """Test namespace with uppercase is rejected (T012)."""
        # Arrange
        data = {
            "namespace": "TestNamespace",  # Invalid: uppercase
            "name": "collection",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            GalaxyMetadata(**data)

        # Verify error mentions namespace pattern
        assert "namespace" in str(exc_info.value).lower()

    def test_reject_special_characters_in_namespace(self):
        """Test namespace with special characters is rejected (T012)."""
        # Arrange
        data = {
            "namespace": "test-namespace",  # Invalid: hyphen
            "name": "collection",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            GalaxyMetadata(**data)

        assert "namespace" in str(exc_info.value).lower()


class TestGalaxyMetadataVersionValidation:
    """Test GalaxyMetadata version validation (T011)."""

    def test_valid_semantic_version(self):
        """Test version with valid semantic version format (T011)."""
        # Arrange
        valid_versions = ["1.0.0", "2.1.3", "0.0.1", "10.20.30"]

        for version in valid_versions:
            data = {
                "namespace": "test_ns",
                "name": "test_coll",
                "version": version,
                "authors": ["Author"],
                "dependencies": {},
            }

            # Act
            metadata = GalaxyMetadata(**data)

            # Assert
            assert metadata.version == version


class TestGalaxyMetadataFQCN:
    """Test GalaxyMetadata FQCN property (T013)."""

    def test_fqcn_property_returns_namespace_dot_name(self):
        """Test that fqcn property returns 'namespace.name' (T013)."""
        # Arrange
        data = {
            "namespace": "my_namespace",
            "name": "my_collection",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }

        # Act
        metadata = GalaxyMetadata(**data)

        # Assert
        assert metadata.fqcn == "my_namespace.my_collection"


class TestGalaxyMetadataImmutability:
    """Test GalaxyMetadata immutability (T014)."""

    def test_model_is_frozen(self):
        """Test that GalaxyMetadata is immutable (frozen=True) (T014)."""
        # Arrange
        data = {
            "namespace": "test_ns",
            "name": "test_coll",
            "version": "1.0.0",
            "authors": ["Author"],
            "dependencies": {},
        }
        metadata = GalaxyMetadata(**data)

        # Act & Assert
        with pytest.raises((ValidationError, AttributeError)):
            metadata.namespace = "new_namespace"  # Should fail - frozen model


class TestGalaxyMetadataMinimalFields:
    """Test GalaxyMetadata with minimal required fields only (T015)."""

    def test_minimal_required_fields_only(self):
        """Test creating metadata with only required fields, no optional (T015)."""
        # Arrange - schema 1.0.0 required fields only

        # This test may need adjustment based on final schema interpretation
        # If authors/dependencies can have defaults, this should pass
        # If they're strictly required, this should fail

        # For now, test with all required fields:
        data_complete = {
            "namespace": "minimal",
            "name": "collection",
            "version": "0.1.0",
            "authors": [],  # Minimal: empty list
            "dependencies": {},  # Minimal: empty dict
        }

        # Act
        metadata = GalaxyMetadata(**data_complete)

        # Assert
        assert metadata.namespace == "minimal"
        assert metadata.name == "collection"
        assert metadata.version == "0.1.0"
        assert metadata.authors == []
        assert metadata.dependencies == {}
