# Plan: Feature 005 — Internationalization (i18n) Support

**Feature Branch**: `005-i18n-support`
**Milestone**: v0.6.0
**Owner**: TBD
**Status**: Planned

This plan follows the project's constitution (TDD mandatory, SemVer, CLI coverage, and tests-first approach). We adopt an incremental, evidence-driven approach: Phase 0 (Research), Phase 1 (Design & Contracts), Phase 2 (Implementation & Tests), Phase 3 (QA & Performance), Phase 4 (Docs & Release)

---

## Quick Summary

Goal: Add multi-language documentation generation with translation YAML files, Jinja2 `t()` filter, multi-language output directories and CLI flags. Provide high-quality tests, performance limits, fallback rules, and support for custom translation files.

Deliverables:
- `LanguageConfig` (Pydantic) + config schema
- `TranslationLoader` + `TranslationProvider`
- `t()` Jinja2 filter for templates
- `MultiLanguageGenerator` orchestration
- CLI flags: `--language` / `--languages`
- Unit, integration, and E2E tests
- Updated docs, CLI examples, and demos

---

## Phase 0 - Research (Deliverable: research.md)

Goals:
- Clarify pluralization and ICU/pluralization strategy
- Choose library or implement simple pluralization logic
- Determine translation file merging precedence (embedded vs custom)
- Confirm thread-safety and multi-language generation approach (single parse + multiple render passes)
- Identify performance constraints and caching strategy

Tasks (research-first; produce `research.md`):
- R005-R1: Survey pluralization approaches and libraries (Babel, python-i18n, custom) and present pros/cons
- R005-R2: Investigate integration with Jinja2 `t()` filter and variable substitution patterns
- R005-R3: Decide file merging strategy (prefer: custom translations override embedded; project-level override collection-level override embedded)
- R005-R4: Evaluate YAML structure best practices (nested dot-notation support) and YAML validation
- R005-R5: Determine caching strategy and per-session cache TTL
- R005-R6: Benchmark generation overhead per language for typical role/collection

Acceptance: `research.md` resolves all unknowns or documents open questions marked NEEDS CLARIFICATION.

---

## Phase 1 - Design & Contracts (Deliverable: data-model.md, contracts/TranslationProvider, plan for TemplateFilter)

Goals:
- Define `LanguageConfig`, `TranslationProvider` API/contract, and Jinja2 `t()` filter signature
- Decide translation file locations, naming convention, and override precedence
- Design `MultiLanguageGenerator` orchestration and caching policy

Design tasks (test-first approach):
- D005-01: Design `LanguageConfig` model and validation; write tests verifying invalid codes rejected (mypy + pydantic). (SC-001)
- D005-02: Define `TranslationLoader` contract: load embedded + custom files and provide fallback chain (unit tests for loader). (SC-002)
- D005-03: Define `TranslationProvider` contract: `translate(key, lang, fallback=True, **kwargs) -> str` with plural & variable support and tests. (SC-003, SC-009, SC-010)
- D005-04: Define `t()` filter integration in TemplateEngine and tests for proper substitution and nested key access. (SC-003, SC-008)
- D005-05: Define how languages are enabled/disabled in CLI and config; tests for CLI behavior (SC-005).
- D005-06: Contract for `MultiLanguageGenerator` to reuse parsed role data across languages (SC-007 & TC-007)
- D005-07: Define caching interface and per-session cache testcase (TC-002)

Acceptance: `data-model.md` and interface contract files (under `specs/005-i18n-support/contracts/`) created, tests-first stubs present and failing (RED). No implementation yet.

---

## Phase 2 - Implementation & Tests

Goals:
- Implement required classes, functions and Jinja2 filter per contracts. Run TDD: write tests, implement, refactor.

Implementation steps (ordered for TDD):
- I005-T01: Unit tests for `collection_slug` and `role_slug` naming for consistency across features (collaboration with specs 004/006)
- I005-T02: Write unit tests for `LanguageConfig` parsing/validation
- I005-T03: Unit tests for `TranslationLoader` (embedded + custom files, fallback), failing
- I005-T04: Unit tests for `TranslationProvider.translate()` for simple keys, nested keys, variable substitution, plural selection
- I005-T05: Implement `TranslationLoader` and `TranslationProvider`; run tests (GREEN)
- I005-T06: Implement `t()` Jinja2 filter and register it with the TemplateEngine; add tests verifying correct translation behavior during rendering
- I005-T07: Implement `MultiLanguageGenerator`: iterate enabled languages, set language context, and write to `docs/lang/{code}/...`
- I005-T08: Add CLI flags (`--language`, `--languages`) with parsing and override behavior unit tests
- I005-T09: Integration tests: generate role docs in multiple languages, verify output structure and expected translated strings (SC-004)
- I005-T10: Integration tests: missing keys fall back to fallback language (SC-007)
- I005-T11: Performance tests for multi-language generation (SC-006) and caching (TC-002). Optimize implementation (e.g., reuse parsed data across languages)
- I005-T12: Add tests for i18n for collection and project generation integrations (collaboration with specs 004/006 and later specs). Run integration tests for at least one sample collection and project.

Paths & Modules to change:
- `ansibledoctor/config/*` - add `LanguageConfig` Pydantic model
- `ansibledoctor/translations/__init__.py` - add base translation load helper
- `ansibledoctor/translation/loader.py` - New file: `TranslationLoader`
- `ansibledoctor/translation/provider.py` - New file: `TranslationProvider` with plural/vars support
- `ansibledoctor/templates/filters.py` - Add `t()` filter code integrating provider
- `ansibledoctor/generator/multi_language.py` - New orchestrator: `MultiLanguageGenerator`
- `ansibledoctor/cli/*.py` - CLI flag changes and help text updates
- Tests in: `tests/unit/translation_*.py`, `tests/integration/i18n_*` and `tests/e2e/demo_i18n.py`

