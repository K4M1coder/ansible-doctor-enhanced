"""Handler parser for Ansible roles (Spec 001, User Story 5)."""

from pathlib import Path
from typing import Any

from ansibledoctor.models.handler import Handler
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.parser.yaml_utils import extract_tags_from_yaml
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class HandlerParser:
    """Parser for Ansible handler files.

    Extracts handler definitions from handlers/*.yml files,
    including tags and listen directives.
    """

    def __init__(self, role_path: str):
        """Initialize the handler parser.

        Args:
            role_path: Path to the Ansible role directory
        """
        self.role_path = Path(role_path)
        self.handlers_dir = self.role_path / "handlers"
        self.handlers: list[Handler] = []
        self.yaml_loader = RuamelYAMLLoader()

    def parse(self) -> list[Handler]:
        """Parse all handler files in the handlers/ directory.

        Returns:
            List of Handler objects
        """
        if not self.handlers_dir.exists():
            logger.debug(f"No handlers directory found at {self.handlers_dir}")
            return []

        main_file = self.handlers_dir / "main.yml"
        if not main_file.exists():
            logger.debug(f"No handlers/main.yml found at {main_file}")
            return []

        self._parse_handler_file(main_file)

        logger.info(f"Parsed {len(self.handlers)} handlers from {self.role_path}")
        return self.handlers

    def _parse_handler_file(self, file_path: Path, visited: set[Path] | None = None) -> None:
        """Parse a single handler file and follow includes.

        Args:
            file_path: Path to the handler YAML file
            visited: Set of already visited files (to prevent circular includes)
        """
        if visited is None:
            visited = set()

        if file_path in visited:
            logger.warning(f"Circular include detected: {file_path}")
            return

        visited.add(file_path)

        try:
            data = self.yaml_loader.load_file(file_path)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return

        if not data or not isinstance(data, list):
            return

        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            # Check for includes
            if "include_tasks" in item or "import_tasks" in item:
                include_file = item.get("include_tasks") or item.get("import_tasks")
                if include_file:
                    include_path = file_path.parent / include_file
                    if include_path.exists():
                        self._parse_handler_file(include_path, visited)
                continue

            # Parse handler definition
            if "name" in item:
                handler = self._extract_handler(item, file_path, idx + 1)
                if handler:
                    self.handlers.append(handler)

    def _extract_handler(
        self, handler_data: dict[str, Any], file_path: Path, line_number: int
    ) -> Handler | None:
        """Extract a Handler object from handler data.

        Args:
            handler_data: Handler dictionary from YAML
            file_path: Source file path
            line_number: Approximate line number

        Returns:
            Handler object or None if invalid
        """
        name = handler_data.get("name")
        if not name:
            return None

        # Extract tags using shared utility
        tags = extract_tags_from_yaml(handler_data.get("tags"))

        # Extract listen directive
        listen = handler_data.get("listen")

        return Handler(
            name=name,
            tags=tags,
            listen=listen,
            file_path=str(file_path.relative_to(self.role_path)),
            line_number=line_number,
        )
