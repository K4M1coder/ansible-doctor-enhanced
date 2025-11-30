"""
Integration tests for parsing real-world collections.

Tests the complete collection parsing workflow with realistic collection structures
that mirror actual Ansible collections like community.general.
"""

from pathlib import Path

import pytest

from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import PluginType
from ansibledoctor.parser.collection_parser import CollectionParser


@pytest.fixture
def realistic_collection_path(tmp_path):
    """
    Path to the realistic collection fixture.

    Simulates a real collection like community.general with:
    - Multiple roles (webserver, database, loadbalancer)
    - Multiple plugin types (modules, filters, lookup)
    - Comprehensive galaxy.yml metadata
    - Dependencies on other collections
    """
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
    return fixtures_dir / "realistic_collection"


class TestRealisticCollectionParsing:
    """Test parsing of realistic collection structures."""

    def test_parse_realistic_collection_structure(self, realistic_collection_path):
        """
        Test parsing a realistic collection structure.

        Verifies:
        - Collection metadata is extracted correctly
        - All roles are discovered
        - All plugin types are discovered
        - Dependencies are parsed
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        assert isinstance(collection, AnsibleCollection)
        assert collection.metadata.namespace == "community"
        assert collection.metadata.name == "general"
        assert collection.metadata.version == "2.5.0"
        assert collection.fqcn == "community.general"

    def test_discover_all_roles_in_realistic_collection(self, realistic_collection_path):
        """
        Test role discovery in realistic collection.

        Verifies all role directories are discovered:
        - webserver
        - database
        - loadbalancer
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        assert len(collection.roles) == 3
        assert "webserver" in collection.roles
        assert "database" in collection.roles
        assert "loadbalancer" in collection.roles

    def test_discover_modules_in_realistic_collection(self, realistic_collection_path):
        """
        Test module discovery in realistic collection.

        Verifies modules are discovered in plugins/modules/:
        - package_mgr.py
        - docker_container.py
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        modules = collection.plugins.get(PluginType.MODULE, [])
        assert len(modules) == 2
        assert "package_mgr" in modules
        assert "docker_container" in modules

    def test_discover_filters_in_realistic_collection(self, realistic_collection_path):
        """
        Test filter plugin discovery in realistic collection.

        Verifies filters are discovered in plugins/filters/:
        - text_manipulation.py
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        filters = collection.plugins.get(PluginType.FILTER, [])
        assert len(filters) == 1
        assert "text_manipulation" in filters

    def test_discover_lookup_plugins_in_realistic_collection(self, realistic_collection_path):
        """
        Test lookup plugin discovery in realistic collection.

        Verifies lookup plugins are discovered in plugins/lookup/:
        - env_var.py
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        lookups = collection.plugins.get(PluginType.LOOKUP, [])
        assert len(lookups) == 1
        assert "env_var" in lookups

    def test_parse_dependencies_in_realistic_collection(self, realistic_collection_path):
        """
        Test dependency parsing in realistic collection.

        Verifies dependencies are extracted from galaxy.yml:
        - ansible.posix: ">=1.0.0"
        - community.crypto: ">=2.0.0"
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        assert len(collection.metadata.dependencies) == 2
        assert "ansible.posix" in collection.metadata.dependencies
        assert "community.crypto" in collection.metadata.dependencies
        assert collection.metadata.dependencies["ansible.posix"] == ">=1.0.0"
        assert collection.metadata.dependencies["community.crypto"] == ">=2.0.0"

    def test_parse_authors_in_realistic_collection(self, realistic_collection_path):
        """
        Test author extraction in realistic collection.

        Verifies authors list is parsed correctly.
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        assert len(collection.metadata.authors) == 2
        assert "Ansible Community" in collection.metadata.authors
        assert "Various Contributors" in collection.metadata.authors

    def test_realistic_collection_json_serialization(self, realistic_collection_path):
        """
        Test that realistic collection can be serialized to JSON.

        Verifies the parsed collection model can be converted to JSON
        for CLI output purposes.
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        # Test JSON serialization
        json_data = collection.model_dump(mode="json")

        assert json_data["metadata"]["namespace"] == "community"
        assert json_data["metadata"]["name"] == "general"
        assert len(json_data["roles"]) == 3
        # Plugin types are stored by enum value (module, filter, lookup, etc.)
        assert "module" in json_data["plugins"]
        assert "filter" in json_data["plugins"]
        assert "lookup" in json_data["plugins"]


