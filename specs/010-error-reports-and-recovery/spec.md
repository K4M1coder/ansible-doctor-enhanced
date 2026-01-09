# Feature Specification: Error Reports & Recovery

**Feature Branch**: `010-error-reports-and-recovery`  
**Created**: 2025-12-02  
**Milestone**: v0.9.0  
**Prerequisites**: v0.8.0 (Template Customization) COMPLETE ✅  
**Status**: Draft

## Objective

**ENHANCEMENT** (extends existing exception hierarchy)

Standardize error reporting, recovery suggestions, and graceful degradation in ansible-doctor-enhanced. Build upon the existing `AnsibleDoctorError` hierarchy to provide aggregated error reports, intelligent recovery suggestions, partial success handling, and user-friendly error presentation.

## What is Error Reports & Recovery?

Error Reports & Recovery provides structured error handling and user guidance:

- **Aggregated Error Reports**: Consolidated view of all errors encountered during processing
- **Recovery Suggestions**: Intelligent, context-aware suggestions for fixing each error type
- **Graceful Degradation**: Continue processing when individual files fail, document what succeeded
- **Error Classification**: Categorize errors by severity (fatal, error, warning, info) and type
- **Machine-Readable Errors**: Structured error output for tooling integration

**Existing Infrastructure** (from `exceptions.py` and `generator/errors.py`):

- `AnsibleDoctorError` base class with message, context, and suggestion attributes
- Specialized exceptions: `ParsingError`, `ValidationError`, `ConfigError`, `TemplateError`
- Generator-specific: `TemplateNotFoundError`, `TemplateValidationError`, `RenderError`

**Enhancement Goals**:

- Add error aggregation collector for multi-file processing
- Implement recovery suggestion database with common fixes
- Provide partial success reporting (N of M files processed)
- Support error export to structured formats (JSON, SARIF)
- Enable IDE integration with file:line error references

**Error Report Structure Example**:

```json
{
  "summary": {
    "total_files": 15,
    "successful": 12,
    "failed": 3,
    "warnings": 5
  },
  "errors": [
    {
      "severity": "error",
      "type": "ParsingError",
      "code": "E001",
      "file": "defaults/main.yml",
      "line": 42,
      "column": 5,
      "message": "Invalid YAML syntax: unexpected indent",
      "suggestion": "Check indentation at line 42. YAML requires consistent spacing.",
      "documentation_url": "https://docs.ansible-doctor.io/errors/E001"
    }
  ],
  "warnings": [
    {
      "severity": "warning",
      "type": "AnnotationWarning",
      "code": "W001",
      "file": "defaults/main.yml",
      "line": 15,
      "message": "Variable 'app_port' missing @var annotation",
      "suggestion": "Add '# @var app_port: Description' above the variable definition"
    }
  ]
}
```

## User Scenarios & Testing

### User Story 1 - Aggregated Error Report (Priority: P1) 🎯 MVP

As a documentation maintainer with a large project, I want to see all errors aggregated at the end of processing so that I can systematically fix issues without re-running the command multiple times.

**Why this priority**: When processing 100+ roles, scattered error messages are hard to track. An aggregated report provides actionable overview and prioritization.

**Independent Test**: Run `ansible-doctor generate project/` with multiple files having errors → End of output shows consolidated error report grouped by file.

**Acceptance Scenarios**:

1. **Given** multiple files have errors, **When** command completes, **Then** console shows aggregated report with count per file and error types
2. **Given** errors occur in different phases (parsing, rendering), **When** report is generated, **Then** errors are grouped by phase with clear labels
3. **Given** `--error-format json` flag, **When** errors occur, **Then** structured JSON error report is written to stderr or specified file
4. **Given** `--error-format sarif` flag, **When** errors occur, **Then** SARIF format report is generated for IDE integration
5. **Given** both errors and warnings, **When** report is generated, **Then** errors are listed first (higher severity), then warnings

---

### User Story 2 - Intelligent Recovery Suggestions (Priority: P1) 🎯 MVP

