---
description: "Contract for TemplateContext theme extensions - Feature 008"
---

# TemplateContext Theme Extensions

## Overview

This document defines the extensions to `TemplateContext` for supporting theme configuration, CSS injection, and variant templates.

## New Fields

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ansibledoctor.config.theme import ThemeConfig
from ansibledoctor.generator.css_injector import CSSTag
from ansibledoctor.generator.variant_resolver import Variant


@dataclass
class TemplateContext:
    """Extended template context with theme support."""
    
    # Existing fields (unchanged)
    role: AnsibleRole
    output_format: OutputFormat
    generator_version: str
    generation_date: datetime = field(default_factory=datetime.now)
    custom_data: dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    hierarchical_context: HasBreadcrumb | None = None
    
    # NEW: Theme configuration
    theme_config: ThemeConfig | None = None
    
    # NEW: Current variant being rendered
    variant: Variant = Variant.DETAILED
    
    # NEW: Pre-rendered CSS tags for HTML head
    css_tags: str = ""
    
    # NEW: Theme toggle components (HTML only)
    toggle_button: str = ""
    toggle_css: str = ""
    toggle_script: str = ""
```

## Integration with to_dict()

```python
def to_dict(self) -> dict[str, Any]:
    """Convert context to template-friendly dictionary."""
    result = {
        # Existing fields
        "role": self.role,
        "role_name": self.role_name,
        "role_description": self.role_description,
        # ... other existing fields ...
        "language": self.language,
        
        # NEW: Theme fields
        "theme_config": self.theme_config,
        "variant": self.variant.value if self.variant else "detailed",
        "css_tags": self.css_tags,
        "toggle_button": self.toggle_button,
        "toggle_css": self.toggle_css,
        "toggle_script": self.toggle_script,
    }
    
    # Hierarchical context (existing)
    if self.hierarchical_context is not None:
        result["context"] = {
            "breadcrumb": self.hierarchical_context.get_breadcrumb(),
            "siblings": self.hierarchical_context.get_siblings(),
        }
    
    return result
```

## Factory Method for Theme Context

```python
@classmethod
def with_theme(
    cls,
    role: AnsibleRole,
    output_format: OutputFormat,
    generator_version: str,
    theme_config: ThemeConfig,
    variant: Variant | None = None,
    language: str = "en",
    **kwargs,
) -> "TemplateContext":
    """
    Create context with theme configuration applied.
    
    This factory method handles CSS injection and toggle generation
    based on the theme configuration.
    """
    from ansibledoctor.generator.css_injector import CSSInjector
    from ansibledoctor.generator.theme_toggle import ThemeToggleGenerator
    
    # Determine variant
    effective_variant = variant or theme_config.variant
    
    # Generate CSS tags (HTML only)
    css_tags = ""
    toggle_button = ""
    toggle_css = ""
    toggle_script = ""
    
    if output_format == OutputFormat.HTML:
        injector = CSSInjector()
        css_tags = injector.render_head_tags(
            css_url=theme_config.css_url,
            css_inline=theme_config.css_inline,
            include_base=True,
        )
        
        if theme_config.enable_toggle:
            toggle_gen = ThemeToggleGenerator()
            toggle_button = toggle_gen.generate_button_html()
            toggle_css = toggle_gen.generate_toggle_css()
            toggle_script = toggle_gen.generate_script_tag()
    
    return cls(
        role=role,
        output_format=output_format,
        generator_version=generator_version,
        theme_config=theme_config,
        variant=effective_variant,
        css_tags=css_tags,
        toggle_button=toggle_button,
        toggle_css=toggle_css,
        toggle_script=toggle_script,
        language=language,
        **kwargs,
    )
```

## Template Usage Examples

### HTML Template

```jinja2
<!DOCTYPE html>
<html lang="{{ language }}" data-theme="auto">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ role_name }} - Documentation</title>
  
  {# Inject CSS (base + external + inline) #}
  {{ css_tags | safe }}
  
  {# Toggle button styles #}
  {% if theme_config and theme_config.enable_toggle %}
  <style>{{ toggle_css }}</style>
  {% endif %}
</head>
<body>
  {# Theme toggle button #}
  {% if theme_config and theme_config.enable_toggle %}
  {{ toggle_button | safe }}
  {% endif %}
  
  <header class="ad-header">
    <h1>{{ role_name }}</h1>
    <p class="ad-variant">Variant: {{ variant }}</p>
  </header>
  
  <main class="ad-content">
    {{ content }}
  </main>
  
  {# Theme toggle script #}
  {% if theme_config and theme_config.enable_toggle %}
  {{ toggle_script | safe }}
  {% endif %}
</body>
</html>
```

### Markdown/RST Templates

For non-HTML formats, theme fields are ignored:

```jinja2
{# Markdown template - no theme injection #}
# {{ role_name }}

{{ role_description }}

{# theme_config, css_tags, etc. are available but not used #}
```

## Backward Compatibility

- All new fields have sensible defaults
- Existing templates continue to work without modification
- Theme features are opt-in via configuration
- `theme_config=None` means no theme customization

## Renderer Updates

### HTML Renderer

```python
class HTMLRenderer:
    def render(self, context: TemplateContext) -> str:
        # Apply theme if configured
        if context.theme_config:
            context = TemplateContext.with_theme(
                role=context.role,
                output_format=context.output_format,
                generator_version=context.generator_version,
                theme_config=context.theme_config,
                variant=context.variant,
                language=context.language,
                generation_date=context.generation_date,
                hierarchical_context=context.hierarchical_context,
            )
        
        return self._render_template(context)
```

### Markdown/RST Renderers

No changes needed - theme fields are simply ignored in templates.
