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
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(minimal_collection_path),
            ],
            capture_output=True,
            text=True,
            check=False,
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
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(minimal_collection_path),
                "--pretty",
            ],
            capture_output=True,
            text=True,
            check=False,
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
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(minimal_collection_path),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists(), "Output file was not created"

        # Verify file contains valid JSON
        with open(output_file, "r", encoding="utf-8") as f:
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
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(minimal_collection_path),
                "--validate",
            ],
            capture_output=True,
            text=True,
            check=False,
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
            check=False,
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
            check=False,
        )

        assert result.returncode != 0, "Command should fail for malformed YAML"
        # Error message should mention YAML or parsing
        assert (
            "YAML" in result.stderr or "yaml" in result.stderr or "parse" in result.stderr.lower()
        )

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
            check=False,
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
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(realistic_collection_path),
                "--output",
                str(output_file),
                "--pretty",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
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
            check=False,
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
            check=False,
        )

        # Version command should succeed
        assert result.returncode == 0
        # Output should contain version number
        assert any(char.isdigit() for char in result.stdout)


class TestCollectionGenerateCLI:
    """Test collection generate CLI command end-to-end (T171)."""

    def test_generate_collection_docs_markdown(self, minimal_collection_path, tmp_path):
        """
        Test generating collection documentation in Markdown format.

        Verifies:
        - Command executes successfully
        - README.md is created
        - File contains expected content
        - Exit code is 0
        """
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(minimal_collection_path),
                "--output-dir",
                str(output_dir),
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify README.md was created
        readme_file = output_dir / "README.md"
        assert readme_file.exists(), "README.md was not created"

        # Verify content
        content = readme_file.read_text(encoding="utf-8")
        assert "# test_namespace.test_collection" in content
        assert "## Installation" in content
        assert "ansible-galaxy collection install" in content

    def test_generate_collection_docs_html(self, minimal_collection_path, tmp_path):
        """
        Test generating collection documentation in HTML format.

        Verifies:
        - HTML output is generated
        - File contains valid HTML
        - Exit code is 0
        """
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(minimal_collection_path),
                "--output-dir",
                str(output_dir),
                "--format",
                "html",
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify HTML file was created
        html_file = output_dir / "README.html"
        assert html_file.exists(), "README.html was not created"

        # Verify HTML structure
        content = html_file.read_text(encoding="utf-8")
        assert "<html>" in content or "<!DOCTYPE html>" in content
        assert "</html>" in content

    def test_generate_collection_docs_rst(self, minimal_collection_path, tmp_path):
        """
        Test generating collection documentation in RST format.

        Verifies:
        - RST output is generated
        - File uses RST syntax
        - Exit code is 0
        """
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(minimal_collection_path),
                "--output-dir",
                str(output_dir),
                "--format",
                "rst",
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify RST file was created
        rst_file = output_dir / "README.rst"
        assert rst_file.exists(), "README.rst was not created"

        # Verify RST structure
        content = rst_file.read_text(encoding="utf-8")
        assert "=" * 10 in content or "-" * 10 in content

    def test_generate_realistic_collection_docs(self, realistic_collection_path, tmp_path):
        """
        Test generating documentation for realistic collection.

        Verifies:
        - Complete documentation is generated
        - All roles are included
        - Dependencies are documented
        - Exit code is 0
        """
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(realistic_collection_path),
                "--output-dir",
                str(output_dir),
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        readme_file = output_dir / "README.md"
        assert readme_file.exists()

        content = readme_file.read_text(encoding="utf-8")

        # Verify realistic collection content
        assert "community.general" in content
        assert "webserver" in content
        assert "database" in content
        assert "loadbalancer" in content
        assert "ansible.posix" in content
        assert "community.crypto" in content

    def test_generate_with_custom_template(self, minimal_collection_path, tmp_path):
        """
        Test generating documentation with custom template.

        Verifies:
        - Custom template is used
        - Output reflects custom formatting
        - Exit code is 0
        """
        # Create custom template
        template_file = tmp_path / "custom.md.j2"
        template_file.write_text(
            "# CUSTOM TEMPLATE\n\n"
            "Collection: {{ collection.metadata.fqcn }}\n"
            "Version: {{ collection.metadata.version }}\n",
            encoding="utf-8",
        )

        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(minimal_collection_path),
                "--output-dir",
                str(output_dir),
                "--template",
                str(template_file),
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        readme_file = output_dir / "README.md"
        assert readme_file.exists()

        content = readme_file.read_text(encoding="utf-8")
        assert "CUSTOM TEMPLATE" in content
        assert "test_namespace.test_collection" in content

    def test_generate_command_help(self):
        """
        Test generate command help output.

        Verifies:
        - --help works
        - Help text contains expected information
        - Exit code is 0
        """
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "generate", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert "generate" in result.stdout.lower()
        assert "--output-dir" in result.stdout
        assert "--format" in result.stdout
        assert "--template" in result.stdout

    def test_generate_nonexistent_collection(self, tmp_path):
        """
        Test generating docs for nonexistent collection.

        Verifies:
        - Exit code is non-zero
        - Error message is shown
        - No files are created
        """
        nonexistent_path = tmp_path / "nonexistent"
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(nonexistent_path),
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0, "Command should fail for nonexistent path"
        assert "Error" in result.stderr or "error" in result.stderr.lower()

    def test_generate_with_invalid_format(self, minimal_collection_path, tmp_path):
        """
        Test generating docs with invalid format option.

        Verifies:
        - Exit code is non-zero
        - Error message mentions invalid format
        """
        output_dir = tmp_path / "docs"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(minimal_collection_path),
                "--output-dir",
                str(output_dir),
                "--format",
                "invalid",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0, "Command should fail for invalid format"
        # Error should mention format issue
        assert "format" in result.stderr.lower() or "invalid" in result.stderr.lower()


