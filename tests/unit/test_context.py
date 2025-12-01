"""Unit tests for hierarchical context detection.

These tests follow TDD (Test-Driven Development) - tests are written first,
then implementation follows to make them pass.

Feature 007: Hierarchical Context Detection
Task T309: Write unit tests for context detector
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from ansibledoctor.context.detector import (
    ComponentType,
    ContextDetector,
    HierarchicalContext,
)


class TestComponentType:
    """Tests for ComponentType enum."""

    def test_component_types_exist(self):
        """All component types should be defined."""
        assert ComponentType.PROJECT is not None
        assert ComponentType.COLLECTION is not None
        assert ComponentType.ROLE is not None
        assert ComponentType.STANDALONE is not None


class TestHierarchicalContext:
    """Tests for HierarchicalContext data class."""

    def test_create_standalone_context(self):
        """Create a standalone context with no parent."""
        ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=Path("/path/to/role"),
            component_name="webserver",
            component_slug="role_ns.webserver",
        )
        assert ctx.component_type == ComponentType.ROLE
        assert ctx.parent is None
        assert ctx.is_standalone

    def test_create_nested_context(self):
        """Create a role context with parent collection."""
        collection_ctx = HierarchicalContext(
            component_type=ComponentType.COLLECTION,
            component_path=Path("/path/to/collection"),
            component_name="my_namespace.my_collection",
            component_slug="collection_my-namespace.my-collection",
        )
        role_ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=Path("/path/to/collection/roles/webserver"),
            component_name="webserver",
            component_slug="role_my_namespace.webserver",
            parent=collection_ctx,
        )
        assert role_ctx.parent == collection_ctx
        assert not role_ctx.is_standalone

    def test_breadcrumb_for_standalone(self):
        """Standalone component should have single-item breadcrumb."""
        ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=Path("/path/to/role"),
            component_name="webserver",
            component_slug="role_ns.webserver",
        )
        breadcrumb = ctx.get_breadcrumb()
        assert len(breadcrumb) == 1
        assert breadcrumb[0].name == "webserver"
        assert breadcrumb[0].slug == "role_ns.webserver"

    def test_breadcrumb_for_role_in_collection(self):
        """Role in collection should have two-item breadcrumb."""
        collection_ctx = HierarchicalContext(
            component_type=ComponentType.COLLECTION,
            component_path=Path("/path/to/collection"),
            component_name="my_collection",
            component_slug="collection_ns.my-collection",
        )
        role_ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=Path("/path/to/collection/roles/webserver"),
            component_name="webserver",
            component_slug="role_ns.webserver",
            parent=collection_ctx,
        )
        breadcrumb = role_ctx.get_breadcrumb()
        assert len(breadcrumb) == 2
        assert breadcrumb[0].name == "my_collection"
        assert breadcrumb[1].name == "webserver"

    def test_breadcrumb_for_full_hierarchy(self):
        """Role in collection in project should have three-item breadcrumb."""
        project_ctx = HierarchicalContext(
            component_type=ComponentType.PROJECT,
            component_path=Path("/path/to/project"),
            component_name="My Project",
            component_slug="ansibleproject_my-project",
        )
        collection_ctx = HierarchicalContext(
            component_type=ComponentType.COLLECTION,
            component_path=Path("/path/to/project/collections/my_collection"),
            component_name="my_collection",
            component_slug="collection_ns.my-collection",
            parent=project_ctx,
        )
        role_ctx = HierarchicalContext(
            component_type=ComponentType.ROLE,
            component_path=Path("/path/to/project/collections/my_collection/roles/webserver"),
            component_name="webserver",
            component_slug="role_ns.webserver",
            parent=collection_ctx,
        )
        breadcrumb = role_ctx.get_breadcrumb()
        assert len(breadcrumb) == 3
        assert breadcrumb[0].name == "My Project"
        assert breadcrumb[1].name == "my_collection"
        assert breadcrumb[2].name == "webserver"


class TestContextDetector:
    """Tests for ContextDetector class."""

    def test_detect_standalone_role(self, tmp_path: Path):
        """Role with no parent markers should be standalone."""
        role_dir = tmp_path / "standalone_role"
        role_dir.mkdir()
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text("---\n- name: Test\n  debug: msg=test\n")
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text("---\ngalaxy_info:\n  role_name: standalone_role\n")

        detector = ContextDetector()
        ctx = detector.detect(role_dir)

        assert ctx.component_type == ComponentType.ROLE
        assert ctx.is_standalone
        assert ctx.parent is None

    def test_detect_role_in_collection(self, tmp_path: Path):
        """Role inside a collection should have collection as parent."""
        # Create collection structure
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )

        # Create role inside collection
        role_dir = collection_dir / "roles" / "webserver"
        role_dir.mkdir(parents=True)
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text("---\n- name: Test\n  debug: msg=test\n")

        detector = ContextDetector()
        ctx = detector.detect(role_dir)

        assert ctx.component_type == ComponentType.ROLE
        assert not ctx.is_standalone
        assert ctx.parent is not None
        assert ctx.parent.component_type == ComponentType.COLLECTION
        assert "my_namespace" in ctx.parent.component_name or "my_collection" in ctx.parent.component_name

    def test_detect_collection_in_project(self, tmp_path: Path):
        """Collection inside a project should have project as parent."""
        # Create project structure
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]\nroles_path = roles\n")
        (project_dir / "playbooks").mkdir()

        # Create collection inside project
        collection_dir = project_dir / "collections" / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )

        detector = ContextDetector()
        ctx = detector.detect(collection_dir)

        assert ctx.component_type == ComponentType.COLLECTION
        assert not ctx.is_standalone
        assert ctx.parent is not None
        assert ctx.parent.component_type == ComponentType.PROJECT

    def test_detect_role_in_collection_in_project(self, tmp_path: Path):
        """Full hierarchy: role > collection > project."""
        # Create project structure
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]\nroles_path = roles\n")

        # Create collection inside project
        collection_dir = project_dir / "collections" / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )

        # Create role inside collection
        role_dir = collection_dir / "roles" / "webserver"
        role_dir.mkdir(parents=True)
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text("---\n- name: Test\n  debug: msg=test\n")

        detector = ContextDetector()
        ctx = detector.detect(role_dir)

        assert ctx.component_type == ComponentType.ROLE
        assert ctx.parent is not None
        assert ctx.parent.component_type == ComponentType.COLLECTION
        assert ctx.parent.parent is not None
        assert ctx.parent.parent.component_type == ComponentType.PROJECT

    def test_max_depth_limit(self, tmp_path: Path):
        """Should stop searching after 3 levels."""
        # Create very deep structure with project 5 levels up
        deep_dir = tmp_path / "l1" / "l2" / "l3" / "l4" / "l5" / "role"
        deep_dir.mkdir(parents=True)
        (deep_dir / "tasks").mkdir()
        (deep_dir / "tasks" / "main.yml").write_text("---\n- name: Test\n  debug: msg=test\n")

        # Put project marker 5 levels up (beyond 3-level limit)
        (tmp_path / "ansible.cfg").write_text("[defaults]\n")

        detector = ContextDetector(max_depth=3)
        ctx = detector.detect(deep_dir)

        # Should not find the project because it's beyond max depth
        assert ctx.is_standalone or (ctx.parent is None)

    def test_detect_project_directly(self, tmp_path: Path):
        """Detecting a project directory should return project context."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]\nroles_path = roles\n")
        (project_dir / "playbooks").mkdir()
        (project_dir / "playbooks" / "site.yml").write_text("---\n- hosts: all\n")

        detector = ContextDetector()
        ctx = detector.detect(project_dir)

        assert ctx.component_type == ComponentType.PROJECT
        assert ctx.is_standalone  # Projects have no parent

    def test_detect_collection_directly(self, tmp_path: Path):
        """Detecting a collection directory should return collection context."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )

        detector = ContextDetector()
        ctx = detector.detect(collection_dir)

        assert ctx.component_type == ComponentType.COLLECTION

    def test_caching_within_session(self, tmp_path: Path):
        """Parent detection should be cached within a session."""
        # Create structure
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )
        role1_dir = collection_dir / "roles" / "role1"
        role1_dir.mkdir(parents=True)
        (role1_dir / "tasks").mkdir()
        (role1_dir / "tasks" / "main.yml").write_text("---\n")
        role2_dir = collection_dir / "roles" / "role2"
        role2_dir.mkdir(parents=True)
        (role2_dir / "tasks").mkdir()
        (role2_dir / "tasks" / "main.yml").write_text("---\n")

        detector = ContextDetector()
        ctx1 = detector.detect(role1_dir)
        ctx2 = detector.detect(role2_dir)

        # Both roles should reference the same cached collection parent
        assert ctx1.parent is ctx2.parent


class TestContextDetectorNoParent:
    """Tests for --no-parent / detect_parent: false behavior."""

    def test_no_parent_flag_skips_detection(self, tmp_path: Path):
        """With no_parent=True, should return standalone context immediately."""
        # Create role in collection
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )
        role_dir = collection_dir / "roles" / "webserver"
        role_dir.mkdir(parents=True)
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text("---\n")

        detector = ContextDetector(detect_parent=False)
        ctx = detector.detect(role_dir)

        # Should be standalone despite having a parent collection
        assert ctx.is_standalone
        assert ctx.parent is None


class TestSiblingDiscovery:
    """Tests for discovering sibling components."""

    def test_discover_sibling_roles(self, tmp_path: Path):
        """Should discover other roles in the same collection."""
        collection_dir = tmp_path / "my_namespace" / "my_collection"
        collection_dir.mkdir(parents=True)
        (collection_dir / "galaxy.yml").write_text(
            "namespace: my_namespace\nname: my_collection\nversion: 1.0.0\n"
        )

        # Create multiple roles
        for role_name in ["webserver", "database", "cache"]:
            role_dir = collection_dir / "roles" / role_name
            role_dir.mkdir(parents=True)
            (role_dir / "tasks").mkdir()
            (role_dir / "tasks" / "main.yml").write_text("---\n")

        detector = ContextDetector()
        ctx = detector.detect(collection_dir / "roles" / "webserver")

        siblings = ctx.get_siblings()
        sibling_names = [s.component_name for s in siblings]

        assert "database" in sibling_names
        assert "cache" in sibling_names
        assert "webserver" not in sibling_names  # Current component not in siblings

    def test_discover_sibling_collections(self, tmp_path: Path):
        """Should discover other collections in the same project."""
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        (project_dir / "ansible.cfg").write_text("[defaults]\n")

        # Create multiple collections
        for coll_name in ["web_collection", "db_collection", "util_collection"]:
            coll_dir = project_dir / "collections" / "my_ns" / coll_name
            coll_dir.mkdir(parents=True)
            (coll_dir / "galaxy.yml").write_text(
                f"namespace: my_ns\nname: {coll_name}\nversion: 1.0.0\n"
            )

        detector = ContextDetector()
        ctx = detector.detect(project_dir / "collections" / "my_ns" / "web_collection")

        siblings = ctx.get_siblings()
        sibling_names = [s.component_name for s in siblings]

        assert "db_collection" in sibling_names or "my_ns.db_collection" in sibling_names
        assert "util_collection" in sibling_names or "my_ns.util_collection" in sibling_names
