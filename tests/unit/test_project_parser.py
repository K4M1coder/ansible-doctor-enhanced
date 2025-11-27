import pytest
from ansibledoctor.parser.project_parser import ProjectParser
from ansibledoctor.models.project import Project


def test_project_parser_empty_dir(tmp_path):
    parser = ProjectParser()
    project = parser.parse(tmp_path)

    assert isinstance(project, Project)
    assert project.name == '' or project.name is None
    assert project.roles == []
    assert project.collections == []
    assert project.playbooks == []


def test_project_parser_discovers_roles_and_collections(tmp_path):
    # Create roles
    roles_dir = tmp_path / "roles"
    roles_dir.mkdir()
    (roles_dir / "webserver").mkdir()
    (roles_dir / "db").mkdir()

    # Create collections using both layout variants
    collections_dir = tmp_path / "collections"
    collections_dir.mkdir()
    # Variant A: collections/ansible_collections/<namespace>/<collection>
    ans_col = collections_dir / "ansible_collections" / "my_ns" / "my_coll"
    ans_col.mkdir(parents=True)
    # Variant B: collections/<namespace>/<collection>
    std_col = collections_dir / "other_ns" / "other_coll"
    std_col.mkdir(parents=True)

    parser = ProjectParser()
    project = parser.parse(tmp_path)

    # Roles discovered
    role_names = {r.name for r in project.roles}
    assert "webserver" in role_names
    assert "db" in role_names

    # Collections discovered
    coll_names = {c.name for c in project.collections}
    assert "my_ns.my_coll" in coll_names
    assert "other_ns.other_coll" in coll_names