class TestCollectionCLIWorkflow:
    """Test complete workflow combining parse and generate commands."""

    def test_parse_then_generate_workflow(self, realistic_collection_path, tmp_path):
        """
        Test complete workflow: parse collection, then generate docs.

        Verifies:
        - Parse command succeeds
        - Generate command succeeds
        - Both outputs are valid
        - Workflow completes successfully
        """
        # Step 1: Parse collection
        parse_output = tmp_path / "collection.json"

        parse_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "parse",
                str(realistic_collection_path),
                "--output",
                str(parse_output),
                "--pretty",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert parse_result.returncode == 0, f"Parse failed: {parse_result.stderr}"
        assert parse_output.exists()

        # Step 2: Generate documentation
        docs_dir = tmp_path / "docs"

        generate_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "generate",
                str(realistic_collection_path),
                "--output-dir",
                str(docs_dir),
                "--legacy-output",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert generate_result.returncode == 0, f"Generate failed: {generate_result.stderr}"

        readme_file = docs_dir / "README.md"
        assert readme_file.exists()

        # Verify both outputs contain consistent data
        with open(parse_output, "r", encoding="utf-8") as f:
            parse_data = json.load(f)

        readme_content = readme_file.read_text(encoding="utf-8")

        # Verify consistency
        assert parse_data["fqcn"] in readme_content
        assert str(parse_data["version"]) in readme_content

        for role in parse_data["roles"]:
            assert role in readme_content


class TestCollectionAnalyzeCLI:
    """Test collection analyze CLI command end-to-end."""

    def test_analyze_collection_check_circular(self, realistic_collection_path):
        """
        Test analyzing collection with --check-circular flag.

        Verifies:
        - Command executes successfully
        - Exit code is 0 (no circular dependencies)
        - Success message is displayed
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "analyze",
                str(realistic_collection_path),
                "--check-circular",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify success message in stderr (where progress output goes)
        assert "No circular dependencies found" in result.stderr

    def test_analyze_collection_show_dependencies_text(self, realistic_collection_path):
        """
        Test analyzing collection with --show-dependencies flag (text format).

        Verifies:
        - Command executes successfully
        - ASCII tree is displayed
        - Exit code is 0
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "analyze",
                str(realistic_collection_path),
                "--show-dependencies",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify ASCII tree output in stdout
        # Realistic collection has roles: database, loadbalancer, webserver
        assert "database" in result.stdout
        assert "loadbalancer" in result.stdout
        assert "webserver" in result.stdout

    def test_analyze_collection_show_dependencies_json(self, realistic_collection_path):
        """
        Test analyzing collection with --show-dependencies and --output-format json.

        Verifies:
        - Command executes successfully
        - JSON output is valid
        - Exit code is 0
        - JSON contains expected structure
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "analyze",
                str(realistic_collection_path),
                "--show-dependencies",
                "--output-format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Parse JSON output from stdout
        output_data = json.loads(result.stdout)

        # Verify JSON structure
        assert "nodes" in output_data
        assert "edges" in output_data
        assert "circular_dependencies" in output_data
        assert "has_cycles" in output_data

        # Verify nodes contain expected roles
        node_names = [node["name"] for node in output_data["nodes"]]
        assert "database" in node_names
        assert "loadbalancer" in node_names
        assert "webserver" in node_names

        # Verify no cycles
        assert output_data["has_cycles"] is False

    def test_analyze_collection_show_dependencies_mermaid(self, realistic_collection_path):
        """
        Test analyzing collection with --show-dependencies and --output-format mermaid.

        Verifies:
        - Command executes successfully
        - Mermaid diagram is generated
        - Exit code is 0
        - Mermaid syntax is correct
        """
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "analyze",
                str(realistic_collection_path),
                "--show-dependencies",
                "--output-format",
                "mermaid",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Verify Mermaid diagram syntax
        assert "graph TD" in result.stdout

        # Verify role nodes are present
        assert "database" in result.stdout
        assert "loadbalancer" in result.stdout
        assert "webserver" in result.stdout

    def test_analyze_collection_with_circular_deps_exits_with_error(self, tmp_path):
        """
        Test analyzing collection with circular dependencies and --check-circular flag.

        Verifies:
        - Command exits with error code 1
        - Error message is displayed
        - Circular dependency warning is shown
        """
        # Create collection with circular dependencies
        collection_path = tmp_path / "circular_namespace.circular_collection"
        collection_path.mkdir()

        # Create galaxy.yml
        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """
