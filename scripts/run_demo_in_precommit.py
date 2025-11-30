#!/usr/bin/env python3
"""Run the demo generation commands for project, collection and role.

This script runs the CLI over the demo assets to ensure the "actual" code path executes.
It prints all logs and returns 0 so pre-commit does not block commits when demo generation
fails during TDD.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory, mkdtemp


def run_cmd(cmd: list[str]) -> int:
    print("\nRunning:", " ".join(cmd))
    env = {**dict(os.environ)}
    # Ensure demo command can import local package by adding project root to PYTHONPATH
    project_root = Path(__file__).resolve().parents[1]
    env.setdefault("PYTHONPATH", str(project_root))

    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print(proc.stdout)
    if proc.stderr:
        print("stderr:\n", proc.stderr)
    print(f"Exit code: {proc.returncode}\n")
    return proc.returncode


def main() -> int:
    python = sys.executable
    project_root = Path(__file__).resolve().parents[1]
    # By default, do not alter tracked files in repo during pre-commit.
    # If PRECOMMIT_DEMO_STAGE is set, write to repo and stage files.
    stage_docs = os.environ.get("PRECOMMIT_DEMO_STAGE", "0") == "1"

    # Sources for demos
    demo_role = project_root / "demo" / "role_demo_namespace.demo_demo_role"
    demo_collection = project_root / "demo" / "collection_demo_namespace.demo_collection"

    # Determine output directories. By default generate into a temp dir
    # so we don't modify tracked files and avoid pre-commit 'modified files' failures.
    temp_dir_obj = None
    keep_temp = os.environ.get("ANSIBLE_DOCTOR_DEMO_KEEP_TEMP", "0") == "1"
    if not stage_docs:
        # If user requests to keep the demo temp dir for debugging, use mkdtemp
        # which will create a directory that is not cleaned up automatically on process exit.
        if keep_temp:
            base_out = Path(mkdtemp(prefix="ansibledoctor-demo-"))
        else:
            temp_dir_obj = TemporaryDirectory(prefix="ansibledoctor-demo-")
            base_out = Path(temp_dir_obj.name)
        # Print base output dir for debugging and test discovery
        print(f"Demo temp base path: {base_out}")
        # Also emit a machine-friendly env var-like line so tests can reliably parse it
        print(f"DEMO_TEMP_BASE={base_out}")
        # Normalize output to follow project docs structure: docs/collections/<collection_name> and docs/roles/<role_name>
        demo_role_docs = base_out / "docs" / "roles" / demo_role.name
        demo_collection_docs = base_out / "docs" / "collections" / demo_collection.name
        project_docs = base_out / "docs"
    else:
        demo_role_docs = demo_role / "docs"
        demo_collection_docs = project_root / "docs" / "collections" / demo_collection.name
        project_docs = project_root / "docs"
        project_docs = project_root / "docs"

    demo_role_docs.mkdir(parents=True, exist_ok=True)
    demo_collection_docs.mkdir(parents=True, exist_ok=True)
    project_docs.mkdir(parents=True, exist_ok=True)

    cmds: list[list[str]] = []

    # Role generation: md, html, rst
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "generate",
            str(demo_role),
            "--format",
            "markdown",
            "--output",
            str(demo_role_docs / "README.md"),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "generate",
            str(demo_role),
            "--format",
            "html",
            "--output",
            str(demo_role_docs / "index.html"),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "generate",
            str(demo_role),
            "--format",
            "rst",
            "--output",
            str(demo_role_docs / "README.rst"),
        ]
    )

    # Collection generation: md, html, rst
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "collection",
            "generate",
            str(demo_collection),
            "--format",
            "markdown",
            "--output-dir",
            str(demo_collection_docs),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "collection",
            "generate",
            str(demo_collection),
            "--format",
            "html",
            "--output-dir",
            str(demo_collection_docs),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "collection",
            "generate",
            str(demo_collection),
            "--format",
            "rst",
            "--output-dir",
            str(demo_collection_docs),
        ]
    )

    # Project generation: md, html, rst
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "project",
            "generate",
            str(project_root),
            "--format",
            "markdown",
            "--output-dir",
            str(project_docs),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "project",
            "generate",
            str(project_root),
            "--format",
            "html",
            "--output-dir",
            str(project_docs),
        ]
    )
    cmds.append(
        [
            python,
            "-m",
            "ansibledoctor",
            "project",
            "generate",
            str(project_root),
            "--format",
            "rst",
            "--output-dir",
            str(project_docs),
        ]
    )

    exit_codes = [run_cmd(cmd) for cmd in cmds]

    if any(c != 0 for c in exit_codes):
        print("Some demo operations failed. See logs above.")
    else:
        print("All demo commands executed successfully.")

    # Never fail pre-commit
    # If files were generated, and staging is enabled, stage them so pre-commit does not treat the hook as modifying files
    try:
        # Find generated files in demo and docs directories
        repo_root = project_root
        # staging all docs/ files under demo/**/docs and project docs
        demo_docs = (
            list((repo_root / "demo").rglob("*/docs/**/*")) if (repo_root / "demo").exists() else []
        )
        # also include project docs
        project_docs_list = (
            list((repo_root / "docs").rglob("**/*")) if (repo_root / "docs").exists() else []
        )
        to_stage = [p for p in set(demo_docs + project_docs_list) if p.is_file()]
        if to_stage and stage_docs:
            print("Staging generated doc files:")
            for p in to_stage:
                print(p)
                subprocess.run(["git", "add", str(p)])
        elif to_stage:
            print(
                "Generated docs written to temp directory. Not staging by default in local pre-commit."
            )
            for p in to_stage[:5]:
                print(p)
    except Exception:
        # Best effort: ignore staging errors
        pass

    # Clean up the TemporaryDirectory object only when it was used and not requested to keep.
    if temp_dir_obj:
        # Allow tests and debugging to keep the temp directory using ANSIBLE_DOCTOR_DEMO_KEEP_TEMP
        # If a TemporaryDirectory object was used and the user did not request keeping it,
        # then run cleanup to remove the directory, otherwise leave it on disk for debugging.
        if not keep_temp:
            temp_dir_obj.cleanup()
        else:
            print(f"Preserving demo temp dir for debugging: {base_out}")
            # Print discovered generated docs for integration tests to discover exact paths
            # Look for markdown-based collection README(s)
            generated_files: list[str] = []
            for p in sorted(base_out.rglob("**/*")):
                if p.is_file() and p.suffix.lower() in {".md", ".html", ".rst"}:
                    # Heuristic: only report files under docs/collections, docs/roles, or project docs
                    try:
                        parts = p.parts
                        if "docs" in parts:
                            idx = parts.index("docs")
                            # Only report files under docs/collections, docs/roles or docs project root
                            if len(parts) > idx + 1 and parts[idx + 1] in {"collections", "roles"}:
                                print(f"Documentation generated: {p}")
                                generated_files.append(str(p))
                            elif len(parts) == idx + 1 or parts[idx + 1] not in {
                                "collections",
                                "roles",
                            }:
                                # Project-level docs
                                print(f"Documentation generated: {p}")
                                generated_files.append(str(p))
                    except Exception:
                        # Skip odd paths
                        continue
            # Print a machine parseable JSON summary in a single line for tests to inspect
            try:
                summary = {"base": str(base_out), "files": generated_files}
                # Use compact separators so the output fits a single line
                print(
                    "DEMO_OUTPUT_JSON="
                    + json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
                )
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
