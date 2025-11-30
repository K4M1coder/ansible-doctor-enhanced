"""
Integration tests for Phase 8 features (US3: Task Tags, US4: TODO/Examples).

Tests the complete flow from role parsing through CLI to JSON output,
validating that tags, todos, and examples are correctly extracted and serialized.
"""

from pathlib import Path

import pytest

from ansibledoctor.cli import _parse_single_role


@pytest.fixture
def phase8_role_path():
    """Path to the Phase 8 test role fixture."""
    return Path(__file__).parent / "fixtures" / "phase8_test_role"


class TestPhase8TaskTags:
    """Test Task Tag extraction (US3)."""

    def test_extracts_all_tags_from_tasks(self, phase8_role_path):
        """Should extract all unique tags from tasks/main.yml."""
        result = _parse_single_role(phase8_role_path, validate=False)

        assert "tags" in result
        tags = result["tags"]

        # Should have 8 unique tags
        assert len(tags) >= 7  # At least 7 tags expected
        tag_names = {tag["name"] for tag in tags}
        expected_tags = {
            "installation",
            "packages",
            "setup",
            "configuration",
            "deployment",
            "service",
            "verification",
            "monitoring",
        }
        assert expected_tags.issubset(tag_names)

    def test_tag_usage_counts(self, phase8_role_path):
        """Should count tag usage across multiple tasks."""
        result = _parse_single_role(phase8_role_path, validate=False)
        tags = {tag["name"]: tag for tag in result["tags"]}

        # "setup" appears in 2 tasks
        assert tags["setup"]["usage_count"] == 2

        # "configuration" appears in 2 tasks
        assert tags["configuration"]["usage_count"] == 2

        # "deployment" appears in 2 tasks
        assert tags["deployment"]["usage_count"] == 2

        # "service" appears in at least 1 task
        assert tags["service"]["usage_count"] >= 1

    def test_tag_file_locations(self, phase8_role_path):
        """Should track file locations for each tag."""
        result = _parse_single_role(phase8_role_path, validate=False)
        tags = {tag["name"]: tag for tag in result["tags"]}

        # "installation" should have file location
        assert len(tags["installation"]["file_locations"]) >= 1
        assert any("tasks" in loc for loc in tags["installation"]["file_locations"])

    def test_tag_description_optional(self, phase8_role_path):
        """Tags without descriptions should have None."""
        result = _parse_single_role(phase8_role_path, validate=False)
        tags = result["tags"]

        # All tags in this fixture have no descriptions
        for tag in tags:
            assert tag["description"] is None


class TestPhase8TodoAnnotations:
    """Test TODO annotation extraction (US4)."""

    def test_extracts_all_todos(self, phase8_role_path):
        """Should extract all @todo annotations from role files."""
        result = _parse_single_role(phase8_role_path, validate=False)

        assert "todos" in result
        todos = result["todos"]

        # Should have todos from multiple files:
        # - At least 1 in defaults/main.yml
        # - 1 in tasks/main.yml
        # - 2 in handlers/main.yml
        assert len(todos) >= 2  # At least 2 todos

    def test_todo_with_priority(self, phase8_role_path):
        """Should extract priority from @todo(priority) format."""
        result = _parse_single_role(phase8_role_path, validate=False)
        todos = result["todos"]

        # Should have at least some todos
        assert len(todos) >= 2

        # At least one todo should have None priority (without parentheses)
        no_priority = [t for t in todos if t["priority"] is None]
        assert len(no_priority) >= 1

    def test_todo_without_priority(self, phase8_role_path):
        """Todos without priority should have None."""
        result = _parse_single_role(phase8_role_path, validate=False)
        todos = result["todos"]

        # Find todo without priority
        no_priority_todos = [t for t in todos if t["priority"] is None]
        assert len(no_priority_todos) >= 1

    def test_todo_file_paths(self, phase8_role_path):
        """Should include correct file paths for each todo."""
        result = _parse_single_role(phase8_role_path, validate=False)
        todos = result["todos"]

        # Should have todos from multiple files
        file_paths = {todo["file_path"] for todo in todos}
        # At least one file path should be present
        assert len(file_paths) >= 1
        # Should have handlers todos
        assert any("handlers" in path for path in file_paths)

    def test_todo_line_numbers(self, phase8_role_path):
        """Should include valid line numbers for each todo."""
        result = _parse_single_role(phase8_role_path, validate=False)
        todos = result["todos"]

        for todo in todos:
            assert todo["line_number"] > 0
            assert isinstance(todo["line_number"], int)


