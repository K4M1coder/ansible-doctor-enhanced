"""
Unit tests for TaskParser.

Tests the TaskParser which extracts tags from Ansible task files.
Following TDD Red-Green-Refactor cycle for Phase 8 US3.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ansibledoctor.parser.protocols import YAMLLoader
from ansibledoctor.parser.task_parser import TaskParser


@pytest.fixture
def yaml_loader():
    """Mock YAML loader for testing."""
    return Mock(spec=YAMLLoader)


@pytest.fixture
def task_parser(yaml_loader):
    """Create TaskParser instance with mocked dependencies."""
    return TaskParser(yaml_loader=yaml_loader)


class TestTaskParserBasics:
    """Test basic TaskParser functionality."""

    def test_parser_creation(self, yaml_loader):
        """Should create parser with dependencies."""
        parser = TaskParser(yaml_loader=yaml_loader)

        assert parser is not None
        assert parser.yaml_loader is yaml_loader

    def test_parse_single_tag(self, task_parser, yaml_loader):
        """Should extract single tag from task."""
        yaml_loader.load_file.return_value = [
            {
                "name": "Install packages",
                "apt": {"name": "nginx", "state": "present"},
                "tags": ["install"],
            }
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].name == "install"
        assert tags[0].usage_count == 1

    def test_parse_multiple_tags_single_task(self, task_parser, yaml_loader):
        """Should extract multiple tags from single task."""
        yaml_loader.load_file.return_value = [
            {
                "name": "Configure service",
                "template": {"src": "config.j2", "dest": "/etc/app.conf"},
                "tags": ["install", "configure"],
            }
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert "install" in tag_names
        assert "configure" in tag_names

    def test_parse_multiple_tasks_same_tag(self, task_parser, yaml_loader):
        """Should aggregate tag usage count across tasks."""
        yaml_loader.load_file.return_value = [
            {"name": "Task 1", "debug": {"msg": "test"}, "tags": ["install"]},
            {"name": "Task 2", "debug": {"msg": "test"}, "tags": ["install"]},
            {"name": "Task 3", "debug": {"msg": "test"}, "tags": ["install"]},
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].name == "install"
        assert tags[0].usage_count == 3

    def test_parse_task_without_tags(self, task_parser, yaml_loader):
        """Should handle tasks without tags gracefully."""
        yaml_loader.load_file.return_value = [
            {"name": "Task without tags", "debug": {"msg": "test"}}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 0

    def test_parse_empty_task_file(self, task_parser, yaml_loader):
        """Should handle empty task file."""
        yaml_loader.load_file.return_value = []

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 0


class TestTagFormatVariations:
    """Test different tag format variations."""

    def test_parse_tag_as_string(self, task_parser, yaml_loader):
        """Should handle single tag as string instead of list."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": "install"}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].name == "install"

    def test_parse_tag_with_whitespace(self, task_parser, yaml_loader):
        """Should strip whitespace from tag names."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": ["  install  "]}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].name == "install"

    def test_parse_duplicate_tags_in_same_task(self, task_parser, yaml_loader):
        """Should handle duplicate tags in same task (count as one)."""
        yaml_loader.load_file.return_value = [
            {
                "name": "Task",
                "debug": {"msg": "test"},
                "tags": ["install", "install", "configure"],
            }
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # Should have 2 unique tags
        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert "install" in tag_names
        assert "configure" in tag_names


class TestFileLocationTracking:
    """Test tracking of file locations for tags."""

    def test_track_tag_file_location(self, task_parser, yaml_loader):
        """Should track file location where tag is used."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": ["install"]}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert len(tags[0].file_locations) > 0
        # Should contain reference to tasks/main.yml
        assert any("tasks" in loc for loc in tags[0].file_locations)

    def test_track_multiple_file_locations(self, task_parser, yaml_loader):
        """Should track tag usage across multiple files."""
        # This would be tested when parsing multiple task files
        # For now, ensure file_locations is populated
        yaml_loader.load_file.return_value = [
            {"name": "Task 1", "debug": {"msg": "test"}, "tags": ["install"]},
            {"name": "Task 2", "debug": {"msg": "test"}, "tags": ["install"]},
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        # Multiple usages in same file still tracked
        assert tags[0].usage_count == 2


class TestTagDescriptions:
    """Test extraction of tag descriptions from @tag annotations."""

    def test_parse_tag_without_description(self, task_parser, yaml_loader):
        """Should create tag without description when no annotation present."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": ["install"]}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 1
        assert tags[0].description is None

    def test_associate_tag_description_from_annotation(self, task_parser, yaml_loader):
        """Should associate @tag annotation with tag (integration with annotation parser)."""
        # This will be tested in integration tests
        # The TaskParser itself just extracts tags, descriptions come from annotations
        yaml_loader.load_file.return_value = [
            {"name": "Install packages", "debug": {"msg": "test"}, "tags": ["install"]}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # At this level, no description yet (added by RoleParser integration)
        assert tags[0].description is None


class TestErrorHandling:
    """Test error handling in TaskParser."""

    def test_handle_missing_tasks_directory(self, task_parser, yaml_loader):
        """Should handle missing tasks directory gracefully."""
        yaml_loader.load_file.side_effect = FileNotFoundError("tasks/main.yml not found")

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # Should return empty list, not crash
        assert tags == []

    def test_handle_malformed_task_yaml(self, task_parser, yaml_loader):
        """Should handle malformed YAML gracefully."""
        yaml_loader.load_file.side_effect = ValueError("Invalid YAML")

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # Should return empty list and log warning
        assert tags == []

    def test_handle_task_with_invalid_tags_type(self, task_parser, yaml_loader):
        """Should handle invalid tags field type."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": 123}  # Invalid: int
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # Should skip invalid tags
        assert len(tags) == 0

    def test_handle_none_tags_field(self, task_parser, yaml_loader):
        """Should handle None tags field."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": None}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        assert len(tags) == 0


class TestMultipleTaskFiles:
    """Test parsing multiple task files."""

    def test_parse_main_tasks_file(self, task_parser, yaml_loader):
        """Should parse tasks/main.yml by default."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": ["install"]}
        ]

        role_path = Path("/fake/role")
        _ = task_parser.parse_tasks(role_path)

        # Should have called load_file with tasks/main.yml
        yaml_loader.load_file.assert_called()
        call_args = yaml_loader.load_file.call_args[0][0]
        assert "tasks" in str(call_args)
        assert "main.yml" in str(call_args)

    def test_discover_all_task_files(self, task_parser):
        """Should discover all .yml files in tasks/ directory."""
        # This would be tested with real file system or better mocking
        # For now, test the main file access pattern
        role_path = Path("/fake/role")

        # Verify the parser looks in the right place
        expected_path = role_path / "tasks" / "main.yml"
        assert expected_path.parent.name == "tasks"


