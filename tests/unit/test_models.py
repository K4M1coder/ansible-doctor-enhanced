"""Tests for generator data models."""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor import __version__
from ansibledoctor.generator.models import RenderResult, TemplateContext
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.role import AnsibleRole


class TestRenderResult:
    """Test suite for RenderResult dataclass."""

    def test_render_result_creation(self):
        """Test basic RenderResult creation."""
        result = RenderResult(
            content="# Test\n\nContent",
            output_format=OutputFormat.MARKDOWN,
            source_file="/path/to/role",
        )

        assert result.content == "# Test\n\nContent"
        assert result.output_format == OutputFormat.MARKDOWN
        assert result.source_file == "/path/to/role"
        assert isinstance(result.rendered_at, datetime)
        assert result.template_name == "default"

    def test_render_result_with_template_name(self):
        """Test RenderResult with custom template name."""
        result = RenderResult(
            content="content",
            output_format=OutputFormat.HTML,
            source_file="/path",
            template_name="custom.html.j2",
        )

        assert result.template_name == "custom.html.j2"

    def test_render_result_file_extension(self):
        """Test file_extension property."""
        result_md = RenderResult(content="", output_format=OutputFormat.MARKDOWN, source_file="/")
        assert result_md.file_extension == ".md"

        result_html = RenderResult(content="", output_format=OutputFormat.HTML, source_file="/")
        assert result_html.file_extension == ".html"

        result_rst = RenderResult(content="", output_format=OutputFormat.RST, source_file="/")
        assert result_rst.file_extension == ".rst"

    def test_render_result_size_bytes(self):
        """Test size_bytes property."""
        result = RenderResult(
            content="Hello World",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
        )

        assert result.size_bytes == len("Hello World".encode("utf-8"))

    def test_render_result_size_bytes_unicode(self):
        """Test size_bytes with Unicode characters."""
        result = RenderResult(
            content="Hello 世界 🎉",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
        )

        assert result.size_bytes == len("Hello 世界 🎉".encode("utf-8"))
        assert result.size_bytes > len("Hello 世界 🎉")  # UTF-8 is multi-byte

    def test_render_result_line_count(self):
        """Test line_count property."""
        result = RenderResult(
            content="Line 1\nLine 2\nLine 3",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
        )

        assert result.line_count == 3

    def test_render_result_line_count_empty(self):
        """Test line_count with empty content."""
        result = RenderResult(
            content="",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
        )

        assert result.line_count == 0

    def test_render_result_metadata(self):
        """Test metadata dictionary."""
        metadata = {"author": "test", "version": "1.0"}
        result = RenderResult(
            content="content",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
            metadata=metadata,
        )

        assert result.metadata == metadata
        assert result.metadata["author"] == "test"

    def test_render_result_save_to_file(self, tmp_path):
        """Test saving render result to file."""
        output_file = tmp_path / "output.md"
        result = RenderResult(
            content="# Test\n\nContent",
            output_format=OutputFormat.MARKDOWN,
            source_file="/",
        )

        result.save_to_file(str(output_file))

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == "# Test\n\nContent"


class TestTemplateContext:
    """Test suite for TemplateContext dataclass."""

    @pytest.fixture
    def sample_role(self):
        """Create sample AnsibleRole for testing."""

        from ansibledoctor.models.example import Example
        from ansibledoctor.models.tag import Tag
        from ansibledoctor.models.todo import TodoItem
        from ansibledoctor.models.variable import Variable, VariableType

        metadata = RoleMetadata(
            description="A test role",
            author="Test Author",
        )

        variables = [
            Variable(
                name="var1",
                value="value1",
                type=VariableType.STRING,
                source="defaults",
                description="Variable 1",
            ),
            Variable(
                name="var2",
                value="value2",
                type=VariableType.STRING,
                source="defaults",
                description="Variable 2",
            ),
        ]

        tags = [
            Tag(name="install", description="Installation tasks"),
            Tag(name="configure", description="Configuration tasks"),
        ]

        todos = [
            TodoItem(description="Fix bug", file_path="tasks/main.yml", line_number=10),
        ]

        examples = [
            Example(title="Example 1", code="- hosts: all", description="Basic usage"),
        ]

        return AnsibleRole(
            path=Path("C:/ansible/roles/test-role").resolve(),
            name="test-role",
            metadata=metadata,
            variables=variables,
            tags=tags,
            todos=todos,
            examples=examples,
        )

    def test_template_context_creation(self, sample_role):
        """Test basic TemplateContext creation."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.role == sample_role
        assert context.output_format == OutputFormat.MARKDOWN
        assert isinstance(context.generation_date, datetime)
        assert context.generator_version == __version__

    def test_template_context_role_name(self, sample_role):
        """Test role_name property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.role_name == "test-role"

    def test_template_context_role_description(self, sample_role):
        """Test role_description property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.role_description == "A test role"

    def test_template_context_has_variables(self, sample_role):
        """Test has_variables property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.has_variables is True
        assert context.variable_count == 2

    def test_template_context_has_tags(self, sample_role):
        """Test has_tags property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.has_tags is True
        assert context.tag_count == 2

    def test_template_context_has_todos(self, sample_role):
        """Test has_todos property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.has_todos is True
        assert context.todo_count == 1

    def test_template_context_has_examples(self, sample_role):
        """Test has_examples property."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        assert context.has_examples is True
        assert context.example_count == 1

    def test_template_context_format_name(self, sample_role):
        """Test format_name property."""
        context_md = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )
        assert context_md.format_name == "Markdown"

        context_html = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version=__version__,
        )
        assert context_html.format_name == "HTML"

        context_rst = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.RST,
            generator_version=__version__,
        )
        assert context_rst.format_name == "reStructuredText"

    def test_template_context_to_dict(self, sample_role):
        """Test to_dict conversion."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
        )

        context_dict = context.to_dict()

        assert isinstance(context_dict, dict)
        assert context_dict["role"] == sample_role
        assert context_dict["role_name"] == "test-role"
        assert context_dict["role_description"] == "A test role"
        assert context_dict["output_format"] == OutputFormat.MARKDOWN
        assert context_dict["format_name"] == "Markdown"
        assert context_dict["has_variables"] is True
        assert context_dict["variable_count"] == 2
        assert context_dict["has_tags"] is True
        assert context_dict["tag_count"] == 2
        assert context_dict["has_todos"] is True
        assert context_dict["todo_count"] == 1
        assert context_dict["has_examples"] is True
        assert context_dict["example_count"] == 1

    def test_template_context_custom_data(self, sample_role):
        """Test custom_data dictionary."""
        custom_data = {"theme": "dark", "lang": "en"}
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version=__version__,
            custom_data=custom_data,
        )

        assert context.custom_data == custom_data
        context_dict = context.to_dict()
        assert context_dict["custom_data"] == custom_data
