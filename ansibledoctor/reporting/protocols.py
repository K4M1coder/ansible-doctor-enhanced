"""Protocol definitions for reporting subsystem.

This module defines protocols (interfaces) for the reporting system
following the Dependency Inversion Principle (SOLID). Protocols enable
loose coupling and testability without concrete implementations.
"""

from pathlib import Path
from typing import Protocol

from ansibledoctor.models.execution_report import ExecutionMetrics, ExecutionReport


class ReportGenerator(Protocol):
    """Protocol for execution report generation.

    Defines the interface for creating and writing execution reports
    from execution context. Implementations must provide methods to
    generate reports and write them to files in various formats.
    """

    def generate(self, context: dict) -> ExecutionReport:
        """Generate an execution report from execution context.

        Args:
            context: Dictionary containing execution data (correlation_id,
                    command, status, timing, metrics, warnings, errors)

        Returns:
            ExecutionReport instance with all data populated
        """
        ...

    def write_report(self, report: ExecutionReport, path: Path, format: str = "json") -> None:
        """Write report to file in specified format.

        Args:
            report: ExecutionReport to write
            path: Output file path
            format: Output format ("json", "text", "summary")

        Raises:
            IOError: If file cannot be written
            ValueError: If format is not supported
        """
        ...


class MetricsCollector(Protocol):
    """Protocol for metrics collection during execution.

    Defines the interface for collecting performance metrics including
    phase timing, file counts, and entity counts. Implementations must
    provide thread-safe metric collection.
    """

    def start_phase(self, phase_name: str) -> None:
        """Start timing a named phase.

        Args:
            phase_name: Name of the phase (e.g., "parsing", "rendering")

        Raises:
            ValueError: If phase is already started
        """
        ...

    def end_phase(self, phase_name: str) -> None:
        """End timing a named phase.

        Args:
            phase_name: Name of the phase to end

        Raises:
            ValueError: If phase was not started
        """
        ...

    def increment_counter(self, counter_name: str, value: int = 1) -> None:
        """Increment a named counter.

        Args:
            counter_name: Name of the counter (e.g., "files_processed")
            value: Amount to increment (default: 1)

        Raises:
            ValueError: If value is negative
        """
        ...

    def get_metrics(self) -> ExecutionMetrics:
        """Get collected metrics.

        Returns:
            ExecutionMetrics instance with all collected data
        """
        ...
