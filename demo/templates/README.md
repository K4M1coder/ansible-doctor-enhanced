# Demo Templates and CSS

This directory contains demo templates and CSS examples for Feature 008 - Template Customization & Theming.

## Template Variants

### Minimal (`role.minimal.html.j2`)
Compact output with essential information only:
- Role name and description
- Variables list (name + default)
- Tasks list (name only)

Best for quick reference docs or embedding.

### Detailed (`role.detailed.html.j2`)
Full documentation with all sections:
- Metadata (author, license, version)
- Variables table (name, type, default, description)
- Tasks with descriptions and tags
- Dependencies
- Examples

Best for comprehensive documentation.

### Modern (`role.modern.html.j2`)
Contemporary styling with enhanced visual elements:
- Hero section with badges
- Card-based layout
- Variable grid display
- Task timeline visualization
- Gradient accents

Best for user-facing docs and portfolios.

## CSS Examples

### `css/sample-theme.css`
Complete custom theme CSS showing:
- Custom brand colors (green palette)
- Dark mode color overrides
- Card hover effects
- Table styling
- Theme toggle positioning
- Print styles
- Responsive breakpoints

Usage:
```bash
ansible-doctor role . --css-url demo/css/sample-theme.css
```

### `css/inline-overrides.css`
Minimal inline CSS for quick overrides:
- Primary color change
- Font size adjustments
- Container padding

Usage:
```bash
ansible-doctor role . --css-inline "$(cat demo/css/inline-overrides.css)"
```

## Usage Examples

### Using Minimal Variant
```bash
ansible-doctor role ./my-role --variant minimal --format html
```

### Using Modern Variant with Custom CSS
```bash
ansible-doctor role ./my-role \
  --variant modern \
  --format html \
  --css-url https://cdn.example.com/theme.css
```

### Using Detailed Variant with Dark Mode
```bash
ansible-doctor role ./my-role \
  --variant detailed \
  --format html \
  --color-scheme dark
```

### Using Theme Toggle
```bash
ansible-doctor role ./my-role \
  --format html \
  --theme-toggle
```

## Template Variables

Templates receive these variables in context:

| Variable | Type | Description |
|----------|------|-------------|
| `role` | Role | Role metadata object |
| `variables` | list[Variable] | Role variables |
| `tasks` | list[Task] | Role tasks |
| `dependencies` | list | Role dependencies |
| `examples` | list[Example] | Usage examples |
| `breadcrumb` | list[BreadcrumbItem] | Navigation breadcrumb |
| `css_tags` | list[str] | CSS tags for head |
| `theme_toggle` | str | Theme toggle HTML/JS |
| `t` | callable | Translation function |

## Custom Template Creation

To create custom templates:

1. Copy one of the variant templates as a starting point
2. Place in your role's `templates/` directory or project root
3. Name it following the pattern: `role.{name}.html.j2`
4. Templates inherit base CSS variables automatically

Example custom template location:
```
my-role/
├── templates/
│   └── role.custom.html.j2  # Custom template
├── tasks/
├── defaults/
└── meta/
```

## CSS Variables Reference

| Variable | Default (Light) | Dark |
|----------|----------------|------|
| `--ad-color-primary` | #2563eb | #2563eb |
| `--ad-color-bg` | #ffffff | #0f172a |
| `--ad-color-text` | #1e293b | #f8fafc |
| `--ad-color-border` | #e2e8f0 | #334155 |
| `--ad-font-family` | system-ui | system-ui |
| `--ad-spacing-md` | 1rem | 1rem |
| `--ad-radius-md` | 0.375rem | 0.375rem |

See `ansibledoctor/generator/css_injector.py` for full list.
