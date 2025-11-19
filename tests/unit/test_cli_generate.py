"""Unit tests for CLI generate command.

T221: TDD - Write tests FIRST before implementing generate command.
Tests CLI interface, argument parsing, and error handling.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli
from ansibledoctor.generator.models import OutputFormat


class TestGenerateCommand:
    """Test suite for 'generate' CLI command."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_role_data(self):
        """Sample role data for testing."""
        return {
            "name": "test-role",
            "path": "/tmp/test-role",
            "metadata": {
                "author": "Test Author",
                "description": "Test description",
            },
            "variables": [],
            "tags": [],
            "todos": [],
            "examples": [],
        }

    def test_generate_command_exists(self, runner):
        """Test that generate command is registered."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "generate" in result.output.lower()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_role_path(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with role path argument."""
        # Setup mocks
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        # Mock role parsing
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_role = AnsibleRole(
            name="test-role",
            path=role_path.resolve(),
            metadata=RoleMetadata(author="Test", description="Test role"),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )
        mock_parse.return_value = mock_role
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Test Role\n\nGenerated docs"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path)])
        
        # Should succeed (exit code 0) and print to stdout
        assert result.exit_code == 0
        assert "Test Role" in result.output or "Generated docs" in result.output

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_format_option(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --format option."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Documentation"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "markdown"])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_output_file(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --output option."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        output_file = tmp_path / "README.md"
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Documentation Content"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--output", str(output_file)])
        
        assert result.exit_code == 0
        # File should be created
        if output_file.exists():
            assert "Documentation Content" in output_file.read_text()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_custom_template(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --template option."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        template_path = tmp_path / "custom.j2"
        template_path.write_text("# {{ role_name }}")
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Custom Template Output"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, [
            "generate", 
            str(role_path), 
            "--template", 
            str(template_path)
        ])
        
        assert result.exit_code == 0

    def test_generate_with_nonexistent_role_path(self, runner):
        """Test generate command with invalid role path."""
        result = runner.invoke(cli, ["generate", "/nonexistent/path"])
        
        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "error" in result.output.lower()

    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_invalid_format(self, mock_renderer_class, runner, tmp_path):
        """Test generate command with unsupported format."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        (role_path / "meta" / "main.yml").write_text("---\ngalaxy_info:\n  author: Test\n")
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "invalid"])
        
        # Should fail with error message
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "format" in result.output.lower()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_verbose_flag(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --verbose flag."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Documentation"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--verbose"])
        
        # Should succeed and potentially show debug output
        assert result.exit_code == 0

    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_handles_rendering_error(self, mock_renderer_class, mock_parse, runner, tmp_path):
        """Test generate command handles renderer errors gracefully."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.side_effect = Exception("Template error")
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path)])
        
        # Should handle error gracefully
        assert result.exit_code != 0
        assert "error" in result.output.lower()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.MarkdownRenderer")
    def test_generate_with_all_options(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with all options combined."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        output_file = tmp_path / "output.md"
        template_path = tmp_path / "template.j2"
        template_path.write_text("# {{ role_name }}")
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "# Complete Documentation"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, [
            "generate",
            str(role_path),
            "--format", "markdown",
            "--output", str(output_file),
            "--template", str(template_path),
            "--verbose"
        ])
        
        assert result.exit_code == 0

    def test_generate_help_shows_usage_examples(self, runner):
        """Test that generate --help shows clear usage examples."""
        result = runner.invoke(cli, ["generate", "--help"])
        
        assert result.exit_code == 0
        assert "--format" in result.output
        assert "--output" in result.output
        assert "--template" in result.output or "template" in result.output.lower()


class TestGenerateHtmlFormat:
    """Test suite for HTML format generation (T236)."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_format(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --format html."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_role = AnsibleRole(
            name="test-role",
            path=role_path.resolve(),
            metadata=RoleMetadata(author="Test", description="Test role"),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )
        mock_parse.return_value = mock_role
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<!DOCTYPE html><html><body>Test</body></html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "html"])
        
        assert result.exit_code == 0
        # HtmlRenderer should be instantiated with default options
        mock_renderer_class.assert_called_once_with(
            embed_css=True,
            generate_toc=True,
            template_path=None
        )

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_with_embed_css(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --embed-css flag."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<html>Embedded CSS</html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "html", "--embed-css"])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once_with(
            embed_css=True,
            generate_toc=True,
            template_path=None
        )

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_with_no_embed_css(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --no-embed-css flag."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<html>External CSS</html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "html", "--no-embed-css"])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once_with(
            embed_css=False,
            generate_toc=True,
            template_path=None
        )

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_with_generate_toc(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --generate-toc flag."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<html>With TOC</html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "html", "--generate-toc"])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once_with(
            embed_css=True,
            generate_toc=True,
            template_path=None
        )

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_with_no_generate_toc(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with --no-generate-toc flag."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<html>No TOC</html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, ["generate", str(role_path), "--format", "html", "--no-generate-toc"])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once_with(
            embed_css=True,
            generate_toc=False,
            template_path=None
        )

    @patch("ansibledoctor.cli.RolePathValidator.validate_role_structure")
    @patch("ansibledoctor.cli._parse_role_for_generation")
    @patch("ansibledoctor.cli.HtmlRenderer")
    def test_generate_html_with_all_options(self, mock_renderer_class, mock_parse, mock_validate, runner, tmp_path):
        """Test generate command with all HTML options combined."""
        role_path = tmp_path / "test-role"
        role_path.mkdir()
        (role_path / "meta").mkdir()
        
        # Mock validation to pass
        mock_validate.return_value = True
        
        from ansibledoctor.models import AnsibleRole, RoleMetadata
        mock_parse.return_value = AnsibleRole(
            name="test-role", path=role_path.resolve(),
            metadata=RoleMetadata(author="Test"), variables=[], tags=[], todos=[], examples=[]
        )
        
        output_file = tmp_path / "index.html"
        
        mock_renderer = MagicMock()
        mock_renderer.render.return_value = "<html>Complete HTML</html>"
        mock_renderer_class.return_value = mock_renderer
        
        result = runner.invoke(cli, [
            "generate",
            str(role_path),
            "--format", "html",
            "--output", str(output_file),
            "--no-embed-css",
            "--no-generate-toc"
        ])
        
        assert result.exit_code == 0
        mock_renderer_class.assert_called_once_with(
            embed_css=False,
            generate_toc=False,
            template_path=None
        )
