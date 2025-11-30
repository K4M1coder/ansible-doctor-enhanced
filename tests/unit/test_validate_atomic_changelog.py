import subprocess
import sys

from scripts import validate_atomic_changelog as vac


class FakeCompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def fake_run_factory(output_map):
    def fake_run(args, check=False, capture_output=False, text=False, stdout=None, stderr=None):
        cmd = " ".join(args)
        # Handle rev-parse
        if args[:3] == ["git", "rev-parse", "--verify"] or "rev-parse" in cmd:
            ref = args[-1]
            if output_map.get(("rev-parse", ref), False):
                return FakeCompletedProcess(returncode=0)
            return FakeCompletedProcess(returncode=1)
        if args[:3] == ["git", "fetch", "--no-tags"] or "git fetch" in cmd:
            # Emulate successful fetch
            return FakeCompletedProcess(returncode=0)
        if args[:3] == ["git", "diff", "--name-only"] or "git diff --name-only" in cmd:
            rng = args[-1]
            return FakeCompletedProcess(returncode=0, stdout=output_map.get(("diff", rng), ""))
        if args[:3] == ["git", "log", "--pretty=format:%H"]:
            rng = args[3]
            return FakeCompletedProcess(returncode=0, stdout=output_map.get(("log", rng), ""))
        if args[:3] == ["git", "show"]:
            ref = args[1]
            _ = args[2]
            # Not used in these tests beyond accepting the command
            return FakeCompletedProcess(returncode=0, stdout="tool.poetry.version = '0.1.0'\n")
        if args[:3] == ["git", "diff-tree", "--no-commit-id"]:
            return FakeCompletedProcess(
                returncode=0, stdout=output_map.get(("files_in_commit", args[-1]), "")
            )
        return FakeCompletedProcess(returncode=0, stdout="")

    return fake_run


def test_git_changed_files_origin_main(monkeypatch):
    # origin/main not present locally; fetch should be attempted and base fallback occurs
    output_map = {
        ("rev-parse", "origin/main"): False,
        ("rev-parse", "main"): True,
        ("diff", "main..HEAD"): "pyproject.toml\nCHANGELOG.md\nREADME.md\n",
    }
    monkeypatch.setattr(subprocess, "run", fake_run_factory(output_map))
    files = vac.git_changed_files("origin/main", "HEAD")
    assert "pyproject.toml" in files
    assert "CHANGELOG.md" in files
    assert "README.md" in files


def test_git_changed_files_base_missing_fallback(monkeypatch):
    # base not provided, fallback to HEAD~1
    output_map = {("diff", "HEAD~1..HEAD"): "pyproject.toml\n"}
    monkeypatch.setattr(subprocess, "run", fake_run_factory(output_map))
    files = vac.git_changed_files(None, "HEAD")
    assert files == ["pyproject.toml"]


def test_main_detects_version_bump_and_fails(monkeypatch):
    # prepare fake diff output indicating version bump without changelog/readme
    output_map = {
        ("rev-parse", "origin/main"): True,
        ("diff", "origin/main..HEAD"): "pyproject.toml\n",
        ("log", "origin/main..HEAD"): "abcde12345\n",
        ("files_in_commit", "abcde12345"): "pyproject.toml\n",
    }
    monkeypatch.setattr(subprocess, "run", fake_run_factory(output_map))
    # Simulate invocation with --base origin/main so the script uses the mapped diff
    monkeypatch.setattr(
        sys, "argv", ["validate_atomic_changelog.py", "--base", "origin/main", "--head", "HEAD"]
    )
    # Call main() directly and check the return code (0 success, non-zero error code on failure)
    assert vac.main() == 2
