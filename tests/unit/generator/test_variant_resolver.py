"""Unit tests for VariantTemplateResolver.

Feature 008 - Template Customization & Theming
T336: TDD unit tests for variant resolution and fallback chains
"""

from unittest.mock import MagicMock

import pytest

from ansibledoctor.config.theme import ThemeVariant
from ansibledoctor.generator.cascading_loader import (
    CascadingTemplateLoader,
    TemplateNotFoundError,
    TemplateSource,
)
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.generator.variant_resolver import (
    ResolvedTemplate,
    Variant,
    VariantTemplateResolver,
)


class TestVariantEnum:
    """Test Variant enum values."""

    def test_minimal_variant(self):
        """Variant.MINIMAL should have value 'minimal'."""
        assert Variant.MINIMAL == "minimal"
        assert Variant.MINIMAL.value == "minimal"

    def test_detailed_variant(self):
        """Variant.DETAILED should have value 'detailed'."""
        assert Variant.DETAILED == "detailed"
        assert Variant.DETAILED.value == "detailed"

    def test_modern_variant(self):
        """Variant.MODERN should have value 'modern'."""
        assert Variant.MODERN == "modern"
        assert Variant.MODERN.value == "modern"

    def test_default_variant(self):
        """Variant.DEFAULT should have value 'default'."""
        assert Variant.DEFAULT == "default"
        assert Variant.DEFAULT.value == "default"

    def test_variant_from_theme_variant(self):
        """Variant can be created from ThemeVariant."""
        # ThemeVariant and Variant should be compatible
        assert Variant(ThemeVariant.MINIMAL.value) == Variant.MINIMAL
        assert Variant(ThemeVariant.DETAILED.value) == Variant.DETAILED
        assert Variant(ThemeVariant.MODERN.value) == Variant.MODERN


class TestResolvedTemplate:
    """Test ResolvedTemplate dataclass."""

    def test_resolved_template_creation(self):
        """ResolvedTemplate should hold resolution result."""
        resolved = ResolvedTemplate(
            name="role.modern.html.j2",
            base_name="role",
            variant=Variant.MODERN,
            format=OutputFormat.HTML,
            is_fallback=False,
        )
        assert resolved.name == "role.modern.html.j2"
        assert resolved.base_name == "role"
        assert resolved.variant == Variant.MODERN
        assert resolved.format == OutputFormat.HTML
        assert resolved.is_fallback is False

    def test_resolved_template_is_frozen(self):
        """ResolvedTemplate should be immutable."""
        resolved = ResolvedTemplate(
            name="role.html.j2",
            base_name="role",
            variant=Variant.DETAILED,
            format=OutputFormat.HTML,
            is_fallback=False,
        )
        with pytest.raises(Exception):  # FrozenInstanceError
            resolved.name = "other.j2"

    def test_candidates_list(self):
        """candidates property should return ordered fallback list."""
        resolved = ResolvedTemplate(
            name="role.modern.html.j2",
            base_name="role",
            variant=Variant.MODERN,
            format=OutputFormat.HTML,
            is_fallback=False,
        )
        candidates = resolved.candidates
        assert candidates == [
            "role.modern.html.j2",
            "role.html.j2",
            "role.default.html.j2",
            "role.j2",
        ]

    def test_candidates_for_markdown(self):
        """candidates should use correct format extension."""
        resolved = ResolvedTemplate(
            name="collection.minimal.md.j2",
            base_name="collection",
            variant=Variant.MINIMAL,
            format=OutputFormat.MARKDOWN,
            is_fallback=False,
        )
        candidates = resolved.candidates
        assert "collection.minimal.md.j2" in candidates
        assert "collection.md.j2" in candidates


class TestVariantTemplateResolverInit:
    """Test VariantTemplateResolver initialization."""

    def test_requires_loader(self):
        """VariantTemplateResolver requires a CascadingTemplateLoader."""
        loader = MagicMock(spec=CascadingTemplateLoader)
        resolver = VariantTemplateResolver(loader)
        assert resolver._loader is loader

    def test_default_variant_is_detailed(self):
        """Default variant should be DETAILED when not specified."""
        loader = MagicMock(spec=CascadingTemplateLoader)
        resolver = VariantTemplateResolver(loader)
        assert resolver.default_variant == Variant.DETAILED


