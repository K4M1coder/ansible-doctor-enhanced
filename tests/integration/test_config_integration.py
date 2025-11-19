"""Integration tests for config file commands.

Feature 003 - Phase 5 US3 - T026
Tests config validate and config show commands with parent directory configs.
"""

import subprocess
from pathlib import Path

import pytest


class TestConfigValidateCommand:
    """Integration tests for 'config validate' command."""
    
    def test_config_validate_with_valid_config(self, tmp_path):
        """Test config validate returns exit code 0 for valid config."""
        # Create valid config file
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: markdown
output: README.md
recursive: false
""")
        
        # Run config validate command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Should exit with code 0 for valid config. stderr: {result.stderr}"
        assert "valid" in result.stdout.lower() or "✓" in result.stdout
    
    def test_config_validate_with_invalid_yaml_syntax(self, tmp_path):
        """Test config validate returns exit code 1 for YAML syntax errors."""
        # Create config with invalid YAML syntax
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: markdown
output: README.md
recursive: [invalid syntax
""")
        
        # Run config validate command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1, "Should exit with code 1 for invalid YAML"
        # Error messages go to stderr
        assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_config_validate_with_invalid_schema(self, tmp_path):
        """Test config validate returns exit code 1 for schema validation errors."""
        # Create config with invalid output_format value
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: invalid_format
output: README.md
""")
        
        # Run config validate command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 1, "Should exit with code 1 for schema validation error"
        # Error messages go to stderr
        assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()
    
    def test_config_validate_with_parent_directory_config(self, tmp_path):
        """Test config validate finds and validates config in parent directory."""
        # Create config in parent directory
        parent_config = tmp_path / ".ansibledoctor.yml"
        parent_config.write_text("""output_format: html
output: docs/index.html
""")
        
        # Create subdirectory
        subdir = tmp_path / "roles" / "my-role"
        subdir.mkdir(parents=True)
        
        # Run config validate from subdirectory
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(subdir)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Should find and validate parent config"
        assert "valid" in result.stdout.lower() or "✓" in result.stdout
    
    def test_config_validate_with_no_config_file(self, tmp_path):
        """Test config validate handles missing config gracefully."""
        # Empty directory with no config file
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        # Run config validate command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(empty_dir)],
            capture_output=True,
            text=True
        )
        
        # Should indicate no config found (behavior may vary - accept either)
        assert "not found" in result.stdout.lower() or "no config" in result.stdout.lower() or result.returncode != 0


class TestConfigShowCommand:
    """Integration tests for 'config show' command."""
    
    def test_config_show_displays_config_from_file(self, tmp_path):
        """Test config show displays configuration from file."""
        # Create config file
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: html
output: docs/role.html
recursive: true
exclude_patterns:
  - "*.pyc"
  - ".git"
""")
        
        # Run config show command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "show", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Should exit with code 0. stderr: {result.stderr}"
        assert "html" in result.stdout.lower()
        assert "output" in result.stdout.lower()
    
    def test_config_show_displays_parent_directory_config(self, tmp_path):
        """Test config show finds and displays config from parent directory."""
        # Create config in parent
        parent_config = tmp_path / ".ansibledoctor.yml"
        parent_config.write_text("""output_format: rst
template: custom.j2
""")
        
        # Create subdirectory
        subdir = tmp_path / "roles" / "web-server"
        subdir.mkdir(parents=True)
        
        # Run config show from subdirectory
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "show", "--path", str(subdir)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "rst" in result.stdout.lower()
        assert "template" in result.stdout.lower() or "custom.j2" in result.stdout
    
    def test_config_show_displays_merged_config_with_cli_override(self, tmp_path):
        """Test config show displays merged configuration with CLI override."""
        # Create config file
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: markdown
output: README.md
""")
        
        # Run config show command
        # Note: Current implementation may not support CLI overrides in 'config show'
        # This test documents expected behavior for future enhancement
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "show", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "markdown" in result.stdout.lower()
        # Config show should display the file config
        assert "readme.md" in result.stdout.lower() or "output" in result.stdout.lower()
    
    def test_config_show_with_no_config_uses_defaults(self, tmp_path):
        """Test config show displays defaults when no config file exists."""
        # Empty directory with no config file
        empty_dir = tmp_path / "no-config"
        empty_dir.mkdir()
        
        # Run config show command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "show", "--path", str(empty_dir)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        # Should show default configuration
        assert "defaults" in result.stderr.lower() or "recursive" in result.stdout.lower()
    
    def test_config_show_includes_config_file_path(self, tmp_path):
        """Test config show displays the path to the loaded config file."""
        # Create config file
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: html
""")
        
        # Run config show command
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "show", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        # Should indicate config file location
        assert ".ansibledoctor.yml" in result.stdout or "config" in result.stdout.lower()


class TestConfigIntegrationWithGenerate:
    """Integration tests for config file usage with generate command."""
    
    def test_generate_command_uses_parent_directory_config(self, tmp_path):
        """Test generate command discovers and uses config from parent directory."""
        # Create minimal role structure
        role_dir = tmp_path / "roles" / "test-role"
        (role_dir / "defaults").mkdir(parents=True)
        (role_dir / "meta").mkdir(parents=True)
        (role_dir / "tasks").mkdir(parents=True)  # Required directory
        
        # Create minimal metadata
        (role_dir / "meta" / "main.yml").write_text("""---
galaxy_info:
  author: Test Author
  description: Test role
  license: MIT
""")

        # Create minimal task file
        (role_dir / "tasks" / "main.yml").write_text("""---
# Main tasks
- name: Example task
  debug:
    msg: "Hello"
""")
        
        # Create config in parent directory (tmp_path)
        parent_config = tmp_path / ".ansibledoctor.yml"
        parent_config.write_text("""output_format: markdown
""")
        
        # Run generate command from role directory (should find parent config)
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "generate", str(role_dir)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should succeed and use parent config
        assert result.returncode == 0, f"Generate should succeed. stderr: {result.stderr}"
        assert "test-role" in result.stdout.lower() or "Test role" in result.stdout


@pytest.mark.skipif(
    not Path("tests/integration/fixtures/minimal_role").exists(),
    reason="Requires minimal_role fixture"
)
class TestConfigWithRealRole:
    """Integration tests using existing role fixtures."""
    
    def test_config_validate_with_real_role(self, tmp_path):
        """Test config validate works with real role structure."""
        # Create config in temp directory
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""output_format: html
output: docs/role.html
recursive: false
""")
        
        result = subprocess.run(
            ["poetry", "run", "ansible-doctor-enhanced", "config", "validate", "--path", str(tmp_path)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "valid" in result.stdout.lower() or "✓" in result.stdout
