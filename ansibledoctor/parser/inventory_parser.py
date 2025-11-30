"""Inventory parsing utilities to parse INI and YAML inventory files.

This parser supports a small subset of Ansible inventory formats sufficient for
documentation purposes: INI group definitions and simple YAML host/group
structures. It's intentionally conservative and focuses on name discovery and
group membership, not a full Ansible inventory expansion implementation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ansibledoctor.models.project import InventoryItem
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


def parse_ini_inventory(file_path: Path) -> Iterable[InventoryItem]:
    """Parse a straightforward INI-style inventory file.

    Recognizes group headers (e.g., [webservers]) and host lines below them.
    Lines with key=value pairs are allowed but the host name is taken as the
    first token.
    """
    items: dict[str, InventoryItem] = {}
    current_group: str | None = None
    for raw in file_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_group = line[1:-1].strip()
            continue
        # Host line: take the first token as hostname
        host_token = line.split()[0]
        if host_token not in items:
            items[host_token] = InventoryItem(name=host_token, groups=[])
        if current_group and current_group not in items[host_token].groups:
            items[host_token].groups.append(current_group)
    return list(items.values())


def parse_yaml_inventory(file_path: Path) -> Iterable[InventoryItem]:
    loader = RuamelYAMLLoader()
    data = loader.load_file(file_path)
    items: dict[str, InventoryItem] = {}

    # Support simple Ansible inventory YAML with 'all' -> 'children' -> group -> hosts
    if not isinstance(data, dict):
        return []
    all_section = data.get("all") or data
    children = all_section.get("children", {}) if isinstance(all_section, dict) else {}
    for group_name, group_val in children.items() if isinstance(children, dict) else []:
        hosts = group_val.get("hosts", {}) if isinstance(group_val, dict) else {}
        for host_name in hosts.keys():
            if host_name not in items:
                items[host_name] = InventoryItem(name=host_name, groups=[])
            if group_name not in items[host_name].groups:
                items[host_name].groups.append(group_name)
    # Also handle top-level hosts under all.hosts
    hosts_top = all_section.get("hosts", {}) if isinstance(all_section, dict) else {}
    for host_name in hosts_top.keys() if isinstance(hosts_top, dict) else []:
        if host_name not in items:
            items[host_name] = InventoryItem(name=host_name, groups=[])
    return list(items.values())


def parse_inventory_dir(inv_dir: Path) -> Iterable[InventoryItem]:
    items: dict[str, InventoryItem] = {}
    if not inv_dir.exists():
        return []
    for entry in inv_dir.iterdir():
        if entry.is_file():
            try:
                if entry.suffix in {".yml", ".yaml"}:
                    parsed = parse_yaml_inventory(entry)
                else:
                    parsed = parse_ini_inventory(entry)
                for p in parsed:
                    if p.name not in items:
                        items[p.name] = p
                    else:
                        # Merge groups
                        for g in p.groups:
                            if g not in items[p.name].groups:
                                items[p.name].groups.append(g)
            except Exception:
                logger.debug("inventory_parse_error", file=str(entry))
                continue
    return list(items.values())
