"""Unit tests for configuration file loader.

Feature 003 - Phase 3 US1 - T007-T008
Tests config file discovery and loading BEFORE implementation (TDD RED).

Constitutional compliance:
- Article III: TDD - Tests written BEFORE implementation
- Article I: Library-first architecture
"""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from ansibledoctor.config.loader import find_config_file, load_config, merge_config
from ansibledoctor.config.models import ConfigModel


class TestConfigFileDiscovery:
    """Test suite for find_config_file() - TDD RED phase."""
    
    def test_find_config_file_in_current_dir_yml(self, tmp_path):
        """Test find_config_file() discovers .ansibledoctor.yml in current dir."""
        # Create config file in temp directory
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("output_format: html\n")
        
        # Should find config in current directory
        result = find_config_file(tmp_path)
        
        assert result is not None
        assert result == config_file
        assert result.name == ".ansibledoctor.yml"
    
    def test_find_config_file_in_current_dir_yaml(self, tmp_path):
        """Test find_config_file() discovers .ansibledoctor.yaml (alternate extension)."""
        # Create config file with .yaml extension
        config_file = tmp_path / ".ansibledoctor.yaml"
        config_file.write_text("output_format: markdown\n")
        
        result = find_config_file(tmp_path)
        
        assert result is not None
        assert result == config_file
        assert result.name == ".ansibledoctor.yaml"
    
    def test_find_config_file_prefers_yml_over_yaml(self, tmp_path):
        """Test .yml extension takes precedence over .yaml when both exist."""
        # Create both extensions
        yml_file = tmp_path / ".ansibledoctor.yml"
        yaml_file = tmp_path / ".ansibledoctor.yaml"
        yml_file.write_text("output_format: html\n")
        yaml_file.write_text("output_format: markdown\n")
        
        result = find_config_file(tmp_path)
        
        assert result is not None
        assert result.name == ".ansibledoctor.yml", "Should prefer .yml over .yaml"
    
    def test_find_config_file_in_parent_directory(self, tmp_path):
        """Test find_config_file() discovers config in parent directory."""
        # Create config in parent directory
        parent_config = tmp_path / ".ansibledoctor.yml"
        parent_config.write_text("output_format: rst\n")
        
        # Create subdirectory without config
        subdir = tmp_path / "roles" / "my-role"
        subdir.mkdir(parents=True)
        
        # Search from subdirectory should find parent config
        result = find_config_file(subdir)
        
        assert result is not None
        assert result == parent_config
    
    def test_find_config_file_nearest_wins(self, tmp_path):
        """Test nearest config wins (role dir over parent dir)."""
        # Create config in parent
        parent_config = tmp_path / ".ansibledoctor.yml"
        parent_config.write_text("output_format: html\n")
        
        # Create subdirectory with its own config
        subdir = tmp_path / "roles"
        subdir.mkdir()
        subdir_config = subdir / ".ansibledoctor.yml"
        subdir_config.write_text("output_format: markdown\n")
        
        # Search from subdirectory should find nearest (subdir) config
        result = find_config_file(subdir)
        
        assert result is not None
        assert result == subdir_config, "Nearest config should win"
    
    def test_find_config_file_returns_none_when_not_found(self, tmp_path):
        """Test find_config_file() returns None when no config exists."""
        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = find_config_file(empty_dir)
        
        assert result is None, "Should return None when no config found"
    
    def test_find_config_file_in_grandparent_directory(self, tmp_path):
        """Test find_config_file() discovers config in grandparent directory (T025)."""
        # Create config in grandparent (tmp_path)
        grandparent_config = tmp_path / ".ansibledoctor.yml"
        grandparent_config.write_text("output_format: rst\n")
        
        # Create nested subdirectories: tmp_path/parent/child/grandchild
        grandchild_dir = tmp_path / "parent" / "child" / "grandchild"
        grandchild_dir.mkdir(parents=True)
        
        # Search from grandchild should find grandparent config
        result = find_config_file(grandchild_dir)
        
        assert result is not None
        assert result == grandparent_config
        assert result.parent == tmp_path, "Should find config in grandparent directory"
    
    def test_find_config_file_stops_at_filesystem_root(self, tmp_path):
        """Test search stops at filesystem root (doesn't loop forever)."""
        # Search from temp directory with no config
        result = find_config_file(tmp_path)
        
        # Should return None, not raise exception or loop forever
        assert result is None