class TestRealisticCollectionEdgeCases:
    """Test edge cases with realistic collection structures."""

    def test_collection_with_empty_plugin_directories(self, tmp_path):
        """
        Test parsing collection with empty plugin type directories.

        Verifies parser handles plugin directories that exist but are empty.
        """
        # Create minimal collection with empty plugin dirs
        collection_path = tmp_path / "test_collection"
        collection_path.mkdir()

        (collection_path / "roles").mkdir()
        (collection_path / "plugins" / "modules").mkdir(parents=True)
        (collection_path / "plugins" / "filters").mkdir(parents=True)

        # Create minimal galaxy.yml
        galaxy_yml = collection_path / "galaxy.yml"
        galaxy_yml.write_text(
            """---
namespace: test
name: empty_plugins
version: 1.0.0
authors:
  - "Test Author"
dependencies: {}
"""
        )

        parser = CollectionParser()
        collection = parser.parse(collection_path)

        # Should parse successfully with empty plugin lists
        assert collection.metadata.namespace == "test"
        modules = collection.plugins.get(PluginType.MODULE, [])
        filters = collection.plugins.get(PluginType.FILTER, [])
        assert len(modules) == 0
        assert len(filters) == 0

    def test_collection_performance_with_multiple_plugins(self, realistic_collection_path):
        """
        Test parsing performance with realistic collection size.

        Verifies parsing completes in reasonable time (<5s for typical collection).
        """
        import time

        parser = CollectionParser()

        start_time = time.time()
        collection = parser.parse(realistic_collection_path)
        elapsed_time = time.time() - start_time

        # Should complete in under 5 seconds
        assert elapsed_time < 5.0
        assert collection is not None


class TestRealisticCollectionDocumentationGeneration:
    """Test documentation generation for realistic collections (T169)."""

    def test_generate_docs_for_realistic_collection(self, realistic_collection_path, tmp_path):
        """
        Test generating documentation for realistic collection structure.

        Verifies:
        - Documentation is generated successfully
        - All roles are documented
        - Dependencies section is included
        - Output is well-formatted
        """
        # Parse the realistic collection
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        # Generate documentation
        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "community.general.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify output exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text(encoding="utf-8")

        # Check collection identity
        assert "# community.general" in content
        assert "**Version:** 2.5.0" in content

        # Check all roles are listed
        assert "## Roles" in content
        assert "webserver" in content
        assert "database" in content
        assert "loadbalancer" in content

        # Check dependencies section
        assert "## Dependencies" in content
        assert "ansible.posix" in content
        assert "community.crypto" in content
        assert ">=1.0.0" in content
        assert ">=2.0.0" in content

        # Check installation instructions
        assert "## Installation" in content
        assert "ansible-galaxy collection install community.general" in content

    def test_generate_html_for_realistic_collection(self, realistic_collection_path, tmp_path):
        """
        Test generating HTML documentation for realistic collection.

        Verifies:
        - HTML output is generated
        - Contains valid HTML structure
        - Includes all key sections
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "community.general.html"

        generator.generate(output_path=output_file, format=OutputFormat.HTML.value)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")

        # Verify HTML structure
        assert "<html>" in content or "<!DOCTYPE html>" in content
        assert "</html>" in content

        # Check for headers
        assert "<h1>" in content or "<h2>" in content

        # Verify collection name is present
        assert "community.general" in content

    def test_generate_rst_for_realistic_collection(self, realistic_collection_path, tmp_path):
        """
        Test generating RST documentation for realistic collection.

        Verifies:
        - RST output is generated
        - Uses proper RST syntax
        - Includes all sections
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "community.general.rst"

        generator.generate(output_path=output_file, format=OutputFormat.RST.value)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")

        # Verify RST structure (uses === and --- for headers)
        assert "=" * 10 in content or "-" * 10 in content

        # Check content includes collection name
        assert "community.general" in content
        assert "2.5.0" in content

    def test_documentation_includes_all_metadata(self, realistic_collection_path, tmp_path):
        """
        Test that generated documentation includes all metadata fields.

        Verifies:
        - Authors are listed
        - Version is displayed
        - Namespace and name are correct
        - Dependencies are documented
        """
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        output = generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify all metadata is present
        assert "Ansible Community" in output
        assert "Various Contributors" in output
        assert "2.5.0" in output
        assert "community" in output
        assert "general" in output
        assert "ansible.posix" in output
        assert "community.crypto" in output

    def test_documentation_generation_performance(self, realistic_collection_path, tmp_path):
        """
        Test documentation generation performance.

        Verifies generation completes in reasonable time (<3s for typical collection).
        """
        import time

        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        start_time = time.time()
        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)
        elapsed_time = time.time() - start_time

        # Should complete quickly
        assert elapsed_time < 3.0
        assert output_file.exists()
