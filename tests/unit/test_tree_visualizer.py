"""Unit tests for TreeVisualizer class."""

from pathlib import Path

import pytest

from ansibledoctor.generator.tree_visualizer import TreeVisualizer
from ansibledoctor.models.index import IndexItem


class TestTreeVisualizer:
    """Tests for US2 - ASCII Tree Rendering."""

    @pytest.fixture
    def simple_tree(self):
        """Create simple tree structure for testing."""
        root = IndexItem(
            name="my_collection",
            type="collection",
            path=Path("collections/my_collection"),
            namespace="my_namespace",
        )

        role1 = IndexItem(
            name="webserver",
            type="role",
            description="Web server role",
            path=Path("collections/my_collection/roles/webserver"),
            namespace="my_namespace",
        )

        role2 = IndexItem(
            name="database",
            type="role",
            description="Database role",
            path=Path("collections/my_collection/roles/database"),
            namespace="my_namespace",
        )

        root.children.extend([role1, role2])
        return [root]

    @pytest.fixture
    def deep_tree(self):
        """Create deep tree structure for depth testing."""
        # Collection
        collection = IndexItem(
            name="my_collection",
            type="collection",
            path=Path("collections/my_collection"),
            namespace="my_namespace",
        )

        # Role
        role = IndexItem(
            name="deploy",
            type="role",
            path=Path("collections/my_collection/roles/deploy"),
            namespace="my_namespace",
        )

        # Module (deeper level for testing depth)
        module = IndexItem(
            name="install_packages",
            type="module",
            path=Path("collections/my_collection/plugins/modules/install_packages.py"),
            namespace="my_namespace",
        )

        collection.children.append(role)
        role.children.append(module)
        return [collection]

    def test_ascii_tree_rendering(self, simple_tree):
        """T031: Test ASCII tree rendering with correct characters."""
        visualizer = TreeVisualizer()
        output = visualizer.render_tree(simple_tree)

        # Check for tree structure characters
        assert "my_collection" in output
        assert "├──" in output or "└──" in output  # Branch or last branch
        assert "webserver" in output
        assert "database" in output

    def test_unicode_tree_rendering(self, simple_tree):
        """T034: Test Unicode box-drawing characters."""
        visualizer = TreeVisualizer(use_unicode=True)
        output = visualizer.render_tree(simple_tree)

        # Check for Unicode box-drawing characters
        assert "my_collection" in output
        # Unicode box-drawing: ├──, └──, │
        assert any(char in output for char in ["├", "└", "│"])

    def test_ascii_fallback(self, simple_tree):
        """Test ASCII fallback when use_unicode=False."""
        visualizer = TreeVisualizer(use_unicode=False)
        output = visualizer.render_tree(simple_tree)

        # Should use ASCII characters
        assert "my_collection" in output
        # ASCII alternatives: +-- or |--
        assert any(chars in output for chars in ["├──", "└──", "|--", "+--"])

    def test_depth_limiting(self, deep_tree):
        """T039: Test depth limiting in tree rendering."""
        visualizer = TreeVisualizer(max_depth=1)
        output = visualizer.render_tree(deep_tree)

        # Should include collection and role (depth 0 and 1)
        assert "my_collection" in output
        assert "deploy" in output

        # Should not include module (depth 2, exceeds max_depth of 1)
        assert "install_packages" not in output

    def test_empty_tree(self):
        """Test rendering empty tree."""
        visualizer = TreeVisualizer()
        output = visualizer.render_tree([])

        assert output.strip() == ""

    def test_single_node(self):
        """Test rendering tree with single node."""
        single_node = [
            IndexItem(
                name="standalone_role",
                type="role",
                path=Path("roles/standalone"),
                namespace="my_namespace",
            )
        ]

        visualizer = TreeVisualizer()
        output = visualizer.render_tree(single_node)

        assert "standalone_role" in output
        # Single node should not have tree characters
        assert "├──" not in output
        assert "└──" not in output

    def test_multiple_root_nodes(self):
        """Test rendering tree with multiple root nodes."""
        roots = [
            IndexItem(
                name="collection1",
                type="collection",
                path=Path("collections/collection1"),
                namespace="ns1",
            ),
            IndexItem(
                name="collection2",
                type="collection",
                path=Path("collections/collection2"),
                namespace="ns2",
            ),
        ]

        visualizer = TreeVisualizer()
        output = visualizer.render_tree(roots)

        assert "collection1" in output
        assert "collection2" in output

    def test_description_rendering(self):
        """Test rendering node descriptions."""
        node = IndexItem(
            name="test_role",
            type="role",
            description="This is a test role for unit testing",
            path=Path("roles/test"),
            namespace="my_namespace",
        )

        visualizer = TreeVisualizer(show_description=True)
        output = visualizer.render_tree([node])

        assert "test_role" in output
        assert "This is a test role" in output

    def test_no_description_rendering(self):
        """Test rendering without descriptions."""
        node = IndexItem(
            name="test_role",
            type="role",
            description="This should not appear",
            path=Path("roles/test"),
            namespace="my_namespace",
        )

        visualizer = TreeVisualizer(show_description=False)
        output = visualizer.render_tree([node])

        assert "test_role" in output
        assert "This should not appear" not in output
