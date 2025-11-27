"""Slug utilities for consistent output naming and hierarchical paths.

These functions are intentionally unimplemented (NotImplementedError) until TDD tests (in tests/unit/test_slug.py) fail (RED), then developers will implement the expected behavior accordingly.
"""

from __future__ import annotations

import re
import unicodedata


def _slugify(s: str, allow_underscore: bool = False) -> str:
    # Normalize unicode characters to ASCII, lowercase
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower().strip()
    # Preserve underscores optionally
    if allow_underscore:
        s = re.sub(r"[^a-z0-9_]+", "-", s)
    else:
        s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def collection_slug(namespace: str, name: str) -> str:
    """Return slug for a collection with prefix 'collection_' and dot separator between namespace and name.

    Example: collection_my-namespace.my-collection
    """
    ns = _slugify(namespace)
    nm = _slugify(name)
    return f"collection_{ns}.{nm}"


def role_slug(namespace: str, name: str) -> str:
    """Return slug for a role with prefix 'role_' and dot separator between namespace and name.

    Example: role_my_namespace.webserver
    """
    ns = _slugify(namespace, allow_underscore=True)
    nm = _slugify(name)
    return f"role_{ns}.{nm}"


def project_slug(name: str) -> str:
    """Return slug for a project with prefix 'ansibleproject_'.

    Example: ansibleproject_my-project
    """
    nm = _slugify(name)
    return f"ansibleproject_{nm}"


def join_hierarchy(project: str, collection: str, role: str) -> str:
    """Join slugs into a hierarchical path output.

    Example: ansibleproject_my-project/collections/collection_my-namespace.my-collection/role_my_namespace.webserver
    """
    # Join the provided slugs into a consistent path
    return f"{project}/collections/{collection}/{role}"
