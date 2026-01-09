"""
Metadata parser for Ansible roles.

Extracts role metadata from meta/main.yml and meta/argument_specs.yml files.
Implements MetadataParser following Constitution Article III (TDD) and Article X (DDD).

This module implements US1: "Extract role metadata" from specification 001.
"""

from pathlib import Path
from typing import Any

from ansibledoctor.exceptions import ParsingError
from ansibledoctor.models.metadata import ArgumentSpec, Dependency, Platform, RoleMetadata
from ansibledoctor.parser.protocols import YAMLLoader
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class MetadataParser:
    """
    Parser for Ansible role metadata files.

    Responsibilities (DDD Domain Service):
    - Parse meta/main.yml galaxy_info section
    - Parse meta/argument_specs.yml (Ansible 2.11+)
    - Transform raw YAML into RoleMetadata value objects
    - Handle missing/malformed metadata gracefully

    Following DDD principles:
    - Uses YAMLLoader protocol (Dependency Inversion)
    - Returns RoleMetadata aggregate
    - Translates external format to domain models (Anti-Corruption Layer)
    """

    def __init__(self, yaml_loader: YAMLLoader):
        """
        Initialize metadata parser.

        Args:
            yaml_loader: YAMLLoader implementation for reading YAML files
        """
        self._yaml_loader = yaml_loader
        logger.debug("MetadataParser initialized")

    def parse_metadata(self, meta_dir: Path) -> RoleMetadata:
        """
        Parse complete role metadata from meta directory.

        This is the main entry point combining galaxy_info and argument_specs parsing.

        Args:
            meta_dir: Path to role's meta/ directory

        Returns:
            RoleMetadata: Parsed and validated metadata

        Raises:
            ParsingError: If meta/main.yml cannot be parsed
        """
        logger.info("parsing_role_metadata", meta_dir=str(meta_dir))

        meta_file = meta_dir / "main.yml"
        metadata = self.parse_galaxy_info(meta_file)

        # Parse argument_specs.yml (optional, Ansible 2.11+)
        specs_file = meta_dir / "argument_specs.yml"
        if specs_file.exists():
            arg_specs = self.parse_argument_specs(specs_file)
            # Update metadata with argument specs
            metadata = RoleMetadata(
                galaxy_info=metadata.galaxy_info,
                author=metadata.author,
                description=metadata.description,
                company=metadata.company,
                license=metadata.license,
                min_ansible_version=metadata.min_ansible_version,
                platforms=metadata.platforms,
                galaxy_tags=metadata.galaxy_tags,
                dependencies=metadata.dependencies,
                argument_specs=arg_specs,
                meta_file_path=metadata.meta_file_path,
            )

        logger.info(
            "metadata_parsed",
            author=metadata.author,
            platforms_count=len(metadata.platforms),
            dependencies_count=len(metadata.dependencies),
            has_argument_specs=len(metadata.argument_specs) > 0,
        )

        return metadata

    def parse_galaxy_info(self, meta_file: Path) -> RoleMetadata:
        """
        Parse galaxy_info section from meta/main.yml.

        Extracts:
        - author, description, company, license
        - min_ansible_version
        - platforms (list of Platform value objects)
        - galaxy_tags
        - dependencies (list of Dependency value objects)

        Args:
            meta_file: Path to meta/main.yml file

        Returns:
            RoleMetadata: Parsed metadata with galaxy_info

        Raises:
            ParsingError: If file doesn't exist or YAML is malformed
        """
        logger.debug("parsing_galaxy_info", meta_file=str(meta_file))

        if not meta_file.exists():
            raise ParsingError(
                message=f"Metadata file not found: {meta_file}",
                context={"file_path": str(meta_file)},
                suggestion="Ensure the role has a meta/main.yml file with galaxy_info section.",
            )

        try:
            data = self._yaml_loader.load_file(meta_file)
        except ParsingError:
            # Re-raise with additional context
            raise
        except Exception as e:
            raise ParsingError(
                message=f"Failed to parse metadata file: {meta_file}",
                context={"file_path": str(meta_file), "error": str(e)},
                suggestion="Check YAML syntax in meta/main.yml file.",
            ) from e

        # Ensure data is a dict (YAML file might contain a list)
        if not isinstance(data, dict):
            logger.warning("metadata_not_dict", file=str(meta_file))
            data = {}

        galaxy_info = data.get("galaxy_info", {})
        dependencies_raw = data.get("dependencies", [])

        # Extract basic fields
        author = galaxy_info.get("author")
        description = galaxy_info.get("description")
        company = galaxy_info.get("company")
        license_field = galaxy_info.get("license")
        min_ansible_version = galaxy_info.get("min_ansible_version")
        galaxy_tags = galaxy_info.get("galaxy_tags", [])

        # Parse platforms
        platforms = self._parse_platforms(galaxy_info.get("platforms", []))

        # Parse dependencies
        dependencies = self._parse_dependencies(dependencies_raw)

        logger.debug(
            "galaxy_info_parsed",
            author=author,
            platforms_count=len(platforms),
            dependencies_count=len(dependencies),
        )

        return RoleMetadata(
            galaxy_info=galaxy_info,
            author=author,
            description=description,
            company=company,
            license=license_field,
            min_ansible_version=min_ansible_version,
            platforms=platforms,
            galaxy_tags=galaxy_tags,
            dependencies=dependencies,
            argument_specs={},
            meta_file_path=str(meta_file),
        )

    def parse_argument_specs(self, specs_file: Path) -> dict[str, ArgumentSpec]:
        """
        Parse argument_specs.yml (Ansible 2.11+ feature).

        argument_specs.yml defines role parameters similar to module arguments.
        This is an optional file, so missing file returns empty dict.

        Args:
            specs_file: Path to meta/argument_specs.yml

        Returns:
            dict[str, ArgumentSpec]: Argument specs by entry point name
        """
        logger.debug("parsing_argument_specs", specs_file=str(specs_file))

        if not specs_file.exists():
            logger.debug("argument_specs_not_found", specs_file=str(specs_file))
            return {}

        try:
            data = self._yaml_loader.load_file(specs_file)
        except ParsingError as e:
            logger.warning("argument_specs_parse_failed", error=str(e))
            return {}

        # Ensure data is a dict
        if not isinstance(data, dict):
            logger.warning("argument_specs_not_dict", file=str(specs_file))
            return {}

        argument_specs_raw = data.get("argument_specs", {})
        argument_specs = {}

        for entry_point, spec_data in argument_specs_raw.items():
            short_description = spec_data.get("short_description", "")
            options = spec_data.get("options", {})
            description = spec_data.get("description")

            argument_specs[entry_point] = ArgumentSpec(
                entry_point=entry_point,
                short_description=short_description,
                options=options,
                description=description,
            )

        logger.debug("argument_specs_parsed", count=len(argument_specs))

        return argument_specs

    def _parse_platforms(self, platforms_raw: list[dict[str, Any]]) -> list[Platform]:
        """
        Parse platforms from galaxy_info.

        Handles various formats:
        - versions as list: ["focal", "jammy"]
        - versions as string: "all"
        - missing versions field

        Args:
            platforms_raw: Raw platforms list from galaxy_info

        Returns:
            list[Platform]: Parsed Platform value objects
        """
        platforms = []

        for platform_data in platforms_raw:
            if not isinstance(platform_data, dict):
                logger.warning("invalid_platform_format", platform_data=platform_data)
                continue

            name = platform_data.get("name")
            if not name:
                logger.warning("platform_missing_name", platform_data=platform_data)
                continue

            versions_raw = platform_data.get("versions", [])

            # Handle versions as string (e.g., "all")
            if isinstance(versions_raw, str):
                versions = [versions_raw] if versions_raw else []
            # Handle versions as list
            elif isinstance(versions_raw, list):
                versions = [str(v) for v in versions_raw]
            else:
                versions = []

            platforms.append(Platform(name=name, versions=versions))

        return platforms

    def _parse_dependencies(self, dependencies_raw: list[Any]) -> list[Dependency]:
        """
        Parse role dependencies.

        Handles two formats:
        1. String: "geerlingguy.nginx"
        2. Dict: {name: "geerlingguy.docker", version: ">=4.0.0"}
           or:   {role: "geerlingguy.php", version: "3.x"}

        Args:
            dependencies_raw: Raw dependencies list from meta/main.yml

        Returns:
            list[Dependency]: Parsed Dependency value objects
        """
        dependencies = []

        for dep_data in dependencies_raw:
            # Format 1: Simple string (role name only)
            if isinstance(dep_data, str):
                dependencies.append(Dependency(name=dep_data, version=None, source=None))
            # Format 2: Dictionary with name/version/source
            elif isinstance(dep_data, dict):
                # Try 'name' key first, fallback to 'role' key
                name = dep_data.get("name") or dep_data.get("role")
                if not name:
                    logger.warning("dependency_missing_name", dep_data=dep_data)
                    continue

                version = dep_data.get("version")
                source = dep_data.get("src") or dep_data.get("source")

                dependencies.append(Dependency(name=name, version=version, source=source))
            else:
                logger.warning("invalid_dependency_format", dep_data=dep_data)

        return dependencies
