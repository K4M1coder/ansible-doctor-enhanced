"""Theme configuration model.

Feature 008 - Template Customization & Theming
T333: ThemeConfig Pydantic model with validation
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ThemeVariant(str, Enum):
    """Available template variants.
    
    Controls the level of detail and style in generated documentation.
    
    Attributes:
        MINIMAL: Compact output with essential information only
        DETAILED: Full documentation with all sections (default)
        MODERN: Contemporary styling with enhanced visual elements
    """
    
    MINIMAL = "minimal"
    DETAILED = "detailed"
    MODERN = "modern"


class ColorScheme(str, Enum):
    """Color scheme options for documentation output.
    
    Attributes:
        LIGHT: Light background with dark text
        DARK: Dark background with light text
        AUTO: Respects user's OS/browser preference (default)
    """
    
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeConfig(BaseModel):
    """Theme configuration for documentation output.
    
    Controls visual presentation including template variant, color scheme,
    and optional custom CSS. Designed for use in .ansibledoctor.yml files.
    
    Attributes:
        name: Theme name (reserved for future theme marketplace)
        variant: Template variant (minimal, detailed, modern)
        color_scheme: Color scheme (light, dark, auto)
        enable_toggle: Show dark/light mode toggle button
        css_url: External CSS URL to include
        css_inline: Inline CSS content to embed
    
    Example:
        >>> config = ThemeConfig(variant="modern", color_scheme="dark")
        >>> config.variant
        <ThemeVariant.MODERN: 'modern'>
        >>> config.color_scheme
        <ColorScheme.DARK: 'dark'>
    
    Feature: US23 - Theme Configuration
    Task: T333 - ThemeConfig implementation
    """
    
    name: str = Field(
        default="default",
        description="Theme name (reserved for future theme marketplace)"
    )
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
        """Validate that css_url is an absolute URL or path.
        
        Args:
            v: CSS URL value
            
        Returns:
            Validated URL
            
        Raises:
            ValueError: If URL is not absolute (http://, https://, or /)
        """
        if v is not None and not v.startswith(("http://", "https://", "/")):
            raise ValueError(
                "css_url must be an absolute URL (http:// or https://) or "
                "absolute path (starting with /)"
            )
        return v
    
    model_config = {
        "frozen": True,
        "extra": "forbid",
    }
