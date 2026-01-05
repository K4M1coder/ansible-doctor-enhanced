"""Integration tests for theme variants.

Feature 008 - Template Customization & Theming
T343: End-to-end tests for minimal/detailed/modern variants
"""

import pytest

from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.models import AnsibleRole, Example, RoleMetadata, Tag, TodoItem, Variable


class TestThemeVariantsIntegration:
    """Integration tests for theme variant rendering."""

    @pytest.fixture
    def sample_role(self, tmp_path):
        """Create a sample role with typical content."""
        # Create role directory
        role_path = tmp_path / "sample_role"
        role_path.mkdir()

        return AnsibleRole(
            name="sample_role",
            path=role_path,
            metadata=RoleMetadata(
                author="Test Author",
                description="A sample role for theme testing",
                license="MIT",
                min_ansible_version="2.9",
            ),
            variables=[
                Variable(
                    name="app_port",
                    value=8080,
                    type="number",
                    description="Application port",
                    source="defaults/main.yml",
                    required=True,
                ),
                Variable(
                    name="app_debug",
                    value=False,
                    type="boolean",
                    description="Enable debug mode",
                    source="defaults/main.yml",
                ),
            ],
            tags=[
                Tag(name="configuration", count=3),
                Tag(name="deployment", count=2),
            ],
            todos=[
                TodoItem(
                    description="Add SSL support",
                    file_path="tasks/main.yml",
                    line_number=15,
                    priority="medium",
                ),
            ],
            examples=[
                Example(
                    title="Basic usage",
                    code="- hosts: all\n  roles:\n    - sample_role",
                    description="Basic role usage example",
                    language="yaml",
                ),
            ],
        )

    @pytest.fixture
    def minimal_theme(self):
        """Create minimal variant theme config."""
        return ThemeConfig(
            variant=ThemeVariant.MINIMAL,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

    @pytest.fixture
    def detailed_theme(self):
        """Create detailed variant theme config."""
        return ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

    @pytest.fixture
    def modern_theme(self):
        """Create modern variant theme config."""
        return ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

    def test_render_with_minimal_variant(self, sample_role, minimal_theme):
        """Test HTML rendering with minimal variant."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=minimal_theme,
        )

        result = renderer.render(context)

        # Should produce valid HTML
        assert isinstance(result, str)
        assert len(result) > 0
        assert "<html" in result.lower()
        # Should contain role name
        assert "sample_role" in result

    def test_render_with_detailed_variant(self, sample_role, detailed_theme):
        """Test HTML rendering with detailed variant."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=detailed_theme,
        )

        result = renderer.render(context)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "<html" in result.lower()
        assert "sample_role" in result

    def test_render_with_modern_variant(self, sample_role, modern_theme):
        """Test HTML rendering with modern variant."""
        renderer = HtmlRenderer()
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=modern_theme,
        )

        result = renderer.render(context)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "<html" in result.lower()
        assert "sample_role" in result

    def test_css_tags_included_in_context(self, sample_role, detailed_theme):
        """Test CSS tags are available in rendering context."""
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=detailed_theme,
        )

        css_tags = context.css_tags

        # Should have at least base CSS
        assert len(css_tags) >= 1
        # Should contain CSS variables
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")
        assert "--ad-" in all_css

    def test_theme_toggle_included_when_enabled(self, sample_role, detailed_theme):
        """Test theme toggle is available when enabled."""
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=detailed_theme,
        )

        toggle_html = context.theme_toggle_html
        toggle_js = context.theme_toggle_js

        # Toggle should be present when enabled
        assert "<button" in toggle_html
        assert "localStorage" in toggle_js

    def test_theme_toggle_absent_when_disabled(self, sample_role):
        """Test theme toggle is absent when disabled."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=False,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        toggle_html = context.theme_toggle_html
        toggle_js = context.theme_toggle_js

        # Toggle should be empty when disabled
        assert toggle_html == ""
        assert toggle_js == ""


class TestColorSchemeIntegration:
    """Integration tests for color scheme application."""

    @pytest.fixture
    def sample_role(self, tmp_path):
        """Create minimal role for color scheme testing."""
        role_path = tmp_path / "color_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="color_test_role",
            path=role_path,
            metadata=RoleMetadata(description="Color test"),
        )

    def test_light_scheme_css_generation(self, sample_role):
        """Test light color scheme generates appropriate CSS."""
        theme_config = ThemeConfig(
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=False,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags
        assert len(css_tags) >= 1
        # Light scheme should have base variables
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")
        assert "--ad-color-bg" in all_css

    def test_dark_scheme_css_generation(self, sample_role):
        """Test dark color scheme generates appropriate CSS."""
        theme_config = ThemeConfig(
            color_scheme=ColorScheme.DARK,
            enable_toggle=False,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags
        assert len(css_tags) >= 1
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")
        # Dark mode CSS should have data-theme selector or media query
        assert "--ad-" in all_css

    def test_auto_scheme_includes_media_query(self, sample_role):
        """Test auto color scheme includes prefers-color-scheme."""
        theme_config = ThemeConfig(
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")
        # Auto mode should include media query for system preference
        assert "prefers-color-scheme" in all_css


class TestCustomCSSIntegration:
    """Integration tests for custom CSS injection."""

    @pytest.fixture
    def sample_role(self, tmp_path):
        """Create minimal role for CSS testing."""
        role_path = tmp_path / "css_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="css_test_role",
            path=role_path,
            metadata=RoleMetadata(description="CSS test"),
        )

    def test_external_css_url_included(self, sample_role):
        """Test external CSS URL is included in CSS tags."""
        theme_config = ThemeConfig(
            css_url="https://example.com/custom-theme.css",
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags
        link_tags = [t for t in css_tags if t.tag_type == "link"]

        assert len(link_tags) >= 1
        assert any("https://example.com/custom-theme.css" in t.content for t in link_tags)

    def test_inline_css_included(self, sample_role):
        """Test inline CSS is included in CSS tags."""
        custom_css = "body { font-family: 'Roboto', sans-serif; }"
        theme_config = ThemeConfig(
            css_inline=custom_css,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags
        inline_tags = [t for t in css_tags if t.tag_type == "style"]

        assert any("font-family" in t.content for t in inline_tags)

    def test_css_order_base_url_inline(self, sample_role):
        """Test CSS tags are ordered: base, URL, inline."""
        custom_css = ".custom { color: red; }"
        theme_config = ThemeConfig(
            css_url="https://example.com/theme.css",
            css_inline=custom_css,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        css_tags = context.css_tags

        # Should have 3 tags: base (inline), URL (link), custom (inline)
        assert len(css_tags) >= 3

        # First should be base CSS (inline)
        assert css_tags[0].tag_type == "style"
        assert "--ad-" in css_tags[0].content

        # Second should be external URL (link)
        assert css_tags[1].tag_type == "link"
        assert "example.com" in css_tags[1].content

        # Third should be custom inline CSS
        assert css_tags[2].tag_type == "style"
        assert ".custom" in css_tags[2].content


class TestThemeContextDictIntegration:
    """Integration tests for theme context dictionary."""

    @pytest.fixture
    def sample_role(self, tmp_path):
        """Create minimal role."""
        role_path = tmp_path / "dict_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="dict_test_role",
            path=role_path,
            metadata=RoleMetadata(description="Dict test"),
        )

    def test_to_dict_includes_all_theme_properties(self, sample_role):
        """Test to_dict() includes all theme-related properties."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
            theme_config=theme_config,
        )

        data = context.to_dict()

        # All theme properties should be present
        assert "theme_config" in data
        assert "css_tags" in data
        assert "theme_toggle_html" in data
        assert "theme_toggle_js" in data
        assert "color_scheme" in data

        # Values should match
        assert data["theme_config"] == theme_config
        assert data["color_scheme"] == ColorScheme.DARK
        assert isinstance(data["css_tags"], list)
        assert "<button" in data["theme_toggle_html"]

    def test_to_dict_without_theme_config(self, sample_role):
        """Test to_dict() works without theme_config."""
        context = TemplateContext(
            role=sample_role,
            generator_version="0.5.0",
            output_format=OutputFormat.HTML,
        )

        data = context.to_dict()

        # Theme properties should be None or empty
        assert data["theme_config"] is None
        assert data["css_tags"] == []
        assert data["theme_toggle_html"] == ""
        assert data["theme_toggle_js"] == ""
        assert data["color_scheme"] is None
