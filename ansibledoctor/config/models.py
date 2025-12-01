"""Configuration data models using Pydantic.

Feature 003 - US1: Configuration File Support
T005: ConfigModel Pydantic schema with validation

Feature 008 - Template Customization & Theming
T333: Integration of ThemeConfig into ConfigModel
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ansibledoctor.config.language import LanguageConfig
from ansibledoctor.config.theme import ThemeConfig


class ConfigModel(BaseModel):
    """Configuration model for .ansibledoctor.yml files.

    Provides type-safe configuration with validation for documentation
    generation settings. Backward compatible with original ansible-doctor
    config format.

    Attributes:
        output: Output file path (optional, can be set via CLI)
        output_format: Documentation format (markdown, html, rst)
        template: Custom template file path (optional)
        template_dir: Directory containing custom templates (optional)
        recursive: Enable recursive role discovery (default: False)
        output_dir: Output directory for batch generation (optional)
        exclude_patterns: Glob patterns to exclude from processing

    Example:
        >>> config = ConfigModel(output_format="html", output="docs/role.html")
        >>> config.output_format
        'html'
        >>> config.recursive
        False
    """

    output: Optional[str] = Field(
        default=None, description="Output file path for generated documentation"
    )
    output_format: Optional[str] = Field(
        default=None, description="Documentation format: markdown, html, or rst"
    )
    template: Optional[str] = Field(default=None, description="Path to custom Jinja2 template file")
    template_dir: Optional[str] = Field(
        default=None, description="Directory containing custom templates"
    )
    recursive: bool = Field(
        default=False, description="Enable recursive role discovery in subdirectories"
    )
    output_dir: Optional[str] = Field(
        default=None, description="Output directory for batch generation (with --recursive)"
    )
    exclude_patterns: list[str] = Field(
        default_factory=lambda: ["*.pyc", "__pycache__", ".git"],
        description="Glob patterns to exclude from processing",
    )

    languages: Optional[LanguageConfig] = Field(
        default=None, description="Language configuration for i18n"
    )
    
    theme: Optional[ThemeConfig] = Field(
        default=None, description="Theme configuration for documentation output"
    )

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate output_format is one of the supported formats.

        Args:
            v: Output format value

        Returns:
            Validated output format

        Raises:
            ValueError: If format is not supported
        """
        if v is not None and v not in ("markdown", "html", "rst"):
            raise ValueError(f"output_format must be 'markdown', 'html', or 'rst', got '{v}'")
        return v

    @field_validator("exclude_patterns")
    @classmethod
    def validate_exclude_patterns(cls, v: list[str]) -> list[str]:
        """Validate exclude_patterns is a list of strings.

        Args:
            v: List of exclude patterns

        Returns:
            Validated exclude patterns list
        """
        if not isinstance(v, list):
            raise ValueError("exclude_patterns must be a list")
        if not all(isinstance(pattern, str) for pattern in v):
            raise ValueError("All exclude patterns must be strings")
        return v

    model_config = {
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,  # Strip whitespace from strings
    }
