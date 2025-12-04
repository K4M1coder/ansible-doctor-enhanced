"""Tests for deep parsing (T331-T335).

Verify that when deep_parse=True, ProjectParser.parse() performs role/collection parsing
using RoleParser and CollectionParser and populates project.parsed_roles and project.parsed_collections.
"""

from pathlib import Path
import pytest

from ansibledoctor.parser.project_parser import ProjectParser
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.models.collection import AnsibleCollection


ROLE_META_YML = """
---
# meta/main.yml
galaxy_info:
  author: Demo Author
  description: Demo role
  license: MIT
  min_ansible_version: 2.9
  platforms: []
"""

ROLE_TASKS_YML = """
- name: demo task
  debug:
    msg: "hello"
"""

GALAXY_YML = """
namespace: demo_namespace
name: demo_collection
version: 1.0.0
authors:
  - Demo Author <demo@example.com>
dependencies: {}
"""


def create_role_structure(base: Path, role_name: str) -> None:
    role_dir = base / "roles" / role_name
    role_meta_dir = role_dir / "meta"
    tasks_dir = role_dir / "tasks"
    role_meta_dir.mkdir(parents=True)
    tasks_dir.mkdir(parents=True)
    (role_meta_dir / "main.yml").write_text(ROLE_META_YML)
    (tasks_dir / "main.yml").write_text(ROLE_TASKS_YML)


def create_collection_structure(base: Path, ns: str, coll: str) -> None:
    collection_dir = base / "collections" / "ansible_collections" / ns / coll
    collection_dir.mkdir(parents=True)
    # galaxy.yml
    (collection_dir / "galaxy.yml").write_text(GALAXY_YML)
    # add a role inside the collection
    roles_dir = collection_dir / "roles"
    roles_dir.mkdir(parents=True)
    inner_role_dir = roles_dir / "coll_role"
    inner_role_dir.mkdir(parents=True)
    (inner_role_dir / "meta").mkdir(parents=True)
    (inner_role_dir / "meta" / "main.yml").write_text(ROLE_META_YML)


class TestProjectDeepParsing:
    def test_deep_parse_false(self, tmp_path: Path) -> None:
        """Default parse should not populate parsed_roles or parsed_collections."""
        # Arrange
        create_role_structure(tmp_path, "role_a")
        create_collection_structure(tmp_path, "demo_namespace", "demo_collection")

        # Act
        parser = ProjectParser()
        project = parser.parse(str(tmp_path))

        # Assert
        assert project.parsed_roles == []
        assert project.parsed_collections == []

    def test_deep_parse_true(self, tmp_path: Path) -> None:
        """When deep_parse=True, ProjectParser populates parsed_roles and parsed_collections."""
        # Arrange
        create_role_structure(tmp_path, "role_a")
        create_collection_structure(tmp_path, "demo_namespace", "demo_collection")

        # Act
        parser = ProjectParser()
        project = parser.parse(str(tmp_path), deep_parse=True)

        # Assert
        # At least one parsed role (project's role)
        assert isinstance(project.parsed_roles, list)
        assert any(isinstance(r, AnsibleRole) for r in project.parsed_roles)

        # At least one parsed collection
        assert isinstance(project.parsed_collections, list)
        assert any(isinstance(c, AnsibleCollection) for c in project.parsed_collections)