TDD Note: Implement tests in order I005-T02 -> I005-T04 (unit), then I005-T06 (render), then I005-T09 (integration).

---

## Phase 3 - QA & Performance

Goals:
- Verify performance, caching, thread-safety and resource usage
- Confirm `t()` filter thread-safety and correctness under parallel rendering
- Fix any issues found by integration or E2E tests

QA tasks:
- Q005-01: Add integration test for multi-language generation for medium-size collection (5 roles) and assert overall runtime < 30s
- Q005-02: Add concurrency tests: spawn multiple language-generation tasks in parallel to check `t()` filter thread-safety (TC-008)
- Q005-03: Memory profile run for a large dataset (100 roles) to ensure memory < 100MB for typical runs
- Q005-04: Validate logging and observability points (SC-007 warnings on missing keys)

---

## Phase 4 - Docs, Demos & Release

Goals:
- Update README, CHANGELOG, and demo files; ensure CLI help documentation updated
- Add demo workflow and E2E demo to verify output structure (collection demo and project demo) with new slugs
- Coordinate release notes and PR checklist following constitution

Release tasks:
- REL005-01: Finalize `CHANGELOG.md` [Unreleased] with summary of i18n changes and SC mapping
- REL005-02: Update `README.md` QuickStart to show `--language` usage and output structure `docs/lang/{code}/`
- REL005-03: Add demos and integration tests for `demo/` and `demo-role/` with multi-language examples
- REL005-04: Update `ROADMAP.md` (done) and reference in documentation
- REL005-05: PR with tests, CI green, CHANGELOG, and version/pyproject bump if needed

---

## Gate Criteria (Precondition to implement Phase 2)
- v0.5.0 (Collection) must be stable ✅
- TemplateEngine must support custom filters (Feature 002) ✅
- TDD test stubs written & failing for all core behaviors described above ✅

---

## Acceptance Traceability (Mapping to Spec Success Criteria)
- SC-001 LanguageConfig validation <-> D005-01 & I005-T02
- SC-002 TranslationLoader behavior <-> D005-02 & I005-T03
- SC-003 Jinja2 `t()` filter <-> D005-03 & I005-T06
- SC-004 Multi-language output <-> I005-T07 & I005-T09
- SC-005 CLI override <-> D005-05 & I005-T08
- SC-006 Performance <-> I005-T11 & Q005-01
- SC-007 Missing translation fallback & logging <-> D005-02 & I005-T10
- SC-008 Nested translation keys <-> I005-T04
- SC-009 Variable substitution <-> I005-T04
- SC-010 Plural selection <-> I005-T04
- SC-011 Embedded defaults <-> D005-02 & I005-T03
- SC-012 Custom files <-> D005-02 & I005-T03

---

## Tasks and Suggested TIDs (to put into `tasks.md`)
- T005-01: Research library for pluralization and performance (Babel recommended) (R005-R1)
- T005-02: Create `LanguageConfig` model tests & code (D005-01)
- T005-03: Create `TranslationLoader` tests for embedded+custom, fallback (D005-02)
- T005-04: Create `TranslationProvider.translate` tests (D005-03)
- T005-05: Implement `t()` filter integration tests (D005-03)
- T005-06: Implement `MultiLanguageGenerator` tests & code (I005-T07)
- T005-07: Add CLI flags tests & code (I005-T08)
- T005-08: Integration tests: verify output directories & translated strings (I005-T09)
- T005-09: Performance tests: multi-language generation times & caching viability (I005-T11)
- T005-10: Doc updates & demo tests (REL005-02/03)

---

## Risks & Mitigations
- Pluralization complexity across languages: Use a library (Babel/ICU) or minimal plural approach initially, expand later for complex languages. Document limitations.
- Performance overhead for multi-language: Implement caching and resource reuse, benchmark, and accept small overhead whilst supporting parallelization.
- Breaking changes if we alter output format: Provide compatibility option or migration guide and follow SemVer rules (major/minor bump if breaking).

---

## Timeline & Estimates
Phased estimates (approx):
- Phase 0 (Research): 1-2 days
- Phase 1 (Design & Contracts): 2-3 days
- Phase 2 (Implementation & Tests): 5-8 days
- Phase 3 (QA): 2-3 days
- Phase 4 (Docs & Release): 1-2 days

**Total Estimate**: 11-18 days (TDD lean implementation)

---

## Deliverables
- `specs/005-i18n-support/research.md`
- `specs/005-i18n-support/data-model.md` and `contracts/TranslationProvider.md`
- `specs/005-i18n-support/tasks.md` with T005-xx items
- Code: `ansibledoctor/config/language.py`, `ansibledoctor/translation/*`, `ansibledoctor/generator/multi_language.py`, CLI flags
- Tests: Unit + Integration + E2E covering SC-001..SC-012
- Updated docs and README Quick Start with examples

---

## Notes
- All tasks must follow TDD: tests created first (RED) then implementation to pass (GREEN) and refactor.
- Keep the `TranslationLoader`/`TranslationProvider` minimal & extendable; follow the constitution's DDD and library-first architecture principles.
- For complex plural rules or ICU message format, postpone full support to later versions with an explicit roadmap item.
- Coordinate with Feature 004 (Collections), Feature 006 (Project) and Feature 007 (Context) to test integration scenarios.

---

If you'd like, I can now generate `tasks.md` with T005-01..T005-10 entries and create the tests stubs (RED tests) for the first units to start TDD; say "OK — create tasks and RED tests stubs" and I'll proceed.