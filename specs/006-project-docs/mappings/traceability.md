# Traceability Matrix — Project Documentation

This artifact maps the `CHK` checklist items (quality/acceptance checks) to the `T` task IDs in `tasks.md` that implement or validate them.

| CHK | Description | Mapped Task(s) | Notes |
|---|---|---|---|
| CHK001 | Ansible.cfg parsing & key fields (project name, default paths) | T201, T203, T204 | Parser + unit tests validate fields; ensure `ansible.cfg` parser covers roles_path, collections_path |
| CHK002 | Inventory formats & precedence (INI/YAML, group/host precedence) | T314, T315, T316 | Inventory parser + integration tests to cover INI/YAML; variable precedence captured by T316 |
| CHK003 | Playbook parsing semantics & expected detail level | T209, T210 | Static analysis + visualization tasks validate playbook extraction and flow diagrams |
| CHK004 | Project naming & output folder / slug rules | T301, T302 | Slug tasks ensure `ansibleproject_{projectname}` outputs |
| CHK005 | Local collections & roles inclusion & nested ownership | T205, T206 | Discovery & ProjectDocumentationGenerator must include nested collections and local roles |
| CHK006 | i18n for project docs & multi-language generation | T211, T212, T320 | Translation keys and fallback behavior tests |
| CHK007 | Visual architecture diagrams (Mermaid / format) | T208, T209, T210 | Diagrams and playbook flow mapping |
| CHK008 | CLI commands + flags & examples | T308-T313, T303 | Unit/integration tests for CLI commands, README usage tested in T303 |
| CHK009 | Performance expectations & integration tests (<10s) | T307, T314, T315 | Performance test + parser optimizations |
| CHK010 | Cross-project or external collection references | T206, T302 | Map external vs local collection references in docs |
| CHK011 | Breadcrumb / hierarchical parent detection | T315, T322 | Monorepo detection + admin guidance; consider integration with Feature 007 tasks |
| CHK012 | Fallback behavior for missing ansible.cfg or ambiguous inventory | T203, T314 | Parser error modes should be covered by unit/integration tests |
| CHK013 | Acceptance tests & test data structures defined | T306, T207 | E2E and unit coverage provide sample fixtures and expected outputs |
| CHK014 | Output structure for docs/lang/{code}/project/ | T302, T311 | Generator + CLI ensure output path layout + legacy migration |
| CHK015 | Security & privacy / sensitive data redaction | T317, T318 | Tests & config for `--redact-sensitive` option and default safe behavior |
| CHK016 | Examples of expected generated content included | T206, T207 | Unit tests for generated README and component outputs |
| CHK017 | Multi-language generation & i18n coverage | T211, T212, T320 | Ensure translations load & fallbacks applied |
| CHK018 | Monorepo & multi-ansible.cfg/complex layout handling | T315 | Tests for project root detection & monorepo heuristics |
| CHK019 | Safe overwrite rules & `--force` usage | T303, T311 | CLI docs and generator CLI behavior; tests to ensure safe defaults |
| CHK020 | Tracing & structured logging rules included (correlation IDs) | T203, T303 | Parser & CLI/Generator should add structured logs; add logging tests during integration |
| CHK021 | CLI flags & commands implemented & tested | T308-T313 | Cross-check presence of unit/integration tests for each CLI command |
| CHK022 | Checklist mapping completeness | T321 | This artifact (T321) is the traceability matrix — mapping CHKs to tasks |
| CHK023 | Variable precedence captured & documented | T316 | Tests for precedence & documentation output |
| CHK024 | Existing docs extraction (README, CHANGELOG, CONTRIBUTING, LICENSE) | T325-T330 | DocsExtractor integration, ExistingDocs model (NEW) |
| CHK025 | License type detection algorithm | T327, T339, T340 | Keyword patterns for MIT, Apache-2.0, GPL-3.0; license badge generation (NEW) |
| CHK026 | Deep recursive parsing option (--deep flag) | T331-T336 | Full role/collection parsing vs shallow discovery (NEW) |
| CHK027 | Generated documentation sections for existing docs | T337-T342 | Template slots, section order, license badge placement (NEW) |
| CHK028 | ExistingDocs model shared across Role/Collection/Project | T328 | Verify model consistency in models/existing_docs.py (NEW) |

---

Notes:
- This map reflects the current tasks in `tasks.md`. When tasks or CHKs change, update this file accordingly.
- Any CHK mapped only to documentation tasks (e.g., T303) should also be validated via unit tests (preferred) to satisfy Constitution Article IV (Integration & Contract Testing).
- **NEW**: CHK024-CHK028 added for Phase 7 (Existing Docs & Deep Parsing) requirements.

## Checklist Completion

All project checklist items in `checklists/project.md` have been reviewed. CHK001-CHK023 are complete; CHK024-CHK028 are new items for Phase 7 implementation. Each CHK maps to at least one task (T###) in this file. Update this matrix if task IDs or mappings change.

