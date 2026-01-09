"""
TodoParser for extracting @todo annotations from role files.

Scans all source files in a role to discover TODO comments for
documentation and project planning purposes.

Part of Phase 8 US4 (TODO/Examples extraction).
"""

import re
from pathlib import Path
from typing import Literal

import structlog

from ansibledoctor.models.todo import TodoItem


class TodoParser:
    """
    Parser for extracting @todo annotations from role files.

    Scans all relevant files in a role (YAML, Python, Jinja2 templates)
    to find TODO comments with optional priority indicators.

    Follows DDD Repository pattern for accessing todo annotations.
    """

    # Regex patterns for todo extraction
    TODO_PATTERN = re.compile(
        r"^\s*(?:#|//|{#)\s*@todo(?:\s+\[(\w+)\])?\s*:\s*(.+?)(?:\s*#})?$", re.IGNORECASE
    )

    CONTINUATION_PATTERN = re.compile(r"^\s*(?:#|//)\s+(.+)$")

    # Directories to skip during scanning
    SKIP_DIRS = {
        ".git",
        ".hypothesis",
        "__pycache__",
        "htmlcov",
        ".pytest_cache",
        "node_modules",
        ".tox",
        "venv",
        ".venv",
    }

    # File extensions to scan
    SOURCE_EXTENSIONS = {".yml", ".yaml", ".py", ".j2", ".jinja", ".jinja2"}

    def __init__(self) -> None:
        """Initialize TodoParser."""
        self.logger = structlog.get_logger()

    def parse_file(self, file_path: Path) -> list[TodoItem]:
        """
        Parse a single file for @todo annotations.

        Args:
            file_path: Path to file to scan

        Returns:
            List of TodoItem objects found in the file
        """
        if not file_path.exists():
            self.logger.warning("file_not_found", file=str(file_path))
            return []

        try:
            # Try to read as text
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as exc:
            self.logger.debug(
                "file_read_error",
                file=str(file_path),
                error=type(exc).__name__,
            )
            return []

        todos: list[TodoItem] = []
        lines = content.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            match = self.TODO_PATTERN.match(line)

            if match:
                priority = match.group(1)  # Optional priority
                description = match.group(2).strip()
                line_number = i + 1  # 1-indexed

                # Check for multiline continuation (must be indented comment on next line)
                i += 1
                while i < len(lines):
                    cont_match = self.CONTINUATION_PATTERN.match(lines[i])
                    # Only continue if line starts with comment AND has leading whitespace (indentation)
                    if (
                        cont_match
                        and lines[i].lstrip() != lines[i]  # Has indentation
                        and not lines[i].strip().startswith(("---", "var:", "-", "@"))
                    ):
                        # Continuation line
                        description += " " + cont_match.group(1).strip()
                        i += 1
                    else:
                        break

                # Create TodoItem
                try:
                    priority_value: Literal["low", "medium", "high", "critical"] | None = None
                    if priority:
                        priority_lower = priority.lower()
                        if priority_lower in {"low", "medium", "high", "critical"}:
                            priority_value = priority_lower  # type: ignore[assignment]

                    todo = TodoItem(
                        description=description,
                        file_path=str(file_path),
                        line_number=line_number,
                        priority=priority_value,
                    )
                    todos.append(todo)
                except Exception as exc:
                    self.logger.warning(
                        "todo_creation_failed",
                        file=str(file_path),
                        line=line_number,
                        error=str(exc),
                    )
            else:
                i += 1

        return todos

    def parse_directory(self, directory: Path) -> list[TodoItem]:
        """
        Parse all source files in a directory for @todo annotations.

        Args:
            directory: Path to directory to scan

        Returns:
            List of all TodoItem objects found
        """
        todos: list[TodoItem] = []

        for file_path in directory.rglob("*"):
            # Skip directories and non-source files
            if file_path.is_dir():
                continue

            if file_path.suffix not in self.SOURCE_EXTENSIONS:
                continue

            # Skip excluded directories
            if any(skip_dir in file_path.parts for skip_dir in self.SKIP_DIRS):
                continue

            file_todos = self.parse_file(file_path)
            todos.extend(file_todos)

        return todos

    def parse_role(self, role_path: Path) -> list[TodoItem]:
        """
        Parse entire role directory for @todo annotations.

        Scans all standard Ansible role directories (tasks, handlers,
        defaults, vars, templates, etc.) for TODO comments.

        Args:
            role_path: Path to role root directory

        Returns:
            List of TodoItem objects with paths relative to role root
        """
        if not role_path.exists():
            self.logger.warning("role_path_not_found", role=str(role_path))
            return []

        todos = self.parse_directory(role_path)

        # Make paths relative to role root
        for todo in todos:
            try:
                abs_path = Path(todo.file_path)
                rel_path = abs_path.relative_to(role_path)
                # Create new TodoItem with relative path (immutable)
                todo = TodoItem(
                    description=todo.description,
                    file_path=str(rel_path).replace("\\", "/"),  # Use forward slashes
                    line_number=todo.line_number,
                    priority=todo.priority,
                )
                # Update in list
                idx = todos.index(todo) if todo in todos else None
                if idx is not None:
                    todos[idx] = todo
            except (ValueError, Exception) as exc:
                # Path is not relative to role_path, keep as-is
                self.logger.debug(
                    "path_not_relative",
                    file=todo.file_path,
                    role=str(role_path),
                    error=str(exc),
                )

        # Recreate all todos with relative paths
        relative_todos = []
        for todo in todos:
            try:
                abs_path = (
                    Path(todo.file_path)
                    if not Path(todo.file_path).is_absolute()
                    else Path(todo.file_path)
                )
                if abs_path.is_absolute():
                    rel_path = abs_path.relative_to(role_path)
                else:
                    rel_path = abs_path

                relative_todo = TodoItem(
                    description=todo.description,
                    file_path=str(rel_path).replace("\\", "/"),
                    line_number=todo.line_number,
                    priority=todo.priority,
                )
                relative_todos.append(relative_todo)
            except ValueError:
                # Can't make relative, keep original
                relative_todos.append(todo)

        self.logger.info(
            "role_todos_parsed",
            role=role_path.name,
            todo_count=len(relative_todos),
        )

        return relative_todos
