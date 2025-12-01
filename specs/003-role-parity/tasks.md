---

description: "Task list template for feature implementation"
---

# Tasks: ansible-doctor Parity - Config & Watch Mode

**Branch**: `003-role-parity` | **Milestone**: v0.4.0  
**Input**: Design documents from `/specs/003-role-parity/`  
**Prerequisites**: spec.md ✅, plan.md ✅

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create module structure and install dependencies

- [X] T001 Create `ansibledoctor/config/` module directory structure
  - `ansibledoctor/config/__init__.py`
  - `ansibledoctor/config/models.py`
  - `ansibledoctor/config/loader.py`
  - `ansibledoctor/config/validator.py`

- [X] T002 Create `ansibledoctor/watcher/` module directory structure
  - `ansibledoctor/watcher/__init__.py`
  - `ansibledoctor/watcher/monitor.py`
  - `ansibledoctor/watcher/debouncer.py`
  - `ansibledoctor/watcher/handler.py`

- [X] T003 [P] Add `watchdog` dependency to pyproject.toml
  - Add `watchdog = "^6.0.0"` to [tool.poetry.dependencies]
  - Run `poetry lock` to update lock file

- [X] T004 [P] Create test fixture directories
  - `tests/fixtures/config_files/` for sample .ansibledoctor.yml files
  - Create valid, invalid, and edge-case config samples

**Checkpoint**: Module structure ready, dependencies installed ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core config schema that both US1 and US2 depend on

**⚠️ CRITICAL**: Config models must be complete before implementing US1 or US2

- [X] T005 Create ConfigModel Pydantic schema in `ansibledoctor/config/models.py`
  - Fields: output (str | None), output_format (str | None), template (str | None)
  - Fields: template_dir (str | None), recursive (bool), output_dir (str | None)
  - Fields: exclude_patterns (list[str])
  - Validators: output_format must be valid (markdown/html/rst)
  - Defaults matching v0.3.0 CLI defaults

- [X] T006 [P] Add unit tests for ConfigModel in `tests/unit/test_config_models.py`
  - Test valid config with all fields
  - Test valid config with minimal fields (defaults applied)
  - Test invalid output_format (should raise ValidationError)
  - Test exclude_patterns as list and empty list
  - 100% coverage of ConfigModel validators

**Checkpoint**: Config schema complete and validated - US1/US2 can proceed in parallel ✅

---

## Phase 3: User Story 1 - Configuration File Support (Priority: P1) 🎯 MVP

**Goal**: Users can store doc settings in `.ansibledoctor.yml` file, eliminating repetitive CLI flags

**Independent Test**: Create `.ansibledoctor.yml` with `output_format: html`, run `ansible-doctor generate .`, verify HTML generated without `--format` flag

### Tests for User Story 1 (TDD RED → GREEN)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Unit tests for config discovery in `tests/unit/test_config_loader.py`
  - Test find_config_file() discovers `.ansibledoctor.yml` in current dir
  - Test find_config_file() discovers `.ansibledoctor.yaml` (alternate extension)
  - Test find_config_file() discovers config in parent directory
  - Test find_config_file() returns None when no config exists
  - Test nearest config wins (role dir over parent dir)

- [X] T008 [P] [US1] Unit tests for config loading in `tests/unit/test_config_loader.py`
  - Test load_config() parses valid YAML successfully
  - Test load_config() raises clear error on YAML syntax error (with line number)
  - Test load_config() raises clear error on Pydantic validation error
  - Test load_config() handles missing optional fields (uses defaults)

- [X] T009 [P] [US1] Integration tests in `tests/integration/test_config_integration.py`
  - Test CLI reads config from `.ansibledoctor.yml` (output_format: html)
  - Test CLI flags override config file (config says html, CLI says rst → rst wins)
  - Test invalid config shows clear error before generation starts

### Implementation for User Story 1

- [X] T010 [US1] Implement find_config_file() in `ansibledoctor/config/loader.py`
  - Search current directory for `.ansibledoctor.yml` or `.ansibledoctor.yaml`
  - If not found, search parent directories up to filesystem root
  - Return Path object or None

- [X] T011 [US1] Implement load_config() in `ansibledoctor/config/loader.py`
  - Load YAML file using ruamel.yaml
  - Parse into ConfigModel (Pydantic validation)
  - Catch YAMLError and show file location + line number
  - Catch ValidationError and show field names + expected types

