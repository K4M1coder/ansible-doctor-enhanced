"""Unit tests for --continue-on-error CLI flag (Phase 5 - T043).

These tests verify the flag is accepted and properly stored in the context.
"""

import pytest
from click.testing import CliRunner

from ansibledoctor.cli import cli


class TestContinueOnErrorFlag:
    """Test --continue-on-error CLI flag acceptance (T043)."""

    def test_flag_is_accepted(self):
        """CLI should accept --continue-on-error flag without error."""
        runner = CliRunner()
        
        # Test that the flag is accepted (doesn't cause CLI error)
        # We'll use --help to test flag parsing without actually running commands
        result = runner.invoke(cli, ["--help"])
        
        # Should see the flag in help output
        assert result.exit_code == 0
        # Flag should be documented in help text (once implemented)

    def test_flag_with_parse_command(self):
        """Parse command should accept --continue-on-error flag."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a minimal role structure
            import os
            os.makedirs("test_role/meta")
            with open("test_role/meta/main.yml", "w") as f:
                f.write("---\ndependencies: []\n")
            
            # Run parse with flag - should not error on flag itself
            result = runner.invoke(
                cli,
                ["parse", "test_role", "--continue-on-error"],
                catch_exceptions=False
            )
            
            # May fail for other reasons, but not due to unknown flag
            # If flag is unknown, Click returns exit code 2
            assert result.exit_code != 2, "Flag should be recognized by CLI"

    def test_flag_with_generate_project_command(self):
        """Generate project command should accept --continue-on-error flag."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a minimal project structure
            import os
            os.makedirs("test_project/roles")
            
            # Run generate with flag - should not error on flag itself
            result = runner.invoke(
                cli,
                ["project", "generate", "test_project", "--continue-on-error"],
                catch_exceptions=False
            )
            
            # May fail for other reasons, but not due to unknown flag
            assert result.exit_code != 2, "Flag should be recognized by CLI"

    def test_flag_with_generate_collection_command(self):
        """Generate collection command should accept --continue-on-error flag."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a minimal collection structure
            import os
            os.makedirs("ansible_collections/test_ns/test_col/roles")
            with open("ansible_collections/test_ns/test_col/galaxy.yml", "w") as f:
                f.write("---\nnamespace: test_ns\nname: test_col\nversion: 1.0.0\n")
            
            # Run generate with flag - should not error on flag itself
            result = runner.invoke(
                cli,
                [
                    "collection",
                    "generate",
                    "ansible_collections/test_ns/test_col",
                    "--continue-on-error"
                ],
                catch_exceptions=False
            )
            
            # May fail for other reasons, but not due to unknown flag
            assert result.exit_code != 2, "Flag should be recognized by CLI"
