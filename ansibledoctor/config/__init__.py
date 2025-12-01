"""Configuration management for ansible-doctor-enhanced.

This module provides configuration file support for .ansibledoctor.yml files,
enabling persistent documentation settings without CLI flags.

Constitutional Principles:
- Library-First Architecture (Article I)
- Test-Driven Development (Article III)
- Domain-Driven Design (Article X)

Feature 003 - US1: Configuration File Support
Feature 008 - Template Customization & Theming
"""

from ansibledoctor.config.models import ConfigModel
from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant

__all__ = [
    "ConfigModel",
    "ColorScheme",
    "ThemeConfig",
    "ThemeVariant",
]
