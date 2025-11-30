#!/usr/bin/env python3
"""Sync version across pyproject.toml, CHANGELOG.md, and README files.

This script:
 - Reads the version from pyproject.toml
 - If version differs from the latest release listed in CHANGELOG.md, it moves
   the topmost Unreleased section to a new section with the new version and date,
   and creates a new empty Unreleased section at the top.
 - Replaces any `Version: x.y.z` text in README files with the version from
   pyproject.toml (this applies to files whose content includes `Version:` pattern).

It is intended to run from repo root and be used by a pre-commit hook. The default
behavior is to modify files in-place and stage them via `git add` when run from
pre-commit to avoid subsequent 'modified by hook' failures.

Make sure to run `poetry run pre-commit run sync-version --all-files` to test.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
from pathlib import Path

try:
    import tomllib
except Exception:
    import tomli as tomllib  # type: ignore


def read_pyproject_version(pyproject_path: Path) -> str | None:
    try:
        content = pyproject_path.read_text(encoding="utf-8")
        parsed = tomllib.loads(content)
        version = parsed.get("tool", {}).get("poetry", {}).get("version")
        return version
    except Exception:
        return None


def update_changelog(changelog_path: Path, version: str) -> bool:
    """Move Unreleased -> version and create a blank Unreleased section.
    Returns True if an update was made, False otherwise.
    """
    text = changelog_path.read_text(encoding="utf-8")

    # Basic parsing: find '## [Unreleased]' at start of a line
    unre_match = re.search(r"^## \[Unreleased\]\s*$", text, flags=re.MULTILINE)
    if not unre_match:
        # If no Unreleased section, add a new versioned section at top
        date_str = datetime.date.today().isoformat()
        new_header = f"## [{version}] - {date_str}\n\n- \n\n"
        changelog_path.write_text(new_header + text, encoding="utf-8")
        return True

    # Find the end of Unreleased section (next '## ' header)
    start = unre_match.start()
    # find next `^## ` after unre_match.end()
    next_header = re.search(r"^## \[", text[unre_match.end() :], flags=re.MULTILINE)
    end = unre_match.end() + (next_header.start() if next_header else len(text) - unre_match.end())

    unre_section = text[unre_match.end() : end].strip()
    # do not process if Unreleased empty (no changes) — still create version if forced
    date_str = datetime.date.today().isoformat()
    version_header = f"## [{version}] - {date_str}\n\n"
    new_unreleased = "## [Unreleased]\n\n- \n\n"

    # If version already exists in changelog, we will not duplicate; just insert Unreleased above
    if re.search(rf"^## \[{re.escape(version)}\]", text, flags=re.MULTILINE):
        # Ensure there is an Unreleased header at the top; replace earlier Unreleased if exists
        text = re.sub(r"^## \[Unreleased\]\s*$", "## [Unreleased]", text, flags=re.MULTILINE)
        # no further change
        return False

    # Replace Unreleased with Version header + content, and add top empty Unreleased
    if unre_section:
        # Keep existing content under the version header
        body = text[:start]
        remainder = text[end:]
        new_text = body + new_unreleased + version_header + unre_section + "\n\n" + remainder
    else:
        # empty unreleased: still create version header + placeholder
        body = text[:start]
        remainder = text[end:]
        new_text = body + new_unreleased + version_header + "- \n\n" + remainder

    changelog_path.write_text(new_text, encoding="utf-8")
    return True


def update_readme_versions(repo_root: Path, version: str) -> int:
    """Find README files with Version: pattern and replace version string.
    Returns number of files modified.
    """
    files = list(repo_root.rglob("README.md")) + list(repo_root.rglob("README.rst"))
    modified = 0
    version_pattern = re.compile(r"(Version\*?\*?:\s*)([0-9]+\.[0-9]+\.[0-9]+)")
    # Also catch patterns like '**Version:** 0.4.0' or 'Version: 0.4.0'
    alt_pattern = re.compile(r"(\*\*Version:\*\*\s*)([0-9]+\.[0-9]+\.[0-9]+)")
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except Exception:
            continue
        new_content = version_pattern.sub(rf"\1{version}", content)
        new_content = alt_pattern.sub(rf"\1{version}", new_content)
        if new_content != content:
            f.write_text(new_content, encoding="utf-8")
            modified += 1
    return modified


def stage_changes(paths: list[Path]) -> None:
    try:
        for p in paths:
            subprocess.run(["git", "add", str(p)], check=False)
    except Exception:
        # best-effort
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    parser.add_argument("--root", default=".")
    parser.add_argument("--stage", default=None, help="Force to stage changes (1/0 or env var) ")
    parser.add_argument(
        "--date", default=None, help="ISO date to use for version header instead of today"
    )
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    pyproject = repo_root / args.pyproject
    changelog = repo_root / args.changelog

    version = read_pyproject_version(pyproject)
    if not version:
        print("Could not read version from pyproject.toml")
        return 1

    # Update changelog
    changed_changelog = update_changelog(changelog, version)
    # Update README(s)
    modified_readmes = update_readme_versions(repo_root, version)

    # Stage changes if running in pre-commit and staging allowed via env or args
    stage_allowed = os.environ.get("PRECOMMIT_SYNC_STAGE", "0") == "1"
    if args.stage is not None:
        if args.stage in ("1", "true", "True"):
            stage_allowed = True
        elif args.stage in ("0", "False", "false"):
            stage_allowed = False

    if stage_allowed and (changed_changelog or modified_readmes > 0):
        paths_to_stage = [changelog] if changed_changelog else []
        # gather modified readmes
        for p in repo_root.rglob("README.md"):
            try:
                content = p.read_text(encoding="utf-8")
                if f"Version: {version}" in content or f"**Version:** {version}" in content:
                    paths_to_stage.append(p)
            except Exception:
                pass
        stage_changes(paths_to_stage)

    if changed_changelog or modified_readmes > 0:
        print(f"Updated CHANGELOG: {changed_changelog}, READMEs modified: {modified_readmes}")
        return 0

    print("No changes required (versions already in sync)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
