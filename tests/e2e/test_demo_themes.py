"""End-to-end tests for theme demo outputs.

Feature 008 - Template Customization & Theming
T354: E2E demo tests validating demo outputs and theme toggle
"""

from pathlib import Path

import pytest

from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant
from ansibledoctor.generator.css_injector import CSSInjector, CSSTag, ThemeToggleGenerator


# Path to demo directory
DEMO_DIR = Path(__file__).parent.parent.parent / "demo"


class TestDemoTemplatesExist:
    """Tests that verify demo templates exist and are valid."""

    def test_demo_templates_directory_exists(self):
        """Test demo/templates directory exists."""
        templates_dir = DEMO_DIR / "templates"
        assert templates_dir.exists(), "demo/templates directory should exist"

    def test_minimal_template_exists(self):
        """Test minimal variant template exists."""
        template = DEMO_DIR / "templates" / "role.minimal.html.j2"
        assert template.exists(), "role.minimal.html.j2 should exist"

    def test_detailed_template_exists(self):
        """Test detailed variant template exists."""
        template = DEMO_DIR / "templates" / "role.detailed.html.j2"
        assert template.exists(), "role.detailed.html.j2 should exist"

    def test_modern_template_exists(self):
        """Test modern variant template exists."""
        template = DEMO_DIR / "templates" / "role.modern.html.j2"
        assert template.exists(), "role.modern.html.j2 should exist"

    def test_templates_readme_exists(self):
        """Test templates README exists."""
        readme = DEMO_DIR / "templates" / "README.md"
        assert readme.exists(), "templates/README.md should exist"


