# Tasks: Code Quality & CI/CD Infrastructure

**Input**: Design documents from `/specs/014-code-quality-cicd/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, checklists/
**Tests**: Tests are MANDATORY per Constitution §III (TDD). All tests must be written BEFORE implementation (Red-Green-Refactor).
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install and configure Black (24.4.0), isort (5.13.0), Ruff, mypy in pyproject.toml
- [x] T002 Create .pre-commit-config.yaml skeleton with repo structure
- [x] T003 [P] Add pre-commit library to dev dependencies
- [x] T004 Create helper scripts directory `scripts/`
- [x] T005 Create `scripts/run_pytest_precommit.py` wrapper for unified test execution

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Configure basic pre-commit hooks (checks-yaml, end-of-file-fixer, trailing-whitespace)
- [x] T007 Implement `scripts/check_yaml.py` for custom YAML validation
- [x] T008 [P] Create CI workflow directory structure in .github/workflows/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

## Phase 3: User Story 1 - Developer Commits Code with Quality Checks (Priority: P1)

**Goal**: Ensure every commit is automatically validated for code quality locally.

**Independent Test**: Developer commits code → Pre-commit hooks run → Code is formatted/validated → Commit succeeds only if all checks pass.

### Implementation for User Story 1

- [x] T009 [P] [US1] Configure Black hook in .pre-commit-config.yaml
- [x] T010 [P] [US1] Configure isort hook in .pre-commit-config.yaml
- [x] T011 [P] [US1] Configure Ruff hook in .pre-commit-config.yaml
- [x] T012 [P] [US1] Configure mypy hook with `pass_filenames: true` and exclusions
- [x] T013 [US1] Implement `scripts/sync_version.py` for version synchronization hook
- [x] T014 [US1] Implement `scripts/update_readme_toc.py` for table of contents management
- [x] T015 [US1] Configure `pytest-unit`, `pytest-integration` hooks using `run_pytest_precommit.py`

## Phase 4: User Story 2 - CI Pipeline Validates All Changes (Priority: P1)

**Goal**: Every push triggers comprehensive CI checks on multiple Python versions.

**Independent Test**: Code is pushed → CI runs on Windows (Python 3.11, 3.13) → All tests pass → Coverage is measured → Artifacts are uploaded.

### Implementation for User Story 2

- [x] T016 [US2] Create .github/workflows/ci-windows.yml with matrix strategy (3.11, 3.13)
- [x] T017 [US2] Add artifact upload logic for `coverage-*.json` and `pytest-*.xml`
- [x] T018 [US2] Add CLI smoke test step (`ansible-doctor-enhanced --help`) in CI
- [x] T019 [US2] Create .github/workflows/pre-commit.yml for pull requests
- [x] T020 [US2] Implement pre-commit output capture in `pre-commit.yml`
- [x] T021 [US2] Implement `scripts/parse_precommit_results.py` to convert logs to JSON
- [x] T022 [US2] Configure artifact upload for `precommit-metrics.json`

## Phase 5: User Story 3 - Badge System Provides Real-Time Metrics (Priority: P2)

**Goal**: Real-time code quality metrics displayed as badges in the README, integrating data from multiple sources.

**Independent Test**: CI completes → Badge workflow runs → Metrics are parsed → Badges are generated → JSONs uploaded to Gist/Artifacts.

### Implementation for User Story 3

- [X] T023 [US3] Create .github/workflows/badges.yml triggered by `workflow_run`
- [X] T024 [US3] Implement logic to download artifacts from triggering workflow (CI/Pre-commit)
- [X] T025 [US3] Implement `scripts/generate_badge_metrics.py` to aggregate:
    - Coverage JSON
    - Pre-commit metrics JSON
    - Performance results JSON
- [X] T026 [US3] Add fallback logic for manual component testing (`workflow_dispatch`)
- [X] T027 [US3] Configure `actions-deploy-gist` step for badge persistence
- [X] T028 [US3] Add badge definitions (16 total) to README.md pointing to Gist/Shields.io endpoint

## Phase 6: User Story 4 - Performance Regression Detection (Priority: P2)

**Goal**: Detect performance regressions with progressive tolerance.

**Independent Test**: Performance tests run → Timings are compared against thresholds → Status (pass/warn/fail) is determined → Badge reflects current performance.

### Implementation for User Story 4

- [X] T029 [US4] Create tests/performance/conftest.py for custom metrics plugin
- [X] T030 [US4] Implement progressive tolerance logic (target/max)
- [X] T031 [US4] Add `run_pytest_precommit.py` support for performance test group
- [X] T032 [US4] Configure CI to upload `performance-results.json` artifact
- [X] T033 [US4] Update `generate_badge_metrics.py` to parse and color-code performance data

## Phase 7: User Story 5 - Commit Quality Standards Enforcement (Priority: P1)

**Goal**: Documented standards for commit quality with pre-commit enforcement.

**Independent Test**: Contributor attempts to bypass pre-commit → CI catches it → standards guide them.

### Implementation for User Story 5

- [X] T034 [US5] Implement `scripts/validate_atomic_changelog.py` logic
- [X] T035 [US5] Add `validate-atomic-changelog` hook to .pre-commit-config.yaml
- [X] T036 [US5] Create .github/COMMIT_QUALITY.md documentation
- [X] T037 [US5] Configure `check-changelog-atomic.yml` workflow for strictly atomic updates

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T038 Verify complex dependency chains in pre-commit hooks (e.g. `types-*` packages)
- [X] T039 Ensure `pyproject.toml` tool versions match pre-commit versions
- [X] T040 Update `CONTRIBUTING.md` to reference new quality tools
- [X] T041 Validate Gist integration permissions and secrets
