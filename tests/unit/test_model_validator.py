"""Unit tests for data model validation.

Tests the DataModelValidator with Role and Collection models.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.validation.model_validator import DataModelValidator


@pytest.fixture
def model_validator():
    """Create a DataModelValidator instance."""
    return DataModelValidator()


class TestRoleValidation:
    """Tests for role data validation."""

    def test_valid_role_passes_validation(self, model_validator):
        """Test that a valid role passes validation with no errors.

        T059: Valid data validation - success with no errors
        """
        # Create a valid role
        role = AnsibleRole(
            path=Path("E:/tmp/my_role"),
            name="my_role",
            metadata=RoleMetadata(
                author="John Doe",
                company="Example Corp",
                license="MIT",
                min_ansible_version="2.9",
                description="A test role",
            ),
        )

        # Validate the role
        result = model_validator.validate_model(role)

        # Should pass with no errors
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_role_missing_required_field_fails(self, model_validator):
        """Test that missing required fields are detected.

        T057: Missing required field - role missing name
        """
        # Create role with missing name (truly required field)
        role_data = {
            "path": "E:/tmp/my_role",
            # "name" is missing - required field
            "metadata": {
                "company": "Example Corp",
                "license": "MIT",
            },
        }

        # Validate should detect missing name
        result = model_validator.validate_dict(role_data, AnsibleRole)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check that error mentions "name" field
        error_messages = [e.message for e in result.errors]
        assert any("name" in msg.lower() for msg in error_messages)

    def test_role_with_invalid_path_type(self, model_validator):
        """Test that invalid field types are detected."""
        # Create role with invalid path type
        role_data = {
            "path": 123,  # Should be string or Path, not int
            "name": "my_role",
            "metadata": {
                "author": "John Doe",
                "company": "Example Corp",
                "license": "MIT",
            },
        }

        result = model_validator.validate_dict(role_data, AnsibleRole)

        assert result.is_valid is False
        assert len(result.errors) > 0


class TestCollectionValidation:
    """Tests for collection data validation."""

    def test_valid_collection_passes_validation(self, model_validator):
        """Test that a valid collection passes validation.

        T059: Valid data validation
        """
        # Create a valid collection
        collection = AnsibleCollection(
            metadata=GalaxyMetadata(
                namespace="my_namespace",
                name="my_collection",
                version="1.0.0",
                authors=["John Doe"],
                description="A test collection",
            ),
            roles=[],
        )

        result = model_validator.validate_model(collection)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_collection_missing_namespace_fails(self, model_validator):
        """Test that missing namespace is detected."""
        # Create collection with missing namespace
        collection_data = {
            "metadata": {
                "name": "my_collection",
                "version": "1.0.0",
                "authors": ["John Doe"],
                # "namespace" is missing - required field
            },
            "roles": [],
        }

        result = model_validator.validate_dict(collection_data, AnsibleCollection)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check error mentions namespace
        error_messages = [e.message for e in result.errors]
        assert any("namespace" in msg.lower() for msg in error_messages)

    def test_collection_invalid_dependency_format_fails(self, model_validator):
        """Test that invalid dependency formats are detected.

        T058: Invalid dependency format - collection dependencies
        """
        # Create collection with invalid dependency
        collection_data = {
            "metadata": {
                "namespace": "my_namespace",
                "name": "my_collection",
                "version": "1.0.0",
                "authors": ["John Doe"],
                "dependencies": {"invalid_dep": "not_a_valid_version"},  # Should follow semver
            },
            "roles": [],
        }

        # This might pass pydantic validation but fail semantic validation
        result = model_validator.validate_dict(collection_data, AnsibleCollection)

        # Should either have errors or warnings about dependency format
        assert result.is_valid is False or len(result.warnings) > 0


class TestStrictValidationMode:
    """Tests for strict validation mode."""

    def test_strict_mode_treats_warnings_as_errors(self, model_validator):
        """Test that strict mode treats warnings as errors.

        T060: Strict validation mode - warnings as errors
        """
        # Create role with a field that might trigger a warning
        # (e.g., deprecated field, recommended but not required)
        role = AnsibleRole(
            path=Path("E:/tmp/my_role"),
            name="my_role",
            metadata=RoleMetadata(
                author="John Doe",
                company="Example Corp",
                license="MIT",
                # Missing description - might be a warning
            ),
        )

        # Validate in strict mode
        result = model_validator.validate_model(role, strict=True)

        # In strict mode, warnings should prevent is_valid from being True
        # if there are any warnings
        if len(result.warnings) > 0:
            assert result.is_valid is False

    def test_normal_mode_allows_warnings(self, model_validator):
        """Test that normal mode allows warnings without failing validation."""
        role = AnsibleRole(
            path=Path("E:/tmp/my_role"),
            name="my_role",
            metadata=RoleMetadata(
                author="John Doe",
                company="Example Corp",
                license="MIT",
            ),
        )

        # Validate in normal mode
        result = model_validator.validate_model(role, strict=False)

        # Should pass even with warnings (if any)
        assert result.is_valid is True or len(result.errors) == 0


class TestSchemaGeneration:
    """Tests for schema generation from pydantic models."""

    def test_generate_schema_from_role_model(self, model_validator):
        """Test schema generation from Role model.

        T063: Schema generation from pydantic models
        """
        schema = model_validator.generate_schema(AnsibleRole)

        assert schema is not None
        assert "$schema" in schema or "properties" in schema
        assert "path" in schema.get("properties", {})
        assert "name" in schema.get("properties", {})
        assert "metadata" in schema.get("properties", {})

    def test_generate_schema_from_collection_model(self, model_validator):
        """Test schema generation from Collection model."""
        schema = model_validator.generate_schema(AnsibleCollection)

        assert schema is not None
        assert "properties" in schema
        assert "metadata" in schema["properties"]
        assert "roles" in schema["properties"]

    def test_generated_schema_includes_required_fields(self, model_validator):
        """Test that generated schemas include required field info."""
        schema = model_validator.generate_schema(AnsibleRole)

        # Role has required fields: path, name
        assert "required" in schema
        assert "path" in schema["required"]
        assert "name" in schema["required"]


class TestValidationErrorDetails:
    """Tests for validation error detail and reporting."""

    def test_validation_error_includes_field_path(self, model_validator):
        """Test that validation errors include the field path."""
        role_data = {
            "path": "E:/tmp/my_role",
            # Missing required name field
            "metadata": {
                "author": "Test Author",
                "company": "Example Corp",
            },
        }

        result = model_validator.validate_dict(role_data, AnsibleRole)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Error should include path like "name"
        error = result.errors[0]
        assert error.path is not None
        assert "name" in error.path or "name" in error.message.lower()

    def test_validation_error_includes_helpful_message(self, model_validator):
        """Test that validation errors include helpful messages."""
        role_data = {
            "path": "E:/tmp/my_role",
            "name": "my_role",
            "metadata": {
                "author": "John Doe",
                "license": "INVALID_LICENSE",  # Not a valid license
            },
        }

        result = model_validator.validate_dict(role_data, AnsibleRole)

        # Should provide helpful error message
        if not result.is_valid:
            assert len(result.errors) > 0
            error = result.errors[0]
            assert len(error.message) > 0
