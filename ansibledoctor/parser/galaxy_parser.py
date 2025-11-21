"""Galaxy metadata parser for galaxy.yml files.

This module parses galaxy.yml files following Ansible Galaxy schema
version 1.0.0. Validates required fields and extracts collection metadata.

Following Constitution Article X (DDD): Parser in Infrastructure layer,
constructs domain GalaxyMetadata models.
"""

from pathlib import Path
from typing import Any, Dict

from pydantic import ValidationError

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.parser.base_validator import BaseValidator
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class GalaxyMetadataParser:
    """
    Parser for galaxy.yml files (schema version 1.0.0).
    
    Parses required fields only in v0.5.0:
    - namespace (required)
    - name (required)
    - version (required)
    - authors (required)
    - dependencies (required)
    
    Optional fields deferred to v0.6.0.
    """
    
    def __init__(self) -> None:
        """Initialize parser with YAML loader."""
        self.yaml_loader = RuamelYAMLLoader()
    
    def parse(self, galaxy_file: Path) -> GalaxyMetadata:
        """
        Parse galaxy.yml file and return GalaxyMetadata model.
        
        Args:
            galaxy_file: Path to galaxy.yml file
            
        Returns:
            GalaxyMetadata model with required fields
            
        Raises:
            ParsingError: If file not found, malformed YAML, or missing required fields
            
        Example:
            >>> parser = GalaxyMetadataParser()
            >>> metadata = parser.parse(Path("galaxy.yml"))
            >>> metadata.fqcn
            'my_namespace.my_collection'
        """
        logger.debug("parsing_galaxy_yml", file=str(galaxy_file))
        
        # Validate file exists using BaseValidator
        BaseValidator.validate_file_exists(
            galaxy_file,
            file_type="galaxy.yml",
            suggestion=(
                "Ensure this is a valid Ansible collection with a galaxy.yml file. "
                "Try running 'ls -la' to check if the file exists in the collection root."
            )
        )
        
        # Load YAML (catches YAML syntax errors)
        try:
            data = self.yaml_loader.load_file(galaxy_file)
        except Exception as e:
            raise BaseValidator.create_actionable_error(
                message=f"Failed to parse galaxy.yml: {e}",
                context={"file_path": str(galaxy_file), "error": str(e)},
                suggestion="Check YAML syntax and structure",
                troubleshooting_steps=[
                    f"Run 'yamllint {galaxy_file}' to identify syntax errors",
                    "Ensure proper indentation (use spaces, not tabs)",
                    "Verify no special characters or encoding issues",
                    "Check examples at https://galaxy.ansible.com/docs/contributing/creating_collections.html"
                ]
            ) from e
        
        # Validate required fields and construct model
        try:
            # Ensure data is a dict for unpacking
            if not isinstance(data, dict):
                raise ParsingError(
                    f"galaxy.yml must contain a dictionary, not {type(data).__name__}",
                    context={"file_path": str(galaxy_file), "data_type": type(data).__name__},
                    suggestion="Ensure galaxy.yml contains key-value pairs, not a list or scalar value"
                )
            metadata = GalaxyMetadata(**data)
            
            logger.info(
                "galaxy_yml_parsed",
                file=str(galaxy_file),
                fqcn=metadata.fqcn,
                version=metadata.version,
            )
            
            return metadata
            
        except ValidationError as e:
            # Extract missing/invalid fields from Pydantic error
            error_details = str(e)
            
            raise BaseValidator.create_actionable_error(
                message=f"Invalid galaxy.yml: {error_details}",
                context={
                    "file_path": str(galaxy_file),
                    "validation_errors": error_details
                },
                suggestion="Ensure galaxy.yml contains all required fields with valid formats",
                troubleshooting_steps=[
                    "Required fields: namespace, name, version, authors, dependencies",
                    "namespace/name: lowercase alphanumeric with underscores (e.g., 'my_namespace')",
                    "version: semantic version format (e.g., '1.0.0')",
                    "authors: list of strings (e.g., ['Author Name <email@example.com>'])",
                    "dependencies: dictionary (e.g., {'community.general': '>=5.0.0'})",
                    "See https://docs.ansible.com/ansible/latest/dev_guide/collections_galaxy_meta.html"
                ]
            ) from e
