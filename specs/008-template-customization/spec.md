# Feature Specification: Advanced Template Customization & Theming

**Feature Branch**: `008-template-customization`  
**Created**: 2025-11-26  
**Milestone**: v0.8.0  
**Prerequisites**: v0.2.0 (Template System) COMPLETE ✅  
**Status**: Planned (Blocked until v0.2.0 - can run in parallel with Feature 007)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Provide advanced template customization and theming system for ansible-doctor-enhanced. Support multiple design variants (minimal, detailed, modern), cascading template overrides at project/collection/role levels, custom CSS/styling, and dark/light theme switching. Enable users to customize documentation appearance without modifying core templates.

## What is Template Customization?

Template Customization provides a flexible theming system for documentation appearance:

- **Design Variants**: Built-in layout options (minimal, detailed, modern) per output format
- **Theme System**: Base theme + variant + custom CSS/styling
- **Cascading Overrides**: Template discovery hierarchy from role → collection → project → embedded
- **CSS Customization**: Link external stylesheets or embed inline CSS
- **Dark/Light Mode**: Toggle theme color scheme via CSS variables and user preference
- **Backward Compatibility**: Theme changes don't break existing template data structures

**Built-in Variants**:
1. **Minimal**: Compact layout, essential information only, single-page output
2. **Detailed**: Verbose layout with expanded sections, examples, and metadata
3. **Modern**: Enhanced UI with rich formatting, collapsible sections, improved navigation

**Template Discovery Hierarchy** (highest priority first):
1. **Role-specific**: `role/.ansibledoctor/templates/`
2. **Collection-specific**: `collection/.ansibledoctor/templates/`
3. **Project-specific**: `project/.ansibledoctor/templates/`
4. **Embedded defaults**: Package built-in templates

**Theme Configuration Example**:
```yaml
# .ansibledoctor.yml
theme:
  name: "modern"                    # Base theme (minimal, detailed, modern)
  variant: "detailed"               # Variant within theme
  color_scheme: "auto"              # auto, light, dark
  css_url: "https://example.com/custom.css"
  css_inline: |
    :root {
      --primary-color: #0066cc;
      --background-color: #ffffff;
    }
  template_dirs:
    - "./.ansibledoctor/templates"  # Project-specific templates
```

## User Scenarios

### US23 - Define Themes in Configuration (Priority: P1) 🎯 MVP

As a documentation maintainer, I want to configure theme settings in `.ansibledoctor.yml` so that I can control the appearance and layout of generated documentation.

**Independent Test**: Set `theme.name: modern` → Generated docs use modern layout

**Acceptance Scenarios**:
1. **Given** `.ansibledoctor.yml` with `theme.name: minimal`, **When** generating docs, **Then** use minimal variant templates (compact layout)
2. **Given** `theme.variant: detailed`, **When** generating docs, **Then** include expanded sections and verbose metadata
3. **Given** `theme.color_scheme: dark`, **When** generating HTML docs, **Then** inject dark mode CSS variables
4. **Given** `theme.css_url: "https://cdn.example.com/style.css"`, **When** generating HTML, **Then** include `<link>` tag to external stylesheet
5. **Given** `theme.css_inline` with custom CSS, **When** generating HTML, **Then** embed CSS in `<style>` tag in document head

---

### US24 - Cascading Template Overrides (Priority: P1) 🎯 MVP

As a developer customizing documentation, I want to override templates at multiple levels (role, collection, project) so that I can customize appearance without modifying embedded templates.

**Independent Test**: Create `project/.ansibledoctor/templates/role.html.j2` → All roles use custom template

**Acceptance Scenarios**:
1. **Given** custom template in `role/.ansibledoctor/templates/role.html.j2`, **When** generating role docs, **Then** use role-specific template (highest priority)
2. **Given** custom template in `collection/.ansibledoctor/templates/role.html.j2`, **When** generating collection roles, **Then** use collection-wide template for all roles in collection
3. **Given** custom template in `project/.ansibledoctor/templates/role.html.j2`, **When** generating project docs, **Then** use project-wide template for all roles in project
4. **Given** no custom templates found, **When** generating docs, **Then** fall back to embedded default templates
5. **Given** role-specific template AND collection template exist, **When** generating, **Then** role-specific takes precedence
6. **Given** template discovery finds custom template, **When** rendering, **Then** log message indicating which template source was used (role/collection/project/embedded)

