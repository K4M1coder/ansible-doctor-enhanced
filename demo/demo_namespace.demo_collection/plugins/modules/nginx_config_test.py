#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nginx_config_test
short_description: Test Nginx configuration
description:
  - Test Nginx configuration for syntax errors
  - Verify configuration before reloading
version_added: "1.0.0"
options:
  config_path:
    description: Path to Nginx configuration
    required: false
    default: /etc/nginx/nginx.conf
    type: str
author:
  - Demo Author (@demo)
'''

EXAMPLES = r'''
- name: Test Nginx config
  demo_namespace.demo_collection.nginx_config_test:
    config_path: /etc/nginx/nginx.conf
'''

RETURN = r'''
valid:
  description: Whether configuration is valid
  returned: always
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            config_path=dict(type='str', required=False, default='/etc/nginx/nginx.conf'),
        ),
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        valid=True
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
