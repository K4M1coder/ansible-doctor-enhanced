"""
Unit tests for TodoParser.

Tests the TodoParser which extracts @todo annotations from role files.
Following TDD Red-Green-Refactor cycle for Phase 8 US4 (TODO extraction).
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ansibledoctor.models.todo import TodoItem
from ansibledoctor.parser.todo_parser import TodoParser


class TestTodoParserCreation:
    """Test TodoParser initialization."""

    def test_create_todo_parser(self):
        """Should create TodoParser."""
        parser = TodoParser()

        assert parser is not None


class TestSimpleTodoExtraction:
    """Test extracting simple @todo annotations."""

    def test_extract_simple_todo_annotation(self, tmp_path):
        """Should extract basic @todo comment."""
        file_path = tmp_path / "tasks" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""
# @todo: Implement error handling
- name: Deploy application
  command: /usr/bin/deploy
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 1
        assert todos[0].description == "Implement error handling"
        # parse_file() returns absolute paths, parse_role() makes them relative
        assert str(file_path) in todos[0].file_path
        assert todos[0].line_number == 2
        assert todos[0].priority is None

    def test_extract_todo_with_colon_in_description(self, tmp_path):
        """Should handle todo descriptions containing colons."""
        file_path = tmp_path / "vars" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("# @todo: Fix issue: variable not validated\n")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 1
        assert "Fix issue: variable not validated" in todos[0].description


class TestTodoWithPriority:
    """Test extracting @todo annotations with priority."""

    def test_extract_todo_with_high_priority(self, tmp_path):
        """Should parse priority from @todo annotation."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("# @todo [HIGH]: Critical bug fix needed\n")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 1
        assert todos[0].priority == "high"
        assert "Critical bug fix needed" in todos[0].description

    def test_extract_todo_with_medium_priority(self, tmp_path):
        """Should handle different priority levels."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("# @todo [MEDIUM]: Refactor this code\n")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos[0].priority == "medium"

    def test_extract_todo_with_low_priority(self, tmp_path):
        """Should parse low priority todos."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("# @todo [LOW]: Add more tests\n")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos[0].priority == "low"

    def test_extract_todo_with_critical_priority(self, tmp_path):
        """Should parse critical priority todos."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("# @todo [CRITICAL]: Security vulnerability\n")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos[0].priority == "critical"


class TestMultipleTodos:
    """Test extracting multiple @todo annotations."""

    def test_extract_multiple_todos_from_same_file(self, tmp_path):
        """Should extract all @todo annotations in a file."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @todo: First task
var1: value1

# @todo: Second task  
var2: value2

# @todo: Third task
var3: value3
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 3
        descriptions = [t.description for t in todos]
        assert "First task" in descriptions
        assert "Second task" in descriptions
        assert "Third task" in descriptions

    def test_track_line_numbers_for_each_todo(self, tmp_path):
        """Should track correct line number for each todo."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("""# @todo: First todo
# Regular comment
# @todo: Second todo
# Another comment
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 2
        assert todos[0].line_number == 1
        assert todos[1].line_number == 3


class TestMultilineTodos:
    """Test extracting multiline @todo annotations."""

    def test_extract_multiline_todo_annotation(self, tmp_path):
        """Should handle @todo that spans multiple comment lines."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @todo: This is a long todo that needs
#        multiple lines to describe properly
#        and continues here
var: value
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 1
        # Should capture the full description across lines
        assert "long todo" in todos[0].description.lower()

    def test_multiline_todo_ends_at_non_comment(self, tmp_path):
        """Should stop multiline todo at first non-comment line."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @todo: Multiline todo
#        continues here
var: value
# This is not part of the todo
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert len(todos) == 1
        assert "not part" not in todos[0].description


