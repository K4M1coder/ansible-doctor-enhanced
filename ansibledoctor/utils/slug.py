"""Slug utilities for consistent output naming and hierarchical paths.

These functions are intentionally unimplemented (NotImplementedError) until TDD tests (in tests/unit/test_slug.py) fail (RED), then developers will implement the expected behavior accordingly.
"""

from __future__ import annotations


def collection_slug(namespace: str, name: str) -> str:
    """Return slug for a collection with prefix 'collection_' and dot separator between namespace and name.

    Example: collection_my-namespace.my-collection
    """
    raise NotImplementedError("collection_slug not implemented yet")


def role_slug(namespace: str, name: str) -> str:
    """Return slug for a role with prefix 'role_' and dot separator between namespace and name.

    Example: role_my_namespace.webserver
    """
    raise NotImplementedError("role_slug not implemented yet")


def project_slug(name: str) -> str:
    """Return slug for a project with prefix 'ansibleproject_'.

    Example: ansibleproject_my-project
    """
    raise NotImplementedError("project_slug not implemented yet")


def join_hierarchy(project: str, collection: str, role: str) -> str:
    """Join slugs into a hierarchical path output.

    Example: ansibleproject_my-project/collections/collection_my-namespace.my-collection/role_my_namespace.webserver
    """
    raise NotImplementedError("join_hierarchy not implemented yet")
