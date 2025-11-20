#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ansible lookup plugin for environment variables.
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import os

DOCUMENTATION = '''
---
lookup: env_var
short_description: Look up environment variables
description:
  - Retrieve environment variable values
author:
  - "Community Contributors"
'''

class LookupModule(LookupBase):
    """Environment variable lookup plugin."""
    
    def run(self, terms, variables=None, **kwargs):
        ret = []
        for term in terms:
            var_value = os.getenv(term)
            if var_value is None:
                raise AnsibleError(f"Environment variable {term} not found")
            ret.append(var_value)
        return ret
