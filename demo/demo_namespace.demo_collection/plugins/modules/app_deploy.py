#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: app_deploy
short_description: Deploy application version
description:
  - Deploy new version of the application
  - Supports rollback functionality
version_added: "1.0.0"
options:
  app_name:
    description: Application name
    required: true
    type: str
  version:
    description: Version to deploy
    required: true
    type: str
  deploy_path:
    description: Deployment directory
    required: true
    type: str
author:
  - Demo Author (@demo)
'''

EXAMPLES = r'''
- name: Deploy application
  demo_namespace.demo_collection.app_deploy:
    app_name: myapp
    version: "1.2.3"
    deploy_path: /opt/myapp
'''

RETURN = r'''
deployed_version:
  description: Version that was deployed
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            app_name=dict(type='str', required=True),
            version=dict(type='str', required=True),
            deploy_path=dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    result = dict(
        changed=True,
        deployed_version=module.params['version']
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
