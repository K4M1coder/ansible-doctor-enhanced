---
description: "Research document for Feature 008: Template Customization & Theming"
---

# Research: Template Customization & Theming (Feature 008)

## T321: CSS Variable Schema & Color Token Map

### CSS Variable Naming Convention

Following industry standards (Tailwind CSS, Bootstrap 5, Material Design), we adopt a semantic naming approach:

```css
/* Color Tokens - Primary Palette */
--ad-color-primary: #2563eb;        /* Brand color */
--ad-color-primary-light: #3b82f6;  /* Hover states */
--ad-color-primary-dark: #1d4ed8;   /* Active states */

/* Color Tokens - Semantic Colors */
--ad-color-success: #10b981;
--ad-color-warning: #f59e0b;
--ad-color-error: #ef4444;
--ad-color-info: #0ea5e9;

/* Color Tokens - Neutral Palette */
--ad-color-bg: #ffffff;
--ad-color-bg-secondary: #f8fafc;
--ad-color-bg-tertiary: #f1f5f9;
--ad-color-text: #1e293b;
--ad-color-text-secondary: #64748b;
--ad-color-text-muted: #94a3b8;
--ad-color-border: #e2e8f0;

/* Dark Mode Overrides */
[data-theme="dark"] {
  --ad-color-bg: #0f172a;
  --ad-color-bg-secondary: #1e293b;
  --ad-color-bg-tertiary: #334155;
  --ad-color-text: #f8fafc;
  --ad-color-text-secondary: #cbd5e1;
  --ad-color-text-muted: #64748b;
  --ad-color-border: #334155;
}

/* Typography Tokens */
--ad-font-family: system-ui, -apple-system, sans-serif;
--ad-font-family-mono: ui-monospace, SFMono-Regular, monospace;
--ad-font-size-base: 1rem;
--ad-font-size-sm: 0.875rem;
--ad-font-size-lg: 1.125rem;
--ad-font-size-xl: 1.25rem;
--ad-font-size-2xl: 1.5rem;
--ad-font-size-3xl: 1.875rem;
--ad-line-height: 1.6;

/* Spacing Tokens */
--ad-spacing-xs: 0.25rem;
--ad-spacing-sm: 0.5rem;
--ad-spacing-md: 1rem;
--ad-spacing-lg: 1.5rem;
--ad-spacing-xl: 2rem;
--ad-spacing-2xl: 3rem;

/* Border Radius */
--ad-radius-sm: 0.25rem;
--ad-radius-md: 0.375rem;
--ad-radius-lg: 0.5rem;
--ad-radius-xl: 0.75rem;

/* Shadows */
--ad-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--ad-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--ad-shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
```

### Color Token Categories

| Category | Purpose | Variables |
| ---------- | --------- | ----------- |
| Primary | Brand identity | `--ad-color-primary`, `-light`, `-dark` |
| Semantic | Status indicators | success, warning, error, info |
| Neutral | Background, text, borders | bg, text, border variants |
| Typography | Font settings | font-family, sizes, line-height |
| Spacing | Layout consistency | xs through 2xl |
| Effects | Visual polish | radius, shadows |

### Decision: Use `--ad-` Prefix

Rationale:

- Avoids collisions with user CSS
- `ad` = Ansible Doctor (clear namespace)
- Short but descriptive

---

## T322: TemplateLoader Fallback Chain & Caching

### Current Template Loader Architecture

From `ansibledoctor/generator/loaders.py`:

- `EmbeddedTemplateLoader` - Loads from package resources
- `FileSystemTemplateLoader` - Loads from custom directories
- Both use `PackageLoader` or `FileSystemLoader` for Jinja2 includes

### Proposed Cascading Template Discovery

```
Discovery Order (highest to lowest priority):
1. role/.ansibledoctor/templates/         # Role-specific override
2. collection/.ansibledoctor/templates/   # Collection-wide templates
3. project/.ansibledoctor/templates/      # Project-level templates
4. ~/.ansibledoctor/templates/            # User-global templates
5. ansibledoctor/generator/templates/     # Package embedded (fallback)
```

### Caching Strategy

```python
@dataclass
class TemplateDiscoveryResult:
    template_path: Path
    source_level: str  # "role", "collection", "project", "user", "embedded"
    cached_at: datetime
    
class CascadingTemplateLoader:
    def __init__(self):
        self._cache: dict[str, TemplateDiscoveryResult] = {}
        self._cache_ttl = 300  # 5 minutes
    
    def find_template(self, name: str, context_path: Path) -> TemplateDiscoveryResult:
        cache_key = f"{context_path}:{name}"
        if cache_key in self._cache:
            result = self._cache[cache_key]
            if (datetime.now() - result.cached_at).seconds < self._cache_ttl:
                return result
        # ... discovery logic
```

### API Changes Required

```python
# New function in loaders.py
def create_cascading_loader(
    context_path: Path,
    variant: str = "default",
    custom_paths: list[Path] | None = None
) -> CascadingTemplateLoader:
    """Create a template loader with cascading discovery."""
    pass
```

---

## T323: Jinja2 Inheritance Across Search Paths

### Current Behavior

Jinja2's `{% extends %}` and `{% include %}` resolve templates relative to the loader's search path. With multiple loaders (cascading), we need special handling.

### Edge Cases

1. **Cross-level inheritance**: Role template extends collection template
   - Solution: Use `PrefixLoader` or `ChoiceLoader` with namespaced paths
2. **Circular includes**: A includes B, B includes A
   - Solution: Jinja2 handles this with recursion detection
3. **Missing parent template**: Child extends non-existent base
   - Solution: Fallback to embedded templates with clear error message

### Proposed Solution: ChoiceLoader with Namespaces

