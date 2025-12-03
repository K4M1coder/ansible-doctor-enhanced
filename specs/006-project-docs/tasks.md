---
description: "Task breakdown for Feature 006: Project Documentation"
---

# Tasks: Project Documentation

**Input**: `spec.md` for Project Documentation
**Prerequisites**: v0.6.0 (i18n) ✅, v0.5.0 (collection) ✅

## Phase 1: Setup
- [x] T201 Create project parser skeleton `ansibledoctor/parser/project_parser.py` and tests
- [x] T202 Add pydantic models `ansibledoctor/models/project.py` (Project, Playbook, Inventory, HostGroup)

## Phase 2: Parsing & Analysis
- [x] T203 [US14] Write tests for project parsing in `tests/unit/test_project_parser.py` (TDD)
- [x] T204 [US14] Implement project parser to parse ansible.cfg, inventory, playbooks, roles, collections
- [x] T205 [US14] Add discovery for local roles and collections inside a project

## Phase 3: Documentation Generation
- [x] T206 [US15] Implement `ProjectDocumentationGenerator` using TemplateEngine
- [x] T207 [US15] Write unit tests for generated project README and per-component docs
- [x] T208 [US15] Add architecture summary generation (Mermaid diagram) and integration tests

## Phase 4: CLI Commands & Integration (TDD first)
- [x] T308 [US14] Write unit tests for `parse-project` CLI command in `tests/unit/test_cli_project.py` (TDD)
- [x] T309 [US15] Implement `parse-project` CLI command skeleton and minimal functionality in `ansibledoctor/cli/project.py` (RED→GREEN)
- [x] T310 [US15] Write unit tests for `generate-project` CLI command, including options: `--languages`, `--output`, `--legacy-output`, `--force`, `--format` (TDD)
- [x] T311 [US15] Implement `generate-project` CLI command skeleton and integrate ProjectDocumentationGenerator (RED→GREEN)
- [x] T312 [US16] Add unit/integration tests for `analyze-project` and `visualize-project` CLI commands (TDD)
- [x] T313 [US16] Implement `analyze-project` and `visualize-project` CLI command skeletons and basic parsers/renderers

## Phase 5: i18n Integration & Multi-Language
- [x] T211 [US18] Add sample translation keys for Project docs (project.title, playbook.summary)
- [x] T212 [US18] Add tests to verify translation fallback behaviour and per-language output generation

## Slug & Output Naming Tasks (Project-level)
- [x] T301 [US14] Create `project_slug(name) -> str` utility in `ansibledoctor/utils/slug.py` with unit tests at `tests/unit/test_slug.py` ensuring ASCII-safe lowercase, hyphenation, dot-preserving behaviour
- [x] T302 [US14] Update `ProjectDocumentationGenerator` to use `ansibleproject_{projectname}` slug and update CLI output paths to `docs/lang/{code}/ansibleproject_{projectname}/`; add integration tests to verify paths
- [x] T319 [US15] Add tests to ensure project-level templates reuse role/collection templates where appropriate (TDD)

## Phase 6: Polish & Docs
- [x] T303 Update CLI usage and README examples for `generate-project` commands
- [x] T304 Add migration docs and `--legacy-output` verification tests
- [x] T305 Finalize changelog & README updates

## Parsing & Data Quality (TDD first)
- [x] T314 [US14] Add tests & parsing logic for supported inventory formats (INI, YAML, host_vars/group_vars lookup) — `ansibledoctor/parser/inventory_parser.py` (TDD)
- [x] T315 [US14] Add integration tests for monorepo / multi-ansible.cfg detection and project root discovery (TDD)
- [x] T316 [US14] Implement variable precedence capture & documentation tests (ansible.cfg, group_vars, host_vars, role defaults) — include sample fixtures

## Security & Redaction
- [x] T317 [US18] Add tests for redaction defaults (passwords, tokens, secrets) and a CLI flag `--redact-sensitive` (TDD)
- [x] T318 [US18] Implement redaction configuration options (config defaults, mapping patterns, redaction replacements)

