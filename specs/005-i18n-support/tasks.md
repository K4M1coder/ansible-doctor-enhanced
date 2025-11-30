# Tasks: Feature 005 — Internationalization (i18n) Support

- [x] T005-01 [US11] Create `LanguageConfig` Pydantic model and unit tests in `ansibledoctor/config/language.py` and `tests/unit/test_language_config.py` to validate schema (default, enabled, fallback, detect_system) and ISO 639-1 enforcement.  ✅ Implemented

- [x] T005-02 [US11] Implement CLI flags `--language` and `--languages`, update CLI help text, and write unit tests in `ansibledoctor/cli/generate.py` and `tests/unit/test_cli_languages.py` ensuring precedence over config file and argument parsing.  ✅ Implemented

- [x] T005-03 [US12] Create failing unit tests for `TranslationLoader` in `tests/unit/test_translation_loader.py` asserting loading of embedded translations and custom `./.ansibledoctor/translations/{lang}.yml` file override rules, and file discovery paths.  ✅ Implemented

- [x] T005-04 [US12] Implement `TranslationLoader` in `ansibledoctor/translation/loader.py` to load embedded package translations and project-local overrides; add unit coverage for YAML load correctness and file precedence.  ✅ Implemented

- [x] T005-05 [US12] Create failing unit tests for `TranslationProvider` in `tests/unit/test_translation_provider.py` covering basic key lookups, nested keys, variable substitution, and plural selection with `one`/`other` keys.  ✅ Implemented

- [x] T005-06 [US12] Implement `TranslationProvider` in `ansibledoctor/translation/provider.py`, add pluralization selection logic (Babel recommended) or minimal fallback rules; tests should pass after implementation.  ✅ Implemented (initial minimal plural rules).

- [x] T005-07 [US12] Create failing unit tests for the Jinja2 `t()` filter in `tests/unit/test_template_filters.py`. Verify translation calls: `t('section.key')`, `t('section.count', count=3)` return appropriate strings and handle missing keys.  ✅ Implemented

- [x] T005-08 [US12] Implement `t()` filter registration in `ansibledoctor/templates/filters.py` and integrate into TemplateEngine; tests for context-aware language switching must pass (`tests/unit/test_template_filters.py`).  ✅ Implemented

- [x] T005-09 [US13] Create failing integration tests for `MultiLanguageGenerator` (`tests/integration/test_multilang_generator.py`) asserting that parsing is done once and templates are rendered for multiple languages writing files under `docs/lang/{code}/...`.  ✅ Unit tests and E2E added and passing

- [x] T005-10 [US13] Implement `MultiLanguageGenerator` in `ansibledoctor/generator/multi_language.py` to reuse parsed role data, set language context per render, and write language-specific outputs.  ✅ Implemented

- [x] T005-11 [P] [US13] Add E2E tests for generating a sample role and collection in 3 languages (English, French, German) under `tests/e2e/demo_i18n.py` verifying the `docs/lang/en|fr|de/...` file trees and translated content.  ✅ Implemented (e2e test added and passing)

- [x] T005-12 [US12] Implement unit and integration tests for translation fallback behavior (missing keys fallback to configured fallback language) in `tests/integration/test_i18n_fallback.py` and implement logging warning behavior.  ✅ Implemented (logging via structlog; provider tracks missing keys)

- [x] T005-13 [US12] Implement caching per-generation-session for `TranslationLoader`/`TranslationProvider` with unit tests verifying that repeated lookups are served from cache and the cache is cleared per session (`tests/unit/test_translation_cache.py`).  ✅ Implemented

- [x] T005-14 [P] Add concurrency/thread-safety tests for `t()` filter and provider in `tests/integration/test_i18n_concurrency.py` to ensure safe behavior under multi-threaded rendering (TC-008). ✅ Implemented

- [x] T005-15 [P] Add performance tests and benchmarks in `tests/perf/test_multilang_perf.py` validating SC-006 (multi-language overhead <5s for typical role) and caching impact.  ✅ Implemented

- [x] T005-16 [US11] Add unit tests for system locale detection (`languages.detect_system`) using `locale` module and CLI flag override semantics in `tests/unit/test_locale_detection.py`. ✅ Implemented

- [x] T005-17 [US12] Add unit tests for pluralization behavior in `tests/unit/test_pluralization.py` for English (one/other) and do minimal support for languages without plural rules. ✅ Implemented

- [x] T005-18 [US12] Implement test fixtures and sample translation YAMLs under `specs/005-i18n-support/fixtures/` for EN/FR/DE to be used by the tests; add embedded defaults in `ansibledoctor/translations/`.  ✅ Implemented (added de.yml and fixtures)

- [ ] T005-19 [P] Documentation tasks: Update `README.md` QuickStart, `specs/005-i18n-support/spec.md` usage examples, CLI help, and `CHANGELOG.md` in `docs` and `README-generated.md`. (Files: `README.md`, `specs/005-i18n-support/spec.md`, `CHANGELOG.md`)

- [ ] T005-20 [P] Add demo updates: Update `demo/` and `demo-role/` outputs to include language-specific directories and examples. Update templates and sample custom translations in `demo/` files.

- [x] T005-21 [US13] Add integration test verifying custom translation file in `project/.ansibledoctor/translations/fr.yml` overrides embedded translations and overrides collection-level translations if present. ✅ Implemented (unit tests cover project-level overrides and deep merge behavior)

- [x] T005-22 [US11] Add tests and logic for invalid language codes handling in `tests/unit/test_language_codes.py` (skip vs error rule) and implement appropriate logging & error handling. ✅ Implemented (loader falls back to 'en' and warns)

- [x] T005-23 [US12] Security & validation: Add unit tests for YAML parsing safety and substitution injection patterns (`tests/unit/test_translation_security.py`) and implement safe string formatting (no code execution). ✅ Implemented

- [ ] T005-24 [P] Release tasks: Update Roadmap/Version: Bump feature milestone references, prepare CHANGELOG entry in `CHANGELOG.md`, and create PR checklist ensuring TDD, tests passing, documentation updated, and SemVer considerations handled (breaking change or not documented).

---

<!-- Side work items moved to a final 'tasks' block and renumbered to continue the T005-XX sequence (T005-25+). -->
---

## Side work: 2025-11-30 (Implementation housekeeping & repo operations)

- [x] T005-25 [P] Rebased `005-i18n-support` on `dev` and resolved conflicts; pushed updated branch
- [x] T005-26 [P] Merged `005-i18n-support` into `007-project-navigation` to test integration with navigation features and resolved conflicts
- [x] T005-27 [P] Added `scripts/run_cli_main.py`, `scripts/run_cli.*`, `scripts/run_tests.*` and `ansibledoctor/cli/__main__.py` to improve run-from-source experience and ensure `ansible-doctor-enhanced` script runs via console script
- [x] T005-28 [P] Removed generated artifacts `README-generated.md` and `test-output.json` from repository
- [x] T005-29 [P] Added `pr_body.md` and `scripts/create_pr.py` to assist in PR creation and standardized PR description for Feature 005
- [x] T005-30 [P] Updated `README.md` and `CONTRIBUTING.md` to recommend `poetry install --with dev` and documented pre-commit & run-from-source steps
- [x] T005-31 [P] Confirmed targeted i18n tests (`test_pluralization.py`, `test_i18n_fallback.py`) passed locally; recorded as completed side work
