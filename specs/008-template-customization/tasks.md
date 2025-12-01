---
description: "Task breakdown for Feature 008: Template Customization & Theming"
---

# Tasks: Template Customization & Theming (Feature 008)

**Input**: `spec.md`, `plan.md` in `specs/008-template-customization/`

## Phase 0: Research (T321-T325)

- [x] T321 Research: Create `specs/008-template-customization/research.md` with CSS variable schema & color token map (no code changes)
    - Created research.md with `--ad-` prefixed CSS variables
    - 20+ color tokens: primary, semantic, neutral, typography, spacing, effects
    - Light/dark mode support via `[data-theme="dark"]`
- [x] T322 Research: Investigate TemplateLoader fallback chain & caching; document API changes to `ansibledoctor/generator/template_loader.py` (no code changes)
    - Documented 5-level cascading discovery: role → collection → project → user → embedded
    - Proposed `CascadingTemplateLoader` with TTL-based caching
    - Defined `TemplateDiscoveryResult` dataclass for tracking source
- [x] T323 [US28] Research: Validate Jinja2 inheritance across search paths and list edge cases for template validation (no code changes)
    - Proposed `ChoiceLoader` for multi-path resolution
    - Documented edge cases: cross-level inheritance, circular includes, missing parent
    - Defined validation requirements and logging
- [x] T324 Research: Evaluate security & sandboxing needs for optional theme toggle JS; document recommendations
    - Proposed `SandboxedEnvironment` for user templates
    - Self-contained JS toggle with localStorage persistence
    - ARIA attributes for accessibility
    - `--no-theme-toggle` flag recommendation
- [x] T325 Research: UX mapping for CLI flags and precedence vs YAML config; add examples to research.md
    - Defined 7-level precedence: CLI > Env > Role > Collection > Project > User > Default
    - Mapped 6 CLI flags: --variant, --color-scheme, --no-theme-toggle, --template-dir, --css-url, --css-inline
    - Added example .ansibledoctor.yml with theme configuration

## Phase 1: Design & Contracts (T326-T331)

- [x] T326 Design: Create `ThemeConfig` model and YAML contract in `ansibledoctor/config/theme.py` and `specs/008-template-customization/contracts/theme_config.yaml`
    - Created contracts/theme_config.yaml with Pydantic model spec
    - Defined ThemeVariant and ColorScheme enums
    - Validation rules for css_url, defaults for all fields
- [x] T327 Design: Draft `CascadingTemplateLoader` contract and caching rules in `specs/008-template-customization/contracts/cascading_loader.md`
    - 5-level discovery order: role → collection → project → user → embedded
    - TemplateSource dataclass for tracking source level
    - TTL-based caching with clear_cache() support
- [x] T328 Design: Draft `VariantTemplateResolver` contract and fallback chain rules in `specs/008-template-customization/contracts/variant_resolver.md`
    - Variant enum: minimal, detailed, modern, default
    - 4-step fallback chain for template resolution
    - ResolvedTemplate dataclass with is_fallback flag
- [x] T329 Design: Define `CSSInjector` and `ThemeToggleGenerator` interfaces and examples in `specs/008-template-customization/contracts/css_injector.md`
    - CSSInjector with base CSS variables (20+ tokens)
    - ThemeToggleGenerator with ARIA-compliant JS toggle
    - Dark mode support via data-theme attribute
- [x] T330 Design: Define TemplateContext changes (`css_tags`, `theme_config`, `variant`, `context.breadcrumb`) and update `specs/008-template-customization/contracts/template_context.md`
    - New fields: theme_config, variant, css_tags, toggle_*
    - Factory method with_theme() for theme-aware context
    - Backward-compatible with existing templates
- [x] T331 Deliver: Collate all contracts in `specs/008-template-customization/contracts/` for PR review
    - theme_config.yaml: ThemeConfig model
    - cascading_loader.md: CascadingTemplateLoader
    - variant_resolver.md: VariantTemplateResolver
    - css_injector.md: CSSInjector + ThemeToggleGenerator
    - template_context.md: TemplateContext extensions

