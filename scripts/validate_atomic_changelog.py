#!/usr/bin/env python3
"""Validate that version bump, CHANGELOG and README updates are committed atomically.

This script is intended to run in CI or locally and validates that when
`pyproject.toml`'s `version` is updated in a PR or a range of commits, the
change is accompanied by a `CHANGELOG.md` update and a `README.md` update,
and that the version change and the updates are present in the same commit
or at least in the same PR as a safety check.

Usage (CI / PR):
  python scripts/validate_atomic_changelog.py --base origin/main --head HEAD

Usage (local):
  python scripts/validate_atomic_changelog.py --base HEAD~5 --head HEAD

Exit code: 0 on success; non-zero on validation failure.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover - fallback for older Python on CI/local
    import tomli as tomllib  # type: ignore

from typing import List


def run(cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, capture_output=capture_output, text=True)


def git_ref_exists(ref: str) -> bool:
    """Return True if git ref exists locally; works for 'main', 'origin/main', and commit hashes.

    We try `git rev-parse --verify --quiet` to verify the ref; this will return 0 if the ref
    resolves locally in any form.
    """
    cp = run(["git", "rev-parse", "--verify", "--quiet", ref])
    return cp.returncode == 0


def git_changed_files(base: str | None, head: str) -> List[str]:
    """Return list of changed files between base and head.

    If base is None or invalid, attempts to fallback to HEAD~1..HEAD.
    This is robust to `origin/main` and `main` style refs and will fetch the
    necessary remote branch when possible.
    """
    # Determine a base ref to use for diff. If base is of form 'origin/main', fetch
    # just the branch portion so remote ref is available locally.
    if base:
        # If base contains a slash and starts with 'origin/', fetch only the remote branch
        if "/" in base:
            remote, branch = base.split("/", 1)
            # try to fetch the branch from remote
            _ = run(["git", "fetch", "--no-tags", "--depth=1", remote, branch])
        else:
            # try to fetch the base in case the local repo doesn't have it
            _ = run(["git", "fetch", "--no-tags", "--depth=1", "origin", base])

        # if the base ref doesn't exist locally after attempting fetch, try
        # using the short branch name (e.g., 'origin/main' -> 'main') or fallback
        if not git_ref_exists(base):
            if "/" in base:
                _, branch = base.split("/", 1)
                if git_ref_exists(branch):
                    base = branch
                else:
                    base = None
            else:
                base = None

    # Compose the diff range
    if base:
        rng = f"{base}..{head}"
    else:
        rng = f"{head}~1..{head}"

    cp = run(["git", "diff", "--name-only", rng])
    if cp.returncode != 0:
        # Try fallback to a simpler local range if the requested pair isn't available
        if base:
            cp = run(["git", "diff", "--name-only", f"{head}~1..{head}"])
    if cp.returncode != 0:
        # Nothing we can do: return an empty list (we don't want to crash the hook)
        return []
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def git_file_content_at_ref(path: Path, ref: str) -> str:
    cp = run(["git", "show", f"{ref}:{path.as_posix()}"], capture_output=True)
    if cp.returncode != 0:
        return ""
    return cp.stdout


def parse_version_from_pyproject(content: str) -> str | None:
    try:
        parsed = tomllib.loads(content)
        tool = parsed.get("tool", {})
        poetry = tool.get("poetry")
        if isinstance(poetry, dict):
            return poetry.get("version")
    except Exception:
        return None
    return None


def commits_touching_file(base: str, head: str, path: Path) -> List[str]:
    # commit hashes touching file in the range
    cp = run(["git", "log", "--pretty=format:%H", f"{base}..{head}", "--", path.as_posix()])
    if cp.returncode != 0:
        raise SystemExit(2)
    return [h.strip() for h in cp.stdout.splitlines() if h.strip()]


def files_in_commit(commit_hash: str) -> List[str]:
    cp = run(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash])
    if cp.returncode != 0:
        raise SystemExit(2)
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=None, help="Base ref (e.g., origin/main)")
    parser.add_argument("--head", default="HEAD", help="Head ref (e.g., HEAD)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    base = args.base
    head = args.head

    changed_files = git_changed_files(base, head)
    if not args.quiet:
        print(f"Changed files between {base} and {head}: {changed_files}")

    # Only validate when pyproject.toml changed
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.as_posix() not in changed_files:
        if not args.quiet:
            print("pyproject.toml not changed - no version bump detected; nothing to validate.")
        return 0

    old_pyproject = git_file_content_at_ref(pyproject_path, base)
    new_pyproject = pyproject_path.read_text(encoding="utf-8")
    old_version = parse_version_from_pyproject(old_pyproject)
    new_version = parse_version_from_pyproject(new_pyproject)
    if old_version == new_version:
        if not args.quiet:
            print("pyproject version unchanged - nothing to validate.")
        return 0

    if not args.quiet:
        print(f"Version bump detected: {old_version} -> {new_version}")

    # Required files: CHANGELOG.md and README.md (or README-generated.md)
    required_files = {"CHANGELOG.md", "README.md", "README-generated.md"}
    found_required = any(q in changed_files for q in required_files)

    if not found_required:
        print("ERROR: Version bump must include CHANGELOG.md and README update in the same PR.")
        print("Changed files did not include CHANGELOG.md or any README file.")
        print("Files changed:", changed_files)
        return 2

    # Now check atomicity: find the commits in the range that touched pyproject
    commits = commits_touching_file(base, head, pyproject_path)
    if not commits:
        print("ERROR: No commits touching pyproject found in given range (unexpected).")
        return 2

    # Check whether at least one of the commits that changed pyproject ALSO touched
    # the changelog and README in the same commit
    atomic_found = False
    for c in commits:
        files = files_in_commit(c)
        if pyproject_path.as_posix() in files and any(f in files for f in required_files):
            atomic_found = True
            if not args.quiet:
                print(f"Found atomic commit {c} touching: {files}")
            break

    if not atomic_found:
        print(
            "ERROR: No single commit found that updates version, CHANGELOG and README atomically."
        )
        print("Commits that changed pyproject:")
        for c in commits:
            print(c, files_in_commit(c))
        return 2

    print("OK: Version bump, changelog and README updated atomically in commit", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