class TestFileTypeScanning:
    """Test scanning different file types for @todo."""

    def test_scan_yaml_files(self, tmp_path):
        """Should scan .yml and .yaml files."""
        (tmp_path / "test.yml").write_text("# @todo: In yml file\n")
        (tmp_path / "test.yaml").write_text("# @todo: In yaml file\n")

        parser = TodoParser()
        todos = parser.parse_directory(tmp_path)

        assert len(todos) == 2

    def test_scan_python_files(self, tmp_path):
        """Should scan .py files for todos."""
        py_file = tmp_path / "script.py"
        py_file.write_text("# @todo: In python file\n")

        parser = TodoParser()
        todos = parser.parse_directory(tmp_path)

        assert len(todos) == 1
        assert "python file" in todos[0].description.lower()

    def test_scan_jinja2_templates(self, tmp_path):
        """Should scan .j2 template files."""
        j2_file = tmp_path / "template.j2"
        j2_file.write_text("{# @todo: In jinja2 template #}\n")

        parser = TodoParser()
        todos = parser.parse_file(j2_file)

        assert len(todos) == 1


class TestRoleWideScanning:
    """Test scanning entire role directory for @todo."""

    def test_scan_role_all_directories(self, tmp_path):
        """Should scan all standard role directories."""
        role_path = tmp_path / "my_role"
        
        # Create todos in different directories
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "tasks" / "main.yml").write_text("# @todo: In tasks\n")
        
        (role_path / "defaults").mkdir(parents=True)
        (role_path / "defaults" / "main.yml").write_text("# @todo: In defaults\n")
        
        (role_path / "vars").mkdir(parents=True)
        (role_path / "vars" / "main.yml").write_text("# @todo: In vars\n")
        
        (role_path / "handlers").mkdir(parents=True)
        (role_path / "handlers" / "main.yml").write_text("# @todo: In handlers\n")

        parser = TodoParser()
        todos = parser.parse_role(role_path)

        assert len(todos) == 4

    def test_ignore_non_source_directories(self, tmp_path):
        """Should skip .git, .hypothesis, __pycache__ directories."""
        role_path = tmp_path / "role"
        
        (role_path / ".git").mkdir(parents=True)
        (role_path / ".git" / "config").write_text("# @todo: Should be ignored\n")
        
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "tasks" / "main.yml").write_text("# @todo: Should be found\n")

        parser = TodoParser()
        todos = parser.parse_role(role_path)

        assert len(todos) == 1
        assert "Should be found" in todos[0].description


class TestNoTodosCase:
    """Test handling files without @todo annotations."""

    def test_file_without_todos(self, tmp_path):
        """Should return empty list when no todos found."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
var: value
# Regular comment
another_var: another_value
""")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos == []

    def test_empty_file(self, tmp_path):
        """Should handle empty file gracefully."""
        file_path = tmp_path / "test.yml"
        file_path.write_text("")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos == []

    def test_role_without_todos(self, tmp_path):
        """Should return empty list when role has no todos."""
        role_path = tmp_path / "role"
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "tasks" / "main.yml").write_text("- name: Task\n  debug: msg='hi'\n")

        parser = TodoParser()
        todos = parser.parse_role(role_path)

        assert todos == []


class TestErrorHandling:
    """Test error handling in TodoParser."""

    def test_handle_nonexistent_file(self, tmp_path):
        """Should handle missing file gracefully."""
        file_path = tmp_path / "nonexistent.yml"

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos == []

    def test_handle_binary_file(self, tmp_path):
        """Should skip binary files without crashing."""
        file_path = tmp_path / "binary.bin"
        file_path.write_bytes(b"\x00\x01\x02\x03")

        parser = TodoParser()
        todos = parser.parse_file(file_path)

        assert todos == []

    def test_handle_permission_error(self, tmp_path):
        """Should handle files that can't be read."""
        # This test is platform-dependent and may be skipped
        pytest.skip("Permission testing requires platform-specific setup")


class TestRelativePathTracking:
    """Test tracking relative paths for todos."""

    def test_store_relative_path_from_role_root(self, tmp_path):
        """Should store path relative to role root."""
        role_path = tmp_path / "my_role"
        task_file = role_path / "tasks" / "install.yml"
        task_file.parent.mkdir(parents=True)
        task_file.write_text("# @todo: Test todo\n")

        parser = TodoParser()
        todos = parser.parse_role(role_path)

        assert len(todos) == 1
        # Path should be relative to role root
        assert todos[0].file_path == "tasks/install.yml"
