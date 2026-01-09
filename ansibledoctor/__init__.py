"""
Ansible Doctor Enhanced - Modernized Ansible role documentation generator.

This package provides tools for parsing Ansible roles and generating comprehensive
documentation from metadata, variables, tasks, and inline annotations.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    # Use the actual distribution/project name declared in pyproject.toml
    __version__ = version("ansible-doctor-enhanced")
except PackageNotFoundError:
    # Fallback for development or uninstalled package: try to read pyproject.toml
    try:
        import tomllib
        from pathlib import Path

        def _version_from_pyproject() -> str | None:
            p = Path(__file__).resolve()
            for parent in p.parents:
                candidate = parent / "pyproject.toml"
                if candidate.exists():
                    with candidate.open("rb") as f:
                        data = tomllib.load(f)
                    version_val: str | None = data.get("tool", {}).get("poetry", {}).get("version")
                    return version_val
            return None

        __version__ = _version_from_pyproject() or "0.0.0+dev"
    except Exception:
        __version__ = "0.0.0+dev"

__author__ = "Cédric Thédrez"
__license__ = "MIT"

from ansibledoctor.exceptions import (
    AnsibleDoctorError,
    ConfigError,
    ParsingError,
    TemplateError,
    ValidationError,
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "AnsibleDoctorError",
    "ConfigError",
    "ParsingError",
    "TemplateError",
    "ValidationError",
]
