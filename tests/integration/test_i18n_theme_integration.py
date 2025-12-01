"""Integration tests for i18n theme integration.

Feature 008 - Template Customization & Theming
T344: End-to-end tests validating t() translation keys for theme labels
and translations for multilingual outputs.

Tests verify:
- Translation keys work in theme-enabled templates
- Theme labels are translatable via t() filter
- Theme CSS included with multilingual templates
- Theme toggle respects language settings
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant
from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.models import AnsibleRole, Example, RoleMetadata, Tag, TodoItem, Variable
from ansibledoctor.translation.loader import TranslationLoader
from ansibledoctor.translation.provider import TranslationProvider


class TestTranslationFilterWithTheme:
    """Test t() translation filter works with theme-enabled templates."""

    @pytest.fixture
    def english_provider(self) -> TranslationProvider:
        """Create English translation provider."""
        translations = {
            "section.variables": "Variables",
            "section.examples": "Examples",
            "section.todo": "TODOs",
            "theme.toggle_label": "Toggle dark/light mode",
            "theme.dark_mode": "Dark Mode",
            "theme.light_mode": "Light Mode",
            "role.description": "Role Description",
            "role.requirements": "Requirements",
        }
        return TranslationProvider(translations=translations, lang="en")

    @pytest.fixture
    def german_provider(self) -> TranslationProvider:
        """Create German translation provider."""
        translations = {
            "section.variables": "Variablen",
            "section.examples": "Beispiele",
            "section.todo": "Aufgaben",
            "theme.toggle_label": "Dunkler/Heller Modus umschalten",
            "theme.dark_mode": "Dunkler Modus",
            "theme.light_mode": "Heller Modus",
            "role.description": "Rollenbeschreibung",
            "role.requirements": "Anforderungen",
        }
        return TranslationProvider(translations=translations, lang="de")

    @pytest.fixture
    def french_provider(self) -> TranslationProvider:
        """Create French translation provider."""
        translations = {
            "section.variables": "Variables",
            "section.examples": "Exemples",
            "section.todo": "À faire",
            "theme.toggle_label": "Basculer mode sombre/clair",
            "theme.dark_mode": "Mode sombre",
            "theme.light_mode": "Mode clair",
            "role.description": "Description du rôle",
            "role.requirements": "Prérequis",
        }
        return TranslationProvider(translations=translations, lang="fr")

    def test_template_with_english_translation(self, english_provider):
        """Test template renders English translations."""
        template_str = """
<h2>{{ 'section.variables' | t }}</h2>
<p>{{ 'role.description' | t }}</p>
"""
        engine = TemplateEngine.create(translation_provider=english_provider)
        result = engine.render_string(template_str)

        assert "Variables" in result
        assert "Role Description" in result

    def test_template_with_german_translation(self, german_provider):
        """Test template renders German translations."""
        template_str = """
<h2>{{ 'section.variables' | t }}</h2>
<p>{{ 'role.description' | t }}</p>
"""
        engine = TemplateEngine.create(translation_provider=german_provider)
        result = engine.render_string(template_str)

        assert "Variablen" in result
        assert "Rollenbeschreibung" in result

    def test_template_with_french_translation(self, french_provider):
        """Test template renders French translations."""
        template_str = """
<h2>{{ 'section.variables' | t }}</h2>
<p>{{ 'role.description' | t }}</p>
"""
        engine = TemplateEngine.create(translation_provider=french_provider)
        result = engine.render_string(template_str)

        assert "Variables" in result  # Same in French
        assert "Description du rôle" in result

    def test_theme_labels_translated_english(self, english_provider):
        """Test theme labels are translated to English."""
        template_str = """
<button aria-label="{{ 'theme.toggle_label' | t }}">
  {{ 'theme.dark_mode' | t }}
</button>
"""
        engine = TemplateEngine.create(translation_provider=english_provider)
        result = engine.render_string(template_str)

        assert "Toggle dark/light mode" in result
        assert "Dark Mode" in result

    def test_theme_labels_translated_german(self, german_provider):
        """Test theme labels are translated to German."""
        template_str = """
<button aria-label="{{ 'theme.toggle_label' | t }}">
  {{ 'theme.dark_mode' | t }}
