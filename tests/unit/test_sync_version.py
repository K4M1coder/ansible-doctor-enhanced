import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def repo(tmp_path):
    # create a minimal repo structure
    p = tmp_path
    (p / "pyproject.toml").write_text(
        textwrap.dedent(
            """
            [tool.poetry]
            name = "ansibledoctor"
            version = "0.5.1"
            """
        )
    )
    (p / "CHANGELOG.md").write_text(
        textwrap.dedent(
            """
            # Changelog

            ## [Unreleased]

            - updated templates

            ## [0.5.0] - 2025-01-01

            - initial
            """
        )
    )
    (p / "README.md").write_text("Project docs\n\nVersion: 0.5.0\n")

    # init git
    subprocess.run(["git", "init"], cwd=str(p), check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=str(p), check=True)
    subprocess.run(["git", "config", "user.name", "CI Bot"], cwd=str(p), check=True)
    subprocess.run(["git", "add", "--all"], cwd=str(p), check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(p), check=True)
    return p


def run_sync(repo, stage=False):
    # locate script relative to this test file (repo root), but run it in the tmp repo cwd
    script_path = Path(__file__).resolve().parents[3] / "scripts" / "sync_version.py"
    cmd = [sys.executable, str(script_path)]
    if stage:
        cmd += ["--stage", "1"]
    subprocess.run(cmd, cwd=str(repo), check=True)


def test_sync_moves_unreleased_to_version(repo, tmp_path):
    # run sync script and assert CHANGELOG adjusted
    # sys import not used directly here; run_sync uses sys.executable
    run_sync(repo, stage=True)

    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "## [0.5.1] -" in changelog

    readme = (repo / "README.md").read_text(encoding="utf-8")
    assert "Version: 0.5.1" in readme

    # If staged, git status should show no changes
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(repo), check=True, capture_output=True
    )
    assert out.stdout.decode().strip() == ""


def test_sync_creates_version_when_no_unreleased(repo):
    # replace changelog with no Unreleased
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## [0.5.0] - 2025-01-01\n\n- initial\n")
    subprocess.run(["git", "add", "--all"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-m", "reset changelog"], cwd=str(repo), check=True)

    # sys import not used directly here; run_sync uses sys.executable
    run_sync(repo, stage=True)

    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.5.1] -" in changelog
    assert "## [Unreleased]" in changelog


def test_sync_stages_with_env_var(repo):
    # ensure PRECOMMIT_SYNC_STAGE env var works to stage changes
    # sys import not used directly here; used only in run_sync or direct subprocess calls

    env = os.environ.copy()
    env["PRECOMMIT_SYNC_STAGE"] = "1"
    script_path = Path(__file__).resolve().parents[3] / "scripts" / "sync_version.py"
    cmd = [sys.executable, str(script_path)]
    subprocess.run(cmd, cwd=str(repo), check=True, env=env)

    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(repo), check=True, capture_output=True
    )
    assert out.stdout.decode().strip() == ""
