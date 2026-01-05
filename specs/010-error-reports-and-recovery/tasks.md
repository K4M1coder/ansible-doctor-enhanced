# Tasks: Error Reports & Recovery

**Input**: Design documents from `/specs/010-error-reports-and-recovery/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are MANDATORY per Constitution §III (TDD). All tests must be written BEFORE implementation (Red-Green-Refactor).

**Cross-Spec Dependencies**:
- **Extends**: Existing `ansibledoctor/exceptions.py` exception hierarchy
- **Consumed by Spec 009**: ErrorAggregator provides error summaries for ExecutionReport
- **Provides**: ErrorEntry, ErrorAggregator, RecoverySuggestions models for all specs

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- File paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create exceptions module extensions: `ansibledoctor/exceptions/codes.py`, `aggregator.py`, `recovery.py`
- [ ] T002 [P] Create error report model: `ansibledoctor/models/error_report.py`
- [ ] T003 [P] Create SARIF formatter: `ansibledoctor/utils/sarif.py`
- [ ] T004 [P] Create test fixtures directory: `tests/fixtures/error_scenarios/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Define ErrorCode enum with hierarchical numbering (E1xx=parsing, E2xx=validation, E3xx=generation, E4xx=io) in `ansibledoctor/exceptions/codes.py`
- [ ] T006 [P] Create ErrorEntry model in `ansibledoctor/models/error_report.py` with code, severity, file, line, column, message
- [ ] T007 [P] Create ErrorReport aggregate model in `ansibledoctor/models/error_report.py`
- [ ] T008 Create RecoverySuggestion database structure (JSON/YAML) with error code mappings
- [X] T009 Add error_code property to base AnsibleDoctorError class in `ansibledoctor/exceptions/__init__.py`
- [X] T010 Map existing exceptions to error codes (ParsingError→E1xx, ValidationError→E2xx, TemplateError→E3xx)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Aggregated Error Report (Priority: P1) 🎯 MVP

**Goal**: Enable aggregated error collection and reporting for multi-file processing

**Independent Test**: Run `ansible-doctor generate project/` with multiple errors → Consolidated error report at end showing all issues grouped by file

### Tests for User Story 1 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Unit test for ErrorAggregator.add_error() with deduplication in `tests/unit/test_aggregator.py`
- [X] T012 [P] [US1] Unit test for ErrorAggregator bounded memory (cap at 1000 errors) in `tests/unit/test_aggregator.py`
- [X] T013 [P] [US1] Unit test for ErrorReport.to_text() formatting in `tests/unit/test_error_report.py`
- [X] T014 [P] [US1] Unit test for ErrorReport.to_json() serialization in `tests/unit/test_error_report.py`
- [ ] T015 [P] [US1] Integration test for multi-file error collection in `tests/integration/test_error_reporting.py`
- [ ] T016 [P] [US1] Integration test for error grouping by file in `tests/integration/test_error_reporting.py`

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement ErrorAggregator class with add_error/add_warning methods in `ansibledoctor/exceptions/aggregator.py`
- [X] T018 [US1] Implement deduplication logic using ErrorEntry.hash in `ansibledoctor/exceptions/aggregator.py`
- [X] T019 [US1] Implement memory-bounded collection (max 1000 errors) with overflow handling in `ansibledoctor/exceptions/aggregator.py`
- [X] T020 [US1] Implement ErrorReport.to_text() for human-readable terminal output in `ansibledoctor/models/error_report.py`
- [X] T021 [US1] Implement ErrorReport.to_json() with Pydantic serialization in `ansibledoctor/models/error_report.py`
- [X] T022 [US1] Add `--error-format {text,json,sarif}` CLI flag in `ansibledoctor/cli/__init__.py`
- [X] T023 [US1] Add `--error-output FILE` CLI flag for report file output in `ansibledoctor/cli/__init__.py`
- [X] T024 [US1] Integrate ErrorAggregator into CLI command lifecycle in `ansibledoctor/cli/__init__.py`
- [X] T025 [US1] Display aggregated error report at command completion in CLI in `ansibledoctor/cli/__init__.py`

**Checkpoint**: User Story 1 complete - aggregated error reports with text/JSON output

