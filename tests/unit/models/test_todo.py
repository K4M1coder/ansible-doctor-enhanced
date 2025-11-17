"""
Unit tests for TodoItem value object.

Tests the TodoItem model which represents a @todo annotation found in role files.
Following TDD Red-Green-Refactor cycle for Phase 8 US4.
"""

import pytest
from pydantic import ValidationError

from ansibledoctor.models.todo import TodoItem


class TestTodoItemCreation:
    """Test TodoItem value object creation and validation."""

    def test_create_simple_todo(self):
        """Should create todo with required fields."""
        todo = TodoItem(
            description="Implement feature X",
            file_path="tasks/main.yml",
            line_number=42,
        )

        assert todo.description == "Implement feature X"
        assert todo.file_path == "tasks/main.yml"
        assert todo.line_number == 42
        assert todo.priority is None

    def test_create_todo_with_priority(self):
        """Should create todo with priority specification."""
        todo = TodoItem(
            description="Fix critical bug",
            file_path="handlers/main.yml",
            line_number=10,
            priority="high",
        )

        assert todo.description == "Fix critical bug"
        assert todo.priority == "high"

    def test_todo_description_required(self):
        """Should fail validation when description is missing."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(  # type: ignore
                file_path="test.yml",
                line_number=1,
            )

        assert "description" in str(exc_info.value)

    def test_todo_file_path_required(self):
        """Should fail validation when file_path is missing."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(  # type: ignore
                description="Test todo",
                line_number=1,
            )

        assert "file_path" in str(exc_info.value)

    def test_todo_line_number_required(self):
        """Should fail validation when line_number is missing."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(  # type: ignore
                description="Test todo",
                file_path="test.yml",
            )

        assert "line_number" in str(exc_info.value)

    def test_todo_description_cannot_be_empty(self):
        """Should fail validation when description is empty string."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(
                description="",
                file_path="test.yml",
                line_number=1,
            )

        assert "description" in str(exc_info.value)

    def test_todo_file_path_cannot_be_empty(self):
        """Should fail validation when file_path is empty string."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(
                description="Test todo",
                file_path="",
                line_number=1,
            )

        assert "file_path" in str(exc_info.value)

    def test_todo_line_number_must_be_positive(self):
        """Should fail validation when line_number is zero or negative."""
        with pytest.raises(ValidationError) as exc_info:
            TodoItem(
                description="Test todo",
                file_path="test.yml",
                line_number=0,
            )

        assert "line_number" in str(exc_info.value)

        with pytest.raises(ValidationError):
            TodoItem(
                description="Test todo",
                file_path="test.yml",
                line_number=-5,
            )

    def test_todo_is_immutable(self):
        """Should prevent modification of todo after creation (frozen)."""
        todo = TodoItem(
            description="Test",
            file_path="test.yml",
            line_number=1,
        )

        with pytest.raises(ValidationError):
            todo.description = "Modified"  # type: ignore


class TestTodoItemPriority:
    """Test TodoItem priority handling."""

    def test_valid_priority_values(self):
        """Should accept valid priority values."""
        priorities = ["low", "medium", "high", "critical"]

        for priority in priorities:
            todo = TodoItem(
                description="Test",
                file_path="test.yml",
                line_number=1,
                priority=priority,
            )
            assert todo.priority == priority

    def test_priority_case_insensitive(self):
        """Should normalize priority to lowercase."""
        todo = TodoItem(
            description="Test",
            file_path="test.yml",
            line_number=1,
            priority="HIGH",
        )

        assert todo.priority == "high"

    def test_default_priority_is_none(self):
        """Should have no priority by default."""
        todo = TodoItem(
            description="Test",
            file_path="test.yml",
            line_number=1,
        )

        assert todo.priority is None


class TestTodoItemSerialization:
    """Test TodoItem serialization to dict/JSON."""

    def test_todo_to_dict(self):
        """Should serialize todo to dictionary."""
        todo = TodoItem(
            description="Refactor parser logic",
            file_path="ansibledoctor/parser/role_parser.py",
            line_number=125,
            priority="medium",
        )

        result = todo.model_dump()

        assert result["description"] == "Refactor parser logic"
        assert result["file_path"] == "ansibledoctor/parser/role_parser.py"
        assert result["line_number"] == 125
        assert result["priority"] == "medium"

    def test_todo_to_json(self):
        """Should serialize todo to JSON string."""
        todo = TodoItem(
            description="Add error handling",
            file_path="tasks/main.yml",
            line_number=50,
        )

        json_str = todo.model_dump_json()

        assert "Add error handling" in json_str
        assert "tasks/main.yml" in json_str
        assert "50" in json_str


class TestTodoItemLocation:
    """Test TodoItem location formatting."""

    def test_get_location_string(self):
        """Should format file location as file:line."""
        todo = TodoItem(
            description="Test",
            file_path="vars/main.yml",
            line_number=33,
        )

        # This would be a helper method
        location = f"{todo.file_path}:{todo.line_number}"

        assert location == "vars/main.yml:33"

    def test_multiple_todos_same_file(self):
        """Should handle multiple todos from same file with different lines."""
        todo1 = TodoItem(
            description="First todo",
            file_path="tasks/main.yml",
            line_number=10,
        )
        todo2 = TodoItem(
            description="Second todo",
            file_path="tasks/main.yml",
            line_number=25,
        )

        assert todo1.file_path == todo2.file_path
        assert todo1.line_number != todo2.line_number


class TestTodoItemRepresentation:
    """Test TodoItem string representation."""

    def test_todo_repr(self):
        """Should provide useful string representation."""
        todo = TodoItem(
            description="Implement feature",
            file_path="test.yml",
            line_number=1,
        )

        repr_str = repr(todo)

        assert "TodoItem" in repr_str
        assert "test.yml" in repr_str or "1" in repr_str

    def test_todo_str(self):
        """Should provide readable string format."""
        todo = TodoItem(
            description="Fix bug",
            file_path="tasks/main.yml",
            line_number=42,
        )

        str_result = str(todo)

        assert "Fix bug" in str_result or "tasks/main.yml:42" in str_result