class TestResolutionChain:
    """Test template resolution fallback chain."""

    @pytest.fixture
    def mock_loader(self):
        """Create a mock CascadingTemplateLoader."""
        return MagicMock(spec=CascadingTemplateLoader)

    @pytest.fixture
    def resolver(self, mock_loader):
        """Create a VariantTemplateResolver with mock loader."""
        return VariantTemplateResolver(mock_loader)

    def test_exact_variant_match(self, resolver, mock_loader, tmp_path):
        """Should return exact variant when available."""
        from datetime import datetime

        # Mock loader to find the exact variant template
        mock_loader.find_template.return_value = (
            MagicMock(),  # Template
            TemplateSource(
                path=tmp_path / "role.modern.html.j2",
                level="role",
                discovered_at=datetime.now(),
            ),
        )

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
            context_path=tmp_path,
        )

        assert result.name == "role.modern.html.j2"
        assert result.variant == Variant.MODERN
        assert result.is_fallback is False

    def test_fallback_to_format_default(self, resolver, mock_loader, tmp_path):
        """Should fall back to format-specific default when variant not found."""
        from datetime import datetime

        # First call (variant-specific) fails, second call (default) succeeds
        mock_loader.find_template.side_effect = [
            TemplateNotFoundError("role.modern.html.j2"),
            (
                MagicMock(),
                TemplateSource(
                    path=tmp_path / "role.html.j2",
                    level="role",
                    discovered_at=datetime.now(),
                ),
            ),
        ]

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
            context_path=tmp_path,
        )

        assert result.name == "role.html.j2"
        assert result.is_fallback is True

    def test_fallback_to_explicit_default(self, resolver, mock_loader, tmp_path):
        """Should fall back to role.default.html.j2."""
        from datetime import datetime

        # First two calls fail, third succeeds
        mock_loader.find_template.side_effect = [
            TemplateNotFoundError("role.modern.html.j2"),
            TemplateNotFoundError("role.html.j2"),
            (
                MagicMock(),
                TemplateSource(
                    path=tmp_path / "role.default.html.j2",
                    level="role",
                    discovered_at=datetime.now(),
                ),
            ),
        ]

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
            context_path=tmp_path,
        )

        assert result.name == "role.default.html.j2"
        assert result.is_fallback is True

    def test_fallback_to_generic(self, resolver, mock_loader, tmp_path):
        """Should fall back to role.j2 as last resort."""
        from datetime import datetime

        # First three calls fail, fourth succeeds
        mock_loader.find_template.side_effect = [
            TemplateNotFoundError("role.modern.html.j2"),
            TemplateNotFoundError("role.html.j2"),
            TemplateNotFoundError("role.default.html.j2"),
            (
                MagicMock(),
                TemplateSource(
                    path=tmp_path / "role.j2",
                    level="role",
                    discovered_at=datetime.now(),
                ),
            ),
        ]

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
            context_path=tmp_path,
        )

        assert result.name == "role.j2"
        assert result.is_fallback is True

    def test_no_template_found_raises_error(self, resolver, mock_loader, tmp_path):
        """Should raise TemplateNotFoundError when no fallback exists."""
        mock_loader.find_template.side_effect = TemplateNotFoundError("template")

        with pytest.raises(TemplateNotFoundError):
            resolver.resolve(
                base_name="nonexistent",
                format=OutputFormat.HTML,
                variant=Variant.MODERN,
                context_path=tmp_path,
            )


class TestBuildCandidates:
    """Test candidate list building."""

    @pytest.fixture
    def resolver(self):
        """Create a resolver with mock loader."""
        loader = MagicMock(spec=CascadingTemplateLoader)
        return VariantTemplateResolver(loader)

    def test_build_candidates_order(self, resolver):
        """Candidates should be in correct fallback order."""
        candidates = resolver._build_candidates(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
        )
        assert candidates == [
            "role.modern.html.j2",
            "role.html.j2",
            "role.default.html.j2",
            "role.j2",
        ]

    def test_build_candidates_markdown(self, resolver):
        """Candidates should use markdown extension."""
        candidates = resolver._build_candidates(
            base_name="collection",
            format=OutputFormat.MARKDOWN,
            variant=Variant.MINIMAL,
        )
        assert candidates == [
            "collection.minimal.md.j2",
            "collection.md.j2",
            "collection.default.md.j2",
            "collection.j2",
        ]

    def test_build_candidates_rst(self, resolver):
        """Candidates should use rst extension."""
        candidates = resolver._build_candidates(
            base_name="project",
            format=OutputFormat.RST,
            variant=Variant.DETAILED,
        )
        assert candidates == [
            "project.detailed.rst.j2",
            "project.rst.j2",
            "project.default.rst.j2",
            "project.j2",
        ]