---

### US25 - Built-in Design Variants (Priority: P1) 🎯 MVP

As a documentation reader, I want to choose between minimal, detailed, or modern layouts so that I can view documentation in the format that best suits my needs.

**Independent Test**: Generate with `--variant minimal` → Compact single-page output

**Acceptance Scenarios**:
1. **Given** `theme.variant: minimal`, **When** generating role docs, **Then** output compact layout with only essential sections (description, variables, dependencies)
2. **Given** `theme.variant: detailed`, **When** generating role docs, **Then** include all sections with expanded metadata (authors, license, tags, full examples)
3. **Given** `theme.variant: modern`, **When** generating HTML docs, **Then** include enhanced UI elements (collapsible sections, syntax highlighting, navigation sidebar)
4. **Given** CLI flag `--variant detailed`, **When** generating, **Then** override config file variant setting
5. **Given** variant not specified, **When** generating, **Then** default to `detailed` variant

---

### US26 - CSS Customization (Priority: P2)

As a documentation maintainer, I want to apply custom CSS styling so that documentation matches my organization's branding and design guidelines.

**Independent Test**: Set `theme.css_url` → HTML output includes external stylesheet link

**Acceptance Scenarios**:
1. **Given** `theme.css_url: "https://example.com/brand.css"`, **When** generating HTML, **Then** inject `<link rel="stylesheet" href="...">` in document head
2. **Given** `theme.css_inline` with CSS rules, **When** generating HTML, **Then** embed CSS in `<style>` tag after base theme styles
3. **Given** both `css_url` and `css_inline`, **When** generating HTML, **Then** include both (URL first, inline second for overrides)
4. **Given** custom CSS references CSS variables (e.g., `var(--primary-color)`), **When** rendering, **Then** CSS variables work correctly with theme color scheme
5. **Given** Markdown or RST output format, **When** generating, **Then** ignore CSS settings (CSS only applies to HTML)

---

### US27 - Dark/Light Theme Switching (Priority: P2)

As a documentation reader, I want to toggle between dark and light themes so that I can read documentation comfortably in different lighting conditions.

**Independent Test**: Open HTML docs with `color_scheme: auto` → Theme matches system preference

**Acceptance Scenarios**:
1. **Given** `theme.color_scheme: auto`, **When** generating HTML docs, **Then** inject CSS with `@media (prefers-color-scheme: dark)` query for automatic theme switching
2. **Given** `theme.color_scheme: light`, **When** generating HTML, **Then** force light theme CSS variables (no dark mode)
3. **Given** `theme.color_scheme: dark`, **When** generating HTML, **Then** force dark theme CSS variables (no light mode)
4. **Given** `color_scheme: auto`, **When** user opens docs in browser with dark mode preference, **Then** documentation displays in dark theme
5. **Given** HTML docs with theme toggle button, **When** user clicks toggle, **Then** switch between light/dark themes via JavaScript and localStorage
6. **Given** theme preference saved in localStorage, **When** user returns to docs, **Then** apply previously selected theme

---

### US28 - Template Inheritance (Priority: P2)

As a template developer, I want to extend base templates using Jinja2 `{% extends %}` so that I can customize specific sections without duplicating entire templates.

**Independent Test**: Create custom template with `{% extends "base/role.html.j2" %}` → Inherits base structure

**Acceptance Scenarios**:
1. **Given** custom template with `{% extends "role.html.j2" %}`, **When** rendering, **Then** inherit structure from embedded default template
2. **Given** custom template overrides `{% block header %}`, **When** rendering, **Then** use custom header block, keep other blocks from parent
3. **Given** custom template uses `{{ super() }}`, **When** rendering, **Then** include parent block content plus custom additions
4. **Given** template extends non-existent parent, **When** rendering, **Then** raise clear error with template name and search paths
5. **Given** nested template inheritance (custom extends base, base extends root), **When** rendering, **Then** correctly resolve all inheritance levels

---

## Success Criteria

