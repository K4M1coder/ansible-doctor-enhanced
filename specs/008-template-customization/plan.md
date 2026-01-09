---
description: "Implementation plan for Feature 008 - Advanced Template Customization & Theming"
---

# Plan: Feature 008 — Advanced Template Customization & Theming

This plan breaks Feature 008 into research, design, implementation, integration, docs/demo, and release phases — aligned to the repository's TDD-first workflow and Constitution.

## Scope & Goals

- Implement theme configuration parsing (`ThemeConfig`) and CLI overrides
- Implement cascading template discovery & variant resolution (role → collection → project → embedded)
- Add CSS injection for HTML generation, optional theme toggle (JS), and CSS-only dark/light modes
- Provide built-in variants (minimal, detailed, modern) per format
- Ensure Jinja2 inheritance works for custom templates and log the template source for debugging
- Ensure the system remains backward compatible and test-first for all tasks

## Unknowns / Needs Clarification (NEEDS CLARIFICATION)

- Use a formal Color Token set vs ad-hoc CSS variables? (Rationale: consistency across themes)
- Security policy for embedded JS: are script tags allowed in generated documentation? (per constitution/network concerns)
- Do we need to provide a theme packaging format (out-of-scope for v0.8.0)?
- Maximum template inheritance depth (TC-009 suggested 5) — confirm agreed limit

## Dependencies

- Must: Feature 002 (Template System), Feature 005 (i18n) (recommended), Feature 006 (Project generation) for project-level templates
- Optional: Feature 007 (Hierarchical context) to render breadcrumbs & context-aware navigation

## Plan Phases

### Phase 0: Research & Decision (T321-T325) — 3–5 days

- [ ] T321 Research: CSS variable schema (common token names) and design trade-offs; produce research.md with chosen names and rationale
- [ ] T322 Research: Template discovery & TemplateLoader behavior (fallback, caching); confirm necessary API changes to `ansibledoctor/generator/template_loader.py`
- [ ] T323 Research: Jinja2 inheritance patterns & any limitations when resolving templates from multiple directories (role/collection/project)
- [ ] T324 Research: Security & sandboxing for JS injection (Theme toggle) — propose optional JS injection approach vs no-JS fallback
- [ ] T325 Research & UX: CLI flags mapping (`--variant`, `--color-scheme`, `--no-theme-toggle`, `--template-dir`) and precedence over YAML config

### Phase 1: Design & Contracts (T326-T331) — 2–4 days

- [ ] T326 Design: Create `ThemeConfig` model in `ansibledoctor/config/theme.py` (Pydantic) and YAML-to-model mapping; specify validation: name ∈ {minimal, detailed, modern}, variant fallback rules
- [ ] T327 Design: `CascadingTemplateLoader` interface & expected fallback chain; plan caching behavior and logging (source resolution message)
- [ ] T328 Design: `VariantTemplateResolver` API; provide fallback chain builder & resolver for variant-to-template-name mapping
- [ ] T329 Design: `CSSInjector` API and `ThemeToggleGenerator` (JS skeleton) interfaces; define tag content and order (external link first, then inline style, then toggle JS if enabled)
- [ ] T330 Design: TemplateContext changes to include `css_tags`, `theme_config`, `variant`, and `context.breadcrumb` entry for hierarchical context
- [ ] T331 Deliver: Contracts & API changes as a small `contracts/` (or add to existing `/specs/002-doc-generator/contracts`) with function signatures & example YAML snippets

### Phase 2: Implementation (T332-T342) — 5–10 days

Follow TDD: write failing tests first, then implement minimal code to pass tests, then refactor.  

- [ ] T332 Unit test: `ThemeConfig` model loads from YAML and verifies defaults (e.g., `detailed` default); tests for invalid values (e.g., unsupported variant) in `tests/unit/test_theme_config.py`
- [ ] T333 Implement: `ansibledoctor/config/theme.py` with `ThemeConfig` Pydantic model and registration in the CLI config loader
- [ ] T334 Unit test: `CascadingTemplateLoader` search order & behavior; tests for role/collection/project/embedded precedence and cached discovery in `tests/unit/generator/test_cascading_template_loader.py`
- [ ] T335 Implement: `ansibledoctor/generator/cascading_loader.py` with logging about template source
- [ ] T336 Unit test: `VariantTemplateResolver` resolving `role.modern.html.j2` etc. and fallback chains in `tests/unit/generator/test_variant_resolver.py`
- [ ] T337 Implement: `ansibledoctor/generator/variant_resolver.py` and integrate with `CascadingTemplateLoader` so that resolution tries `role.<variant>.<fmt>.j2`, `role.<fmt>.j2`, `role.default.<fmt>.j2`
- [ ] T338 Unit test: CSS injection building correct `<link>` and `<style>` tags and dark-mode wrapper behavior in `tests/unit/generator/test_css_injector.py`
- [ ] T339 Implement: `ansibledoctor/generator/css_injector.py` and `ThemeToggleGenerator` with optional JS snippet; add non-JS fallback tests
- [ ] T340 Update: Register `css_tags` in `TemplateContext` or in the RenderResult; update renderers for HTML to pick up `css_tags` and `theme_config` during rendering
- [ ] T341 Unit test: CLI flags precedence & config override: ensure CLI flags override YAML, and environment variable if present, tests in `tests/unit/test_cli_flags.py`
- [ ] T342 Implement: CLI Flags in `ansibledoctor/cli/generate.py` (`--variant`, `--color-scheme`, `--no-theme-toggle`, `--template-dir`), update help text and tests in `tests/unit/test_cli_generate.py`

