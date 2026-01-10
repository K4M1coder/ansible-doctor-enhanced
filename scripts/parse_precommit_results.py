#!/usr/bin/env python3
"""Parse pre-commit output and extract metrics for badge generation.

This script analyzes the output from pre-commit hooks and extracts
status information for each tool (black, isort, ruff, mypy, tests).
"""

import json
import re
import sys
from typing import Any


def parse_precommit(output_file: str) -> dict[str, Any]:
    """Parse pre-commit output and extract tool statuses.

    Args:
        output_file: Path to file containing pre-commit output

    Returns:
        Dictionary with status for each tool and additional metrics
    """
    try:
        with open(output_file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {output_file}", file=sys.stderr)
        return _default_metrics()

    metrics: dict[str, Any] = {
        "timestamp": None,
        "overall_status": "passed",
        "tools": {},
        "mypy_files_checked": 0,
        "mypy_errors": 0,
        "tests_passed": 0,
        "tests_skipped": 0,
        "tests_failed": 0,
    }

    # Parse individual tool results
    tools = ["black", "isort", "ruff", "mypy", "pytest-unit"]

    for tool in tools:
        # Match patterns like "black...Passed" or "black...Failed"
        passed_pattern = rf"{tool}.*?Passed"
        failed_pattern = rf"{tool}.*?Failed"
        skipped_pattern = rf"{tool}.*?Skipped"

        if re.search(passed_pattern, content, re.IGNORECASE):
            metrics["tools"][tool] = "passed"
        elif re.search(failed_pattern, content, re.IGNORECASE):
            metrics["tools"][tool] = "failed"
            metrics["overall_status"] = "failed"
        elif re.search(skipped_pattern, content, re.IGNORECASE):
            metrics["tools"][tool] = "skipped"
        else:
            metrics["tools"][tool] = "unknown"

    # Extract mypy details
    mypy_match = re.search(r"Success: no issues found in (\d+) source files", content)
    if mypy_match:
        metrics["mypy_files_checked"] = int(mypy_match.group(1))
        metrics["mypy_errors"] = 0
    else:
        # Try to find error count
        error_match = re.search(r"Found (\d+) errors? in (\d+) files?", content)
        if error_match:
            metrics["mypy_errors"] = int(error_match.group(1))
            metrics["mypy_files_checked"] = int(error_match.group(2))

    # Extract pytest results
    pytest_match = re.search(r"(\d+) passed(?:, (\d+) skipped)?(?:, (\d+) failed)?", content)
    if pytest_match:
        metrics["tests_passed"] = int(pytest_match.group(1))
        metrics["tests_skipped"] = int(pytest_match.group(2) or 0)
        metrics["tests_failed"] = int(pytest_match.group(3) or 0)

    return metrics


def _default_metrics() -> dict[str, Any]:
    """Return default metrics when parsing fails."""
    return {
        "timestamp": None,
        "overall_status": "unknown",
        "tools": {
            "black": "unknown",
            "isort": "unknown",
            "ruff": "unknown",
            "mypy": "unknown",
            "pytest-unit": "unknown",
        },
        "mypy_files_checked": 0,
        "mypy_errors": 0,
        "tests_passed": 0,
        "tests_skipped": 0,
        "tests_failed": 0,
    }


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <precommit-output-file>", file=sys.stderr)
        sys.exit(1)

    output_file = sys.argv[1]
    metrics = parse_precommit(output_file)

    # Output JSON to stdout
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
