"""Performance tests for template discovery and CSS injection.

T347: Verify theme-related operations complete within acceptable time bounds.
Target: < 50ms overhead for CSS injection and template discovery.
"""

import time
from pathlib import Path

import pytest

from ansibledoctor.config.theme import ColorScheme, ThemeConfig, ThemeVariant
from ansibledoctor.generator.cascading_loader import CascadingTemplateLoader
from ansibledoctor.generator.css_injector import CSSInjector, ThemeToggleGenerator
from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.models.metadata import RoleMetadata
from ansibledoctor.models.role import AnsibleRole


class TestCSSInjectorPerformance:
    """Performance tests for CSS injection operations."""

    @pytest.fixture
    def css_injector(self) -> CSSInjector:
        """Create CSS injector instance."""
        return CSSInjector()

    def test_css_tag_generation_under_10ms(self, css_injector: CSSInjector):
        """CSS tag generation should complete in under 10ms."""
        # Warm up
        css_injector.generate_tags(include_base=True)

        # Measure
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            css_injector.generate_tags(include_base=True)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 10, f"CSS tag generation took {avg_ms:.2f}ms on average (target: <10ms)"

    def test_css_tag_to_html_under_1ms(self, css_injector: CSSInjector):
        """Converting CSS tags to HTML should be very fast."""
        tags = css_injector.generate_tags(include_base=True)

        # Measure
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            for tag in tags:
                tag.to_html()
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 1, f"CSS tag to_html took {avg_ms:.3f}ms on average (target: <1ms)"

    def test_all_css_options_under_50ms(self, css_injector: CSSInjector):
        """Generating CSS with all options should complete in under 50ms total."""
        scenarios = [
            {"include_base": True},
            {"include_base": True, "css_url": "https://example.com/theme.css"},
            {"include_base": True, "css_inline": ".custom { color: red; }"},
            {"include_base": False, "css_inline": ".custom-only { color: blue; }"},
        ]

        # Warm up
        for scenario in scenarios:
            css_injector.generate_tags(**scenario)

        # Measure all scenarios
        start = time.perf_counter()
        for _ in range(10):
            for scenario in scenarios:
                tags = css_injector.generate_tags(**scenario)
                for tag in tags:
                    tag.to_html()
        elapsed = time.perf_counter() - start

        elapsed_ms = elapsed * 1000
        assert elapsed_ms < 50, f"All CSS scenarios took {elapsed_ms:.2f}ms (target: <50ms)"


class TestThemeTogglePerformance:
    """Performance tests for theme toggle generation."""

    @pytest.fixture
    def toggle_generator(self) -> ThemeToggleGenerator:
        """Create theme toggle generator."""
        return ThemeToggleGenerator()

    def test_toggle_generation_under_5ms(self, toggle_generator: ThemeToggleGenerator):
        """Theme toggle generation should complete in under 5ms."""
        # Warm up
        toggle_generator.generate_toggle(enabled=True)

        # Measure
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            toggle_generator.generate_toggle(enabled=True)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 5, f"Toggle generation took {avg_ms:.2f}ms on average (target: <5ms)"

    def test_toggle_disabled_is_instant(self, toggle_generator: ThemeToggleGenerator):
        """When toggle is disabled, generation should be nearly instant."""
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            toggle_generator.generate_toggle(enabled=False)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 0.5, f"Disabled toggle took {avg_ms:.3f}ms on average (target: <0.5ms)"