---

## Phase 4: User Story 2 - Intelligent Recovery Suggestions (Priority: P1) 🎯 MVP

**Goal**: Provide context-aware, actionable recovery suggestions for each error type

**Independent Test**: Trigger YAML syntax error → Error message includes specific suggestion like "Check indentation at line X"

### Tests for User Story 2 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US2] Unit test for recovery suggestion lookup by error code in `tests/unit/test_recovery_suggestions.py`
- [ ] T027 [P] [US2] Unit test for suggestion fallback when code unknown in `tests/unit/test_recovery_suggestions.py`
- [ ] T028 [P] [US2] Unit test for multi-step recovery suggestions in `tests/unit/test_recovery_suggestions.py`
- [ ] T029 [P] [US2] Integration test for YAML syntax error with suggestion in `tests/integration/test_error_reporting.py`
- [ ] T030 [P] [US2] Integration test for missing file error with template suggestion in `tests/integration/test_error_reporting.py`

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create recovery suggestion database (JSON/YAML) with mappings for E1xx-E4xx codes in `ansibledoctor/exceptions/recovery_db.json`
- [ ] T032 [US2] Implement RecoverySuggestionProvider with lookup and fallback logic in `ansibledoctor/exceptions/recovery.py`
- [ ] T033 [US2] Add common recovery suggestions for YAML errors (E101-E103) to database
- [ ] T034 [US2] Add common recovery suggestions for validation errors (E201-E203) to database
- [ ] T035 [US2] Add common recovery suggestions for generation errors (E301-E303) to database
- [ ] T036 [US2] Add common recovery suggestions for I/O errors (E401-E403) to database
- [ ] T037 [US2] Integrate RecoverySuggestionProvider into ErrorAggregator.add_error() in `ansibledoctor/exceptions/aggregator.py`
- [ ] T038 [US2] Include recovery suggestions in error output (text, JSON, SARIF) in error report formatters

**Checkpoint**: User Story 2 complete - intelligent recovery suggestions for all error types

---

## Phase 5: User Story 3 - Graceful Degradation (Priority: P1) 🎯 MVP

**Goal**: Continue processing when individual files fail to enable partial documentation generation

**Independent Test**: Run `ansible-doctor generate project/` with 1 broken role among 10 → 9 roles documented, error report shows failure

### Tests for User Story 3 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T039 [P] [US3] Integration test for partial success with one failed role in `tests/integration/test_error_reporting.py`
- [ ] T040 [P] [US3] Integration test for `--continue-on-error` flag behavior in `tests/integration/test_error_reporting.py`
- [ ] T041 [P] [US3] Integration test for partial success reporting (N of M files) in `tests/integration/test_error_reporting.py`
- [ ] T042 [P] [US3] Integration test for atomic file writes (no half-written docs) in `tests/integration/test_error_reporting.py`

### Implementation for User Story 3

- [ ] T043 [P] [US3] Add `--continue-on-error` CLI flag in `ansibledoctor/cli/__init__.py`
- [ ] T044 [US3] Implement try-catch wrappers in parser modules to capture errors without stopping in parser modules
- [ ] T045 [US3] Implement try-catch wrappers in generator modules to capture errors without stopping in generator modules
- [ ] T046 [US3] Track successful vs failed files in execution context during processing
- [ ] T047 [US3] Add partial_success field to ErrorReport model in `ansibledoctor/models/error_report.py`
- [ ] T048 [US3] Display "N of M files processed successfully" in error report summary
- [ ] T049 [US3] Ensure exit code 1 even with partial success when errors occurred

**Checkpoint**: User Story 3 complete - graceful degradation with partial documentation

---

## Phase 6: User Story 4 - Error Classification & Codes (Priority: P2)

**Goal**: Provide unique error codes for documentation lookup and suppression configuration

**Independent Test**: Trigger error → Error message includes code like "E101" with documentation URL

