"""Schema documentation generator.

Generates human-readable Markdown documentation from JSON Schema definitions.

Spec 012 Phase 7: T074-T078 - Schema documentation implementation
"""

from typing import Any, Dict, List


class SchemaDocumenter:
    """Generate Markdown documentation from JSON Schema.

    Converts JSON Schema definitions into user-friendly Markdown documentation
    with proper formatting, heading hierarchy, and comprehensive property details.

    Features:
    - Markdown generation with proper heading hierarchy
    - Property type, default, and description documentation
    - Nested object handling with recursive documentation
    - Enum value listing
    - Deprecated property marking
    - Required field indicators
    - Examples inclusion

    Example:
        >>> documenter = SchemaDocumenter()
        >>> schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        >>> docs = documenter.generate_docs(schema)
        >>> print(docs)
    """

    def __init__(self):
        """Initialize the schema documenter."""
        pass

    def generate_docs(self, schema: Dict[str, Any]) -> str:
        """Generate Markdown documentation from JSON Schema.

        Args:
            schema: JSON Schema dictionary (Draft 2020-12 compatible)

        Returns:
            Markdown-formatted documentation string

        Example:
            >>> schema = {
            ...     "title": "Config",
            ...     "type": "object",
            ...     "properties": {
            ...         "name": {"type": "string", "description": "User name"}
            ...     }
            ... }
            >>> docs = documenter.generate_docs(schema)
        """
        lines: List[str] = []

        # Title and description
        title = schema.get("title", "Schema Documentation")
        lines.append(f"# {title}\n")

        if "description" in schema:
            lines.append(f"{schema['description']}\n")

        # Check if schema has properties
        properties = schema.get("properties", {})
        if not properties:
            lines.append("\n*No properties defined.*\n")
            return "\n".join(lines)

        # Required fields
        required_fields = set(schema.get("required", []))

        # Document properties
        lines.append("\n## Properties\n")

        for prop_name, prop_schema in properties.items():
            lines.extend(
                self._document_property(
                    prop_name, prop_schema, is_required=prop_name in required_fields, level=3
                )
            )

        return "\n".join(lines)

    def _document_property(
        self, name: str, schema: Dict[str, Any], is_required: bool = False, level: int = 3
    ) -> List[str]:
        """Document a single property.

        Args:
            name: Property name
            schema: Property schema
            is_required: Whether property is required
            level: Heading level (3 = ###, 4 = ####, etc.)

        Returns:
            List of documentation lines
        """
        lines: List[str] = []

        # Property heading
        heading = "#" * level
        required_marker = " *(required)*" if is_required else ""
        deprecated_marker = " **[DEPRECATED]**" if schema.get("deprecated", False) else ""
        lines.append(f"\n{heading} `{name}`{required_marker}{deprecated_marker}\n")

        # Type
        prop_type = schema.get("type", "any")
        lines.append(f"**Type**: `{prop_type}`\n")

        # Description
        if "description" in schema:
            lines.append(f"{schema['description']}\n")

        # Default value
        if "default" in schema:
            default_value = schema["default"]
            lines.append(f"**Default**: `{default_value}`\n")

        # Enum values
        if "enum" in schema:
            enum_values = schema["enum"]
            lines.append("**Allowed values**:")
            for value in enum_values:
                lines.append(f"- `{value}`")
            lines.append("")

        # Examples
        if "examples" in schema:
            examples = schema["examples"]
            lines.append("**Examples**:")
            for example in examples:
                lines.append(f"- `{example}`")
            lines.append("")

        # Nested object properties
        if prop_type == "object" and "properties" in schema:
            nested_required = set(schema.get("required", []))
            lines.append("\n**Nested properties**:\n")

            for nested_name, nested_schema in schema["properties"].items():
                lines.extend(
                    self._document_property(
                        nested_name,
                        nested_schema,
                        is_required=nested_name in nested_required,
                        level=level + 1,
                    )
                )

        return lines