## Phase 2: Implementation (T332-T342)

- [x] T332 [US23] Write failing unit tests in `tests/unit/test_theme_config.py` that assert YAML parsing, defaulting, and validation errors for `ThemeConfig` (TDD)
    - 40 unit tests covering enums, defaults, parsing, validation, immutability, serialization
    - Tests for ThemeVariant (minimal, detailed, modern) and ColorScheme (light, dark, auto)
    - Validation tests for css_url absolute path requirement
- [x] T333 [US23] Implement `ansibledoctor/config/theme.py` (Pydantic model) and register it to runtime config loader at `ansibledoctor/config/__init__.py`
    - ThemeConfig with name, variant, color_scheme, enable_toggle, css_url, css_inline
    - ThemeVariant and ColorScheme enums
    - Frozen model with css_url validator
    - Integrated into ConfigModel and exported from __init__.py
- [x] T334 [US24] Write failing unit tests in `tests/unit/generator/test_cascading_template_loader.py` asserting search order (role/collection/project/embedded) and caching behavior
    - 29 unit tests covering TemplateSource, loader init, discovery order, caching, environment, errors
    - Tests for 5-level discovery: role → collection → project → user → embedded
    - Cache TTL expiry and clear_cache() tests
- [x] T335 [US24] Implement `ansibledoctor/generator/cascading_loader.py` with logging for the template source and caching behavior
    - CascadingTemplateLoader with 5-level discovery
    - TemplateSource dataclass for tracking source level
    - TTL-based caching with clear_cache()
    - Project root detection via ansible.cfg, pyproject.toml, .git
    - Jinja2 ChoiceLoader with embedded fallback
- [x] T336 [US25] Write failing unit tests in `tests/unit/generator/test_variant_resolver.py` for `role.modern.*.j2` resolution and fallback chains
    - 24 unit tests covering Variant enum, ResolvedTemplate, resolution chain, fallback behavior
    - Tests for 4-step fallback: variant → format → default → generic
    - Integration tests with CascadingTemplateLoader
- [x] T337 [US25] Implement `ansibledoctor/generator/variant_resolver.py` and integrate with `cascading_loader` to support variant-aware resolution
    - Variant enum (minimal, detailed, modern, default)
    - ResolvedTemplate dataclass with candidates property
    - 4-step fallback chain resolution
    - list_variants() for discovering available variants
- [x] T338 [US26] Write failing unit tests in `tests/unit/generator/test_css_injector.py` for external link, inline CSS, dark-mode wrapper, and tag generation (HTML only)
    - 33 unit tests covering CSSTag, CSSInjector, ThemeToggleGenerator
    - Tag rendering (link/style), base CSS variables, dark mode support
    - Theme toggle JS with localStorage, ARIA attributes
- [x] T339 [US26] Implement `ansibledoctor/generator/css_injector.py` and `ansibledoctor/generator/theme_toggle.py` (JS snippet) with safe defaults and tests
    - CSSTag dataclass with to_html() method
    - CSSInjector with BASE_CSS containing CSS variables and dark mode
    - ThemeToggleGenerator with ARIA-accessible toggle button
    - Auto dark mode via prefers-color-scheme media query
- [ ] T340 [P] Add `css_tags`/`theme_config` to `ansibledoctor/generator/context.py` or `ansibledoctor/generator/models.py` (RenderResult) and update `ansibledoctor/generator/renderers/html.py` to include `css_tags`
- [ ] T341 [US23] Write failing unit tests in `tests/unit/test_cli_flags.py` validating CLI precedence over YAML for `--variant`, `--color-scheme`, `--no-theme-toggle`, `--template-dir`
- [ ] T342 [US23] Implement CLI flags in `ansibledoctor/cli/generate.py` and update `tests/unit/test_cli_generate.py` (TDD)