class TestListVariants:
    """Test listing available variants."""

    @pytest.fixture
    def mock_loader(self):
        """Create a mock CascadingTemplateLoader."""
        return MagicMock(spec=CascadingTemplateLoader)

    @pytest.fixture
    def resolver(self, mock_loader):
        """Create a VariantTemplateResolver."""
        return VariantTemplateResolver(mock_loader)

    def test_list_available_variants(self, resolver, mock_loader, tmp_path):
        """Should return list of variants that have templates."""
        from datetime import datetime

        # Only minimal and detailed have templates
        def find_template_side_effect(name, path):
            if "minimal" in name or "detailed" in name:
                return (
                    MagicMock(),
                    TemplateSource(
                        path=tmp_path / name,
                        level="embedded",
                        discovered_at=datetime.now(),
                    ),
                )
            raise TemplateNotFoundError(name)

        mock_loader.find_template.side_effect = find_template_side_effect

        variants = resolver.list_variants(
            base_name="role",
            format=OutputFormat.HTML,
            context_path=tmp_path,
        )

        assert Variant.MINIMAL in variants
        assert Variant.DETAILED in variants
        assert Variant.MODERN not in variants

    def test_list_no_variants(self, resolver, mock_loader, tmp_path):
        """Should return empty list when no variants found."""
        mock_loader.find_template.side_effect = TemplateNotFoundError("template")

        variants = resolver.list_variants(
            base_name="nonexistent",
            format=OutputFormat.HTML,
            context_path=tmp_path,
        )

        assert variants == []


class TestIntegrationWithCascadingLoader:
    """Test integration with real CascadingTemplateLoader."""

    def test_resolve_embedded_template(self, tmp_path):
        """Should resolve to embedded template."""
        loader = CascadingTemplateLoader()
        resolver = VariantTemplateResolver(loader)

        # The embedded templates use format subdirectories
        # e.g., html/role.j2
        result = resolver.resolve(
            base_name="html/role",
            format=OutputFormat.HTML,
            variant=Variant.DETAILED,
            context_path=tmp_path,
        )

        # Should fall back to html/role.j2 (the existing template)
        assert result.is_fallback is True

    def test_resolve_custom_template(self, tmp_path):
        """Should resolve custom template from role directory."""
        # Create a role with custom variant template
        role_dir = tmp_path / "my_role"
        role_dir.mkdir()
        templates_dir = role_dir / ".ansibledoctor" / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "role.modern.html.j2").write_text("<html>Modern template</html>")

        loader = CascadingTemplateLoader()
        resolver = VariantTemplateResolver(loader)

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            variant=Variant.MODERN,
            context_path=role_dir,
        )

        assert result.name == "role.modern.html.j2"
        assert result.variant == Variant.MODERN
        assert result.is_fallback is False


class TestDefaultVariantBehavior:
    """Test default variant handling."""

    @pytest.fixture
    def resolver(self):
        """Create a resolver with mock loader."""
        loader = MagicMock(spec=CascadingTemplateLoader)
        return VariantTemplateResolver(loader)

    def test_resolve_uses_default_variant(self, resolver, tmp_path):
        """resolve() should use DETAILED as default variant."""
        from datetime import datetime

        resolver._loader.find_template.return_value = (
            MagicMock(),
            TemplateSource(
                path=tmp_path / "role.detailed.html.j2",
                level="role",
                discovered_at=datetime.now(),
            ),
        )

        result = resolver.resolve(
            base_name="role",
            format=OutputFormat.HTML,
            context_path=tmp_path,
        )

        # Should have tried detailed variant first
        first_call = resolver._loader.find_template.call_args_list[0]
        assert "detailed" in first_call[0][0]
