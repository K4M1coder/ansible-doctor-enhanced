# Release Notes - v0.8.0

**Release Date**: December 2025

## Overview

Version 0.8.0 introduces **Template Customization & Theming** (Feature 008), enabling users to customize documentation output with template variants, CSS theming, and dark mode support.

## Highlights

### 🎨 Template Variants

Choose from three built-in documentation styles:

- **minimal** - Compact output with essential information only
- **detailed** - Full documentation with all sections (default)
- **modern** - Contemporary styling with cards and timeline visualization

```bash
# Use minimal variant
ansible-doctor generate --variant minimal

# Use modern variant
ansible-doctor generate --variant modern
```

### 🌙 Dark Mode Support

Built-in dark mode with automatic detection and manual toggle:

```bash
# Force dark mode
ansible-doctor generate --color-scheme dark

# Auto-detect from system preference (default)
ansible-doctor generate --color-scheme auto

# Disable theme toggle button
ansible-doctor generate --no-theme-toggle
```

### 🎯 CSS Customization

Inject custom CSS for brand-specific styling:

```bash
# External CSS file
ansible-doctor generate --css-url /path/to/theme.css

# Or via configuration
# .ansibledoctor.yml
theme:
  variant: modern
  color_scheme: auto
  css_url: "https://example.com/brand-theme.css"
  css_inline: ":root { --ad-color-primary: #1a73e8; }"
```

### 🔒 Template Security

Secure sandboxed environment for user templates:

- Blocks dangerous Python constructs
- Restricts access to sensitive attributes
- Validates templates before rendering

### 📋 Template Inheritance Validation

Actionable error messages for template issues:

- Reports missing parent templates with search paths
- Validates include dependencies
- Checks import statements

## New CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--variant` | Template variant (minimal/detailed/modern) | detailed |
| `--color-scheme` | Color scheme (light/dark/auto) | auto |
| `--theme-toggle` / `--no-theme-toggle` | Enable/disable theme toggle | enabled |
| `--template-dir` | Custom template directory | - |
| `--css-url` | External CSS URL | - |
| `--css-inline` | Inline CSS string | - |

## Configuration Example

```yaml
# .ansibledoctor.yml
theme:
  name: "My Custom Theme"
  variant: modern
  color_scheme: auto
  enable_toggle: true
  css_url: "https://cdn.example.com/docs-theme.css"
  css_inline: |
    :root {
      --ad-color-primary: #0066cc;
      --ad-color-secondary: #6c757d;
    }
```

## CSS Variables Reference

All CSS variables use the `--ad-` prefix:

### Colors
- `--ad-color-primary` - Primary brand color
- `--ad-color-secondary` - Secondary accent color
- `--ad-color-success` - Success state color
- `--ad-color-warning` - Warning state color
- `--ad-color-error` - Error state color

### Typography
- `--ad-font-family` - Base font family
- `--ad-font-size-base` - Base font size
- `--ad-line-height` - Base line height

### Spacing
- `--ad-spacing-xs` through `--ad-spacing-xl`

### Dark Mode
Dark mode automatically applies when:
- User clicks the theme toggle button
- System preference is set to dark (`prefers-color-scheme: dark`)
- `color_scheme: dark` is configured

## Migration Guide

See [MIGRATION.md](../specs/008-template-customization/MIGRATION.md) for:
- Upgrading from v0.7.x
- Template search path changes
- Configuration key updates

## Breaking Changes

None. This release is fully backward compatible.

## Test Coverage

- 1496+ tests passing
- 74 template sandboxing tests
- 45 accessibility tests
- 45 E2E demo tests
- 105 integration tests for theming features

## Contributors

Thank you to all contributors who made this release possible!

## Links

- [Full Changelog](../CHANGELOG.md)
- [Template Guide](TEMPLATE_GUIDE.md)
- [Feature Specification](../specs/008-template-customization/spec.md)
