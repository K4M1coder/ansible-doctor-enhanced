# feat(i18n): Implement i18n support (Feature 005)

This PR implements i18n support:
- TranslationProvider and TranslationLoader with Babel pluralization support and caching
- Jinja `t()` filter and integration with the generator environment
- MultiLanguageGenerator to output per-locale docs under `docs/lang/*`
- Windows CI job, helper scripts, and a pre-commit hook for atomic changelog checks

See `CHANGELOG.md` and `README.md` for additional context.

Tests:
- Unit tests for pluralization and translations
- Integration tests for fallback and overlay behavior

Notes:
- `poetry install --with dev` to install dev deps locally
- Some Ansible tests require Linux (e.g. fcntl/grp modules) and may not run on Windows.
