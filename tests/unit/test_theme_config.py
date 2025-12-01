"""Unit tests for ThemeConfig model.

Feature 008 - Template Customization & Theming
T332: TDD unit tests for ThemeConfig YAML parsing, defaulting, and validation
"""

import pytest

from ansibledoctor.config.theme import (
    ThemeConfig,
    ThemeVariant,
    ColorScheme,
)


class TestThemeVariantEnum:
    """Test ThemeVariant enum values."""

    def test_minimal_variant(self):
        """ThemeVariant.MINIMAL should have value 'minimal'."""
        assert ThemeVariant.MINIMAL == "minimal"
        assert ThemeVariant.MINIMAL.value == "minimal"

    def test_detailed_variant(self):
        """ThemeVariant.DETAILED should have value 'detailed'."""
        assert ThemeVariant.DETAILED == "detailed"
        assert ThemeVariant.DETAILED.value == "detailed"

    def test_modern_variant(self):
        """ThemeVariant.MODERN should have value 'modern'."""
        assert ThemeVariant.MODERN == "modern"
        assert ThemeVariant.MODERN.value == "modern"

    def test_variant_from_string(self):
        """ThemeVariant can be created from string value."""
        assert ThemeVariant("minimal") == ThemeVariant.MINIMAL
        assert ThemeVariant("detailed") == ThemeVariant.DETAILED
        assert ThemeVariant("modern") == ThemeVariant.MODERN

    def test_invalid_variant_raises_error(self):
        """Invalid variant string should raise ValueError."""
        with pytest.raises(ValueError):
            ThemeVariant("invalid")


class TestColorSchemeEnum:
    """Test ColorScheme enum values."""

    def test_light_scheme(self):
        """ColorScheme.LIGHT should have value 'light'."""
        assert ColorScheme.LIGHT == "light"
        assert ColorScheme.LIGHT.value == "light"

    def test_dark_scheme(self):
        """ColorScheme.DARK should have value 'dark'."""
        assert ColorScheme.DARK == "dark"
        assert ColorScheme.DARK.value == "dark"

    def test_auto_scheme(self):
        """ColorScheme.AUTO should have value 'auto'."""
        assert ColorScheme.AUTO == "auto"
        assert ColorScheme.AUTO.value == "auto"

    def test_scheme_from_string(self):
        """ColorScheme can be created from string value."""
        assert ColorScheme("light") == ColorScheme.LIGHT
        assert ColorScheme("dark") == ColorScheme.DARK
        assert ColorScheme("auto") == ColorScheme.AUTO

    def test_invalid_scheme_raises_error(self):
        """Invalid color scheme string should raise ValueError."""
        with pytest.raises(ValueError):
            ColorScheme("invalid")


class TestThemeConfigDefaults:
    """Test ThemeConfig default values."""

    def test_default_name(self):
        """Default name should be 'default'."""
        config = ThemeConfig()
        assert config.name == "default"

    def test_default_variant(self):
        """Default variant should be DETAILED."""
        config = ThemeConfig()
        assert config.variant == ThemeVariant.DETAILED
        assert config.variant == "detailed"

    def test_default_color_scheme(self):
        """Default color_scheme should be AUTO."""
        config = ThemeConfig()
        assert config.color_scheme == ColorScheme.AUTO
        assert config.color_scheme == "auto"

    def test_default_enable_toggle(self):
        """Default enable_toggle should be True."""
        config = ThemeConfig()
        assert config.enable_toggle is True

    def test_default_css_url(self):
        """Default css_url should be None."""
        config = ThemeConfig()
        assert config.css_url is None

    def test_default_css_inline(self):
        """Default css_inline should be None."""
        config = ThemeConfig()
        assert config.css_inline is None


class TestThemeConfigParsing:
    """Test ThemeConfig parsing from dict (simulating YAML)."""

    def test_parse_minimal_config(self):
        """Parse minimal theme configuration."""
        data = {"variant": "minimal"}
        config = ThemeConfig(**data)
        assert config.variant == ThemeVariant.MINIMAL
        assert config.color_scheme == ColorScheme.AUTO  # default

    def test_parse_full_config(self):
        """Parse full theme configuration."""
        data = {
            "name": "corporate",
            "variant": "modern",
            "color_scheme": "light",
            "enable_toggle": False,
            "css_url": "https://cdn.example.com/theme.css",
            "css_inline": ".ad-header { background: blue; }",
        }
        config = ThemeConfig(**data)
        assert config.name == "corporate"
        assert config.variant == ThemeVariant.MODERN
        assert config.color_scheme == ColorScheme.LIGHT
        assert config.enable_toggle is False
        assert config.css_url == "https://cdn.example.com/theme.css"
        assert config.css_inline == ".ad-header { background: blue; }"

    def test_parse_variant_string(self):
        """Variant can be parsed from string value."""
        config = ThemeConfig(variant="minimal")
        assert config.variant == ThemeVariant.MINIMAL

    def test_parse_color_scheme_string(self):
        """Color scheme can be parsed from string value."""
        config = ThemeConfig(color_scheme="dark")
        assert config.color_scheme == ColorScheme.DARK

    def test_parse_empty_dict(self):
        """Empty dict should use all defaults."""
        config = ThemeConfig(**{})
        assert config.name == "default"
        assert config.variant == ThemeVariant.DETAILED
        assert config.color_scheme == ColorScheme.AUTO
        assert config.enable_toggle is True