**SC-001**: Load theme configuration from `.ansibledoctor.yml` with `theme.name`, `theme.variant`, and `theme.color_scheme` options  
**SC-002**: Support 4-level template discovery hierarchy: role-specific > collection-specific > project-specific > embedded defaults  
**SC-003**: Provide 3 built-in variants per format: minimal (compact), detailed (verbose), modern (enhanced UI)  
**SC-004**: Inject custom CSS into HTML output via `theme.css_url` (external link) or `theme.css_inline` (embedded styles)  
**SC-005**: Theme switching maintains backward compatibility (existing templates work without modification)  
**SC-006**: Template inheritance allows extending base templates via Jinja2 `{% extends %}` directive  
**SC-007**: Dark/light theme switching via `color_scheme: auto` with CSS media query or manual toggle  
**SC-008**: Theme toggle button in HTML output with JavaScript to switch themes and save preference  
**SC-009**: Log template source (role/collection/project/embedded) during generation for debugging  
**SC-010**: Custom CSS applies to HTML output only (Markdown/RST ignore CSS settings)

---

## Technical Constraints

**TC-001**: Themes are template + CSS combinations, not separate rendering engines (reuse existing TemplateEngine)  
**TC-002**: All variants use same TemplateContext data structure (no variant-specific data models)  
**TC-003**: Custom CSS applies to HTML output only (Markdown/RST use structure/content only)  
**TC-004**: Template discovery uses existing TemplateLoader protocol from Feature 002  
**TC-005**: CSS variables define color scheme: `--primary-color`, `--background-color`, `--text-color`, `--border-color`, etc.  
**TC-006**: Dark mode CSS uses `@media (prefers-color-scheme: dark)` for automatic switching  
**TC-007**: Theme toggle JavaScript must be optional (docs work without JS, toggle enhances UX)  
**TC-008**: Maximum 3 variant options per theme to avoid overwhelming users  
**TC-009**: Template inheritance depth limited to 5 levels to prevent circular references and performance issues  
**TC-010**: Custom templates must use `.j2` extension and valid Jinja2 syntax

---

## Key Entities

### ThemeConfig
**Purpose**: Store theme configuration from `.ansibledoctor.yml`  
**Attributes**:
- `name: str` - Base theme name (minimal, detailed, modern)
- `variant: str` - Variant within theme (minimal, detailed, modern)
- `color_scheme: Literal['auto', 'light', 'dark']` - Color scheme preference
- `css_url: Optional[str]` - External stylesheet URL
- `css_inline: Optional[str]` - Inline CSS to embed
- `template_dirs: List[Path]` - Additional template search directories

**Operations**:
- `from_config(config: Dict) -> ThemeConfig` - Parse from YAML configuration
- `get_variant_template_name(base_name: str) -> str` - Resolve variant template (e.g., `role.minimal.html.j2`)
- `has_custom_css() -> bool` - Check if custom CSS is configured

### CascadingTemplateLoader
**Purpose**: Implement 4-level template discovery hierarchy  
**Attributes**:
- `role_path: Optional[Path]` - Role-specific template directory
- `collection_path: Optional[Path]` - Collection-specific template directory
- `project_path: Optional[Path]` - Project-specific template directory
- `embedded_loader: PackageLoader` - Built-in template loader
- `search_paths: List[Path]` - Ordered list of search paths

**Operations**:
- `get_source(name: str) -> Tuple[str, str, Callable]` - Find template in cascade hierarchy
- `list_templates() -> List[str]` - List all available templates across all sources
- `_search_custom_paths(name: str) -> Optional[Path]` - Search custom template directories
- `_log_template_source(name: str, source: str)` - Log which template source was used

### VariantTemplateResolver
**Purpose**: Resolve variant-specific template names  
**Attributes**:
- `variant: str` - Current variant (minimal, detailed, modern)
- `format: str` - Output format (html, markdown, rst)
- `fallback_chain: List[str]` - Template name fallback order

**Operations**:
- `resolve_template_name(base: str) -> str` - Get variant template name (e.g., `role.html.j2` → `role.modern.html.j2`)
- `build_fallback_chain(base: str) -> List[str]` - Create fallback list (variant-specific → base → default)
- `variant_exists(template_name: str) -> bool` - Check if variant template exists

### CSSInjector
**Purpose**: Inject custom CSS into HTML output  
**Attributes**:
- `theme_config: ThemeConfig` - Theme configuration with CSS settings
- `color_scheme: str` - Color scheme (auto, light, dark)
- `base_css: str` - Base theme CSS