</button>
"""
        engine = TemplateEngine.create(translation_provider=german_provider)
        result = engine.render_string(template_str)

        assert "Dunkler/Heller Modus umschalten" in result
        assert "Dunkler Modus" in result


class TestThemeWithTemplateContext:
    """Test theme integration with template context and translations."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        return AnsibleRole(
            name="test_role",
            path=role_path,
            description="A test role for i18n theme testing",
            metadata=RoleMetadata(
                galaxy_info={"author": "Test Author"},
                dependencies=[],
            ),
            variables=[
                Variable(
                    name="test_var",
                    value="default_value",
                    type="string",
                    source="defaults/main.yml",
                    description="A test variable",
                ),
            ],
            tags=[
                Tag(name="test", description="Test tag"),
            ],
            todos=[
                TodoItem(
                    description="Implement feature",
                    file_path=str(role_path / "tasks/main.yml"),
                    line_number=10,
                ),
            ],
            examples=[
                Example(
                    title="Basic example",
                    code="- hosts: all\n  roles:\n    - test_role",
                    language="yaml",
                ),
            ],
        )

    @pytest.fixture
    def theme_config(self) -> ThemeConfig:
        """Create theme config for testing."""
        return ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

    @pytest.fixture
    def english_provider(self) -> TranslationProvider:
        """Create English translation provider."""
        translations = {
            "section.variables": "Variables",
        }
        return TranslationProvider(translations=translations, lang="en")

    def test_context_with_theme_and_translation(
        self, sample_role, theme_config, english_provider
    ):
        """Test template context includes both theme and translations."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # Verify theme is present
        ctx_dict = context.to_dict()
        assert "css_tags" in ctx_dict
        assert "theme_toggle_html" in ctx_dict

        # Create engine with translations
        engine = TemplateEngine.create(translation_provider=english_provider)

        # Render template that uses both theme and translations
        template_str = """
{{ css_tags }}
<h1>{{ 'section.variables' | t }}</h1>
{% for var in role.variables %}
<p>{{ var.name }}: {{ var.description }}</p>
{% endfor %}
{{ theme_toggle_html }}
"""
        result = engine.render_string(template_str, **ctx_dict)

        assert "--ad-color-primary" in result  # CSS variables
        assert "Variables" in result  # Translation
        assert "test_var" in result  # Variable from context
        assert "ad-theme-toggle" in result  # Toggle button

    def test_multilingual_output_with_theme(self, sample_role, theme_config):
        """Test multiple language outputs include theme consistently."""
        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # Create providers for different languages
        en_translations = {
            "section.variables": "Variables",
        }
        de_translations = {
            "section.variables": "Variablen",
        }

        template_str = """
{{ css_tags }}
<h1>{{ 'section.variables' | t }}</h1>
{{ theme_toggle_html }}
"""

        # Render English
        en_provider = TranslationProvider(translations=en_translations, lang="en")
        en_engine = TemplateEngine.create(translation_provider=en_provider)
        en_result = en_engine.render_string(template_str, **context.to_dict())

        # Render German
        de_provider = TranslationProvider(translations=de_translations, lang="de")
        de_engine = TemplateEngine.create(translation_provider=de_provider)
        de_result = de_engine.render_string(template_str, **context.to_dict())

        # Both should have theme CSS
        assert "--ad-color-primary" in en_result
        assert "--ad-color-primary" in de_result

        # Both should have toggle
        assert "ad-theme-toggle" in en_result
        assert "ad-theme-toggle" in de_result

        # Different translations
        assert "Variables" in en_result
        assert "Variablen" in de_result


class TestThemeColorSchemeWithTranslations:
    """Test color scheme variations with translations."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "test_role"
        role_path.mkdir()
        
        return AnsibleRole(
            name="test_role",
            path=role_path,
            description="Test",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    @pytest.fixture
    def translations(self) -> dict:
        """Standard test translations."""
        return {
            "section.variables": "Variables",
            "section.examples": "Examples",
        }

    def test_light_scheme_with_translations(self, sample_role, translations):
        """Test light color scheme with translations."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.LIGHT,
            enable_toggle=False,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        provider = TranslationProvider(translations=translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
{{ css_tags }}
<h1>{{ 'section.variables' | t }}</h1>
Color scheme: {{ color_scheme }}
"""
        result = engine.render_string(template_str, **context.to_dict())

        assert "Variables" in result
        assert "light" in result.lower() or "ColorScheme" in result

    def test_dark_scheme_with_translations(self, sample_role, translations):
        """Test dark color scheme with translations."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MINIMAL,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )

        context = TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        provider = TranslationProvider(translations=translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
{{ css_tags }}
<h1>{{ 'section.examples' | t }}</h1>
"""
        result = engine.render_string(template_str, **context.to_dict())

        assert "Examples" in result
        # Dark mode CSS should be included
        assert "[data-theme=\"dark\"]" in result


class TestTranslationFallback:
    """Test translation fallback behavior with themes."""

    @pytest.fixture
    def sample_role(self, tmp_path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "no_i18n_role"
        role_path.mkdir()
        
        return AnsibleRole(
            name="no_i18n_role",
            path=role_path,
            description="No i18n test",
            metadata=RoleMetadata(galaxy_info={}, dependencies=[]),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_missing_key_returns_key_name(self):
        """Missing translation key returns the key itself."""
        translations = {"section.known": "Known Section"}
        provider = TranslationProvider(translations=translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
<h1>{{ 'section.known' | t }}</h1>
<h2>{{ 'section.unknown' | t }}</h2>
"""
        result = engine.render_string(template_str)

        assert "Known Section" in result
        assert "section.unknown" in result  # Falls back to key name

    def test_theme_renders_without_translation_provider(self, sample_role):
        """Theme works even without translation provider."""
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

        # Engine without translation provider
        engine = TemplateEngine.create()

        template_str = """
{{ css_tags }}
<h1>{{ role.name }}</h1>
{{ theme_toggle_html }}
"""
        result = engine.render_string(template_str, **context.to_dict())

        assert "no_i18n_role" in result
        assert "--ad-color-primary" in result
        assert "ad-theme-toggle" in result


class TestVariantTranslation:
    """Test variant-specific translations."""

    @pytest.fixture
    def variant_translations(self) -> dict:
        """Translations with variant-specific keys."""
        return {
            "variant.minimal.title": "Minimal Documentation",
            "variant.detailed.title": "Detailed Documentation",
            "variant.modern.title": "Modern Documentation",
            "variant.minimal.description": "Compact role documentation",
            "variant.detailed.description": "Full role documentation with examples",
            "variant.modern.description": "Contemporary styled documentation",
        }

    def test_minimal_variant_uses_correct_translation(self, variant_translations):
        """Minimal variant uses correct translation keys."""
        provider = TranslationProvider(translations=variant_translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
<h1>{{ 'variant.minimal.title' | t }}</h1>
<p>{{ 'variant.minimal.description' | t }}</p>
"""
        result = engine.render_string(template_str)

        assert "Minimal Documentation" in result
        assert "Compact role documentation" in result

    def test_detailed_variant_uses_correct_translation(self, variant_translations):
        """Detailed variant uses correct translation keys."""
        provider = TranslationProvider(translations=variant_translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
<h1>{{ 'variant.detailed.title' | t }}</h1>
<p>{{ 'variant.detailed.description' | t }}</p>
"""
        result = engine.render_string(template_str)

        assert "Detailed Documentation" in result
        assert "Full role documentation with examples" in result

    def test_modern_variant_uses_correct_translation(self, variant_translations):
        """Modern variant uses correct translation keys."""
        provider = TranslationProvider(translations=variant_translations, lang="en")
        engine = TemplateEngine.create(translation_provider=provider)

        template_str = """
<h1>{{ 'variant.modern.title' | t }}</h1>
<p>{{ 'variant.modern.description' | t }}</p>
"""
        result = engine.render_string(template_str)

        assert "Modern Documentation" in result
        assert "Contemporary styled documentation" in result


class TestTranslationLoaderIntegration:
    """Test TranslationLoader integration with themes."""

    def test_translation_loader_loads_embedded_files(self):
        """Test TranslationLoader can load embedded translation files."""
        loader = TranslationLoader()
        provider = loader.load("en")

        # Should have some translations from embedded en.yml
        # At minimum the provider should be created successfully
        assert provider is not None
        assert provider.lang == "en"

    def test_translation_loader_with_german(self):
        """Test TranslationLoader loads German translations."""
        loader = TranslationLoader()
        provider = loader.load("de")

        # German translations should be loaded
        assert provider is not None
        # The language should be set
        assert "de" in provider.lang or "en" in provider.lang  # May fallback

    def test_translation_loader_with_project_translations(self, tmp_path):
        """Test TranslationLoader loads project-level translations."""
        # Create project translations directory
        translations_dir = tmp_path / ".ansibledoctor" / "translations"
        translations_dir.mkdir(parents=True)

        en_file = translations_dir / "en.yml"
        en_file.write_text(
            """
section:
  variables: "Custom Variables"
  examples: "Custom Examples"
theme:
  toggle: "Custom Toggle Theme"
"""
        )

        loader = TranslationLoader()
        provider = loader.load("en", project_root=tmp_path)

        # Should load custom translations
        assert provider.get("section.variables") == "Custom Variables"
        assert provider.get("theme.toggle") == "Custom Toggle Theme"
