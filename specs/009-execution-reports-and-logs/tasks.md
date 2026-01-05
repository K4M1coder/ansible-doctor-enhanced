# Tasks: Execution Reports & Structured Logging

**Input**: Design documents from `/specs/009-execution-reports-and-logs/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: Tests are MANDATORY per Constitution §III (TDD). All tests must be written BEFORE implementation (Red-Green-Refactor).

**Cross-Spec Dependencies**:
- **Consumes Spec 010**: ErrorAggregator from `ansibledoctor/exceptions/aggregator.py` for error summaries
- **Extends**: Existing `ansibledoctor/utils/logging.py` structlog infrastructure
- **Consumed by**: Specs 011, 012, 013 for metrics integration

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- File paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create reporting module structure: `ansibledoctor/reporting/__init__.py`
- [X] T002 [P] Create models directory structure for execution models
- [X] T003 [P] Create test structure: `tests/unit/models/`, `tests/unit/reporting/`, `tests/integration/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create ExecutionMetrics model in `ansibledoctor/models/execution_report.py` with Pydantic schema
- [X] T005 [P] Create ExecutionWarning model in `ansibledoctor/models/execution_warning.py`
- [X] T006 [P] Create ExecutionError model in `ansibledoctor/models/execution_error.py` with suggestion field
- [X] T007 Create ExecutionReport aggregate model in `ansibledoctor/models/execution_report.py`
- [X] T008 [P] Define ReportGenerator protocol in `ansibledoctor/reporting/protocols.py`
- [X] T009 [P] Define MetricsCollector protocol in `ansibledoctor/reporting/protocols.py`
- [X] T010 Create correlation ID utilities in `ansibledoctor/utils/correlation.py` with UUID4 generation
- [X] T011 Add exit code property to exception classes in `ansibledoctor/exceptions.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Execution Report (Priority: P1) 🎯 MVP

**Goal**: Enable structured execution reports for CI/CD integration with status, metrics, and errors

**Independent Test**: Run `ansible-doctor generate role/ --report report.json` → JSON file created with complete execution data

### Tests for User Story 1 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Unit test for ExecutionReport serialization to JSON in `tests/unit/models/test_execution_report.py`
- [X] T013 [P] [US1] Unit test for ExecutionReport model validation (required fields, status enum) in `tests/unit/models/test_execution_report.py`
- [X] T014 [P] [US1] Unit test for report with warnings (status="completed_with_warnings") in `tests/unit/models/test_execution_report.py`
- [X] T015 [P] [US1] Unit test for report with errors (status="failed") in `tests/unit/models/test_execution_report.py`
- [X] T016 [P] [US1] Integration test for CLI `--report report.json` flag creates file in `tests/integration/test_report_generation_cli.py`
- [X] T017 [P] [US1] Integration test for report contains correct status after successful run in `tests/integration/test_report_generation_cli.py`
- [X] T018 [P] [US1] Integration test for report contains warnings array when warnings occur in `tests/integration/test_report_generation_cli.py`
- [X] T019 [P] [US1] Integration test for report contains errors array when errors occur in `tests/integration/test_report_generation_cli.py`

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement JSON serializer in `ansibledoctor/reporting/serializers.py` with ISO 8601 datetime formatting
- [X] T021 [P] [US1] Implement text serializer for human-readable reports in `ansibledoctor/reporting/serializers.py`
- [X] T022 [US1] Implement ReportGenerator class in `ansibledoctor/reporting/report_generator.py` (depends on T020, T021)
- [X] T023 [US1] Implement `generate()` method to create ExecutionReport from context in `ansibledoctor/reporting/report_generator.py`
- [X] T024 [US1] Implement `write_report()` method with atomic file write (temp + rename) in `ansibledoctor/reporting/report_generator.py`
- [X] T025 [US1] Add `--report PATH` flag to CLI in `ansibledoctor/cli/__init__.py`
- [X] T026 [US1] Add `--report-format {json,text,summary}` flag to CLI in `ansibledoctor/cli/__init__.py`
- [X] T027 [US1] Integrate report generation at command completion in CLI entry points in `ansibledoctor/cli/__init__.py`
- [X] T028 [US1] Add report file path validation and error handling in `ansibledoctor/cli/__init__.py`

**Checkpoint**: User Story 1 complete - structured JSON/text reports can be generated with `--report` flag

---

## Phase 4: User Story 2 - Performance Metrics Collection (Priority: P1) 🎯 MVP

**Goal**: Collect and display timing metrics, file counts, and throughput data for performance visibility

**Independent Test**: Run `ansible-doctor generate project/ --verbose` → Console shows timing per phase and file counts

### Tests for User Story 2 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T029 [P] [US2] Unit test for MetricsCollector phase timing in `tests/unit/reporting/test_metrics_collector.py`
- [ ] T030 [P] [US2] Unit test for MetricsCollector counter increments in `tests/unit/reporting/test_metrics_collector.py`
- [ ] T031 [P] [US2] Unit test for nested phase timing (parsing → file_parsing) in `tests/unit/reporting/test_metrics_collector.py`
- [ ] T032 [P] [US2] Unit test for metrics timing accuracy (<5% error) using mocked time in `tests/unit/reporting/test_metrics_collector.py`
- [ ] T033 [P] [US2] Integration test for metrics in report JSON structure in `tests/integration/test_metrics_collection_e2e.py`
- [ ] T034 [P] [US2] Integration test for verbose mode displays phase timing in `tests/integration/test_metrics_collection_e2e.py`

### Implementation for User Story 2

- [ ] T035 [P] [US2] Implement MetricsCollector class with timing context manager in `ansibledoctor/reporting/metrics_collector.py`
- [ ] T036 [US2] Implement `start_phase()` and `end_phase()` using `time.perf_counter()` in `ansibledoctor/reporting/metrics_collector.py`
- [ ] T037 [US2] Implement `increment_counter()` for file/role/collection counts in `ansibledoctor/reporting/metrics_collector.py`
- [ ] T038 [US2] Implement `get_metrics()` to return ExecutionMetrics in `ansibledoctor/reporting/metrics_collector.py`
- [ ] T039 [US2] Add metrics collection hooks to parsing phase in existing parser modules
- [ ] T040 [US2] Add metrics collection hooks to rendering phase in existing generator modules
- [ ] T041 [US2] Add metrics collection hooks to writing phase in existing file output code
- [ ] T042 [US2] Enhance `--verbose` mode to display phase timing in console output in `ansibledoctor/cli/__init__.py`
- [ ] T043 [US2] Add metrics summary to report generation in `ansibledoctor/reporting/report_generator.py`

**Checkpoint**: User Story 2 complete - performance metrics collected and displayed in verbose mode and reports

---

## Phase 5: User Story 3 - Correlation ID Tracing (Priority: P2)

**Goal**: Enable request tracing across nested operations with correlation IDs in all log entries

**Independent Test**: Run `ansible-doctor generate project/` with JSON logging → All logs share same correlation_id

### Tests for User Story 3 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T044 [P] [US3] Unit test for correlation ID generation (UUID4 format) in `tests/unit/utils/test_correlation.py`
- [ ] T045 [P] [US3] Unit test for correlation ID propagation via contextvars in `tests/unit/utils/test_correlation.py`
- [ ] T046 [P] [US3] Unit test for custom correlation ID acceptance in `tests/unit/utils/test_correlation.py`
- [ ] T047 [P] [US3] Integration test for correlation ID in all log entries in `tests/integration/test_correlation_propagation.py`
- [ ] T048 [P] [US3] Integration test for correlation ID in report JSON in `tests/integration/test_correlation_propagation.py`
- [ ] T049 [P] [US3] Integration test for nested operations share parent correlation ID in `tests/integration/test_correlation_propagation.py`

### Implementation for User Story 3

- [ ] T050 [P] [US3] Implement correlation ID generation function in `ansibledoctor/utils/correlation.py`
- [ ] T051 [US3] Implement contextvars binding for correlation ID in `ansibledoctor/utils/correlation.py`
- [ ] T052 [US3] Implement correlation ID retrieval function in `ansibledoctor/utils/correlation.py`
- [ ] T053 [US3] Add `--correlation-id ID` CLI flag in `ansibledoctor/cli/__init__.py`
- [ ] T054 [US3] Bind correlation ID at command start in CLI entry point in `ansibledoctor/cli/__init__.py`
- [ ] T055 [US3] Enhance structlog binding to include correlation_id in `ansibledoctor/utils/logging.py`
- [ ] T056 [US3] Add correlation_id to ExecutionReport in `ansibledoctor/reporting/report_generator.py`
- [ ] T057 [US3] Ensure correlation ID propagates to nested operations (role → collection → project)

**Checkpoint**: User Story 3 complete - correlation IDs trace execution across nested operations

---

## Phase 6: User Story 4 - Aggregated Error Summary (Priority: P2)

**Goal**: Provide consolidated error/warning summaries at command completion for large projects

**Cross-Spec Dependency**: This story CONSUMES `ErrorAggregator` from Spec 010 (`ansibledoctor/exceptions/aggregator.py`).
If Spec 010 is not yet implemented, use a simplified local implementation that can be replaced later.

**Independent Test**: Run `ansible-doctor generate project/` with errors → End of output shows summary table

### Tests for User Story 4 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T058 [P] [US4] Unit test for error aggregation by file in `tests/unit/reporting/test_report_generator.py`
- [ ] T059 [P] [US4] Unit test for warning aggregation by file in `tests/unit/reporting/test_report_generator.py`
- [ ] T060 [P] [US4] Unit test for summary text formatting in `tests/unit/reporting/test_serializers.py`
- [ ] T061 [P] [US4] Integration test for console summary displays error counts in `tests/integration/test_report_generation_cli.py`
- [ ] T062 [P] [US4] Integration test for summary includes file paths and error types in `tests/integration/test_report_generation_cli.py`

### Implementation for User Story 4

- [ ] T063 [P] [US4] Implement error collection in ExecutionContext during parsing/generation
- [ ] T064 [US4] Implement warning collection in ExecutionContext during parsing/generation
- [ ] T065 [US4] Implement error aggregation logic in `ansibledoctor/reporting/report_generator.py` (consume Spec 010 ErrorAggregator when available)
- [ ] T066 [US4] Implement summary formatter for console output in `ansibledoctor/reporting/serializers.py`
- [ ] T067 [US4] Add `--fail-on-warnings` flag to CLI in `ansibledoctor/cli/__init__.py`
- [ ] T068 [US4] Add `--continue-on-error` flag to CLI in `ansibledoctor/cli/__init__.py`
- [ ] T069 [US4] Display aggregated summary at command completion in CLI in `ansibledoctor/cli/__init__.py`
- [ ] T070 [US4] Add error/warning arrays to ExecutionReport in report generation
- [ ] T070b [US4] **INTEGRATION**: When Spec 010 available, refactor T065 to use `from ansibledoctor.exceptions.aggregator import ErrorAggregator`

**Checkpoint**: User Story 4 complete - aggregated error summaries displayed at end of execution

---

## Phase 7: User Story 5 - CI/CD Integration with Exit Codes (Priority: P3)

**Goal**: Provide predictable exit codes for pipeline automation and build failure control

**Independent Test**: Run commands with various conditions → Exit codes match expectations (0/1/2/3)

### Tests for User Story 5 ✅

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T071 [P] [US5] Integration test for exit code 0 on success in `tests/integration/test_exit_codes.py`
- [ ] T072 [P] [US5] Integration test for exit code 1 on fatal error in `tests/integration/test_exit_codes.py`
- [ ] T073 [P] [US5] Integration test for exit code 2 with `--fail-on-warnings` in `tests/integration/test_exit_codes.py`
- [ ] T074 [P] [US5] Integration test for exit code 3 on invalid usage in `tests/integration/test_exit_codes.py`
- [ ] T075 [P] [US5] Integration test for warnings without `--fail-on-warnings` exit code 0 in `tests/integration/test_exit_codes.py`

### Implementation for User Story 5

- [ ] T076 [P] [US5] Define exit code constants in `ansibledoctor/exceptions.py` (SUCCESS=0, ERROR=1, WARNING=2, INVALID=3)
- [ ] T077 [US5] Implement exit code logic based on execution status in CLI in `ansibledoctor/cli/__init__.py`
- [ ] T078 [US5] Handle `--fail-on-warnings` flag to set exit code 2 in `ansibledoctor/cli/__init__.py`
- [ ] T079 [US5] Set exit code 1 on fatal errors in exception handling in `ansibledoctor/cli/__init__.py`
- [ ] T080 [US5] Set exit code 3 on invalid arguments (click validation) in `ansibledoctor/cli/__init__.py`
- [ ] T081 [US5] Document exit codes in CLI help text and README

**Checkpoint**: User Story 5 complete - predictable exit codes enable CI/CD pipeline automation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, performance optimization, and final integration

- [ ] T082 Update CLI `--help` output with all new flags and exit code documentation
- [ ] T083 [P] Add docstrings to all reporting module classes and functions
- [ ] T084 [P] Update README.md with execution reporting examples
- [ ] T085 [P] Create user guide section for CI/CD integration in docs/
- [ ] T086 Add JSON schema export for ExecutionReport for external validation
- [ ] T087 Performance optimization: ensure report generation <100ms overhead
- [ ] T088 [P] Add logging for report write operations (success, errors)
- [ ] T089 [P] Add validation for report file path (writable directory, valid filename)
- [ ] T090 Integration testing with existing watch mode functionality
- [ ] T091 Backward compatibility verification (no reports generated without --report flag)

---

## Dependencies & Parallelization

### Parallel Execution Opportunities

**After T011 (Foundational Complete)**:
- User Story 1, 2, 3, 4, 5 can be worked on in parallel by different developers
- Test writing for all stories can happen simultaneously

**Within Each User Story**:
- All test tasks marked [P] can run in parallel
- Model/utility implementation can happen while tests are being written

### Critical Path

```
T001-T003 (Setup) → T004-T011 (Foundation) → T012-T028 (US1 MVP) → T029-T043 (US2 MVP)
```

MVP delivery requires completing User Stories 1 and 2 (report generation + metrics).

---

## Suggested MVP Scope

**Minimum Viable Product** (first release):
- ✅ User Story 1: Generate Execution Report
- ✅ User Story 2: Performance Metrics Collection
- ⏭️ User Story 3-5: Can be delivered in subsequent releases

**Estimated Effort**:
- Setup + Foundation: 8 hours
- User Story 1 (MVP): 12 hours
- User Story 2 (MVP): 10 hours
- User Story 3: 8 hours
- User Story 4: 8 hours
- User Story 5: 6 hours
- Polish: 6 hours
- **Total: 58 hours (~7.5 days for 1 developer)**

---

## Implementation Strategy

1. **TDD Approach**: Write tests first (T012-T019 before T020-T028)
2. **Incremental Delivery**: Complete US1+US2 for MVP, then iterate
3. **Backward Compatibility**: All features opt-in via CLI flags
4. **Performance Testing**: Validate <100ms report overhead with benchmarks
5. **Integration Testing**: Ensure works with existing watch mode, project generation
6. **Regression Testing**: Verify existing Spec 001-008 functionality unchanged

---

## Backward Compatibility Regression Tasks

These tasks ensure existing functionality is not broken:

- [ ] T092 [REGRESSION] Run existing Spec 001-006 test suites to verify no regressions
- [ ] T093 [REGRESSION] Verify default behavior (no --report flag) produces identical output to before
- [ ] T094 [REGRESSION] Test that existing CLI commands work without new flags

---

## Success Criteria

- ✅ All 91 tasks completed with passing tests
- ✅ Test coverage >85% (90% for core reporting logic)
- ✅ Report generation overhead <100ms
- ✅ All constitution gates pass (TDD, CLI-first, observability)
- ✅ Backward compatible (no breaking changes)
- ✅ Documentation complete (CLI help, README, user guide)
- ✅ CI/CD example pipeline included in docs

**Status**: Ready for implementation
