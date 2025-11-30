"""Tests for template validator."""

import pytest
from jinja2 import Environment

from ansibledoctor.generator.errors import TemplateValidationError
from ansibledoctor.generator.validator import TemplateValidator


@pytest.fixture
def validator():
    """Create template validator."""
    env = Environment()
    return TemplateValidator(env)


class TestTemplateSyntaxValidation:
    """Tests for template syntax validation."""

    def test_validate_valid_template(self, validator):
        """Test validating valid template."""
        template = "Hello {{ name }}!"

        # Should not raise
        validator.validate_syntax(template)

    def test_validate_invalid_syntax(self, validator):
        """Test validating template with syntax error."""
        template = "Hello {{ name }!"  # Missing closing brace

        with pytest.raises(TemplateValidationError) as exc_info:
            validator.validate_syntax(template, "test.j2")

        assert "Syntax error" in str(exc_info.value)
        assert "test.j2" in str(exc_info.value)

    def test_validate_complex_template(self, validator):
        """Test validating complex template with loops and conditionals."""
        template = """
        {% for item in items %}
            {% if item.active %}
                {{ item.name }}
            {% endif %}
        {% endfor %}
        """

        validator.validate_syntax(template)

    def test_validate_unclosed_block(self, validator):
        """Test validating template with unclosed block."""
        template = "{% for item in items %}{{ item }}"  # Missing endfor

        with pytest.raises(TemplateValidationError):
            validator.validate_syntax(template)


class TestTemplateFileValidation:
    """Tests for template file validation."""

    def test_validate_existing_file(self, validator, tmp_path):
        """Test validating existing template file."""
        template_file = tmp_path / "test.j2"
        template_file.write_text("Hello {{ name }}!")

        validator.validate_file(template_file)

    def test_validate_nonexistent_file(self, validator):
        """Test validating non-existent file."""
        with pytest.raises(TemplateValidationError, match="not found"):
            validator.validate_file("/nonexistent/template.j2")

    def test_validate_directory_not_file(self, validator, tmp_path):
        """Test validating directory instead of file."""
        with pytest.raises(TemplateValidationError, match="Not a file"):
            validator.validate_file(tmp_path)

    def test_validate_file_with_syntax_error(self, validator, tmp_path):
        """Test validating file with syntax error."""
        template_file = tmp_path / "bad.j2"
        template_file.write_text("{{ unclosed")

        with pytest.raises(TemplateValidationError, match="Syntax error"):
            validator.validate_file(template_file)


class TestVariableDetection:
    """Tests for variable detection."""

    def test_get_undeclared_variables_simple(self, validator):
        """Test getting variables from simple template."""
        template = "Hello {{ name }}!"

        variables = validator.get_undeclared_variables(template)

        assert variables == {"name"}

    def test_get_undeclared_variables_multiple(self, validator):
        """Test getting multiple variables."""
        template = "{{ greeting }} {{ name }}, you have {{ count }} messages."

        variables = validator.get_undeclared_variables(template)

        assert variables == {"greeting", "name", "count"}

    def test_get_undeclared_variables_in_loops(self, validator):
        """Test variables in loops are not undeclared."""
        template = "{% for item in items %}{{ item }}{% endfor %}"

        variables = validator.get_undeclared_variables(template)

        assert "item" not in variables
        assert "items" in variables

    def test_get_undeclared_variables_filters(self, validator):
        """Test variables used with filters."""
        template = "{{ name | upper }}"

        variables = validator.get_undeclared_variables(template)

        assert variables == {"name"}

    def test_get_undeclared_variables_nested(self, validator):
        """Test nested variable access."""
        template = "{{ user.name }} - {{ user.email }}"

        variables = validator.get_undeclared_variables(template)

        assert variables == {"user"}


class TestRequiredVariablesValidation:
    """Tests for required variables validation."""

    def test_validate_all_required_present(self, validator):
        """Test validating when all required variables are present."""
        template = "{{ name }} - {{ email }}"
        required = {"name", "email"}

        # Should not raise
        validator.validate_required_variables(template, required)

    def test_validate_missing_required(self, validator):
        """Test validating when required variables are missing."""
        template = "{{ name }}"
        required = {"name", "email", "age"}

        with pytest.raises(TemplateValidationError) as exc_info:
            validator.validate_required_variables(template, required, "test.j2")

        assert "missing required variables" in str(exc_info.value).lower()
        assert "email" in str(exc_info.value)
        assert "age" in str(exc_info.value)

    def test_validate_extra_variables_ok(self, validator):
        """Test that extra variables don't cause errors."""
        template = "{{ name }} - {{ email }} - {{ age }}"
        required = {"name"}

        validator.validate_required_variables(template, required)


class TestUnusedVariableDetection:
    """Tests for unused variable detection."""

    def test_check_all_variables_used(self, validator):
        """Test when all context variables are used."""
        template = "{{ name }} - {{ email }}"
        context = {"name": "John", "email": "john@example.com"}

        unused = validator.check_variable_usage(template, context)

        assert unused == []

    def test_check_unused_variables(self, validator):
        """Test detecting unused context variables."""
        template = "{{ name }}"
        context = {"name": "John", "email": "john@example.com", "age": 30}

        unused = validator.check_variable_usage(template, context)

        assert set(unused) == {"email", "age"}

    def test_check_no_context_variables(self, validator):
        """Test with empty context."""
        template = "Hello world!"
        context = {}

        unused = validator.check_variable_usage(template, context)

        assert unused == []


class TestComprehensiveValidation:
    """Tests for comprehensive validation."""

    def test_validate_valid_template(self, validator):
        """Test comprehensive validation of valid template."""
        template = "Hello {{ name }}!"

        result = validator.validate_template(template)

        assert result["valid"] is True
        assert result["errors"] == []
        assert "name" in result["undeclared_variables"]

    def test_validate_invalid_template(self, validator):
        """Test comprehensive validation of invalid template."""
        template = "{{ unclosed"

        result = validator.validate_template(template, "test.j2")

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "Syntax error" in result["errors"][0]

    def test_validate_with_required_vars(self, validator):
        """Test validation with required variables."""
        template = "{{ name }}"
        required = {"name", "email"}

        result = validator.validate_template(template, required_vars=required)

        assert result["valid"] is False
        assert any("email" in error for error in result["errors"])

    def test_validate_complete_result_structure(self, validator):
        """Test validation result contains all expected keys."""
        template = "{{ name }}"

        result = validator.validate_template(template)

        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "undeclared_variables" in result
        assert isinstance(result["valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["undeclared_variables"], set)
