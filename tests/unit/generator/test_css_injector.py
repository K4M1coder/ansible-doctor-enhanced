"""Unit tests for CSSInjector and ThemeToggleGenerator.

Feature 008 - Template Customization & Theming
T338: TDD unit tests for CSS injection and theme toggle generation
"""

import pytest

from ansibledoctor.generator.css_injector import CSSInjector, CSSTag, ThemeToggleGenerator


class TestCSSTag:
    """Test CSSTag dataclass."""

    def test_link_tag_creation(self):
        """CSSTag with type 'link' should hold URL."""
        tag = CSSTag(
            tag_type="link",
            content="https://example.com/style.css",
        )
        assert tag.tag_type == "link"
        assert tag.content == "https://example.com/style.css"
        assert tag.attributes is None

    def test_style_tag_creation(self):
        """CSSTag with type 'style' should hold CSS content."""
        css = ".header { color: blue; }"
        tag = CSSTag(
            tag_type="style",
            content=css,
        )
        assert tag.tag_type == "style"
        assert tag.content == css

    def test_tag_with_attributes(self):
        """CSSTag can have additional attributes."""
        tag = CSSTag(
            tag_type="link",
            content="https://example.com/style.css",
            attributes={"crossorigin": "anonymous", "integrity": "sha256-abc"},
        )
        assert tag.attributes["crossorigin"] == "anonymous"
        assert tag.attributes["integrity"] == "sha256-abc"

    def test_tag_is_frozen(self):
        """CSSTag should be immutable."""
        tag = CSSTag(tag_type="link", content="url")
        with pytest.raises(Exception):  # FrozenInstanceError
            tag.content = "new_url"

    def test_link_tag_to_html(self):
        """to_html() should render link tag correctly."""
        tag = CSSTag(
            tag_type="link",
            content="https://example.com/style.css",
        )
        html = tag.to_html()
        assert "<link" in html
        assert 'rel="stylesheet"' in html
        assert 'href="https://example.com/style.css"' in html

    def test_link_tag_to_html_with_attributes(self):
        """to_html() should include custom attributes."""
        tag = CSSTag(
            tag_type="link",
            content="https://example.com/style.css",
            attributes={"crossorigin": "anonymous"},
        )
        html = tag.to_html()
        assert 'crossorigin="anonymous"' in html

    def test_style_tag_to_html(self):
        """to_html() should render style tag with content."""
        css = ".header { color: blue; }"
        tag = CSSTag(
            tag_type="style",
            content=css,
        )
        html = tag.to_html()
        assert "<style>" in html
        assert "</style>" in html
        assert css in html


class TestCSSInjector:
    """Test CSSInjector class."""

    @pytest.fixture
    def injector(self):
        """Create a CSSInjector instance."""
        return CSSInjector()

    def test_base_css_contains_variables(self, injector):
        """Base CSS should contain CSS variables."""
        assert "--ad-color-primary" in injector.BASE_CSS
        assert "--ad-color-bg" in injector.BASE_CSS
        assert "--ad-color-text" in injector.BASE_CSS

    def test_base_css_contains_dark_mode(self, injector):
        """Base CSS should contain dark mode styles."""
        assert '[data-theme="dark"]' in injector.BASE_CSS
        assert "prefers-color-scheme: dark" in injector.BASE_CSS

    def test_generate_tags_with_base_only(self, injector):
        """generate_tags() with only base CSS should return one tag."""
        tags = injector.generate_tags(include_base=True)
        assert len(tags) == 1
        assert tags[0].tag_type == "style"
        assert "--ad-color" in tags[0].content

    def test_generate_tags_with_external_url(self, injector):
        """generate_tags() with external URL should include link tag."""
        tags = injector.generate_tags(
            css_url="https://example.com/theme.css",
            include_base=True,
        )
        assert len(tags) == 2
        # Base is first
        assert tags[0].tag_type == "style"
        # External URL is second
        assert tags[1].tag_type == "link"
        assert tags[1].content == "https://example.com/theme.css"

    def test_generate_tags_with_inline_css(self, injector):
        """generate_tags() with inline CSS should include style tag."""
        inline_css = ".custom { color: red; }"
        tags = injector.generate_tags(
            css_inline=inline_css,
            include_base=True,
        )
        assert len(tags) == 2
        # Base is first
        assert tags[0].tag_type == "style"
        # Inline is second
        assert tags[1].tag_type == "style"
        assert ".custom" in tags[1].content

    def test_generate_tags_full_order(self, injector):
        """Tags should be in order: base, external, inline."""
        tags = injector.generate_tags(
            css_url="https://example.com/theme.css",
            css_inline=".custom { color: red; }",
            include_base=True,
        )
        assert len(tags) == 3
        # 1. Base CSS
        assert tags[0].tag_type == "style"
        assert "--ad-color" in tags[0].content
        # 2. External URL
        assert tags[1].tag_type == "link"
        # 3. Inline CSS
        assert tags[2].tag_type == "style"
        assert ".custom" in tags[2].content

    def test_generate_tags_without_base(self, injector):
        """generate_tags() with include_base=False should skip base CSS."""
        tags = injector.generate_tags(
            css_url="https://example.com/theme.css",
            include_base=False,
        )
        assert len(tags) == 1
        assert tags[0].tag_type == "link"
        # Should not have base variables
        assert "--ad-color" not in tags[0].content

    def test_generate_tags_empty(self, injector):
        """generate_tags() with no options should return empty list."""
        tags = injector.generate_tags(include_base=False)
        assert tags == []

    def test_external_url_has_crossorigin(self, injector):
        """External CSS links should have crossorigin attribute."""
        tags = injector.generate_tags(
            css_url="https://cdn.example.com/style.css",
            include_base=False,
        )
        assert tags[0].attributes is not None
        assert tags[0].attributes.get("crossorigin") == "anonymous"

    def test_render_head_tags(self, injector):
        """render_head_tags() should return HTML string."""
        html = injector.render_head_tags(
            css_url="https://example.com/theme.css",
            include_base=True,
        )
        assert isinstance(html, str)
        assert "<style>" in html
        assert "<link" in html

    def test_render_head_tags_order(self, injector):
        """render_head_tags() should maintain tag order."""
        html = injector.render_head_tags(
            css_url="https://example.com/theme.css",
            css_inline=".custom { color: red; }",
            include_base=True,
        )
        # Check order by position
        base_pos = html.find("--ad-color")
        link_pos = html.find("<link")
        inline_pos = html.find(".custom")
        assert base_pos < link_pos < inline_pos


