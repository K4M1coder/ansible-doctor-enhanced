"""
Ansible Doctor Enhanced - Modernized Ansible role documentation generator.

This package provides tools for parsing Ansible roles and generating comprehensive
documentation from metadata, variables, tasks, and inline annotations.

Constitutional Principles:
- Library-First Architecture (Article I)
- Test-Driven Development (Article III)
- Domain-Driven Design (Article X)
"""

__version__ = "0.1.0"
__author__ = "Your Name"
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
