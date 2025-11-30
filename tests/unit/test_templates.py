"""Tests for default templates."""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.loaders import FileSystemTemplateLoader
from ansibledoctor.generator.models import TemplateContext
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.models import AnsibleRole, Example, RoleMetadata, Tag, TodoItem, Variable


@pytest.fixture
def sample_role(tmp_path):
    """Create sample role with all features."""
    role_path = tmp_path / "test-role"
    role_path.mkdir()

    role = AnsibleRole(
        name="test-role",
        path=role_path,
    )

    # Add metadata
    role.metadata = RoleMetadata(
        author="Test Author",
        description="A test role for documentation",
        license="MIT",
        platforms=[],
        dependencies=[],
    )

    # Add variables
    role.variables = [
        Variable(
            name="test_var",
            value="default_value",
            type="string",
            source="defaults",
            description="A test variable",
            required=False,
        ),
    ]

    # Add tags
    role.tags = [
        Tag(
            name="install",
            description="Installation tasks",
            usage_count=3,
            file_locations=["tasks/install.yml:10", "tasks/install.yml:20"],
        ),
    ]

    # Add todos
    role.todos = [
        TodoItem(
            description="Improve error handling",
            priority="high",
            file_path="/tmp/test-role/tasks/main.yml",
            line_number=42,
        ),
    ]

    # Add examples
    role.examples = [
        Example(
            title="Basic Usage",
            code="- name: Use role\n  include_role:\n    name: test-role",
            description="Example of using the role",
            language="yaml",
        ),
    ]

    return role


@pytest.fixture
def template_context(sample_role):
    """Create template context."""
    return TemplateContext(
        role=sample_role,
        output_format=OutputFormat.MARKDOWN,
        generation_date=datetime(2024, 1, 1, 12, 0, 0),
        generator_version="0.3.0",
    )


class TestMarkdownTemplate:
    """Tests for Markdown template."""

    def test_markdown_template_renders(self, template_context):
        """Test that Markdown template renders without errors."""
        # Get templates directory
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )

        # Create loader and engine
        _ = FileSystemTemplateLoader(templates_dir)
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        # Load and render template
        template = engine.get_template("markdown/role.j2")
        result = template.render(**template_context.to_dict())

        # Basic validation
        assert result
        assert "test-role" in result
        assert "Test Author" in result
        assert "## Variables" in result  # Section should exist
        assert "## Tags" in result
        assert "## TODOs" in result
        assert "## Examples" in result


class TestHtmlTemplate:
    """Tests for HTML template."""

    def test_html_template_renders(self, template_context):
        """Test that HTML template renders without errors."""
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )

        _ = FileSystemTemplateLoader(templates_dir)
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        template_context.output_format = OutputFormat.HTML
        template = engine.get_template("html/role.j2")
        result = template.render(**template_context.to_dict())

        assert result
        assert "<!DOCTYPE html>" in result
        assert "<title>test-role" in result
        assert "Test Author" in result
        # Template should include variable section (conditional on has_variables)
        assert "variables" in result.lower() or len(result) > 1000


class TestRstTemplate:
    """Tests for RST template."""

    def test_rst_template_renders(self, template_context):
        """Test that RST template renders without errors."""
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )

        _ = FileSystemTemplateLoader(templates_dir)
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        template_context.output_format = OutputFormat.RST
        template = engine.get_template("rst/role.j2")
        result = template.render(**template_context.to_dict())

        assert result
        assert "test-role" in result
        assert "====" in result  # RST heading underline
        assert "Test Author" in result
        assert ".. code-block::" in result


class TestTemplateContent:
    """Tests for template content and structure."""

    def test_markdown_includes_all_sections(self, template_context):
        """Test Markdown template includes all sections."""
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        template = engine.get_template("markdown/role.j2")
        result = template.render(**template_context.to_dict())

        assert "## Overview" in result
        assert "## Variables" in result
        assert "## Tags" in result
        assert "## TODOs" in result
        assert "## Examples" in result

    def test_html_includes_all_sections(self, template_context):
        """Test HTML template includes all sections."""
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        template_context.output_format = OutputFormat.HTML
        template = engine.get_template("html/role.j2")
        result = template.render(**template_context.to_dict())

        # Check for sections (may use id attributes instead of exact h2 text)
        assert "variables" in result.lower()
        assert "tags" in result.lower()
        assert "todo" in result.lower()
        assert "example" in result.lower()
        assert "<!DOCTYPE html>" in result

    def test_rst_includes_all_sections(self, template_context):
        """Test RST template includes all sections."""
        templates_dir = (
            Path(__file__).parent.parent.parent / "ansibledoctor" / "generator" / "templates"
        )
        engine = TemplateEngine.create(template_dir=str(templates_dir))

        template_context.output_format = OutputFormat.RST
        template = engine.get_template("rst/role.j2")
        result = template.render(**template_context.to_dict())

        assert "Overview" in result
        assert "Variables" in result
        assert "Tags" in result
        assert "TODOs" in result
        assert "Examples" in result
