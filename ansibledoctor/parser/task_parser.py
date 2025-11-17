"""
TaskParser for extracting tags from Ansible task files.

Parses tasks/*.yml files to discover all tags used in task definitions.
Aggregates tags with usage counts and file locations for documentation.

Part of Phase 8 US3 (Task Tags extraction).
"""

import structlog
from pathlib import Path
from typing import Protocol

from ansibledoctor.models.tag import Tag


class YamlLoaderProtocol(Protocol):
    """Protocol for YAML loading dependency."""

    def load_file(self, file_path: Path) -> list | dict:
        """Load and parse YAML file."""
        ...


class TaskParser:
    """
    Parser for extracting tags from Ansible task files.
    
    Discovers all task files in a role's tasks/ directory, extracts tag
    definitions, and aggregates them with usage statistics.
    
    Follows DDD Repository pattern for accessing task data.
    """

    def __init__(self, yaml_loader: YamlLoaderProtocol) -> None:
        """
        Initialize TaskParser.
        
        Args:
            yaml_loader: YAML file loader for reading task files
        """
        self.yaml_loader = yaml_loader
        self.logger = structlog.get_logger()

    def parse_task_file(self, task_file: Path) -> list[Tag]:
        """
        Parse a single task file and extract tags.
        
        Args:
            task_file: Path to task YAML file
            
        Returns:
            List of unique Tag objects found in the file
        """
        try:
            content = self.yaml_loader.load_file(task_file)
            
            # Task files should contain a list of tasks
            if not isinstance(content, list):
                self.logger.warning(
                    "task_file_not_list",
                    file=str(task_file),
                    type=type(content).__name__,
                )
                return []
            
            # Collect all tags from all tasks
            tag_map: dict[str, dict] = {}  # name -> {count, locations}
            
            for task_index, task in enumerate(content):
                if not isinstance(task, dict):
                    continue
                
                # Extract tags field (can be string or list)
                tags_field = task.get("tags")
                if not tags_field:
                    continue
                
                # Normalize to list
                if isinstance(tags_field, str):
                    tag_names = [tags_field]
                elif isinstance(tags_field, list):
                    tag_names = tags_field
                else:
                    continue
                
                # Process each tag
                for tag_name in tag_names:
                    if not isinstance(tag_name, str):
                        continue
                    
                    # Clean tag name
                    tag_name = tag_name.strip()
                    if not tag_name:
                        continue
                    
                    # Track tag usage
                    if tag_name not in tag_map:
                        tag_map[tag_name] = {"count": 0, "locations": []}
                    
                    tag_map[tag_name]["count"] += 1
                    # Store location (simplified - could be enhanced with line numbers)
                    location = f"{task_file.name}:{task_index + 1}"
                    tag_map[tag_name]["locations"].append(location)
            
            # Convert to Tag objects
            tags = []
            for tag_name, data in tag_map.items():
                tag = Tag(
                    name=tag_name,
                    usage_count=data["count"],
                    file_locations=data["locations"],
                )
                tags.append(tag)
            
            return tags
            
        except Exception as exc:
            self.logger.error(
                "task_file_parse_error",
                file=str(task_file),
                error=str(exc),
            )
            return []

    def parse_role_tasks(self, role_path: Path) -> list[Tag]:
        """
        Parse all task files in a role's tasks/ directory.
        
        Args:
            role_path: Path to role root directory
            
        Returns:
            List of unique Tag objects aggregated from all task files
        """
        tasks_dir = role_path / "tasks"
        
        if not tasks_dir.exists():
            self.logger.info(
                "tasks_directory_missing",
                role=role_path.name,
                tasks_dir=str(tasks_dir),
            )
            return []
        
        # Find all YAML files in tasks/
        task_files = list(tasks_dir.glob("*.yml")) + list(tasks_dir.glob("*.yaml"))
        
        if not task_files:
            self.logger.info(
                "no_task_files_found",
                role=role_path.name,
                tasks_dir=str(tasks_dir),
            )
            return []
        
        # Aggregate tags from all files
        global_tag_map: dict[str, dict] = {}
        
        for task_file in sorted(task_files):
            file_tags = self.parse_task_file(task_file)
            
            for tag in file_tags:
                if tag.name not in global_tag_map:
                    global_tag_map[tag.name] = {
                        "count": 0,
                        "locations": [],
                    }
                
                global_tag_map[tag.name]["count"] += tag.usage_count
                global_tag_map[tag.name]["locations"].extend(tag.file_locations)
        
        # Convert to final Tag objects
        tags = []
        for tag_name, data in global_tag_map.items():
            tag = Tag(
                name=tag_name,
                usage_count=data["count"],
                file_locations=data["locations"],
            )
            tags.append(tag)
        
        self.logger.info(
            "role_tasks_parsed",
            role=role_path.name,
            task_files=len(task_files),
            unique_tags=len(tags),
        )
        
        return tags
