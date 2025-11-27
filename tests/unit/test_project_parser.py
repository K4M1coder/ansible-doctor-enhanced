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


def test_project_parser_name_read_from_ansible_cfg(tmp_path):
    (tmp_path / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
    parser = ProjectParser()
    project = parser.parse(tmp_path)
    # If ansible.cfg is present, parser sets name to the directory's basename
    assert project.name == tmp_path.name


def test_project_parser_parses_ini_inventory(tmp_path):
        inv_dir = tmp_path / "inventory"
        inv_dir.mkdir()
        inv_file = inv_dir / "hosts.ini"
        inv_file.write_text("""
[webservers]
host1 ansible_host=1.2.3.4
host2

[db]
db1
""", encoding="utf-8")

        parser = ProjectParser()
        project = parser.parse(tmp_path)
        host_names = {h.name for h in project.inventory}
        assert "host1" in host_names
        assert "host2" in host_names
        assert "db1" in host_names


def test_project_parser_parses_yaml_inventory(tmp_path):
        inv_dir = tmp_path / "inventory"
        inv_dir.mkdir()
        inv_file = inv_dir / "hosts.yml"
        inv_file.write_text(
                """
all:
    children:
        webservers:
            hosts:
                hosta:
                    ansible_host: 1.2.3.4
                hostb: {}
""",
                encoding="utf-8",
        )
        parser = ProjectParser()
        project = parser.parse(tmp_path)
        host_names = {h.name for h in project.inventory}
        assert "hosta" in host_names
        assert "hostb" in host_names


def test_project_parser_discovers_playbooks(tmp_path):
        # Create a simple playbooks folder with one playbook
        pdir = tmp_path / "playbooks"
        pdir.mkdir()
        pb = pdir / "site.yml"
        pb.write_text(
            """
    - name: Site Playbook
      hosts: webservers
      roles:
        - webserver
    """,
            encoding="utf-8",
        )
        parser = ProjectParser()
        project = parser.parse(tmp_path)
        assert len(project.playbooks) == 1
        pb_info = project.playbooks[0]
        assert "webservers" in pb_info.hosts
        assert "webserver" in pb_info.roles
