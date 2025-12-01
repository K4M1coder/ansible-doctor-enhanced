"""Cascading template loader with multi-level discovery.

Feature 008 - Template Customization & Theming
T335: CascadingTemplateLoader implementation

Discovers templates from multiple sources in priority order:
1. Role-level (.ansibledoctor/templates/)
2. Collection-level (parent collection's .ansibledoctor/templates/)
3. Project-level (project root's .ansibledoctor/templates/)
4. User-level (~/.ansibledoctor/templates/)
5. Embedded (package templates - always available)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, Template

from ansibledoctor.generator.filters import FILTERS

log = logging.getLogger(__name__)


class TemplateNotFoundError(Exception):
    """Raised when a template cannot be found at any level.

    Attributes:
        template_name: Name of the template that wasn't found
        searched_paths: List of paths that were searched
    """

    def __init__(self, template_name: str, searched_paths: list[Path] | None = None):
        self.template_name = template_name
        self.searched_paths = searched_paths or []

        if self.searched_paths:
            paths_str = "\n  - ".join(str(p) for p in self.searched_paths)
            message = f"Template '{template_name}' not found. Searched:\n  - {paths_str}"
        else:
            message = f"Template '{template_name}' not found"

        super().__init__(message)


@dataclass(frozen=True)
class TemplateSource:
    """Information about where a template was loaded from.

    Attributes:
        path: Full path to the template file
        level: Discovery level (role, collection, project, user, custom, embedded)
        discovered_at: Timestamp when template was discovered
    """

    path: Path
    level: str
    discovered_at: datetime

    def __str__(self) -> str:
        """Return formatted string showing level and path."""
        return f"{self.level}:{self.path}"


class CascadingTemplateLoader:
    """Template loader with cascading discovery and caching.

    Discovers templates from multiple sources in priority order, with TTL-based
    caching to improve performance during repeated documentation generation.

    Attributes:
        cache_ttl: Cache time-to-live in seconds (default: 300)
        search_paths: Additional custom search paths

    Example:
        >>> loader = CascadingTemplateLoader()
        >>> template, source = loader.find_template("role.html.j2", Path("roles/nginx"))
        >>> print(source.level)  # 'role', 'collection', 'project', 'user', or 'embedded'

    Feature: US24 - Custom Template Paths
    Task: T335 - CascadingTemplateLoader implementation
    """

    # Project root markers - files that indicate project root
    PROJECT_MARKERS = ["ansible.cfg", "pyproject.toml", ".ansible-lint", ".git"]

    def __init__(
        self,
        cache_ttl: int = 300,
        search_paths: list[Path] | None = None,
    ) -> None:
        """Initialize cascading template loader.

        Args:
            cache_ttl: Cache time-to-live in seconds
            search_paths: Additional paths to search for templates
        """
        self._cache: dict[str, tuple[Template, TemplateSource]] = {}
        self._cache_timestamps: dict[str, datetime] = {}
        self._cache_ttl = cache_ttl
        self._search_paths = search_paths or []

    @property
    def cache_ttl(self) -> int:
        """Return cache TTL in seconds."""
        return self._cache_ttl

    @property
    def search_paths(self) -> list[Path]:
        """Return list of custom search paths."""
        return self._search_paths.copy()

    def find_template(
        self,
        name: str,
        context_path: Path,
    ) -> tuple[Template, TemplateSource]:
        """Find and load a template by name.

        Searches for the template in priority order: role, collection, project,
        user, custom, and embedded. Results are cached for performance.

        Args:
            name: Template name (e.g., "role.html.j2")
            context_path: Path to the current role/collection/project

        Returns:
            Tuple of (Template, TemplateSource)

        Raises:
            TemplateNotFoundError: If template cannot be found at any level
        """
        cache_key = f"{context_path}:{name}"

        # Check cache
        if cache_key in self._cache:
            cached_at = self._cache_timestamps[cache_key]
            if (datetime.now() - cached_at).total_seconds() < self._cache_ttl:
                log.debug("Template cache hit", extra={"template": name, "cache_key": cache_key})
                return self._cache[cache_key]

        # Discover template
        template, source = self._discover_template(name, context_path)

        # Update cache
        self._cache[cache_key] = (template, source)
        self._cache_timestamps[cache_key] = datetime.now()

        return template, source

    def _discover_template(
        self,
        name: str,
        context_path: Path,
    ) -> tuple[Template, TemplateSource]:
        """Internal discovery logic.

        Builds search order and tries each path until template is found.

        Args:
            name: Template name
            context_path: Context path for discovery

        Returns:
            Tuple of (Template, TemplateSource)

        Raises:
            TemplateNotFoundError: If template not found
        """
        search_order = self._build_search_order(context_path)
        searched_paths: list[Path] = []

        for level, path in search_order:
            if level == "embedded":
                # Try embedded templates
                try:
                    env = self._create_environment(path)
                    template = env.get_template(name)
                    source = TemplateSource(
                        path=Path(f"<embedded>/{name}"),
                        level="embedded",
                        discovered_at=datetime.now(),
                    )
                    log.debug(
                        "Template discovered",
                        extra={
                            "template": name,
                            "source": str(source.path),
                            "level": level,
                        },
                    )
                    return template, source
                except Exception:
                    searched_paths.append(Path(f"<embedded>/{name}"))
                    continue

            template_path = path / name
            searched_paths.append(template_path)

            if template_path.exists():
                env = self._create_environment(path)
                template = env.get_template(name)
                source = TemplateSource(
                    path=template_path,
                    level=level,
                    discovered_at=datetime.now(),
                )
                log.debug(
                    "Template discovered",
                    extra={
                        "template": name,
                        "source": str(template_path),
                        "level": level,
                    },
                )
                return template, source

        raise TemplateNotFoundError(name, searched_paths)

    def _build_search_order(
        self,
        context_path: Path,
    ) -> list[tuple[str, Path]]:
        """Build ordered list of (level, path) to search.

        Args:
            context_path: Path to the current context (role/collection/project)

        Returns:
            Ordered list of (level_name, template_directory) tuples
        """
        order: list[tuple[str, Path]] = []
        resolved_path = context_path.resolve()

        # 1. Role level
        role_templates = resolved_path / ".ansibledoctor" / "templates"
        if role_templates.exists():
            order.append(("role", role_templates))

        # 2. Collection level (parent of roles/)
        if (
            resolved_path.parent.name == "roles"
            and (resolved_path.parent.parent / "galaxy.yml").exists()
        ):
            coll_templates = resolved_path.parent.parent / ".ansibledoctor" / "templates"
            if coll_templates.exists():
                order.append(("collection", coll_templates))

        # 3. Project level
        project_root = self._find_project_root(resolved_path)
        if project_root:
            proj_templates = project_root / ".ansibledoctor" / "templates"
            if proj_templates.exists():
                order.append(("project", proj_templates))

        # 4. User level
        user_templates = Path.home() / ".ansibledoctor" / "templates"
        if user_templates.exists():
            order.append(("user", user_templates))

        # 5. Custom search paths
        for custom_path in self._search_paths:
            if custom_path.exists():
                order.append(("custom", custom_path))

        # 6. Embedded (always last, marker path)
        order.append(("embedded", Path("__embedded__")))

        return order

    def _find_project_root(self, start_path: Path) -> Path | None:
        """Find project root by looking for marker files.

        Walks up directory tree looking for project markers like ansible.cfg,
        pyproject.toml, or .git.

        Args:
            start_path: Starting path for search

        Returns:
            Path to project root, or None if not found
        """
        current = start_path.resolve()

        while True:
            for marker in self.PROJECT_MARKERS:
                if (current / marker).exists():
                    return current

            parent = current.parent
            if parent == current:
                # Reached filesystem root
                return None

            current = parent

    def _create_environment(self, template_path: Path) -> Environment:
        """Create Jinja2 environment with fallback to embedded templates.

        Uses ChoiceLoader to try template_path first, then fall back to
        embedded package templates.

        Args:
            template_path: Primary template directory path

        Returns:
            Configured Jinja2 Environment
        """
        loaders = []

        # Primary path first (unless embedded marker)
        if template_path != Path("__embedded__"):
            loaders.append(FileSystemLoader(str(template_path)))

        # Always include embedded as fallback
        loaders.append(PackageLoader("ansibledoctor.generator", "templates"))

        env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=True,
        )

        # Register custom filters
        env.filters.update(FILTERS)

        return env

    def get_environment(self, context_path: Path) -> Environment:
        """Get Jinja2 environment configured for the given context.

        Creates an environment with all template paths in the search order
        available via ChoiceLoader.

        Args:
            context_path: Path to the current context

        Returns:
            Configured Jinja2 Environment
        """
        search_order = self._build_search_order(context_path)
        loaders = []

        for level, path in search_order:
            if level != "embedded" and path.exists():
                loaders.append(FileSystemLoader(str(path)))

        # Always include embedded
        loaders.append(PackageLoader("ansibledoctor.generator", "templates"))

        env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=True,
        )

        # Register custom filters
        env.filters.update(FILTERS)

        return env

    def clear_cache(self) -> None:
        """Clear the template discovery cache.

        Useful when templates have been modified and need to be reloaded
        before the TTL expires.
        """
        self._cache.clear()
        self._cache_timestamps.clear()
        log.debug("Template cache cleared")
