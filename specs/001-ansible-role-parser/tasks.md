---
description: "Task breakdown for Feature 001: Ansible Role Parser"
---

# Tasks: Ansible Role Parser with Annotation Extraction

**Input**: Design documents from `/specs/001-ansible-role-parser/`
**Prerequisites**: plan.md ✓, spec.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 0: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per Constitution Article VII (Simplicity Gate)

- [X] T001 Initialize Python project with Poetry at repository root (pyproject.toml)
- [X] T002 Configure dependencies: ruamel.yaml, pydantic v2, click, structlog, pathspec
- [X] T003 [P] Configure dev dependencies: pytest, pytest-cov, pytest-mock, hypothesis, mypy, black, isort, ruff
- [X] T004 [P] Configure development tools: black (line-length 100), isort, mypy --strict in pyproject.toml
- [X] T005 Create project structure: ansibledoctor/{__init__.py, exceptions.py, models/, parser/, cli/, utils/}
- [X] T006 Create test structure: tests/{unit/, integration/fixtures/}
- [X] T007 [P] Setup structured logging infrastructure in ansibledoctor/utils/logging.py (Article V)
- [X] T008 [P] Create base exception hierarchy in ansibledoctor/exceptions.py
- [X] T009 Update CHANGELOG.md [Unreleased] section with project setup (Article VIII)
- [X] T010 Update README.md Installation section with Poetry setup (Article IX)

---

<!-- Side work entries were moved to the end of this file and renumbered to maintain numeric continuity. See the bottom of this file for the task IDs T101-T104. -->


**Checkpoint**: Foundation ready - project structure initialized, dependencies configured

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create protocol definitions in ansibledoctor/parser/protocols.py (RoleParser, YAMLLoader, AnnotationExtractor)
- [X] T012 [P] Create Pydantic models in ansibledoctor/models/role.py (AnsibleRole)
- [X] T013 [P] Create Pydantic models in ansibledoctor/models/metadata.py (RoleMetadata, ArgumentSpec, Platform, Dependency)
- [X] T014 [P] Create Pydantic models in ansibledoctor/models/variable.py (Variable, VariableType enum)
- [X] T015 [P] Create Pydantic models in ansibledoctor/models/annotation.py (Annotation, AnnotationType enum, TodoItem, Example)
- [X] T016 [P] Create Pydantic models in ansibledoctor/models/tag.py (Tag)
- [X] T017 Implement YAML loader in ansibledoctor/parser/yaml_loader.py using ruamel.yaml
- [X] T018 [P] Create path utilities in ansibledoctor/utils/paths.py (role validation, .ansibledoctor-ignore support)
- [X] T019 [P] Setup integration test fixtures: tests/integration/fixtures/{minimal_role/, complex_role/, invalid_role/}
- [X] T020 Update CHANGELOG.md with foundational models and infrastructure (Article VIII)

**Checkpoint**: Foundation ready - all protocols, models, and base utilities complete

---

## Phase 2: User Story 1 - Extract Role Metadata from Galaxy (Priority: P1) 🎯 MVP

**Goal**: Parse meta/main.yml and meta/argument_specs.yml to extract galaxy_info, dependencies, and argument specifications

**Independent Test**: Provide role with meta/main.yml → verify JSON output contains author, description, license, platforms, dependencies

### Implementation for User Story 1

