# Merge Request: feature/006-project-docs -> dev

Title: Add LanguageConfig + i18n groundwork (T005-01)

Summary:
- Adds a `LanguageConfig` Pydantic model to validate language options (`default`, `enabled`, `fallback`, `detect_system`).
- Adds unit tests for the new model ensuring ISO 639-1 validation and defaults.  

Change-type: minor
PR-Notes:
- Committed under `006-project-docs` branch; this will be merged into `dev` as an atomic commit for the initial i18n scaffolding.
 - Future work: Implementation of `TranslationProvider`, `t()` template filter, `MultiLanguageGenerator`, CLI `--languages`, and translation file merging.

Testing:
- Added `tests/unit/test_language_config.py` with validation and defaults. All tests pass for the added suite locally.

Linked Tasks:
- T005-01 (LanguageConfig)

Changelog:
- Added: `LanguageConfig` pydantic model for i18n config validation (T005-01)