class TestThemeToggleGenerator:
    """Test ThemeToggleGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a ThemeToggleGenerator instance."""
        return ThemeToggleGenerator()

    def test_toggle_js_is_self_contained(self, generator):
        """Toggle JS should be self-contained IIFE."""
        js = generator.TOGGLE_JS
        assert js.strip().startswith("(function()")
        assert js.strip().endswith("})();")

    def test_toggle_js_uses_localstorage(self, generator):
        """Toggle JS should use localStorage."""
        js = generator.TOGGLE_JS
        assert "localStorage" in js
        assert "ad-theme" in js.lower() or "STORAGE_KEY" in js

    def test_toggle_js_respects_media_query(self, generator):
        """Toggle JS should check prefers-color-scheme."""
        js = generator.TOGGLE_JS
        assert "prefers-color-scheme" in js

    def test_toggle_js_has_aria_attributes(self, generator):
        """Toggle JS should set ARIA attributes."""
        js = generator.TOGGLE_JS
        assert "aria-pressed" in js
        assert "aria-label" in js

    def test_toggle_button_html_structure(self, generator):
        """Button HTML should have correct structure."""
        html = generator.TOGGLE_BUTTON_HTML
        assert 'id="ad-theme-toggle"' in html
        assert 'type="button"' in html
        assert "aria-pressed" in html
        assert "aria-label" in html

    def test_toggle_button_has_icon(self, generator):
        """Button HTML should include an icon."""
        html = generator.TOGGLE_BUTTON_HTML
        assert "aria-hidden" in html  # Icon should be hidden from screen readers

    def test_generate_toggle_returns_both(self, generator):
        """generate_toggle() should return button HTML and script."""
        result = generator.generate_toggle()
        assert "button_html" in result or hasattr(result, "button_html")
        assert "script_js" in result or hasattr(result, "script_js")

    def test_generate_toggle_disabled(self, generator):
        """generate_toggle(enabled=False) should return empty."""
        result = generator.generate_toggle(enabled=False)
        # When disabled, should return empty or None values
        if isinstance(result, dict):
            assert result.get("button_html") == "" or result.get("button_html") is None
        else:
            assert result.button_html == "" or result.button_html is None

    def test_render_toggle_html(self, generator):
        """render_toggle() should return complete HTML snippet."""
        html = generator.render_toggle()
        assert "<button" in html
        assert "<script>" in html or "script" in html.lower()

    def test_render_toggle_disabled(self, generator):
        """render_toggle(enabled=False) should return empty string."""
        html = generator.render_toggle(enabled=False)
        assert html == ""


class TestCSSColorScheme:
    """Test CSS color scheme support."""

    @pytest.fixture
    def injector(self):
        """Create a CSSInjector instance."""
        return CSSInjector()

    def test_light_mode_colors(self, injector):
        """Base CSS should have light mode colors as default."""
        css = injector.BASE_CSS
        # Default (root) should have light colors
        assert "#ffffff" in css or "#f8fafc" in css  # Light backgrounds

    def test_dark_mode_colors(self, injector):
        """Dark mode section should have dark colors."""
        css = injector.BASE_CSS
        # Dark mode section
        dark_section_start = css.find('[data-theme="dark"]')
        dark_section = css[dark_section_start : dark_section_start + 500]
        assert "#0f172a" in dark_section or "#1e293b" in dark_section  # Dark backgrounds

    def test_auto_mode_media_query(self, injector):
        """CSS should include auto mode via media query."""
        css = injector.BASE_CSS
        assert "@media (prefers-color-scheme: dark)" in css


class TestIntegration:
    """Integration tests for CSS injection with theme toggle."""

    def test_full_html_head_injection(self):
        """Complete head injection should include CSS and toggle."""
        injector = CSSInjector()
        toggle_gen = ThemeToggleGenerator()

        css_html = injector.render_head_tags(
            css_url="https://example.com/custom.css",
            css_inline=".role-name { font-weight: bold; }",
            include_base=True,
        )
        toggle_html = toggle_gen.render_toggle()

        full_head = f"{css_html}\n{toggle_html}"

        # Should have all components
        assert "<style>" in full_head
        assert "<link" in full_head
        assert "<script>" in full_head or "script" in full_head.lower()

    def test_minimal_injection(self):
        """Minimal injection with just base CSS."""
        injector = CSSInjector()
        toggle_gen = ThemeToggleGenerator()

        css_html = injector.render_head_tags(include_base=True)
        toggle_html = toggle_gen.render_toggle(enabled=False)

        # Should have base CSS only
        assert "<style>" in css_html
        assert "--ad-color" in css_html
        # Toggle should be empty
        assert toggle_html == ""
