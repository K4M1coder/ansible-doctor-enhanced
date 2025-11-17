"""
Unit tests for Example value object.

Tests the Example model which represents a @example code block found in role files.
Following TDD Red-Green-Refactor cycle for Phase 8 US4.
"""

import pytest
from pydantic import ValidationError

from ansibledoctor.models.example import Example


class TestExampleCreation:
    """Test Example value object creation and validation."""

    def test_create_simple_example(self):
        """Should create example with required fields."""
        example = Example(
            title="Basic usage",
            code="- hosts: all\n  roles:\n    - my_role",
        )

        assert example.title == "Basic usage"
        assert example.code == "- hosts: all\n  roles:\n    - my_role"
        assert example.description is None
        assert example.language == "yaml"  # default

    def test_create_example_with_description(self):
        """Should create example with optional description."""
        example = Example(
            title="Advanced configuration",
            code="demo_var: value",
            description="This example shows advanced configuration options",
        )

        assert example.title == "Advanced configuration"
        assert example.description == "This example shows advanced configuration options"

    def test_create_example_with_language(self):
        """Should create example with specified language."""
        example = Example(
            title="Jinja2 template",
            code="{{ demo_var | default('fallback') }}",
            language="jinja2",
        )

        assert example.title == "Jinja2 template"
        assert example.language == "jinja2"

    def test_example_title_required(self):
        """Should fail validation when title is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Example(code="test code")  # type: ignore

        assert "title" in str(exc_info.value)

    def test_example_code_required(self):
        """Should fail validation when code is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Example(title="Test")  # type: ignore

        assert "code" in str(exc_info.value)

    def test_example_title_cannot_be_empty(self):
        """Should fail validation when title is empty string."""
        with pytest.raises(ValidationError) as exc_info:
            Example(title="", code="test")

        assert "title" in str(exc_info.value)

    def test_example_code_cannot_be_empty(self):
        """Should fail validation when code is empty string."""
        with pytest.raises(ValidationError) as exc_info:
            Example(title="Test", code="")

        assert "code" in str(exc_info.value)

    def test_example_is_immutable(self):
        """Should prevent modification of example after creation (frozen)."""
        example = Example(title="Test", code="test code")

        with pytest.raises(ValidationError):
            example.title = "Modified"  # type: ignore


class TestExampleLanguage:
    """Test Example language handling."""

    def test_default_language_is_yaml(self):
        """Should default to 'yaml' language."""
        example = Example(title="Test", code="key: value")

        assert example.language == "yaml"

    def test_valid_language_values(self):
        """Should accept valid language identifiers."""
        languages = ["yaml", "jinja2", "bash", "python", "json"]

        for lang in languages:
            example = Example(title="Test", code="code", language=lang)
            assert example.language == lang

    def test_language_case_insensitive(self):
        """Should normalize language to lowercase."""
        example = Example(title="Test", code="code", language="YAML")

        assert example.language == "yaml"

    def test_language_yml_normalized_to_yaml(self):
        """Should normalize 'yml' to 'yaml' for consistency."""
        example = Example(title="Test", code="code", language="yml")

        assert example.language == "yaml"


class TestExampleSerialization:
    """Test Example serialization to dict/JSON."""

    def test_example_to_dict(self):
        """Should serialize example to dictionary."""
        example = Example(
            title="Role configuration",
            code="my_role_var: production",
            description="Production environment settings",
            language="yaml",
        )

        result = example.model_dump()

        assert result["title"] == "Role configuration"
        assert result["code"] == "my_role_var: production"
        assert result["description"] == "Production environment settings"
        assert result["language"] == "yaml"

    def test_example_to_json(self):
        """Should serialize example to JSON string."""
        example = Example(
            title="Test example",
            code="test: value",
        )

        json_str = example.model_dump_json()

        assert "Test example" in json_str
        assert "test: value" in json_str

    def test_example_with_multiline_code(self):
        """Should preserve multiline code blocks."""
        code = """- name: Install packages
  apt:
    name: nginx
    state: present"""

        example = Example(title="Install", code=code)

        assert "\n" in example.code
        assert "Install packages" in example.code


class TestExampleRepresentation:
    """Test Example string representation."""

    def test_example_repr(self):
        """Should provide useful string representation."""
        example = Example(title="Test", code="code")

        repr_str = repr(example)

        assert "Example" in repr_str
        assert "Test" in repr_str

    def test_example_str(self):
        """Should provide readable string format."""
        example = Example(
            title="Basic playbook",
            code="- hosts: all",
            language="yaml",
        )

        str_result = str(example)

        assert "Basic playbook" in str_result


class TestExampleCodeFormatting:
    """Test Example code handling and formatting."""

    def test_preserves_code_indentation(self):
        """Should preserve code indentation exactly."""
        code = "  - name: Task\n    debug:\n      msg: test"
        example = Example(title="Test", code=code)

        assert example.code == code

    def test_preserves_trailing_whitespace_in_code(self):
        """Should preserve code exactly as provided (including trailing spaces)."""
        example = Example(title="Test", code="key: value   \n   ")

        # Code is preserved as-is for formatting fidelity
        assert example.code == "key: value   \n   "

    def test_handles_empty_lines_in_code(self):
        """Should preserve empty lines in code blocks."""
        code = "line1\n\nline3"
        example = Example(title="Test", code=code)

        assert "\n\n" in example.code
