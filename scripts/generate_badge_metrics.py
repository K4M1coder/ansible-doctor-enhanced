#!/usr/bin/env python3
"""Generate badge JSON files from test/coverage/quality metrics.

This script creates Shields.io-compatible JSON endpoint files
for dynamic badges displaying project health metrics.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def generate_coverage_badge(coverage_data: dict[str, Any]) -> dict[str, Any]:
    """Generate coverage badge JSON.

    Args:
        coverage_data: pytest-cov JSON output

    Returns:
        Shields.io badge JSON
    """
    try:
        percent = float(coverage_data["totals"]["percent_covered"])
    except (KeyError, ValueError):
        return {
            "schemaVersion": 1,
            "label": "coverage",
            "message": "unknown",
            "color": "lightgrey",
            "namedLogo": "pytest",
        }

    # Dynamic color based on thresholds
    if percent < 80:
        color = "red"
    elif percent < 90:
        color = "orange"
    else:
        color = "brightgreen"

    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent:.1f}%",
        "color": color,
        "namedLogo": "pytest",
        "style": "flat-square",
    }


def generate_mypy_badge(precommit_data: dict[str, Any]) -> dict[str, Any]:
    """Generate mypy type checking badge JSON."""
    status = precommit_data.get("tools", {}).get("mypy", "unknown")
    files = precommit_data.get("mypy_files_checked", 0)
    errors = precommit_data.get("mypy_errors", 0)

    if status == "passed" and errors == 0:
        return {
            "schemaVersion": 1,
            "label": "mypy",
            "message": f"✨ 0 errors ({files} files)",
            "color": "brightgreen",
            "namedLogo": "python",
            "style": "flat-square",
        }
    elif status == "passed":
        return {
            "schemaVersion": 1,
            "label": "mypy",
            "message": f"{errors} errors",
            "color": "orange",
            "namedLogo": "python",
            "style": "flat-square",
        }
    else:
        return {
            "schemaVersion": 1,
            "label": "mypy",
            "message": "errors found",
            "color": "red",
            "namedLogo": "python",
            "style": "flat-square",
        }


def generate_tool_badge(
    tool_name: str, precommit_data: dict[str, Any], logo: str | None = None
) -> dict[str, Any]:
    """Generate badge for individual tool (black, isort, ruff)."""
    status = precommit_data.get("tools", {}).get(tool_name, "unknown")

    if status == "passed":
        color = "brightgreen"
        message = "passing"
    elif status == "failed":
        color = "red"
        message = "failing"
    elif status == "skipped":
        color = "yellow"
        message = "skipped"
    else:
        color = "lightgrey"
        message = "unknown"

    badge = {
        "schemaVersion": 1,
        "label": tool_name,
        "message": message,
        "color": color,
        "style": "flat-square",
    }

    if logo:
        badge["namedLogo"] = logo

    return badge


def generate_tests_badge(precommit_data: dict[str, Any]) -> dict[str, Any]:
    """Generate tests summary badge."""
    passed = precommit_data.get("tests_passed", 0)
    skipped = precommit_data.get("tests_skipped", 0)
    failed = precommit_data.get("tests_failed", 0)

    if failed > 0:
        color = "red"
        message = f"{failed} failed, {passed} passed"
    elif passed > 0:
        color = "brightgreen"
        message = f"{passed} passed"
        if skipped > 0:
            message += f", {skipped} skipped"
    else:
        color = "lightgrey"
        message = "no tests"

    return {
        "schemaVersion": 1,
        "label": "tests",
        "message": message,
        "color": color,
        "namedLogo": "pytest",
        "style": "flat-square",
    }


def generate_python_version_badge(pyproject_path: str) -> dict[str, Any]:
    """Generate Python version badge from pyproject.toml."""
    try:
        import tomllib

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        python_version = data["tool"]["poetry"]["dependencies"]["python"]
        # Clean up version string (e.g., "^3.11" -> "3.11+")
        version_clean = python_version.replace("^", "").replace("~", "")
        if "," in version_clean:
            # Handle ranges like ">=3.11,<3.14"
            parts = version_clean.split(",")
            version_clean = parts[0].replace(">=", "").replace(">", "")

        display = f"{version_clean}+" if "^" in python_version else version_clean

        return {
            "schemaVersion": 1,
            "label": "python",
            "message": display,
            "color": "blue",
            "namedLogo": "python",
            "style": "flat-square",
        }
    except Exception as e:
        print(f"Warning: Could not parse Python version: {e}", file=sys.stderr)
        return {
            "schemaVersion": 1,
            "label": "python",
            "message": "3.11+",
            "color": "blue",
            "namedLogo": "python",
            "style": "flat-square",
        }


def generate_package_version_badge(pyproject_path: str) -> dict[str, Any]:
    """Generate package version badge from pyproject.toml."""
    try:
        import tomllib

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        version = data["tool"]["poetry"]["version"]

        return {
            "schemaVersion": 1,
            "label": "version",
            "message": f"v{version}",
            "color": "blue",
            "style": "flat-square",
        }
    except Exception as e:
        print(f"Warning: Could not parse package version: {e}", file=sys.stderr)
        return {
            "schemaVersion": 1,
            "label": "version",
            "message": "unknown",
            "color": "lightgrey",
            "style": "flat-square",
        }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate badge JSON files for Shields.io")
    parser.add_argument("--coverage", required=False, help="Path to coverage.json from pytest-cov")
    parser.add_argument("--precommit", required=False, help="Path to precommit-metrics.json")
    parser.add_argument("--pyproject", required=True, help="Path to pyproject.toml")
    parser.add_argument("--output", required=True, help="Output directory for badge JSON files")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load input data
    coverage_data = {}
    if args.coverage and Path(args.coverage).exists():
        with open(args.coverage, encoding="utf-8") as f:
            coverage_data = json.load(f)

    precommit_data = {}
    if args.precommit and Path(args.precommit).exists():
        with open(args.precommit, encoding="utf-8") as f:
            precommit_data = json.load(f)

    # Generate all badges
    badges = {
        "python-version.json": generate_python_version_badge(args.pyproject),
        "package-version.json": generate_package_version_badge(args.pyproject),
    }

    if coverage_data:
        badges["coverage.json"] = generate_coverage_badge(coverage_data)

    if precommit_data:
        badges["mypy.json"] = generate_mypy_badge(precommit_data)
        badges["black.json"] = generate_tool_badge("black", precommit_data)
        badges["isort.json"] = generate_tool_badge("isort", precommit_data)
        badges["ruff.json"] = generate_tool_badge("ruff", precommit_data, "ruff")
        badges["tests.json"] = generate_tests_badge(precommit_data)

    # Write badge files
    for filename, badge_data in badges.items():
        output_path = output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(badge_data, f, indent=2)
        print(f"Generated: {output_path}")

    print(f"\n✓ Generated {len(badges)} badge files in {output_dir}")


if __name__ == "__main__":
    main()
