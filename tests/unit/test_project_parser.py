import pytest
import textwrap
from pathlib import Path
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


def test_project_parser_playbook_hosts_list_and_role_dict(tmp_path):
    pdir = tmp_path / "playbooks"
    pdir.mkdir()
    pb = pdir / "multi.yml"
    pb.write_text(textwrap.dedent("""
- name: Multi Playbook
  hosts:
    - webservers
    - db
  roles:
    - role: webserver
    - name: db
"""), encoding="utf-8")
    parser = ProjectParser()
    project = parser.parse(tmp_path)
    # Should detect the playbook and both hosts/roles
    assert any(p.name == "multi" for p in project.playbooks)
    pinfo = next(p for p in project.playbooks if p.name == "multi")
    assert "webservers" in pinfo.hosts
    assert "db" in pinfo.hosts
    assert "webserver" in pinfo.roles or "webserver" in pinfo.roles
    assert "db" in pinfo.roles


def test_project_parser_discovers_top_level_playbook(tmp_path):
        # Create playbook at project root
        pb = tmp_path / "site.yml"
        pb.write_text(
            "- name: Root Playbook\n  hosts: webservers\n  roles:\n    - webserver\n",
            encoding="utf-8",
        )
        parser = ProjectParser()
        project = parser.parse(tmp_path)
        assert any(p.name == "site" for p in project.playbooks)


def test_project_parser_inventory_merges_groups(tmp_path):
        # Create inventory dir with multiple files that must merge
        inv_dir = tmp_path / "inventory"
        inv_dir.mkdir()
        f1 = inv_dir / "hosts1.ini"
        f1.write_text("""
[webservers]
host1
""", encoding="utf-8")
        f2 = inv_dir / "hosts2.yml"
        f2.write_text("""
all:
    children:
        db:
            hosts:
                host1: {}
""", encoding="utf-8")
        parser = ProjectParser()
        project = parser.parse(tmp_path)
        # host1 should be present with both groups
        host1 = next((h for h in project.inventory if h.name == "host1"), None)
        assert host1 is not None
        assert set(host1.groups) == {"webservers", "db"}


def test_project_parser_monorepo_root_detection(tmp_path):
    # Create repo structure where project lives inside a subdir but ansible.cfg is in ancestor
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
    sub = repo / "subproject"
    sub.mkdir()
    # Call parser on subdirectory; expect it to detect the ancestor ansible.cfg and set project.name to 'repo'
    parser = ProjectParser()
    project = parser.parse(str(sub))
    assert project.name == repo.name
    assert Path(project.path).resolve() == repo.resolve()


def test_project_parser_respects_ansible_cfg_inventory_path(tmp_path):
    # Create ansible.cfg in repo and custom inventory path under repo
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
inventory = custom_inventory
""", encoding="utf-8")
    custom_inv = repo / "custom_inventory"
    custom_inv.mkdir()
    (custom_inv / "hosts.ini").write_text("""
[webservers]
hostcfg
""", encoding="utf-8")
    parser = ProjectParser()
    project = parser.parse(str(repo))
    # Inventory should be parsed from custom_inventory instead of default 'inventory'
    host_names = {h.name for h in project.inventory}
    assert "hostcfg" in host_names


def test_project_parser_respects_ansible_cfg_inventory_multiple_paths(tmp_path):
    # Create ansible.cfg in repo and custom inventory path under repo with multiple values
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
inventory = custom_inventory:other_inventory
""", encoding="utf-8")
    custom_inv = repo / "custom_inventory"
    custom_inv.mkdir()
    (custom_inv / "hosts.ini").write_text("""
[webservers]
hosta
""", encoding="utf-8")
    other_inv = repo / "other_inventory"
    other_inv.mkdir()
    (other_inv / "hosts2.ini").write_text("""
[db]
hostb
""", encoding="utf-8")
    parser = ProjectParser()
    project = parser.parse(str(repo))
    # Both hosts from custom_inventory and other_inventory should be present
    names = {h.name for h in project.inventory}
    assert "hosta" in names
    assert "hostb" in names


def test_project_parser_respects_ansible_cfg_inventory_file_path(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
inventory = custom_inventory/hosts.ini
""", encoding="utf-8")
    custom_inv = repo / "custom_inventory"
    custom_inv.mkdir()
    (custom_inv / "hosts.ini").write_text("""
[webservers]
filehost
""", encoding="utf-8")
    parser = ProjectParser()
    project = parser.parse(str(repo))
    names = {h.name for h in project.inventory}
    assert "filehost" in names


def test_project_parser_respects_ansible_cfg_roles_path_single(tmp_path):
    # Create repo and custom roles_path specified in ansible.cfg
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
roles_path = custom_roles
""", encoding="utf-8")
    custom_roles = repo / "custom_roles"
    custom_roles.mkdir()
    (custom_roles / "webserver").mkdir()
    parser = ProjectParser()
    project = parser.parse(str(repo))
    role_names = {r.name for r in project.roles}
    assert "webserver" in role_names


def test_project_parser_respects_ansible_cfg_roles_path_multiple(tmp_path):
    # Create repo and custom roles_path with multiple values
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
roles_path = custom_roles:other_roles
""", encoding="utf-8")
    custom_roles = repo / "custom_roles"
    custom_roles.mkdir()
    (custom_roles / "webserver").mkdir()
    other_roles = repo / "other_roles"
    other_roles.mkdir()
    (other_roles / "db").mkdir()
    parser = ProjectParser()
    project = parser.parse(str(repo))
    role_names = {r.name for r in project.roles}
    assert "webserver" in role_names
    assert "db" in role_names


def test_project_parser_respects_ansible_cfg_collections_path_single(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
collections_path = custom_collections
""", encoding="utf-8")
    custom_col = repo / "custom_collections" / "my_ns" / "my_coll"
    custom_col.mkdir(parents=True)
    parser = ProjectParser()
    project = parser.parse(str(repo))
    coll_names = {c.name for c in project.collections}
    assert "my_ns.my_coll" in coll_names


def test_project_parser_respects_ansible_cfg_collections_path_multiple(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("""
[defaults]
collections_path = custom_collections:other_collections
""", encoding="utf-8")
    custom_col = repo / "custom_collections" / "ns1" / "coll1"
    custom_col.mkdir(parents=True)
    other_col = repo / "other_collections" / "ns2" / "coll2"
    other_col.mkdir(parents=True)
    parser = ProjectParser()
    project = parser.parse(str(repo))
    coll_names = {c.name for c in project.collections}
    assert "ns1.coll1" in coll_names
    assert "ns2.coll2" in coll_names
