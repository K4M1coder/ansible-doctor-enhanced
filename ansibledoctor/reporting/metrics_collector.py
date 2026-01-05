"""
Performance metrics collection module.

This module provides the MetricsCollector class for tracking execution timing
and counters during ansible-doctor operations.

Classes:
    MetricsCollector: Collects phase timing and counter metrics
"""

import time
from typing import Dict

from ansibledoctor.models.execution_report import ExecutionMetrics


class MetricsCollector:
    """Collects execution timing and counter metrics.

    This class tracks:
    - Phase timing using perf_counter for high precision (<5% error)
    - Counters for files, roles, collections, projects, warnings, errors
    - Nested phase timing with "parent.child" notation

    Attributes:
        phase_timing: Dict mapping phase names to duration in seconds
        counters: Dict mapping counter names to integer counts
        _active_phases: Dict tracking start times for active phases

    Example:
        >>> collector = MetricsCollector()
        >>> collector.start_phase("parsing")
        >>> # ... do work ...
        >>> collector.end_phase("parsing")
        >>> collector.increment_counter("files_processed", 3)
        >>> metrics = collector.get_metrics()
        >>> print(metrics.phase_timing["parsing"])
        0.123
    """

    def __init__(self) -> None:
        """Initialize the metrics collector with empty state."""
        self.phase_timing: Dict[str, float] = {}
        self.counters: Dict[str, int] = {
            "files_processed": 0,
            "roles_documented": 0,
            "collections_documented": 0,
            "projects_documented": 0,
            "warnings_count": 0,
            "errors_count": 0,
        }
        self._active_phases: Dict[str, float] = {}

    def start_phase(self, phase_name: str) -> None:
        """Start timing a named phase.

        Args:
            phase_name: Name of the phase to track (e.g., "parsing", "rendering.template")

        Raises:
            ValueError: If the phase is already active

        Example:
            >>> collector.start_phase("parsing")
            >>> collector.start_phase("parsing.role_files")
        """
        if phase_name in self._active_phases:
            raise ValueError(f"Phase '{phase_name}' is already active")
        self._active_phases[phase_name] = time.perf_counter()

    def end_phase(self, phase_name: str) -> None:
        """End timing a named phase and record duration.

        Args:
            phase_name: Name of the phase to end

        Raises:
            ValueError: If the phase was not started

        Example:
            >>> collector.start_phase("parsing")
            >>> # ... do work ...
            >>> collector.end_phase("parsing")
        """
        if phase_name not in self._active_phases:
            raise ValueError(f"Phase '{phase_name}' was not started")

        start_time = self._active_phases.pop(phase_name)
        duration_seconds = time.perf_counter() - start_time
        # Convert to milliseconds (int) to match ExecutionMetrics specification
        duration_ms = int(duration_seconds * 1000)
        self.phase_timing[phase_name] = duration_ms

    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a named counter.

        Args:
            counter_name: Name of the counter (e.g., "files_processed", "roles_documented")
            value: Amount to increment (default: 1)

        Example:
            >>> collector.increment_counter("files_processed")
            >>> collector.increment_counter("roles_documented", 3)
        """
        if counter_name not in self.counters:
            self.counters[counter_name] = 0
        self.counters[counter_name] += value

    def get_metrics(self) -> ExecutionMetrics:
        """Get current metrics as an ExecutionMetrics model.

        Returns:
            ExecutionMetrics: Pydantic model with current metrics state

        Example:
            >>> metrics = collector.get_metrics()
            >>> print(metrics.files_processed)
            5
        """
        return ExecutionMetrics(
            files_processed=self.counters.get("files_processed", 0),
            roles_documented=self.counters.get("roles_documented", 0),
            collections_documented=self.counters.get("collections_documented", 0),
            projects_documented=self.counters.get("projects_documented", 0),
            warnings_count=self.counters.get("warnings_count", 0),
            errors_count=self.counters.get("errors_count", 0),
            phase_timing=self.phase_timing.copy(),
        )
