---
description: "Task breakdown for Feature 008: Template Customization & Theming"
---

# Tasks: Template Customization & Theming (Feature 008)

**Input**: `spec.md`, `plan.md` in `specs/008-template-customization/`

## Phase 0: Research (T321-T325)

- [ ] T321 Research: Create `specs/008-template-customization/research.md` with CSS variable schema & color token map (no code changes)
- [ ] T322 Research: Investigate TemplateLoader fallback chain & caching; document API changes to `ansibledoctor/generator/template_loader.py` (no code changes)
- [ ] T323 [US28] Research: Validate Jinja2 inheritance across search paths and list edge cases for template validation (no code changes)
- [ ] T324 Research: Evaluate security & sandboxing needs for optional theme toggle JS; document recommendations
- [ ] T325 Research: UX mapping for CLI flags and precedence vs YAML config; add examples to research.md

## Phase 1: Design & Contracts (T326-T331)

- [ ] T326 Design: Create `ThemeConfig` model and YAML contract in `ansibledoctor/config/theme.py` and `specs/008-template-customization/contracts/theme_config.yaml`
- [ ] T327 Design: Draft `CascadingTemplateLoader` contract and caching rules in `specs/008-template-customization/contracts/cascading_loader.md`
- [ ] T328 Design: Draft `VariantTemplateResolver` contract and fallback chain rules in `specs/008-template-customization/contracts/variant_resolver.md`
- [ ] T329 Design: Define `CSSInjector` and `ThemeToggleGenerator` interfaces and examples in `specs/008-template-customization/contracts/css_injector.md`
- [ ] T330 Design: Define TemplateContext changes (`css_tags`, `theme_config`, `variant`, `context.breadcrumb`) and update `specs/002-doc-generator/contracts/context.md`
- [ ] T331 Deliver: Collate all contracts in `specs/008-template-customization/contracts/` for PR review

## Phase 2: Implementation (T332-T342)

- [ ] T332 [US23] Write failing unit tests in `tests/unit/test_theme_config.py` that assert YAML parsing, defaulting, and validation errors for `ThemeConfig` (TDD)
- [ ] T333 [US23] Implement `ansibledoctor/config/theme.py` (Pydantic model) and register it to runtime config loader at `ansibledoctor/config/__init__.py`
- [ ] T334 [US24] Write failing unit tests in `tests/unit/generator/test_cascading_template_loader.py` asserting search order (role/collection/project/embedded) and caching behavior
- [ ] T335 [US24] Implement `ansibledoctor/generator/cascading_loader.py` with logging for the template source and caching behavior
- [ ] T336 [US25] Write failing unit tests in `tests/unit/generator/test_variant_resolver.py` for `role.modern.*.j2` resolution and fallback chains
- [ ] T337 [US25] Implement `ansibledoctor/generator/variant_resolver.py` and integrate with `cascading_loader` to support variant-aware resolution
- [ ] T338 [US26] Write failing unit tests in `tests/unit/generator/test_css_injector.py` for external link, inline CSS, dark-mode wrapper, and tag generation (HTML only)
- [ ] T339 [US26] Implement `ansibledoctor/generator/css_injector.py` and `ansibledoctor/generator/theme_toggle.py` (JS snippet) with safe defaults and tests
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