class TestThemeConfigValidation:
    """Test ThemeConfig validation rules."""

    def test_invalid_variant_raises_validation_error(self):
        """Invalid variant should raise validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThemeConfig(variant="invalid")
        assert "variant" in str(exc_info.value)

    def test_invalid_color_scheme_raises_validation_error(self):
        """Invalid color scheme should raise validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThemeConfig(color_scheme="invalid")
        assert "color_scheme" in str(exc_info.value)

    def test_css_url_must_be_absolute_https(self):
        """css_url with https:// should be valid."""
        config = ThemeConfig(css_url="https://example.com/style.css")
        assert config.css_url == "https://example.com/style.css"

    def test_css_url_must_be_absolute_http(self):
        """css_url with http:// should be valid."""
        config = ThemeConfig(css_url="http://example.com/style.css")
        assert config.css_url == "http://example.com/style.css"

    def test_css_url_must_be_absolute_path(self):
        """css_url with / prefix should be valid (absolute path)."""
        config = ThemeConfig(css_url="/static/theme.css")
        assert config.css_url == "/static/theme.css"

    def test_css_url_relative_path_raises_error(self):
        """css_url with relative path should raise validation error."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            ThemeConfig(css_url="styles/theme.css")
        assert "css_url" in str(exc_info.value).lower()

    def test_css_url_none_is_valid(self):
        """css_url can be None."""
        config = ThemeConfig(css_url=None)
        assert config.css_url is None

    def test_css_inline_accepts_any_string(self):
        """css_inline accepts any valid CSS string."""
        css = """
        .ad-header {
            background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        }
        :root {
            --ad-color-primary: #3b82f6;
        }
        """
        config = ThemeConfig(css_inline=css)
        assert config.css_inline == css

    def test_enable_toggle_must_be_bool(self):
        """enable_toggle must be boolean."""
        config = ThemeConfig(enable_toggle=False)
        assert config.enable_toggle is False

    def test_enable_toggle_invalid_type_raises_error(self):
        """enable_toggle with truly non-bool should raise error."""
        from pydantic import ValidationError

        # Pydantic coerces "true", "yes", "1" to True, so use a dict/list
        with pytest.raises(ValidationError):
            ThemeConfig(enable_toggle={"invalid": "type"})


class TestThemeConfigImmutability:
    """Test ThemeConfig immutability (frozen model)."""

    def test_config_is_immutable(self):
        """ThemeConfig should be immutable (frozen)."""
        config = ThemeConfig()
        with pytest.raises(Exception):  # ValidationError for frozen models
            config.name = "new_name"

    def test_config_is_hashable(self):
        """Frozen ThemeConfig should be hashable."""
        config = ThemeConfig()
        # Should not raise - frozen models are hashable
        hash(config)

    def test_config_equality(self):
        """Two ThemeConfig with same values should be equal."""
        config1 = ThemeConfig(variant="minimal", color_scheme="dark")
        config2 = ThemeConfig(variant="minimal", color_scheme="dark")
        assert config1 == config2


class TestThemeConfigIntegration:
    """Test ThemeConfig integration with config loader."""

    def test_from_nested_dict(self):
        """Parse ThemeConfig from nested YAML structure."""
        yaml_data = {
            "theme": {
                "variant": "modern",
                "color_scheme": "light",
                "enable_toggle": True,
            }
        }
        # Extract theme section as would happen in config loader
        theme_data = yaml_data.get("theme", {})
        config = ThemeConfig(**theme_data)
        assert config.variant == ThemeVariant.MODERN
        assert config.color_scheme == ColorScheme.LIGHT

    def test_missing_theme_section_uses_defaults(self):
        """Missing theme section should use all defaults."""
        yaml_data = {"output_format": "html"}
        theme_data = yaml_data.get("theme", {})
        config = ThemeConfig(**theme_data)
        assert config.variant == ThemeVariant.DETAILED
        assert config.color_scheme == ColorScheme.AUTO

    def test_partial_theme_section(self):
        """Partial theme section should merge with defaults."""
        yaml_data = {"theme": {"variant": "minimal"}}
        theme_data = yaml_data.get("theme", {})
        config = ThemeConfig(**theme_data)
        assert config.variant == ThemeVariant.MINIMAL
        assert config.color_scheme == ColorScheme.AUTO  # default
        assert config.enable_toggle is True  # default


class TestThemeConfigSerialization:
    """Test ThemeConfig serialization for caching and debugging."""

    def test_model_dump(self):
        """ThemeConfig can be serialized to dict."""
        config = ThemeConfig(variant="modern", color_scheme="dark")
        data = config.model_dump()
        assert data["name"] == "default"
        assert data["variant"] == "modern"
        assert data["color_scheme"] == "dark"
        assert data["enable_toggle"] is True
        assert data["css_url"] is None
        assert data["css_inline"] is None

    def test_model_dump_json(self):
        """ThemeConfig can be serialized to JSON string."""
        config = ThemeConfig(variant="minimal")
        json_str = config.model_dump_json()
        assert '"variant":"minimal"' in json_str
        assert '"color_scheme":"auto"' in json_str

    def test_round_trip_serialization(self):
        """ThemeConfig can be round-tripped through dict."""
        original = ThemeConfig(
            name="test",
            variant="modern",
            color_scheme="light",
            enable_toggle=False,
            css_url="https://example.com/style.css",
        )
        data = original.model_dump()
        restored = ThemeConfig(**data)
        assert original == restored
