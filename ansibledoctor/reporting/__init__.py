"""Execution reporting subsystem for ansible-doctor.

This module provides comprehensive execution reporting capabilities including:
- Structured execution reports (JSON, text, summary formats)
- Performance metrics collection (timing, counts, throughput)
- Report generation and serialization
- Metrics collection with phase timing

The reporting system extends the existing structlog infrastructure to provide
machine-readable reports for CI/CD integration and human-readable summaries
for documentation maintainers.
"""

from ansibledoctor.reporting import serializers
from ansibledoctor.reporting.report_generator import ReportGenerator

__all__ = [
    "ReportGenerator",
    "serializers",
]
