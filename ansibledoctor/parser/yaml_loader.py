"""
YAML file loader implementation using ruamel.yaml.

Following Constitution Article X (DDD): Anti-Corruption Layer shielding domain
from external YAML library implementation details.
"""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class RuamelYAMLLoader:
    """
    Concrete implementation of YAMLLoader protocol using ruamel.yaml.

    Implements Anti-Corruption Layer pattern: isolates ruamel.yaml specifics
    from the rest of the codebase, enabling easy replacement if needed.
    """

    def __init__(self) -> None:
        """Initialize YAML parser with safe loading and comment preservation."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False

    def load_file(self, file_path: Path) -> dict[str, Any] | list[Any]:
        """
        Load and parse a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML content as dictionary or list

        Raises:
            ParsingError: If file not found or YAML syntax is invalid
        """
        if not file_path.exists():
            raise ParsingError(
                f"YAML file not found: {file_path}",
                context={"file_path": str(file_path)},
                suggestion=f"Check that the file exists at {file_path}",
            )

        try:
            logger.debug("loading_yaml_file", file_path=str(file_path))
            # Create a new YAML parser per call to maintain thread-safety.
            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.default_flow_style = False
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.load(f)

            # Handle empty files
            if data is None:
                logger.warning("empty_yaml_file", file_path=str(file_path))
                return {}

            logger.info(
                "yaml_file_loaded",
                file_path=str(file_path),
                keys_count=len(data) if isinstance(data, dict) else 0,
            )
            # Return data as-is (can be dict or list for tasks)
            if isinstance(data, (dict, list)):
                return data
            return {}

        except Exception as e:
            logger.error(
                "yaml_parsing_failed",
                file_path=str(file_path),
                error=str(e),
            )
            raise ParsingError(
                f"Failed to parse YAML file: {file_path}",
                context={"file_path": str(file_path), "error": str(e)},
                suggestion="Check YAML syntax using a validator or 'yamllint' tool",
            ) from e

    def load_with_comments(self, file_path: Path) -> tuple[dict[str, Any], list[str]]:
        """
        Load YAML file preserving comments for annotation extraction.

        Args:
            file_path: Path to YAML file

        Returns:
            Tuple of (parsed_content, comment_lines)

        Raises:
            ParsingError: If file not found or YAML syntax is invalid
        """
        if not file_path.exists():
            raise ParsingError(
                f"YAML file not found: {file_path}",
                context={"file_path": str(file_path)},
                suggestion=f"Check that the file exists at {file_path}",
            )

        try:
            logger.debug("loading_yaml_with_comments", file_path=str(file_path))

            # Load parsed data
            # Create a fresh YAML instance for thread-safe parsing
            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.default_flow_style = False
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.load(f)

            # Extract comments from raw file
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            comment_lines = [line.strip() for line in lines if line.strip().startswith("#")]

            parsed_data = dict(data) if isinstance(data, (dict, CommentedMap)) else {}

            logger.info(
                "yaml_with_comments_loaded",
                file_path=str(file_path),
                comment_count=len(comment_lines),
                keys_count=len(parsed_data),
            )

            return parsed_data, comment_lines

        except Exception as e:
            logger.error(
                "yaml_parsing_with_comments_failed",
                file_path=str(file_path),
                error=str(e),
            )
            raise ParsingError(
                f"Failed to parse YAML file with comments: {file_path}",
                context={"file_path": str(file_path), "error": str(e)},
                suggestion="Check YAML syntax using a validator or 'yamllint' tool",
            ) from e

    def dump_to_string(self, data: dict[str, Any]) -> str:
        """
        Serialize dictionary to YAML string.

        Utility method for testing and output generation.

        Args:
            data: Dictionary to serialize

        Returns:
            YAML formatted string
        """
        from io import StringIO

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        stream = StringIO()
        yaml.dump(data, stream)
        return stream.getvalue()
