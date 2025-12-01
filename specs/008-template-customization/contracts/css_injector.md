---
description: "Contract for CSSInjector and ThemeToggleGenerator - Feature 008"
---

# CSSInjector & ThemeToggleGenerator Contract

## Overview

The `CSSInjector` generates HTML tags for CSS inclusion (external links and inline styles), while `ThemeToggleGenerator` creates the JavaScript for dark/light mode switching.

## CSSInjector Interface

```python
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CSSTag:
    """Represents a CSS inclusion tag."""
    
    tag_type: str  # "link" or "style"
    content: str   # URL for link, CSS content for style
    attributes: dict[str, str] | None = None
    
    def to_html(self) -> str:
        """Render as HTML tag."""
        if self.tag_type == "link":
            attrs = self.attributes or {}
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            return f'<link rel="stylesheet" href="{self.content}" {attr_str}>'
        else:
            return f"<style>\n{self.content}\n</style>"


class CSSInjectorProtocol(Protocol):
    """Protocol for CSS injection."""
    
    def generate_tags(
        self,
        css_url: str | None = None,
        css_inline: str | None = None,
        include_base: bool = True,
    ) -> list[CSSTag]:
        """
        Generate CSS tags for HTML head injection.
        
        Args:
            css_url: External CSS URL to include
            css_inline: Inline CSS content to embed
            include_base: Include base theme CSS variables
            
        Returns:
            List of CSSTag objects in order of inclusion
        """
        ...


class CSSInjector:
    """
    Generates CSS tags for HTML documentation.
    
    Tag order:
    1. Base theme variables (if include_base=True)
    2. External CSS URL (if provided)
    3. Inline CSS (if provided)
    """
    
    BASE_CSS = '''
:root {
  /* Color Tokens - Primary Palette */
  --ad-color-primary: #2563eb;
  --ad-color-primary-light: #3b82f6;
  --ad-color-primary-dark: #1d4ed8;

  /* Semantic Colors */
  --ad-color-success: #10b981;
  --ad-color-warning: #f59e0b;
  --ad-color-error: #ef4444;
  --ad-color-info: #0ea5e9;

  /* Neutral Palette */
  --ad-color-bg: #ffffff;
  --ad-color-bg-secondary: #f8fafc;
  --ad-color-bg-tertiary: #f1f5f9;
  --ad-color-text: #1e293b;
  --ad-color-text-secondary: #64748b;
  --ad-color-text-muted: #94a3b8;
  --ad-color-border: #e2e8f0;

  /* Typography */
  --ad-font-family: system-ui, -apple-system, sans-serif;
  --ad-font-family-mono: ui-monospace, SFMono-Regular, monospace;
  --ad-line-height: 1.6;

  /* Spacing */
  --ad-spacing-sm: 0.5rem;
  --ad-spacing-md: 1rem;
  --ad-spacing-lg: 1.5rem;
  --ad-spacing-xl: 2rem;

  /* Border Radius */
  --ad-radius-md: 0.375rem;
  --ad-radius-lg: 0.5rem;
}

/* Dark Mode */
[data-theme="dark"] {
  --ad-color-bg: #0f172a;
  --ad-color-bg-secondary: #1e293b;
  --ad-color-bg-tertiary: #334155;
  --ad-color-text: #f8fafc;
  --ad-color-text-secondary: #cbd5e1;
  --ad-color-text-muted: #64748b;
  --ad-color-border: #334155;
}

/* Auto dark mode via media query */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ad-color-bg: #0f172a;
    --ad-color-bg-secondary: #1e293b;
    --ad-color-bg-tertiary: #334155;
    --ad-color-text: #f8fafc;
    --ad-color-text-secondary: #cbd5e1;
    --ad-color-text-muted: #64748b;
    --ad-color-border: #334155;
  }
}

/* Base styles */
body {
  font-family: var(--ad-font-family);
  line-height: var(--ad-line-height);
  color: var(--ad-color-text);
  background-color: var(--ad-color-bg);
}
'''
    
    def generate_tags(
        self,
        css_url: str | None = None,
        css_inline: str | None = None,
        include_base: bool = True,
    ) -> list[CSSTag]:
        """Generate CSS tags in correct order."""
        tags = []
        
        # 1. Base theme CSS
        if include_base:
            tags.append(CSSTag(
                tag_type="style",
                content=self.BASE_CSS.strip(),
            ))
        
        # 2. External CSS URL
        if css_url:
            tags.append(CSSTag(
                tag_type="link",
                content=css_url,
                attributes={"crossorigin": "anonymous"},
            ))
        
        # 3. Inline CSS
        if css_inline:
            tags.append(CSSTag(
                tag_type="style",
                content=css_inline.strip(),
            ))
        
        return tags
    
    def render_head_tags(
        self,
        css_url: str | None = None,
        css_inline: str | None = None,
        include_base: bool = True,
    ) -> str:
        """Render all CSS tags as HTML string for head injection."""
        tags = self.generate_tags(css_url, css_inline, include_base)
        return "\n".join(tag.to_html() for tag in tags)
```

