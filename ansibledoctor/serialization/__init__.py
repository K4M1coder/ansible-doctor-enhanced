"""Serialization and format conversion for ansible-doctor.

This module provides format conversion, schema export, and documentation generation.

Components:
- format_converter: Convert between YAML, JSON, XML, Mermaid
- schema_exporter: Export JSON Schema and OpenAPI specifications
- schema_documenter: Generate Markdown documentation from schemas

Usage:
    from ansibledoctor.serialization import FormatConverter, SchemaExporter

    converter = FormatConverter()
    json_data = converter.convert(yaml_data, from_format="yaml", to_format="json")

    exporter = SchemaExporter()
    schema = exporter.export_schema(MyModel, format="json")
"""

# Placeholder exports for future implementation
__all__ = ["FormatConverter", "SchemaExporter", "SchemaDocumenter"]
