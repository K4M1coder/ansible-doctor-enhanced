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


def build_context_path(
    language: str,
    project: str | None = None,
    collection: str | None = None,
    role: str | None = None,
) -> str:
    """Build a documentation path for the hierarchical context.

    Creates paths like:
    - docs/lang/en/ansibleproject_proj/README.md (project only)
    - docs/lang/en/ansibleproject_proj/collections/collection_ns.coll/README.md (collection in project)
    - docs/lang/en/ansibleproject_proj/collections/collection_ns.coll/role_ns.role/README.md (role in collection in project)
    - docs/lang/en/collection_ns.coll/README.md (standalone collection)
    - docs/lang/en/role_ns.role/README.md (standalone role)

    Args:
        language: ISO 639-1 language code (e.g., 'en', 'fr')
        project: Project slug (e.g., 'ansibleproject_my-project') or None
        collection: Collection slug (e.g., 'collection_ns.name') or None
        role: Role slug (e.g., 'role_ns.name') or None

    Returns:
        Path string like 'docs/lang/en/...'
    """
    parts = ["docs", "lang", language]

    if project:
        parts.append(project)
        if collection:
            parts.append("collections")
            parts.append(collection)
            if role:
                parts.append(role)
    elif collection:
        parts.append(collection)
        if role:
            parts.append(role)
    elif role:
        parts.append(role)

    return "/".join(parts)


def relative_link(from_path: str, to_path: str) -> str:
    """Calculate relative link between two documentation paths.

    Both paths should be in the format returned by build_context_path.

    Args:
        from_path: Current document path (e.g., 'docs/lang/en/collection_ns.coll/role_ns.role')
        to_path: Target document path (e.g., 'docs/lang/en/collection_ns.coll')

    Returns:
        Relative path (e.g., '../README.md')
    """
    from pathlib import PurePosixPath

    # Normalize paths
    from_parts = PurePosixPath(from_path).parts
    to_parts = PurePosixPath(to_path).parts

    # Find common prefix
    common_length = 0
    for i, (f, t) in enumerate(zip(from_parts, to_parts)):
        if f == t:
            common_length = i + 1
        else:
            break

    # Calculate how many levels up to go
    levels_up = len(from_parts) - common_length

    # Build relative path
    if levels_up == 0 and len(to_parts) == common_length:
        # Same directory
        return "README.md"

    rel_parts = [".."] * levels_up + list(to_parts[common_length:])
    if rel_parts:
        return "/".join(rel_parts) + "/README.md"
    else:
        return "README.md"