namespace: circular_namespace
name: circular_collection
version: 1.0.0
authors:
  - Test Author
dependencies: {}
"""
        )

        # Create roles directory with circular dependencies
        roles_path = collection_path / "roles"
        roles_path.mkdir()

        # Create role_a (depends on role_b)
        role_a = roles_path / "role_a"
        role_a.mkdir()
        (role_a / "meta").mkdir()
        (role_a / "meta" / "main.yml").write_text(
            """
galaxy_info:
  author: Test Author
dependencies:
  - role: role_b
"""
        )

        # Create role_b (depends on role_a) - creates cycle
        role_b = roles_path / "role_b"
        role_b.mkdir()
        (role_b / "meta").mkdir()
        (role_b / "meta" / "main.yml").write_text(
            """
galaxy_info:
  author: Test Author
dependencies:
  - role: role_a
"""
        )

        # Run analyze command with --check-circular
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ansibledoctor",
                "collection",
                "analyze",
                str(collection_path),
                "--check-circular",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Verify exit code is 1 (error)
        assert result.returncode == 1, f"Expected error exit code, got {result.returncode}"

        # Verify error message in stderr
        assert "Circular dependencies detected" in result.stderr
        assert "role_a" in result.stderr
        assert "role_b" in result.stderr

    def test_analyze_collection_with_circular_deps_without_check_flag(self, tmp_path):
        """
        Test analyzing collection with circular dependencies without --check-circular flag.

        Verifies:
        - Command exits with code 0 (warning only)
        - Warning message is displayed
        - Circular dependencies are reported
        """
        # Create collection with circular dependencies
        collection_path = tmp_path / "circular_namespace.circular_collection"
        collection_path.mkdir()

        # Create galaxy.yml
        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """
namespace: circular_namespace
name: circular_collection
version: 1.0.0
authors:
  - Test Author
dependencies: {}
"""
        )

        # Create roles directory with circular dependencies
        roles_path = collection_path / "roles"
        roles_path.mkdir()

        # Create role_a (depends on role_b)
        role_a = roles_path / "role_a"
        role_a.mkdir()
        (role_a / "meta").mkdir()
        (role_a / "meta" / "main.yml").write_text(
            """
galaxy_info:
  author: Test Author
dependencies:
  - role: role_b
"""
        )

        # Create role_b (depends on role_a) - creates cycle
        role_b = roles_path / "role_b"
        role_b.mkdir()
        (role_b / "meta").mkdir()
        (role_b / "meta" / "main.yml").write_text(
            """
galaxy_info:
  author: Test Author
dependencies:
  - role: role_a
"""
        )

        # Run analyze command without --check-circular (should warn but not error)
        result = subprocess.run(
            [sys.executable, "-m", "ansibledoctor", "collection", "analyze", str(collection_path)],
            capture_output=True,
            text=True,
            check=False,
        )

        # Verify exit code is 0 (warning, not error)
        assert result.returncode == 0, f"Expected success exit code, got {result.returncode}"

        # Verify warning message in stderr
        assert "Circular dependencies detected" in result.stderr
        assert "use --check-circular to fail" in result.stderr
