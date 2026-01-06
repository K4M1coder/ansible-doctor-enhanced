"""JSON Schema validator implementation.

Provides SchemaValidator class for validating data against JSON Schema.
"""

import json
from pathlib import Path
from typing import Any, Optional

import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError
from ruamel.yaml import YAML

from ansibledoctor.models.schemas import Severity, ValidationError, ValidationResult


class SchemaValidator:
    """Validates data against JSON Schema.

    Attributes:
        schema: JSON Schema dictionary
        validator_class: jsonschema validator class to use
    """

    def __init__(self, schema: dict[str, Any]):
        """Initialize validator with JSON Schema.

        Args:
            schema: JSON Schema dictionary
        """
        self.schema = schema
        self.validator_class = jsonschema.validators.validator_for(schema)
        self.validator_class.check_schema(schema)
        self.validator = self.validator_class(schema)

    def validate(self, data: Any, strict: bool = False) -> ValidationResult:
        """Validate data against schema.

        Args:
            data: Data to validate
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Run JSON Schema validation
        for error in self.validator.iter_errors(data):
            validation_error = self._convert_jsonschema_error(error)

            if validation_error.severity == Severity.WARNING:
                warnings.append(validation_error)
            else:
                errors.append(validation_error)

        is_valid = len(errors) == 0 and (not strict or len(warnings) == 0)

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )

    def validate_file(self, file_path: Path, strict: bool = False) -> ValidationResult:
        """Validate a YAML or JSON file against schema.

        Args:
            file_path: Path to file to validate
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with errors, warnings, and file path
        """
        try:
            data = self._load_file(file_path)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        path="",
                        message=f"Failed to load file: {e}",
                        validator="file_load",
                        severity=Severity.ERROR,
                    )
                ],
                file_path=file_path,
            )

        result = self.validate(data, strict=strict)
        result.file_path = file_path
        return result

    def _load_file(self, file_path: Path) -> Any:
        """Load YAML or JSON file.

        Args:
            file_path: Path to file

        Returns:
            Loaded data

        Raises:
            Exception: If file cannot be loaded
        """
        if file_path.suffix in {".yml", ".yaml"}:
            yaml = YAML()
            yaml.preserve_quotes = True
            with file_path.open("r", encoding="utf-8") as f:
                return yaml.load(f)
        elif file_path.suffix == ".json":
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _convert_jsonschema_error(self, error: JsonSchemaValidationError) -> ValidationError:
        """Convert jsonschema ValidationError to our ValidationError.

        Args:
            error: jsonschema ValidationError

        Returns:
            Our ValidationError instance
        """
        # Build path from error.path
        path_parts = list(error.path)
        path = ".".join(str(p) for p in path_parts) if path_parts else error.validator

        # Determine severity (additionalProperties -> warning, others -> error)
        severity = Severity.WARNING if error.validator == "additionalProperties" else Severity.ERROR

        # Extract expected/actual values
        expected = None
        actual = error.instance if hasattr(error, "instance") else None

        if error.validator == "enum":
            expected = ", ".join(str(v) for v in error.validator_value)
        elif error.validator == "type":
            expected = error.validator_value
        elif error.validator == "required":
            expected = f"Required field: {error.validator_value}"

        # Generate suggestion
        suggestion = self._generate_suggestion(error)

        return ValidationError(
            path=path,
            message=error.message,
            validator=error.validator,
            severity=severity,
            expected=expected,
            actual=actual,
            suggestion=suggestion,
        )

    def _generate_suggestion(self, error: JsonSchemaValidationError) -> Optional[str]:
        """Generate actionable suggestion for validation error.

        Args:
            error: jsonschema ValidationError

        Returns:
            Suggestion string or None
        """
        if error.validator == "enum":
            valid_values = error.validator_value
            return f"Use one of: {', '.join(str(v) for v in valid_values)}"
        elif error.validator == "type":
            expected_type = error.validator_value
            if expected_type == "boolean":
                return "Use 'true' or 'false' without quotes"
            elif expected_type == "integer" or expected_type == "number":
                return "Use a numeric value without quotes"
            else:
                return f"Provide a value of type: {expected_type}"
        elif error.validator == "additionalProperties":
            return "Remove this property or check for typos in the property name"
        elif error.validator == "required":
            missing = error.validator_value
            return f"Add required field: {missing}"
        else:
            return None