- [X] T021 [P] [US1] Write unit tests for metadata parser in tests/unit/test_metadata_parser.py (TDD - tests FIRST)
- [X] T022 [P] [US1] Write integration test for US1 in tests/integration/test_role_parser.py using minimal_role fixture
- [X] T023 [US1] Implement metadata parser in ansibledoctor/parser/metadata_parser.py (parse_galaxy_info function)
- [X] T024 [US1] Implement argument_specs parser in ansibledoctor/parser/metadata_parser.py (parse_argument_specs function)
- [X] T025 [US1] Add metadata validation: check for required fields, log warnings for missing data
- [X] T026 [US1] Add error handling: YAML syntax errors, missing files, malformed metadata
- [X] T027 [US1] Add structured logging for metadata parsing operations (file_path, metadata_keys found)
- [X] T028 [US1] Integrate metadata parser into main RoleParser in ansibledoctor/parser/role_parser.py
- [X] T029 [US1] Run integration tests - verify US1 works independently with minimal_role fixture
- [X] T030 [US1] Update CHANGELOG.md [Unreleased] → Added: "Metadata extraction from meta/main.yml and argument_specs.yml"
- [X] T031 [US1] Update README.md Usage section with metadata extraction example

**Checkpoint**: At this point, User Story 1 should be fully functional - can extract and output role metadata independently

---

## Phase 3: User Story 2 - Parse Variable Definitions with Annotations (Priority: P1) 🎯 MVP

**Goal**: Extract variables from defaults/main.yml and vars/main.yml with inline @var annotations

**Independent Test**: Provide YAML with annotated variables → verify JSON contains variable names, values, types, annotations

### Implementation for User Story 2

- [X] T032 [P] [US2] Write unit tests for annotation parser in tests/unit/test_annotation_parser.py (TDD - tests FIRST)
- [X] T033 [P] [US2] Write unit tests for variable parser in tests/unit/test_variable_parser.py
- [X] T034 [P] [US2] Write integration test for US2 in tests/integration/test_role_parser.py using complex_role fixture
- [X] T035 [US2] Implement annotation regex patterns in ansibledoctor/parser/annotation_parser.py (single-line, multiline, JSON formats)
- [X] T036 [US2] Implement annotation extraction logic: parse @var, @tag, @todo, @example, @meta with line numbers
- [X] T037 [US2] Implement JSON annotation parser for format: # @var name: $ {"type": "string", "example": "value"}
- [X] T038 [US2] Implement variable parser in ansibledoctor/parser/variable_parser.py (parse defaults/ and vars/)
- [X] T039 [US2] Implement type inference for variables: string, number, boolean, list, dict, null
- [X] T040 [US2] Associate parsed annotations with variables by name matching
- [X] T041 [US2] Handle nested variables: preserve structure, annotate nested keys when present
- [X] T042 [US2] Add error handling: malformed annotations, YAML parsing errors
- [X] T043 [US2] Add structured logging for variable parsing (file_path, variable_count, annotation_count)
- [X] T044 [US2] Integrate variable parser into main RoleParser in ansibledoctor/parser/role_parser.py
- [X] T045 [US2] Run integration tests - verify US2 works independently with complex_role fixture
- [X] T046 [US2] Update CHANGELOG.md [Unreleased] → Added: "Variable extraction with @var annotation support (single-line, multiline, JSON)"
- [X] T047 [US2] Update README.md Usage section with variable annotation examples

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - metadata + variables extraction functional

---

## Phase 4: User Story 3 - Extract Task Tags and Descriptions (Priority: P2)