class TestDemoCSSExist:
    """Tests that verify demo CSS files exist and are valid."""

    def test_demo_css_directory_exists(self):
        """Test demo/css directory exists."""
        css_dir = DEMO_DIR / "css"
        assert css_dir.exists(), "demo/css directory should exist"

    def test_sample_theme_css_exists(self):
        """Test sample-theme.css exists."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        assert css_file.exists(), "sample-theme.css should exist"

    def test_inline_overrides_css_exists(self):
        """Test inline-overrides.css exists."""
        css_file = DEMO_DIR / "css" / "inline-overrides.css"
        assert css_file.exists(), "inline-overrides.css should exist"


class TestDemoConfigsExist:
    """Tests that verify demo config examples exist."""

    def test_config_examples_directory_exists(self):
        """Test demo/config-examples directory exists."""
        config_dir = DEMO_DIR / "config-examples"
        assert config_dir.exists(), "demo/config-examples directory should exist"

    def test_minimal_config_exists(self):
        """Test minimal theme config exists."""
        config = DEMO_DIR / "config-examples" / "minimal-theme.ansibledoctor.yml"
        assert config.exists(), "minimal-theme.ansibledoctor.yml should exist"

    def test_detailed_config_exists(self):
        """Test detailed theme config exists."""
        config = DEMO_DIR / "config-examples" / "detailed-theme.ansibledoctor.yml"
        assert config.exists(), "detailed-theme.ansibledoctor.yml should exist"

    def test_modern_config_exists(self):
        """Test modern theme config exists."""
        config = DEMO_DIR / "config-examples" / "modern-theme.ansibledoctor.yml"
        assert config.exists(), "modern-theme.ansibledoctor.yml should exist"

    def test_dark_config_exists(self):
        """Test dark theme config exists."""
        config = DEMO_DIR / "config-examples" / "dark-theme.ansibledoctor.yml"
        assert config.exists(), "dark-theme.ansibledoctor.yml should exist"

    def test_custom_css_config_exists(self):
        """Test custom CSS config exists."""
        config = DEMO_DIR / "config-examples" / "custom-css.ansibledoctor.yml"
        assert config.exists(), "custom-css.ansibledoctor.yml should exist"


class TestDemoTemplateContent:
    """Tests that verify demo template content is valid."""

    def test_minimal_template_has_basic_structure(self):
        """Test minimal template has basic HTML structure."""
        template = DEMO_DIR / "templates" / "role.minimal.html.j2"
        content = template.read_text()

        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_minimal_template_has_css_tags(self):
        """Test minimal template includes CSS tags."""
        template = DEMO_DIR / "templates" / "role.minimal.html.j2"
        content = template.read_text()

        assert "css_tags" in content

    def test_minimal_template_has_role_name(self):
        """Test minimal template displays role name."""
        template = DEMO_DIR / "templates" / "role.minimal.html.j2"
        content = template.read_text()

        assert "role.name" in content

    def test_detailed_template_has_metadata(self):
        """Test detailed template has metadata section."""
        template = DEMO_DIR / "templates" / "role.detailed.html.j2"
        content = template.read_text()

        assert "role.author" in content or "metadata" in content.lower()
        assert "role.license" in content

    def test_detailed_template_has_variables_table(self):
        """Test detailed template has variables table."""
        template = DEMO_DIR / "templates" / "role.detailed.html.j2"
        content = template.read_text()

        assert "<table" in content
        assert "variables" in content.lower()

    def test_detailed_template_has_theme_toggle(self):
        """Test detailed template supports theme toggle."""
        template = DEMO_DIR / "templates" / "role.detailed.html.j2"
        content = template.read_text()

        assert "theme_toggle" in content

    def test_modern_template_has_hero_section(self):
        """Test modern template has hero section."""
        template = DEMO_DIR / "templates" / "role.modern.html.j2"
        content = template.read_text(encoding="utf-8")

        assert "ad-hero" in content

    def test_modern_template_has_card_layout(self):
        """Test modern template uses card layout."""
        template = DEMO_DIR / "templates" / "role.modern.html.j2"
        content = template.read_text(encoding="utf-8")

        assert "ad-card" in content

    def test_modern_template_has_timeline(self):
        """Test modern template has timeline visualization."""
        template = DEMO_DIR / "templates" / "role.modern.html.j2"
        content = template.read_text(encoding="utf-8")

        assert "ad-timeline" in content


class TestDemoCSSContent:
    """Tests that verify demo CSS content is valid."""

    def test_sample_css_has_css_variables(self):
        """Test sample CSS defines CSS custom properties."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        content = css_file.read_text()

        assert "--ad-color-primary" in content
        assert ":root" in content

    def test_sample_css_has_dark_mode(self):
        """Test sample CSS has dark mode support."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        content = css_file.read_text()

        assert '[data-theme="dark"]' in content

    def test_sample_css_has_toggle_button_styles(self):
        """Test sample CSS has toggle button styles."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        content = css_file.read_text()

        assert ".ad-theme-toggle" in content

    def test_sample_css_has_responsive_styles(self):
        """Test sample CSS has responsive styles."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        content = css_file.read_text()

        assert "@media" in content

    def test_sample_css_has_print_styles(self):
        """Test sample CSS has print styles."""
        css_file = DEMO_DIR / "css" / "sample-theme.css"
        content = css_file.read_text()

        assert "@media print" in content

    def test_inline_css_is_minimal(self):
        """Test inline CSS example is minimal."""
        css_file = DEMO_DIR / "css" / "inline-overrides.css"
        content = css_file.read_text()

        # Should be small
        assert len(content) < 500


class TestThemeToggleIntegration:
    """Tests for theme toggle integration with demo templates."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create toggle generator."""
        return ThemeToggleGenerator()

    def test_toggle_html_is_valid(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle HTML is valid for embedding."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "<button" in result.button_html
        assert "id=" in result.button_html
        assert "aria-" in result.button_html

    def test_toggle_script_is_self_contained(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle script has no external dependencies."""
        result = toggle_generator.generate_toggle(enabled=True)

        # Should be an IIFE
        assert "(function()" in result.script_js
        assert "})();" in result.script_js

        # Should not import anything
        assert "import " not in result.script_js
        assert "require(" not in result.script_js

    def test_toggle_stores_preference(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle stores user preference."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "localStorage" in result.script_js

    def test_toggle_respects_system_preference(self, toggle_generator: ThemeToggleGenerator):
        """Test toggle respects system color scheme."""
        result = toggle_generator.generate_toggle(enabled=True)

        assert "prefers-color-scheme" in result.script_js


class TestCSSInjectorWithDemoCSS:
    """Tests for CSS injector with demo CSS files."""

    @pytest.fixture
    def css_injector(self) -> CSSInjector:
        """Create CSS injector."""
        return CSSInjector()

    def test_can_load_demo_css_url(self, css_injector: CSSInjector):
        """Test CSS injector can create tag for demo CSS URL."""
        css_url = "../css/sample-theme.css"
        tags = css_injector.generate_tags(css_url=css_url)

        # Should have base + url
        assert len(tags) == 2
        assert any(css_url in tag.content for tag in tags if tag.tag_type == "link")

    def test_can_load_demo_inline_css(self, css_injector: CSSInjector):
        """Test CSS injector can load demo inline CSS."""
        inline_css = (DEMO_DIR / "css" / "inline-overrides.css").read_text()
        tags = css_injector.generate_tags(css_inline=inline_css)

        # Should have base + inline
        assert len(tags) == 2
        assert any("--ad-color-primary" in tag.content for tag in tags)

    def test_render_produces_valid_html(self, css_injector: CSSInjector):
        """Test render produces valid HTML tags."""
        html = css_injector.render_head_tags(
            css_url="theme.css",
            css_inline=":root { --custom: blue; }",
        )

        assert "<link" in html
        assert "<style>" in html
        assert "</style>" in html


class TestThemeConfigFromDemoConfigs:
    """Tests for ThemeConfig loading from demo config patterns."""

    def test_can_create_minimal_config(self):
        """Test creating minimal theme config."""
        config = ThemeConfig(
            variant=ThemeVariant.MINIMAL,
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=False,
        )

        assert config.variant == ThemeVariant.MINIMAL
        assert config.enable_toggle is False

    def test_can_create_detailed_config(self):
        """Test creating detailed theme config."""
        config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        assert config.variant == ThemeVariant.DETAILED
        assert config.enable_toggle is True

    def test_can_create_modern_config(self):
        """Test creating modern theme config."""
        config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        assert config.variant == ThemeVariant.MODERN

    def test_can_create_dark_config(self):
        """Test creating dark theme config."""
        config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.DARK,
            enable_toggle=False,
        )

        assert config.color_scheme == ColorScheme.DARK

    def test_can_create_custom_css_config(self):
        """Test creating custom CSS config."""
        config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            css_url="https://example.com/theme.css",
            css_inline=":root { --custom: red; }",
            enable_toggle=True,
        )

        assert config.css_url == "https://example.com/theme.css"
        assert config.css_inline is not None


class TestDemoRoleStructure:
    """Tests that verify demo role structure for theme testing."""

    def test_demo_role_exists(self):
        """Test demo role directory exists."""
        demo_role = DEMO_DIR / "role_demo_namespace.demo_demo_role"
        assert demo_role.exists(), "Demo role should exist"

    def test_demo_role_has_config(self):
        """Test demo role has .ansibledoctor.yml."""
        config = DEMO_DIR / "role_demo_namespace.demo_demo_role" / ".ansibledoctor.yml"
        assert config.exists(), "Demo role should have config file"

    def test_demo_role_has_tasks(self):
        """Test demo role has tasks directory."""
        tasks = DEMO_DIR / "role_demo_namespace.demo_demo_role" / "tasks"
        assert tasks.exists(), "Demo role should have tasks"

    def test_demo_role_has_defaults(self):
        """Test demo role has defaults directory."""
        defaults = DEMO_DIR / "role_demo_namespace.demo_demo_role" / "defaults"
        assert defaults.exists(), "Demo role should have defaults"
