"""Schema validation infrastructure for ansible-doctor.

This module provides comprehensive validation capabilities for configuration files,
data models, and schema management.

Components:
- schema_validator: Core JSON Schema validation
- config_validator: Configuration file validation
- model_validator: Data model validation

Usage:
    from ansibledoctor.validation import SchemaValidator, ConfigurationValidator

    validator = ConfigurationValidator()
    result = validator.validate(config_data)
    if not result.is_valid:
        print(result.format_report())
"""

from ansibledoctor.validation.config_validator import ConfigurationValidator
from ansibledoctor.validation.schema_validator import SchemaValidator

__all__ = ["SchemaValidator", "ConfigurationValidator"]
