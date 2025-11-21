#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Demo Namespace
# MIT License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: database_backup
short_description: Create database backups
description:
  - This module creates backups of PostgreSQL databases
  - Supports full and incremental backups
  - Can compress backup files
version_added: "1.0.0"
options:
  database_name:
    description: Name of the database to backup
    required: true
    type: str
  backup_path:
    description: Path where backup will be stored
    required: true
    type: str
  compression:
    description: Enable compression for backup
    required: false
    default: true
    type: bool
  backup_type:
    description: Type of backup (full or incremental)
    required: false
    default: full
    choices: ['full', 'incremental']
    type: str
author:
  - Demo Author (@demo)
'''

EXAMPLES = r'''
- name: Create full database backup
  demo_namespace.demo_collection.database_backup:
    database_name: myapp_db
    backup_path: /var/backups/postgres
    compression: true
    backup_type: full

- name: Create incremental backup
  demo_namespace.demo_collection.database_backup:
    database_name: myapp_db
    backup_path: /var/backups/postgres
    backup_type: incremental
'''

RETURN = r'''
backup_file:
  description: Path to the created backup file
  returned: always
  type: str
  sample: /var/backups/postgres/myapp_db_20250120_103000.sql.gz
backup_size:
  description: Size of the backup file in bytes
  returned: always
  type: int
  sample: 1048576
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            database_name=dict(type='str', required=True),
            backup_path=dict(type='str', required=True),
            compression=dict(type='bool', required=False, default=True),
            backup_type=dict(type='str', required=False, default='full', 
                           choices=['full', 'incremental']),
        ),
        supports_check_mode=True
    )

    # Demo implementation - would normally create actual backup
    result = dict(
        changed=True,
        backup_file=f"{module.params['backup_path']}/{module.params['database_name']}_backup.sql.gz",
        backup_size=1024000
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
