"""Performance test configuration and result collection."""

import json
from pathlib import Path

import pytest

# Global dictionary to store performance results
_perf_results = {}


def pytest_configure(config):
    """Initialize performance result storage."""
    global _perf_results
    _perf_results = {}


def pytest_unconfigure(config):
    """Save performance results to JSON file after all tests."""
    if _perf_results:
        output_file = Path("tests/tmp/performance-results.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(_perf_results, f, indent=2)
        print(f"\nPerformance results saved to {output_file}")


@pytest.fixture
def record_perf():
    """Fixture to record performance metrics."""

    def _record(test_name: str, time_ms: float, target_ms: float, max_ms: float):
        """Record a performance metric.

        Args:
            test_name: Name of the test (e.g., 'small_role')
            time_ms: Actual time in milliseconds
            target_ms: Target threshold in milliseconds
            max_ms: Maximum acceptable threshold in milliseconds
        """
        status = "pass"
        if time_ms > max_ms:
            status = "fail"
        elif time_ms > target_ms:
            status = "warn"

        _perf_results[test_name] = {
            "time_ms": round(time_ms, 2),
            "target_ms": target_ms,
            "max_ms": max_ms,
            "status": status,
        }

    return _record