class TestTemplateDiscoveryPerformance:
    """Performance tests for template discovery with cascading loader."""

    @pytest.fixture
    def role_template_structure(self, tmp_path: Path) -> Path:
        """Create a role with template override structure."""
        role_path = tmp_path / "perf_role"
        role_path.mkdir()
        (role_path / "tasks").mkdir()
        (role_path / "tasks" / "main.yml").write_text("- name: test\n  debug: msg=test\n")

        # Create role-level template override (correct naming)
        templates_dir = role_path / ".ansibledoctor" / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "role.html.j2").write_text(
            """<!DOCTYPE html>
<html><head><title>{{ role_name }}</title></head>
<body><h1>{{ role_name }}</h1></body></html>
"""
        )

        return role_path

    def test_loader_initialization_under_10ms(self):
        """CascadingTemplateLoader initialization should be fast."""
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            CascadingTemplateLoader()
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 10, f"Loader init took {avg_ms:.2f}ms on average (target: <10ms)"

    def test_template_discovery_under_20ms(self, role_template_structure: Path):
        """Template discovery should complete in under 20ms."""
        loader = CascadingTemplateLoader()

        # Warm up (fills cache)
        loader.find_template("role.html.j2", role_template_structure)

        # Clear cache and measure fresh discovery
        loader.clear_cache()

        iterations = 20
        start = time.perf_counter()
        for _ in range(iterations):
            loader.clear_cache()
            loader.find_template("role.html.j2", role_template_structure)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 20, f"Template discovery took {avg_ms:.2f}ms on average (target: <20ms)"

    def test_cached_discovery_under_1ms(self, role_template_structure: Path):
        """Cached template discovery should be very fast."""
        loader = CascadingTemplateLoader()

        # Populate cache
        loader.find_template("role.html.j2", role_template_structure)

        # Measure cached access
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            loader.find_template("role.html.j2", role_template_structure)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 1, f"Cached discovery took {avg_ms:.3f}ms on average (target: <1ms)"


