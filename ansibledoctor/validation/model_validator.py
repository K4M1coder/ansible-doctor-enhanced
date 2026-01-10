"""Data model validation for Ansible structures.

Validates Role, Collection, and other pydantic models against schemas.
"""

from typing import Any, Type

from pydantic import BaseModel, ValidationError

from ansibledoctor.models.schemas import Severity
from ansibledoctor.models.schemas import ValidationError as SchemaValidationError
from ansibledoctor.models.schemas import ValidationResult


class DataModelValidator:
    """Validates data models against their pydantic schemas.

    Provides validation for Role, Collection, and Project models by:
    - Generating JSON Schema from pydantic models
    - Validating data dictionaries against models
    - Validating model instances for completeness
    - Supporting strict mode (warnings as errors)

    Examples:
        >>> validator = DataModelValidator()
        >>> result = validator.validate_model(role_instance)
        >>> result = validator.validate_dict(role_data, AnsibleRole)
        >>> schema = validator.generate_schema(AnsibleRole)
    """

    def validate_model(self, model: BaseModel, strict: bool = False) -> ValidationResult:
        """Validate a pydantic model instance.

        Args:
            model: Pydantic model instance to validate
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with errors and warnings

        Examples:
            >>> role = AnsibleRole(path=Path("/tmp/role"), name="my_role")
            >>> result = validator.validate_model(role)
            >>> if not result.is_valid:
            ...     print(result.errors)
        """
        errors: list[SchemaValidationError] = []
        warnings: list[SchemaValidationError] = []

        # Pydantic already validated on construction, but we can check for
        # recommended fields that might be missing

        # Check for recommended but not required fields
        # For example, role metadata should have description
        if hasattr(model, "metadata"):
            metadata = model.metadata
            if hasattr(metadata, "description"):
                if not metadata.description or len(metadata.description.strip()) == 0:
                    warnings.append(
                        SchemaValidationError(
                            path="metadata.description",
                            message="Description is recommended but missing or empty",
                            validator="recommended_field",
                            severity=Severity.WARNING,
                        )
                    )

            # Check dependency format for collections
            if hasattr(metadata, "dependencies") and metadata.dependencies:
                for dep_name, _dep_version in metadata.dependencies.items():
                    # Check if dependency name follows FQCN format (namespace.name)
                    if "." not in dep_name or dep_name.count(".") != 1:
                        warnings.append(
                            SchemaValidationError(
                                path=f"metadata.dependencies.{dep_name}",
                                message=f"Dependency '{dep_name}' should follow FQCN format 'namespace.name'",
                                validator="dependency_format",
                                severity=Severity.WARNING,
                            )
                        )

        # In strict mode, warnings become errors
        if strict and warnings:
            is_valid = False
        else:
            is_valid = len(errors) == 0

        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def validate_dict(
        self, data: dict[str, Any], model_class: Type[BaseModel], strict: bool = False
    ) -> ValidationResult:
        """Validate a dictionary against a pydantic model schema.

        Args:
            data: Dictionary data to validate
            model_class: Pydantic model class to validate against
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult with errors and warnings

        Examples:
            >>> role_data = {"path": "/tmp/role", "name": "my_role", "metadata": {...}}
            >>> result = validator.validate_dict(role_data, AnsibleRole)
        """
        errors: list[SchemaValidationError] = []
        warnings: list[SchemaValidationError] = []

        try:
            # Try to construct the model - pydantic will validate
            instance = model_class(**data)

            # If successful, run additional validation on the instance
            result = self.validate_model(instance, strict=strict)
            return result

        except ValidationError as e:
            # Pydantic validation failed - convert to our error format
            for error in e.errors():
                # Extract field path
                field_path = ".".join(str(loc) for loc in error["loc"])

                # Create helpful error message
                error_type = error["type"]
                message = error["msg"]

                # Enhance message based on error type
                if error_type == "missing":
                    message = f"Required field '{field_path}' is missing"
                elif error_type == "value_error":
                    message = f"Invalid value for '{field_path}': {message}"
                elif error_type.startswith("type_error"):
                    expected_type = error.get("ctx", {}).get("expected_type", "correct type")
                    message = f"Field '{field_path}' has wrong type. Expected {expected_type}"

                errors.append(
                    SchemaValidationError(
                        path=field_path,
                        message=message,
                        validator=error_type,
                        severity=Severity.ERROR,
                    )
                )

            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    def generate_schema(self, model_class: Type[BaseModel]) -> dict[str, Any]:
        """Generate JSON Schema from a pydantic model.

        Args:
            model_class: Pydantic model class

        Returns:
            JSON Schema dictionary

        Examples:
            >>> schema = validator.generate_schema(AnsibleRole)
            >>> print(schema["properties"]["name"])
        """
        # Use pydantic's built-in schema generation
        schema = model_class.model_json_schema()

        # Add $schema property for compatibility
        if "$schema" not in schema:
            schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"

        return schema

    def validate_role(self, role_data: dict[str, Any], strict: bool = False) -> ValidationResult:
        """Validate role data against Role schema.

        Convenience method for validating roles.

        Args:
            role_data: Role dictionary data
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult
        """
        from ansibledoctor.models.role import AnsibleRole

        return self.validate_dict(role_data, AnsibleRole, strict=strict)

    def validate_collection(
        self, collection_data: dict[str, Any], strict: bool = False
    ) -> ValidationResult:
        """Validate collection data against Collection schema.

        Convenience method for validating collections.

        Args:
            collection_data: Collection dictionary data
            strict: If True, treat warnings as errors

        Returns:
            ValidationResult
        """
        from ansibledoctor.models.collection import AnsibleCollection

        return self.validate_dict(collection_data, AnsibleCollection, strict=strict)
