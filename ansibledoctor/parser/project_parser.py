from __future__ import annotations

import os
from typing import Optional

from ansibledoctor.models.project import Project, RoleInfo


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

        # TODO: add playbook, collection, inventory parsing in later tasks
        return project
