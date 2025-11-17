"""
Unit tests for TaskParser.

Tests the TaskParser which extracts tags from Ansible task files.
Following TDD Red-Green-Refactor cycle for Phase 8 US3 (Task Tags).
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ansibledoctor.models.tag import Tag
from ansibledoctor.parser.task_parser import TaskParser


class TestTaskParserCreation:
    """Test TaskParser initialization."""

    def test_create_task_parser(self):
        """Should create TaskParser with YAML loader."""
        yaml_loader = Mock()
        parser = TaskParser(yaml_loader=yaml_loader)

        assert parser is not None
        assert parser.yaml_loader == yaml_loader


class TestSingleTagExtraction:
    """Test extracting a single tag from tasks."""

    def test_extract_single_tag_from_task(self, tmp_path):
        """Should extract one tag from a task definition."""
        # Create test task file
        task_file = tmp_path / "tasks" / "main.yml"
        task_file.parent.mkdir(parents=True)
        task_file.write_text("""
- name: Install nginx
  apt:
    name: nginx
    state: present
  tags: install
""")

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {
                "name": "Install nginx",
                "apt": {"name": "nginx", "state": "present"},
                "tags": "install",
            }
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert len(tags) == 1
        assert tags[0].name == "install"
        assert tags[0].usage_count == 1

    def test_extract_tag_from_task_list_format(self, tmp_path):
        """Should handle tags as list with single item."""
        task_file = tmp_path / "main.yml"
        task_file.write_text("- name: Task\n  tags: [install]")

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task", "tags": ["install"]}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert len(tags) == 1
        assert tags[0].name == "install"


class TestMultipleTagsExtraction:
    """Test extracting multiple tags from tasks."""

    def test_extract_multiple_tags_from_single_task(self, tmp_path):
        """Should extract all tags when task has multiple tags."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Configure app", "tags": ["install", "configure", "deploy"]}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert len(tags) == 3
        tag_names = {tag.name for tag in tags}
        assert tag_names == {"install", "configure", "deploy"}

    def test_aggregate_duplicate_tags_across_tasks(self, tmp_path):
        """Should count duplicate tags only once but track usage."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task 1", "tags": ["install"]},
            {"name": "Task 2", "tags": ["install"]},
            {"name": "Task 3", "tags": ["configure"]},
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        # Should return unique tags
        assert len(tags) == 2
        
        install_tag = next(t for t in tags if t.name == "install")
        assert install_tag.usage_count == 2

        configure_tag = next(t for t in tags if t.name == "configure")
        assert configure_tag.usage_count == 1


class TestNoTagsCase:
    """Test handling tasks without tags."""

    def test_task_without_tags_field(self, tmp_path):
        """Should return empty list when task has no tags."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task without tags", "debug": {"msg": "hello"}}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert tags == []

    def test_empty_task_file(self, tmp_path):
        """Should handle empty task file gracefully."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = []

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert tags == []

    def test_task_with_empty_tags_list(self, tmp_path):
        """Should handle task with empty tags list."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task", "tags": []}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert tags == []


class TestFileLocationTracking:
    """Test tracking where tags appear in files."""

    def test_track_file_location_for_tags(self, tmp_path):
        """Should record file path where tag is found."""
        task_file = tmp_path / "tasks" / "install.yml"
        task_file.parent.mkdir(parents=True)

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Install", "tags": "install"}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert len(tags) == 1
        assert len(tags[0].file_locations) == 1
        assert "install.yml" in tags[0].file_locations[0]

    def test_track_multiple_locations_for_same_tag(self, tmp_path):
        """Should track all locations where a tag appears."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        # Simulate YAML with line tracking (simplified)
        yaml_loader.load_file.return_value = [
            {"name": "Task 1", "tags": "install"},
            {"name": "Task 2", "tags": "install"},
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        install_tag = tags[0]
        assert install_tag.usage_count == 2
        # File locations should be tracked (exact format TBD in implementation)
        assert len(install_tag.file_locations) >= 1


class TestRoleWideTagCollection:
    """Test collecting tags from all task files in a role."""

    def test_parse_role_tasks_directory(self, tmp_path):
        """Should discover and parse all task files in role."""
        role_path = tmp_path / "my_role"
        tasks_dir = role_path / "tasks"
        tasks_dir.mkdir(parents=True)

        # Create multiple task files
        (tasks_dir / "main.yml").write_text("- name: Main\n  tags: install")
        (tasks_dir / "configure.yml").write_text("- name: Config\n  tags: configure")

        yaml_loader = Mock()
        yaml_loader.load_file.side_effect = [
            [{"name": "Main", "tags": "install"}],
            [{"name": "Config", "tags": "configure"}],
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_role_tasks(role_path)

        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert tag_names == {"install", "configure"}

    def test_aggregate_tags_across_multiple_files(self, tmp_path):
        """Should aggregate same tags from different files."""
        role_path = tmp_path / "role"
        tasks_dir = role_path / "tasks"
        tasks_dir.mkdir(parents=True)

        (tasks_dir / "install.yml").write_text("- tags: install")
        (tasks_dir / "deploy.yml").write_text("- tags: install")

        yaml_loader = Mock()
        yaml_loader.load_file.side_effect = [
            [{"name": "T1", "tags": "install"}],
            [{"name": "T2", "tags": "install"}],
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_role_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].name == "install"
        assert tags[0].usage_count == 2
        assert len(tags[0].file_locations) == 2


class TestErrorHandling:
    """Test error handling in TaskParser."""

    def test_handle_missing_tasks_directory(self, tmp_path):
        """Should handle missing tasks/ directory gracefully."""
        role_path = tmp_path / "role"
        role_path.mkdir()

        yaml_loader = Mock()
        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_role_tasks(role_path)

        assert tags == []

    def test_handle_malformed_yaml_in_task_file(self, tmp_path):
        """Should log error and continue when YAML is malformed."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.side_effect = Exception("YAML parse error")

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        # Should return empty list and not crash
        assert tags == []

    def test_handle_non_list_task_structure(self, tmp_path):
        """Should handle task file that doesn't return list."""
        task_file = tmp_path / "main.yml"

        yaml_loader = Mock()
        yaml_loader.load_file.return_value = {"not": "a list"}

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(task_file)

        assert tags == []


class TestTagStringFormats:
    """Test different tag string formats in YAML."""

    def test_tag_as_string(self):
        """Should handle tags as single string value."""
        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task", "tags": "install"}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(Path("test.yml"))

        assert len(tags) == 1
        assert tags[0].name == "install"

    def test_tag_as_list(self):
        """Should handle tags as list of strings."""
        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task", "tags": ["install", "configure"]}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(Path("test.yml"))

        assert len(tags) == 2

    def test_tag_with_whitespace(self):
        """Should strip whitespace from tag names."""
        yaml_loader = Mock()
        yaml_loader.load_file.return_value = [
            {"name": "Task", "tags": "  install  "}
        ]

        parser = TaskParser(yaml_loader=yaml_loader)
        tags = parser.parse_task_file(Path("test.yml"))

        assert tags[0].name == "install"
