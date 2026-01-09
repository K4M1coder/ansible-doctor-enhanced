# Feature Specification: Execution Reports & Structured Logging

**Feature Branch**: `009-execution-reports-and-logs`  
**Created**: 2025-12-02  
**Milestone**: v0.9.0  
**Prerequisites**: v0.8.0 (Template Customization) COMPLETE ✅  
**Status**: Draft

## Objective

**ENHANCEMENT** (extends existing logging infrastructure)

Formalize and extend the execution reporting system in ansible-doctor-enhanced. Build upon the existing structlog-based logging infrastructure to provide comprehensive execution reports, performance metrics collection, aggregated error summaries, and enhanced correlation ID tracing across operations.

## What is Execution Reporting?

Execution reporting provides visibility into ansible-doctor operations:

- **Execution Reports**: Structured summaries of operations (files processed, warnings, errors, timing)
- **Performance Metrics**: Duration tracking, file counts, throughput measurements
- **Correlation IDs**: Request tracing across nested operations (role → collection → project)
- **Aggregated Errors**: Consolidated error summaries with recovery suggestions
- **Machine-Readable Output**: JSON reports for CI/CD integration and automation

**Existing Infrastructure** (from `utils/logging.py`):

- structlog with JSON/console output modes
- Correlation ID binding via contextvars
- Module-level logger factory (`get_logger()`)
- Context binding (`bind_context()`, `clear_context()`)

**Enhancement Goals**:

- Add execution report generation at command completion
- Implement performance metrics collection (timing, counts)
- Provide aggregated error summaries with file locations
- Support report export to file (JSON, summary text)
- Enable CI/CD-friendly exit codes and reports

**Report Structure Example**:

```json
{
  "correlation_id": "abc-123-def",
  "command": "generate",
  "status": "completed_with_warnings",
  "started_at": "2025-12-02T10:30:00Z",
  "completed_at": "2025-12-02T10:30:05Z",
  "duration_ms": 5234,
  "metrics": {
    "files_processed": 15,
    "roles_documented": 3,
    "warnings_count": 2,
    "errors_count": 0
  },
  "warnings": [
    {"file": "defaults/main.yml", "line": 42, "message": "Variable missing @var annotation"}
  ],
  "errors": [],
  "output_files": ["docs/README.md", "docs/index.html"]
}
```

## User Scenarios & Testing

### User Story 1 - Generate Execution Report (Priority: P1) 🎯 MVP

As a DevOps engineer running ansible-doctor in CI/CD pipelines, I want to receive a structured execution report after each command so that I can programmatically verify success, check metrics, and identify issues.

**Why this priority**: CI/CD integration is critical for automation. Structured reports enable pipeline decisions (fail on errors, warn on warnings, report metrics to dashboards).

**Independent Test**: Run `ansible-doctor generate role/ --report report.json` → JSON file created with status, metrics, timing, and any warnings/errors.

**Acceptance Scenarios**:

1. **Given** a successful generation command, **When** `--report report.json` is specified, **Then** a JSON file is created with status "completed", timing metrics, and files generated
2. **Given** a generation with warnings (e.g., missing annotations), **When** report is generated, **Then** status is "completed_with_warnings" and warnings array contains file locations and messages
3. **Given** a failed generation (parsing error), **When** report is generated, **Then** status is "failed", errors array contains detailed error info with recovery suggestions
4. **Given** `--report-format text` flag, **When** command completes, **Then** human-readable summary is written instead of JSON
5. **Given** no `--report` flag, **When** command completes, **Then** no report file is generated (backward compatible)

---

### User Story 2 - Performance Metrics Collection (Priority: P1) 🎯 MVP

As a documentation maintainer, I want to see performance metrics (timing, file counts) so that I can identify slow operations and optimize large projects.

**Why this priority**: Performance visibility is essential for large projects with hundreds of roles. Enables bottleneck identification and optimization decisions.

**Independent Test**: Run `ansible-doctor generate project/ --verbose` → Console output includes timing per phase (parsing, rendering, writing) and file counts.

**Acceptance Scenarios**:

1. **Given** verbose mode is enabled, **When** command runs, **Then** console shows phase timing (e.g., "Parsing: 1.2s, Rendering: 0.8s, Writing: 0.3s")
2. **Given** multiple roles are processed, **When** command completes, **Then** metrics include total files processed, roles/collections/projects documented
3. **Given** `--report` flag is used, **When** command completes, **Then** report includes `metrics` object with `duration_ms`, `files_processed`, `roles_documented`
4. **Given** watch mode is running, **When** regeneration occurs, **Then** each regeneration cycle reports its own timing metrics

---

### User Story 3 - Correlation ID Tracing (Priority: P2)

As a developer debugging issues, I want all log entries from a single operation to share a correlation ID so that I can trace the complete execution flow across nested operations.

**Why this priority**: Debugging complex issues (e.g., in project with 50 roles) requires tracing logs across multiple components. Correlation IDs are the standard solution.

**Independent Test**: Run `ansible-doctor generate project/` with JSON logging → All log entries share the same `correlation_id` field.

**Acceptance Scenarios**:

1. **Given** a command starts execution, **When** logging is enabled, **Then** a unique correlation ID is generated and included in all log entries
2. **Given** nested operations (project → collection → role), **When** each component logs, **Then** all logs share the parent correlation ID
3. **Given** `--correlation-id abc-123` CLI flag, **When** command runs, **Then** provided ID is used instead of auto-generated
4. **Given** watch mode triggers multiple regenerations, **When** each regeneration starts, **Then** a new correlation ID is generated for each cycle
5. **Given** JSON log output mode, **When** logs are parsed, **Then** all entries for one operation can be filtered by correlation ID

