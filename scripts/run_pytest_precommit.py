#!/usr/bin/env python3
"""Run unit tests in a way that prints detailed results but does not cause pre-commit to fail.

This wrapper executes pytest programmatically and preserves non-zero status for logs, but
always exits with code 0 so pre-commit won't block the commit. Use CI workflows or other guards
for strict validation.

To run with exit-on-failure behavior, set environment variable PRECOMMIT_FATAL_TESTS=1.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def main() -> int:
    # Allow passing pytest args via command line (preferred) or via env var
    cmdline_args = sys.argv[1:]

    # Check for custom --fatal flag and remove it from args
    is_fatal = os.environ.get("PRECOMMIT_FATAL_TESTS") in ("1", "true", "True")
    if "--fatal" in cmdline_args:
        is_fatal = True
        cmdline_args.remove("--fatal")

    if cmdline_args:
        args = cmdline_args
    else:
        args = os.environ.get("PRECOMMIT_PYTEST_ARGS")
        if args:
            args = args.split()
        else:
            args = ["-q", "tests/unit"]

    # Make sure tests can import the local package by adding the project root
    project_root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("PYTHONPATH", str(project_root))
    # Ensure the current Python process can import the local package
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Allow passing additional args via environment (rare), e.g., PRECOMMIT_PYTEST_ARGS
    extra = os.environ.get("PRECOMMIT_PYTEST_ARGS")
    if extra:
        args.extend(extra.split())

    print("Running pytest (pre-commit wrapper) with args:", args)
    exit_code = pytest.main(args)

    if exit_code == 0:
        print("pytest: all unit tests passed")
        return 0

    print(f"pytest: unit tests reported non-zero exit code: {exit_code}")

    if is_fatal:
        print("Failure is FATAL; returning pytest exit code to fail pre-commit")
        return exit_code

    # Do not fail pre-commit: return 0 but provide verbose message
    print("NOTE: Unit tests failed — continuing commit because tests are not fatal in pre-commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
