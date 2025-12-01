"""CSS injection and theme toggle generation.

Feature 008 - Template Customization & Theming
T339: CSSInjector and ThemeToggleGenerator implementation

Generates CSS tags for HTML head injection and JavaScript
for dark/light mode toggle functionality.
"""

from dataclasses import dataclass
from typing import NamedTuple


@dataclass(frozen=True)
class CSSTag:
    """Represents a CSS inclusion tag.
    
    Can be either a <link> tag for external stylesheets or a <style>
    tag for inline CSS content.
    
    Attributes:
        tag_type: "link" for external CSS or "style" for inline
        content: URL for link tags, CSS content for style tags
        attributes: Optional additional HTML attributes
    """
    
    tag_type: str  # "link" or "style"
    content: str
    attributes: dict[str, str] | None = None
    
    def to_html(self) -> str:
        """Render as HTML tag.
        
        Returns:
            HTML string for this CSS tag
        """
        if self.tag_type == "link":
            attrs = self.attributes or {}
            attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
            if attr_str:
                return f'<link rel="stylesheet" href="{self.content}" {attr_str}>'
            return f'<link rel="stylesheet" href="{self.content}">'
        else:
            return f"<style>\n{self.content}\n</style>"


class ToggleResult(NamedTuple):
    """Result of theme toggle generation.
    
    Attributes:
        button_html: HTML for the toggle button
        script_js: JavaScript for toggle functionality
    """
    
    button_html: str
    script_js: str


class CSSInjector:
    """Generates CSS tags for HTML documentation.
    
    Manages CSS inclusion order for proper cascade:
    1. Base theme CSS variables
    2. External CSS URL
    3. Inline CSS overrides
    
    Example:
        >>> injector = CSSInjector()
        >>> html = injector.render_head_tags(
        ...     css_url="https://example.com/theme.css",
        ...     include_base=True
        ... )
    
    Feature: US26 - CSS Injection
    Task: T339 - CSSInjector implementation
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
        """Generate CSS tags in correct order.
        
        Args:
            css_url: External CSS URL to include
            css_inline: Inline CSS content to embed
            include_base: Include base theme CSS variables
            
        Returns:
            List of CSSTag objects in order of inclusion
        """
        tags: list[CSSTag] = []
        
        # 1. Base theme CSS (first, can be overridden)
        if include_base:
            tags.append(CSSTag(
                tag_type="style",
                content=self.BASE_CSS.strip(),
            ))
        
        # 2. External CSS URL (second, extends/overrides base)
        if css_url:
            tags.append(CSSTag(
                tag_type="link",
                content=css_url,
                attributes={"crossorigin": "anonymous"},
            ))
        
        # 3. Inline CSS (last, highest priority)
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
        """Render all CSS tags as HTML string for head injection.
        
        Args:
            css_url: External CSS URL to include
            css_inline: Inline CSS content to embed
            include_base: Include base theme CSS variables
            
        Returns:
            HTML string containing all CSS tags
        """
        tags = self.generate_tags(css_url, css_inline, include_base)
        return "\n".join(tag.to_html() for tag in tags)


class ThemeToggleGenerator:
    """Generates JavaScript for dark/light mode toggle.
    
    Features:
    - Respects prefers-color-scheme media query
    - Persists preference to localStorage
    - ARIA attributes for accessibility
    - No external dependencies
    
    Example:
        >>> generator = ThemeToggleGenerator()
        >>> html = generator.render_toggle()
        >>> # Include html in document body
    
    Feature: US26 - Theme Toggle
    Task: T339 - ThemeToggleGenerator implementation
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
    
    def generate_toggle(self, enabled: bool = True) -> ToggleResult:
        """Generate toggle button and script.
        
        Args:
            enabled: Whether toggle is enabled
            
        Returns:
            ToggleResult with button HTML and script JS
        """
        if not enabled:
            return ToggleResult(button_html="", script_js="")
        
        return ToggleResult(
            button_html=self.TOGGLE_BUTTON_HTML.strip(),
            script_js=self.TOGGLE_JS.strip(),
        )
    
    def render_toggle(self, enabled: bool = True) -> str:
        """Render complete toggle HTML snippet.
        
        Args:
            enabled: Whether toggle is enabled
            
        Returns:
            HTML string with button and script, or empty if disabled
        """
        if not enabled:
            return ""
        
        result = self.generate_toggle(enabled=True)
        return f"{result.button_html}\n<script>\n{result.script_js}\n</script>"