- [X] T012 [US1] Implement merge_config() in `ansibledoctor/config/loader.py`
  - Merge priority: CLI flags > config file > defaults
  - Return final ConfigModel with all None fields filled

- [X] T013 [US1] Add config loading to `generate` command in `ansibledoctor/cli/__init__.py`
  - Call find_config_file() from role_path directory
  - If found, load_config() and merge with CLI flags
  - Use merged config for OutputFormat, output path, template options
  - Log config file location when used (INFO level)

- [X] T014 [US1] Add `config show` command in `ansibledoctor/cli/__init__.py`
  - Display effective configuration (merged defaults + file + CLI)
  - Show config file location if loaded
  - Format as YAML for readability

- [X] T015 [US1] Add `config validate` command in `ansibledoctor/cli/__init__.py`
  - Find config file, load and validate
  - Show success message or validation errors
  - Exit code 0 for valid, 1 for invalid

**Checkpoint**: `.ansibledoctor.yml` support complete - users can set persistent doc settings ✅ (v0.4.0-alpha.1 released)

---

## Phase 4: User Story 2 - Watch Mode Auto-Regeneration (Priority: P2)

**Goal**: Documentation auto-regenerates when role files change, enabling real-time preview during development

**Independent Test**: Run `ansible-doctor watch /role`, modify `defaults/main.yml`, verify docs regenerate within 2 seconds

### Tests for User Story 2 (TDD RED → GREEN)

- [X] T016 [P] [US2] Unit tests for debouncer in `tests/unit/test_debouncer.py`
  - Test single file change triggers callback after quiet period (500ms)
  - Test burst of 10 changes debounces to single callback
  - Test multiple files changing simultaneously debounces correctly
  - Test clear() cancels pending callback

- [X] T017 [P] [US2] Unit tests for file monitor in `tests/unit/test_monitor.py`
  - Test monitor detects file modifications in `defaults/`
  - Test monitor detects new files created in `tasks/`
  - Test monitor ignores excluded patterns (e.g., `.git/`, `*.pyc`)
  - Test monitor handles config file changes (`.ansibledoctor.yml`)

- [X] T018 [P] [US2] Integration tests in `tests/integration/test_watch_mode.py`
  - Test watch command starts and monitors role directory
  - Test modifying `defaults/main.yml` triggers regeneration
  - Test generation errors don't crash watch mode (displays error, continues)
  - Test Ctrl+C exits gracefully
  - 9 integration tests: file monitoring, debouncing, exclusions, config changes, graceful shutdown, error handling

### Implementation for User Story 2

- [X] T019 [US2] Implement Debouncer class in `ansibledoctor/watcher/debouncer.py`
  - __init__(callback, delay=0.5) - callback function, delay in seconds
  - trigger() method - schedule callback after delay, cancel previous
  - clear() method - cancel pending callback
  - Use threading.Timer for delayed execution

- [X] T020 [US2] Implement FileChangeHandler in `ansibledoctor/watcher/handler.py`
  - Extend watchdog.events.FileSystemEventHandler
  - on_modified(), on_created() methods filter relevant files
  - Call debouncer.trigger() on file events
  - Ignore directories, .pyc, __pycache__, .git

- [X] T021 [US2] Implement WatchMonitor class in `ansibledoctor/watcher/monitor.py`
  - __init__(role_path, on_change_callback) - setup watchdog observer
  - Watch paths: meta/, defaults/, vars/, tasks/, handlers/, .ansibledoctor.yml
  - start() - begin monitoring
  - stop() - graceful shutdown
  - Use watchdog.observers.Observer with FileChangeHandler

- [X] T022 [US2] Implement regeneration callback in `ansibledoctor/cli/__init__.py`
  - regenerate_docs() function inside watch command
  - Calls _parse_role_for_generation() and renderer.render()
  - Catches exceptions, logs errors with timestamps, doesn't propagate (watch continues)
  - Writes to output file or stdout

- [X] T023 [US2] Add `watch` command in `ansibledoctor/cli/__init__.py`
  - New Click command: `ansible-doctor watch <role-path>`
  - Loads config from role directory (integrates US1)
  - Creates WatchMonitor with regeneration callback
  - Prints "Watching <path>... Press Ctrl+C to stop"
  - Handles KeyboardInterrupt for graceful exit
  - Displays generation status on each trigger with timestamps

