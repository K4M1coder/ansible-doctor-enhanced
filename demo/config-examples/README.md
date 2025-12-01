# Example configs for ansible-doctor-enhanced theming

This directory contains example configuration files demonstrating various theme options.

## Configuration Files

| File | Description |
|------|-------------|
| `minimal-theme.ansibledoctor.yml` | Compact output with essential info only |
| `detailed-theme.ansibledoctor.yml` | Full documentation (default variant) |
| `modern-theme.ansibledoctor.yml` | Contemporary card-based styling |
| `dark-theme.ansibledoctor.yml` | Forced dark mode |
| `custom-css.ansibledoctor.yml` | External CSS and inline overrides |

## Usage

Copy a config file to your role/collection directory:

```bash
cp minimal-theme.ansibledoctor.yml /path/to/my-role/.ansibledoctor.yml
```

Or reference the variant directly via CLI:

```bash
ansible-doctor role ./my-role --variant minimal --format html
```

## Theme Variants

### Minimal
Best for: Quick reference, embedding in other docs
- Compact output
- Essential info only
- No toggle button

### Detailed (Default)
Best for: Comprehensive documentation
- Full metadata
- Tables for variables
- All sections included

### Modern
Best for: User-facing portfolios, documentation sites
- Card-based layout
- Hero section with badges
- Visual timeline for tasks

## Color Schemes

| Scheme | Description |
|--------|-------------|
| `light` | Force light background |
| `dark` | Force dark background |
| `auto` | Respects user's OS/browser preference (default) |

## CSS Customization

See `../css/` for CSS examples:
- `sample-theme.css` - Complete custom theme
- `inline-overrides.css` - Minimal overrides

## Environment Variables

Override config file settings:

```bash
export ANSIBLE_DOCTOR_THEME_VARIANT=modern
export ANSIBLE_DOCTOR_COLOR_SCHEME=dark
export ANSIBLE_DOCTOR_THEME_TOGGLE=true
```

## CLI Flags

Override all settings via CLI:

```bash
ansible-doctor role ./my-role \
  --variant modern \
  --color-scheme auto \
  --theme-toggle \
  --css-url https://example.com/theme.css
```

Precedence: CLI > Environment > Config File > Defaults
