"""File system watching and auto-regeneration for ansible-doctor-enhanced.

This module provides watch mode functionality for automatic documentation
regeneration when role files change.

Constitutional Principles:
- Library-First Architecture (Article I)
- Test-Driven Development (Article III)
- Domain-Driven Design (Article X)

Feature 003 - US2: Watch Mode Auto-Regeneration
"""

from ansibledoctor.watcher.monitor import WatchMonitor

__all__ = [
    "WatchMonitor",
]
