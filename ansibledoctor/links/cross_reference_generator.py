"""Cross-reference generator for documentation linking.

Generates cross-references between related documentation:
- Dependency links (role dependencies)
- Parent collection links
- Project context breadcrumbs
- Related roles ('See Also' section)
"""

from pathlib import Path
from typing import Any

from ansibledoctor.models.link import Link, LinkType
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.parser.role_parser import RoleParser


class CrossReferenceGenerator:
    """Generates cross-references between related documentation."""

    def __init__(self, base_path: Path):
        """Initialize cross-reference generator.

        Args:
            base_path: Base path for resolving relative links
        """
        self.base_path = Path(base_path)

    def generate_references(self, role: AnsibleRole) -> dict[str, Any]:
        """Generate all cross-references for a role.

        Args:
            role: Role to generate cross-references for

        Returns:
            Dictionary with cross-reference sections:
            - depends_on: List of dependency links
            - parent_collection: Parent collection link (if any)
            - project_context: Project context and breadcrumbs
            - see_also: Related roles
        """
        references = {}

        # Generate dependency links
        depends_on = self._generate_dependency_links(role)
        if depends_on:
            references["depends_on"] = depends_on

        # Generate parent collection link
        parent = self._generate_parent_collection_link(role)
        if parent:
            references["parent_collection"] = parent

        # Generate project context
        context = self._generate_project_context(role)
        if context:
            references["project_context"] = context

        # Generate related roles ('See Also')
        related = self._generate_related_roles(role)
        if related:
            references["see_also"] = related

        return references

    def _generate_dependency_links(self, role: AnsibleRole) -> list[dict[str, Any]]:
        """Generate links to role dependencies.

        Args:
            role: Role with dependencies

        Returns:
            List of dependency information with links
        """
        dependencies = []

        # Access dependencies through role.metadata
        if not role.metadata.dependencies:
            return dependencies

        for dep in role.metadata.dependencies:
            dep_name = dep.name
            dep_version = dep.version or ""

            # Construct link to dependency's README
            dep_path = self.base_path / "roles" / dep_name / "README.md"
            link_text = f"{dep_name} (v{dep_version})" if dep_version else dep_name

            link = Link(
                source_file=role.path / "README.md",
                target=str(dep_path),
                link_type=LinkType.CROSS_REFERENCE,
                text=link_text,
                line_number=None,
            )

            dependencies.append(
                {
                    "name": dep_name,
                    "version": dep_version,
                    "link": link,
                }
            )

        return dependencies

    def _generate_parent_collection_link(self, role: AnsibleRole) -> dict[str, Any] | None:
        """Generate link to parent collection.

        Args:
            role: Role within a collection

        Returns:
            Parent collection information with link, or None if standalone role
        """
        if not hasattr(role, "parent_collection") or not role.parent_collection:
            return None

        collection = role.parent_collection
        collection_name = f"{collection.namespace}.{collection.name}"
        collection_version = collection.version

        # Construct link to collection's README
        collection_path = collection.path / "README.md"
        link_text = f"{collection_name} (v{collection_version})"

        link = Link(
            source_file=role.path / "README.md",
            target=str(collection_path),
            link_type=LinkType.CROSS_REFERENCE,
            text=link_text,
            line_number=None,
        )

        return {
            "name": collection_name,
            "version": collection_version,
            "link": link,
        }

    def _generate_project_context(self, role: AnsibleRole) -> dict[str, Any] | None:
        """Generate project context breadcrumbs.

        Args:
            role: Role within a project

        Returns:
            Project context with breadcrumbs and hierarchy
        """
        context = {
            "breadcrumb": [],
            "hierarchy": {},
        }

        # Generate breadcrumb trail
        if hasattr(role, "parent_collection") and role.parent_collection:
            collection = role.parent_collection

            # Collection level
            context["breadcrumb"].append(
                {
                    "name": collection.name,
                    "link": Link(
                        source_file=role.path / "README.md",
                        target=str(collection.path / "README.md"),
                        link_type=LinkType.CROSS_REFERENCE,
                        text=collection.name,
                        line_number=None,
                    ),
                }
            )

            # Roles directory level
            roles_dir = collection.path / "roles"
            if roles_dir.exists():
                context["breadcrumb"].append(
                    {
                        "name": "roles",
                        "link": Link(
                            source_file=role.path / "README.md",
                            target=str(roles_dir / "README.md"),
                            link_type=LinkType.CROSS_REFERENCE,
                            text="roles",
                            line_number=None,
                        ),
                    }
                )

            # Role level
            context["breadcrumb"].append(
                {
                    "name": role.name,
                    "link": Link(
                        source_file=role.path / "README.md",
                        target=str(role.path / "README.md"),
                        link_type=LinkType.CROSS_REFERENCE,
                        text=role.name,
                        line_number=None,
                    ),
                }
            )

            # Hierarchy information
            context["hierarchy"] = {
                "collection": collection.name,
                "roles_dir": "roles",
                "role_category": (
                    role.path.parent.name if role.path.parent.name != "roles" else None
                ),
            }

        return context if context["breadcrumb"] else None

    def _generate_related_roles(self, role: AnsibleRole) -> list[dict[str, Any]]:
        """Generate 'See Also' links to related roles.

        Args:
            role: Role to find related roles for

        Returns:
            List of related roles with relevance scores
        """
        related_roles = []

        # Get role's tags from metadata
        role_tags = set(getattr(role.metadata, "galaxy_tags", []))
        if not role_tags:
            return related_roles

        # Get role's dependencies to exclude from 'See Also'
        dep_names = set()
        if role.metadata.dependencies:
            dep_names = {dep.name for dep in role.metadata.dependencies}

        # Find all roles in the same directory
        roles_dir = self.base_path / "roles"
        if not roles_dir.exists():
            return related_roles

        for role_path in roles_dir.iterdir():
            if not role_path.is_dir():
                continue

            # Skip self and dependencies
            if role_path.name == role.name or role_path.name in dep_names:
                continue

            try:
                # Parse role to get tags
                role_parser = RoleParser()
                other_role = role_parser.parse(role_path)
                other_tags = set(getattr(other_role, "galaxy_tags", []))

                # Calculate relevance (number of shared tags)
                shared_tags = role_tags & other_tags
                if not shared_tags:
                    continue

                relevance_score = len(shared_tags)

                # Create link
                link = Link(
                    source_file=role.path / "README.md",
                    target=str(role_path / "README.md"),
                    link_type=LinkType.CROSS_REFERENCE,
                    text=other_role.name,
                    line_number=None,
                )

                related_roles.append(
                    {
                        "name": other_role.name,
                        "relevance_score": relevance_score,
                        "shared_tags": list(shared_tags),
                        "link": link,
                    }
                )

            except Exception:
                # Skip roles that can't be parsed
                continue

        # Sort by relevance score (descending)
        related_roles.sort(key=lambda r: r["relevance_score"], reverse=True)

        return related_roles

    def get_document_context(self, doc_path: Path) -> dict[str, Any]:
        """Get context information for a document.

        Args:
            doc_path: Path to documentation file

        Returns:
            Context information (collection name, role name, etc.)
        """
        context = {}

        # Extract context from path
        parts = doc_path.parts

        # Check if in a collection
        if "ansible_collections" in parts:
            idx = parts.index("ansible_collections")
            if len(parts) > idx + 2:
                namespace = parts[idx + 1]
                collection = parts[idx + 2]
                context["collection_name"] = f"{namespace}.{collection}"

        # Check if in a role
        if "roles" in parts:
            idx = parts.index("roles")
            if len(parts) > idx + 1:
                context["role_name"] = parts[idx + 1]

        return context
