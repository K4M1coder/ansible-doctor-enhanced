"""
Protocol definitions for Ansible Doctor Enhanced.

Following Constitution Article I (Library-First Architecture) and Article X (DDD):
- Protocols define clear interfaces (Dependency Inversion Principle)
- Enable testability without complex mocking
- Anti-Corruption Layer for external dependencies
"""

from pathlib import Path
from typing import Any, Protocol

from ansibledoctor.models.role import AnsibleRole


class YAMLLoader(Protocol):
    """
    Protocol for loading and parsing YAML files.

    Anti-Corruption Layer: Shields domain model from ruamel.yaml implementation details.
    Enables easy testing and potential YAML library replacement.
    """

    def load_file(self, file_path: Path) -> dict[str, Any] | list[Any]:
        """
        Load and parse a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary or list

        Raises:
            ParsingError: If YAML syntax is invalid
        """
        ...

    def load_with_comments(self, file_path: Path) -> tuple[dict[str, Any], list[str]]:
        """
        Load YAML file preserving comments for annotation extraction.

        Args:
            file_path: Path to YAML file

        Returns:
            Tuple of (parsed_content, comment_lines)

        Raises:
            ParsingError: If YAML syntax is invalid
        """
        ...


class AnnotationExtractor(Protocol):
    """
    Protocol for extracting inline documentation annotations.

    Domain Service: Operates on text content to extract structured annotations
    following ansible-doctor annotation syntax.
    """

    def extract_annotations(self, content: str, file_path: Path) -> list[dict[str, Any]]:
        """
        Extract all annotations from file content.

        Supported formats:
        - Single-line: # @var name: description
        - Multiline: # @var name: > ... @end
        - JSON: # @var name: $ {"type": "string", "example": "value"}

        Args:
            content: File content as string
            file_path: Path for context in annotations

        Returns:
            List of annotation dictionaries with keys: type, key, content, line_number
        """
        ...

    def parse_annotation_attributes(self, content: str) -> dict[str, Any]:
        """
        Parse annotation content into structured attributes.

        For JSON format annotations, parses the JSON payload.
        For text annotations, extracts description and optional type hints.

        Args:
            content: Annotation content string

        Returns:
            Dictionary with keys: type, description, example, required, deprecated, default
        """
        ...


class RoleParser(Protocol):
    """
    Protocol for parsing complete Ansible roles.

    Aggregate Root Service: Coordinates parsing of all role components and
    constructs the AnsibleRole aggregate.
    """

    def parse_role(self, role_path: Path) -> AnsibleRole:
        """
        Parse an Ansible role directory into structured domain model.

        This is the main entry point for role parsing. It orchestrates:
        1. Metadata extraction (meta/main.yml, meta/argument_specs.yml)
        2. Variable parsing (defaults/main.yml, vars/main.yml)
        3. Task parsing and tag extraction (tasks/*.yml)
        4. Annotation collection across all files

        Args:
            role_path: Path to Ansible role directory

        Returns:
            Complete AnsibleRole aggregate with all parsed data

        Raises:
            ParsingError: If role structure is invalid or parsing fails
            ValidationError: If required metadata is missing
        """
        ...

    def validate_role_structure(self, role_path: Path) -> bool:
        """
        Validate that role directory has expected structure.

        Args:
            role_path: Path to check

        Returns:
            True if valid role structure, False otherwise
        """
        ...
