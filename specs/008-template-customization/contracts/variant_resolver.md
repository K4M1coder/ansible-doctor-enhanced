---
description: "Contract for VariantTemplateResolver - Feature 008"
---

# VariantTemplateResolver Contract

## Overview

The `VariantTemplateResolver` resolves template names based on the requested variant (minimal, detailed, modern) with fallback to default templates.

## Resolution Chain

For a request like `render("role", format="html", variant="modern")`:

```
1. role.modern.html.j2       # Variant-specific
2. role.html.j2              # Default for format
3. role.default.html.j2      # Explicit default
4. role.j2                   # Generic fallback
```

## Interface Definition

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol


class Variant(str, Enum):
    """Template variants."""
    MINIMAL = "minimal"
    DETAILED = "detailed"
    MODERN = "modern"
    DEFAULT = "default"


class OutputFormat(str, Enum):
    """Output format types."""
    HTML = "html"
    MARKDOWN = "md"
    RST = "rst"


@dataclass(frozen=True)
class ResolvedTemplate:
    """Result of template resolution."""
    
    name: str                    # Full template name (e.g., "role.modern.html.j2")
    base_name: str               # Base template name (e.g., "role")
    variant: Variant             # Resolved variant
    format: OutputFormat         # Output format
    is_fallback: bool           # True if using fallback template
    
    @property
    def candidates(self) -> list[str]:
        """Return list of template names tried during resolution."""
        return [
            f"{self.base_name}.{self.variant.value}.{self.format.value}.j2",
            f"{self.base_name}.{self.format.value}.j2",
            f"{self.base_name}.default.{self.format.value}.j2",
            f"{self.base_name}.j2",
        ]


class VariantResolverProtocol(Protocol):
    """Protocol for variant-aware template resolution."""
    
    def resolve(
        self,
        base_name: str,
        format: OutputFormat,
        variant: Variant = Variant.DETAILED,
    ) -> ResolvedTemplate:
        """
        Resolve template name with variant fallback.
        
        Args:
            base_name: Base template name (e.g., "role", "collection")
            format: Output format (html, md, rst)
            variant: Requested variant
            
        Returns:
            ResolvedTemplate with the best matching template
            
        Raises:
            TemplateNotFoundError: If no template matches
        """
        ...
    
    def list_variants(
        self, 
        base_name: str, 
        format: OutputFormat
    ) -> list[Variant]:
        """List available variants for a base template and format."""
        ...


class VariantTemplateResolver:
    """
    Resolves template names based on variant with fallback chain.
    
    Works in conjunction with CascadingTemplateLoader to find
    the actual template file.
    """
    
    def __init__(self, loader: "CascadingTemplateLoader") -> None:
        self._loader = loader
    
    def resolve(
        self,
        base_name: str,
        format: OutputFormat,
        variant: Variant = Variant.DETAILED,
        context_path: Path | None = None,
    ) -> ResolvedTemplate:
        """Resolve template with fallback chain."""
        candidates = self._build_candidates(base_name, format, variant)
        
        for candidate in candidates:
            try:
                # Try to find template using cascading loader
                self._loader.find_template(
                    candidate, 
                    context_path or Path.cwd()
                )
                return ResolvedTemplate(
                    name=candidate,
                    base_name=base_name,
                    variant=variant if candidate.startswith(f"{base_name}.{variant.value}") else Variant.DEFAULT,
                    format=format,
                    is_fallback=candidate != candidates[0],
                )
            except TemplateNotFoundError:
                continue
        
        raise TemplateNotFoundError(
            f"No template found for {base_name} ({format.value}, {variant.value})"
        )
    
    def _build_candidates(
        self,
        base_name: str,
        format: OutputFormat,
        variant: Variant,
    ) -> list[str]:
        """Build ordered list of template candidates."""
        return [
            # 1. Exact variant match
            f"{base_name}.{variant.value}.{format.value}.j2",
            # 2. Format-specific default
            f"{base_name}.{format.value}.j2",
            # 3. Explicit default variant
            f"{base_name}.default.{format.value}.j2",
            # 4. Generic fallback
            f"{base_name}.j2",
        ]
    
    def list_variants(
        self, 
        base_name: str, 
        format: OutputFormat,
        context_path: Path | None = None,
    ) -> list[Variant]:
        """List available variants for a template."""
        available = []
        ctx = context_path or Path.cwd()
        
        for variant in Variant:
            template_name = f"{base_name}.{variant.value}.{format.value}.j2"
            try:
                self._loader.find_template(template_name, ctx)
                available.append(variant)
            except TemplateNotFoundError:
                pass
        
        return available
```

## Built-in Variant Templates

### Directory Structure

```
ansibledoctor/generator/templates/
├── html/
│   ├── role.html.j2              # Default (detailed)
│   ├── role.minimal.html.j2      # Minimal variant
│   ├── role.modern.html.j2       # Modern variant
│   ├── collection.html.j2
│   ├── collection.minimal.html.j2
│   └── collection.modern.html.j2
├── markdown/
│   ├── role.md.j2
│   ├── role.minimal.md.j2
│   └── role.modern.md.j2
└── rst/
    ├── role.rst.j2
    ├── role.minimal.rst.j2
    └── role.modern.rst.j2
```

### Variant Characteristics

| Variant | Description | Use Case |
|---------|-------------|----------|
| minimal | Compact, essential info only | README files, quick reference |
| detailed | Full documentation (default) | Comprehensive docs |
| modern | Rich UI, icons, enhanced styling | Web documentation portals |

## Template Naming Convention

```
{base}.{variant}.{format}.j2
```

Examples:
- `role.modern.html.j2` - Modern HTML role template
- `collection.minimal.md.j2` - Minimal Markdown collection template
- `project.detailed.rst.j2` - Detailed RST project template

## Fallback Behavior

```python
# Example: Request modern HTML role template
resolver.resolve("role", OutputFormat.HTML, Variant.MODERN)

# Resolution order:
# 1. role.modern.html.j2  -> Found? Return it
# 2. role.html.j2         -> Found? Return it (is_fallback=True)
# 3. role.default.html.j2 -> Found? Return it (is_fallback=True)
# 4. role.j2              -> Found? Return it (is_fallback=True)
# 5. None found           -> Raise TemplateNotFoundError
```

## Integration Example

```python
from ansibledoctor.generator.cascading_loader import CascadingTemplateLoader
from ansibledoctor.generator.variant_resolver import VariantTemplateResolver

# Create loader and resolver
loader = CascadingTemplateLoader()
resolver = VariantTemplateResolver(loader)

# Resolve template
result = resolver.resolve(
    base_name="role",
    format=OutputFormat.HTML,
    variant=Variant.MODERN,
    context_path=role_path,
)

# Load and render
template, source = loader.find_template(result.name, role_path)
html = template.render(context=template_context)

# Log resolution
log.info(
    "Template resolved",
    template=result.name,
    variant=result.variant.value,
    is_fallback=result.is_fallback,
    source=str(source),
)
```