---

### User Story 4 - Aggregated Error Summary (Priority: P2)

As a documentation maintainer with a large project, I want to see an aggregated summary of all errors and warnings at the end of execution so that I can address issues systematically.

**Why this priority**: When processing 100+ roles, individual errors scroll by quickly. An aggregated summary at the end provides actionable overview.

**Independent Test**: Run `ansible-doctor generate project/` with some roles having errors → End of output shows summary table with error counts per file.

**Acceptance Scenarios**:

1. **Given** multiple files have warnings, **When** command completes, **Then** console shows summary: "3 warnings in 2 files" with file list
2. **Given** some roles fail to parse, **When** command completes, **Then** summary shows "2 errors in 2 roles" with role names and error types
3. **Given** `--fail-on-warnings` flag, **When** any warnings occur, **Then** command exits with non-zero code (exit code 2)
4. **Given** errors occur but `--continue-on-error` is set, **When** command completes, **Then** all processable files are documented and error summary is shown
5. **Given** report is generated, **When** errors exist, **Then** report includes `errors` array with file path, line number, error type, message, and suggestion

---

### User Story 5 - CI/CD Integration with Exit Codes (Priority: P3)

As a CI/CD pipeline maintainer, I want predictable exit codes so that I can configure pipeline behavior based on execution results.

**Why this priority**: Standard exit codes enable pipeline automation (fail builds on errors, warn on warnings, pass on success).

**Independent Test**: Run `ansible-doctor generate role/` with various conditions → Exit codes match expected values (0=success, 1=error, 2=warning).

**Acceptance Scenarios**:

1. **Given** successful execution with no warnings, **When** command completes, **Then** exit code is 0
2. **Given** execution completes with warnings, **When** command completes, **Then** exit code is 0 (unless `--fail-on-warnings`)
3. **Given** execution fails with errors, **When** command completes, **Then** exit code is 1
4. **Given** `--fail-on-warnings` flag and warnings occur, **When** command completes, **Then** exit code is 2
5. **Given** invalid arguments or configuration, **When** command starts, **Then** exit code is 3 with usage help

---

### Edge Cases

- What happens when report output path is not writable?
  - MUST fail with clear error message and suggestion (check permissions, directory exists)
- What happens when correlation ID format is invalid?
  - MUST accept any string as correlation ID (no format validation), log warning if unusually long
- How does system handle out-of-memory during large project processing?
  - MUST gracefully fail with partial report including last successful file processed
- What happens when watch mode is interrupted during report generation?
  - MUST write partial report with "interrupted" status
- How does system handle concurrent executions with same report file?
  - MUST use atomic write (write to temp, rename) to prevent corruption

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate execution reports in JSON format when `--report <path>` flag is provided
- **FR-002**: System MUST support `--report-format` flag with values: `json` (default), `text`, `summary`
- **FR-003**: Reports MUST include: correlation_id, command, status, started_at, completed_at, duration_ms, metrics, warnings, errors
- **FR-004**: System MUST collect timing metrics for each execution phase (parsing, rendering, writing)
- **FR-005**: System MUST count files processed, roles/collections/projects documented, warnings, and errors
- **FR-006**: System MUST generate unique correlation ID per execution (UUIDv4 format)
- **FR-007**: System MUST support `--correlation-id` CLI flag to use provided ID
- **FR-008**: All log entries MUST include correlation_id field when JSON logging is enabled
- **FR-009**: System MUST aggregate errors and warnings by file/component at command completion
- **FR-010**: Aggregated summary MUST show file path, line number (if available), message, and count
- **FR-011**: System MUST support `--fail-on-warnings` flag to return non-zero exit code on warnings
- **FR-012**: System MUST support `--continue-on-error` flag to process all files despite individual failures
- **FR-013**: Exit codes MUST follow convention: 0=success, 1=error, 2=warnings (with --fail-on-warnings), 3=invalid usage
- **FR-014**: System MUST use atomic file writes for reports to prevent corruption
- **FR-015**: Verbose mode MUST display phase timing and progress during execution

### Key Entities

- **ExecutionReport**: Complete execution summary with status, timing, metrics, warnings, errors, output files
- **ExecutionMetrics**: Numeric measurements (duration_ms, files_processed, roles_documented, warnings_count, errors_count)
- **ExecutionWarning**: Warning entry with file path, line number (optional), message, warning type
- **ExecutionError**: Error entry with file path, line number (optional), error type, message, suggestion, stack trace (optional)
- **CorrelationContext**: Request-scoped context holding correlation_id and operation metadata

## Success Criteria

### Measurable Outcomes

- **SC-001**: Execution reports are generated within 100ms overhead regardless of project size
- **SC-002**: All CLI commands support `--report` flag for JSON report generation
- **SC-003**: Correlation IDs enable filtering all logs from a single execution within 1 grep/jq command
- **SC-004**: Aggregated error summary shows all issues discovered in a single view (no scrolling through logs)
- **SC-005**: CI/CD pipelines can make pass/fail decisions based solely on exit code without parsing output
- **SC-006**: Performance metrics are accurate within 5% margin for timing measurements
- **SC-007**: Reports are valid JSON that can be parsed by standard tools (jq, Python json module)

## Technical Constraints

- **TC-001**: MUST extend existing structlog infrastructure (no new logging framework)
- **TC-002**: MUST maintain backward compatibility (no report generated unless flag specified)
- **TC-003**: MUST work with existing exception hierarchy (AnsibleDoctorError and subclasses)
- **TC-004**: Report generation MUST NOT block or slow down normal output
- **TC-005**: Correlation ID MUST propagate through existing contextvars mechanism