class TestConfigFileLoading:
    """Test suite for load_config() - TDD RED phase."""
    
    def test_load_config_parses_valid_yaml(self, tmp_path):
        """Test load_config() parses valid YAML successfully."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""
output_format: html
output: docs/role.html
recursive: true
exclude_patterns:
  - "*.pyc"
  - "test_*"
""")
        
        config = load_config(config_file)
        
        assert isinstance(config, ConfigModel)
        assert config.output_format == "html"
        assert config.output == "docs/role.html"
        assert config.recursive is True
        assert config.exclude_patterns == ["*.pyc", "test_*"]
    
    def test_load_config_handles_minimal_file(self, tmp_path):
        """Test load_config() handles file with minimal fields."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("output_format: markdown\n")
        
        config = load_config(config_file)
        
        assert config.output_format == "markdown"
        assert config.output is None
        assert config.recursive is False  # Default value
    
    def test_load_config_handles_empty_file(self, tmp_path):
        """Test load_config() handles empty config file (uses all defaults)."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("")
        
        config = load_config(config_file)
        
        # Should use all defaults
        assert config.output_format is None
        assert config.recursive is False
        assert config.exclude_patterns == ["*.pyc", "__pycache__", ".git"]
    
    def test_load_config_raises_on_yaml_syntax_error(self, tmp_path):
        """Test load_config() raises clear error on YAML syntax error."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""
output_format: "unclosed string
recursive: false
""")
        
        with pytest.raises(Exception) as exc_info:
            load_config(config_file)
        
        # Should mention the file and ideally line number
        error_msg = str(exc_info.value).lower()
        assert "yaml" in error_msg or "syntax" in error_msg
    
    def test_load_config_raises_on_validation_error(self, tmp_path):
        """Test load_config() raises clear error on Pydantic validation error."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""
output_format: invalid_format
recursive: false
""")
        
        with pytest.raises(ValidationError) as exc_info:
            load_config(config_file)
        
        # Should contain validation details
        error = exc_info.value
        assert len(error.errors()) > 0
        assert any("output_format" in str(e.get("loc", "")) for e in error.errors())
    
    def test_load_config_handles_missing_optional_fields(self, tmp_path):
        """Test load_config() handles missing optional fields (uses defaults)."""
        config_file = tmp_path / ".ansibledoctor.yml"
        config_file.write_text("""
output_format: rst
# output not specified
# template_dir not specified
""")
        
        config = load_config(config_file)
        
        assert config.output_format == "rst"
        assert config.output is None
        assert config.template_dir is None
        assert config.exclude_patterns == ["*.pyc", "__pycache__", ".git"]  # Default
    
    def test_load_config_file_not_found(self, tmp_path):
        """Test load_config() raises appropriate error when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.yml"
        
        with pytest.raises(FileNotFoundError):
            load_config(nonexistent)


class TestConfigMerging:
    """Test suite for merge_config() - TDD RED phase."""
    
    def test_merge_config_cli_overrides_file(self):
        """Test CLI flags override config file (config says html, CLI says rst → rst wins)."""
        file_config = ConfigModel(output_format="html", recursive=False)
        cli_config = ConfigModel(output_format="rst")
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output_format == "rst", "CLI should override file"
        assert merged.recursive is False, "File value should remain when CLI doesn't specify"
    
    def test_merge_config_file_overrides_defaults(self):
        """Test file config overrides defaults."""
        file_config = ConfigModel(output_format="markdown", recursive=True)
        cli_config = ConfigModel()  # All defaults
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output_format == "markdown"
        assert merged.recursive is True
    
    def test_merge_config_priority_cli_file_defaults(self):
        """Test merge priority: CLI > file > defaults."""
        file_config = ConfigModel(
            output_format="html",
            output="docs/file.html",
            recursive=True
        )
        cli_config = ConfigModel(
            output_format="rst",  # Override file
            # output not specified - use file value
            # recursive not specified - use file value
        )
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output_format == "rst", "CLI override"
        assert merged.output == "docs/file.html", "File value (CLI didn't specify)"
        assert merged.recursive is True, "File value (CLI didn't specify)"
    
    def test_merge_config_handles_none_values(self):
        """Test merge handles None values correctly (None means 'not specified')."""
        file_config = ConfigModel(output_format="html", output="docs/role.html")
        cli_config = ConfigModel(output_format=None, template="custom.j2")
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output_format == "html", "None in CLI means use file value"
        assert merged.output == "docs/role.html"
        assert merged.template == "custom.j2", "CLI value should be used"
    
    def test_merge_config_exclude_patterns_cli_overrides(self):
        """Test exclude_patterns from CLI completely replaces file patterns."""
        file_config = ConfigModel(exclude_patterns=["*.pyc", "*.tmp"])
        cli_config = ConfigModel(exclude_patterns=["test_*"])
        
        merged = merge_config(file_config, cli_config)
        
        # CLI should completely override, not merge lists
        assert merged.exclude_patterns == ["test_*"]
    
    def test_merge_config_with_both_none(self):
        """Test merge when both configs have None for a field (use default)."""
        file_config = ConfigModel(output_format=None)
        cli_config = ConfigModel(output_format=None)
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output_format is None  # Both None → None
    
    def test_merge_config_all_fields(self):
        """Test merge works correctly for all ConfigModel fields."""
        file_config = ConfigModel(
            output="file.html",
            output_format="html",
            template="file_template.j2",
            template_dir="file_templates/",
            recursive=True,
            output_dir="file_output/",
            exclude_patterns=["file_*"]
        )
        cli_config = ConfigModel(
            output="cli.rst",
            output_format="rst",
            # template not specified - use file
            template_dir="cli_templates/",
            # recursive not specified - use file
            output_dir="cli_output/",
            # exclude_patterns not specified - use file
        )
        
        merged = merge_config(file_config, cli_config)
        
        assert merged.output == "cli.rst"  # CLI override
        assert merged.output_format == "rst"  # CLI override
        assert merged.template == "file_template.j2"  # File (CLI None)
        assert merged.template_dir == "cli_templates/"  # CLI override
        assert merged.recursive is True  # File (CLI default)
        assert merged.output_dir == "cli_output/"  # CLI override
        assert merged.exclude_patterns == ["file_*"]  # File (CLI default)
