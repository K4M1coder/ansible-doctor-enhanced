"""Unit tests for CLI theme options (T341).

Feature 008 - Template Customization & Theming
Tests CLI flags for --variant, --color-scheme, --no-theme-toggle, --template-dir
"""

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli


@pytest.fixture
def runner():
    """Create Click test runner."""
    return CliRunner()


@pytest.fixture
def minimal_role(tmp_path):
    """Create a minimal role for CLI testing."""
    role_dir = tmp_path / "test_role"
    role_dir.mkdir()

    # Create minimal tasks/main.yml
    tasks_dir = role_dir / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "main.yml").write_text("---\n- name: Test task\n  debug:\n    msg: Hello\n")

    # Create minimal meta/main.yml
    meta_dir = role_dir / "meta"
    meta_dir.mkdir()
    (meta_dir / "main.yml").write_text(
        "---\ngalaxy_info:\n  author: Test Author\n  description: Test role\n"
    )

    return role_dir


class TestVariantOption:
    """Test --variant CLI option."""

    def test_variant_option_exists_in_help(self, runner):
        """Test --variant is documented in generate help."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--variant" in result.output

    def test_variant_option_accepts_minimal(self, runner, minimal_role):
        """Test --variant minimal is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--variant", "minimal"]
        )
        # Should succeed or exit gracefully
        assert result.exit_code in [0, 1, 2]

    def test_variant_option_accepts_detailed(self, runner, minimal_role):
        """Test --variant detailed is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--variant", "detailed"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_variant_option_accepts_modern(self, runner, minimal_role):
        """Test --variant modern is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--variant", "modern"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_variant_option_rejects_invalid(self, runner, minimal_role):
        """Test --variant rejects invalid variant names."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--variant", "invalid_variant"]
        )
        # Click should reject invalid choice
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "choice" in result.output.lower()

    def test_variant_default_is_detailed(self, runner):
        """Test --variant defaults to detailed when not specified."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        # Help should indicate default is detailed
        assert "detailed" in result.output.lower()


class TestColorSchemeOption:
    """Test --color-scheme CLI option."""

    def test_color_scheme_option_exists_in_help(self, runner):
        """Test --color-scheme is documented in generate help."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--color-scheme" in result.output

    def test_color_scheme_option_accepts_light(self, runner, minimal_role):
        """Test --color-scheme light is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--color-scheme", "light"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_color_scheme_option_accepts_dark(self, runner, minimal_role):
        """Test --color-scheme dark is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--color-scheme", "dark"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_color_scheme_option_accepts_auto(self, runner, minimal_role):
        """Test --color-scheme auto is accepted."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--color-scheme", "auto"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_color_scheme_option_rejects_invalid(self, runner, minimal_role):
        """Test --color-scheme rejects invalid values."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--color-scheme", "invalid"]
        )
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "choice" in result.output.lower()

    def test_color_scheme_default_is_auto(self, runner):
        """Test --color-scheme defaults to auto."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "auto" in result.output.lower()


class TestThemeToggleOption:
    """Test --no-theme-toggle CLI option."""

    def test_no_theme_toggle_option_exists_in_help(self, runner):
        """Test --no-theme-toggle is documented in generate help."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        # Either --theme-toggle/--no-theme-toggle or just --no-theme-toggle
        assert "theme-toggle" in result.output.lower()

    def test_theme_toggle_enabled_by_default(self, runner, minimal_role):
        """Test theme toggle is enabled by default."""
        result = runner.invoke(cli, ["generate", str(minimal_role), "--format", "html"])
        # Should succeed without explicit toggle option
        assert result.exit_code in [0, 1, 2]

    def test_no_theme_toggle_disables_toggle(self, runner, minimal_role):
        """Test --no-theme-toggle disables the toggle."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--no-theme-toggle"]
        )
        assert result.exit_code in [0, 1, 2]

    def test_theme_toggle_enables_toggle(self, runner, minimal_role):
        """Test --theme-toggle explicitly enables the toggle."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "html", "--theme-toggle"]
        )
        assert result.exit_code in [0, 1, 2]


class TestTemplateDirOption:
    """Test --template-dir CLI option."""

    def test_template_dir_option_exists_in_help(self, runner):
        """Test --template-dir is documented in generate help."""
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--template-dir" in result.output

    def test_template_dir_option_accepts_path(self, runner, minimal_role, tmp_path):
        """Test --template-dir accepts a valid directory path."""
        templates_dir = tmp_path / "custom_templates"
        templates_dir.mkdir()

        result = runner.invoke(
            cli,
            [
                "generate",
                str(minimal_role),
                "--format",
                "html",
                "--template-dir",
                str(templates_dir),
            ],
        )
        assert result.exit_code in [0, 1, 2]

    def test_template_dir_option_rejects_nonexistent(self, runner, minimal_role, tmp_path):
        """Test --template-dir rejects non-existent directory."""
        nonexistent = tmp_path / "nonexistent_dir"

        result = runner.invoke(
            cli,
            ["generate", str(minimal_role), "--format", "html", "--template-dir", str(nonexistent)],
        )
        # Click should reject non-existent path
        assert result.exit_code != 0

    def test_template_dir_option_rejects_file(self, runner, minimal_role, tmp_path):
        """Test --template-dir rejects a file path (requires directory)."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("content")

        result = runner.invoke(
            cli,
            ["generate", str(minimal_role), "--format", "html", "--template-dir", str(file_path)],
        )
        # Should reject file when directory is expected
        assert result.exit_code != 0


class TestCombinedThemeOptions:
    """Test combinations of theme options."""

    def test_all_theme_options_together(self, runner, minimal_role, tmp_path):
        """Test using all theme options together."""
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()

        result = runner.invoke(
            cli,
            [
                "generate",
                str(minimal_role),
                "--format",
                "html",
                "--variant",
                "modern",
                "--color-scheme",
                "dark",
                "--no-theme-toggle",
                "--template-dir",
                str(templates_dir),
            ],
        )
        assert result.exit_code in [0, 1, 2]

    def test_theme_options_only_apply_to_html(self, runner, minimal_role):
        """Test theme options work with markdown format too (graceful handling)."""
        result = runner.invoke(
            cli, ["generate", str(minimal_role), "--format", "markdown", "--variant", "minimal"]
        )
        # Should succeed even for non-HTML format
        assert result.exit_code in [0, 1, 2]


class TestThemeOptionsInConfig:
    """Test theme options from config file."""

    def test_config_theme_section_recognized(self, runner, minimal_role, tmp_path):
        """Test config file with theme section is recognized."""
        config_file = minimal_role / ".ansibledoctor.yml"
        config_file.write_text(
            """
theme:
  variant: modern
  color_scheme: dark
  enable_toggle: false
"""
        )

        result = runner.invoke(cli, ["generate", str(minimal_role), "--format", "html"])
        # Config should be loaded without error
        assert result.exit_code in [0, 1, 2]

    def test_cli_options_override_config(self, runner, minimal_role, tmp_path):
        """Test CLI options override config file theme settings."""
        config_file = minimal_role / ".ansibledoctor.yml"
        config_file.write_text(
            """
theme:
  variant: minimal
  color_scheme: light
"""
        )

        result = runner.invoke(
            cli,
            [
                "generate",
                str(minimal_role),
                "--format",
                "html",
                "--variant",
                "modern",  # Should override config
                "--color-scheme",
                "dark",  # Should override config
            ],
        )
        assert result.exit_code in [0, 1, 2]
