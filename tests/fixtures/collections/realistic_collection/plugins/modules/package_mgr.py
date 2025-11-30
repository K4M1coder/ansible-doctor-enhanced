#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible module for managing system packages.
"""

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: package_mgr
short_description: Manage system packages
description:
  - Install, remove, or update system packages
author:
  - "Community Contributors"
"""


def main():
    module = AnsibleModule(
        argument_spec={
            "name": {"required": True, "type": "str"},
            "state": {"default": "present", "choices": ["present", "absent", "latest"]},
        }
    )
    module.exit_json(changed=False, msg="Package module executed")


if __name__ == "__main__":
    main()