### Phase 3: Integration & multi-language support (T343-T349) — 3–5 days

- [ ] T343 Integration test: Generate HTML/Markdown outputs for `minimal/detailed/modern` variants and verify file structures & variant templates were applied `tests/integration/test_theme_variants.py`
- [ ] T344 Integration test: Verify i18n integration: `t('theme.name')` keys & localized variant labels; test fallback behavior when translation missing `tests/integration/test_i18n_theme_integration.py`
- [ ] T345 Integration test: Verify custom theme directories at role/collection/project levels are discovered and that the template source log contains the correct source entries
- [ ] T346 Integration test: Verify CSS injection and toggle JS presence in HTML output and that Markdown/RST outputs ignore CSS injection
- [ ] T347 Performance test: Template discovery & CSS injection < 50ms additional overhead on generation; benchmarks in `tests/perf/test_theme_perf.py`
- [ ] T348 Security test: Ensure nested templates or template override doesn't permit arbitrary code execution (secure Jinja2 options & sandboxing where necessary)
- [ ] T349 Accessibility checks: Add basic ARIA attributes to theme toggle & run basic HTML validator script in `tests/integration/test_theme_accessibility.py`

### Phase 4: Demonstrations & Documentation (T350-T354) — 2–3 days

- [ ] T350 Create demo templates for each built-in variant under `demo/` and `demo-role/` with both HTML and Markdown outputs; add sample CSS inline and external link usage
- [ ] T351 Update README.md (QuickStart & CLI flags) and `TEMPLATE_GUIDE.md` to document theme config, CLI flags, and template override flow
- [ ] T352 Write a migration guide (if required) to indicate how to move to `template_dirs` or theme config; add `--legacy-output` notes if necessary
- [ ] T353 Add user-facing docs in `docs/FEATURE_008_TEMPLATE_CUSTOMIZATION.md` showing sample `.ansibledoctor.yml` and examples for overrides & variants
- [ ] T354 Add demo tests that verify the demo outputs & theme toggle (e2e)

### Phase 5: Polish, QA & Release (T355-T360) — 2–4 days

- [ ] T355 Cross-platform tests: Windows/PowerShell, Linux Bash, macOS shell (verify path handling & template detection)
- [ ] T356 Fix and improve template validation errors & descriptive messages when template loading fails or inheritance unresolved
- [ ] T357 Prepare change log entry, release notes, and PR checklist (TDD validated, tests green, docs updated) — add to CHANGELOG.md
- [ ] T358 Final QA: Ensure all tests pass and performance goals met; update ROADMAP.md & release milestone (v0.8.0)
- [ ] T359 Tag v0.8.0 release branch with required PR checklist and release notes
- [ ] T360 Optional follow-ups: theme marketplace, theme packaging, advanced JS-based themes (deferred to v0.9+)

## Success/Exit Criteria

- All units & integration tests for Phase 2 and 3 pass
- Built-in variant templates for HTML render correctly and match acceptance scenarios
- CLI flags work & override config as expected
- Template discovery logs a source for each template rendered (role/collection/project/embedded)
- CSS injection works only for HTML generation; Markdown/RST remain unchanged
- Performance overhead is reasonable and caching works
- Accessibility checks for HTML theme toggle pass basic ARIA rules

## Non-Goals & Out-of-Scope (for v0.8.0)

- JavaScript-based theme systems that require a client-side bundler or build (webpack, rollup)
- Package distribution / marketplace for themes
- Complex user interface for theme management (no web UI) — CLI only

## Deliverables

- `specs/008-template-customization/plan.md` (this file)
- `specs/008-template-customization/tasks.md` (task list generated from TIDs in this plan) — TODO
- `ansibledoctor/config/theme.py` (ThemeConfig model) & tests
- `ansibledoctor/generator/cascading_loader.py` & `ansibledoctor/generator/variant_resolver.py` & `ansibledoctor/generator/css_injector.py` & `ansibledoctor/generator/theme_toggle.py` & tests
- CLI flags & examples in docs and README
- Demo templates & demo output artifacts

## Suggested Implementation Order

1. Research decisions (colors, CSS variables, JS allowed) and confirm with the team (T321–T325)
2. Implement ThemeConfig & unit tests (T332–T333)
3. Implement CascadingTemplateLoader & variant resolver (T334–T337)
4. Implement CSS injection and theme toggle generation (T338–T339)
5. Integrate with generator and CLI (T340–T342)
6. Add integration tests & performance tests (T343–T347)
7. Demos, docs, and release tasks (T350–T360)

## Risk Assessment & Mitigation
