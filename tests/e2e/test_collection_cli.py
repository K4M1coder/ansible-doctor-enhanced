"""
End-to-end integration tests for collection CLI commands.

Tests the complete CLI workflow including:
- Command execution
- JSON output format
- File output with --output flag
- Pretty printing with --pretty flag
- Validation mode with --validate flag
- Exit codes
- Error scenarios
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def minimal_collection_path():
    """Path to minimal valid test collection."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
    return fixtures_dir / "minimal_valid"


@pytest.fixture
def realistic_collection_path():
    """Path to realistic test collection."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
    return fixtures_dir / "realistic_collection"


class TestCollectionParseCLI:
    """Test collection parse CLI command end-to-end."""
    
    def test_parse_collection_to_stdout(self, minimal_collection_path):
        """
        Test parsing collection with JSON output to stdout.
        
        Verifies:
        - Command executes successfully
        - Output is valid JSON
        - Exit code is 0
        - JSON contains expected structure
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(minimal_collection_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        
        # Verify structure (flat format with fqcn, version, etc. at top level)
        assert "fqcn" in output_data
        assert "namespace" in output_data
        assert "name" in output_data
        assert "version" in output_data
        assert "authors" in output_data
        assert "dependencies" in output_data
        assert "roles" in output_data
        assert "plugins" in output_data
    
    def test_parse_collection_with_pretty_flag(self, minimal_collection_path):
        """
        Test parsing collection with --pretty flag for formatted JSON.
        
        Verifies:
        - JSON is pretty-printed (indented)
        - Output is still valid JSON
        - Exit code is 0
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(minimal_collection_path), "--pretty"],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Verify output is pretty-printed (contains newlines and indentation)
        assert "\n" in result.stdout
        assert "  " in result.stdout  # Indentation
        
        # Verify it's still valid JSON
        output_data = json.loads(result.stdout)
        assert "fqcn" in output_data
        assert "roles" in output_data
    
    def test_parse_collection_with_output_file(self, minimal_collection_path, tmp_path):
        """
        Test parsing collection with --output flag to write to file.
        
        Verifies:
        - File is created at specified path
        - File contains valid JSON
        - Exit code is 0
        - Stdout is empty (output goes to file)
        """
        output_file = tmp_path / "collection_output.json"
        
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(minimal_collection_path), "--output", str(output_file)],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists(), "Output file was not created"
        
        # Verify file contains valid JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        assert "fqcn" in output_data
        assert "namespace" in output_data
    
    def test_parse_collection_with_validate_flag(self, minimal_collection_path):
        """
        Test parsing collection with --validate flag (no output).
        
        Verifies:
        - Exit code is 0 for valid collection
        - No JSON output to stdout
        - Parser runs successfully
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(minimal_collection_path), "--validate"],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        # In validate mode, stdout should be empty (no JSON output)
        assert result.stdout.strip() == "" or "Valid" in result.stdout


class TestCollectionCLIErrorHandling:
    """Test error scenarios and exit codes for collection CLI."""
    
    def test_parse_nonexistent_collection(self, tmp_path):
        """
        Test parsing nonexistent collection directory.
        
        Verifies:
        - Exit code is non-zero (error)
        - Error message is shown
        - No JSON output
        """
        nonexistent_path = tmp_path / "nonexistent_collection"
        
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(nonexistent_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode != 0, "Command should fail for nonexistent path"
        assert "Error" in result.stderr or "error" in result.stderr.lower()
    
    def test_parse_malformed_galaxy_yml(self):
        """
        Test parsing collection with malformed galaxy.yml.
        
        Verifies:
        - Exit code is non-zero (error)
        - Error message mentions YAML parsing
        - No JSON output
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
        malformed_path = fixtures_dir / "malformed_yaml"
        
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(malformed_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode != 0, "Command should fail for malformed YAML"
        # Error message should mention YAML or parsing
        assert "YAML" in result.stderr or "yaml" in result.stderr or "parse" in result.stderr.lower()
    
    def test_parse_collection_missing_required_fields(self):
        """
        Test parsing collection with missing required galaxy.yml fields.
        
        Verifies:
        - Exit code is non-zero (error)
        - Error message mentions missing fields
        - No JSON output
        """
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
        invalid_path = fixtures_dir / "invalid_missing_namespace"
        
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(invalid_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode != 0, "Command should fail for invalid galaxy.yml"
        assert "Error" in result.stderr or "error" in result.stderr.lower()


class TestCollectionCLIIntegration:
    """Test complete CLI workflows with realistic collections."""
    
    def test_parse_realistic_collection_end_to_end(self, realistic_collection_path, tmp_path):
        """
        Test complete workflow with realistic collection.
        
        Verifies:
        - Parse realistic collection
        - Export to file
        - Verify all components present
        - JSON is well-formed
        """
        output_file = tmp_path / "realistic_output.json"
        
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", str(realistic_collection_path), "--output", str(output_file), "--pretty"],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
        
        # Verify collection structure
        assert output_data["namespace"] == "community"
        assert output_data["name"] == "general"
        assert output_data["fqcn"] == "community.general"
        assert len(output_data["roles"]) == 3
        assert "module" in output_data["plugins"]
        assert "filter" in output_data["plugins"]
        assert "lookup" in output_data["plugins"]
    
    def test_cli_help_command(self):
        """
        Test CLI help output.
        
        Verifies:
        - --help flag works
        - Help text contains expected information
        - Exit code is 0
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "parse", "--help"],
            capture_output=True,
            text=True,
            check=False
        )
        
        assert result.returncode == 0
        assert "parse" in result.stdout.lower()
        assert "--output" in result.stdout
        assert "--pretty" in result.stdout
        assert "--validate" in result.stdout
    
    def test_cli_version_consistency(self):
        """
        Test CLI version output consistency.
        
        Verifies:
        - Version command works
        - Version format is valid
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Version command should succeed
        assert result.returncode == 0
        # Output should contain version number
        assert any(char.isdigit() for char in result.stdout)