## Acceptance Tests
- [x] T306 E2E test: generate multi-language project docs and verify output structure and translated headers
    - Extended to verify generation in all formats (markdown, html, rst) for sample demo project artifacts (integration tests) [tests/integration/test_demo_all_formats_generation.py]
- [x] T307 Performance test: ensure typical project doc generation under 10s
    - Created `tests/perf/test_project_perf.py` with tests for small/medium/large projects
    - All tests verify generation completes within 10s threshold
    - Added pytest --ignore=tests/fixtures to pyproject.toml

## Task Mapping to Checklists & Acceptance
- [x] T321 Create traceability matrix that maps `checklists/project.md` CHK items to these tasks (T201-T320) and mark any coverage gaps; create `mappings/traceability.md` artifact
    - Matrix already existed in mappings/traceability.md - verified complete with all 23 CHK items mapped
- [x] T322 [ADMIN] Resolve or document feature numbering mismatch (constitution vs repo) and add guidance for maintainers; do not change code or branch names without consensus
    - Created `specs/FEATURE_NUMBERING.md` documenting duplicate 007 folders and resolution guidance
    - Identified `007-hierarchical-context/` as canonical spec, `007-project-navigation/` as duplicate
    - Added version/feature alignment table and maintainer guidance

---

## Side work: 2025-11-30 (Docs/Packaging & CI)
- [x] T320 [P] Updated `README.md` and `CONTRIBUTING.md` to recommend `poetry install --with dev` and document run-from-source helper scripts
- [x] T323 [P] Ensured CLI `ansible-doctor-enhanced` alias and `ansibledoctor` convenience alias are present in `pyproject.toml` scripts
- [x] T324 [P] Verified `poetry lock` and `poetry install --with dev` complete via local checks and updated relevant docs

---

## Phase 7: Existing Docs & Deep Parsing (NEW)

**Purpose**: Add existing documentation extraction and deep recursive parsing support per SC-011, SC-012, SC-013.

### T325-T330: Existing Docs Extraction (US14 Extension)

- [ ] T325 [R] Write test_project_existing_docs.py: test DocsExtractor.extract() finds README, CHANGELOG, CONTRIBUTING, LICENSE at project root
- [ ] T326 [G] Integrate DocsExtractor into ProjectParser.parse() - populate Project.existing_docs field
- [ ] T327 [R] Write test for license type detection in project context (MIT, Apache-2.0, GPL-3.0)
- [ ] T328 [G] Add existing_docs: ExistingDocs field to Project model in models/project.py
- [ ] T329 [R] Write test for partial docs (only README exists, other files missing)
- [ ] T330 [R] Integration test: extract demo project existing docs, verify in Project model

### T331-T336: Deep Recursive Parsing (US14 Extension)

- [ ] T331 [R] Write test_deep_parsing.py: test --deep flag triggers full role/collection parsing
- [ ] T332 [G] Add deep_parse: bool parameter to ProjectParser.parse()
- [ ] T333 [G] When deep_parse=True, call RoleParser.parse() for each discovered role
- [ ] T334 [G] When deep_parse=True, call CollectionParser.parse() for each discovered collection
- [ ] T335 [R] Integration test: deep parse demo project, verify full role/collection details
- [ ] T336 [REFACTOR] Add CLI --deep flag to project parse/generate commands

### T337-T342: Generate Docs for Existing Docs (US15 Extension)

- [ ] T337 [R] Write test_generate_existing_docs_section.py: verify existing docs appear in generated project output
- [ ] T338 [G] Add existing docs section to project template (README content, CHANGELOG summary, license badge)
- [ ] T339 [R] Write test for license badge generation based on license_type
- [ ] T340 [G] Implement license badge rendering in project generator (shields.io style)
- [ ] T341 [R] Write test for CONTRIBUTING link in generated docs
- [ ] T342 [R] Integration test: generate docs for demo project with existing docs

---

## Status Summary

**Completed**: 32 tasks (T201-T324)
**New Tasks**: 18 tasks (T325-T342) - Existing Docs & Deep Parsing
**Remaining**: 18 tasks

Feature 006 implementation is 64% COMPLETE (32/50 tasks)
New Phase 7 adds existing documentation extraction and deep parsing support.

