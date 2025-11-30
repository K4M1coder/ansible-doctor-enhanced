#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible module for Docker container management.
"""

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: docker_container
short_description: Manage Docker containers
description:
  - Create, start, stop, or remove Docker containers
author:
  - "Community Contributors"
"""


def main():
    module = AnsibleModule(
        argument_spec={
            "name": {"required": True, "type": "str"},
            "state": {"default": "started", "choices": ["started", "stopped", "absent"]},
            "image": {"required": False, "type": "str"},
        }
    )
    module.exit_json(changed=False, msg="Docker container module executed")


if __name__ == "__main__":
    main()