## ThemeToggleGenerator Interface

```python
class ThemeToggleGenerator:
    """
    Generates JavaScript for dark/light mode toggle.
    
    Features:
    - Respects prefers-color-scheme media query
    - Persists preference to localStorage
    - ARIA attributes for accessibility
    - No external dependencies
    """
    
    TOGGLE_JS = '''
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
      toggle.setAttribute('aria-label', 
        theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
      );
    }
  }
  
  // Initialize theme
  setTheme(getPreferredTheme());
  
  // Listen for system preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
  
  // Toggle handler
  if (toggle) {
    toggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();
'''
    
    TOGGLE_BUTTON_HTML = '''
<button 
  id="ad-theme-toggle" 
  type="button" 
  class="ad-theme-toggle"
  aria-pressed="false"
  aria-label="Switch to dark mode"
  title="Toggle dark/light mode">
  <span class="ad-theme-toggle-icon" aria-hidden="true">🌙</span>
</button>
'''
    
    TOGGLE_CSS = '''
.ad-theme-toggle {
  position: fixed;
  bottom: var(--ad-spacing-lg);
  right: var(--ad-spacing-lg);
  padding: var(--ad-spacing-sm) var(--ad-spacing-md);
  border: 1px solid var(--ad-color-border);
  border-radius: var(--ad-radius-lg);
  background: var(--ad-color-bg-secondary);
  cursor: pointer;
  font-size: 1.25rem;
  z-index: 1000;
  transition: transform 0.2s, box-shadow 0.2s;
}

.ad-theme-toggle:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ad-theme-toggle:focus {
  outline: 2px solid var(--ad-color-primary);
  outline-offset: 2px;
}

[data-theme="dark"] .ad-theme-toggle-icon::before {
  content: '☀️';
}
'''
    
    def generate_script_tag(self) -> str:
        """Generate the theme toggle script tag."""
        return f"<script>\n{self.TOGGLE_JS.strip()}\n</script>"
    
    def generate_button_html(self) -> str:
        """Generate the toggle button HTML."""
        return self.TOGGLE_BUTTON_HTML.strip()
    
    def generate_toggle_css(self) -> str:
        """Generate CSS for the toggle button."""
        return self.TOGGLE_CSS.strip()
    
    def generate_full_toggle(self) -> dict[str, str]:
        """
        Generate all components for theme toggle.
        
        Returns:
            Dict with 'html', 'css', and 'js' keys
        """
        return {
            "html": self.generate_button_html(),
            "css": self.generate_toggle_css(),
            "js": self.generate_script_tag(),
        }
```

## Usage in HTML Template

```jinja2
<!DOCTYPE html>
<html lang="{{ language }}">
<head>
  <meta charset="UTF-8">
  <title>{{ role.name }} - Documentation</title>
  
  {# CSS injection #}
  {{ css_tags }}
  
  {# Toggle button CSS (if enabled) #}
  {% if theme_config.enable_toggle %}
  <style>{{ toggle_css }}</style>
  {% endif %}
</head>
<body>
  {# Toggle button (if enabled) #}
  {% if theme_config.enable_toggle %}
  {{ toggle_button | safe }}
  {% endif %}
  
  {# Main content #}
  <main>
    {{ content }}
  </main>
  
  {# Toggle script (if enabled) #}
  {% if theme_config.enable_toggle %}
  {{ toggle_script | safe }}
  {% endif %}
</body>
</html>
```

## Security Considerations

1. **No `eval()`**: Toggle JS uses no dynamic code execution
2. **No `innerHTML`**: All DOM manipulation uses safe methods
3. **Scoped**: IIFE pattern prevents global namespace pollution
4. **CSP Compatible**: Works with Content-Security-Policy
5. **Sanitized**: User CSS is included as-is (user responsibility)

## Accessibility Features

- `aria-pressed`: Indicates toggle state
- `aria-label`: Describes current action
- `title`: Tooltip for hover
- Keyboard accessible: Focusable, responds to Enter/Space
- High contrast: Toggle button visible in both themes
