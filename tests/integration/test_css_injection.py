"""Integration tests for CSS injection.

Feature 008 - Template Customization & Theming
T346: Tests verifying CSS injection in HTML output and
ensuring CSS is ignored for Markdown/RST outputs.

Tests verify:
- CSS tags are injected in HTML output
- External CSS URL is linked correctly
- Inline CSS is embedded in style tags
- Theme toggle JS is included when enabled
- CSS injection is skipped for Markdown output
- CSS injection is skipped for RST output
"""

from __future__ import annotations

import pytest

from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant
from ansibledoctor.generator.css_injector import CSSInjector, CSSTag, ThemeToggleGenerator
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.generator.renderers.rst import RstRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata


class TestCSSTagGeneration:
    """Test CSS tag generation by CSSInjector."""

    def test_generates_base_css_by_default(self):
        """Base CSS is generated when include_base=True."""
        injector = CSSInjector()
        tags = injector.generate_tags(include_base=True)

        assert len(tags) >= 1
        # First tag should be base CSS
        base_tag = tags[0]
        assert base_tag.tag_type == "style"
        assert "--ad-color-primary" in base_tag.content
        assert "--ad-color-bg" in base_tag.content

    def test_generates_link_tag_for_external_url(self):
        """External CSS URL generates link tag."""
        injector = CSSInjector()
        tags = injector.generate_tags(
            css_url="https://example.com/theme.css",
            include_base=False,
        )

        assert len(tags) == 1
        link_tag = tags[0]
        assert link_tag.tag_type == "link"
        assert link_tag.content == "https://example.com/theme.css"

    def test_generates_style_tag_for_inline_css(self):
        """Inline CSS generates style tag."""
        injector = CSSInjector()
        custom_css = "body { background: red; }"
        tags = injector.generate_tags(
            css_inline=custom_css,
            include_base=False,
        )

        assert len(tags) == 1
        style_tag = tags[0]
        assert style_tag.tag_type == "style"
        assert custom_css in style_tag.content

    def test_css_ordering_base_then_external_then_inline(self):
        """CSS tags are ordered: base, external, inline."""
        injector = CSSInjector()
        tags = injector.generate_tags(
            css_url="https://example.com/theme.css",
            css_inline="body { color: blue; }",
            include_base=True,
        )

        assert len(tags) == 3

        # Order should be: base (style), external (link), inline (style)
        assert tags[0].tag_type == "style"  # Base
        assert "--ad-color-primary" in tags[0].content

        assert tags[1].tag_type == "link"  # External
        assert "theme.css" in tags[1].content

        assert tags[2].tag_type == "style"  # Inline
        assert "color: blue" in tags[2].content


class TestCSSTagHtmlRendering:
    """Test CSS tag rendering to HTML."""

    def test_link_tag_renders_correctly(self):
        """Link tag renders as valid HTML link element."""
        tag = CSSTag(
            tag_type="link",
            content="https://example.com/styles.css",
        )

        html = tag.to_html()

        assert '<link rel="stylesheet"' in html
        assert 'href="https://example.com/styles.css"' in html

    def test_link_tag_includes_attributes(self):
        """Link tag includes additional attributes."""
        tag = CSSTag(
            tag_type="link",
            content="https://cdn.example.com/styles.css",
            attributes={"crossorigin": "anonymous", "integrity": "sha256-abc"},
        )

        html = tag.to_html()

        assert 'crossorigin="anonymous"' in html
        assert 'integrity="sha256-abc"' in html

    def test_style_tag_renders_correctly(self):
        """Style tag wraps content in style element."""
        tag = CSSTag(
            tag_type="style",
            content="body { margin: 0; }",
        )

        html = tag.to_html()

        assert "<style>" in html
        assert "</style>" in html
        assert "body { margin: 0; }" in html


class TestThemeToggleGeneration:
    """Test theme toggle HTML and JS generation."""

    def test_generates_toggle_when_enabled(self):
        """Toggle generates HTML and JS when enabled."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        assert result.button_html != ""
        assert result.script_js != ""

    def test_toggle_button_has_aria_attributes(self):
        """Toggle button includes ARIA attributes for accessibility."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        assert "aria-pressed" in result.button_html
        assert "aria-label" in result.button_html

    def test_toggle_button_has_id(self):
        """Toggle button has correct ID for JS targeting."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        assert 'id="ad-theme-toggle"' in result.button_html

    def test_toggle_js_uses_localstorage(self):
        """Toggle JS uses localStorage for persistence."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        assert "localStorage" in result.script_js

    def test_toggle_js_sets_data_theme(self):
        """Toggle JS sets data-theme attribute."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        assert "data-theme" in result.script_js

    def test_toggle_disabled_returns_empty(self):
        """Disabled toggle returns empty strings."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=False)

        assert result.button_html == ""
        assert result.script_js == ""


