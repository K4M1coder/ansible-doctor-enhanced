"""Project parsing utilities used to discover roles, collections and playbooks.

The ProjectParser is a minimal skeleton providing enough behavior for early
unit tests and will be expanded by feature tasks as parsing complexity grows.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ansibledoctor.models.project import Project, RoleInfo, CollectionInfo, Playbook
from ansibledoctor.parser.inventory_parser import parse_inventory_dir, parse_ini_inventory, parse_yaml_inventory
from configparser import ConfigParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


class ProjectParser:
    """Simple skeleton parser for Ansible projects.

    This parser performs minimal parsing and returns a `Project` model.
    It is intentionally small and will be expanded per tasks in `tasks.md`.
    """

    def __init__(self, redact_sensitive: bool = True):
        self.redact_sensitive = redact_sensitive

    def parse(self, path: str) -> Project:
        # Minimal implementation: set name from directory name and path
        # Project name comes from ansible.cfg if present
        # Determine if an ansible.cfg exists in given path or any parent (monorepo root detection)
        path_obj = Path(path).resolve()
        cfg_path: Optional[Path] = None
        for p in [path_obj] + list(path_obj.parents):
            candidate = p / "ansible.cfg"
            if candidate.is_file():
                cfg_path = candidate
                # prefer the nearest ancestor that contains ansible.cfg and stop
                break
        name = None
        if cfg_path:
            # If ansible.cfg is present, use the ancestor directory's basename
            name = cfg_path.parent.name
            # And update the effective project root path to the dir with ansible.cfg
            path_obj = cfg_path.parent
        else:
            # If no ansible.cfg, use the directory name
            name = path_obj.name

        project = Project(name=name, path=str(path_obj))

        # Roles discovery: look for 'roles' subdirectory or honor 'roles_path' in ansible.cfg
        roles_cfg_paths: Optional[list[Path]] = None
        if cfg_path:
            try:
                cfg = cfg if 'cfg' in locals() else ConfigParser()
                cfg.read(cfg_path)
                if cfg.has_option("defaults", "roles_path"):
                    rp_val = cfg.get("defaults", "roles_path").strip()
                    # Support multiple roles_path entries (colon or comma separated)
                    rp_items = [i.strip() for i in rp_val.replace(",", ":").split(":") if i.strip()]
                    rp_paths: list[Path] = []
                    for it in rp_items:
                        pth = (cfg_path.parent / it).resolve()
                        rp_paths.append(pth)
                    if rp_paths:
                        roles_cfg_paths = rp_paths
            except Exception:
                roles_cfg_paths = None

        if roles_cfg_paths is not None:
            for rp in roles_cfg_paths:
                if rp.is_dir():
                    for entry in os.listdir(str(rp)):
                        role_path = os.path.join(str(rp), entry)
                        if os.path.isdir(role_path):
                            project.roles.append(RoleInfo(name=entry, path=role_path))
        else:
            roles_dir = os.path.join(str(path_obj), "roles")
            if os.path.isdir(roles_dir):
                for entry in os.listdir(roles_dir):
                    role_path = os.path.join(roles_dir, entry)
                    if os.path.isdir(role_path):
                        project.roles.append(RoleInfo(name=entry, path=role_path))

        # Collections discovery: support both 'collections/ansible_collections/<ns>/<coll>'
        # and 'collections/<ns>/<coll>' layouts as well as custom collections_path in ansible.cfg
        collections_cfg_paths: Optional[list[Path]] = None
        if cfg_path:
            try:
                cfg = cfg if 'cfg' in locals() else ConfigParser()
                cfg.read(cfg_path)
                if cfg.has_option("defaults", "collections_path"):
                    cp_val = cfg.get("defaults", "collections_path").strip()
                    cp_items = [i.strip() for i in cp_val.replace(",", ":").split(":") if i.strip()]
                    cp_paths: list[Path] = []
                    for it in cp_items:
                        pth = (cfg_path.parent / it).resolve()
                        cp_paths.append(pth)
                    if cp_paths:
                        collections_cfg_paths = cp_paths
            except Exception:
                collections_cfg_paths = None

        collections_dir = None
        if collections_cfg_paths is not None:
            # collections_cfg_paths replaces default discovery and will be used to find collections
            collections_dirs_to_scan = [str(p) for p in collections_cfg_paths if p.is_dir()]
        else:
            collections_dirs_to_scan = [os.path.join(str(path_obj), "collections")]

        for collections_dir in collections_dirs_to_scan:
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
        # Also respect 'inventory' path set in ansible.cfg under [defaults]
        inventory_cfg_dir: Optional[Path] = None
        if cfg_path:
            try:
                cfg = ConfigParser()
                cfg.read(cfg_path)
                if cfg.has_option("defaults", "inventory"):
                    inv_val = cfg.get("defaults", "inventory").strip()
                    # Support multiple inventory sources in ansible.cfg (colon or comma separated)
                    inv_items = [i.strip() for i in inv_val.replace(",", ":").split(":") if i.strip()]
                    inv_paths: list[Path] = []
                    for it in inv_items:
                        pth = (cfg_path.parent / it).resolve()
                        inv_paths.append(pth)
                    # If multiple paths are provided, we will parse them all in order and merge
                    if inv_paths:
                        inventory_cfg_dir = inv_paths
            except Exception:
                # If parsing fails, fall back to default inventory lookup
                inventory_cfg_dir = None

        # prefer inventory specified in ansible.cfg if present
        if inventory_cfg_dir is not None:
            # inventory_cfg_dir can be a list of Paths (multiple inventory sources)
            if isinstance(inventory_cfg_dir, list):
                for ip in inventory_cfg_dir:
                    if ip.is_dir():
                        for item in parse_inventory_dir(Path(ip)):
                            project.inventory.append(item)
                    elif ip.is_file():
                        ext = ip.suffix
                        if ext in {".yml", ".yaml"}:
                            for item in parse_yaml_inventory(ip):
                                project.inventory.append(item)
                        else:
                            for item in parse_ini_inventory(ip):
                                project.inventory.append(item)
            else:
                if inventory_cfg_dir.is_dir():
                    for item in parse_inventory_dir(Path(inventory_cfg_dir)):
                        project.inventory.append(item)
                elif inventory_cfg_dir.is_file():
                    # parse single file
                    ext = inventory_cfg_dir.suffix
                    if ext in {".yml", ".yaml"}:
                        for item in parse_yaml_inventory(inventory_cfg_dir):
                            project.inventory.append(item)
                    else:
                        for item in parse_ini_inventory(inventory_cfg_dir):
                            project.inventory.append(item)
        else:
            inventory_dir = os.path.join(str(path_obj), "inventory")
            if os.path.isdir(inventory_dir):
                for item in parse_inventory_dir(Path(inventory_dir)):
                    project.inventory.append(item)

        # Playbook discovery: look for 'playbooks' directory or any top-level .yml files
        playbooks_dir = os.path.join(str(path_obj), "playbooks")
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
            for f in os.listdir(str(path_obj)):
                if f.endswith(".yml") or f.endswith(".yaml"):
                    pb_path = os.path.join(str(path_obj), f)
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
        # ----
        # Group_vars / Host_vars parsing and variable precedence
        # ----
        group_vars_dir = os.path.join(str(path_obj), "group_vars")
        host_vars_dir = os.path.join(str(path_obj), "host_vars")
        # Read group_vars
        if os.path.isdir(group_vars_dir):
            for fname in os.listdir(group_vars_dir):
                if fname.endswith(".yml") or fname.endswith(".yaml"):
                    group_name = os.path.splitext(fname)[0]
                    pth = Path(os.path.join(group_vars_dir, fname))
                    try:
                        data = yaml_loader.load_file(pth)
                        if isinstance(data, dict):
                            project.group_vars[group_name] = data
                    except Exception:
                        continue
        # Read host_vars
        if os.path.isdir(host_vars_dir):
            for fname in os.listdir(host_vars_dir):
                if fname.endswith(".yml") or fname.endswith(".yaml"):
                    host_name = os.path.splitext(fname)[0]
                    pth = Path(os.path.join(host_vars_dir, fname))
                    try:
                        data = yaml_loader.load_file(pth)
                        if isinstance(data, dict):
                            project.host_vars[host_name] = data
                    except Exception:
                        continue

        # Parse role defaults (lowest precedence)
        role_defaults_map: dict[str, dict] = {}
        for role in project.roles:
            defaults_file = Path(role.path) / "defaults" / "main.yml"
            if defaults_file.exists():
                try:
                    r_data = yaml_loader.load_file(defaults_file)
                    if isinstance(r_data, dict):
                        role_defaults_map[role.name] = r_data
                except Exception:
                    role_defaults_map[role.name] = {}

        # Compute effective vars per host
        # Allow project-level redaction config in .ansibledoctor.yml
        redact_patterns = None
        redact_placeholder = "***REDACTED***"
        config_candidate = Path(path_obj) / ".ansibledoctor.yml"
        if not config_candidate.exists():
            config_candidate = Path(path_obj) / ".ansibledoctor.yaml"
        if config_candidate.exists():
            try:
                cfg_data = yaml_loader.load_file(config_candidate)
                if isinstance(cfg_data, dict) and cfg_data.get("redaction"):
                    r = cfg_data.get("redaction")
                    if isinstance(r, dict):
                        if r.get("patterns") and isinstance(r.get("patterns"), list):
                            redact_patterns = r.get("patterns")
                        if r.get("placeholder"):
                            redact_placeholder = r.get("placeholder")
            except Exception:
                pass
        def _merge_dicts(base: dict, overrides: dict) -> dict:
            result = dict(base)
            for k, v in overrides.items():
                if isinstance(v, dict) and isinstance(result.get(k), dict):
                    result[k] = _merge_dicts(result.get(k, {}), v)
                else:
                    result[k] = v
            return result

        def _redact_keys(d: dict) -> dict:
            # default sensitive patterns
            patterns = redact_patterns if redact_patterns is not None else ["password", "secret", "token", "key", "credential", "pwd", "pass"]
            def redact_value(val, parent_key=None):
                if isinstance(val, dict):
                    return {k: redact_value(v, k) for k, v in val.items()}
                elif isinstance(val, list):
                    return [redact_value(x, parent_key) for x in val]
                else:
                    if parent_key:
                        if any(patt in parent_key.lower() for patt in patterns):
                            return redact_placeholder
                    return val
            return redact_value(d)

        for host_item in project.inventory:
            host = host_item.name
            merged: dict = {}
            # role defaults: include all role defaults as base (lowest precedence)
            for rdef in role_defaults_map.values():
                merged = _merge_dicts(merged, rdef)
            # group_vars: all -> group-specific
            if "all" in project.group_vars:
                merged = _merge_dicts(merged, project.group_vars["all"])
            for g in sorted(host_item.groups):
                if g in project.group_vars:
                    merged = _merge_dicts(merged, project.group_vars[g])
            # host_vars (highest precedence)
            if host in project.host_vars:
                merged = _merge_dicts(merged, project.host_vars[host])
            # optionally redact sensitive values
            if self.redact_sensitive:
                project.effective_vars[host] = _redact_keys(merged)
            else:
                project.effective_vars[host] = merged
        return project
