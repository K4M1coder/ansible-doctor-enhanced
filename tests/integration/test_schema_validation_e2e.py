"""End-to-end tests for data model validation.

Tests show how schema validation catches invalid role/collection data
that would cause parser failures.

Spec 012 Phase 6: T068 - Integration examples
"""


import pytest

from ansibledoctor.models import AnsibleCollection, AnsibleRole
from ansibledoctor.validation import DataModelValidator


class TestRoleValidationE2E:
    """End-to-end tests for role data validation."""

    @pytest.fixture
    def validator(self):
        """Create DataModelValidator instance."""
        return DataModelValidator()

    def test_valid_role_data_passes_validation(self, validator):
        """Test that valid role data passes validation.

        This demonstrates the happy path - correct role metadata
        validates successfully.
        """
        role_data = {
            "path": "E:/tmp/demo_role",
            "name": "demo_role",
            "metadata": {
                "author": "Demo Author",
                "description": "A demo role for testing",
                "company": "Demo Corp",
                "license": "MIT",
                "min_ansible_version": "2.9",
                "platforms": [{"name": "Ubuntu", "versions": ["20.04", "22.04"]}],
                "galaxy_tags": ["demo", "testing"],
            },
        }

        result = validator.validate_role(role_data, strict=False)

        assert result.is_valid
        assert len(result.errors) == 0
        # May have warnings (e.g., recommended fields)
        if result.warnings:
            assert all(w.severity == "WARNING" for w in result.warnings)

    def test_invalid_role_data_caught_early(self, validator):
        """Test that invalid role data is caught before parser runs.

        This demonstrates how schema validation prevents parser failures
        by catching data type errors early.
        """
        role_data = {
            "path": "E:/tmp/demo_role",
            "name": "demo_role",
            "metadata": {
                "author": "Demo Author",
                "platforms": "Ubuntu",  # Should be list, not string
            },
        }

        result = validator.validate_role(role_data, strict=False)

        # Validation should fail due to type error
        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check error details
        error = result.errors[0]
        assert "platforms" in error.path.lower() or "platforms" in error.message.lower()
        assert error.validator is not None  # Should specify error type

    def test_strict_mode_catches_missing_description(self, validator):
        """Test that strict mode catches recommended but missing fields.

        Demonstrates strict validation mode treating warnings as errors.
        """
        role_data = {
            "path": "E:/tmp/demo_role",
            "name": "demo_role",
            "metadata": {
                "author": "Demo Author",
                # Missing description (recommended but not required)
            },
        }

        # Normal mode: should pass with warning
        result_normal = validator.validate_role(role_data, strict=False)
        assert result_normal.is_valid
        assert len(result_normal.warnings) > 0

        # Strict mode: should fail
        result_strict = validator.validate_role(role_data, strict=True)
        assert result_strict.is_valid is False
        assert len(result_strict.warnings) > 0


class TestCollectionValidationE2E:
    """End-to-end tests for collection data validation."""

    @pytest.fixture
    def validator(self):
        """Create DataModelValidator instance."""
        return DataModelValidator()

    def test_valid_collection_data_passes_validation(self, validator):
        """Test that valid collection data passes validation."""
        collection_data = {
            "metadata": {
                "namespace": "demo_namespace",
                "name": "demo_collection",
                "version": "1.0.0",
                "authors": ["Demo Author <demo@example.com>"],
                "license": ["MIT"],
                "dependencies": {"ansible.posix": ">=1.0.0"},
            }
        }

        result = validator.validate_collection(collection_data, strict=False)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_dependency_format_warning(self, validator):
        """Test that invalid dependency format triggers warning."""
        collection_data = {
            "metadata": {
                "namespace": "demo_namespace",
                "name": "demo_collection",
                "version": "1.0.0",
                "authors": ["Demo Author"],
                "license": ["MIT"],
                "dependencies": {"invalid_dep": "1.0.0"},  # Missing namespace separator
            }
        }

        result = validator.validate_collection(collection_data, strict=False)

        # Should pass but with warning about dependency format
        assert result.is_valid
        assert len(result.warnings) > 0

        # Check warning mentions dependency
        warning_messages = [w.message for w in result.warnings]
        assert any("invalid_dep" in msg or "FQCN" in msg for msg in warning_messages)

    def test_missing_required_metadata_fails(self, validator):
        """Test that missing required metadata fields fail validation."""
        collection_data = {
            "metadata": {
                "namespace": "demo_namespace",
                # Missing 'name' - required field
                "version": "1.0.0",
            }
        }

        result = validator.validate_collection(collection_data, strict=False)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Error should mention missing field
        error_messages = [e.message for e in result.errors]
        assert any("name" in msg.lower() for msg in error_messages)


class TestSchemaGenerationE2E:
    """End-to-end tests for schema generation."""

    @pytest.fixture
    def validator(self):
        """Create DataModelValidator instance."""
        return DataModelValidator()

    def test_generate_role_schema_for_ide_integration(self, validator):
        """Test generating role schema for IDE autocomplete.

        Demonstrates how to generate JSON Schema for IDE integration.
        """
        schema = validator.generate_schema(AnsibleRole)

        # Schema should be valid JSON Schema
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

        # Should contain role properties
        assert "properties" in schema
        properties = schema["properties"]
        assert "path" in properties
        assert "name" in properties
        assert "metadata" in properties

        # Required fields should be marked
        assert "required" in schema
        assert "path" in schema["required"]
        assert "name" in schema["required"]

    def test_generate_collection_schema_for_ide_integration(self, validator):
        """Test generating collection schema for IDE autocomplete."""
        schema = validator.generate_schema(AnsibleCollection)

        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "properties" in schema

        # Collection has metadata
        properties = schema["properties"]
        assert "metadata" in properties

        # Check nested metadata properties
        if "properties" in properties["metadata"]:
            metadata_props = properties["metadata"]["properties"]
            assert "namespace" in metadata_props
            assert "name" in metadata_props
            assert "version" in metadata_props


class TestValidationErrorDetails:
    """Test validation error detail and message quality."""

    @pytest.fixture
    def validator(self):
        """Create DataModelValidator instance."""
        return DataModelValidator()

    def test_error_includes_field_path(self, validator):
        """Test that errors include JSONPath to invalid field."""
        role_data = {
            "path": "E:/tmp/demo_role",
            # Missing required 'name'
            "metadata": {"author": "Demo"},
        }

        result = validator.validate_role(role_data, strict=False)

        assert result.is_valid is False
        error = result.errors[0]

        # Error should have path
        assert error.path is not None
        assert len(error.path) > 0

    def test_error_includes_helpful_message(self, validator):
        """Test that errors include helpful, actionable messages."""
        role_data = {"path": "E:/tmp/demo_role", "name": 123}  # Wrong type - should be string

        result = validator.validate_role(role_data, strict=False)

        assert result.is_valid is False
        error = result.errors[0]

        # Error should have clear message
        assert error.message is not None
        assert len(error.message) > 10

        # Should mention the issue
        assert any(word in error.message.lower() for word in ["string", "type", "invalid"])

    def test_error_includes_validator_type(self, validator):
        """Test that errors include validator type."""
        role_data = {
            "path": "E:/tmp/demo_role",
            # Missing required field
        }

        result = validator.validate_role(role_data, strict=False)

        assert result.is_valid is False
        error = result.errors[0]

        # Error should specify validator type
        assert error.validator is not None
        assert len(error.validator) > 0