As a user encountering an error, I want to see specific, actionable suggestions for fixing the issue so that I can resolve problems without searching documentation.

**Why this priority**: Clear recovery suggestions reduce time-to-fix and improve user experience. Most errors have well-known solutions.

**Independent Test**: Trigger YAML syntax error → Error message includes specific suggestion like "Check indentation at line X" with example of correct syntax.

**Acceptance Scenarios**:

1. **Given** YAML syntax error, **When** error is reported, **Then** suggestion includes line number and common fix (e.g., "Check for tabs vs spaces")
2. **Given** missing required file (e.g., tasks/main.yml), **When** error is reported, **Then** suggestion includes expected file path and minimum content template
3. **Given** invalid annotation syntax, **When** error is reported, **Then** suggestion shows correct syntax with example
4. **Given** circular dependency detected, **When** error is reported, **Then** suggestion shows dependency chain and how to break cycle
5. **Given** template variable undefined, **When** error is reported, **Then** suggestion lists available variables and similar-named alternatives (typo detection)

---

### User Story 3 - Graceful Degradation (Priority: P1) 🎯 MVP

As a CI/CD pipeline operator, I want ansible-doctor to continue processing when individual files fail so that I get partial documentation rather than nothing.

**Why this priority**: In large projects, one broken file shouldn't block documentation for all other files. Partial results are better than no results.

**Independent Test**: Run `ansible-doctor generate project/` with 1 broken role among 10 → 9 roles are documented, error report shows which one failed.

**Acceptance Scenarios**:

1. **Given** one role has parsing errors, **When** processing multiple roles, **Then** other roles are processed successfully and documented
2. **Given** `--strict` flag is NOT set, **When** errors occur, **Then** processing continues and partial results are generated
3. **Given** `--strict` flag is set, **When** any error occurs, **Then** processing stops immediately with full error details
4. **Given** partial success, **When** report is generated, **Then** summary shows "12 of 15 roles documented successfully"
5. **Given** partial success, **When** output files are generated, **Then** each successful file is complete (no half-written docs)

---

### User Story 4 - Error Classification & Codes (Priority: P2)

As a documentation maintainer, I want errors to have unique codes so that I can search for solutions and configure error suppression.

**Why this priority**: Error codes enable documentation lookup, suppression rules, and consistent communication about issues.

**Independent Test**: Trigger an error → Error message includes code like "E001" that can be looked up in documentation.

**Acceptance Scenarios**:

1. **Given** any error, **When** error is displayed, **Then** it includes a unique error code (E001, W001, etc.)
2. **Given** error code E001, **When** user visits documentation URL, **Then** detailed explanation with examples is available
3. **Given** `--ignore E001,W002` flag, **When** those errors occur, **Then** they are suppressed from output (not counted as failures)
4. **Given** `.ansibledoctor.yml` with `ignore_errors: [E001]`, **When** E001 occurs, **Then** it is suppressed
5. **Given** ignored errors, **When** report is generated, **Then** summary shows count of suppressed errors separately

---

### User Story 5 - IDE-Friendly Error Output (Priority: P2)

As a developer using VS Code/PyCharm, I want errors to include file:line:column references so that I can click to navigate directly to the problem.

**Why this priority**: IDE integration improves developer productivity by enabling direct navigation to error locations.

**Independent Test**: Run command in VS Code terminal with error → Error output format allows clicking to jump to file location.

**Acceptance Scenarios**:

1. **Given** error with known file and line, **When** error is displayed in console, **Then** format is `file:line:column: error[CODE]: message`
2. **Given** SARIF output format, **When** imported into VS Code, **Then** Problems panel shows all errors with navigation
3. **Given** error in nested include file, **When** error is displayed, **Then** both the include location and actual error location are shown
4. **Given** multiple errors in same file, **When** errors are displayed, **Then** they are sorted by line number

---

### User Story 6 - Error Context Preservation (Priority: P3)

As a developer debugging a complex issue, I want to see the full context (stack trace, surrounding code) so that I can understand the root cause.

**Why this priority**: For complex issues, minimal error messages aren't enough. Full context aids debugging without requiring reproduction.