**Operations**:
- `generate_css_tags() -> str` - Create `<link>` and `<style>` tags for HTML head
- `inject_theme_variables(color_scheme: str) -> str` - Generate CSS custom properties for colors
- `wrap_dark_mode_css(css: str) -> str` - Wrap CSS in `@media (prefers-color-scheme: dark)` query
- `generate_theme_toggle_script() -> str` - Create JavaScript for theme toggle button

### ThemeToggleGenerator
**Purpose**: Generate theme toggle UI and JavaScript  
**Attributes**:
- `enabled: bool` - Whether theme toggle is enabled
- `default_scheme: str` - Default color scheme (light, dark, auto)

**Operations**:
- `generate_toggle_html() -> str` - Create theme toggle button markup
- `generate_toggle_script() -> str` - JavaScript for theme switching and localStorage
- `generate_theme_icons() -> str` - SVG icons for light/dark mode buttons

---

## Architecture

### Component Interactions

```
┌────────────────────────────────────────────────────────────────┐
│                    Documentation Generator                      │
│                      (from Feature 002)                         │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  ThemeConfig    │
                   │  (from .yml)    │
                   └────────┬────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │ CascadingTemplateLoader     │
              │ (4-level template search)   │
              └─────────┬───────────────────┘
                        │
           ┌────────────┴───────────┐
           ▼                        ▼
  ┌─────────────────┐      ┌─────────────────┐
  │ VariantTemplate│      │ Custom Template │
  │    Resolver     │      │   Directories   │
  └────────┬────────┘      └────────┬────────┘
           │                        │
           └────────────┬───────────┘
                        ▼
               ┌─────────────────┐
               │  Jinja2 Render  │
               │  + Inheritance  │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  CSSInjector    │
               │  (HTML only)    │
               └────────┬────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ ThemeToggleGenerator │
              │ (optional JS toggle) │
              └──────────┬───────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Final HTML     │
                │  with Theme     │
                └─────────────────┘
```

### Template Discovery Flow

```
1. Parse .ansibledoctor.yml → ThemeConfig
2. Create CascadingTemplateLoader with search paths:
   - role/.ansibledoctor/templates/
   - collection/.ansibledoctor/templates/
   - project/.ansibledoctor/templates/
   - embedded package templates
3. Resolve template name with VariantTemplateResolver:
   - Input: "role.html.j2", variant="modern"
   - Try: "role.modern.html.j2" → "role.html.j2" → "role.default.html.j2"
4. Search cascade:
   - Check role-specific path
   - Check collection-specific path
   - Check project-specific path
   - Fall back to embedded templates
5. Log template source for debugging
6. Render with Jinja2 (supports {% extends %})
7. If HTML: Inject CSS via CSSInjector
8. If HTML + toggle enabled: Add theme toggle UI + JavaScript
9. Output final documentation
```

---

## Configuration Schema

```yaml
# .ansibledoctor.yml
theme:
  # Base theme (affects template selection)
  name: "modern"                    # Options: minimal, detailed, modern
  
  # Variant within theme
  variant: "detailed"               # Options: minimal, detailed, modern
  
  # Color scheme
  color_scheme: "auto"              # Options: auto (system preference), light, dark
  
  # External stylesheet URL
  css_url: "https://cdn.example.com/custom.css"
  
  # Inline CSS (embedded in <style> tag)
  css_inline: |
    :root {
      --primary-color: #0066cc;
      --secondary-color: #ff6600;
      --background-color: #ffffff;
      --text-color: #333333;
    }
  
  # Theme toggle button in HTML output
  enable_toggle: true               # Show dark/light theme toggle button
  
  # Additional template search directories
  template_dirs:
    - "./.ansibledoctor/templates"  # Project-specific templates
    - "./custom_templates"          # Additional custom templates

# Output formats (from Feature 002)
output:
  formats:
    - html                          # CSS applies to HTML only
    - markdown                      # CSS ignored for Markdown
```

### CLI Flags

```bash
# Override theme variant
ansible-doctor generate --variant minimal ./roles/webserver

# Override color scheme
ansible-doctor generate --color-scheme dark ./roles/webserver

# Disable theme toggle
ansible-doctor generate --no-theme-toggle ./roles/webserver

# Specify custom template directory
ansible-doctor generate --template-dir ./my_templates ./roles/webserver
```

---

## Built-in Variants