- [X] T024 [US2] Add signal handling for graceful shutdown
  - Registers SIGINT/SIGTERM handlers using signal.signal()
  - Calls monitor.stop() before exit
  - Prints "Watch stopped" message
  - Also handles KeyboardInterrupt exception as fallback

**Checkpoint**: Watch mode complete - docs auto-regenerate on file changes ✅ (US2 complete)

---

## Phase 5: User Story 3 - Config File Discovery & Validation (Priority: P3)

**Goal**: Config discovery in parent directories + validation CLI for catching errors early

**Independent Test**: Place `.ansibledoctor.yml` in parent dir, run command in subdirectory, verify config is used

### Tests for User Story 3 (TDD RED → GREEN)

- [X] T025 [P] [US3] Unit tests for parent directory discovery in `tests/unit/test_config_loader.py`
  - Test config found in grandparent directory (../../.ansibledoctor.yml)
  - Test config in role dir overrides parent dir (nearest wins)
  - Test discovery stops at filesystem root
  - **Complete**: All 8 config discovery tests passing

- [X] T026 [P] [US3] Integration tests for validation in `tests/integration/test_config_integration.py`
  - Test `config validate` command with valid config (exit code 0)
  - Test `config validate` command with invalid config (exit code 1, error shown)
  - Test `config show` displays merged config from parent dir
  - **Complete**: 12 integration tests passing, Unicode encoding fixed for Windows

### Implementation for User Story 3

- [X] T027 [US3] Update find_config_file() for parent directory search
  - Walk up directory tree: current → parent → grandparent → root
  - Check for .ansibledoctor.yml and .ansibledoctor.yaml at each level
  - Return first found (nearest wins)
  - Already implemented in T010, enhance tests here
  - **Complete**: Already implemented and tested with T025/T026

- [X] T028 [US3] Add validation output formatting to `config validate` command
  - Print "[VALID] Config valid: <path>" on success
  - Print "[INVALID] Config invalid: <path>" + errors on failure
  - Show line numbers for YAML syntax errors
  - Show field names for schema validation errors
  - **Complete**: Enhanced error output with line numbers and field names

- [X] T029 [US3] Add effective config display to `config show` command
  - Show config file path if loaded (or "Using defaults")
  - Display merged config as formatted YAML
  - Show which settings come from file vs defaults
  - Show resolved paths (absolute, not relative)
  - **Complete**: All features implemented and tested

**Checkpoint**: Config discovery complete - works like Git config (nearest file wins)

---

## Phase 6: Documentation & Polish

**Purpose**: Complete Feature 003 with documentation and final validation

- [X] T030 [P] Update README.md with config file examples
  - Section: "Configuration File Support"
  - Show .ansibledoctor.yml example with all supported keys
  - Document config discovery (current dir → parent dirs)
  - Document CLI flag override behavior
  - **Complete**: All sections already present and comprehensive

- [X] T031 [P] Update README.md with watch mode examples
  - Section: "Watch Mode"
  - Show `ansible-doctor watch <role-path>` usage
  - Explain debouncing and monitored paths
  - Show expected output during watch
  - **Complete**: Watch mode fully documented with examples

- [X] T032 Update CHANGELOG.md with v0.4.0 section
  - Add [0.4.0-alpha.3] section with full release notes
  - List US1: Config file support (.ansibledoctor.yml)
  - List US2: Watch mode with auto-regeneration
  - List US3: Config discovery & validation CLI
  - Note: Achieves 100% role-level parity with original ansible-doctor
  - **Complete**: v0.4.0-alpha.3 section added with comprehensive details

- [X] T033 [P] Create docs/CONFIG_GUIDE.md
  - Comprehensive config file guide
  - All supported keys with descriptions and examples
  - Config priority explanation (CLI > file > defaults)
  - Migration guide from original ansible-doctor config
  - **Complete**: 472-line comprehensive guide created

- [X] T034 [P] Create migration guide from original ansible-doctor
  - Config file compatibility notes
  - CLI flag mapping (if any differences)
  - Feature comparison table
  - **Complete**: Integrated into CONFIG_GUIDE.md "Migration" section

