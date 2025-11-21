"""YAML loader utilities for collection parsing.

This module provides YAML loading utilities specifically for collection files.
The existing RuamelYAMLLoader from ansibledoctor.parser.yaml_loader is used
for galaxy.yml parsing, following the Anti-Corruption Layer pattern.

No extension needed - RuamelYAMLLoader handles galaxy.yml schema 1.0.0 correctly.
"""

# T005 Complete: Using existing RuamelYAMLLoader from ansibledoctor.parser.yaml_loader
# The loader already supports:
# - Safe YAML loading
# - Error handling with ParsingError
# - Comment preservation (for future annotation support)
# - Anti-Corruption Layer pattern

# Import for convenience
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader

__all__ = ["RuamelYAMLLoader"]