### Minimal Variant
**Purpose**: Compact, essential information only  
**Characteristics**:
- Single-page output (no separate sections)
- Only required sections: Description, Variables, Dependencies
- No metadata (authors, license, tags)
- Minimal styling, fast loading
- Best for: Quick reference, CI/CD pipelines

**Example**: `role.minimal.html.j2`
```jinja2
<!DOCTYPE html>
<html>
<head>
  <title>{{ role.name }}</title>
  <style>body { font-family: sans-serif; max-width: 800px; margin: 0 auto; }</style>
</head>
<body>
  <h1>{{ role.name }}</h1>
  <p>{{ role.description }}</p>
  
  <h2>{{ t('role.variables') }}</h2>
  <ul>
    {% for var in role.variables %}
    <li><code>{{ var.name }}</code>: {{ var.description }}</li>
    {% endfor %}
  </ul>
</body>
</html>
```

### Detailed Variant
**Purpose**: Comprehensive documentation with all metadata  
**Characteristics**:
- Multi-section layout with navigation
- All sections: Description, Variables, Dependencies, Examples, Authors, License, Tags
- Expanded metadata and examples
- Rich formatting and syntax highlighting
- Best for: Complete reference documentation

**Example**: `role.detailed.html.j2`
```jinja2
{% extends "base/role.html.j2" %}

{% block metadata %}
<section class="metadata">
  <h2>{{ t('role.metadata') }}</h2>
  <dl>
    <dt>{{ t('role.authors') }}</dt>
    <dd>{{ role.meta.galaxy_info.author }}</dd>
    
    <dt>{{ t('role.license') }}</dt>
    <dd>{{ role.meta.galaxy_info.license }}</dd>
    
    <dt>{{ t('role.platforms') }}</dt>
    <dd>{{ role.meta.galaxy_info.platforms | join(', ') }}</dd>
  </dl>
</section>
{% endblock %}

{% block examples %}
<section class="examples">
  <h2>{{ t('role.examples') }}</h2>
  {% for example in role.examples %}
  <pre><code class="yaml">{{ example.code }}</code></pre>
  <p>{{ example.description }}</p>
  {% endfor %}
</section>
{% endblock %}
```

### Modern Variant
**Purpose**: Enhanced UI with interactive elements  
**Characteristics**:
- Modern design with improved UX
- Collapsible sections (JavaScript-enhanced)
- Syntax highlighting for code blocks
- Navigation sidebar with anchors
- Responsive layout (mobile-friendly)
- Best for: Interactive web documentation

**Example**: `role.modern.html.j2`
```jinja2
{% extends "base/role.html.j2" %}

{% block head_extra %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
{% endblock %}

{% block navigation %}
<nav class="sidebar">
  <ul>
    <li><a href="#overview">{{ t('role.overview') }}</a></li>
    <li><a href="#variables">{{ t('role.variables') }}</a></li>
    <li><a href="#dependencies">{{ t('role.dependencies') }}</a></li>
    <li><a href="#examples">{{ t('role.examples') }}</a></li>
  </ul>
</nav>
{% endblock %}

{% block variables %}
<section id="variables" class="collapsible">
  <h2 onclick="toggleSection('variables')">
    {{ t('role.variables') }}
    <span class="toggle-icon">▼</span>
  </h2>
  <div class="content">
    <table class="variables-table">
      <thead>
        <tr>
          <th>{{ t('variable.name') }}</th>
          <th>{{ t('variable.default') }}</th>
          <th>{{ t('variable.description') }}</th>
        </tr>
      </thead>
      <tbody>
        {% for var in role.variables %}
        <tr>
          <td><code>{{ var.name }}</code></td>
          <td><code>{{ var.default | default('—') }}</code></td>
          <td>{{ var.description }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>
{% endblock %}
```

---

## CSS Variables and Color Schemes

### Light Theme (Default)
```css
:root {
  /* Primary colors */
  --primary-color: #0066cc;
  --secondary-color: #ff6600;
  --accent-color: #00cc66;
  
  /* Background colors */
  --background-color: #ffffff;
  --background-secondary: #f5f5f5;
  --background-code: #f8f8f8;
  
  /* Text colors */
  --text-color: #333333;
  --text-secondary: #666666;
  --text-muted: #999999;
  
  /* Border colors */
  --border-color: #dddddd;
  --border-light: #eeeeee;
  
  /* Interactive elements */
  --link-color: #0066cc;
  --link-hover: #0052a3;
  --button-bg: #0066cc;
  --button-text: #ffffff;
}
```

