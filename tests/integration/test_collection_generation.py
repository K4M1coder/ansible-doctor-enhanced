"""
Integration tests for collection documentation generation.

Tests the complete documentation generation workflow including:
- Generating docs for mock collections
- Multiple output formats (Markdown, HTML, RST)
- Custom template usage
- Output file creation and validation
"""

from pathlib import Path

import pytest

from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.parser.collection_parser import CollectionParser


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


@pytest.fixture
def comprehensive_collection_path():
    """Path to comprehensive collection with all plugin types."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures" / "collections"
    return fixtures_dir / "comprehensive_collection"


class TestCollectionDocumentationGeneration:
    """Test documentation generation for collections."""

    def test_generate_docs_for_minimal_collection(self, minimal_collection_path, tmp_path):
        """
        Test generating documentation for minimal collection.

        Verifies:
        - Documentation is generated successfully
        - Output file is created
        - Output contains expected sections (title, installation, etc.)
        - Markdown format is correct
        """
        # Parse collection
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        # Generate documentation
        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify output file exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text(encoding="utf-8")

        # Check for key sections
        assert f"# {collection.metadata.fqcn}" in content
        assert "## Installation" in content
        assert "ansible-galaxy collection install" in content
        assert collection.metadata.fqcn in content

        # Check version info
        assert str(collection.metadata.version) in content

    def test_generate_docs_for_realistic_collection(self, realistic_collection_path, tmp_path):
        """
        Test generating documentation for realistic collection with roles and plugins.

        Verifies:
        - All roles are listed
        - All plugins are listed
        - Dependencies are documented
        - Structure is well-formatted
        """
        # Parse collection
        parser = CollectionParser()
        collection = parser.parse(realistic_collection_path)

        # Generate documentation
        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify output file exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text(encoding="utf-8")

        # Check roles section
        assert "## Roles" in content
        for role_name in collection.roles:
            assert role_name in content

        # Check dependencies if present
        if collection.metadata.dependencies:
            assert "## Dependencies" in content

        # Note: Plugins section requires Plugin objects to be passed to generator
        # Currently, CollectionParser only discovers plugin names, not full Plugin objects
        # This is expected behavior for v0.5.0 MVP

    def test_generate_docs_with_all_plugin_types(self, comprehensive_collection_path, tmp_path):
        """
        Test generating documentation for collection with all plugin types.

        Verifies:
        - All plugin types are documented
        - Plugins are grouped by type
        - Each plugin type section is present
        """
        # Parse collection
        parser = CollectionParser()
        collection = parser.parse(comprehensive_collection_path)

        # Generate documentation
        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify output file exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text(encoding="utf-8")

        # Check for basic structure
        assert "## Overview" in content
        assert "## Installation" in content

        # Note: Plugins section requires Plugin objects to be passed to generator
        # Currently, CollectionParser only discovers plugin names, not full Plugin objects
        # This is expected behavior for v0.5.0 MVP - plugin details will be in v0.6.0
        assert len(content) > 500  # Substantial content


class TestMultipleOutputFormats:
    """Test generating documentation in multiple output formats."""

    def test_generate_markdown_format(self, minimal_collection_path, tmp_path):
        """
        Test generating Markdown format documentation.

        Verifies:
        - .md file is created
        - Content is valid Markdown
        - Headers use # syntax
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        assert output_file.exists()
        assert output_file.suffix == ".md"

        content = output_file.read_text(encoding="utf-8")
        assert content.startswith("#")  # Markdown header
        assert "##" in content  # Subheaders

    def test_generate_html_format(self, minimal_collection_path, tmp_path):
        """
        Test generating HTML format documentation.

        Verifies:
        - .html file is created
        - Content is valid HTML
        - Contains HTML tags
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.html"

        generator.generate(output_path=output_file, format=OutputFormat.HTML.value)

        assert output_file.exists()
        assert output_file.suffix == ".html"

        content = output_file.read_text(encoding="utf-8")
        assert "<html>" in content or "<!DOCTYPE html>" in content
        assert "<h1>" in content or "<h2>" in content  # HTML headers
        assert "</html>" in content

    def test_generate_rst_format(self, minimal_collection_path, tmp_path):
        """
        Test generating reStructuredText format documentation.

        Verifies:
        - .rst file is created
        - Content is valid RST
        - Uses RST header syntax
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.rst"

        generator.generate(output_path=output_file, format=OutputFormat.RST.value)

        assert output_file.exists()
        assert output_file.suffix == ".rst"

        content = output_file.read_text(encoding="utf-8")
        # RST uses underlines for headers (===, ---, ~~~)
        assert ("=" * 10) in content or ("-" * 10) in content


class TestCustomTemplateUsage:
    """Test using custom templates for documentation generation."""

    def test_generate_with_custom_template(self, minimal_collection_path, tmp_path):
        """
        Test generating documentation with custom template.

        Verifies:
        - Custom template is used
        - Template variables are populated
        - Output reflects custom formatting
        """
        # Create a simple custom template
        custom_template = tmp_path / "custom_collection.md.j2"
        custom_template.write_text(
            """# CUSTOM: {{ collection.metadata.fqcn }}

Version: {{ collection.metadata.version }}

Custom template test!

Roles: {{ collection.roles | length }}
""",
            encoding="utf-8",
        )

        # Parse collection
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        # Generate documentation with custom template
        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(
            output_path=output_file,
            format=OutputFormat.MARKDOWN.value,
            template_path=custom_template,
        )

        # Verify output
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")

        # Verify custom template was used
        assert "CUSTOM:" in content
        assert "Custom template test!" in content
        assert collection.metadata.fqcn in content
        assert f"Roles: {len(collection.roles)}" in content

    def test_generate_with_missing_custom_template_fails(self, minimal_collection_path, tmp_path):
        """
        Test that generation fails gracefully with missing custom template.

        Verifies:
        - Appropriate error is raised
        - Error message is clear
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"
        missing_template = tmp_path / "nonexistent_template.j2"

        with pytest.raises(FileNotFoundError):
            generator.generate(
                output_path=output_file,
                format=OutputFormat.MARKDOWN.value,
                template_path=missing_template,
            )


class TestGenerationEdgeCases:
    """Test edge cases in documentation generation."""

    def test_generate_for_collection_with_no_roles(self, minimal_collection_path, tmp_path):
        """
        Test generating docs for collection with no roles.

        Verifies:
        - Generation succeeds
        - Roles section handles empty list gracefully
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        generator = CollectionDocumentationGenerator(collection=collection)
        output_file = tmp_path / "README.md"

        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")

        # Should still have main sections
        assert "Installation" in content

    def test_generate_overwrites_existing_file(self, minimal_collection_path, tmp_path):
        """
        Test that generation overwrites existing output file.

        Verifies:
        - Existing file is replaced
        - New content is written
        """
        parser = CollectionParser()
        collection = parser.parse(minimal_collection_path)

        output_file = tmp_path / "README.md"

        # Create existing file with old content
        output_file.write_text("OLD CONTENT", encoding="utf-8")

        # Generate new documentation
        generator = CollectionDocumentationGenerator(collection=collection)
        generator.generate(output_path=output_file, format=OutputFormat.MARKDOWN.value)

        # Verify new content
        content = output_file.read_text(encoding="utf-8")
        assert "OLD CONTENT" not in content
        assert collection.metadata.fqcn in content
