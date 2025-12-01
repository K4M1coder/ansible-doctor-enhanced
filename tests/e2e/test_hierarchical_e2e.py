"""
End-to-end test for hierarchical context across project->collection->role (T314).

This test verifies that documentation generation for a full project structure
with nested collections and roles produces correct navigation links.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.context.detector import ComponentType, ContextDetector
from ansibledoctor.generator.models import TemplateContext
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.utils.slug import build_context_path, relative_link


class TestHierarchicalE2E:
    """End-to-end tests for hierarchical documentation generation."""

    @pytest.fixture
    def full_project_structure(self, tmp_path: Path) -> Path:
        """
        Create a complete project structure with nested collections and roles.

        Structure:
        my_project/
        ├── ansible.cfg
        ├── playbooks/
        │   └── site.yml
        ├── roles/
        │   ├── common/
        │   │   └── tasks/main.yml
        │   └── webserver/
        │       └── tasks/main.yml
        └── collections/
            └── myns/
                └── infra/
                    ├── galaxy.yml
                    └── roles/
                        ├── database/
                        │   └── tasks/main.yml
                        └── cache/
                            └── tasks/main.yml
        """
        project = tmp_path / "my_project"
        project.mkdir()

        # ansible.cfg
        (project / "ansible.cfg").write_text(
            "[defaults]\nroles_path = roles\ncollections_path = collections\n"
        )

        # Playbooks
        playbooks = project / "playbooks"
        playbooks.mkdir()
        (playbooks / "site.yml").write_text(
            "---\n- name: Site playbook\n  hosts: all\n  roles:\n    - common\n"
        )

        # Project-level roles
        roles = project / "roles"
        roles.mkdir()

        common = roles / "common"
        common.mkdir()
        (common / "tasks").mkdir()
        (common / "tasks" / "main.yml").write_text(
            "---\n- name: Common task\n  debug: msg=common\n"
        )

        webserver = roles / "webserver"
        webserver.mkdir()
        (webserver / "tasks").mkdir()
        (webserver / "tasks" / "main.yml").write_text(
            "---\n- name: Webserver task\n  debug: msg=webserver\n"
        )

        # Collection with roles
        collections = project / "collections" / "myns" / "infra"
        collections.mkdir(parents=True)
        (collections / "galaxy.yml").write_text(
            "---\nnamespace: myns\nname: infra\nversion: 1.0.0\n"
            "authors: [test]\ndescription: Infrastructure collection\n"
        )

        coll_roles = collections / "roles"
        coll_roles.mkdir()

        database = coll_roles / "database"
        database.mkdir()
        (database / "tasks").mkdir()
        (database / "tasks" / "main.yml").write_text(
            "---\n- name: Database task\n  debug: msg=database\n"
        )

        cache = coll_roles / "cache"
        cache.mkdir()
        (cache / "tasks").mkdir()
        (cache / "tasks" / "main.yml").write_text(
            "---\n- name: Cache task\n  debug: msg=cache\n"
        )

        return project

    def test_detect_all_hierarchy_levels(self, full_project_structure: Path):
        """Test: ContextDetector correctly identifies all hierarchy levels."""
        detector = ContextDetector()

        # Test project detection
        project_ctx = detector.detect(full_project_structure)
        assert project_ctx is not None
        assert project_ctx.component_type == ComponentType.PROJECT
        assert project_ctx.parent is None

        # Test project-level role detection
        common_role = full_project_structure / "roles" / "common"
        role_ctx = detector.detect(common_role)
        assert role_ctx is not None
        assert role_ctx.component_type == ComponentType.ROLE
        # Role inside project should have project as parent
        assert role_ctx.parent is not None
        assert role_ctx.parent.component_type == ComponentType.PROJECT

        # Test collection detection
        collection = (
            full_project_structure / "collections" / "myns" / "infra"
        )
        coll_ctx = detector.detect(collection)
        assert coll_ctx is not None
        assert coll_ctx.component_type == ComponentType.COLLECTION
        # Collection inside project should have project as parent
        assert coll_ctx.parent is not None
        assert coll_ctx.parent.component_type == ComponentType.PROJECT

        # Test collection role detection
        db_role = collection / "roles" / "database"
        db_ctx = detector.detect(db_role)
        assert db_ctx is not None
        assert db_ctx.component_type == ComponentType.ROLE
        # Role inside collection should have collection as parent
        assert db_ctx.parent is not None
        assert db_ctx.parent.component_type == ComponentType.COLLECTION
        # Collection should have project as grandparent
        assert db_ctx.parent.parent is not None
        assert db_ctx.parent.parent.component_type == ComponentType.PROJECT

    def test_breadcrumb_chain_complete(self, full_project_structure: Path):
        """Test: Breadcrumb chain is complete from role to project."""
        detector = ContextDetector()

        # Get context for deeply nested role
        collection = (
            full_project_structure / "collections" / "myns" / "infra"
        )
        db_role = collection / "roles" / "database"
        db_ctx = detector.detect(db_role)

        breadcrumb = db_ctx.get_breadcrumb()

        # Should have 3 items: project -> collection -> role
        assert len(breadcrumb) == 3
        assert breadcrumb[0].component_type == ComponentType.PROJECT
        assert breadcrumb[1].component_type == ComponentType.COLLECTION
        assert breadcrumb[2].component_type == ComponentType.ROLE

        # Verify names
        assert breadcrumb[0].name == "my_project"
        assert "myns" in breadcrumb[1].name and "infra" in breadcrumb[1].name
        assert breadcrumb[2].name == "database"

    def test_sibling_discovery_at_each_level(self, full_project_structure: Path):
        """Test: Siblings are discovered at each hierarchy level."""
        detector = ContextDetector()

        # Test project-level role siblings
        common_role = full_project_structure / "roles" / "common"
        common_ctx = detector.detect(common_role)
        siblings = common_ctx.get_siblings()

        # common and webserver are siblings
        sibling_names = [s.component_name for s in siblings]
        assert "webserver" in sibling_names

        # Test collection role siblings
        collection = (
            full_project_structure / "collections" / "myns" / "infra"
        )
        db_role = collection / "roles" / "database"
        db_ctx = detector.detect(db_role)
        db_siblings = db_ctx.get_siblings()

        # database and cache are siblings
        db_sibling_names = [s.component_name for s in db_siblings]
        assert "cache" in db_sibling_names

    def test_documentation_path_generation(self, full_project_structure: Path):
        """Test: Documentation paths follow hierarchical slug pattern."""
        # Project docs path
        project_path = build_context_path(
            language="en",
            project="ansibleproject_my_project",
        )
        assert project_path == "docs/lang/en/ansibleproject_my_project"

        # Collection docs path under project
        collection_path = build_context_path(
            language="en",
            project="ansibleproject_my_project",
            collection="collection_myns.infra",
        )
        assert "ansibleproject_my_project" in collection_path
        assert "collections" in collection_path
        assert "collection_myns.infra" in collection_path

        # Role docs path under collection under project
        role_path = build_context_path(
            language="en",
            project="ansibleproject_my_project",
            collection="collection_myns.infra",
            role="role_database",
        )
        assert "ansibleproject_my_project" in role_path
        assert "collections" in role_path
        assert "collection_myns.infra" in role_path
        assert "role_database" in role_path

    def test_navigation_links_bidirectional(self, full_project_structure: Path):
        """Test: Navigation links work bidirectionally between levels."""
        # Build paths
        project_path = "docs/lang/en/ansibleproject_my_project"
        collection_path = (
            "docs/lang/en/ansibleproject_my_project/collections/collection_myns.infra"
        )
        role_path = (
            "docs/lang/en/ansibleproject_my_project/collections/"
            "collection_myns.infra/roles/role_database"
        )

        # Role -> Collection link
        role_to_coll = relative_link(role_path, collection_path)
        assert ".." in role_to_coll
        assert role_to_coll.endswith("README.md")

        # Role -> Project link
        role_to_proj = relative_link(role_path, project_path)
        assert ".." in role_to_proj
        # Should go up multiple levels
        assert role_to_proj.count("..") >= 3

        # Collection -> Project link
        coll_to_proj = relative_link(collection_path, project_path)
        assert ".." in coll_to_proj
        assert coll_to_proj.endswith("README.md")

        # Collection -> Role link (downward)
        coll_to_role = relative_link(collection_path, role_path)
        assert "roles" in coll_to_role
        assert "role_database" in coll_to_role

    def test_full_render_with_hierarchy(self, full_project_structure: Path):
        """Test: Full documentation render includes hierarchy navigation."""
        detector = ContextDetector()

        # Get context for collection role
        collection = (
            full_project_structure / "collections" / "myns" / "infra"
        )
        db_role_path = collection / "roles" / "database"
        hier_ctx = detector.detect(db_role_path)

        # Create role model for rendering
        role = AnsibleRole(
            name="database",
            path=db_role_path,
            metadata=RoleMetadata(
                name="database",
                description="Database role for infrastructure",
                platforms=[],
                galaxy_tags=["database", "postgresql"],
                dependencies=[],
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
            annotations=[],
        )

        # Create template context with hierarchical info
        context = TemplateContext(
            role=role,
            generator_version="0.5.0",
            output_format=OutputFormat.MARKDOWN,
            language="en",
            generation_date=datetime.now(),
            hierarchical_context=hier_ctx,
        )

        # Render
        renderer = MarkdownRenderer()
        output = renderer.render(context)

        # Verify breadcrumb elements are present
        assert "my_project" in output
        assert "myns" in output or "infra" in output
        assert "database" in output

        # Verify the role content is present
        assert "Database role for infrastructure" in output

    def test_standalone_role_has_minimal_breadcrumb(self, tmp_path: Path):
        """Test: Standalone role (no project/collection) has minimal breadcrumb."""
        # Create standalone role
        role_dir = tmp_path / "standalone_role"
        role_dir.mkdir()
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text(
            "---\n- name: Standalone task\n  debug: msg=standalone\n"
        )

        detector = ContextDetector()
        ctx = detector.detect(role_dir)

        assert ctx is not None
        assert ctx.component_type == ComponentType.ROLE
        assert ctx.parent is None

        breadcrumb = ctx.get_breadcrumb()
        assert len(breadcrumb) == 1
        assert breadcrumb[0].name == "standalone_role"

    def test_standalone_collection_breadcrumb(self, tmp_path: Path):
        """Test: Standalone collection has correct breadcrumb."""
        # Create standalone collection
        coll_dir = tmp_path / "my_collection"
        coll_dir.mkdir()
        (coll_dir / "galaxy.yml").write_text(
            "---\nnamespace: testns\nname: testcoll\nversion: 1.0.0\n"
            "authors: [test]\n"
        )

        # Add a role to the collection
        roles = coll_dir / "roles" / "myrole"
        roles.mkdir(parents=True)
        (roles / "tasks").mkdir()
        (roles / "tasks" / "main.yml").write_text(
            "---\n- name: Collection role task\n  debug: msg=test\n"
        )

        detector = ContextDetector()

        # Collection context
        coll_ctx = detector.detect(coll_dir)
        assert coll_ctx.component_type == ComponentType.COLLECTION
        assert coll_ctx.parent is None

        coll_breadcrumb = coll_ctx.get_breadcrumb()
        assert len(coll_breadcrumb) == 1

        # Role inside standalone collection
        role_ctx = detector.detect(roles)
        assert role_ctx.component_type == ComponentType.ROLE
        assert role_ctx.parent is not None
        assert role_ctx.parent.component_type == ComponentType.COLLECTION

        role_breadcrumb = role_ctx.get_breadcrumb()
        assert len(role_breadcrumb) == 2
