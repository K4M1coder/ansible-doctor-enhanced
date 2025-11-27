"""Project parsing utilities used to discover roles, collections and playbooks.

The ProjectParser is a minimal skeleton providing enough behavior for early
unit tests and will be expanded by feature tasks as parsing complexity grows.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ansibledoctor.models.project import Project, RoleInfo, CollectionInfo, Playbook
from ansibledoctor.parser.inventory_parser import parse_inventory_dir
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


class ProjectParser:
    """Simple skeleton parser for Ansible projects.

    This parser performs minimal parsing and returns a `Project` model.
    It is intentionally small and will be expanded per tasks in `tasks.md`.
    """

    def __init__(self):
        pass

    def parse(self, path: str) -> Project:
        # Minimal implementation: set name from directory name and path
        # Project name comes from ansible.cfg if present
        ansible_cfg = os.path.join(path, "ansible.cfg")
        name = None
        if os.path.isfile(ansible_cfg):
            # If ansible.cfg is present, the parser can extract values (future task),
            # for now we default to directory name if cfg exists
            name = os.path.basename(os.path.abspath(path))

        project = Project(name=name, path=str(path))

        # Roles discovery: look for 'roles' subdirectory
        roles_dir = os.path.join(path, "roles")
        if os.path.isdir(roles_dir):
            for entry in os.listdir(roles_dir):
                role_path = os.path.join(roles_dir, entry)
                if os.path.isdir(role_path):
                    project.roles.append(RoleInfo(name=entry, path=role_path))

        # Collections discovery: support both 'collections/ansible_collections/<ns>/<coll>'
        # and 'collections/<ns>/<coll>' layouts
        collections_dir = os.path.join(path, "collections")
        if os.path.isdir(collections_dir):
            # Variant A: collections/ansible_collections/<namespace>/<collection>
            ans_col_dir = os.path.join(collections_dir, "ansible_collections")
            if os.path.isdir(ans_col_dir):
                for ns in os.listdir(ans_col_dir):
                    ns_path = os.path.join(ans_col_dir, ns)
                    if os.path.isdir(ns_path):
                        for coll in os.listdir(ns_path):
                            coll_path = os.path.join(ns_path, coll)
                            if os.path.isdir(coll_path):
                                project.collections.append(CollectionInfo(name=f"{ns}.{coll}", path=coll_path))
            # Variant B: collections/<namespace>/<collection>
            # We should parse this even if ansible_collections exists alongside other layout
            for ns in os.listdir(collections_dir):
                if ns == "ansible_collections":
                    # Skip already processed ansible_collections folder
                    continue
                ns_path = os.path.join(collections_dir, ns)
                if os.path.isdir(ns_path):
                    for coll in os.listdir(ns_path):
                        coll_path = os.path.join(ns_path, coll)
                        if os.path.isdir(coll_path):
                            project.collections.append(CollectionInfo(name=f"{ns}.{coll}", path=coll_path))

        # Inventory discovery: support parsing of inventory files under 'inventory' dir
        inventory_dir = os.path.join(path, "inventory")
        if os.path.isdir(inventory_dir):
            for item in parse_inventory_dir(Path(inventory_dir)):
                project.inventory.append(item)

        # Playbook discovery: look for 'playbooks' directory or any top-level .yml files
        playbooks_dir = os.path.join(path, "playbooks")
        yaml_loader = RuamelYAMLLoader()
        if os.path.isdir(playbooks_dir):
            for fname in os.listdir(playbooks_dir):
                if fname.endswith(".yml") or fname.endswith(".yaml"):
                    pb_path = os.path.join(playbooks_dir, fname)
                    try:
                        data = yaml_loader.load_file(Path(pb_path))
                        # Playbook is typically a list of plays, but sometimes a dict (single-play)
                        if (isinstance(data, list) and data) or (
                            isinstance(data, dict) and ("hosts" in data or "roles" in data)
                        ):
                            # Build a Playbook model with aggregated hosts and roles
                            hosts = set()
                            roles = set()
                            plays_list = data if isinstance(data, list) else [data]
                            for play in plays_list:
                                if isinstance(play, dict):
                                    hs = play.get("hosts")
                                    if hs:
                                        if isinstance(hs, list):
                                            hosts.update(hs)
                                        else:
                                            hosts.add(str(hs))
                                    rls = play.get("roles") or []
                                    for r in rls:
                                        if isinstance(r, dict):
                                            # role may be dict: {role: name}
                                            name = r.get("role") or r.get("name")
                                            if name:
                                                roles.add(name)
                                        else:
                                            roles.add(str(r))
                            pb = Playbook(name=os.path.splitext(fname)[0], path=pb_path, hosts=list(hosts), roles=list(roles))
                            project.playbooks.append(pb)
                    except Exception:
                        # Ignore playbook parse errors for now; logging may be added later
                        continue
        else:
            # Also search top-level yml files as potential playbooks
            for f in os.listdir(path):
                if f.endswith(".yml") or f.endswith(".yaml"):
                    pb_path = os.path.join(path, f)
                    try:
                        data = yaml_loader.load_file(Path(pb_path))
                        if (isinstance(data, list) and data) or (
                            isinstance(data, dict) and ("hosts" in data or "roles" in data)
                        ):
                            hosts = set()
                            roles = set()
                            plays_list = data if isinstance(data, list) else [data]
                            for play in plays_list:
                                if isinstance(play, dict):
                                    hs = play.get("hosts")
                                    if hs:
                                        if isinstance(hs, list):
                                            hosts.update(hs)
                                        else:
                                            hosts.add(str(hs))
                                    rls = play.get("roles") or []
                                    for r in rls:
                                        if isinstance(r, dict):
                                            name = r.get("role") or r.get("name")
                                            if name:
                                                roles.add(name)
                                        else:
                                            roles.add(str(r))
                            pb = Playbook(name=os.path.splitext(f)[0], path=pb_path, hosts=list(hosts), roles=list(roles))
                            project.playbooks.append(pb)
                    except Exception:
                        continue

        # TODO: additional parsing for playbooks, inventory, and more advanced features
        return project