### Dark Theme (Auto-detected)
```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Primary colors (adjusted for dark mode) */
    --primary-color: #3399ff;
    --secondary-color: #ff9933;
    --accent-color: #33ff99;
    
    /* Background colors */
    --background-color: #1a1a1a;
    --background-secondary: #2a2a2a;
    --background-code: #222222;
    
    /* Text colors */
    --text-color: #e0e0e0;
    --text-secondary: #b0b0b0;
    --text-muted: #808080;
    
    /* Border colors */
    --border-color: #404040;
    --border-light: #333333;
    
    /* Interactive elements */
    --link-color: #3399ff;
    --link-hover: #66b3ff;
    --button-bg: #3399ff;
    --button-text: #ffffff;
  }
}
```

### Theme Toggle JavaScript
```javascript
// Embedded in HTML output when theme.enable_toggle: true
(function() {
  const STORAGE_KEY = 'ansible-doctor-theme';
  const toggle = document.getElementById('theme-toggle');
  
  // Get current theme from localStorage or system preference
  function getCurrentTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }
  
  // Apply theme to document
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateToggleIcon(theme);
  }
  
  // Update toggle button icon
  function updateToggleIcon(theme) {
    const icon = toggle.querySelector('.icon');
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
  
  // Toggle between light and dark
  function toggleTheme() {
    const current = getCurrentTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  }
  
  // Initialize
  applyTheme(getCurrentTheme());
  toggle.addEventListener('click', toggleTheme);
})();
```

---

## Template Inheritance Examples

### Base Template (Embedded)
```jinja2
{# templates/base/role.html.j2 #}
<!DOCTYPE html>
<html lang="{{ language }}">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}{{ role.name }} - {{ t('role.documentation') }}{% endblock %}</title>
  {% block head_extra %}{% endblock %}
  {{ css_tags | safe }}
</head>
<body>
  {% block navigation %}{% endblock %}
  
  <main>
    {% block header %}
    <header>
      <h1>{{ role.name }}</h1>
      {% if context.breadcrumb %}
      {{ context.breadcrumb | safe }}
      {% endif %}
    </header>
    {% endblock %}
    
    {% block content %}
    {% block description %}
    <section id="description">
      <h2>{{ t('role.description') }}</h2>
      <p>{{ role.description }}</p>
    </section>
    {% endblock %}
    
    {% block variables %}
    <section id="variables">
      <h2>{{ t('role.variables') }}</h2>
      {# Variable rendering #}
    </section>
    {% endblock %}
    
    {% block dependencies %}
    <section id="dependencies">
      <h2>{{ t('role.dependencies') }}</h2>
      {# Dependencies rendering #}
    </section>
    {% endblock %}
    {% endblock %}
  </main>
  
  {% block footer %}
  <footer>
    <p>{{ t('generated_by', tool='ansible-doctor-enhanced') }}</p>
  </footer>
  {% endblock %}
  
  {% block scripts %}{% endblock %}
</body>
</html>
```

### Custom Template (Project-specific Override)
```jinja2
{# project/.ansibledoctor/templates/role.html.j2 #}
{% extends "base/role.html.j2" %}

{# Add custom CSS #}
{% block head_extra %}
<link rel="stylesheet" href="/assets/company-branding.css">
{% endblock %}

{# Override header to add company logo #}
{% block header %}
<header class="company-header">
  <img src="/assets/logo.png" alt="Company Logo" class="logo">
  {{ super() }}
</header>
{% endblock %}

{# Extend footer with additional links #}
{% block footer %}
{{ super() }}
<div class="company-footer">
  <a href="/docs">Documentation Home</a> |
  <a href="/support">Support</a> |
  <a href="/contact">Contact Us</a>
</div>
{% endblock %}
```

---

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.2.0 (Template System) is COMPLETE and stable
2. ✅ v0.3.0 (Documentation Generation) is COMPLETE and stable
3. ✅ TemplateEngine supports Jinja2 inheritance (`{% extends %}`, `{% block %}`)
4. ✅ TemplateLoader protocol works for custom template directories
5. ✅ HTML output generation works correctly
6. ✅ Feature 005 (i18n) is COMPLETE for translation keys in templates
7. ✅ No critical bugs in template rendering