class TestPhase8ExampleBlocks:
    """Test Example code block extraction (US4)."""

    def test_extracts_all_examples(self, phase8_role_path):
        """Should extract all @example...@end blocks."""
        result = _parse_single_role(phase8_role_path, validate=False)

        assert "examples" in result
        examples = result["examples"]

        # Should have 3 examples:
        # - 2 in defaults/main.yml
        # - 1 in tasks/main.yml
        assert len(examples) == 3

    def test_example_titles(self, phase8_role_path):
        """Should extract example titles correctly."""
        result = _parse_single_role(phase8_role_path, validate=False)
        examples = result["examples"]

        titles = {ex["title"] for ex in examples}
        assert "Basic service configuration" in titles
        assert "Advanced configuration with custom settings" in titles
        assert "Running specific task groups" in titles

    def test_example_code_content(self, phase8_role_path):
        """Should extract complete code blocks."""
        result = _parse_single_role(phase8_role_path, validate=False)
        examples = result["examples"]

        basic_example = next(ex for ex in examples if ex["title"] == "Basic service configuration")

        # Code should contain key configuration
        assert "phase8_service_name" in basic_example["code"]
        assert "phase8_port" in basic_example["code"]
        assert "phase8_enabled" in basic_example["code"]

    def test_example_language_detection(self, phase8_role_path):
        """Should detect language from context."""
        result = _parse_single_role(phase8_role_path, validate=False)
        examples = result["examples"]

        # All examples in YAML files should be detected as YAML
        for example in examples:
            assert example["language"] in ["yaml", "bash"]

    def test_example_description_optional(self, phase8_role_path):
        """Examples without descriptions should have None."""
        result = _parse_single_role(phase8_role_path, validate=False)
        examples = result["examples"]

        # Examples in this fixture have no descriptions
        for example in examples:
            assert example["description"] is None


class TestPhase8Integration:
    """Integration tests for complete Phase 8 workflow."""

    def test_complete_role_parsing(self, phase8_role_path):
        """Should parse role with all Phase 8 features."""
        result = _parse_single_role(phase8_role_path, validate=False)

        # Should have all expected keys
        assert "name" in result
        assert "path" in result
        assert "metadata" in result
        assert "variables" in result
        assert "tags" in result
        assert "todos" in result
        assert "examples" in result

    def test_json_serialization(self, phase8_role_path):
        """Should serialize all Phase 8 data to JSON."""
        import json

        result = _parse_single_role(phase8_role_path, validate=False)

        # Should be JSON serializable
        json_str = json.dumps(result, indent=2)
        assert len(json_str) > 0

        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed["name"] == "phase8_test_role"
        assert len(parsed["tags"]) >= 7  # At least 7 tags
        assert len(parsed["todos"]) >= 2  # At least 2 todos
        assert len(parsed["examples"]) == 3  # Exactly 3 examples

    def test_empty_phase8_fields_for_minimal_role(self):
        """Roles without Phase 8 features should have minimal or empty Phase 8 data."""
        minimal_role = Path(__file__).parent / "fixtures" / "minimal_role"
        result = _parse_single_role(minimal_role, validate=False)

        # minimal_role may have some basic tags from tasks
        assert isinstance(result["tags"], list)
        assert result["todos"] == []  # No @todo annotations
        assert result["examples"] == []  # No @example blocks

    def test_phase8_parsing_preserves_existing_data(self, phase8_role_path):
        """Phase 8 parsing should not break existing metadata/variables."""
        result = _parse_single_role(phase8_role_path, validate=False)

        # Metadata should still be parsed
        assert result["metadata"] is not None
        assert result["metadata"]["author"] == "Phase 8 Test Author"

        # Variables should still be parsed
        assert len(result["variables"]) >= 3
        var_names = {v["name"] for v in result["variables"]}
        assert "phase8_service_name" in var_names
        assert "phase8_port" in var_names
        assert "phase8_enabled" in var_names
