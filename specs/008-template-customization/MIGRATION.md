# Migration Guide for Template Customization (v0.8.0)

This guide documents breaking changes and migration steps for Feature 008 - Template Customization & Theming.

## Overview

Version 0.8.0 introduces template customization, theming, and CSS injection capabilities. Most changes are additive and backward-compatible, but some configuration keys have been updated.

## Breaking Changes

### None in v0.8.0

This release maintains full backward compatibility. Existing configurations continue to work without modification.

## New Configuration Keys

### `.ansibledoctor.yml`

The following new keys are available:

```yaml
# New theme configuration block
theme:
  name: default              # Reserved for future theme marketplace
  variant: detailed          # minimal | detailed | modern
  color_scheme: auto         # light | dark | auto
  css_url: null              # External CSS URL
  css_inline: null           # Inline CSS string
  toggle_enabled: false      # Enable dark/light toggle button
```

### Environment Variables

New environment variables for theme configuration:

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| `ANSIBLE_DOCTOR_THEME_VARIANT` | Template variant | `detailed` |
| `ANSIBLE_DOCTOR_COLOR_SCHEME` | Color scheme | `auto` |
| `ANSIBLE_DOCTOR_CSS_URL` | External CSS URL | `null` |
| `ANSIBLE_DOCTOR_THEME_TOGGLE` | Enable toggle | `false` |

### CLI Flags

New CLI flags for theming:

```bash
--variant minimal|detailed|modern    # Template variant
--color-scheme light|dark|auto       # Color scheme
--css-url URL                        # External CSS URL
--css-inline CSS                     # Inline CSS
--theme-toggle                       # Enable toggle button
```

## Template Search Path Changes

### New Search Order

Templates are now discovered in this order (first match wins):

1. **Role/Collection local**: `<role>/templates/` or `<collection>/templates/`
2. **Project root**: `<project>/templates/`
3. **User home**: `~/.ansibledoctor/templates/`
4. **Package built-in**: `ansibledoctor/generator/templates/`

### Template Naming Convention

Variant-specific templates use the naming pattern:

```
role.<variant>.<format>.j2
collection.<variant>.<format>.j2
project.<variant>.<format>.j2
```

Examples:

- `role.minimal.html.j2`
- `role.detailed.md.j2`
- `role.modern.html.j2`

### Fallback Behavior

If a variant-specific template is not found, the generator falls back to:

1. Default variant template: `role.detailed.<format>.j2`
2. Generic template: `role.<format>.j2`

## Template Context Changes

### New Context Variables

Templates now receive additional variables:

| Variable | Type | Description |
| ---------- | ------ | ------------- |
| `css_tags` | `list[CSSTag]` | CSS tags for `<head>` injection |
| `theme_toggle` | `str` | Toggle button HTML/JS (if enabled) |
| `theme_config` | `ThemeConfig` | Full theme configuration object |
| `breadcrumb` | `list[BreadcrumbItem]` | Navigation breadcrumb |

### CSS Tags Usage

```jinja2
<head>
    {# Render CSS tags #}
    {% for tag in css_tags %}
    {{ tag.to_html() | safe }}
    {% endfor %}
</head>
```

Or using the join filter:

```jinja2
<head>
    {{ css_tags | map(attribute='content') | join('\n') | safe }}
</head>
```

## Configuration Precedence

Configuration is now resolved with clear precedence:

1. **CLI flags** (highest priority)
2. **Environment variables**
3. **Config file** (`.ansibledoctor.yml`)
4. **Defaults** (lowest priority)

Example:

```bash
# CLI overrides config file
ansible-doctor role ./my-role --variant modern
# Uses 'modern' even if config file says 'detailed'
```

## CSS Variable Changes

### New CSS Custom Properties

Base CSS now uses CSS custom properties (variables):

```css
:root {
  --ad-color-primary: #2563eb;
  --ad-color-bg: #ffffff;
  --ad-color-text: #1e293b;
  /* ... more variables */
}
```

### Dark Mode Support

Dark mode is implemented via `data-theme` attribute:

```css
[data-theme="dark"] {
  --ad-color-bg: #0f172a;
  --ad-color-text: #f8fafc;
}
```

Auto dark mode uses `prefers-color-scheme`:

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ad-color-bg: #0f172a;
    /* ... dark colors */
  }
}
```

## Security Enhancements

### Template Sandboxing

User-provided templates now run in a sandboxed Jinja2 environment:

- Blocked: `__import__`, `eval`, `exec`, `open`, `getattr`, `setattr`
- Blocked attributes: `__class__`, `__mro__`, `__globals__`, etc.
- Private attributes (starting with `_`) are restricted

### Template Validation

New security validation methods:

```python
from ansibledoctor.generator.validator import create_secure_validator

validator = create_secure_validator()
validator.validate_secure(template_source)  # Raises on security violation
```

## Migration Checklist

### Minimal Migration (Most Users)

No action required. Existing setups continue to work.

### To Use New Features

1. **Add theme configuration** to `.ansibledoctor.yml`:

   ```yaml
   theme:
     variant: modern
     toggle_enabled: true
   ```

2. **Update custom templates** to include CSS tags:

   ```jinja2
   {{ css_tags | join('\n') | safe }}
   ```

3. **Add toggle support** to templates:

   ```jinja2
   {% if theme_toggle %}
   {{ theme_toggle | safe }}
   {% endif %}
   ```

### Full Migration

1. Review template search paths for conflicts
2. Update custom templates with CSS variables
3. Add dark mode support if using custom CSS
4. Test with all three variants
5. Enable theme toggle for HTML output

## Deprecated Features

None in v0.8.0.

## Removed Features

None in v0.8.0.

## Support

For migration questions:

- See [TEMPLATE_GUIDE.md](../../docs/TEMPLATE_GUIDE.md)
- Open an issue on GitHub
- Check demo examples in `demo/templates/`
