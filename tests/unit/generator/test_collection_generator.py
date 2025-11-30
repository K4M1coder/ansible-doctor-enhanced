"""Unit tests for CollectionDocumentationGenerator (T106-T112 RED Phase).

Tests written FIRST following TDD methodology. These tests define the expected
behavior of the CollectionDocumentationGenerator before implementation.

Test Coverage:
- T106: Generator accepts AnsibleCollection model
- T107: Generator builds template context
- T108: Generator renders Markdown output
- T109: Generator supports HTML output format
- T110: Generator supports RST output format
- T111: Generator writes to output file
- T112: Generator uses custom template if provided
"""

from pathlib import Path

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.galaxy import GalaxyMetadata
from ansibledoctor.models.plugin import Plugin, PluginType


class TestCollectionDocumentationGenerator:
    """Unit tests for CollectionDocumentationGenerator."""

    def test_generator_accepts_ansible_collection_model(self) -> None:
        """Test: Generator accepts AnsibleCollection model (T106)."""
        # Setup: Create collection
        metadata = GalaxyMetadata(
            namespace="test_ns",
            name="test_coll",
            version="1.0.0",
            authors=["Test Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=["web_server"],
            plugins={PluginType.MODULE: ["my_module.py"]},
        )

        # Execute: Create generator with collection
        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        # Verify: Generator stores collection
        assert generator.collection == collection
        assert generator.collection.metadata.namespace == "test_ns"
        assert generator.collection.metadata.name == "test_coll"

    def test_generator_builds_template_context(self) -> None:
        """Test: Generator builds template context (T107)."""
        # Setup: Create collection with plugins
        metadata = GalaxyMetadata(
            namespace="namespace",
            name="collection",
            version="2.0.0",
            authors=["Author 1", "Author 2"],
            dependencies={"community.general": ">=3.0.0"},
        )

        plugin1 = Plugin(
            name="my_module",
            type=PluginType.MODULE,
            path=Path("/collection/plugins/modules/my_module.py"),
            short_description="Example module",
        )

        plugin2 = Plugin(
            name="custom_filter",
            type=PluginType.FILTER,
            path=Path("/collection/plugins/filters/custom_filter.py"),
            short_description="Custom filter",
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=["web_server", "database"],
            plugins={
                PluginType.MODULE: ["my_module"],
                PluginType.FILTER: ["custom_filter"],
            },
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(
            collection=collection,
            plugins=[plugin1, plugin2],
        )

        # Execute: Build template context
        context = generator.build_context()

        # Verify: Context has all required fields
        assert "collection" in context
        assert "metadata" in context
        assert "fqcn" in context
        assert context["fqcn"] == "namespace.collection"
        assert "roles" in context
        assert len(context["roles"]) == 2
        assert "plugins_by_type" in context
        assert PluginType.MODULE in context["plugins_by_type"]
        assert PluginType.FILTER in context["plugins_by_type"]

    def test_generator_renders_markdown_output(self, tmp_path: Path) -> None:
        """Test: Generator renders Markdown output (T108)."""
        # Setup: Create minimal collection
        metadata = GalaxyMetadata(
            namespace="my_ns",
            name="my_coll",
            version="1.5.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=["app"],
            plugins={},
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        # Execute: Generate Markdown output
        output = generator.generate(format="markdown")

        # Verify: Output is Markdown with expected content
        assert isinstance(output, str)
        assert "# my_ns.my_coll" in output
        assert "1.5.0" in output
        assert "## Installation" in output
        assert "ansible-galaxy collection install my_ns.my_coll" in output

    def test_generator_supports_html_output_format(self, tmp_path: Path) -> None:
        """Test: Generator supports HTML output format (T109)."""
        # Setup: Create collection
        metadata = GalaxyMetadata(
            namespace="html_test",
            name="collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        # Execute: Generate HTML output
        output = generator.generate(format="html")

        # Verify: Output is HTML with expected structure
        assert isinstance(output, str)
        assert "<html" in output.lower()
        assert "<h1>" in output.lower() or "<h2>" in output.lower()
        assert "html_test.collection" in output

    def test_generator_supports_rst_output_format(self, tmp_path: Path) -> None:
        """Test: Generator supports RST output format (T110)."""
        # Setup: Create collection
        metadata = GalaxyMetadata(
            namespace="rst_test",
            name="collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        # Execute: Generate RST output
        output = generator.generate(format="rst")

        # Verify: Output is RST with expected structure
        assert isinstance(output, str)
        assert "rst_test.collection" in output
        # RST uses heading underlines with = or -
        assert "=" in output or "-" in output

    def test_generator_writes_to_output_file(self, tmp_path: Path) -> None:
        """Test: Generator writes to output file (T111)."""
        # Setup: Create collection
        metadata = GalaxyMetadata(
            namespace="file_test",
            name="collection",
            version="1.0.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        output_file = tmp_path / "collection_docs.md"

        # Execute: Generate and write to file
        generator.generate(format="markdown", output_path=output_file)

        # Verify: File was created with content
        assert output_file.exists()
        content = output_file.read_text()
        assert "file_test.collection" in content
        assert "## Installation" in content

    def test_generator_uses_custom_template_if_provided(self, tmp_path: Path) -> None:
        """Test: Generator uses custom template if provided (T112)."""
        # Setup: Create custom template
        custom_template = tmp_path / "custom_collection.j2"
        custom_template.write_text(
            "# Custom Template\n"
            "Collection: {{ metadata.namespace }}.{{ metadata.name }}\n"
            "Version: {{ metadata.version }}\n"
            "CUSTOM MARKER"
        )

        metadata = GalaxyMetadata(
            namespace="custom_test",
            name="collection",
            version="3.0.0",
            authors=["Author"],
            dependencies={},
        )

        collection = AnsibleCollection(
            metadata=metadata,
            roles=[],
            plugins={},
        )

        from ansibledoctor.generator.collection_generator import CollectionDocumentationGenerator

        generator = CollectionDocumentationGenerator(collection=collection)

        # Execute: Generate with custom template
        output = generator.generate(format="markdown", template_path=str(custom_template))

        # Verify: Custom template was used
        assert "Custom Template" in output
        assert "CUSTOM MARKER" in output
        assert "custom_test.collection" in output
        assert "3.0.0" in output
