#!/usr/bin/env bash
# Run test suite quickly (Unix)
# Usage: ./scripts/run_tests.sh unit|integration|all
scope="${1:-unit}"
case $scope in
  unit) tests_dir="tests/unit" ;;
  integration) tests_dir="tests/integration" ;;
  all) tests_dir="tests" ;;
  *) tests_dir="tests/unit" ;;
esac
if command -v poetry >/dev/null 2>&1; then
  poetry run pytest "$tests_dir" -q --maxfail=1
else
  pytest "$tests_dir" -q --maxfail=1
fi
