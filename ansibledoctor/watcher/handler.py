"""File system event handler for watchdog.

Feature 003 - US2: Watch Mode Auto-Regeneration
T020: FileChangeHandler extending watchdog.events.FileSystemEventHandler
"""

import fnmatch
from pathlib import Path
from typing import Any, Callable

from watchdog.events import FileSystemEventHandler

from ansibledoctor.watcher.debouncer import Debouncer


class FileChangeHandler(FileSystemEventHandler):
    """Handle file system change events from watchdog observer.

    Filters relevant file changes (meta/, defaults/, vars/, tasks/) and
    triggers callback via debouncer to avoid excessive regenerations.

    Attributes:
        callback: Function to call when relevant files change
        watched_patterns: File patterns to monitor

    Example:
        >>> def on_change(file_path):
        ...     print(f"File changed: {file_path}")
        >>> handler = FileChangeHandler(on_change)
        >>> # Used with watchdog Observer

    Feature: US2 - Watch Mode Auto-Regeneration
    """

    def __init__(
        self,
        callback: Callable[[], None],
        debounce_delay: float = 0.5,
        exclude_patterns: list[str] | None = None,
    ):
        """Initialize file change handler.

        Args:
            callback: Function to call when monitored files change
            debounce_delay: Delay in seconds before calling callback (default: 0.5)
            exclude_patterns: File patterns to exclude (e.g., *.pyc, __pycache__)
        """
        super().__init__()
        self.debouncer = Debouncer(callback, delay=debounce_delay)
        self.exclude_patterns = exclude_patterns or []

    def on_modified(self, event: Any) -> None:
        """Handle file modification events.

        Args:
            event: Watchdog file system event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if self._is_relevant_file(file_path):
            self.debouncer.trigger()

    def on_created(self, event: Any) -> None:
        """Handle file creation events.

        Args:
            event: Watchdog file system event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if self._is_relevant_file(file_path):
            self.debouncer.trigger()

    def _is_relevant_file(self, file_path: Path) -> bool:
        """Check if file path is relevant for documentation generation.

        Args:
            file_path: Path to file that changed

        Returns:
            True if file should trigger regeneration, False otherwise
        """
        # Check exclude patterns
        filename = file_path.name
        filepath_str = str(file_path)

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filepath_str, f"*{pattern}*"):
                return False

        # Check if it's a YAML file (most role files are YAML)
        if file_path.suffix in {".yml", ".yaml"}:
            return True

        # Check if it's in a relevant directory
        relevant_dirs = {"defaults", "vars", "tasks", "handlers", "meta"}
        for parent in file_path.parents:
            if parent.name in relevant_dirs:
                return True

        # Check if it's a config file
        if file_path.name in {".ansibledoctor.yml", ".ansibledoctor.yaml"}:
            return True

        return False
