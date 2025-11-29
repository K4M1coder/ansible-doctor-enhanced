#!/usr/bin/env bash
# Local helper: ensure that when you bump version, you include CHANGELOG.md and README update
set -euo pipefail
BASE_REF="$(git rev-parse --abbrev-ref @{u} 2>/dev/null || echo origin/main)"
HEAD_REF="HEAD"
python scripts/validate_atomic_changelog.py --base "${BASE_REF}" --head "${HEAD_REF}" || {
  echo "Validation failed: Please include CHANGELOG.md and README updates in the same commit as pyproject version bump." >&2
  exit 1
}
echo "OK: Changelog/README atomicity checks passed."
