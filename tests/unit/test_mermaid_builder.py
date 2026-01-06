"""Unit tests for Mermaid diagram builder."""

from pathlib import Path

import pytest

from ansibledoctor.models.index import IndexItem
from ansibledoctor.utils.mermaid_builder import MermaidBuilder


class TestMermaidBuilder:
    """Test Mermaid diagram generation."""

    @pytest.fixture
    def simple_structure(self):
        """Create simple structure for testing."""
        collection = IndexItem(
            name="my_collection",
            type="collection",
            description="Test collection",
            path=Path("collections/my_collection"),
            doc_link="./collections/my_collection.md",
        )

        role1 = IndexItem(
            name="webserver",
            type="role",
            description="Web server role",
            path=Path("roles/webserver"),
            doc_link="./roles/webserver.md",
        )

        role2 = IndexItem(
            name="database",
            type="role",
            description="Database role",
            path=Path("roles/database"),
            doc_link="./roles/database.md",
            dependencies=["webserver"],
        )

        collection.children.extend([role1, role2])
        return [collection]

    def test_flowchart_syntax(self, simple_structure):
        """T063: Test Mermaid flowchart generates correct syntax."""
        builder = MermaidBuilder()
        result = builder.build_flowchart(simple_structure, direction="TD")

        # Verify graph declaration
        assert result.startswith("graph TD")

        # Verify nodes are defined
        assert "my_collection[my_collection]" in result
        assert "webserver(webserver)" in result  # Rounded rectangle for role
        assert "database(database)" in result

    def test_dependency_arrows(self, simple_structure):
        """T064: Test dependency arrows are shown correctly."""
        builder = MermaidBuilder()
        result = builder.build_flowchart(simple_structure)

        # Verify dependency arrow (dotted line)
        assert "database -.depends.-> webserver" in result

        # Verify parent-child arrows (solid line)
        assert "my_collection --> webserver" in result
        assert "my_collection --> database" in result

    def test_mindmap_diagram(self, simple_structure):
        """T065: Test mindmap diagram syntax."""
        builder = MermaidBuilder()
        result = builder.build_mindmap(simple_structure)

        # Verify mindmap declaration
        assert result.startswith("mindmap")
        assert "root((Project))" in result

        # Verify hierarchical structure
        assert "my_collection" in result
        assert "webserver" in result
        assert "database" in result

        # Verify indentation (nested structure)
        lines = result.split("\n")
        collection_line = next(line for line in lines if "my_collection" in line)
        role_line = next(line for line in lines if "webserver" in line)

        # Role should be more indented than collection
        assert len(role_line) - len(role_line.lstrip()) > len(collection_line) - len(
            collection_line.lstrip()
        )

    def test_clickable_nodes(self, simple_structure):
        """T066: Test clickable nodes include click directives."""
        builder = MermaidBuilder(use_clickable_nodes=True)
        result = builder.build_flowchart(simple_structure)

        # Verify click directives
        assert 'click my_collection "./collections/my_collection.md"' in result
        assert 'click webserver "./roles/webserver.md"' in result
        assert 'click database "./roles/database.md"' in result

    def test_no_clickable_nodes(self, simple_structure):
        """Test click directives omitted when disabled."""
        builder = MermaidBuilder(use_clickable_nodes=False)
        result = builder.build_flowchart(simple_structure)

        # Verify no click directives
        assert "click" not in result

    def test_node_shapes_by_type(self):
        """Test different node shapes for different component types."""
        builder = MermaidBuilder(use_clickable_nodes=False)

        items = [
            IndexItem(
                name="test_collection", type="collection", path=Path("c"), description=""
            ),
            IndexItem(
                name="test_role", type="role", path=Path("r"), description=""
            ),
            IndexItem(
                name="test_module", type="module", path=Path("m"), description=""
            ),
            IndexItem(
                name="test_playbook", type="playbook", path=Path("p"), description=""
            ),
        ]

        result = builder.build_flowchart(items)

        # Verify shapes
        assert "test_collection[test_collection]" in result  # Rectangle
        assert "test_role(test_role)" in result  # Rounded rectangle
        assert "test_module[[test_module]]" in result  # Subroutine
        assert "test_playbook{test_playbook}" in result  # Rhombus

    def test_large_project_clustering(self):
        """T067: Test large project with 100+ components."""
        # Create 100+ components
        items = []
        for i in range(150):
            collection = IndexItem(
                name=f"collection_{i}",
                type="collection",
                path=Path(f"c{i}"),
                description=f"Collection {i}",
            )

            # Add some roles
            for j in range(3):
                role = IndexItem(
                    name=f"role_{i}_{j}",
                    type="role",
                    path=Path(f"r{i}_{j}"),
                    description=f"Role {i}-{j}",
                )
                collection.children.append(role)

            items.append(collection)

        builder = MermaidBuilder(use_clickable_nodes=False)
        result = builder.build_flowchart(items)

        # Verify diagram generated without error
        assert result.startswith("graph TD")

        # Verify all collections present
        assert "collection_0" in result
        assert "collection_149" in result

        # Verify relationships (sample check)
        assert "collection_0 --> role_0_0" in result

    def test_sanitize_special_characters(self):
        """Test node ID sanitization for special characters."""
        builder = MermaidBuilder(use_clickable_nodes=False)

        items = [
            IndexItem(
                name="my-role.with.special-chars",
                type="role",
                path=Path("r"),
                description="",
            )
        ]

        result = builder.build_flowchart(items)

        # Verify special chars replaced with underscores
        assert "my_role_with_special_chars" in result
