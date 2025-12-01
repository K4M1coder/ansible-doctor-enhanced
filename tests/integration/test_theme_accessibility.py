"""Integration tests for theme toggle accessibility.

Feature 008 - Template Customization & Theming
T349: Accessibility tests for theme toggle

Ensures ARIA attributes in toggle controls and valid HTML structure.
"""

import re

import pytest

from ansibledoctor.generator.css_injector import (
    CSSInjector,
    CSSTag,
    ThemeToggleGenerator,
    ToggleResult,
)


class TestToggleAriaAttributes:
    """Tests for ARIA attributes in toggle button."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_toggle_has_aria_pressed(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle button has aria-pressed attribute."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'aria-pressed="false"' in result.button_html

    def test_toggle_has_aria_label(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle button has aria-label attribute."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'aria-label=' in result.button_html
        assert "Switch to dark mode" in result.button_html

    def test_toggle_has_title(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle button has title attribute for tooltip."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'title="Toggle dark/light mode"' in result.button_html

    def test_toggle_icon_is_aria_hidden(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle icon span is aria-hidden for screen readers."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'aria-hidden="true"' in result.button_html

    def test_toggle_has_type_button(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle has type=button to prevent form submission."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'type="button"' in result.button_html

    def test_toggle_has_id_for_script(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle has id for JavaScript targeting."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'id="ad-theme-toggle"' in result.button_html

    def test_toggle_has_class(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle has class for CSS styling."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert 'class="ad-theme-toggle"' in result.button_html


class TestToggleScriptAccessibility:
    """Tests for accessibility features in toggle JavaScript."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_script_updates_aria_pressed(self, toggle_generator: ThemeToggleGenerator):
        """Test script updates aria-pressed when theme changes."""
        result = toggle_generator.generate_toggle(enabled=True)

        # Script should update aria-pressed
        assert "setAttribute('aria-pressed'" in result.script_js

    def test_script_updates_aria_label(self, toggle_generator: ThemeToggleGenerator):
        """Test script updates aria-label when theme changes."""
        result = toggle_generator.generate_toggle(enabled=True)

        # Script should update aria-label to match new theme
        assert "setAttribute('aria-label'" in result.script_js
        assert "Switch to light mode" in result.script_js
        assert "Switch to dark mode" in result.script_js

    def test_script_respects_prefers_color_scheme(self, toggle_generator: ThemeToggleGenerator):
        """Test script respects user's color scheme preference."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "prefers-color-scheme: dark" in result.script_js

    def test_script_persists_preference(self, toggle_generator: ThemeToggleGenerator):
        """Test script persists user preference to localStorage."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "localStorage.setItem" in result.script_js
        assert "localStorage.getItem" in result.script_js

    def test_script_listens_for_system_changes(self, toggle_generator: ThemeToggleGenerator):
        """Test script listens for system preference changes."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "addEventListener('change'" in result.script_js

    def test_script_uses_data_theme_attribute(self, toggle_generator: ThemeToggleGenerator):
        """Test script uses data-theme attribute on root element."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "data-theme" in result.script_js
        assert "documentElement" in result.script_js


