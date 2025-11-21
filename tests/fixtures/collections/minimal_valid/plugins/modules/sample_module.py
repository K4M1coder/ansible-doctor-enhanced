#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sample module for testing plugin discovery

DOCUMENTATION = r"""
---
module: sample_module
short_description: Sample module for testing
description:
  - This is a minimal sample module for testing collection parsing
author:
  - Test Author (@testauthor)
"""

EXAMPLES = r"""
- name: Use sample module
  test_namespace.test_collection.sample_module:
    param: value
"""

RETURN = r"""
result:
  description: Sample return value
  returned: always
  type: str
"""


def main():
    """Main module entry point."""
    pass


if __name__ == "__main__":
    main()