class TestTemplateContextPerformance:
    """Performance tests for TemplateContext with theme configuration."""

    @pytest.fixture
    def sample_role(self, tmp_path: Path) -> AnsibleRole:
        """Create sample role for testing."""
        role_path = tmp_path / "perf_ctx_role"
        role_path.mkdir()
        (role_path / "tasks").mkdir()
        (role_path / "tasks" / "main.yml").write_text("- name: ctx\n  debug: msg=ctx\n")

        return AnsibleRole(
            path=role_path,
            name="perf_ctx_role",
            metadata=RoleMetadata(),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_context_creation_with_theme_under_20ms(self, sample_role: AnsibleRole):
        """TemplateContext creation with theme should be under 20ms."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        # Warm up
        TemplateContext(
            role=sample_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # Measure
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            TemplateContext(
                role=sample_role,
                output_format=OutputFormat.HTML,
                generator_version="0.5.0",
                theme_config=theme_config,
            )
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 20, f"Context creation took {avg_ms:.2f}ms on average (target: <20ms)"

    def test_context_to_dict_with_css_under_5ms(self, sample_role: AnsibleRole):
        """Converting context to dict (including CSS tags) should be under 5ms."""
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

        # Warm up
        context.to_dict()

        # Measure
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            context.to_dict()
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / iterations) * 1000
        assert avg_ms < 5, f"Context to_dict took {avg_ms:.2f}ms on average (target: <5ms)"

    def test_context_without_theme_is_faster(self, sample_role: AnsibleRole):
        """Context without theme should be faster than with theme."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        iterations = 100

        # Measure with theme
        start = time.perf_counter()
        for _ in range(iterations):
            ctx = TemplateContext(
                role=sample_role,
                output_format=OutputFormat.HTML,
                generator_version="0.5.0",
                theme_config=theme_config,
            )
            ctx.to_dict()
        with_theme_elapsed = time.perf_counter() - start

        # Measure without theme
        start = time.perf_counter()
        for _ in range(iterations):
            ctx = TemplateContext(
                role=sample_role,
                output_format=OutputFormat.HTML,
                generator_version="0.5.0",
            )
            ctx.to_dict()
        without_theme_elapsed = time.perf_counter() - start

        # Without theme should be faster (or at least not significantly slower)
        ratio = with_theme_elapsed / without_theme_elapsed
        # Allow theme context to be up to 3x slower (reasonable overhead)
        assert ratio < 3.0, f"Theme context is {ratio:.1f}x slower than no theme (target: <3x)"


class TestEndToEndThemePerformance:
    """End-to-end performance tests for theme operations."""

    @pytest.fixture
    def typical_role(self, tmp_path: Path) -> AnsibleRole:
        """Create a typical role with common structure."""
        role_path = tmp_path / "typical_role"
        role_path.mkdir()

        # Tasks
        (role_path / "tasks").mkdir()
        (role_path / "tasks" / "main.yml").write_text(
            """
- name: Install packages
  package:
    name: "{{ item }}"
    state: present
  loop: "{{ packages }}"
"""
        )

        # Defaults
        (role_path / "defaults").mkdir()
        (role_path / "defaults" / "main.yml").write_text(
            """
packages:
  - nginx
  - python3
"""
        )

        return AnsibleRole(
            path=role_path,
            name="typical_role",
            metadata=RoleMetadata(
                author="Test Author",
                description="A typical Ansible role for testing",
            ),
            variables=[],
            tags=[],
            todos=[],
            examples=[],
        )

    def test_full_theme_pipeline_under_50ms(self, typical_role: AnsibleRole):
        """Complete theme pipeline should be under 50ms for a typical role."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.MODERN,
            color_scheme=ColorScheme.AUTO,
            enable_toggle=True,
        )

        # Measure complete pipeline
        start = time.perf_counter()

        # 1. Create context with theme
        context = TemplateContext(
            role=typical_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )

        # 2. Get CSS tags
        css_tags = context.css_tags

        # 3. Get toggle HTML/JS
        toggle_html = context.theme_toggle_html
        toggle_js = context.theme_toggle_js

        # 4. Convert to dict for template
        ctx_dict = context.to_dict()

        elapsed = time.perf_counter() - start
        elapsed_ms = elapsed * 1000

        assert elapsed_ms < 50, f"Full theme pipeline took {elapsed_ms:.2f}ms (target: <50ms)"

        # Verify outputs exist
        assert len(css_tags) >= 1
        assert toggle_html is not None
        assert toggle_js is not None
        assert "css_tags" in ctx_dict

    def test_repeated_renders_with_caching(self, typical_role: AnsibleRole):
        """Repeated renders should maintain performance."""
        theme_config = ThemeConfig(
            variant=ThemeVariant.DETAILED,
            color_scheme=ColorScheme.DARK,
            enable_toggle=True,
        )

        # First render (cold)
        start = time.perf_counter()
        context = TemplateContext(
            role=typical_role,
            output_format=OutputFormat.HTML,
            generator_version="0.5.0",
            theme_config=theme_config,
        )
        context.to_dict()
        time.perf_counter() - start

        # Subsequent renders
        start = time.perf_counter()
        for _ in range(10):
            context = TemplateContext(
                role=typical_role,
                output_format=OutputFormat.HTML,
                generator_version="0.5.0",
                theme_config=theme_config,
            )
            context.to_dict()
        subsequent_elapsed = time.perf_counter() - start

        # Each subsequent should be reasonably fast
        avg_subsequent_ms = (subsequent_elapsed / 10) * 1000
        assert (
            avg_subsequent_ms < 50
        ), f"Subsequent renders took {avg_subsequent_ms:.2f}ms on average (target: <50ms)"


class TestCSSTagMemoryEfficiency:
    """Tests for memory efficiency of CSS operations."""

    def test_css_tag_size_is_reasonable(self):
        """CSS tags should not be excessively large."""
        injector = CSSInjector()
        tags = injector.generate_tags(include_base=True)

        # Calculate total size
        total_size = sum(len(tag.content) for tag in tags)

        # CSS should be under 20KB (reasonable for base + dark mode)
        assert total_size < 20 * 1024, f"CSS tags total {total_size} bytes (target: <20KB)"

    def test_toggle_script_size_is_minimal(self):
        """Theme toggle JS should be minimal."""
        generator = ThemeToggleGenerator()
        result = generator.generate_toggle(enabled=True)

        # Toggle JS should be under 2KB
        assert (
            len(result.script_js) < 2 * 1024
        ), f"Toggle JS is {len(result.script_js)} bytes (target: <2KB)"

        # Button HTML should be under 500 bytes
        assert (
            len(result.button_html) < 500
        ), f"Toggle HTML is {len(result.button_html)} bytes (target: <500 bytes)"