**Independent Test**: Run with `--verbose` and trigger error → Output includes stack trace and relevant code snippet.

**Acceptance Scenarios**:

1. **Given** `--verbose` flag, **When** error occurs, **Then** full stack trace is included in output
2. **Given** error at specific line, **When** verbose mode is enabled, **Then** surrounding 3 lines of source are shown
3. **Given** error in template, **When** reported, **Then** template source snippet with error highlighted is included
4. **Given** `--debug` flag, **When** error occurs, **Then** internal exception chain is fully displayed

---

### Edge Cases

- What happens when error report file path is not writable?
  - MUST fail with clear error and still output errors to stderr
- What happens when error occurs during error reporting?
  - MUST fail safely with basic error message, never crash silently
- How does system handle errors with no known recovery suggestion?
  - MUST show generic "Check file syntax and retry" suggestion, never empty
- What happens when same error occurs in 100+ files?
  - MUST aggregate and show "100 files with error E001" instead of 100 lines
- How does system handle errors in binary files accidentally included?
  - MUST skip binary files with warning, never crash on non-text content
- What happens when error code database is missing/corrupted?
  - MUST fall back to generic suggestions, log warning about missing database

## Requirements

### Functional Requirements

- **FR-001**: System MUST aggregate all errors encountered during processing into a single report at command completion
- **FR-002**: System MUST assign unique error codes to each error type (format: E### for errors, W### for warnings)
- **FR-003**: System MUST provide recovery suggestions for all known error types
- **FR-004**: System MUST continue processing other files when individual files fail (unless `--strict` mode)
- **FR-005**: System MUST report partial success (N of M files processed) when some files fail
- **FR-006**: System MUST support error output formats: text (default), json, sarif
- **FR-007**: System MUST include file path, line number, and column (when available) in all error reports
- **FR-008**: System MUST support `--ignore` flag to suppress specific error codes
- **FR-009**: System MUST support error suppression via configuration file (`ignore_errors` setting)
- **FR-010**: System MUST display errors in IDE-friendly format (`file:line:column: type[CODE]: message`)
- **FR-011**: System MUST sort errors by file, then by line number within file
- **FR-012**: System MUST aggregate duplicate errors (same code, same message) with count
- **FR-013**: System MUST include documentation URL in error messages for error codes
- **FR-014**: Verbose mode MUST include stack traces and source code context
- **FR-015**: System MUST classify errors by severity: fatal (processing stops), error (file skipped), warning (continues), info (informational)

### Key Entities

- **ErrorReport**: Aggregated collection of all errors with summary statistics
- **ErrorEntry**: Single error with code, severity, file, line, column, message, suggestion, documentation_url
- **WarningEntry**: Single warning with same structure as ErrorEntry but lower severity
- **ErrorCode**: Unique identifier (E001, W001) with associated message template and suggestion
- **RecoverySuggestion**: Actionable text explaining how to fix specific error type
- **ErrorSuppression**: Configuration for ignoring specific error codes

## Success Criteria

### Measurable Outcomes

- **SC-001**: All error types have unique codes documented with recovery suggestions
- **SC-002**: Aggregated error report is generated within 50ms overhead regardless of error count
- **SC-003**: Users can navigate from error to source location with single click in supported IDEs
- **SC-004**: Partial success processing documents 100% of valid files when some files have errors
- **SC-005**: Error codes can be searched in documentation to find detailed explanations
- **SC-006**: SARIF output integrates with VS Code Problems panel without manual configuration
- **SC-007**: Same error in 100 files is reported in 3 lines (summary) not 100 lines

## Technical Constraints

- **TC-001**: MUST extend existing `AnsibleDoctorError` hierarchy (no parallel exception system)
- **TC-002**: MUST maintain backward compatibility with existing error message format
- **TC-003**: Error codes MUST be stable across versions (no renumbering)
- **TC-004**: SARIF output MUST conform to SARIF 2.1.0 specification
- **TC-005**: Error aggregation MUST NOT consume unbounded memory (cap at 1000 errors, warn if exceeded)
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
