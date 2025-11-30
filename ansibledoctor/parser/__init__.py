"""Parser package for Ansible role parsing logic."""

from ansibledoctor.parser.annotation_extractor import AnnotationExtractor as AnnotationExtractorImpl
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.protocols import AnnotationExtractor, RoleParser, YAMLLoader
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader

__all__ = [
    "YAMLLoader",
    "AnnotationExtractor",
    "RoleParser",
    "RuamelYAMLLoader",
    "MetadataParser",
    "AnnotationExtractorImpl",
    "VariableParser",
]
