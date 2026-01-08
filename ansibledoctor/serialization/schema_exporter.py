"""Schema export functionality for JSON Schema and OpenAPI formats.

Feature 012 - Schema Documentation & Validation
Phase 4: User Story 2 - Export Configuration Schema (T035-T039)

Provides SchemaExporter class to export Pydantic models as JSON Schema
or OpenAPI 3.1 specifications for IDE integration and API documentation.
"""

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

from ansibledoctor.config.models import ConfigModel


class SchemaExporter:
    """Export Pydantic models as JSON Schema or OpenAPI specifications.

    Supports exporting configuration models with enriched metadata including
    descriptions, examples, and default values for IDE autocomplete integration.

    Example:
        >>> exporter = SchemaExporter()
        >>> schema = exporter.export_config_schema(format_type="json-schema")
        >>> schema["$schema"]
        'https://json-schema.org/draft/2020-12/schema'

        >>> exporter.export_to_file("config", Path("schema.json"))
    """

    def export_config_schema(
        self, format_type: Literal["json-schema", "openapi"] = "json-schema"
    ) -> dict[str, Any]:
        """Export configuration model schema in specified format.

        Args:
            format_type: Output format - "json-schema" for JSON Schema Draft 2020-12,
                        or "openapi" for OpenAPI 3.1 specification

        Returns:
            Schema dictionary with proper structure for specified format

        Example:
            >>> exporter = SchemaExporter()
            >>> schema = exporter.export_config_schema("json-schema")
            >>> "properties" in schema
            True
            >>> schema["properties"]["output_format"]["enum"]
            ['markdown', 'html', 'rst']
        """
        if format_type == "json-schema":
            return self._export_json_schema(ConfigModel)
        elif format_type == "openapi":
            return self._export_openapi_schema(ConfigModel)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def export_to_file(
        self,
        schema_type: str,
        output_path: Path,
        format_type: Literal["json-schema", "openapi"] = "json-schema",
    ) -> None:
        """Export schema to a file.

        Args:
            schema_type: Type of schema to export (currently only "config" supported)
            output_path: Path where schema file will be written
            format_type: Output format (json-schema or openapi)

        Example:
            >>> exporter = SchemaExporter()
            >>> exporter.export_to_file("config", Path("schema.json"))
        """
        if schema_type == "config":
            schema = self.export_config_schema(format_type)
        else:
            raise ValueError(f"Unknown schema type: {schema_type}")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write schema with pretty formatting
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    def _export_json_schema(self, model: type[BaseModel]) -> dict[str, Any]:
        """Export Pydantic model as JSON Schema Draft 2020-12.

        T036: Implements pydantic to JSON Schema conversion
        T038: Adds metadata enrichment (descriptions, examples, defaults)
        T039: Injects $schema property for IDE recognition

        Args:
            model: Pydantic model class to export

        Returns:
            JSON Schema dictionary with enriched metadata
        """
        # Generate base schema using pydantic's built-in method
        schema = model.model_json_schema(mode="validation")

        # T039: Inject $schema property for IDE recognition
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"

        # T038: Enrich metadata with better descriptions
        if "title" not in schema:
            schema["title"] = "Ansible Doctor Configuration"
        if "description" not in schema:
            schema["description"] = (
                "Configuration schema for ansible-doctor-enhanced. "
                "Validates .ansibledoctor.yml configuration files."
            )

        # Add $id for schema identification
        schema["$id"] = "https://ansibledoctor.com/schemas/config.json"

        # T038: Enrich property metadata with examples
        properties = schema.get("properties", {})

        # Add examples for output_format
        if "output_format" in properties:
            output_format = properties["output_format"]
            # Pydantic may generate anyOf for Optional fields
            output_format.setdefault("examples", ["markdown", "html"])
            output_format.setdefault("default", "markdown")

        # Add examples for recursive
        if "recursive" in properties:
            recursive = properties["recursive"]
            recursive.setdefault("examples", [False, True])
            if "default" not in recursive:
                recursive["default"] = False

        # Add examples for output_dir
        if "output_dir" in properties:
            output_dir = properties["output_dir"]
            output_dir.setdefault("examples", ["docs/", "./output"])

        return schema

    def _export_openapi_schema(self, model: type[BaseModel]) -> dict[str, Any]:
        """Export Pydantic model as OpenAPI 3.1 specification.

        T037: Implements OpenAPI 3.1 schema export

        Args:
            model: Pydantic model class to export

        Returns:
            OpenAPI 3.1 specification with config schema
        """
        # Get JSON Schema representation
        json_schema = self._export_json_schema(model)

        # Remove $schema and $id as they're not part of OpenAPI component schemas
        config_schema = {k: v for k, v in json_schema.items() if k not in ("$schema", "$id")}

        # Build OpenAPI document
        openapi_doc = {
            "openapi": "3.1.0",
            "info": {
                "title": "Ansible Doctor Configuration API",
                "version": "1.0.0",
                "description": (
                    "API schema for ansible-doctor-enhanced configuration. "
                    "Defines the structure and validation rules for .ansibledoctor.yml files."
                ),
            },
            "components": {"schemas": {"Config": config_schema}},
        }

        return openapi_doc
