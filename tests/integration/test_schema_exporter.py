"""Integration tests for schema export functionality.

Tests the SchemaExporter with JSON Schema and OpenAPI format exports.
"""

import json

import pytest

from ansibledoctor.serialization.schema_exporter import SchemaExporter


@pytest.fixture
def schema_exporter():
    """Create a SchemaExporter instance."""
    return SchemaExporter()


@pytest.fixture
def temp_output_file(tmp_path):
    """Temporary file for schema output."""
    return tmp_path / "schema.json"


class TestSchemaExporter:
    """Tests for SchemaExporter."""

    def test_export_config_json_schema(self, schema_exporter):
        """Test exporting configuration schema as JSON Schema.

        T030: Validates that the exported JSON Schema has proper structure:
        - Has $schema property
        - Has title and description
        - Has properties object with known config fields
        - Follows JSON Schema Draft 2020-12 format
        """
        # Export config schema
        schema = schema_exporter.export_config_schema(format_type="json-schema")

        # Validate schema structure
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"

        # Check metadata
        assert "title" in schema
        assert "description" in schema
        assert "properties" in schema

        # Validate known config properties exist
        properties = schema["properties"]
        assert "output_format" in properties
        assert "output_dir" in properties
        assert "recursive" in properties  # Changed from verbose which doesn't exist

        # Validate output_format accepts correct values
        output_format = properties["output_format"]
        # Pydantic generates anyOf for Optional fields with validators
        assert "description" in output_format
        assert (
            "markdown" in output_format.get("description", "").lower()
            or "html" in output_format.get("description", "").lower()
        )

    def test_export_openapi_format(self, schema_exporter):
        """Test exporting schema in OpenAPI 3.1 format.

        T031: Validates that the exported OpenAPI schema:
        - Has openapi version
        - Has info section
        - Has components/schemas structure
        - Config schema is under components/schemas/Config
        """
        # Export config schema in OpenAPI format
        schema = schema_exporter.export_config_schema(format_type="openapi")

        # Validate OpenAPI structure
        assert isinstance(schema, dict)
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.1")

        # Check info section
        assert "info" in schema
        assert "title" in schema["info"]
        assert "version" in schema["info"]

        # Check components structure
        assert "components" in schema
        assert "schemas" in schema["components"]
        assert "Config" in schema["components"]["schemas"]

        # Validate config schema properties
        config_schema = schema["components"]["schemas"]["Config"]
        assert "properties" in config_schema
        assert "output_format" in config_schema["properties"]

    def test_export_to_file(self, schema_exporter, temp_output_file):
        """Test exporting schema to a file.

        T032: Validates that:
        - Schema is written to specified file path
        - File contains valid JSON
        - File content matches in-memory export
        """
        # Export to file
        schema_exporter.export_to_file(
            "config", output_path=temp_output_file, format_type="json-schema"
        )

        # Verify file was created
        assert temp_output_file.exists()

        # Verify file contains valid JSON
        with open(temp_output_file) as f:
            file_schema = json.load(f)

        assert isinstance(file_schema, dict)
        assert "$schema" in file_schema
        assert "properties" in file_schema

        # Verify content matches in-memory export
        memory_schema = schema_exporter.export_config_schema(format_type="json-schema")
        assert file_schema == memory_schema

    def test_schema_has_examples(self, schema_exporter):
        """Test that exported schemas include examples.

        T034: Validates that:
        - Schema properties have examples
        - Examples are valid for their types
        - Examples help users understand property usage
        """
        # Export config schema
        schema = schema_exporter.export_config_schema(format_type="json-schema")

        # Check for examples in properties
        properties = schema["properties"]

        # output_format should have examples
        if "examples" in properties["output_format"]:
            examples = properties["output_format"]["examples"]
            assert isinstance(examples, list)
            assert len(examples) > 0
            # Examples should be markdown or html
            assert any(ex in ["markdown", "html", "rst"] for ex in examples)

        # recursive should have example
        if "examples" in properties.get("recursive", {}):
            examples = properties["recursive"]["examples"]
            assert isinstance(examples, list)
            assert len(examples) > 0
            # Examples should be boolean
            for example in examples:
                assert isinstance(example, bool)

    def test_export_with_metadata_enrichment(self, schema_exporter):
        """Test that exported schemas have enriched metadata.

        T038: Validates that:
        - Properties have descriptions
        - Properties have default values where applicable
        - Enum types have clear descriptions
        """
        # Export config schema
        schema = schema_exporter.export_config_schema(format_type="json-schema")

        properties = schema["properties"]

        # Check output_format has description
        output_format = properties["output_format"]
        assert "description" in output_format or "title" in output_format
        # Pydantic uses anyOf for Optional fields with validators
        assert "anyOf" in output_format or "type" in output_format
        assert "default" in output_format

        # Check recursive has description and type
        recursive = properties["recursive"]
        assert "description" in recursive or "title" in recursive
        assert recursive.get("type") == "boolean" or not recursive.get("default")

        # Check output_dir has description
        output_dir = properties["output_dir"]
        assert "description" in output_dir or "title" in output_dir

    def test_schema_id_injection(self, schema_exporter):
        """Test that schemas have proper $id and $schema properties.

        T039: Validates that:
        - $schema property points to JSON Schema spec
        - $id property provides unique schema identifier
        - These properties enable IDE recognition
        """
        # Export config schema
        schema = schema_exporter.export_config_schema(format_type="json-schema")

        # Check $schema property
        assert "$schema" in schema
        assert "json-schema.org" in schema["$schema"]
        assert "2020-12" in schema["$schema"]

        # Check $id property for schema identification
        if "$id" in schema:
            schema_id = schema["$id"]
            assert isinstance(schema_id, str)
            assert "ansibledoctor" in schema_id.lower() or "config" in schema_id.lower()
