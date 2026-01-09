import tomllib
from pathlib import Path

from ansibledoctor import __version__


def test_version_matches_pyproject():
    # Locate pyproject.toml relative to this test file (repo root)
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml not found in repository root"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    expected = data.get("tool", {}).get("poetry", {}).get("version")
    assert expected, "version not found in pyproject.toml"

    # Allow local dev suffixes on __version__ (e.g., 0.12.0.dev0) — compare base version
    assert __version__.split("+")[0].split(".dev")[0] == expected
