"""
Role parser module.

This module provides the RoleParser class for parsing Ansible roles.
"""

from pathlib import Path

from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.docs_extractor import DocsExtractor
from ansibledoctor.parser.handler_parser import HandlerParser
from ansibledoctor.parser.metadata_parser import MetadataParser
from ansibledoctor.parser.task_parser import TaskParser
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class RoleParser:
    """Parser for Ansible roles.

    Orchestrates parsing of role components (metadata, variables, tasks, etc.)
    to build a complete AnsibleRole model.
    """

    def __init__(self):
        self.yaml_loader = RuamelYAMLLoader()
        self.annotation_extractor = AnnotationExtractor()

    def parse(self, role_path: Path) -> AnsibleRole:
        """Parse a role directory and return AnsibleRole model."""
        logger.debug(f"Parsing role at {role_path}")

        # Metadata
        meta_parser = MetadataParser(self.yaml_loader)
        # MetadataParser expects meta_dir
        metadata = meta_parser.parse_metadata(role_path / "meta")

        # Variables
        var_parser = VariableParser(self.yaml_loader, self.annotation_extractor)
        variables = var_parser.parse_role_variables(role_path)

        # Tasks (for tags)
        task_parser = TaskParser(self.yaml_loader)
        tags = task_parser.parse_tasks(role_path)

        # Handlers
        handler_parser = HandlerParser(str(role_path))
        handlers = handler_parser.parse()

        # Existing Docs
        docs_extractor = DocsExtractor(str(role_path))
        existing_docs = docs_extractor.extract()

        return AnsibleRole(
            name=role_path.name,
            path=role_path,
            metadata=metadata,
            variables=variables,
            tags=tags,
            handlers=handlers,
            existing_docs=existing_docs,
        )