- [X] T035 Run full test suite and verify coverage
  - Target: 80%+ coverage (constitutional requirement)
  - pytest tests/ --cov=ansibledoctor --cov-report=term
  - Fix any failing tests
  - Verify all 3 user stories work independently
  - **Complete**: 652 tests passing, 81% coverage (exceeds 80% target) ✅

- [X] T036 Update pyproject.toml version to 0.4.0
  - Bump version: 0.3.0 → 0.4.0 (now at 0.5.1)
  - Ensure CHANGELOG.md has [0.4.0] section with today's date
  - Commit: "chore(release): bump version to 0.4.0"

- [X] T037 Create git tag 0.4.0
  - Tag message: "Release 0.4.0 - ansible-doctor Role Parity Complete"
  - No 'v' prefix per Article XI (constitution)
  - Annotated tag with feature summary

---

<!-- Side work entries have been moved to the end of the file and renumbered as T038-T040. -->


## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T004) complete - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T005-T006) complete
- **User Story 2 (Phase 4)**: Depends on Foundational (T005-T006) complete - can run parallel with US1
- **User Story 3 (Phase 5)**: Depends on US1 (T007-T015) complete - extends config loader
- **Documentation (Phase 6)**: Depends on all US complete

### TDD Workflow (per user story)

1. Write tests FIRST (T007-T009, T016-T018, T025-T026)
2. Run tests → verify RED (all fail)
3. Implement features (T010-T015, T019-T024, T027-T029)
4. Run tests → verify GREEN (all pass)
5. Refactor if needed

### Parallel Opportunities

- **Phase 1**: T001, T002, T003, T004 (all [P])
- **Phase 2**: T006 can run parallel with T005 development
- **After Phase 2**: US1 (Phase 3) and US2 (Phase 4) can start in parallel
- **Phase 6**: T030, T031, T033, T034 (all [P])

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 (Setup): T001-T004
2. Complete Phase 2 (Foundational): T005-T006
3. Complete Phase 3 (US1): T007-T015
4. **STOP and VALIDATE**: Test config file support works
5. Can release v0.4.0-beta with US1 only

### Full Feature (All 3 Stories)

1. Complete Setup + Foundational (T001-T006)
2. Complete US1 (T007-T015) → Config files work
3. Complete US2 (T016-T024) → Watch mode works
4. Complete US3 (T025-T029) → Enhanced discovery/validation
5. Complete Documentation (T030-T037) → Release v0.4.0

### Timeline Estimate

- Phase 1 (Setup): 1 hour
- Phase 2 (Foundational): 3 hours
- Phase 3 (US1 Config): 8 hours
- Phase 4 (US2 Watch): 10 hours
- Phase 5 (US3 Discovery): 4 hours
- Phase 6 (Docs/Polish): 4 hours
- **Total: ~30 hours (4 days)**

---

## Success Criteria

- [X] All tests passing (593 baseline + ~30 new = 623 tests) → **Now 1010+ tests!**
- [X] Coverage ≥80% maintained → **83% coverage**
- [X] `.ansibledoctor.yml` config files work (US1)
- [X] `ansible-doctor watch` auto-regenerates (US2)
- [X] Config discovered in parent directories (US3)
- [X] `config validate` and `config show` commands work (US3)
- [X] CLI flags override config file
- [X] Documentation complete (README, CHANGELOG, CONFIG_GUIDE, MIGRATION)
- [X] v0.4.0 tag created per Article XI → **Version now 0.5.1**

---

## Notes

- **TDD Required**: Article III (constitution) mandates Red-Green-Refactor cycle
- **[P] tasks**: Can run in parallel (different files)
- **[US#] labels**: Trace tasks to user stories
- **Checkpoints**: Validate each story independently before proceeding
- **Commit frequency**: After each task or logical group (T010-T012, then commit)

---

## Side work: 2025-11-30 (Dev tools & infra)

- [x] T038 [P] Added `scripts/run_cli_main.py` and `scripts/run_tests.*` to simplify running CLI and tests from source
- [x] T039 [P] Added `pre-commit` config `.pre-commit-config.yaml` and CI pre-commit job to validate formatting and changelog on PRs
- [x] T040 [P] Migrated dev dependencies to `tool.poetry.group.dev.dependencies`, regenerated `poetry.lock` and verified `poetry install --with dev` works

