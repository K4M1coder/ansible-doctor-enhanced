---
description: "Contract for CascadingTemplateLoader - Feature 008"
---

# CascadingTemplateLoader Contract

## Overview

The `CascadingTemplateLoader` discovers templates from multiple sources in priority order, enabling template overrides at different levels of the project hierarchy.

## Discovery Order (Highest to Lowest Priority)

```
1. role/.ansibledoctor/templates/         # Role-specific
2. collection/.ansibledoctor/templates/   # Collection-wide
3. project/.ansibledoctor/templates/      # Project-level
4. ~/.ansibledoctor/templates/            # User-global
5. ansibledoctor/generator/templates/     # Package embedded
```

## Interface Definition

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from jinja2 import Environment, Template


@dataclass(frozen=True)
class TemplateSource:
    """Information about where a template was loaded from."""
    
    path: Path
    level: str  # "role", "collection", "project", "user", "embedded"
    discovered_at: datetime
    
    def __str__(self) -> str:
        return f"{self.level}:{self.path}"


class TemplateLoaderProtocol(Protocol):
    """Protocol for template loaders."""
    
    def find_template(
        self, 
        name: str, 
        context_path: Path
    ) -> tuple[Template, TemplateSource]:
        """
        Find and load a template by name.
        
        Args:
            name: Template name (e.g., "role.html.j2")
            context_path: Path to the current role/collection/project
            
        Returns:
            Tuple of (Template, TemplateSource)
            
        Raises:
            TemplateNotFoundError: If template cannot be found at any level
        """
        ...
    
    def get_environment(self, context_path: Path) -> Environment:
        """Get Jinja2 environment configured for the given context."""
        ...
    
    def clear_cache(self) -> None:
        """Clear the template discovery cache."""
        ...


class CascadingTemplateLoader:
    """
    Template loader with cascading discovery and caching.
    
    Attributes:
        cache_ttl: Cache time-to-live in seconds (default: 300)
        search_paths: Additional search paths to consider
    """
    
    def __init__(
        self,
        cache_ttl: int = 300,
        search_paths: list[Path] | None = None,
    ) -> None:
        self._cache: dict[str, tuple[Template, TemplateSource]] = {}
        self._cache_timestamps: dict[str, datetime] = {}
        self._cache_ttl = cache_ttl
        self._search_paths = search_paths or []
    
    def find_template(
        self, 
        name: str, 
        context_path: Path
    ) -> tuple[Template, TemplateSource]:
        """Find template using cascading discovery."""
        cache_key = f"{context_path}:{name}"
        
        # Check cache
        if cache_key in self._cache:
            cached_at = self._cache_timestamps[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
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
        context_path: Path
    ) -> tuple[Template, TemplateSource]:
        """Internal discovery logic."""
        search_order = self._build_search_order(context_path)
        
        for level, path in search_order:
            template_path = path / name
            if template_path.exists():
                env = self._create_environment(path)
                template = env.get_template(name)
                source = TemplateSource(
                    path=template_path,
                    level=level,
                    discovered_at=datetime.now()
                )
                return template, source
        
        raise TemplateNotFoundError(f"Template '{name}' not found")
    
    def _build_search_order(
        self, 
        context_path: Path
    ) -> list[tuple[str, Path]]:
        """Build ordered list of (level, path) to search."""
        order = []
        
        # Role level
        role_templates = context_path / ".ansibledoctor" / "templates"
        if role_templates.exists():
            order.append(("role", role_templates))
        
        # Collection level (parent of roles/)
        if (context_path.parent.name == "roles" and 
            (context_path.parent.parent / "galaxy.yml").exists()):
            coll_templates = (
                context_path.parent.parent / ".ansibledoctor" / "templates"
            )
            if coll_templates.exists():
                order.append(("collection", coll_templates))
        
        # Project level (look for ansible.cfg)
        project_root = self._find_project_root(context_path)
        if project_root:
            proj_templates = project_root / ".ansibledoctor" / "templates"
            if proj_templates.exists():
                order.append(("project", proj_templates))
        
        # User level
        user_templates = Path.home() / ".ansibledoctor" / "templates"
        if user_templates.exists():
            order.append(("user", user_templates))
        
        # Custom search paths
        for custom_path in self._search_paths:
            if custom_path.exists():
                order.append(("custom", custom_path))
        
        # Embedded (always last)
        order.append(("embedded", Path("__embedded__")))
        
        return order
```

## Caching Behavior

| Scenario | Behavior |
| ---------- | ---------- |
| First access | Discover template, cache result |
| Cache hit (< TTL) | Return cached template |
| Cache hit (>= TTL) | Re-discover, update cache |
| `clear_cache()` called | Invalidate all cached templates |
| Template file modified | Cache invalidated on next TTL expiry |

## Logging

The loader MUST log template discovery for debugging:

```python
import structlog

log = structlog.get_logger()

def _discover_template(self, name: str, context_path: Path):
    for level, path in search_order:
        template_path = path / name
        if template_path.exists():
            log.debug(
                "Template discovered",
                template=name,
                source=str(template_path),
                level=level,
            )
            # ...
```

## Error Handling

```python
class TemplateNotFoundError(Exception):
    """Raised when a template cannot be found at any level."""
    
    def __init__(self, template_name: str, searched_paths: list[Path]):
        self.template_name = template_name
        self.searched_paths = searched_paths
        paths_str = "\n  - ".join(str(p) for p in searched_paths)
        super().__init__(
            f"Template '{template_name}' not found. Searched:\n  - {paths_str}"
        )
```

## Integration with Jinja2 ChoiceLoader

```python
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader

def _create_environment(self, primary_path: Path) -> Environment:
    """Create Jinja2 environment with fallback to embedded templates."""
    loaders = []
    
    # Primary path first
    if primary_path != Path("__embedded__"):
        loaders.append(FileSystemLoader(str(primary_path)))
    
    # Always include embedded as fallback
    loaders.append(
        PackageLoader("ansibledoctor.generator", "templates")
    )
    
    return Environment(
        loader=ChoiceLoader(loaders),
        autoescape=True,
    )
```
