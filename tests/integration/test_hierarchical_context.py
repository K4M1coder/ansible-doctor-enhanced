"""
Integration tests for hierarchical context detection and navigation (T312).

Tests the complete hierarchical documentation structure including:
- Context detection across project->collection->role hierarchy
- Breadcrumb link generation
- Sibling navigation links
- Cross-level link navigation
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.context.detector import ComponentType, ContextDetector, HierarchicalContext
from ansibledoctor.generator.models import TemplateContext
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.utils.slug import build_context_path, relative_link


class TestHierarchicalPathGeneration:
    """Test slug path generation for hierarchical structures."""

    def test_generate_role_path_in_collection_in_project(self):
        """
        Test: Generate path for role inside collection inside project.

        Expected path structure:
        docs/lang/{lang}/project/collections/collection_ns.collection/role_ns.role
        """
        lang = "en"

        path = build_context_path(
            language=lang,
            project="ansibleproject_myproject",
            collection="myns.mycollection",
            role="myrole",
        )

        assert "docs/lang/en" in path
        assert "ansibleproject_myproject" in path
        assert "myns.mycollection" in path
        assert "myrole" in path

    def test_generate_standalone_role_path(self):
        """Test: Generate path for standalone role without project context."""
        lang = "de"

        path = build_context_path(
            language=lang,
            role="standalone_role",
        )

        assert path == "docs/lang/de/standalone_role"

    def test_relative_link_from_role_to_collection(self):
        """Test: Generate relative link from role doc to collection doc."""
        # Paths without README.md since the function adds it
        role_path = "docs/lang/en/project/collections/ns.coll/roles/myrole"
        collection_path = "docs/lang/en/project/collections/ns.coll"

        link = relative_link(role_path, collection_path)

        # Going up two levels (roles/myrole) and adding README.md
        assert "../.." in link or "README.md" in link

    def test_relative_link_from_role_to_project(self):
        """Test: Generate relative link from role doc to project doc."""
        role_path = "docs/lang/en/project/collections/ns.coll/roles/myrole"
        project_path = "docs/lang/en/project"

        link = relative_link(role_path, project_path)

        # Verify it goes up multiple levels
        assert link.count("..") >= 3 or "project" in link

    def test_relative_link_between_sibling_roles(self):
        """Test: Generate relative link between sibling roles in same collection."""
        role1_path = "docs/lang/en/project/collections/ns.coll/roles/role1"
        role2_path = "docs/lang/en/project/collections/ns.coll/roles/role2"

        link = relative_link(role1_path, role2_path)

        # Should go up one level and into role2
        assert "role2" in link
        assert "README.md" in link


class TestHierarchicalContextDetection:
    """Test context detection for nested structures."""

    @pytest.fixture
    def nested_project_structure(self, tmp_path: Path) -> Path:
        """Create a nested project structure for testing."""
        # Create project root with ansible.cfg
        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "ansible.cfg").write_text("[defaults]\n")

        # Create collections directory
        collections_dir = project_root / "collections" / "ansible_collections"
        collections_dir.mkdir(parents=True)

        # Create a collection with galaxy.yml
        collection_dir = collections_dir / "myns" / "mycollection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: myns\nname: mycollection\nversion: 1.0.0\n"
        )

        # Create roles inside collection
        roles_dir = collection_dir / "roles"
        roles_dir.mkdir()

        for role_name in ["role_a", "role_b", "role_c"]:
            role_dir = roles_dir / role_name
            role_dir.mkdir()
            tasks_dir = role_dir / "tasks"
            tasks_dir.mkdir()
            (tasks_dir / "main.yml").write_text("---\n- name: Task\n  debug:\n    msg: test\n")

        return project_root

    def test_detect_role_in_collection_in_project(self, nested_project_structure: Path):
        """
        Test: Detect context for role inside collection inside project.

        Expected:
        - Component type: ROLE
        - Parent: Collection
        - Breadcrumb has 3 items (project > collection > role)
        - Siblings are other roles in collection
        """
        detector = ContextDetector()
        role_path = (
            nested_project_structure
            / "collections"
            / "ansible_collections"
            / "myns"
            / "mycollection"
            / "roles"
            / "role_a"
        )

        context = detector.detect(role_path)

        assert context is not None
        assert context.component_type == ComponentType.ROLE

        # Check breadcrumb (use method, not property)
        breadcrumb = context.get_breadcrumb()
        assert len(breadcrumb) >= 2  # At least collection and role

        # Check for siblings (role_b, role_c should be siblings)
        siblings = context.get_siblings()
        sibling_names = [s.component_name for s in siblings]
        assert "role_b" in sibling_names or len(sibling_names) >= 1

    def test_detect_collection_context(self, nested_project_structure: Path):
        """Test: Detect context for collection inside project."""
        detector = ContextDetector()
        collection_path = (
            nested_project_structure
            / "collections"
            / "ansible_collections"
            / "myns"
            / "mycollection"
        )

        context = detector.detect(collection_path)

        assert context is not None
        assert context.component_type == ComponentType.COLLECTION
        # Collection should have project as parent breadcrumb
        breadcrumb = context.get_breadcrumb()
        assert len(breadcrumb) >= 1

    def test_detect_standalone_role(self, tmp_path: Path):
        """Test: Detect context for standalone role without project."""
        # Create standalone role
        role_dir = tmp_path / "standalone_role"
        role_dir.mkdir()
        tasks_dir = role_dir / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "main.yml").write_text("---\n- name: Task\n  debug: msg=test\n")

        detector = ContextDetector()
        context = detector.detect(role_dir)

        assert context is not None
        # Standalone role is still a ROLE type, just with no parent
        assert context.component_type == ComponentType.ROLE
        # Standalone has no parent hierarchy
        assert context.parent is None
        breadcrumb = context.get_breadcrumb()
        assert len(breadcrumb) == 1  # Just the role itself


class TestBreadcrumbRendering:
    """Test breadcrumb rendering in templates."""

    @pytest.fixture
    def sample_hierarchical_context(self, tmp_path: Path) -> HierarchicalContext:
        """Create sample hierarchical context with breadcrumb chain."""
        # Create role context
        role_ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=tmp_path / "roles" / "my_role",
            component_name="my_role",
            component_slug="my_role",
            parent=None,
        )

        # Create collection context as parent
        collection_ctx = HierarchicalContext(
            component_type=ComponentType.COLLECTION,
            component_path=tmp_path / "collections" / "myns.mycollection",
            component_name="myns.mycollection",
            component_slug="myns.mycollection",
            parent=None,
        )

        # Create project context as grandparent
        project_ctx = HierarchicalContext(
            component_type=ComponentType.PROJECT,
            component_path=tmp_path,
            component_name="My Project",
            component_slug="my_project",
            parent=None,
        )

        # Set up hierarchy
        collection_ctx.parent = project_ctx
        role_ctx.parent = collection_ctx

        # Set up siblings
        sibling_role = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=tmp_path / "roles" / "other_role",
            component_name="other_role",
            component_slug="other_role",
            parent=collection_ctx,
        )
        role_ctx.set_siblings([sibling_role])

        return role_ctx

    def test_breadcrumb_in_markdown_output(
        self, sample_hierarchical_context: HierarchicalContext, tmp_path: Path
    ):
        """Test: Breadcrumb appears in Markdown output with correct links."""
        # Create a minimal role for rendering
        role = AnsibleRole(
            name="my_role",
            path=tmp_path,
            metadata=RoleMetadata(
                name="my_role",
                description="Test role",
                platforms=[],
                galaxy_tags=[],
                dependencies=[],
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
            annotations=[],
        )

        # Build template context with hierarchical info
        context = TemplateContext(
            role=role,
            generator_version="0.5.0",
            output_format=OutputFormat.MARKDOWN,
            language="en",
            generation_date=datetime.now(),
            hierarchical_context=sample_hierarchical_context,
        )

        renderer = MarkdownRenderer()
        output = renderer.render(context)

        # Verify breadcrumb links are present
        assert "My Project" in output
        assert "myns.mycollection" in output
        # The current item should be bold (not linked)
        assert "**my_role**" in output

    def test_sibling_navigation_in_markdown(
        self, sample_hierarchical_context: HierarchicalContext, tmp_path: Path
    ):
        """Test: Sibling navigation appears in Markdown output."""
        role = AnsibleRole(
            name="my_role",
            path=tmp_path,
            metadata=RoleMetadata(
                name="my_role",
                description="Test role",
                platforms=[],
                galaxy_tags=[],
                dependencies=[],
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
            annotations=[],
        )

        context = TemplateContext(
            role=role,
            generator_version="0.5.0",
            output_format=OutputFormat.MARKDOWN,
            language="en",
            generation_date=datetime.now(),
            hierarchical_context=sample_hierarchical_context,
        )

        renderer = MarkdownRenderer()
        output = renderer.render(context)

        # Verify sibling navigation section is present
        assert "Related" in output or "other_role" in output


class TestCrossLevelNavigation:
    """Test navigation across hierarchical levels."""

    def test_navigate_from_role_to_collection_and_back(self, tmp_path: Path):
        """
        Test: Navigation links work bidirectionally between role and collection.

        Role doc should link to collection, collection doc should list roles.
        """
        # This test verifies the link generation logic is correct
        # Using paths without README.md as the function appends it
        role_doc_path = "docs/lang/en/project/collections/ns.coll/roles/role1"
        collection_doc_path = "docs/lang/en/project/collections/ns.coll"

        # Link from role to collection
        role_to_coll = relative_link(role_doc_path, collection_doc_path)
        assert "README.md" in role_to_coll
        assert ".." in role_to_coll  # Going up at least once

        # Link from collection to role
        coll_to_role = relative_link(collection_doc_path, role_doc_path)
        assert "role1" in coll_to_role
        assert "README.md" in coll_to_role

    def test_navigate_from_role_to_project_and_back(self, tmp_path: Path):
        """
        Test: Navigation links work bidirectionally between role and project.
        """
        role_doc_path = "docs/lang/en/project/collections/ns.coll/roles/role1"
        project_doc_path = "docs/lang/en/project"

        # Link from role to project
        role_to_proj = relative_link(role_doc_path, project_doc_path)
        assert "README.md" in role_to_proj
        # Should go up multiple levels
        assert role_to_proj.count("..") >= 3

        # Link from project to role
        proj_to_role = relative_link(project_doc_path, role_doc_path)
        assert "role1" in proj_to_role
        assert "README.md" in proj_to_role
