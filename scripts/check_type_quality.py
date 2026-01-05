#!/usr/bin/env python3
"""Type quality checker - generates a report of mypy errors by category.

This script runs mypy and categorizes the errors to help prioritize fixes.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def run_mypy() -> list[str]:
    """Run mypy and return output lines."""
    cmd = [
        "mypy",
        "ansibledoctor",
        "--config-file=pyproject.toml",
        "--no-error-summary",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.splitlines()


def categorize_errors(lines: list[str]) -> dict[str, list[str]]:
    """Categorize mypy errors by error code."""
    categories = defaultdict(list)

    for line in lines:
        if ": error:" in line:
            # Extract error code from [error-code]
            if "[" in line and "]" in line:
                error_code = line.split("[")[-1].split("]")[0]
                categories[error_code].append(line)
            else:
                categories["unknown"].append(line)

    return categories


def print_report(categories: dict[str, list[str]]) -> None:
    """Print a categorized error report."""
    total_errors = sum(len(errors) for errors in categories.values())

    print(f"\n{'='*80}")
    print(f"TYPE QUALITY REPORT - Total errors: {total_errors}")
    print(f"{'='*80}\n")

    # Sort by error count (descending)
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)

    for error_code, errors in sorted_categories:
        print(f"\n{error_code.upper()} - {len(errors)} errors")
        print("-" * 80)

        # Show first 5 examples
        for error in errors[:5]:
            # Extract file and line number
            parts = error.split(":")
            if len(parts) >= 3:
                file = parts[0]
                line = parts[1]
                message = ":".join(parts[2:])
                print(f"  {Path(file).name}:{line}{message}")

        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    print(f"\n{'='*80}")
    print("Priority fixes:")
    print("  1. var-annotated: Add type annotations to variables")
    print("  2. arg-type: Fix function argument types")
    print("  3. assignment: Fix type mismatches in assignments")
    print("  4. attr-defined: Fix attribute access on wrong types")
    print("  5. import-not-found: Add stub packages or ignore external deps")
    print(f"{'='*80}\n")


def main() -> int:
    """Main entry point."""
    print("Running mypy type checker...")

    lines = run_mypy()
    categories = categorize_errors(lines)

    if not categories:
        print("\n✅ No type errors found! Code is type-safe.")
        return 0

    print_report(categories)

    # Return non-zero if errors found
    return 1 if categories else 0


if __name__ == "__main__":
    sys.exit(main())
