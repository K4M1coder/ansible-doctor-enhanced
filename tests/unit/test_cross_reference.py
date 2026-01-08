"""Unit tests for CrossReferenceGenerator and LinkManager.

These tests use mock objects to test the link generation logic in isolation,
following TDD principles and testing one component at a time.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from ansibledoctor.links.cross_reference_generator import CrossReferenceGenerator
from ansibledoctor.links.link_manager import LinkManager
from ansibledoctor.models.link import Link, LinkType


class TestLinkManager:
    """Unit tests for LinkManager."""

    def test_create_link_with_explicit_parameters(self, tmp_path):
        """LinkManager should create links with all parameters specified."""
        manager = LinkManager(base_path=tmp_path)
        
        source = tmp_path / "source.md"
        target = tmp_path / "target.md"
        
        link = manager.create_link(
            source=source,
            target=target,
            text="Test Link",
            link_type=LinkType.INTERNAL_FILE,
        )
        
        assert link.source_file == source.resolve()
        assert link.target == str(target)
        assert link.text == "Test Link"
        assert link.link_type == LinkType.INTERNAL_FILE

    def test_create_link_with_auto_detection(self, tmp_path):
        """LinkManager should auto-detect link type if not specified."""
        manager = LinkManager(base_path=tmp_path)
        
        source = tmp_path / "source.md"
        
        # External URL
        link = manager.create_link(source, "https://example.com", "Example")
        assert link.link_type == LinkType.EXTERNAL_URL
        
        # Section anchor
        link = manager.create_link(source, "#section", "Section")
        assert link.link_type == LinkType.INTERNAL_SECTION
        
        # Absolute path
        link = manager.create_link(source, "/absolute/path", "Absolute")
        assert link.link_type == LinkType.ABSOLUTE_PATH
        
        # Relative path
        link = manager.create_link(source, "relative/path", "Relative")
        assert link.link_type == LinkType.RELATIVE_PATH

    def test_resolve_link_absolute_path(self, tmp_path):
        """LinkManager should resolve absolute paths correctly."""
        manager = LinkManager(base_path=tmp_path)
        
        target_file = tmp_path / "docs" / "readme.md"
        target_file.parent.mkdir(parents=True)
        target_file.write_text("# README")
        
        link = Link(
            source_file=tmp_path / "index.md",
            target=str(target_file),
            link_type=LinkType.INTERNAL_FILE,
            text="README",
            line_number=None,
        )
        
        resolved = manager.resolve_link(link)
        assert resolved == target_file.resolve()

    def test_resolve_link_relative_path(self, tmp_path):
        """LinkManager should resolve relative paths from base_path."""
        manager = LinkManager(base_path=tmp_path)
        
        link = Link(
            source_file=tmp_path / "index.md",
            target="docs/guide.md",
            link_type=LinkType.RELATIVE_PATH,
            text="Guide",
            line_number=None,
        )
        
        resolved = manager.resolve_link(link)
        expected = (tmp_path / "docs" / "guide.md").resolve()
        assert resolved == expected

    def test_extract_anchor_from_target(self, tmp_path):
        """LinkManager should extract anchors from targets."""
        manager = LinkManager(base_path=tmp_path)
        
        # With anchor
        anchor = manager.extract_anchor("docs/guide.md#section-1")
        assert anchor == "section-1"
        
        # Without anchor
        anchor = manager.extract_anchor("docs/guide.md")
        assert anchor is None

    def test_format_link_markdown(self, tmp_path):
        """LinkManager should format links as Markdown."""
        manager = LinkManager(base_path=tmp_path)
        
        link = Link(
            source_file=tmp_path / "index.md",
            target="docs/guide.md",
            link_type=LinkType.RELATIVE_PATH,
            text="User Guide",
            line_number=None,
        )
        
        formatted = manager.format_link(link, "markdown")
        assert formatted == "[User Guide](docs/guide.md)"

    def test_format_link_html(self, tmp_path):
        """LinkManager should format links as HTML with escaping."""
        manager = LinkManager(base_path=tmp_path)
        
        link = Link(
            source_file=tmp_path / "index.md",
            target="docs/guide.md?param=value&other=data",
            link_type=LinkType.RELATIVE_PATH,
            text="Guide <Beta>",
            line_number=None,
        )
        
        formatted = manager.format_link(link, "html")
        assert formatted == '<a href="docs/guide.md?param=value&amp;other=data">Guide &lt;Beta&gt;</a>'

    def test_format_link_rst(self, tmp_path):
        """LinkManager should format links as reStructuredText."""
        manager = LinkManager(base_path=tmp_path)
        
        link = Link(
            source_file=tmp_path / "index.md",
            target="docs/guide.md",
            link_type=LinkType.RELATIVE_PATH,
            text="User Guide",
            line_number=None,
        )
        
        formatted = manager.format_link(link, "rst")
        assert formatted == "`User Guide <docs/guide.md>`_"


class TestCrossReferenceGenerator:
    """Unit tests for CrossReferenceGenerator."""

    def test_generate_dependency_links(self, tmp_path):
        """CrossReferenceGenerator should create links for role dependencies."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        # Mock role with dependencies
        role = Mock()
        role.path = tmp_path / "roles" / "webserver"
        role.name = "webserver"
        role.parent_collection = None  # Standalone role
        
        # Mock metadata with dependencies
        dep1 = Mock()
        dep1.name = "common"
        dep1.version = "1.2.3"
        
        dep2 = Mock()
        dep2.name = "firewall"
        dep2.version = None
        
        role.metadata = Mock()
        role.metadata.dependencies = [dep1, dep2]
        role.metadata.galaxy_tags = []  # No tags
        
        references = generator.generate_references(role)
        
        assert "depends_on" in references
        deps = references["depends_on"]
        assert len(deps) == 2
        
        # Check first dependency
        assert deps[0]["name"] == "common"
        assert deps[0]["version"] == "1.2.3"
        assert deps[0]["link"].text == "common (v1.2.3)"
        assert "common" in deps[0]["link"].target
        assert "README.md" in deps[0]["link"].target
        
        # Check second dependency (no version)
        assert deps[1]["name"] == "firewall"
        assert deps[1]["version"] == ""
        assert deps[1]["link"].text == "firewall"

    def test_generate_no_dependencies(self, tmp_path):
        """CrossReferenceGenerator should handle roles without dependencies."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        role = Mock()
        role.path = tmp_path / "roles" / "standalone"
        role.name = "standalone"
        role.parent_collection = None
        role.metadata = Mock()
        role.metadata.dependencies = []
        role.metadata.galaxy_tags = []
        
        references = generator.generate_references(role)
        
        assert "depends_on" not in references

    def test_generate_parent_collection_link(self, tmp_path):
        """CrossReferenceGenerator should create parent collection links."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        # Mock collection with proper Path
        collection_path = tmp_path / "ansible_collections" / "myorg" / "mycollection"
        collection = Mock()
        collection.namespace = "myorg"
        collection.name = "mycollection"
        collection.version = "1.0.0"
        collection.path = collection_path
        
        # Mock role with parent collection
        role = Mock()
        role.path = collection_path / "roles" / "webserver"
        role.name = "webserver"
        role.parent_collection = collection
        role.metadata = Mock()
        role.metadata.dependencies = []
        role.metadata.galaxy_tags = []
        
        references = generator.generate_references(role)
        
        assert "parent_collection" in references
        parent = references["parent_collection"]
        assert parent["name"] == "myorg.mycollection"
        assert parent["version"] == "1.0.0"
        assert parent["link"].text == "myorg.mycollection (v1.0.0)"
        assert "mycollection" in parent["link"].target
        assert "README.md" in parent["link"].target

    def test_generate_no_parent_collection(self, tmp_path):
        """CrossReferenceGenerator should handle standalone roles."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        role = Mock()
        role.path = tmp_path / "roles" / "standalone"
        role.name = "standalone"
        role.parent_collection = None
        role.metadata = Mock()
        role.metadata.dependencies = []
        role.metadata.galaxy_tags = []
        
        references = generator.generate_references(role)
        
        assert "parent_collection" not in references

    def test_generate_project_context_with_collection(self, tmp_path):
        """CrossReferenceGenerator should create project context breadcrumbs."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        # Mock collection with proper Path
        collection_path = tmp_path / "ansible_collections" / "myorg" / "myproject"
        collection = Mock()
        collection.namespace = "myorg"
        collection.name = "myproject"
        collection.path = collection_path
        
        # Mock role
        role = Mock()
        role.path = collection_path / "roles" / "api"
        role.name = "api"
        role.parent_collection = collection
        role.metadata = Mock()
        role.metadata.dependencies = []
        role.metadata.galaxy_tags = []
        
        references = generator.generate_references(role)
        
        assert "project_context" in references
        context = references["project_context"]
        
        # Should have breadcrumb trail
        assert "breadcrumb" in context
        assert len(context["breadcrumb"]) >= 2  # At least collection and role
        assert context["breadcrumb"][0]["name"] == "myproject"
        assert context["breadcrumb"][-1]["name"] == "api"
        
        # Should have hierarchy information
        assert context["hierarchy"]["collection"] == "myproject"

    def test_get_document_context_extracts_collection_and_role(self, tmp_path):
        """CrossReferenceGenerator should extract context from document paths."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        doc_path = tmp_path / "ansible_collections" / "myorg" / "myproject" / "roles" / "api" / "README.md"
        
        context = generator.get_document_context(doc_path)
        
        assert context["collection_name"] == "myorg.myproject"
        assert context["role_name"] == "api"

    def test_get_document_context_without_collection(self, tmp_path):
        """CrossReferenceGenerator should handle docs outside collections."""
        generator = CrossReferenceGenerator(base_path=tmp_path)
        
        doc_path = tmp_path / "roles" / "standalone" / "README.md"
        
        context = generator.get_document_context(doc_path)
        
        assert "collection_name" not in context
        assert context["role_name"] == "standalone"
