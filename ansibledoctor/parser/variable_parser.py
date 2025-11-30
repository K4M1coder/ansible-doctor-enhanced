"""
Variable parser for Ansible roles.

Parses role variables from defaults/ and vars/ directories with annotation support.
Implements VariableParser following Constitution Article III (TDD) and Article X (DDD).

This module implements US2: "Parse role variables" from specification 001.
"""

from pathlib import Path

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.annotation import AnnotationType
from ansibledoctor.models.variable import Variable
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.protocols import YAMLLoader
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class VariableParser:
    """
    Parser for Ansible role variables with annotation support.

    Responsibilities (DDD Domain Service):
    - Parse defaults/main.yml and vars/main.yml
    - Extract variable definitions with values
    - Infer variable types automatically
    - Merge variables with @var annotations
    - Transform raw YAML into Variable value objects

    Following DDD principles:
    - Uses YAMLLoader protocol (Dependency Inversion)
    - Uses AnnotationExtractor for annotation parsing
    - Returns Variable value objects (immutable)
    - Anti-Corruption Layer for YAML format
    """

    def __init__(
        self,
        yaml_loader: YAMLLoader,
        annotation_extractor: AnnotationExtractor,
    ):
        """
        Initialize variable parser.

        Args:
            yaml_loader: YAMLLoader implementation for reading YAML files
            annotation_extractor: AnnotationExtractor for parsing @var annotations
        """
        self._yaml_loader = yaml_loader
        self._annotation_extractor = annotation_extractor
        logger.debug("VariableParser initialized")

    def parse_role_variables(self, role_path: Path) -> list[Variable]:
        """
        Parse all variables from a role (defaults + vars).

        Args:
            role_path: Path to role directory

        Returns:
            list[Variable]: All parsed variables from defaults and vars
        """
        logger.info("parsing_role_variables", role_path=str(role_path))

        variables = []

        # Parse defaults/main.yml
        defaults_file = role_path / "defaults" / "main.yml"
        if defaults_file.exists():
            defaults_vars = self.parse_variables_file(defaults_file)
            variables.extend(defaults_vars)
            logger.debug("defaults_parsed", count=len(defaults_vars))

        # Parse vars/main.yml
        vars_file = role_path / "vars" / "main.yml"
        if vars_file.exists():
            vars_vars = self.parse_variables_file(vars_file)
            variables.extend(vars_vars)
            logger.debug("vars_parsed", count=len(vars_vars))

        logger.info(
            "role_variables_parsed",
            role_path=str(role_path),
            total_count=len(variables),
            defaults_count=sum(1 for v in variables if v.source == "defaults"),
            vars_count=sum(1 for v in variables if v.source == "vars"),
        )

        return variables

    def parse_variables_file(self, file_path: Path) -> list[Variable]:
        """
        Parse variables from a defaults or vars file.

        Process:
        1. Load YAML content
        2. Extract variable definitions (key-value pairs)
        3. Extract @var annotations from comments
        4. Merge annotations with variables
        5. Infer types for each variable

        Args:
            file_path: Path to defaults/main.yml or vars/main.yml

        Returns:
            list[Variable]: Parsed variables with annotations
        """
        logger.debug("parsing_variables_file", file_path=str(file_path))

        if not file_path.exists():
            logger.debug("variables_file_not_found", file_path=str(file_path))
            return []

        # Determine source (defaults or vars)
        source = "defaults" if "defaults" in str(file_path) else "vars"

        try:
            # Load YAML data
            data = self._yaml_loader.load_file(file_path)

            # Load raw content for annotation extraction
            yaml_content = file_path.read_text(encoding="utf-8")
            annotations = self._annotation_extractor.extract_annotations(
                yaml_content, str(file_path)
            )

        except ParsingError:
            logger.error("variables_file_parse_failed", file_path=str(file_path))
            return []
        except Exception as e:
            logger.error(
                "variables_file_read_failed",
                file_path=str(file_path),
                error=str(e),
            )
            return []

        # Extract variables from YAML data
        variables = []

        if not data or not isinstance(data, dict):
            logger.debug("empty_or_invalid_variables_file", file_path=str(file_path))
            return []

        # Create annotation lookup by variable name
        var_annotations = {
            ann.key: ann for ann in annotations if ann.type == AnnotationType.VAR and ann.key
        }

        # Process each variable
        for var_name, var_value in data.items():
            # Get annotation if exists
            annotation = var_annotations.get(var_name)

            # Parse annotation attributes
            description = None
            required = None
            example = None
            deprecated = None

            if annotation:
                attrs = annotation.parsed_attributes

                # Extract description (from attributes or raw content)
                if "description" in attrs:
                    description = attrs["description"]
                elif annotation.content and not annotation.content.startswith("{"):
                    # Plain text description (not JSON)
                    description = annotation.content

                # Extract other attributes
                required = attrs.get("required")
                example = attrs.get("example")
                deprecated = attrs.get("deprecated")

            # Infer type
            var_type = Variable.infer_type(var_value)

            # Create Variable value object
            variable = Variable(
                name=var_name,
                value=var_value,
                type=var_type,
                source=source,
                description=description,
                example=example,
                required=required,
                deprecated=deprecated,
            )

            variables.append(variable)

        logger.debug(
            "variables_parsed",
            file_path=str(file_path),
            count=len(variables),
            annotated=len([v for v in variables if v.description]),
        )

        return variables