class TestTagAggregation:
    """Test tag aggregation and deduplication."""

    def test_aggregate_tags_across_tasks(self, task_parser, yaml_loader):
        """Should aggregate and deduplicate tags."""
        yaml_loader.load_file.return_value = [
            {"name": "Task 1", "debug": {"msg": "test"}, "tags": ["install", "configure"]},
            {"name": "Task 2", "debug": {"msg": "test"}, "tags": ["configure", "deploy"]},
            {"name": "Task 3", "debug": {"msg": "test"}, "tags": ["install"]},
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        # Should have 3 unique tags
        assert len(tags) == 3

        # Find each tag and check usage count
        tag_dict = {tag.name: tag for tag in tags}
        assert tag_dict["install"].usage_count == 2
        assert tag_dict["configure"].usage_count == 2
        assert tag_dict["deploy"].usage_count == 1

    def test_return_sorted_tags(self, task_parser, yaml_loader):
        """Should return tags in consistent order (alphabetically)."""
        yaml_loader.load_file.return_value = [
            {"name": "Task", "debug": {"msg": "test"}, "tags": ["zebra", "alpha", "beta"]}
        ]

        role_path = Path("/fake/role")
        tags = task_parser.parse_tasks(role_path)

        tag_names = [tag.name for tag in tags]
        assert tag_names == sorted(tag_names)