class TestDisabledToggleAccessibility:
    """Tests for disabled toggle behavior."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_disabled_returns_empty_button(self, toggle_generator: ThemeToggleGenerator):
        """Test disabled toggle returns empty button HTML."""
        result = toggle_generator.generate_toggle(enabled=False)

        assert result.button_html == ""

    def test_disabled_returns_empty_script(self, toggle_generator: ThemeToggleGenerator):
        """Test disabled toggle returns empty script."""
        result = toggle_generator.generate_toggle(enabled=False)

        assert result.script_js == ""

    def test_disabled_render_returns_empty(self, toggle_generator: ThemeToggleGenerator):
        """Test disabled render_toggle returns empty string."""
        html = toggle_generator.render_toggle(enabled=False)

        assert html == ""


class TestCSSAccessibility:
    """Tests for CSS accessibility features."""

    @pytest.fixture
    def css_injector(self) -> CSSInjector:
        """Create CSS injector."""
        return CSSInjector()

    def test_base_css_has_color_tokens(self, css_injector: CSSInjector):
        """Test base CSS defines color tokens for accessibility."""
        base_css = css_injector.BASE_CSS

        assert "--ad-color-text" in base_css
        assert "--ad-color-bg" in base_css
        assert "--ad-color-primary" in base_css

    def test_base_css_has_dark_mode(self, css_injector: CSSInjector):
        """Test base CSS includes dark mode support."""
        base_css = css_injector.BASE_CSS

        assert '[data-theme="dark"]' in base_css
        assert "prefers-color-scheme: dark" in base_css

    def test_base_css_has_font_settings(self, css_injector: CSSInjector):
        """Test base CSS defines accessible font settings."""
        base_css = css_injector.BASE_CSS

        assert "--ad-font-family" in base_css
        assert "--ad-line-height" in base_css
        # Reasonable line height for readability
        assert "1.6" in base_css

    def test_base_css_has_monospace_font(self, css_injector: CSSInjector):
        """Test base CSS defines monospace font for code."""
        base_css = css_injector.BASE_CSS

        assert "--ad-font-family-mono" in base_css

    def test_dark_mode_adjusts_colors(self, css_injector: CSSInjector):
        """Test dark mode adjusts colors for readability."""
        base_css = css_injector.BASE_CSS

        # Light and dark should have different background values
        assert "--ad-color-bg: #ffffff" in base_css  # Light
        assert "--ad-color-bg: #0f172a" in base_css  # Dark


class TestToggleHTMLStructure:
    """Tests for valid HTML structure."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_button_is_properly_closed(self, toggle_generator: ThemeToggleGenerator):
        """Test button tag is properly closed."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "<button" in result.button_html
        assert "</button>" in result.button_html

    def test_button_contains_span(self, toggle_generator: ThemeToggleGenerator):
        """Test button contains span for icon."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "<span" in result.button_html
        assert "</span>" in result.button_html

    def test_render_includes_script_tag(self, toggle_generator: ThemeToggleGenerator):
        """Test render_toggle includes script tags."""
        html = toggle_generator.render_toggle(enabled=True)

        assert "<script>" in html
        assert "</script>" in html

    def test_render_contains_button_and_script(self, toggle_generator: ThemeToggleGenerator):
        """Test render_toggle contains both button and script."""
        html = toggle_generator.render_toggle(enabled=True)

        assert "<button" in html
        assert "<script>" in html
        # Script should come after button
        button_pos = html.find("<button")
        script_pos = html.find("<script>")
        assert button_pos < script_pos


class TestCSSTagHTMLStructure:
    """Tests for valid CSS tag HTML structure."""

    def test_link_tag_has_rel_stylesheet(self):
        """Test link tag has rel=stylesheet."""
        tag = CSSTag(tag_type="link", content="style.css")
        html = tag.to_html()

        assert 'rel="stylesheet"' in html

    def test_link_tag_has_href(self):
        """Test link tag has href attribute."""
        tag = CSSTag(tag_type="link", content="https://example.com/style.css")
        html = tag.to_html()

        assert 'href="https://example.com/style.css"' in html

    def test_style_tag_is_properly_closed(self):
        """Test style tag is properly closed."""
        tag = CSSTag(tag_type="style", content=".test { color: red; }")
        html = tag.to_html()

        assert "<style>" in html
        assert "</style>" in html

    def test_style_tag_contains_content(self):
        """Test style tag contains CSS content."""
        css_content = ".test { color: red; }"
        tag = CSSTag(tag_type="style", content=css_content)
        html = tag.to_html()

        assert css_content in html

    def test_link_tag_with_attributes(self):
        """Test link tag includes custom attributes."""
        tag = CSSTag(
            tag_type="link",
            content="style.css",
            attributes={"crossorigin": "anonymous", "media": "screen"},
        )
        html = tag.to_html()

        assert 'crossorigin="anonymous"' in html
        assert 'media="screen"' in html


class TestToggleResultStructure:
    """Tests for ToggleResult named tuple."""

    def test_toggle_result_has_button_html(self):
        """Test ToggleResult has button_html field."""
        result = ToggleResult(button_html="<button>", script_js="")

        assert result.button_html == "<button>"

    def test_toggle_result_has_script_js(self):
        """Test ToggleResult has script_js field."""
        result = ToggleResult(button_html="", script_js="console.log('test');")

        assert result.script_js == "console.log('test');"

    def test_toggle_result_is_namedtuple(self):
        """Test ToggleResult is a named tuple."""
        result = ToggleResult(button_html="a", script_js="b")

        # Can unpack like tuple
        button, script = result
        assert button == "a"
        assert script == "b"


