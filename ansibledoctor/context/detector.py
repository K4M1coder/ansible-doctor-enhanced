"""Hierarchical context detection for Ansible components.

Feature 007: Hierarchical Context Detection

This module provides automatic detection of parent context when documenting
Ansible components (roles, collections, projects). It generates breadcrumb
navigation and contextual overviews showing component relationships.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

from ansibledoctor.utils.slug import collection_slug, project_slug, role_slug

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)


class ComponentType(Enum):
    """Type of Ansible component."""

    PROJECT = "project"
    COLLECTION = "collection"
    ROLE = "role"
    STANDALONE = "standalone"


@dataclass
class BreadcrumbItem:
    """Single item in a breadcrumb trail."""

    name: str
    slug: str
    component_type: ComponentType
    path: Path | None = None
    link: str = ""  # Relative link to this item's documentation


@dataclass
class HierarchicalContext:
    """Hierarchical context for an Ansible component.

    Represents a component (role, collection, project) and its position
    in the hierarchy with optional parent reference.
    """

    component_type: ComponentType
    component_path: Path
    component_name: str
    component_slug: str
    parent: HierarchicalContext | None = None
    _siblings: list[HierarchicalContext] = field(default_factory=list, repr=False)

    @property
    def is_standalone(self) -> bool:
        """Check if this component has no parent."""
        return self.parent is None

    def get_breadcrumb(self) -> list[BreadcrumbItem]:
        """Get breadcrumb trail from root to this component.

        Returns list of BreadcrumbItems from the root (project) down to
        this component.
        """
        items: list[BreadcrumbItem] = []

        # Walk up to root, collecting items
        current: HierarchicalContext | None = self
        while current is not None:
            items.append(
                BreadcrumbItem(
                    name=current.component_name,
                    slug=current.component_slug,
                    component_type=current.component_type,
                    path=current.component_path,
                )
            )
            current = current.parent

        # Reverse to get root-first order
        items.reverse()
        return items

    def get_siblings(self) -> list[HierarchicalContext]:
        """Get sibling components at the same level.

        For a role, returns other roles in the same collection.
        For a collection, returns other collections in the same project.

        Returns:
            List of sibling contexts (excluding self)
        """
        return self._siblings

    def set_siblings(self, siblings: list[HierarchicalContext]) -> None:
        """Set sibling components."""
        self._siblings = [s for s in siblings if s.component_path != self.component_path]


class ContextDetector:
    """Detects hierarchical context for Ansible components.

    Scans directory structure to find parent collections and projects,
    generating a hierarchy of contexts with breadcrumb navigation.
    """

    # Markers for component type detection
    ROLE_MARKERS = ["tasks/main.yml", "meta/main.yml", "handlers/main.yml"]
    COLLECTION_MARKERS = ["galaxy.yml"]
    PROJECT_MARKERS = ["ansible.cfg", "playbooks", "site.yml"]

    def __init__(
        self,
        max_depth: int = 3,
        detect_parent: bool = True,
        follow_symlinks: bool = False,
    ):
        """Initialize the context detector.

        Args:
            max_depth: Maximum directory levels to search upward for parents
            detect_parent: Whether to detect parent context (False = standalone mode)
            follow_symlinks: Whether to follow symbolic links during detection
        """
        self.max_depth = max_depth
        self.detect_parent = detect_parent
        self.follow_symlinks = follow_symlinks

        # Cache for parent detection results (session-scoped)
        self._cache: dict[Path, HierarchicalContext] = {}

    def detect(self, component_path: Path) -> HierarchicalContext:
        """Detect hierarchical context for a component.

        Args:
            component_path: Path to the component directory

        Returns:
            HierarchicalContext for the component with parent chain
        """
        component_path = component_path.resolve()
        logger.debug("Detecting context", path=str(component_path))

        # Determine component type
        component_type = self._identify_component_type(component_path)
        if component_type == ComponentType.STANDALONE:
            logger.warning("Could not identify component type", path=str(component_path))

        # Get component name and slug
        name, slug = self._get_name_and_slug(component_path, component_type)

        # Create base context
        ctx = HierarchicalContext(
            component_type=component_type,
            component_path=component_path,
            component_name=name,
            component_slug=slug,
        )

        # Detect parent if enabled and not a project
        if self.detect_parent and component_type != ComponentType.PROJECT:
            parent = self._detect_parent(component_path, component_type)
            if parent:
                ctx.parent = parent
                # Discover siblings
                siblings = self._discover_siblings(ctx)
                ctx.set_siblings(siblings)

        return ctx

    def _identify_component_type(self, path: Path) -> ComponentType:
        """Identify what type of Ansible component is at the given path."""
        # Check for role markers
        for marker in self.ROLE_MARKERS:
            if (path / marker).exists():
                return ComponentType.ROLE

        # Check for collection markers
        for marker in self.COLLECTION_MARKERS:
            if (path / marker).exists():
                return ComponentType.COLLECTION

        # Check for project markers
        for marker in self.PROJECT_MARKERS:
            marker_path = path / marker
            if marker_path.exists():
                return ComponentType.PROJECT

        return ComponentType.STANDALONE

    def _get_name_and_slug(self, path: Path, component_type: ComponentType) -> tuple[str, str]:
        """Get component name and slug based on type."""
        if component_type == ComponentType.ROLE:
            # Try to get namespace from parent collection or use directory name
            name = path.name
            namespace = self._get_role_namespace(path)
            slug = role_slug(namespace, name)
            return name, slug

        elif component_type == ComponentType.COLLECTION:
            # Parse galaxy.yml for namespace.name
            galaxy_path = path / "galaxy.yml"
            if galaxy_path.exists():
                import yaml

                try:
                    with open(galaxy_path) as f:
                        data = yaml.safe_load(f)
                    namespace = data.get("namespace", path.parent.name)
                    name = data.get("name", path.name)
                    full_name = f"{namespace}.{name}"
                    slug = collection_slug(namespace, name)
                    return full_name, slug
                except Exception:
                    pass
            name = path.name
            return name, collection_slug("unknown", name)

        elif component_type == ComponentType.PROJECT:
            # Use directory name or ansible.cfg project name
            name = path.name
            cfg_path = path / "ansible.cfg"
            if cfg_path.exists():
                try:
                    import configparser

                    config = configparser.ConfigParser()
                    config.read(cfg_path)
                    name = config.get("defaults", "project", fallback=path.name)
                except Exception:
                    pass
            slug = project_slug(name)
            return name, slug

        return path.name, path.name

    def _get_role_namespace(self, role_path: Path) -> str:
        """Get namespace for a role from parent collection or directory."""
        # Check if role is in a collection (roles/ subdirectory)
        if role_path.parent.name == "roles":
            collection_path = role_path.parent.parent
            galaxy_path = collection_path / "galaxy.yml"
            if galaxy_path.exists():
                import yaml

                try:
                    with open(galaxy_path) as f:
                        data = yaml.safe_load(f)
                    return data.get("namespace", "unknown")
                except Exception:
                    pass
        # Fallback to parent directory name or "unknown"
        return role_path.parent.name if role_path.parent.name != "roles" else "unknown"

    def _detect_parent(
        self, component_path: Path, component_type: ComponentType
    ) -> HierarchicalContext | None:
        """Detect parent context by scanning upward in directory tree."""
        current = component_path.parent
        depth = 0

        while depth < self.max_depth:
            # Check cache first
            if current in self._cache:
                return self._cache[current]

            # Skip symlinks if not following them
            if current.is_symlink() and not self.follow_symlinks:
                break

            # Identify what's at this level
            parent_type = self._identify_component_type(current)

            # Valid parent types based on component type
            if component_type == ComponentType.ROLE:
                # Role can have collection or project parent
                if parent_type == ComponentType.COLLECTION:
                    ctx = self.detect(current)
                    self._cache[current] = ctx
                    return ctx
                elif parent_type == ComponentType.PROJECT:
                    ctx = self.detect(current)
                    self._cache[current] = ctx
                    return ctx

            elif component_type == ComponentType.COLLECTION:
                # Collection can have project parent
                if parent_type == ComponentType.PROJECT:
                    ctx = self.detect(current)
                    self._cache[current] = ctx
                    return ctx

            # Move up
            if current.parent == current:
                break  # Reached filesystem root
            current = current.parent
            depth += 1

        return None

    def _discover_siblings(self, ctx: HierarchicalContext) -> list[HierarchicalContext]:
        """Discover sibling components at the same level."""
        siblings: list[HierarchicalContext] = []

        if ctx.parent is None:
            return siblings

        parent_path = ctx.parent.component_path

        if ctx.component_type == ComponentType.ROLE:
            # Look for other roles in the collection
            roles_dir = parent_path / "roles"
            if roles_dir.exists():
                for role_path in roles_dir.iterdir():
                    if role_path.is_dir() and role_path != ctx.component_path:
                        if self._identify_component_type(role_path) == ComponentType.ROLE:
                            name, slug = self._get_name_and_slug(role_path, ComponentType.ROLE)
                            sibling = HierarchicalContext(
                                component_type=ComponentType.ROLE,
                                component_path=role_path,
                                component_name=name,
                                component_slug=slug,
                                parent=ctx.parent,
                            )
                            siblings.append(sibling)

        elif ctx.component_type == ComponentType.COLLECTION:
            # Look for other collections in the project
            collections_dir = parent_path / "collections"
            if collections_dir.exists():
                # Collections are in namespace/name structure
                for ns_dir in collections_dir.iterdir():
                    if ns_dir.is_dir():
                        for coll_path in ns_dir.iterdir():
                            if coll_path.is_dir() and coll_path != ctx.component_path:
                                if (
                                    self._identify_component_type(coll_path)
                                    == ComponentType.COLLECTION
                                ):
                                    name, slug = self._get_name_and_slug(
                                        coll_path, ComponentType.COLLECTION
                                    )
                                    sibling = HierarchicalContext(
                                        component_type=ComponentType.COLLECTION,
                                        component_path=coll_path,
                                        component_name=name,
                                        component_slug=slug,
                                        parent=ctx.parent,
                                    )
                                    siblings.append(sibling)

        return siblings

    def clear_cache(self) -> None:
        """Clear the detection cache."""
        self._cache.clear()
