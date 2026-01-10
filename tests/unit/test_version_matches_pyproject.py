import tomllib
from pathlib import Path

from ansibledoctor import __version__


def test_version_matches_pyproject():
    # Locate pyproject.toml relative to this test file (repo root)
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml not found in repository root"
    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    expected_version = data.get("tool", {}).get("poetry", {}).get("version")
    expected_name = data.get("tool", {}).get("poetry", {}).get("name")
    assert expected_version, "version not found in pyproject.toml"
    assert expected_name, "name not found in pyproject.toml"

    # 1. Verify version matches
    # Allow local dev suffixes on __version__ (e.g., 0.12.0.dev0) — compare base version
    assert __version__.split("+")[0].split(".dev")[0] == expected_version

    # 2. Verify app name consistency in ansibledoctor/__init__.py
    init_file = Path(__file__).resolve().parents[2] / "ansibledoctor" / "__init__.py"
    assert init_file.exists(), "ansibledoctor/__init__.py not found"
    init_content = init_file.read_text(encoding="utf-8")

    # Check that version() call uses the correct package name string
    name_reference = f'version("{expected_name}")'
    name_reference_alt = f"version('{expected_name}')"
    assert (name_reference in init_content) or (
        name_reference_alt in init_content
    ), f"ansibledoctor/__init__.py should call version('{expected_name}') to match pyproject.toml"