class TestARIAPatternCompliance:
    """Tests for ARIA authoring pattern compliance."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_follows_button_pattern(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle follows ARIA button pattern."""
        result = toggle_generator.generate_toggle(enabled=True)
        html = result.button_html

        # Must have button role (native button has implicit role)
        assert "<button" in html
        # Must have accessible name (via aria-label)
        assert "aria-label=" in html

    def test_follows_toggle_pattern(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle follows ARIA toggle button pattern."""
        result = toggle_generator.generate_toggle(enabled=True)
        html = result.button_html

        # Toggle buttons use aria-pressed
        assert "aria-pressed=" in html

    def test_decorative_icon_hidden(self, toggle_generator: ThemeToggleGenerator):
        """Test decorative icon is hidden from screen readers."""
        result = toggle_generator.generate_toggle(enabled=True)
        html = result.button_html

        # Icon should have aria-hidden
        assert 'aria-hidden="true"' in html

    def test_theme_labels_are_descriptive(self, toggle_generator: ThemeToggleGenerator):
        """Test theme toggle labels are descriptive."""
        result = toggle_generator.generate_toggle(enabled=True)
        script = result.script_js

        # Labels should clearly describe action
        assert "Switch to light mode" in script
        assert "Switch to dark mode" in script


class TestKeyboardAccessibility:
    """Tests for keyboard accessibility in JavaScript."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_uses_click_event(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle uses click event (works with keyboard)."""
        result = toggle_generator.generate_toggle(enabled=True)

        # Click event fires on Enter/Space for buttons
        assert "addEventListener('click'" in result.script_js

    def test_button_is_focusable(self, toggle_generator: ThemeToggleGenerator):
        """Test button is natively focusable (no tabindex needed)."""
        result = toggle_generator.generate_toggle(enabled=True)

        # Native button is focusable by default
        # Should NOT have tabindex="-1"
        assert 'tabindex="-1"' not in result.button_html


class TestColorContrastSupport:
    """Tests for color contrast accessibility support."""

    @pytest.fixture
    def css_injector(self) -> CSSInjector:
        """Create CSS injector."""
        return CSSInjector()

    def test_has_semantic_color_tokens(self, css_injector: CSSInjector):
        """Test CSS defines semantic color tokens."""
        base_css = css_injector.BASE_CSS

        # Semantic colors for status
        assert "--ad-color-success" in base_css
        assert "--ad-color-warning" in base_css
        assert "--ad-color-error" in base_css
        assert "--ad-color-info" in base_css

    def test_has_text_hierarchy(self, css_injector: CSSInjector):
        """Test CSS defines text color hierarchy."""
        base_css = css_injector.BASE_CSS

        assert "--ad-color-text" in base_css  # Primary text
        assert "--ad-color-text-secondary" in base_css  # Secondary text
        assert "--ad-color-text-muted" in base_css  # Muted text

    def test_dark_mode_maintains_hierarchy(self, css_injector: CSSInjector):
        """Test dark mode maintains text hierarchy."""
        base_css = css_injector.BASE_CSS

        # Dark mode section should redefine text colors
        dark_section_start = base_css.find('[data-theme="dark"]')
        assert dark_section_start > 0

        dark_section = base_css[dark_section_start:]
        assert "--ad-color-text:" in dark_section
        assert "--ad-color-text-secondary:" in dark_section


class TestCSSInjectorAccessibility:
    """Tests for CSSInjector accessibility integration."""

    @pytest.fixture
    def css_injector(self) -> CSSInjector:
        """Create CSS injector."""
        return CSSInjector()

    def test_base_css_included_by_default(self, css_injector: CSSInjector):
        """Test base CSS with accessible tokens is included by default."""
        tags = css_injector.generate_tags()

        assert len(tags) == 1
        assert tags[0].tag_type == "style"
        assert "--ad-color" in tags[0].content

    def test_can_override_with_inline(self, css_injector: CSSInjector):
        """Test custom CSS can override for accessibility needs."""
        tags = css_injector.generate_tags(
            css_inline=".custom { font-size: 1.2rem; }"  # Larger text
        )

        # Should have base + inline
        assert len(tags) == 2
        assert ".custom" in tags[1].content

    def test_render_head_produces_valid_html(self, css_injector: CSSInjector):
        """Test render_head_tags produces valid HTML."""
        html = css_injector.render_head_tags(
            css_url="theme.css",
            css_inline=".test {}",
        )

        # Should have link and style tags
        assert "<link" in html
        assert "<style>" in html
        assert "</style>" in html
