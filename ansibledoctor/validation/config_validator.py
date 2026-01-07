"""Configuration file validator.

Validates .ansibledoctor.yml configuration files against JSON Schema.
"""

from pathlib import Path
from typing import Any, Optional

from ansibledoctor.models.schemas import ValidationResult
from ansibledoctor.validation.schema_validator import SchemaValidator


class ConfigurationValidator(SchemaValidator):
    """Validates ansible-doctor configuration files.

    Extends SchemaValidator with specific schema for .ansibledoctor.yml files.
    """

    # Configuration schema for .ansibledoctor.yml
    CONFIG_SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://ansible-doctor.com/schemas/config.json",
        "title": "Ansible Doctor Configuration",
        "description": "JSON Schema for .ansibledoctor.yml configuration files",
        "type": "object",
        "properties": {
            "output_format": {
                "type": "string",
                "enum": ["markdown", "html", "rst"],
                "default": "markdown",
                "description": "Output documentation format",
            },
            "output_dir": {
                "type": "string",
                "default": "docs",
                "description": "Output directory for generated documentation",
            },
            "verbose": {
                "type": "boolean",
                "default": False,
                "description": "Enable verbose logging",
            },
            "template": {
                "type": "string",
                "description": "Custom template path",
            },
            "template_dir": {
                "type": "string",
                "description": "Custom template directory path",
            },
            "exclude_tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags to exclude from documentation",
            },
            "role_name": {
                "type": "string",
                "description": "Override role name",
            },
            "author": {
                "type": "string",
                "description": "Role author name",
            },
            "description": {
                "type": "string",
                "description": "Role description",
            },
            "license": {
                "type": "string",
                "description": "Role license",
            },
            "min_ansible_version": {
                "type": "string",
                "description": "Minimum Ansible version required",
            },
            "platforms": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Supported platforms",
            },
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Role dependencies",
            },
            "galaxy_tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ansible Galaxy tags",
            },
            "strict_validation": {
                "type": "boolean",
                "default": False,
                "description": "Enable strict validation mode",
            },
            "include_index": {
                "type": "boolean",
                "default": False,
                "description": "Generate index pages",
            },
            "index_style": {
                "type": "string",
                "enum": ["list", "table", "tree", "nested-table", "diagram"],
                "default": "list",
                "description": "Index visualization style",
            },
            "index_format": {
                "type": "string",
                "enum": ["full", "section"],
                "default": "full",
                "description": "Index format (standalone or embedded)",
            },
            "index_depth": {
                "type": "integer",
                "default": 5,
                "minimum": 0,
                "description": "Maximum tree depth for indexes",
            },
            "nested_depth": {
                "type": "integer",
                "default": 2,
                "minimum": 1,
                "description": "Nesting depth for nested-table format",
            },
            "filter": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Index filters (field:value)",
            },
        },
        "additionalProperties": False,
    }

    def __init__(self, schema_cache: Optional[Any] = None):
        """Initialize ConfigurationValidator with config schema.
        
        Args:
            schema_cache: Optional SchemaCache instance for performance
        """
        super().__init__(self.CONFIG_SCHEMA, schema_cache=schema_cache)

    def validate(self, data: Any, strict: bool = False) -> ValidationResult:
        """Validate configuration data.

        Args:
            data: Configuration dictionary
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult
        """
        return super().validate(data, strict=strict)

    def validate_file(self, file_path: Path, strict: bool = False) -> ValidationResult:
        """Validate configuration file.

        Args:
            file_path: Path to .ansibledoctor.yml file
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with file path
        """
        return super().validate_file(file_path, strict=strict)
