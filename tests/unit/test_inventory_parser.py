import textwrap
from pathlib import Path
from ansibledoctor.parser.inventory_parser import parse_inventory_dir, parse_ini_inventory, parse_yaml_inventory


def test_parse_ini_inventory_group_parsing(tmp_path):
    inv_file = tmp_path / "hosts.ini"
    inv_file.write_text(textwrap.dedent("""
    [webservers]
    host1 ansible_host=1.2.3.4
    host2

    [db]
    db1
    """), encoding="utf-8")

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
    inv_file.write_text(textwrap.dedent("""
    all:
      children:
        webservers:
          hosts:
            hosta:
              ansible_host: 1.2.3.4
            hostb: {}
      hosts:
        hosttop: {}
    """), encoding="utf-8")

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
    f1.write_text(textwrap.dedent("""
    [webservers]
    host1
    host2
    """), encoding="utf-8")
    f2 = inv_dir / "hosts2.ini"
    f2.write_text(textwrap.dedent("""
    [db]
    host1
    host3
    """), encoding="utf-8")

    parsed = list(parse_inventory_dir(Path(inv_dir)))
    names = {item.name for item in parsed}
    assert "host1" in names
    host1 = next(i for i in parsed if i.name == "host1")
    assert set(host1.groups) == {"webservers", "db"}
    # also ensure host2 and host3 present
    assert any(i.name == "host2" for i in parsed)
    assert any(i.name == "host3" for i in parsed)