```python
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader

def build_environment(search_paths: list[Path]) -> Environment:
    loaders = [
        FileSystemLoader(str(path)) 
        for path in search_paths 
        if path.exists()
    ]
    # Always include embedded as fallback
    loaders.append(PackageLoader("ansibledoctor.generator", "templates"))
    
    return Environment(loader=ChoiceLoader(loaders))
```

### Validation Requirements

- Check template syntax before rendering
- Log template source for debugging: `"Using template: role/.ansibledoctor/templates/role.html.j2"`
- Warn if template overrides embedded but doesn't extend it

---

## T324: Security & Sandboxing for Theme Toggle JS

### Risk Assessment

| Risk | Severity | Mitigation |
| ------ | ---------- | ------------ |
| XSS via user templates | High | Sandbox Jinja2, escape output |
| Arbitrary code execution | Critical | No `exec`/`eval` in templates |
| File system access | Medium | Restrict template paths |
| Network requests | Low | JS toggle is self-contained |

### Theme Toggle JS Requirements

The toggle JavaScript must be:

1. **Self-contained**: No external dependencies
2. **Safe**: No `eval()`, `innerHTML` with user content
3. **Accessible**: ARIA attributes, keyboard support
4. **Persistent**: Uses `localStorage` for preference

### Proposed Toggle Implementation

```javascript
// Safe theme toggle - no external dependencies
(function() {
  const STORAGE_KEY = 'ad-theme';
  const toggle = document.getElementById('ad-theme-toggle');
  
  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  
  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    if (toggle) {
      toggle.setAttribute('aria-pressed', theme === 'dark');
    }
  }
  
  // Initialize
  setTheme(getPreferredTheme());
  
  // Toggle handler
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();
```

### Jinja2 Sandbox Configuration

```python
from jinja2.sandbox import SandboxedEnvironment

def create_safe_environment():
    env = SandboxedEnvironment(
        autoescape=True,  # Escape HTML by default
        undefined=StrictUndefined,  # Fail on undefined variables
    )
    # Block dangerous operations
    env.globals.pop('range', None)  # Prevent DoS loops
    return env
```

### Recommendation

1. Use `SandboxedEnvironment` for user templates
2. Embedded templates can use regular `Environment`
3. Theme toggle JS is hardcoded (not user-customizable)
4. Add `--no-theme-toggle` CLI flag to disable JS injection

---

## T325: CLI Flags & Configuration Precedence

### CLI Flags Mapping

| CLI Flag | YAML Config | Default | Description |
| ---------- | ------------- | --------- | ------------- |
| `--variant` | `theme.variant` | `detailed` | Template variant |
| `--color-scheme` | `theme.color_scheme` | `auto` | light/dark/auto |
| `--no-theme-toggle` | `theme.enable_toggle` | `true` | Disable JS toggle |
| `--template-dir` | `template.paths` | `[]` | Custom template paths |
| `--css-url` | `theme.css_url` | `null` | External CSS URL |
| `--css-inline` | `theme.css_inline` | `null` | Inline CSS content |

### Precedence Order (highest to lowest)

```
1. CLI flags (--variant modern)
2. Environment variables (AD_THEME_VARIANT=modern)
3. Role-level .ansibledoctor.yml
4. Collection-level .ansibledoctor.yml
5. Project-level .ansibledoctor.yml
6. User-level ~/.ansibledoctor.yml
7. Built-in defaults
```

### Example .ansibledoctor.yml

```yaml
# Theme configuration
theme:
  name: "ansible-doctor"      # Theme name (for future marketplace)
  variant: "detailed"         # minimal | detailed | modern
  color_scheme: "auto"        # light | dark | auto
  enable_toggle: true         # Show dark/light toggle button

  # Custom CSS
  css_url: "https://example.com/custom.css"
  css_inline: |
    .ad-header { background: var(--ad-color-primary); }

# Template discovery paths (in addition to defaults)
template:
  paths:
    - ".ansibledoctor/templates"
    - "docs/templates"
```

### CLI Implementation Example

```python
@click.option(
    "--variant",
    type=click.Choice(["minimal", "detailed", "modern"]),
    help="Template variant to use",
)
@click.option(
    "--color-scheme",
    type=click.Choice(["light", "dark", "auto"]),
    help="Color scheme for HTML output",
)
@click.option(
    "--no-theme-toggle",
    is_flag=True,
    help="Disable dark/light mode toggle in HTML",
)
@click.option(
    "--template-dir",
    type=click.Path(exists=True, file_okay=False),
    multiple=True,
    help="Additional template search paths",
)
def generate(variant, color_scheme, no_theme_toggle, template_dir):
    # CLI overrides config
    config = load_config()
    if variant:
        config.theme.variant = variant
    if color_scheme:
        config.theme.color_scheme = color_scheme
    if no_theme_toggle:
        config.theme.enable_toggle = False
    if template_dir:
        config.template.paths = list(template_dir) + config.template.paths
```

---

## Summary & Recommendations

### Phase 0 Complete

All research tasks (T321-T325) complete:

1. **CSS Variables**: Use `--ad-` prefix, semantic naming, 20+ tokens
2. **Template Loader**: Cascading discovery with 5 levels, caching
3. **Jinja2 Inheritance**: Use `ChoiceLoader`, validate templates
4. **Security**: `SandboxedEnvironment`, self-contained JS toggle
5. **CLI Precedence**: 7-level hierarchy, CLI > Env > Config > Defaults

### Next Steps (Phase 1)

- T326: Create `ThemeConfig` Pydantic model
- T327: Design `CascadingTemplateLoader` contract
- T328: Design `VariantTemplateResolver` contract
- T329: Design `CSSInjector` interface
- T330: Update `TemplateContext` with theme fields
- T331: Collate contracts for review
