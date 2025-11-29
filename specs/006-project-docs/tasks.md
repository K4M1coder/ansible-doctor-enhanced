---
description: "Task breakdown for Feature 006: Project Documentation"
---

# Tasks: Project Documentation

**Input**: `spec.md` for Project Documentation
**Prerequisites**: v0.6.0 (i18n) ✅, v0.5.0 (collection) ✅

## Phase 1: Setup
## Phase 1: Setup
- [x] T201 Create project parser skeleton `ansibledoctor/parser/project_parser.py` and tests
- [x] T202 Add pydantic models `ansibledoctor/models/project.py` (Project, Playbook, Inventory, HostGroup)

## Phase 2: Parsing & Analysis
## Phase 2: Parsing & Analysis
- [x] T203 [US14] Write tests for project parsing in `tests/unit/test_project_parser.py` (TDD)
 - [x] T204 [US14] Implement project parser to parse ansible.cfg, inventory, playbooks, roles, collections
- [x] T205 [US14] Add discovery for local roles and collections inside a project

## Phase 3: Documentation Generation
## Phase 3: Documentation Generation
- [x] T206 [US15] Implement `ProjectDocumentationGenerator` using TemplateEngine
- [x] T207 [US15] Write unit tests for generated project README and per-component docs
- [x] T208 [US15] Add architecture summary generation (Mermaid diagram) and integration tests

## Slug & Output Naming Tasks (Project-level)
- [x] T301 [US14] Create `project_slug(name) -> str` utility in `ansibledoctor/utils/slug.py` with unit tests at `tests/unit/test_slug.py` ensuring ASCII-safe lowercase, hyphenation, dot-preserving behaviour
- [x] T302 [US14] Update `ProjectDocumentationGenerator` to use `ansibleproject_{projectname}` slug and update CLI output paths to `docs/lang/{code}/ansibleproject_{projectname}/`; add integration tests to verify paths
- [x] T319 [US15] Add tests to ensure project-level templates reuse role/collection templates where appropriate (TDD)

## Phase 7: Release Prep
- [x] T305 Finalize changelog & README updates

## Phase 4: Playbook & Visualization
## CLI Commands & Integration (TDD first)
- [x] T308 [US14] Write unit tests for `parse-project` CLI command in `tests/unit/test_cli_project.py` (TDD)
- [x] T309 [US15] Implement `parse-project` CLI command skeleton and minimal functionality in `ansibledoctor/cli/project.py` (RED→GREEN)
- [x] T310 [US15] Write unit tests for `generate-project` CLI command, including options: `--languages`, `--output`, `--legacy-output`, `--force`, `--format` (TDD)
- [x] T311 [US15] Implement `generate-project` CLI command skeleton and integrate ProjectDocumentationGenerator (RED→GREEN)

## Phase 5: i18n Integration & Multi-Language

 - [x] T211 [US18] Add sample translation keys for Project docs (project.title, playbook.summary)

 - [x] T212 [US18] Add tests to verify translation fallback behaviour and per-language output generation

## Slug & Output Naming Tasks (Project-level)
- [ ] T301 [US14] Create `project_slug(name) -> str` utility in `ansibledoctor/utils/slug.py` with unit tests at `tests/unit/test_slug.py` ensuring ASCII-safe lowercase, hyphenation, dot-preserving behaviour
- [x] T302 [US14] Update `ProjectDocumentationGenerator` to use `ansibleproject_{projectname}` slug and update CLI output paths to `docs/lang/{code}/ansibleproject_{projectname}/`; add integration tests to verify paths

## Phase 6: Polish & Docs

- [x] T303 Update CLI usage and README examples for `generate-project` commands

- [x] T304 Add migration docs and `--legacy-output` verification tests

## Phase 7: Release Prep

- [ ] T305 Finalize changelog & README updates

---

## Side work: 2025-11-30 (Docs/Packaging & CI)

- [x] 2025-11-30: Updated `README.md` and `CONTRIBUTING.md` to recommend `poetry install --with dev` and to document run-from-source helper scripts (done)
- [x] 2025-11-30: Ensured CLI `ansible-doctor-enhanced` alias and `ansibledoctor` convenience alias are present in `pyproject.toml` scripts (done)
- [x] 2025-11-30: Verified `poetry lock` and `poetry install --with dev` complete via local checks and updated relevant docs (done)


## Acceptance Tests

- [x] T306 E2E test: generate multi-language project docs and verify output structure and translated headers
    - Extended to verify generation in all formats (markdown, html, rst) for sample demo project artifacts (integration tests) [tests/integration/test_demo_all_formats_generation.py]

- [ ] T307 Performance test: ensure typical project doc generation under 10s

## CLI Commands & Integration (TDD first)

- [x] T310 [US15] Write unit tests for `generate-project` CLI command, including options: `--languages`, `--output`, `--legacy-output`, `--force`, `--format` (TDD)
- [x] T311 [US15] Implement `generate-project` CLI command skeleton and integrate ProjectDocumentationGenerator (RED→GREEN)
    - Verified generate in all formats during integration tests (project/collection/role) [tests/integration/test_demo_all_formats_generation.py]
- [x] T312 [US16] Add unit/integration tests for `analyze-project` and `visualize-project` CLI commands (TDD)
- [x] T313 [US16] Implement `analyze-project` and `visualize-project` CLI command skeletons and basic parsers/renderers

## Parsing & Data Quality (TDD first)

 - [x] T314 [US14] Add tests & parsing logic for supported inventory formats (INI, YAML, host_vars/group_vars lookup) — `ansibledoctor/parser/inventory_parser.py` (TDD)
 - [x] T315 [US14] Add integration tests for monorepo / multi-ansible.cfg detection and project root discovery (TDD)
 - [x] T316 [US14] Implement variable precedence capture & documentation tests (ansible.cfg, group_vars, host_vars, role defaults) — include sample fixtures

## Security & Redaction

 - [x] T317 [US18] Add tests for redaction defaults (passwords, tokens, secrets) and a CLI flag `--redact-sensitive` (TDD)
 - [x] T318 [US18] Implement redaction configuration options (config defaults, mapping patterns, redaction replacements)

## Task Mapping to Checklists & Acceptance

- [ ] T321 Create traceability matrix that maps `checklists/project.md` CHK items to these tasks (T201-T320) and mark any coverage gaps; create `mappings/traceability.md` artifact (current file)

- [ ] T322 [ADMIN] Resolve or document feature numbering mismatch (constitution vs repo) and add guidance for maintainers; do not change code or branch names without consensus

## MVP Status & Backlog

MVP (Minimum Viable Product) for Feature 006 was completed locally and merged to `dev` on 2025-11-27.

Completed MVP work includes: T201, T202, T203, T205, T206, T207, T301, T302, T305, T310, T311 (verify in commit history & changelog).

High-priority backlog (candidate for next sprint or immediate assignment):
 - [x] T204 — Full project parser (ansible.cfg, inventory, playbook parsing) — HIGH
 - [x] T208 — Architecture summary (Mermaid diagram generation) — HIGH
 - [x] T209 — Playbook static analysis (task flow diagrams) — HIGH
 - [x] T210 — Visualization renderer & tests — HIGH
- [ ] T312/T313 — Implement analyze/visualize CLI and tests — HIGH
- [ ] T314/T315/T316 — Inventory parsing & monorepo/root detection & variable precedence — HIGH
- [ ] T317/T318 — Redaction tests and CLI config — HIGH
- [ ] T319/T320 — Template reuse & i18n integration for project-level templates — HIGH

Notes: these backlog items should be scheduled according to team capacity; update `tasks.md` and mark them as [x] when complete.
