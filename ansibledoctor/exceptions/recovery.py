"""Recovery suggestion provider and database.

This module provides intelligent recovery suggestions for error codes.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class RecoverySuggestionProvider:
    """Provides context-aware recovery suggestions for error codes."""

    def __init__(self, database_path: Optional[Path] = None):
        """Initialize recovery suggestion provider.

        Args:
            database_path: Path to recovery suggestion JSON database.
                          If None, uses default embedded database.
        """
        self.database_path = database_path
        self._suggestions: Dict[str, Dict] = {}
        self._load_database()

    def _load_database(self) -> None:
        """Load recovery suggestion database from file or embedded defaults."""
        if self.database_path and self.database_path.exists():
            with open(self.database_path, "r", encoding="utf-8") as f:
                self._suggestions = json.load(f)
        else:
            # Use embedded default suggestions
            self._suggestions = DEFAULT_RECOVERY_SUGGESTIONS

    def get_suggestion(self, error_code: str) -> Optional[str]:
        """Get recovery suggestion for an error code.

        Args:
            error_code: Error code (e.g., "E101")

        Returns:
            Recovery suggestion string, or None if no suggestion available
        """
        suggestion_data = self._suggestions.get(error_code)
        if not suggestion_data:
            # Try category fallback (E1xx -> E100, E2xx -> E200, etc.)
            category_code = f"{error_code[0]}{error_code[1]}00"
            suggestion_data = self._suggestions.get(category_code)

        if suggestion_data:
            return suggestion_data.get("suggestion")

        return None

    def get_doc_url(self, error_code: str) -> Optional[str]:
        """Get documentation URL for an error code.

        Args:
            error_code: Error code (e.g., "E101")

        Returns:
            Documentation URL, or None if not available
        """
        suggestion_data = self._suggestions.get(error_code)
        if suggestion_data:
            return suggestion_data.get("doc_url")
        return None

    def get_steps(self, error_code: str) -> List[str]:
        """Get step-by-step recovery instructions for an error code.

        Args:
            error_code: Error code (e.g., "E101")

        Returns:
            List of recovery steps, or empty list if none available
        """
        suggestion_data = self._suggestions.get(error_code)
        if suggestion_data:
            steps: list[str] = suggestion_data.get("steps", [])
            return steps
        return []


# Default embedded recovery suggestion database
DEFAULT_RECOVERY_SUGGESTIONS: Dict[str, Dict] = {
    # Parsing Errors (E1xx)
    "E100": {
        "suggestion": "Check file syntax and encoding. Verify the file is valid YAML/Ansible content.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E100",
        "steps": [
            "Verify file encoding is UTF-8",
            "Check for syntax errors using a YAML validator",
            "Ensure file follows Ansible role structure conventions",
        ],
    },
    "E101": {
        "suggestion": "YAML syntax error detected. Check indentation, quotes, and special characters.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E101",
        "steps": [
            "Verify indentation uses spaces (not tabs)",
            "Check for unmatched quotes or brackets",
            "Validate colons have spaces after them (key: value)",
            "Use a YAML linter (yamllint) to identify issues",
        ],
    },
    "E102": {
        "suggestion": "YAML structure is invalid. Ensure proper key-value pairs and list formatting.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E102",
        "steps": [
            "Check that all keys have corresponding values",
            "Verify list items start with '-' character",
            "Ensure nested structures are properly indented",
        ],
    },
    "E103": {
        "suggestion": "File encoding issue detected. Save file as UTF-8.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E103",
        "steps": [
            "Open file in editor and check encoding",
            "Save file with UTF-8 encoding",
            "Remove any BOM (Byte Order Mark) if present",
        ],
    },
    "E104": {
        "suggestion": "Galaxy meta/main.yml is invalid. Check required fields and format.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E104",
        "steps": [
            "Verify galaxy_info section exists",
            "Check author, description, license fields are present",
            "Validate min_ansible_version format",
            "Ensure platforms list is properly formatted",
        ],
    },
    # Validation Errors (E2xx)
    "E200": {
        "suggestion": "Validation error detected. Check required files and field values.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E200",
        "steps": [
            "Review Ansible role structure requirements",
            "Verify all required files exist",
            "Check field values match expected types",
        ],
    },
    "E201": {
        "suggestion": "Required file is missing. Add the missing file to your role.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E201",
        "steps": [
            "Check error message for specific missing file",
            "Create the required file in the correct location",
            "Follow Ansible role directory structure conventions",
        ],
    },
    "E202": {
        "suggestion": "Required field is missing. Add the field to your configuration.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E202",
        "steps": [
            "Check error message for specific missing field",
            "Add the field with appropriate value",
            "Consult Ansible role metadata documentation",
        ],
    },
    "E203": {
        "suggestion": "Invalid field value. Check type and format requirements.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E203",
        "steps": [
            "Verify field value matches expected type (string, list, dict, etc.)",
            "Check for typos in field values",
            "Consult documentation for valid values",
        ],
    },
    # Generation Errors (E3xx)
    "E300": {
        "suggestion": "Documentation generation failed. Check template and data availability.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E300",
        "steps": [
            "Verify template files are accessible",
            "Check that role data was parsed successfully",
            "Review template syntax for errors",
        ],
    },
    "E301": {
        "suggestion": "Template file not found. Verify template path and availability.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E301",
        "steps": [
            "Check template path in configuration",
            "Verify template file exists",
            "Use --template flag to specify custom template",
        ],
    },
    "E302": {
        "suggestion": "Template syntax error. Review Jinja2 template syntax.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E302",
        "steps": [
            "Check for unclosed Jinja2 tags ({% %}, {{ }})",
            "Verify filter usage and syntax",
            "Test template with minimal data",
        ],
    },
    "E303": {
        "suggestion": "Template rendering failed. Check data availability and template logic.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E303",
        "steps": [
            "Verify all referenced variables exist in role data",
            "Check template conditions and loops",
            "Review error message for missing variables or filters",
        ],
    },
    # I/O Errors (E4xx)
    "E400": {
        "suggestion": "File system operation failed. Check permissions and disk space.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E400",
        "steps": [
            "Verify file/directory permissions",
            "Check available disk space",
            "Ensure path is valid and accessible",
        ],
    },
    "E401": {
        "suggestion": "File not found. Verify the path exists and is accessible.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E401",
        "steps": [
            "Check file path for typos",
            "Verify file exists in specified location",
            "Check current working directory",
        ],
    },
    "E402": {
        "suggestion": "Permission denied. Check file/directory permissions.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E402",
        "steps": [
            "Verify read/write permissions on file/directory",
            "Check ownership of files",
            "Run with appropriate user permissions",
        ],
    },
    "E403": {
        "suggestion": "Disk full. Free up disk space and retry.",
        "doc_url": "https://docs.ansible-doctor.com/errors/E403",
        "steps": [
            "Check available disk space (df -h)",
            "Delete unnecessary files",
            "Use a different output directory with more space",
        ],
    },
    # Warnings (W1xx-W4xx)
    "W100": {
        "suggestion": "Review warning details and consider addressing the issue.",
        "doc_url": "https://docs.ansible-doctor.com/errors/W100",
        "steps": [],
    },
    "W101": {
        "suggestion": "Deprecated syntax detected. Update to current Ansible conventions.",
        "doc_url": "https://docs.ansible-doctor.com/errors/W101",
        "steps": [
            "Review Ansible deprecation notices",
            "Update syntax to current best practices",
            "Test changes with ansible-lint",
        ],
    },
    "W102": {
        "suggestion": "Missing documentation. Add comments or annotations to improve clarity.",
        "doc_url": "https://docs.ansible-doctor.com/errors/W102",
        "steps": [
            "Add YAML comments describing purpose",
            "Use ansible-doctor annotations for detailed docs",
            "Document complex logic and edge cases",
        ],
    },
    "W103": {
        "suggestion": "Undocumented variable. Add description using annotations or defaults/main.yml comments.",
        "doc_url": "https://docs.ansible-doctor.com/errors/W103",
        "steps": [
            "Add @var annotation above variable definition",
            "Include description, type, and default value",
            "Document variable purpose and usage examples",
        ],
    },
}
