"""
Ansible Doctor Enhanced - Modernized Ansible role documentation generator.

This package provides tools for parsing Ansible roles and generating comprehensive
documentation from metadata, variables, tasks, and inline annotations.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("ansibledoctor")
except PackageNotFoundError:
    # Fallback for development or uninstalled package
    __version__ = "0.4.0"

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