### Tests for User Story 4 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T050 [P] [US4] Unit test for error code uniqueness validation in `tests/unit/test_error_codes.py`
- [ ] T051 [P] [US4] Unit test for `--ignore` flag with error code suppression in `tests/unit/test_error_codes.py`
- [ ] T052 [P] [US4] Integration test for config file `ignore_errors` setting in `tests/integration/test_error_reporting.py`
- [ ] T053 [P] [US4] Integration test for suppressed error count reporting in `tests/integration/test_error_reporting.py`

### Implementation for User Story 4

- [ ] T054 [P] [US4] Add documentation_url field to RecoverySuggestion model in `ansibledoctor/exceptions/recovery.py`
- [ ] T055 [US4] Create error code documentation URLs for all E1xx-E4xx codes in recovery database
- [ ] T056 [US4] Add `--ignore E001,W002` CLI flag for error suppression in `ansibledoctor/cli/__init__.py`
- [ ] T057 [US4] Add `ignore_errors: [E001]` config file support in `.ansibledoctor.yml` parser
- [ ] T058 [US4] Implement error suppression logic in ErrorAggregator.add_error()
- [ ] T059 [US4] Display suppressed error count separately in error report summary
- [ ] T060 [US4] Include error code in all error output formats (text: "[E101]", JSON: "code": "E101")

**Checkpoint**: User Story 4 complete - error codes with suppression and documentation URLs

---

## Phase 7: User Story 5 - IDE-Friendly Error Output (Priority: P2)

**Goal**: Enable IDE integration with clickable file:line:column error references and SARIF format

**Independent Test**: Run in VS Code terminal with error → Output format allows clicking to navigate to file location

### Tests for User Story 5 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T061 [P] [US5] Unit test for SARIF 2.1.0 schema validation in `tests/unit/test_sarif.py`
- [ ] T062 [P] [US5] Unit test for file:line:column format generation in `tests/unit/test_sarif.py`
- [ ] T063 [P] [US5] Unit test for error sorting by file then line in `tests/unit/test_aggregator.py`
- [ ] T064 [P] [US5] Integration test for SARIF output with VS Code Problems panel in `tests/integration/test_error_reporting.py`

### Implementation for User Story 5

- [ ] T065 [P] [US5] Implement SARIFFormatter.format() with SARIF 2.1.0 structure in `ansibledoctor/utils/sarif.py`
- [ ] T066 [US5] Implement SARIFFormatter._create_result() for ErrorEntry conversion in `ansibledoctor/utils/sarif.py`
- [ ] T067 [US5] Implement SARIFFormatter._create_location() with physicalLocation in `ansibledoctor/utils/sarif.py`
- [ ] T068 [US5] Add SARIF tool driver metadata (name, version, informationUri) in `ansibledoctor/utils/sarif.py`
- [ ] T069 [US5] Implement ErrorReport.to_sarif() using SARIFFormatter in `ansibledoctor/models/error_report.py`
- [ ] T070 [US5] Implement error sorting by file, then line number in ErrorAggregator.generate_report()
- [ ] T071 [US5] Format text errors as `file:line:column: error[CODE]: message` for IDE terminal parsing

**Checkpoint**: User Story 5 complete - IDE-friendly SARIF output with clickable references

---

## Phase 8: User Story 6 - Error Context Preservation (Priority: P3)

**Goal**: Provide full error context (stack traces, surrounding code) for debugging complex issues

**Independent Test**: Run with `--verbose` and trigger error → Output includes stack trace and source snippet

### Tests for User Story 6 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T072 [P] [US6] Integration test for `--verbose` stack trace output in `tests/integration/test_error_reporting.py`
- [ ] T073 [P] [US6] Integration test for source context lines (3 lines around error) in `tests/integration/test_error_reporting.py`
- [ ] T074 [P] [US6] Integration test for template error with highlighted snippet in `tests/integration/test_error_reporting.py`

### Implementation for User Story 6

- [ ] T075 [P] [US6] Add stack_trace field to ErrorEntry model in `ansibledoctor/models/error_report.py`
- [ ] T076 [US6] Capture stack trace in ErrorAggregator.add_error() when verbose mode enabled
- [ ] T077 [US6] Implement source line extraction (3 lines around error) in error collection
- [ ] T078 [US6] Display stack traces in verbose text output format
- [ ] T079 [US6] Include stack traces in JSON output when present
- [ ] T080 [US6] Add `--debug` flag for full exception chain display in `ansibledoctor/cli/__init__.py`