class TestCSSInjectionInTemplateContext:
    """Test CSS injection through TemplateContext."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="test_role",
            path=role_path,
            description="Test role for CSS injection",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_context_includes_css_tags_with_theme(self, sample_role):
        """TemplateContext includes CSS tags when theme_config provided."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        ctx_dict = context.to_dict()

        # Should have CSS tags
        assert "css_tags" in ctx_dict
        css_tags = ctx_dict["css_tags"]
        # css_tags is a list of CSSTag objects
        assert len(css_tags) >= 1
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")
        assert "--ad-color-primary" in all_css

    def test_context_includes_theme_toggle_when_enabled(self, sample_role):
        """TemplateContext includes toggle HTML when enabled."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        ctx_dict = context.to_dict()

        assert "theme_toggle_html" in ctx_dict
        assert "ad-theme-toggle" in ctx_dict["theme_toggle_html"]

    def test_context_excludes_toggle_when_disabled(self, sample_role):
        """TemplateContext excludes toggle HTML when disabled."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MINIMAL,
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=False,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        ctx_dict = context.to_dict()

        # Toggle should be empty
        assert ctx_dict.get("theme_toggle_html", "") == ""


class TestHtmlOutputIncludesCSS:
    """Test HTML output includes CSS injection."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "html_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="html_test_role",
            path=role_path,
            description="Test role for HTML output",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_html_output_contains_css_variables(self, sample_role):
        """CSS tags contain CSS variable definitions for HTML output."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # CSS tags are available in context for templates to render
        css_tags = context.css_tags
        assert len(css_tags) >= 1
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")

        # Should contain CSS variables
        assert "--ad-color-primary" in all_css
        assert "--ad-color-bg" in all_css

        # Verify tags can be converted to HTML
        for tag in css_tags:
            html = tag.to_html()
            assert "<style>" in html or "<link" in html

    def test_html_output_contains_dark_mode_css(self, sample_role):
        """CSS tags contain dark mode CSS rules for dark scheme."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # CSS tags should contain dark mode styles
        css_tags = context.css_tags
        assert len(css_tags) >= 1
        all_css = "".join(t.content for t in css_tags if t.tag_type == "style")

        # Dark mode CSS should have data-theme selector
        assert '[data-theme="dark"]' in all_css or "prefers-color-scheme: dark" in all_css

    def test_html_output_contains_toggle_when_enabled(self, sample_role):
        """Theme toggle is available in context when enabled."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # Toggle HTML should be available in context
        assert context.theme_toggle_html is not None
        assert "ad-theme-toggle" in context.theme_toggle_html

        # Toggle JS should also be available
        assert context.theme_toggle_js is not None
        assert "localStorage" in context.theme_toggle_js


class TestMarkdownOutputExcludesCSS:
    """Test Markdown output does not include CSS injection."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "md_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="md_test_role",
            path=role_path,
            description="Test role for Markdown output",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_markdown_output_no_css_variables(self, sample_role):
        """Markdown output does not contain CSS variables."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        renderer = MarkdownRenderer()
        result = renderer.render(context)

        # Should NOT contain CSS variables
        assert "--ad-color-primary" not in result
        assert "<style>" not in result

    def test_markdown_output_no_theme_toggle(self, sample_role):
        """Markdown output does not contain theme toggle."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.MARKDOWN,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        renderer = MarkdownRenderer()
        result = renderer.render(context)

        # Should NOT contain toggle
        assert "ad-theme-toggle" not in result


class TestRstOutputExcludesCSS:
    """Test RST output does not include CSS injection."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "rst_test_role"
        role_path.mkdir()

        return AnsibleRole(
            name="rst_test_role",
            path=role_path,
            description="Test role for RST output",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_rst_output_no_css_variables(self, sample_role):
        """RST output does not contain CSS variables."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.RST,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        renderer = RstRenderer()
        result = renderer.render(context)

        # Should NOT contain CSS variables
        assert "--ad-color-primary" not in result
        assert "<style>" not in result

    def test_rst_output_no_theme_toggle(self, sample_role):
        """RST output does not contain theme toggle."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MINIMAL,
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.RST,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        renderer = RstRenderer()
        result = renderer.render(context)

        # Should NOT contain toggle
        assert "ad-theme-toggle" not in result


class TestExternalCSSUrl:
    """Test external CSS URL injection."""

    def test_external_url_generates_link_tag(self):
        """External CSS URL creates link tag."""
        injector = CSSInjector()
        tags = injector.generate_tags(
            css_url="https://cdn.example.com/theme.css",
            include_base=False,
        )

        assert any(t.tag_type == "link" and "theme.css" in t.content for t in tags)

    def test_external_url_with_base_css(self):
        """External URL can be combined with base CSS."""
        injector = CSSInjector()
        tags = injector.generate_tags(
            css_url="https://cdn.example.com/custom.css",
            include_base=True,
        )

        # Should have both base style and external link
        has_base = any(t.tag_type == "style" and "--ad-color-" in t.content for t in tags)
        has_external = any(t.tag_type == "link" for t in tags)

        assert has_base
        assert has_external

    def test_render_head_tags_produces_html(self):
        """render_head_tags produces complete HTML string."""
        injector = CSSInjector()
        html = injector.render_head_tags(
            css_url="https://example.com/styles.css",
            css_inline="body { padding: 0; }",
            include_base=True,
        )

        # Should be a string with all tags
        assert isinstance(html, str)
        assert "<style>" in html
        assert '<link rel="stylesheet"' in html
        assert "padding: 0" in html