**Gate**: This feature CAN run in parallel with Feature 007 (Hierarchical Context) as they have minimal dependencies. Feature 002 (Template System) must be complete.

---

## Dependencies

### Upstream (Must Complete First)
- ✅ Feature 002 (Template System) - For template rendering and Jinja2 support

### Optional Integration
- 🔄 Feature 005 (i18n Support) - For multi-language theme labels (recommended but not required)
- 🔄 Feature 007 (Hierarchical Context) - Theme can display breadcrumbs if available

### Downstream (Can Start After This)
- Future features that customize documentation appearance
- Plugin system for third-party themes

---

## Out of Scope

**Explicitly NOT included in v0.8.0**:
- ❌ JavaScript-based themes requiring build tools (webpack, npm, etc.)
- ❌ Dynamic CSS generation based on role metadata
- ❌ Live theme preview in CLI or web UI
- ❌ Theme marketplace or downloadable theme packages
- ❌ Automatic dark mode detection with JavaScript (use CSS media query only)
- ❌ SCSS/SASS preprocessing (only plain CSS)
- ❌ Custom fonts or icon libraries (use system fonts and Unicode icons)
- ❌ Responsive breakpoints beyond basic mobile/desktop (no tablet-specific layouts)

These may be considered for future versions (v0.9.0+) based on user feedback.

---

## Testing Strategy

### Unit Tests
- `test_theme_config_loads_from_yaml()` - Parse theme configuration
- `test_cascading_template_loader_hierarchy()` - Verify 4-level search order
- `test_variant_template_resolver()` - Resolve variant-specific template names
- `test_css_injector_generates_tags()` - Create `<link>` and `<style>` tags
- `test_css_injector_wraps_dark_mode()` - Wrap CSS in media query
- `test_theme_toggle_generator()` - Generate toggle button HTML and JavaScript
- `test_template_inheritance()` - Verify Jinja2 `{% extends %}` works
- `test_custom_template_overrides_embedded()` - Custom template takes precedence

### Integration Tests
- `test_generate_with_minimal_variant()` - End-to-end minimal layout generation
- `test_generate_with_modern_variant()` - End-to-end modern layout with features
- `test_custom_css_url_in_output()` - External stylesheet link appears in HTML
- `test_custom_css_inline_in_output()` - Inline CSS embedded in HTML
- `test_theme_toggle_works_in_browser()` - JavaScript theme switching (manual browser test)
- `test_role_template_override()` - Role-specific template used correctly
- `test_project_template_override()` - Project-wide template applies to all roles
- `test_markdown_ignores_css()` - CSS settings don't affect Markdown output

### Performance Tests
- `test_template_loading_cached()` - Template discovery results cached
- `test_css_injection_minimal_overhead()` - CSS injection adds <50ms

---

## v1.0.0 Readiness

Completing this feature (v0.8.0) provides advanced customization capabilities for documentation appearance. Combined with Feature 007 (Hierarchical Context), v0.8.0 delivers:

- **Multi-language documentation** (Feature 005)
- **Project-level documentation** (Feature 006)
- **Hierarchical navigation** (Feature 007)
- **Custom themes and styling** (Feature 008)

After v0.8.0:
- **v0.9.0**: Stabilization, polish, performance tuning, bug fixes, documentation improvements
- **v1.0.0**: Production release with stable API, comprehensive documentation, migration guides

v0.8.0 completes the feature set for v1.0.0. v0.9.0 focuses exclusively on quality, performance, and user experience improvements.

---

## Notes

- **Feature 002 Integration**: Reuse existing TemplateEngine, TemplateLoader, and TemplateContext
- **Feature 005 Integration**: Use i18n translation keys for theme labels (optional but recommended)
- **Feature 007 Integration**: Display breadcrumbs from hierarchical context if available
- **Backward Compatibility**: Existing templates work without modification; themes are additive
- **CSS-Only Theming**: Dark/light mode uses CSS custom properties and media queries (no JavaScript required for basic functionality)
- **Progressive Enhancement**: Theme toggle button enhances UX but docs work without JavaScript
- **Performance**: Template discovery caching is critical for multi-language generation (Feature 005 generates multiple outputs)
- **Graceful Degradation**: If custom template has errors, fall back to embedded default with warning