**Checkpoint**: User Story 6 complete - full error context for debugging

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, performance optimization, and final integration

- [ ] T081 Create comprehensive error code documentation at docs/error-codes.md with examples
- [ ] T082 [P] Add docstrings to all error handling classes and functions
- [ ] T083 [P] Update README.md with error reporting examples and CLI flags
- [ ] T084 [P] Create CI/CD integration guide in docs/ with GitHub Actions examples
- [ ] T085 Update CLI `--help` output with all error reporting flags
- [ ] T086 Performance optimization: ensure error report generation <50ms overhead
- [ ] T087 [P] Add error scenario fixtures (invalid YAML, missing files, bad annotations) in `tests/fixtures/error_scenarios/`
- [ ] T088 Integration with Spec 009 ExecutionReport (link via correlation_id)
- [ ] T089 Backward compatibility testing: ensure existing error messages unchanged by default
- [ ] T090 Add CHANGELOG.md entry with Added: Aggregated error reports, SARIF output, error codes

---

## Dependencies & Parallelization

### Parallel Execution Opportunities

**After T010 (Foundational Complete)**:
- User Story 1, 2, 3 can be worked on in parallel by different developers
- User Story 4, 5, 6 can start after US1 (ErrorAggregator) is complete

**Within Each User Story**:
- All test tasks marked [P] can run in parallel
- US1 implementation tasks T017-T021 can run in parallel (different files)
- US2 database population tasks T033-T036 can run in parallel

### Critical Path

```
T001-T004 (Setup) → T005-T010 (Foundation) → T011-T025 (US1 MVP) → T026-T038 (US2 MVP) → T039-T049 (US3 MVP)
```

MVP delivery requires completing User Stories 1, 2, and 3 (aggregation + suggestions + graceful degradation).

---

## Suggested MVP Scope

**Minimum Viable Product** (first release):
- ✅ User Story 1: Aggregated Error Report
- ✅ User Story 2: Intelligent Recovery Suggestions
- ✅ User Story 3: Graceful Degradation
- ⏭️ User Story 4-6: Can be delivered in subsequent releases

**Estimated Effort**:
- Setup + Foundation: 10 hours
- User Story 1 (MVP): 14 hours
- User Story 2 (MVP): 12 hours
- User Story 3 (MVP): 10 hours
- User Story 4: 8 hours
- User Story 5: 10 hours
- User Story 6: 6 hours
- Polish: 6 hours
- **Total: 76 hours (~9.5 days for 1 developer)**

---

## Implementation Strategy

1. **TDD Approach**: Write tests first (T011-T016 before T017-T025)
2. **Incremental Delivery**: Complete US1+US2+US3 for MVP, then iterate
3. **Backward Compatibility**: Existing error behavior unchanged without new flags
4. **Performance Testing**: Validate <50ms error report overhead with benchmarks
5. **SARIF Validation**: Use schema validation in tests to ensure IDE compatibility (A15 remediation)
6. **Regression Testing**: Verify existing Spec 001-008 error handling unchanged

---

## Backward Compatibility Regression Tasks

These tasks ensure existing functionality is not broken:

- [ ] T091 [REGRESSION] Run existing test suites to verify no regressions
- [ ] T092 [REGRESSION] Verify default error output format unchanged without new flags
- [ ] T093 [REGRESSION] Test that existing exception messages remain identical
- [ ] T094 [A15] Add SARIF 2.1.0 schema validation test in `tests/integration/test_sarif_validation.py`

---

## Success Criteria

- ✅ All 90 tasks completed with passing tests
- ✅ Test coverage >85% (90% for error aggregation logic)
- ✅ Error report generation overhead <50ms
- ✅ All constitution gates pass (TDD, CLI-first, error codes stable across versions)
- ✅ Backward compatible (existing error messages unchanged by default)
- ✅ SARIF 2.1.0 schema validation passes
- ✅ Documentation complete (CLI help, error code docs, CI/CD guide)
- ✅ IDE integration verified (VS Code Problems panel)

**Status**: Ready for implementation
