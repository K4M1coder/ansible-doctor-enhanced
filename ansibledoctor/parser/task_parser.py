"""
TaskParser for extracting tags from Ansible task files.

Parses tasks/*.yml files to discover all tags used in task definitions.
Aggregates tag usage counts and tracks file locations.

Following Constitution Article X (Domain-Driven Design):
- Domain Service: TaskParser extracts tags from infrastructure (YAML files)
- Uses Protocol-based dependency injection for testability
"""

from pathlib import Path
from typing import Any

import structlog

from ansibledoctor.models.tag import Tag
from ansibledoctor.parser.protocols import YAMLLoader

logger = structlog.get_logger()


class TaskParser:
    """
    Domain Service: Parse Ansible task files to extract tags.

    Discovers all task files in the tasks/ directory, extracts tags from
    task definitions, aggregates usage counts, and tracks file locations.

    This parser focuses solely on tag extraction. Tag descriptions from
    @tag annotations are handled separately by the annotation parser and
    merged at the RoleParser level.
    """

    def __init__(self, yaml_loader: YAMLLoader):
        """
        Initialize TaskParser with dependencies.

        Args:
            yaml_loader: YAML file loader for reading task files
        """
        self.yaml_loader = yaml_loader

    def _collect_task_files(
        self, role_path: Path, current_file: Path, visited: set[Path]
    ) -> list[Path]:
        """
        Recursively collect all task files starting from current_file, following includes.
        """
        files: list[Path] = []
        if current_file in visited:
            return files
        visited.add(current_file)
        files.append(current_file)

        try:
            tasks = self.yaml_loader.load_file(current_file)
            if isinstance(tasks, list):
                for task in tasks:
                    if isinstance(task, dict):
                        for include_key in ["include_tasks", "import_tasks"]:
                            if include_key in task:
                                include_path = task[include_key]
                                if isinstance(include_path, str):
                                    included_file = (role_path / "tasks" / include_path).resolve()
                                    if (
                                        included_file.exists()
                                        and included_file.suffix == ".yml"
                                        and included_file not in visited
                                    ):
                                        files.extend(
                                            self._collect_task_files(
                                                role_path, included_file, visited
                                            )
                                        )
        except Exception as e:
            logger.warning("error_collecting_includes", file=str(current_file), error=str(e))

        return files

    def parse_tasks(self, role_path: Path) -> list[Tag]:
        """
        Parse all task files in role to extract tags.

        Reads tasks/main.yml and recursively follows include_tasks/import_tasks to discover
        all tags used in the role. Aggregates tag usage counts and tracks
        file locations.

        Args:
            role_path: Absolute path to role directory

        Returns:
            List of Tag objects with usage counts and file locations

        Note:
            Returns empty list if tasks directory doesn't exist or contains
            no valid task files. Logs warnings for parsing errors.
        """
        tags_dict: dict[str, dict[str, Any]] = {}
        tasks_file = role_path / "tasks" / "main.yml"

        if not tasks_file.exists():
            logger.debug("no_tasks_main_yml", role_path=str(role_path))
            return []

        # Collect all task files recursively following includes
        all_task_files = self._collect_task_files(role_path, tasks_file, set())

        # Parse each task file for tags
        for task_file in all_task_files:
            try:
                tasks = self.yaml_loader.load_file(task_file)

                if not tasks or not isinstance(tasks, list):
                    continue

                # Extract tags from each task
                for task_index, task in enumerate(tasks):
                    if not isinstance(task, dict):
                        continue

                    task_tags = task.get("tags")
                    if not task_tags:
                        continue

                    # Handle both string and list formats
                    if isinstance(task_tags, str):
                        task_tags = [task_tags]
                    elif not isinstance(task_tags, list):
                        logger.warning(
                            "invalid_tags_type",
                            task_index=task_index,
                            task_name=task.get("name", "unnamed"),
                            tags_type=type(task_tags).__name__,
                        )
                        continue

                    # Process each tag
                    _task_name = task.get("name", f"task_{task_index}")
                    file_location = f"{task_file.relative_to(role_path)}:{task_index + 1}"

                    for tag_name in task_tags:
                        if not isinstance(tag_name, str):
                            continue

                        tag_name = tag_name.strip()
                        if not tag_name:
                            continue

                        # Aggregate tag information
                        if tag_name not in tags_dict:
                            tags_dict[tag_name] = {
                                "name": tag_name,
                                "usage_count": 0,
                                "file_locations": [],
                            }

                        tags_dict[tag_name]["usage_count"] += 1
                        if file_location not in tags_dict[tag_name]["file_locations"]:
                            tags_dict[tag_name]["file_locations"].append(file_location)

                logger.debug(
                    "tags_extracted_from_file",
                    file=str(task_file),
                    tags_found=len([t for t in tasks if isinstance(t, dict) and t.get("tags")]),
                )

            except Exception as e:
                logger.warning(
                    "task_file_parsing_error",
                    file=str(task_file),
                    error=str(e),
                )

        # Convert dictionary to Tag objects
        tags = [
            Tag(
                name=tag_data["name"],
                description=None,
                usage_count=tag_data["usage_count"],
                file_locations=tag_data["file_locations"],
            )
            for tag_data in tags_dict.values()
        ]

        logger.debug(
            "task_parsing_complete",
            role_path=str(role_path),
            unique_tags=len(tags),
            files_parsed=len(all_task_files),
        )

        # Return sorted by name for consistency
        return sorted(tags, key=lambda t: t.name)
