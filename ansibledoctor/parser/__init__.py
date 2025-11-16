"""Parser package for Ansible role parsing logic."""

from ansibledoctor.parser.protocols import (
    AnnotationExtractor,
    RoleParser,
    YAMLLoader,
)
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader

__all__ = [
    "YAMLLoader",
    "AnnotationExtractor",
    "RoleParser",
    "RuamelYAMLLoader",
]
