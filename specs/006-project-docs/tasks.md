---
description: "Task breakdown for Feature 006: Project Documentation"
---

# Tasks: Project Documentation

**Input**: `spec.md` for Project Documentation
**Prerequisites**: v0.6.0 (i18n) ✅, v0.5.0 (collection) ✅

## Phase 1: Setup
- [ ] T201 Create project parser skeleton `ansibledoctor/parser/project_parser.py` and tests
- [ ] T202 Add pydantic models `ansibledoctor/models/project.py` (Project, Playbook, Inventory, HostGroup)

## Phase 2: Parsing & Analysis
- [ ] T203 [US14] Write tests for project parsing in `tests/unit/test_project_parser.py` (TDD)
- [ ] T204 [US14] Implement project parser to parse ansible.cfg, inventory, playbooks, roles, collections
- [ ] T205 [US14] Add discovery for local roles and collections inside a project

## Phase 3: Documentation Generation
- [ ] T206 [US15] Implement `ProjectDocumentationGenerator` using TemplateEngine
- [ ] T207 [US15] Write unit tests for generated project README and per-component docs
- [ ] T208 [US15] Add architecture summary generation (Mermaid diagram) and integration tests

## Template & i18n Integration

- [ ] T319 [US15] Add tests to ensure project-level templates reuse role/collection templates where appropriate (TDD)

- [ ] T320 [US18] Add translation keys and tests for project-level templates ensuring fallback behavior (TDD)

## Phase 4: Playbook & Visualization

- [ ] T209 [US16] Implement static playbook analysis to generate task flow diagrams

- [ ] T210 [US17] Implement visualization renderer and tests

## Phase 5: i18n Integration & Multi-Language

- [ ] T211 [US18] Add sample translation keys for Project docs (project.title, playbook.summary)

- [ ] T212 [US18] Add tests to verify translation fallback behaviour and per-language output generation

## Slug & Output Naming Tasks (Project-level)
- [ ] T301 [US14] Create `project_slug(name) -> str` utility in `ansibledoctor/utils/slug.py` with unit tests at `tests/unit/test_slug.py` ensuring ASCII-safe lowercase, hyphenation, dot-preserving behaviour
- [ ] T302 [US14] Update `ProjectDocumentationGenerator` to use `ansibleproject_{projectname}` slug and update CLI output paths to `docs/lang/{code}/ansibleproject_{projectname}/`; add integration tests to verify paths

## Phase 6: Polish & Docs

- [ ] T303 Update CLI usage and README examples for `generate-project` commands

- [ ] T304 Add migration docs and `--legacy-output` verification tests

## Phase 7: Release Prep

- [ ] T305 Finalize changelog & README updates

## Acceptance Tests

- [x] T306 E2E test: generate multi-language project docs and verify output structure and translated headers
    - Extended to verify generation in all formats (markdown, html, rst) for sample demo project artifacts (integration tests) [tests/integration/test_demo_all_formats_generation.py]

- [ ] T307 Performance test: ensure typical project doc generation under 10s

## CLI Commands & Integration (TDD first)

- [ ] T308 [US14] Write unit tests for `parse-project` CLI command in `tests/unit/test_cli_project.py` (TDD)
- [ ] T309 [US15] Implement `parse-project` CLI command skeleton and minimal functionality in `ansibledoctor/cli/project.py` (RED→GREEN)
- [x] T310 [US15] Write unit tests for `generate-project` CLI command, including options: `--languages`, `--output`, `--legacy-output`, `--force`, `--format` (TDD)
- [x] T311 [US15] Implement `generate-project` CLI command skeleton and integrate ProjectDocumentationGenerator (RED→GREEN)
    - Verified generate in all formats during integration tests (project/collection/role) [tests/integration/test_demo_all_formats_generation.py]
- [ ] T312 [US16] Add unit/integration tests for `analyze-project` and `visualize-project` CLI commands (TDD)
- [ ] T313 [US16] Implement `analyze-project` and `visualize-project` CLI command skeletons and basic parsers/renderers

## Parsing & Data Quality (TDD first)

- [ ] T314 [US14] Add tests & parsing logic for supported inventory formats (INI, YAML, host_vars/group_vars lookup) — `ansibledoctor/parser/inventory_parser.py` (TDD)
- [ ] T315 [US14] Add integration tests for monorepo / multi-ansible.cfg detection and project root discovery (TDD)
- [ ] T316 [US14] Implement variable precedence capture & documentation tests (ansible.cfg, group_vars, host_vars, role defaults) — include sample fixtures

## Security & Redaction

- [ ] T317 [US18] Add tests for redaction defaults (passwords, tokens, secrets) and a CLI flag `--redact-sensitive` (TDD)
- [ ] T318 [US18] Implement redaction configuration options (config defaults, mapping patterns, redaction replacements)

## Task Mapping to Checklists & Acceptance

- [ ] T321 Create traceability matrix that maps `checklists/project.md` CHK items to these tasks (T201-T320) and mark any coverage gaps; create `mappings/traceability.md` artifact (current file)

- [ ] T322 [ADMIN] Resolve or document feature numbering mismatch (constitution vs repo) and add guidance for maintainers; do not change code or branch names without consensus
