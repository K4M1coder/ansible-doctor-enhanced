#!/usr/bin/env bash
# Run CLI from source (Unix)
# Usage: ./scripts/run_cli.sh -- --help
if command -v poetry >/dev/null 2>&1; then
  poetry run python -m ansibledoctor.cli "$@"
else
  python -m ansibledoctor.cli "$@"
fi
