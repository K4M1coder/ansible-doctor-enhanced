import textwrap
from pathlib import Path

from ansibledoctor.parser.inventory_parser import (
    parse_ini_inventory,
    parse_inventory_dir,
    parse_yaml_inventory,
)


def test_parse_ini_inventory_group_parsing(tmp_path):
    inv_file = tmp_path / "hosts.ini"
    inv_file.write_text(
        textwrap.dedent(
            """
    [webservers]
    host1 ansible_host=1.2.3.4
    host2

    [db]
    db1
    """
        ),
        encoding="utf-8",
    )

    parsed = list(parse_ini_inventory(inv_file))
    names = {item.name for item in parsed}
    assert "host1" in names
    assert "host2" in names
    assert "db1" in names
    # check groups
    host1 = next(i for i in parsed if i.name == "host1")
    assert "webservers" in host1.groups


def test_parse_yaml_inventory_children_and_top_hosts(tmp_path):
    inv_file = tmp_path / "hosts.yml"
    inv_file.write_text(
        textwrap.dedent(
            """
    all:
      children:
        webservers:
          hosts:
            hosta:
              ansible_host: 1.2.3.4
            hostb: {}
      hosts:
        hosttop: {}
    """
        ),
        encoding="utf-8",
    )

    parsed = list(parse_yaml_inventory(inv_file))
    names = {item.name for item in parsed}
    assert "hosta" in names
    assert "hostb" in names
    assert "hosttop" in names
    hosta = next(i for i in parsed if i.name == "hosta")
    assert "webservers" in hosta.groups


def test_parse_inventory_dir_merges_groups_across_files(tmp_path):
    inv_dir = tmp_path / "inventory"
    inv_dir.mkdir()
    f1 = inv_dir / "hosts1.ini"
    f1.write_text(
        textwrap.dedent(
            """
    [webservers]
    host1
    host2
    """
        ),
        encoding="utf-8",
    )
    f2 = inv_dir / "hosts2.ini"
    f2.write_text(
        textwrap.dedent(
            """
    [db]
    host1
    host3
    """
        ),
        encoding="utf-8",
    )

    parsed = list(parse_inventory_dir(Path(inv_dir)))
    names = {item.name for item in parsed}
    assert "host1" in names
    host1 = next(i for i in parsed if i.name == "host1")
    assert set(host1.groups) == {"webservers", "db"}
    # also ensure host2 and host3 present
    assert any(i.name == "host2" for i in parsed)
    assert any(i.name == "host3" for i in parsed)


def test_group_and_host_vars_parsing_and_precedence(tmp_path):
    # Prepare project structure
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
    # Inventory and host grouping
    inv = repo / "inventory"
    inv.mkdir()
    (inv / "hosts.ini").write_text(
        """
  [web]
  host1
  """,
        encoding="utf-8",
    )
    # group_vars -> all and web
    gdir = repo / "group_vars"
    gdir.mkdir()
    (gdir / "all.yml").write_text(
        """
  global_setting: global
  db_password: group_secret
  """,
        encoding="utf-8",
    )
    (gdir / "web.yml").write_text(
        """
  db_password: web_secret
  role_only: webrole
  """,
        encoding="utf-8",
    )
    # host_vars
    hdir = repo / "host_vars"
    hdir.mkdir()
    (hdir / "host1.yml").write_text(
        """
  db_password: host_secret
  api_token: host_token
  """,
        encoding="utf-8",
    )

    # role defaults (simulate by creating a role with defaults/main.yml)
    roles = repo / "roles"
    roles.mkdir()
    r1 = roles / "webserver"
    (r1 / "defaults").mkdir(parents=True)
    (r1 / "defaults" / "main.yml").write_text(
        """
  db_password: role_secret
  role_default: default
  """,
        encoding="utf-8",
    )

    # Parse project using ProjectParser.parse and verify effective vars
    from ansibledoctor.parser.project_parser import ProjectParser

    parser = ProjectParser(redact_sensitive=False)
    project = parser.parse(str(repo))

    # Ensure group_vars and host_vars were loaded
    assert "all" in project.group_vars
    assert "web" in project.group_vars
    assert "host1" in project.host_vars

    # Compute effective variables for host1 (presence and precedence)
    eff = project.effective_vars.get("host1")
    assert eff is not None
    # Precedence: host_vars > group_vars(web) > group_vars(all) > role defaults
    assert eff["db_password"] == "host_secret"
    assert eff["api_token"] == "host_token"
    assert eff["role_default"] == "default"


def test_project_parser_redacts_sensitive_by_default(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
    inv = repo / "inventory"
    inv.mkdir()
    (inv / "hosts.ini").write_text(
        """
  [web]
  host1
  """,
        encoding="utf-8",
    )
    gdir = repo / "group_vars"
    gdir.mkdir()
    (gdir / "all.yml").write_text(
        """
  db_password: group_secret
  """,
        encoding="utf-8",
    )
    hdir = repo / "host_vars"
    hdir.mkdir()
    (hdir / "host1.yml").write_text(
        """
  db_password: host_secret
  """,
        encoding="utf-8",
    )
    from ansibledoctor.parser.project_parser import ProjectParser

    parser = ProjectParser()  # redact_sensitive default True
    project = parser.parse(str(repo))
    eff = project.effective_vars.get("host1")
    assert eff is not None
    assert eff["db_password"] == "***REDACTED***"


def test_project_parser_respects_redaction_config(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
    (repo / ".ansibledoctor.yml").write_text(
        """
redaction:
  enabled: true
  patterns:
    - "secret"
  placeholder: "<MASKED>"
""",
        encoding="utf-8",
    )
    inv = repo / "inventory"
    inv.mkdir()
    (inv / "hosts.ini").write_text(
        """
[web]
host1
""",
        encoding="utf-8",
    )
    gdir = repo / "group_vars"
    gdir.mkdir()
    (gdir / "all.yml").write_text(
        """
db_secret: sensitive
""",
        encoding="utf-8",
    )
    from ansibledoctor.parser.project_parser import ProjectParser

    parser = ProjectParser()
    project = parser.parse(str(repo))
    eff = project.effective_vars.get("host1")
    assert eff is not None
    assert eff["db_secret"] == "<MASKED>"
