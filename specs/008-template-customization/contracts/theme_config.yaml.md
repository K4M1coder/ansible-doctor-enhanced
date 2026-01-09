---
description: "Contract for ThemeConfig model - Feature 008"
---

# ThemeConfig YAML Contract

## Schema Definition

```yaml
# .ansibledoctor.yml theme configuration
theme:
  # Theme name (reserved for future marketplace)
  name: string  # default: "default"
  
  # Template variant
  variant: enum  # "minimal" | "detailed" | "modern", default: "detailed"
  
  # Color scheme
  color_scheme: enum  # "light" | "dark" | "auto", default: "auto"
  
  # Theme toggle button
  enable_toggle: boolean  # default: true
  
  # External CSS URL
  css_url: string | null  # default: null
  
  # Inline CSS content
  css_inline: string | null  # default: null
```

## Pydantic Model

```python
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ThemeVariant(str, Enum):
    """Available template variants."""
    MINIMAL = "minimal"
    DETAILED = "detailed"
    MODERN = "modern"


class ColorScheme(str, Enum):
    """Color scheme options."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeConfig(BaseModel):
    """Theme configuration for documentation output."""
    
    name: str = Field(default="default", description="Theme name")
    variant: ThemeVariant = Field(
        default=ThemeVariant.DETAILED,
        description="Template variant: minimal, detailed, or modern"
    )
    color_scheme: ColorScheme = Field(
        default=ColorScheme.AUTO,
        description="Color scheme: light, dark, or auto"
    )
    enable_toggle: bool = Field(
        default=True,
        description="Show dark/light mode toggle button"
    )
    css_url: str | None = Field(
        default=None,
        description="External CSS URL to include"
    )
    css_inline: str | None = Field(
        default=None,
        description="Inline CSS content to embed"
    )
    
    @field_validator("css_url")
    @classmethod
    def validate_css_url(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith(("http://", "https://", "/")):
            raise ValueError("css_url must be an absolute URL or path")
        return v
    
    model_config = {"frozen": True}
```

## Validation Rules

1. **variant**: Must be one of "minimal", "detailed", "modern"
2. **color_scheme**: Must be one of "light", "dark", "auto"
3. **css_url**: If provided, must start with `http://`, `https://`, or `/`
4. **css_inline**: Any valid CSS string (no validation, user responsibility)

## Default Values

| Field | Default | Rationale |
| ------- | --------- | ----------- |
| name | "default" | Reserved for theme marketplace |
| variant | "detailed" | Matches current behavior |
| color_scheme | "auto" | Respects user OS preference |
| enable_toggle | true | Provides user control |
| css_url | null | No external CSS by default |
| css_inline | null | No inline CSS by default |

## Usage Examples

### Minimal Configuration

```yaml
theme:
  variant: minimal
```

### Full Configuration

```yaml
theme:
  name: corporate
  variant: modern
  color_scheme: light
  enable_toggle: false
  css_url: https://cdn.example.com/theme.css
  css_inline: |
    .ad-header {
      background: linear-gradient(90deg, #1e3a8a, #3b82f6);
    }
```

### Environment Variable Override

```bash
export AD_THEME_VARIANT=modern
export AD_THEME_COLOR_SCHEME=dark
```

## Integration Points

- `ansibledoctor/config/loader.py`: Parse theme section from YAML
- `ansibledoctor/cli/__init__.py`: Override via CLI flags
- `ansibledoctor/generator/renderers/html.py`: Apply theme during render