## Phase 3: Integration & multi-language support (T343-T349)

- [ ] T343 [US25] Integration: End-to-end `tests/integration/test_theme_variants.py` that renders minimal/detailed/modern variants for roles and collections and validates structure and content
- [ ] T344 [P] [US23] Integration: End-to-end `tests/integration/test_i18n_theme_integration.py` validating `t()` translation keys for theme labels and translations for multilingual outputs
- [ ] T345 [US24] Integration: `tests/integration/test_template_source_logging.py` verifying custom templates at role/collection/project are used and template source is logged
- [ ] T346 [US26] Integration: `tests/integration/test_css_injection.py` verifying CSS injection & optional toggle JS in HTML and ensuring CSS is ignored for Markdown/RST outputs
- [ ] T347 [P] Performance: `tests/perf/test_theme_perf.py` benchmark verifying template discovery and CSS injection overhead < 50ms for a typical role
- [ ] T348 [P] Security: Update `ansibledoctor/generator/template_validator.py` and add tests `tests/unit/test_template_sandboxing.py` to ensure safe Jinja2 options and prevent code execution from templates
- [ ] T349 [US27] Accessibility: `tests/integration/test_theme_accessibility.py` ensuring ARIA attributes in toggle controls and valid HTML structure

## Phase 4: Demos & Documentation (T350-T354)

- [ ] T350 [P] [US25] Create demo templates under `demo/` for minimal/detailed/modern variants (`demo/role.*.html.j2`) and sample CSS inline/URL usage
- [ ] T351 [P] Update `README.md` QuickStart and `docs/TEMPLATE_GUIDE.md` with theme examples, flags, and override behavior
- [ ] T352 [P] Add `specs/008-template-customization/MIGRATION.md` (optional) if we need to change template search paths or config keys
- [ ] T353 [P] Add example configs & theme css examples to `demo/` for selenium/manual testing
- [ ] T354 [P] Add e2e demo tests `tests/e2e/test_demo_themes.py` validating demo outputs and theme toggle

## Phase 5: Polish & Release (T355-T360)

- [ ] T355 [P] Cross-platform tests: Run full pipeline & template discovery on Windows (PowerShell) and Linux/macOS to validate path handling and template resolution
- [ ] T356 [US28] Improve TemplateValidator to provide actionable errors about missing parents or invalid inheritance in `ansibledoctor/generator/template_validator.py`
- [ ] T357 [P] Prepare `CHANGELOG.md` and `docs/RELEASE_NOTES.md` entries for v0.8.0; add PR checklist to `specs/008-template-customization/checklists/`
- [ ] T358 Run full test suite (`pytest tests/ --cov=ansibledoctor`) and fix issues; ensure performance & accessibility tests pass
- [ ] T359 Tag v0.8.0 and prepare release PR with tests green, docs updated, and migration notes
- [ ] T360 Post-release: Compile deferred v0.9.0 enhancements in `specs/008-template-customization/post_release.md`

## Acceptance Criteria & Traceability

- Each user story (US23..US28) is covered by the above tasks and has independent tests (unit → integration → e2e)
- Verify that built-in variants (minimal/detailed/modern) and CSS injection cases appear in `tests/integration/` and demo outputs
- Ensure CLI behavior matches the contract and tests for precedence (YAML < env < CLI)

---

## Side work: 2025-11-30 (Template & i18n integration)

- [x] T361 [P] Registered Jinja2 `t()` translation filter and updated template examples to demonstrate use of translation keys inside templates
- [x] T362 [P] Ensured theme and variant templates support `t()` translation usage and per-locale generation via `MultiLanguageGenerator`
- [x] T363 [P] Verified template validation and pre-commit linting get detected by CI (pre-commit hooks run)


---

<!-- Side work entries moved to the end of the file and renumbered as T361-T363. -->


***