**Goal**: Discover task tags from tasks/*.yml and associate with @tag annotations

**Independent Test**: Provide task files with tags and @tag annotations → verify JSON lists unique tags with descriptions

### Implementation for User Story 3

- [X] T048 [P] [US3] Write unit tests for task parser in tests/unit/test_task_parser.py (TDD - tests FIRST)
- [X] T049 [P] [US3] Write integration test for US3 in tests/integration/test_role_parser.py
- [X] T050 [US3] Implement task file discovery in ansibledoctor/parser/task_parser.py (tasks/*.yml, recursive includes)
- [X] T051 [US3] Implement tag extraction from task definitions (single tags and tag arrays)
- [X] T052 [US3] Extract @tag annotations and associate with tag names
- [X] T053 [US3] Implement recursive include/import following: detect include_tasks, import_tasks, include_role
- [X] T054 [US3] Aggregate unique tags across all task files with usage counts
- [X] T055 [US3] Add error handling for missing task files, invalid task syntax
- [X] T056 [US3] Add structured logging for task parsing (task_count, tag_count, includes_followed)
- [X] T057 [US3] Integrate task parser into main RoleParser in ansibledoctor/parser/role_parser.py
- [X] T058 [US3] Run integration tests - verify US3 works independently
- [X] T059 [US3] Update CHANGELOG.md [Unreleased] → Added: "Task tag extraction with @tag annotation support"
- [X] T060 [US3] Update README.md Usage section with tag extraction example

**Checkpoint**: User Stories 1, 2, AND 3 all functional independently - metadata, variables, tags extraction complete

---

## Phase 5: User Story 4 - Collect TODO Comments and Examples (Priority: P3)

**Goal**: Extract @todo and @example annotations from all role files

**Independent Test**: Provide files with @todo and @example annotations → verify JSON includes TODO items and example blocks

### Implementation for User Story 4

- [X] T061 [P] [US4] Write unit tests for TODO and example extraction in tests/unit/test_annotation_parser.py
- [X] T062 [P] [US4] Write integration test for US4 in tests/integration/test_role_parser.py
- [X] T063 [US4] Implement @todo extraction in ansibledoctor/parser/annotation_parser.py (parse priority if present)
- [X] T064 [US4] Implement @example extraction with code block parsing (multiline format: # @example: > ... @end)
- [X] T065 [US4] Scan all role files for TODOs and examples (not just YAML - include .j2 templates)
- [X] T066 [US4] Add file location tracking (file_path, line_number) for all TODOs and examples
- [X] T067 [US4] Add structured logging for annotation collection (todo_count, example_count)
- [X] T068 [US4] Integrate TODO/example collection into main RoleParser
- [X] T069 [US4] Run integration tests - verify US4 works independently
- [X] T070 [US4] Update CHANGELOG.md [Unreleased] → Added: "@todo and @example annotation extraction"
- [X] T071 [US4] Update README.md Usage section with TODO/example extraction example

**Checkpoint**: All 4 user stories functional independently - complete feature set for parser library

---

## Phase 6: CLI Interface (Constitution Article II)

**Purpose**: Implement command-line interface per CLI Interface Mandate

- [X] T072 [P] Write unit tests for CLI in tests/unit/test_cli.py
- [X] T073 [US-CLI] Implement base CLI in ansibledoctor/cli/__init__.py using click framework
- [X] T074 [US-CLI] Implement parse command in ansibledoctor/cli/parse.py with options: --role-path, --output, --format, --log-level
- [X] T075 [US-CLI] Add --recursive flag for multi-role directory scanning
- [X] T076 [US-CLI] Implement JSON output to stdout, logs to stderr (shell pipeline compatible)
- [X] T077 [US-CLI] Add exit codes: 0 (success), 1 (parse error), 2 (usage error)
- [X] T078 [US-CLI] Add --validate flag to check role structure without full parsing
- [X] T079 [US-CLI] Create CLI entry point in pyproject.toml [tool.poetry.scripts]
- [X] T080 [US-CLI] Test CLI with all integration fixtures: minimal_role, complex_role, invalid_role
- [X] T081 [US-CLI] Update CHANGELOG.md [Unreleased] → Added: "CLI interface with parse command"
- [X] T082 [US-CLI] Update README.md Quick Start section with CLI usage examples

**Checkpoint**: CLI fully functional - parser accessible via command line

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality improvements per Constitution Articles

- [X] T083 [P] Add type checking: run mypy --strict on all modules, fix type errors
- [X] T084 [P] Add code formatting: run black and isort on all modules
- [X] T085 [P] Add linting: run ruff, fix issues
- [X] T086 Run full test suite: pytest tests/ --cov=ansibledoctor --cov-report=term-missing
- [X] T087 Verify coverage ≥80% (Article III requirement), add tests for uncovered lines
- [X] T088 [P] Add property-based tests for annotation parsing using hypothesis (edge cases)
  - **KNOWN BUG**: Fix annotation parsing when content is just `:` (e.g., `@var test_var: :`)
  - Current behavior: ValidationError - parsed_attributes.None.[key] expects string, got None
  - Discovered by hypothesis in test_var_annotation_with_any_description (falsifying example: description=':')
  - Root cause: parse_annotation_attributes() returns dict with None key when content is single colon
  - Expected: Should handle edge case gracefully (empty description or skip None keys)
- [X] T089 [P] Create quickstart.md validation: manual test of documented examples
- [X] T090 Test error scenarios: malformed YAML, circular dependencies, missing files
- [X] T091 Performance testing: verify <500ms for typical role, <2s for large role (SC-002)
- [X] T092 Test cross-platform: verify on Windows, Linux, macOS (if applicable)
- [X] T093 Add docstrings to all public APIs (modules, classes, functions)
- [X] T094 Generate API documentation: update README.md with API reference section
- [X] T095 Review and update README.md: verify all 10 required sections complete (Article IX)
- [X] T096 Review and finalize CHANGELOG.md: ensure all changes documented (Article VIII)
- [X] T097 Create quickstart.md in specs/001-ansible-role-parser/ with developer validation scenarios
- [X] T098 Run constitution compliance check: verify all 9 articles satisfied
- [X] T099 Create Git tag: v0.1.0 (first development release)
- [X] T100 Update CHANGELOG.md: move [Unreleased] to [0.1.0] with release date

## Slug & Output Naming Tasks (Role-level)

- [X] T228 [US1] Create `role_slug(namespace, name) -> str` utility in `ansibledoctor/utils/slug.py` with unit tests in `tests/unit/test_slug.py` verifying sanitization rules and dot-notation retention (e.g., `namespace.role_name`).
- [X] T229 [US1] Update RoleParser to include `role_slug` in generated output metadata: add `slug` property to role JSON output and ensure CLI output uses the slug for link generation.
- [ ] T230 [US1] Add integration tests for role slug output and verify backward compatibility with `--legacy-output` when using the option.

**Checkpoint**: Feature 001 complete, tested, documented, and ready for use

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 0)**: No dependencies - can start immediately
- **Foundational (Phase 1)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 2)**: Depends on Foundational completion - Can proceed independently
- **User Story 2 (Phase 3)**: Depends on Foundational completion - Can proceed in parallel with US1 (different files)
- **User Story 3 (Phase 4)**: Depends on Foundational completion - Can proceed in parallel with US1/US2
- **User Story 4 (Phase 5)**: Depends on Foundational completion - Can proceed in parallel with others
- **CLI Interface (Phase 6)**: Depends on US1 and US2 completion (P1 MVP stories)
- **Polish (Phase 7)**: Depends on all desired user stories and CLI completion

### User Story Independence

- **US1 (Metadata)**: Fully independent - only needs Foundation
- **US2 (Variables)**: Fully independent - only needs Foundation
- **US3 (Tags)**: Fully independent - only needs Foundation
- **US4 (TODO/Examples)**: Fully independent - only needs Foundation

**Note**: User stories can be implemented in parallel by different developers after Foundation phase completes.

### Within Each User Story

1. Write tests FIRST (TDD - Article III)
2. Implement parser logic
3. Add error handling and logging
4. Integrate into main RoleParser
5. Run integration tests
6. Update CHANGELOG.md (Article VIII)
7. Update README.md if user-facing changes (Article IX)

### Parallel Opportunities

**Phase 0 (Setup)**: T003, T004, T007, T008 can run in parallel
**Phase 1 (Foundational)**: T012-T016 (models) can run in parallel, T018-T019 can run in parallel
**Phase 2 (US1)**: T021 and T022 can run in parallel (test files)
**Phase 3 (US2)**: T032, T033, T034 can run in parallel (test files)
**Phase 4 (US3)**: T048 and T049 can run in parallel
**Phase 5 (US4)**: T061 and T062 can run in parallel
**Phase 7 (Polish)**: T083, T084, T085, T088, T089 can run in parallel

**After Foundation**: US1 (T021-T031), US2 (T032-T047), US3 (T048-T060), US4 (T061-T071) can ALL proceed in parallel if team capacity allows

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 0: Setup (T001-T010)
2. Complete Phase 1: Foundational (T011-T020) - **CRITICAL GATE**
3. Complete Phase 2: US1 Metadata (T021-T031)
4. Complete Phase 3: US2 Variables (T032-T047)
5. Complete Phase 6: CLI Interface (T072-T082)
6. Complete Phase 7: Polish (T083-T100)
7. **STOP and VALIDATE**: MVP with metadata + variables extraction functional

### Incremental Delivery

1. MVP (US1 + US2) → Tag as v0.1.0 → Deploy/Demo
2. Add US3 (Tags) → Tag as v0.2.0 → Deploy/Demo
3. Add US4 (TODO/Examples) → Tag as v0.3.0 → Deploy/Demo
4. Each version adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers after Foundation (Phase 1):

- **Developer A**: US1 (T021-T031) - Metadata extraction
- **Developer B**: US2 (T032-T047) - Variables and annotations
- **Developer C**: US3 (T048-T060) - Task tags
- **Developer D**: US4 (T061-T071) - TODO/Examples

Once P1 stories (US1, US2) complete:
- **Developer E**: CLI Interface (T072-T082)

Finally all team:
- **All**: Polish and quality (T083-T100)

---

## Notes

- **[P]** = Parallel-safe tasks (different files, no blocking dependencies)
- **[Story]** = Maps task to user story for traceability and independent testing
- **TDD Mandate** (Article III): Tests MUST be written and FAIL before implementation
- **Commit Strategy**: Commit after each task or logical group of parallel tasks
- **Documentation Mandate** (Articles VIII & IX): EVERY task that adds/changes features MUST update CHANGELOG.md and README.md appropriately
- **Constitution Compliance**: All tasks designed to satisfy 9 constitutional articles
- Each user story should be independently completable and testable at checkpoints
- Stop at any checkpoint to validate story independently before proceeding
- Memory: Use structured logging with context (file paths, counts) for observability
- Performance: Monitor parsing time during integration tests to meet <500ms goal

---

## Task Count Summary

- **Phase 0 (Setup)**: 10 tasks
- **Phase 1 (Foundational)**: 10 tasks
- **Phase 2 (US1 - Metadata)**: 11 tasks
- **Phase 3 (US2 - Variables)**: 16 tasks
- **Phase 4 (US3 - Tags)**: 13 tasks
- **Phase 5 (US4 - TODO/Examples)**: 11 tasks
- **Phase 6 (CLI)**: 11 tasks
- **Phase 7 (Polish)**: 18 tasks

**Total**: 104 tasks

**MVP Tasks** (Setup + Foundation + US1 + US2 + CLI): 58 tasks
**Full Feature**: 100 tasks

---

## Side work: 2025-11-30 (Infra / Tools)

- [x] T101 [P] Add `.pre-commit-config.yaml` and `scripts/validate_atomic_changelog.py` hook; ensure pre-commit integration instructions are in `CONTRIBUTING.md`
- [x] T102 [P] Migrate dev dependencies out of deprecated `tool.poetry.dev-dependencies` section by moving `tomli` into `tool.poetry.group.dev.dependencies` and update `pyproject.toml`
- [x] T103 [P] Add `ghapi` as a dev-dependency and `scripts/create_pr.py` helper to create GitHub PRs programmatically for CI and developer convenience
- [x] T104 [P] Add `scripts/run_cli_main.py`, `scripts/run_cli.*` and `scripts/run_tests.*` to simplify running CLI and tests from source

