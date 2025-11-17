"""Tests for generator exceptions."""
import pytest
from ansibledoctor.generator.errors import (
    GeneratorError,
    RenderError,
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
)


class TestGeneratorExceptions:
    """Test suite for generator exception hierarchy."""

    def test_generator_error_is_base(self):
        """Test that GeneratorError is the base exception."""
        error = GeneratorError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_template_error_inherits_from_generator_error(self):
        """Test TemplateError inheritance."""
        error = TemplateError("template error")
        assert isinstance(error, GeneratorError)
        assert isinstance(error, Exception)

    def test_render_error_inherits_from_generator_error(self):
        """Test RenderError inheritance."""
        error = RenderError("render error")
        assert isinstance(error, GeneratorError)

    def test_template_not_found_error_basic(self):
        """Test TemplateNotFoundError with just template name."""
        error = TemplateNotFoundError("role.md.j2")
        assert isinstance(error, TemplateError)
        assert error.template_name == "role.md.j2"
        assert error.search_paths == []
        assert "Template not found: 'role.md.j2'" in str(error)

    def test_template_not_found_error_with_paths(self):
        """Test TemplateNotFoundError with search paths."""
        paths = ["/custom/templates", "/project/templates", "/embedded/templates"]
        error = TemplateNotFoundError("role.md.j2", paths)
        assert error.template_name == "role.md.j2"
        assert error.search_paths == paths
        assert "Template not found: 'role.md.j2'" in str(error)
        assert "Searched in:" in str(error)
        assert "/custom/templates" in str(error)

    def test_template_validation_error(self):
        """Test TemplateValidationError with details."""
        error = TemplateValidationError(
            "role.md.j2",
            "Syntax error at line 42: unexpected end of statement"
        )
        assert isinstance(error, TemplateError)
        assert error.template_name == "role.md.j2"
        assert "unexpected end of statement" in error.error_details
        assert "Template validation failed" in str(error)
        assert "role.md.j2" in str(error)
        assert "line 42" in str(error)

    def test_render_error_without_context(self):
        """Test RenderError without context data."""
        error = RenderError("Variable 'role_name' is undefined")
        assert isinstance(error, GeneratorError)
        assert error.context == {}
        assert "Rendering failed" in str(error)
        assert "role_name" in str(error)

    def test_render_error_with_context(self):
        """Test RenderError with context data."""
        context = {"role_name": "my-role", "variables": []}
        error = RenderError("Template rendering failed", context)
        assert error.context == context
        assert "Rendering failed" in str(error)
        assert "Context keys:" in str(error)
        assert "role_name" in str(error)
        assert "variables" in str(error)

    def test_exception_can_be_caught_as_generator_error(self):
        """Test that all exceptions can be caught as GeneratorError."""
        exceptions = [
            GeneratorError("test"),
            TemplateError("test"),
            TemplateNotFoundError("test.j2"),
            TemplateValidationError("test.j2", "error"),
            RenderError("test"),
        ]
        
        for exc in exceptions:
            with pytest.raises(GeneratorError):
                raise exc

    def test_exception_can_be_caught_as_template_error(self):
        """Test that template exceptions can be caught as TemplateError."""
        exceptions = [
            TemplateError("test"),
            TemplateNotFoundError("test.j2"),
            TemplateValidationError("test.j2", "error"),
        ]
        
        for exc in exceptions:
            with pytest.raises(TemplateError):
                raise exc
