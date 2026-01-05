"""Unit tests for MetricsCollector class.

Tests the metrics collection system for tracking performance timing,
file counts, and phase execution. Following TDD methodology - these tests
are written BEFORE implementation (RED phase).
"""

import time
from unittest.mock import Mock, patch

import pytest

from ansibledoctor.models.execution_report import ExecutionMetrics
from ansibledoctor.reporting.metrics_collector import MetricsCollector


class TestMetricsCollectorPhaseTiming:
    """T029: Unit test for MetricsCollector phase timing."""

    def test_start_and_end_phase_records_duration(self):
        """Verify start_phase/end_phase records timing in phase_timing dict."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.start_phase("parsing")
        time.sleep(0.01)  # 10ms delay
        collector.end_phase("parsing")
        
        # Assert
        metrics = collector.get_metrics()
        assert "parsing" in metrics.phase_timing
        assert metrics.phase_timing["parsing"] >= 10  # At least 10ms
        assert metrics.phase_timing["parsing"] < 50   # Less than 50ms (sanity check)

    def test_multiple_phases_tracked_independently(self):
        """Verify multiple phases are tracked with separate timings."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.start_phase("parsing")
        time.sleep(0.01)  # 10ms
        collector.end_phase("parsing")
        
        collector.start_phase("rendering")
        time.sleep(0.02)  # 20ms
        collector.end_phase("rendering")
        
        # Assert
        metrics = collector.get_metrics()
        assert "parsing" in metrics.phase_timing
        assert "rendering" in metrics.phase_timing
        assert metrics.phase_timing["parsing"] >= 10
        assert metrics.phase_timing["rendering"] >= 20
        assert metrics.phase_timing["rendering"] > metrics.phase_timing["parsing"]

    def test_end_phase_without_start_raises_error(self):
        """Verify ending a phase without starting it raises ValueError."""
        # Arrange
        collector = MetricsCollector()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Phase 'parsing' was not started"):
            collector.end_phase("parsing")


class TestMetricsCollectorCounters:
    """T030: Unit test for MetricsCollector counter increments."""

    def test_increment_counter_increments_by_default_value(self):
        """Verify increment_counter adds 1 by default."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.increment_counter("files_processed")
        collector.increment_counter("files_processed")
        collector.increment_counter("files_processed")
        
        # Assert
        metrics = collector.get_metrics()
        assert metrics.files_processed == 3

    def test_increment_counter_with_custom_value(self):
        """Verify increment_counter adds custom values."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.increment_counter("files_processed", 5)
        collector.increment_counter("files_processed", 3)
        
        # Assert
        metrics = collector.get_metrics()
        assert metrics.files_processed == 8

    def test_increment_multiple_counters_independently(self):
        """Verify different counters are tracked independently."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.increment_counter("files_processed", 10)
        collector.increment_counter("roles_documented", 3)
        collector.increment_counter("collections_documented", 2)
        collector.increment_counter("warnings_count", 5)
        
        # Assert
        metrics = collector.get_metrics()
        assert metrics.files_processed == 10
        assert metrics.roles_documented == 3
        assert metrics.collections_documented == 2
        assert metrics.warnings_count == 5
        assert metrics.errors_count == 0  # Not incremented


class TestNestedPhaseTiming:
    """T031: Unit test for nested phase timing (parsing → file_parsing)."""

    def test_nested_phases_tracked_separately(self):
        """Verify nested phases (parent.child) are tracked independently."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.start_phase("parsing")
        time.sleep(0.01)  # 10ms
        
        collector.start_phase("parsing.file_parsing")
        time.sleep(0.01)  # 10ms
        collector.end_phase("parsing.file_parsing")
        
        collector.end_phase("parsing")
        
        # Assert
        metrics = collector.get_metrics()
        assert "parsing" in metrics.phase_timing
        assert "parsing.file_parsing" in metrics.phase_timing
        # Parsing should be >= file_parsing since it includes it
        assert metrics.phase_timing["parsing"] >= metrics.phase_timing["parsing.file_parsing"]

    def test_multiple_nested_phases_in_same_parent(self):
        """Verify multiple nested phases within same parent are tracked."""
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.start_phase("generation")
        
        collector.start_phase("generation.template_loading")
        time.sleep(0.01)
        collector.end_phase("generation.template_loading")
        
        collector.start_phase("generation.rendering")
        time.sleep(0.01)
        collector.end_phase("generation.rendering")
        
        collector.end_phase("generation")
        
        # Assert
        metrics = collector.get_metrics()
        assert "generation" in metrics.phase_timing
        assert "generation.template_loading" in metrics.phase_timing
        assert "generation.rendering" in metrics.phase_timing


class TestMetricsTimingAccuracy:
    """T032: Unit test for metrics timing accuracy (<5% error) using mocked time."""

    @patch('ansibledoctor.reporting.metrics_collector.perf_counter')
    def test_timing_accuracy_with_mocked_time(self, mock_perf_counter):
        """Verify timing calculations are accurate when using mocked time."""
        # Arrange
        collector = MetricsCollector()
        # Mock time to return exact values: start=0.0, end=0.150 (150ms)
        mock_perf_counter.side_effect = [0.0, 0.150, 0.150, 0.250]  # Two phases
        
        # Act
        collector.start_phase("parsing")
        collector.end_phase("parsing")
        
        collector.start_phase("rendering")
        collector.end_phase("rendering")
        
        # Assert
        metrics = collector.get_metrics()
        assert metrics.phase_timing["parsing"] == 150  # Exactly 150ms
        assert metrics.phase_timing["rendering"] == 100  # Exactly 100ms

    def test_real_timing_has_reasonable_accuracy(self):
        """Verify real timing is reasonably accurate (within 10% for 100ms)."""
        # Arrange
        collector = MetricsCollector()
        expected_duration_ms = 100
        
        # Act
        collector.start_phase("test_phase")
        time.sleep(expected_duration_ms / 1000.0)  # Convert to seconds
        collector.end_phase("test_phase")
        
        # Assert
        metrics = collector.get_metrics()
        actual_duration = metrics.phase_timing["test_phase"]
        # Allow 10% variance for real timing
        assert abs(actual_duration - expected_duration_ms) <= expected_duration_ms * 0.10
