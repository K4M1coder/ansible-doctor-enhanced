"""Watch monitor for file system changes.

Feature 003 - US2: Watch Mode Auto-Regeneration
T021: WatchMonitor class with watchdog.observers.Observer
"""

from pathlib import Path
from typing import Callable

from watchdog.observers import Observer

from ansibledoctor.watcher.handler import FileChangeHandler


class WatchMonitor:
    """Monitor file system for changes and trigger documentation regeneration.

    Watches specified directories for file changes and triggers callbacks
    with debouncing to avoid excessive regenerations.

    Attributes:
        role_path: Path to Ansible role directory being watched
        callback: Function to call when files change (after debounce)
        debounce_ms: Milliseconds to wait before triggering callback
        observer: Watchdog observer instance
        handler: File change event handler
        debouncer: Debouncer for rate limiting callbacks

    Example:
        >>> def regenerate_docs(changed_file):
        ...     print(f"Regenerating docs for {changed_file}")
        >>> monitor = WatchMonitor(Path("./my-role"), regenerate_docs)
        >>> monitor.start()  # Starts watching in background
        >>> # ... files change, callback triggered after debounce ...
        >>> monitor.stop()  # Stops watching

    Feature: US2 - Watch Mode Auto-Regeneration
    """

    def __init__(
        self,
        role_path: Path,
        callback: Callable[[], None],
        debounce_delay: float = 0.5,
        exclude_patterns: list[str] | None = None,
    ):
        """Initialize watch monitor.

        Args:
            role_path: Path to role directory to watch
            callback: Function to call when files change
            debounce_delay: Debounce delay in seconds (default: 0.5)
            exclude_patterns: File patterns to exclude
        """
        self.role_path = Path(role_path)
        self.callback = callback
        self.exclude_patterns = exclude_patterns or []

        # Create handler and observer
        self.handler = FileChangeHandler(
            callback=callback, debounce_delay=debounce_delay, exclude_patterns=self.exclude_patterns
        )
        self.observer = Observer()

        # Schedule observer to watch role directory recursively
        self.observer.schedule(self.handler, str(self.role_path), recursive=True)

    def start(self) -> None:
        """Start watching for file changes.

        Starts the watchdog observer in a background thread.
        """
        self.observer.start()

    def stop(self) -> None:
        """Stop watching for file changes.

        Gracefully stops the watchdog observer and cleans up resources.
        """
        self.observer.stop()
        self.observer.join(timeout=2.0)

    def is_running(self) -> bool:
        """Check if monitor is currently watching.

        Returns:
            True if observer is running, False otherwise
        """
        return self.observer.is_alive()
