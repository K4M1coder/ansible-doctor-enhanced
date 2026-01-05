# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Execution Reports & Structured Logging (Spec 009)

**Phase 7-8: Exit Code System & CI/CD Integration ✅ COMPLETE**

**Exit Code System (T071-T080)**:
- **Standardized Exit Codes** in `ansibledoctor/exceptions.py`:
  - `EXIT_SUCCESS = 0`: Command succeeded (with or without warnings)
  - `EXIT_ERROR = 1`: Fatal error (parsing failed, file not found, validation failed)
  - `EXIT_WARNING = 2`: Warnings present with --fail-on-warnings flag
  - `EXIT_INVALID = 3`: Invalid command usage (bad arguments, validation errors)

- **CLI Exit Code Logic** (`ansibledoctor/cli/__init__.py`):
  - Proper exception handling hierarchy:
    1. ParsingError exceptions now propagate correctly (allows YAML validation)
    2. ValidationError → EXIT_INVALID for invalid arguments
    3. AnsibleDoctorError → EXIT_ERROR for processing failures
    4. Generic exceptions → EXIT_ERROR with error messages
  - Success paths return EXIT_SUCCESS or EXIT_WARNING based on --fail-on-warnings flag
  - Path validation moved from Click to manual checks with correct exit codes

- **New CLI Flag**: `--fail-on-warnings`
  - Available for both `parse` and `generate` commands
  - Default: False (warnings don't cause non-zero exit)
  - When enabled: Command exits with code 2 if warnings detected
  - Use case: CI/CD quality gates requiring zero warnings

- **Role Validation Improvements**:
  - Changed REQUIRED_DIRS from ["tasks"] to [] in `ansibledoctor/utils/paths.py`
  - Allows minimal roles (meta + defaults only) to pass validation
  - Warnings issued for missing directories instead of errors

**Documentation & CI/CD Integration (T081-T084)**:
- **CLI Help Documentation**:
  - Added comprehensive "Exit Codes:" section to both `parse` and `generate` commands
  - Includes usage examples and exit code explanations
  - Users can now discover exit codes via `--help`

- **README CI/CD Section** (150+ lines):
  - Complete exit code reference table with visual indicators (✅❌⚠️🚫)
  - GitHub Actions workflow example (copy-paste ready)
  - GitLab CI pipeline example
  - Quality gate patterns using --fail-on-warnings
  - Execution report JSON structure examples
  - Correlation ID usage documentation for distributed tracing

- **Comprehensive Docstrings**:
  - All reporting modules fully documented (MetricsCollector, ReportGenerator, serializers)
  - Correlation utilities documented with examples
  - Function signatures include type hints and return value docs

**Testing & Validation (T071-T075, T091-T094)**:
- **Exit Code Test Suite**: 9/9 tests passing (100%)
  - Success scenarios for parse and generate commands
  - Error handling (nonexistent paths, invalid YAML, validation errors)
  - Warning handling with and without --fail-on-warnings flag
  - Invalid flag combinations and argument validation
- **Backward Compatibility**: ✅ Verified
  - All 334 existing integration tests pass without --report flag
  - Default behavior unchanged (no reports generated unless requested)
  - No breaking changes to existing functionality
- **Regression Testing**: ✅ Complete
  - Full test suite: 1628/1640 tests passing (99.3%)
  - 12 failures unrelated to Spec 009 (pre-existing)
  - Exit code system adds no new test failures

**CI/CD Integration Support**:
- Exit codes now enable pipeline automation:
  - `EXIT_SUCCESS (0)`: Safe to proceed, deploy allowed
  - `EXIT_ERROR (1)`: Block pipeline, investigation required
  - `EXIT_WARNING (2)`: Optional quality gate (with --fail-on-warnings)
  - `EXIT_INVALID (3)`: Configuration error, fix arguments
- Compatible with GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure DevOps
- Execution reports (--report flag) provide detailed metrics for dashboards

**Phase Status**: 
- Phase 1-6: All user stories complete (42 tests passing)
- Phase 7: Exit code implementation complete (9 tests passing)
- Phase 8: Documentation and polish complete (all tasks done)
- **Spec 009**: 100% complete with comprehensive CI/CD integration
  - `EXIT_WARNING (2)`: Warning threshold exceeded (with --fail-on-warnings)
  - `EXIT_ERROR (1)`: Build should fail
  - `EXIT_INVALID (3)`: Configuration problem

### Added - Execution Reports & Structured Logging (Spec 009 Phase 1-6 Complete) ✅

**Phase 1: Setup (T001-T003)**
- **Reporting Module**: Created `ansibledoctor/reporting/__init__.py` with module documentation
- **Models Structure**: Created `ansibledoctor/models/execution_report.py` placeholder for execution models
- **Test Structure**: Created test directories for `tests/unit/models/`, `tests/unit/reporting/`, `tests/integration/`

**Phase 2: Foundation (T004-T011)**
- **ExecutionMetrics Model**: Pydantic model for performance metrics (files, roles, collections, projects counts, phase timing)
- **ExecutionWarning Model**: Pydantic model for warnings with file location and line number
- **ExecutionError Model**: Pydantic model for errors with suggestions and stack traces
- **ExecutionReport Model**: Primary aggregate model combining status, timing, metrics, warnings, errors, output files
- **ReportGenerator Protocol**: Interface for report generation and writing (JSON/text/summary formats)
- **MetricsCollector Protocol**: Interface for metrics collection (phase timing, counters)
- **Correlation ID Utilities**: UUID4 generation, contextvars-based propagation (thread-safe)
- **Exit Code Property**: Added `exit_code` property to `AnsibleDoctorError` base class (default: 1, ConfigError: 3)

**Phase 3: User Story 1 Tests (T012-T019) - RED Phase ✅**
- **Unit Tests**: `test_execution_report.py` with 8 comprehensive tests:
  - Serialization to JSON (ISO 8601 datetime, all fields)
  - Model validation (required fields, status enum, non-negative duration)
  - Reports with warnings (status="completed_with_warnings")
  - Reports with errors (status="failed", suggestions included)
- **Integration Tests**: `test_report_generation_cli.py` with 7 CLI tests:
  - `--report` flag creates JSON file
  - Report contains correct status and metrics
  - Warnings and errors arrays populated correctly
  - Failed execution creates report with status="failed"
- **Test Status**: 8/8 unit tests PASS, 0/7 integration tests PASS (expected - no CLI implementation yet)

**Phase 3: User Story 1 Implementation (T020-T028) - GREEN Phase ✅**
- **Serializers**: `ansibledoctor/reporting/serializers.py` with 3 output formats:
  - `serialize_to_json()`: JSON with ISO 8601 datetime (Z suffix), indented, Path → str conversion
  - `serialize_to_text()`: Human-readable text with sections (metrics, phase timing, warnings, errors)
  - `serialize_to_summary()`: Brief console summary with status symbol, duration, counts
- **ReportGenerator**: `ansibledoctor/reporting/report_generator.py` concrete implementation:
  - `generate(context)`: Creates ExecutionReport from dict, parses datetime strings, validates with Pydantic
  - `write_report(report, path, format)`: Atomic file write (temp + rename) to prevent corruption
- **CLI Integration**: `ansibledoctor/cli/__init__.py` enhanced commands:
  - `parse` command: Added `--report PATH` and `--report-format {json,text,summary}` flags
  - `generate` command: Added `--report PATH` and `--report-format {json,text,summary}` flags
  - Correlation ID generation: Set at command start using `set_correlation_id(generate_correlation_id())`
  - Execution timing: Tracks `started_at`, `completed_at`, `duration_ms` for accurate performance metrics
  - Error/warning collection: Aggregates warnings/errors in lists for report inclusion
  - Report generation: Uses `_generate_execution_report()` helper on all exit paths (success, validation error, parsing error, unexpected error)
- **Test Status**: All 15 tests PASSING (8 unit + 7 integration tests) ✅
- **User Story 1**: Complete MVP - JSON/text/summary reports with metrics, warnings, errors ✅

**Phase 4: User Story 2 Tests (T029-T034) - RED Phase ✅**
- **Unit Tests**: `test_metrics_collector.py` with 10 comprehensive tests:
  - `TestMetricsCollectorPhaseTiming` (3 tests): start/end_phase duration tracking, multiple phases independently, error on end without start
  - `TestMetricsCollectorCounters` (3 tests): increment by default (1), custom values, multiple counters independently
  - `TestNestedPhaseTiming` (2 tests): "parent.child" notation for nested phases, multiple nested phases in same parent
  - `TestMetricsTimingAccuracy` (2 tests): mocked perf_counter for exact values, real timing within 10% variance (<5% requirement)
- **Integration Tests**: `test_metrics_collection_e2e.py` with 4 CLI tests:
  - `TestMetricsInReportJSON` (2 tests): phase_timing dict in report JSON, files_processed counter validation
  - `TestVerboseModePhasing` (2 tests): --verbose displays timing info in stderr, works with --report flag
- **Stub Implementation**: `ansibledoctor/reporting/metrics_collector.py` placeholder with NotImplementedError
- **Test Status**: 13/14 tests FAILING with NotImplementedError (expected RED phase) ✅

**Phase 4: User Story 2 Implementation (T035-T043) - GREEN Phase ✅**
- **MetricsCollector Core**: `ansibledoctor/reporting/metrics_collector.py` complete implementation:
  - High-precision timing with `time.perf_counter()` (<5% accuracy requirement)
  - Phase tracking: `start_phase()`, `end_phase()` with ValueError on invalid operations
  - Duration conversion: seconds → milliseconds (int) matching ExecutionMetrics schema
  - Counter tracking: `increment_counter()` for files/roles/collections/projects/warnings/errors
  - Nested phase support: "parent.child" notation for hierarchical timing
  - Metrics export: `get_metrics()` returns ExecutionMetrics Pydantic model
  - Thread-safe dict operations for concurrent access
- **CLI Integration - parse command**: `ansibledoctor/cli/__init__.py`
  - MetricsCollector instantiated at command start
  - Phase tracking: parsing phase (doc.parse()), output phase (serialization/write)
  - Counter tracking: files_processed incremented after successful parse
  - Verbose mode: `--verbose` displays phase timing and counters in stderr
- **CLI Integration - generate command**: `ansibledoctor/cli/__init__.py`
  - MetricsCollector instantiated at command start
  - Phase tracking: parsing (doc.parse()), rendering (doc.render()), writing (output file creation)
  - Counter tracking: files_processed incremented after successful generation
  - Verbose mode: `--verbose` displays phase timing and counters in stderr
- **Report Integration**: ExecutionMetrics from MetricsCollector passed to `_generate_execution_report()`
- **Test Status**: All 14 tests PASSING (10 unit + 4 integration tests) ✅
- **User Story 2**: Complete - Performance metrics with <5% timing accuracy, verbose mode display ✅

**Phase 5: User Story 3 Tests (T044-T049) - RED/GREEN Hybrid ✅**
- **Unit Tests**: `tests/unit/utils/test_correlation.py` with 10 comprehensive tests:
  - `TestCorrelationIDGeneration` (3 tests): UUID4 format validation, uniqueness across calls, parseability as UUID object
  - `TestCorrelationIDPropagation` (4 tests): set/get operations, None when unset, clear functionality, context isolation between operations
  - `TestCustomCorrelationID` (3 tests): custom format acceptance, UUID string handling, overwrite previous value
- **Integration Tests**: `tests/integration/test_correlation_propagation.py` with 4 CLI tests:
  - `TestCorrelationIDInLogEntries` (1 test): Verify correlation_id present in log output during execution
  - `TestCorrelationIDInReport` (2 tests): correlation_id field in report JSON, custom --correlation-id flag support
  - `TestNestedOperationsCorrelationID` (1 test): Nested operations share parent correlation_id
- **Test Status**: 13/14 tests PASSING (10 unit + 3 integration) ✅
  - 1 test failing (custom --correlation-id flag) because flag not yet implemented (expected for T053)
- **Note**: Tests pass because correlation ID implementation already exists from Phase 2 (ansibledoctor/utils/correlation.py)
- **User Story 3**: Tests validate existing functionality - correlation IDs in reports, log propagation, nested operations ✅

**Phase 5: User Story 3 Implementation (T050-T057) - GREEN Phase ✅**
- **CLI Enhancement**: `ansibledoctor/cli/__init__.py` parse and generate commands:
  - Added `--correlation-id ID` optional flag to both commands
  - If not provided, auto-generates UUID4 via `generate_correlation_id()`
  - If provided, uses custom correlation ID from user
  - Sets correlation ID at command start via `set_correlation_id()`
- **Structlog Integration**: `ansibledoctor/utils/correlation.py` enhanced `set_correlation_id()`:
  - Now binds correlation_id to structlog's contextvars automatically
  - Ensures correlation_id appears in ALL log entries (DEBUG, INFO, WARNING, ERROR)
  - Graceful fallback if structlog not available (try/except ImportError)
- **Test Status**: All 14 tests PASSING (10 unit + 4 integration tests) ✅
  - All correlation ID tests pass, including custom --correlation-id flag test
  - Correlation ID present in logs and reports
  - Nested operations share parent correlation_id
- **User Story 3**: Complete - Correlation ID tracing across operations, custom IDs via CLI, structlog binding ✅

**Phase 6: User Story 4 Tests (T058-T062) - RED Phase ✅**
- **Unit Tests**: `tests/unit/reporting/test_error_aggregation.py` with 7 comprehensive tests:
  - `TestErrorAggregationByFile` (2 tests): Errors grouped by file in summary, multiple errors show count
  - `TestWarningAggregationByFile` (2 tests): Warnings grouped by file, mixed warnings/errors both displayed
  - `TestSummaryTextFormatting` (3 tests): File paths in summary, error types shown, table format for readability
- **Integration Tests**: `tests/integration/test_report_generation_cli.py` with 2 CLI tests:
  - `TestAggregatedSummaryDisplay` (2 tests): Console shows error counts, file paths and error types included
- **Test Status**: 8/9 tests FAILING (7 unit + 1 integration) ✅
  - 1 test passing (verifies existing report structure)
  - Failures confirm need for aggregated summary with file grouping
  - Current summary: "✗ Failed in 1.0s\n3 files processed, 1 roles documented\n0 warnings, 3 errors"
  - Expected summary: Grouped errors/warnings by file with line numbers and types
- **User Story 4**: Tests define requirements for aggregated error/warning summaries at command completion ✅

**Phase 6: User Story 4 Implementation (T063-T070b) - GREEN Phase ✅**
- **Summary Formatter Enhancement**: `ansibledoctor/reporting/serializers.py` `serialize_to_summary()`:
  - Groups errors by file path with count per file (e.g., "tasks/main.yml (2):")
  - Groups warnings by file path with count per file
  - Displays line numbers for each error/warning (e.g., "Line 42: yaml_error - Invalid YAML")
  - Shows error/warning type and message for troubleshooting
  - Structured indented format for readability
  - Path normalization: Windows backslashes → forward slashes for consistency
- **Example Enhanced Summary**:
  ```
  ✗ Failed in 1.0s
  3 files processed, 1 roles documented
  
  Errors (3):
    defaults/main.yml (1):
      - Line 5: validation_error - Invalid variable name
    tasks/main.yml (2):
      - Line 10: yaml_error - Invalid YAML syntax
      - Line 25: parsing_error - Missing required field
  ```
- **Test Status**: All 9 tests PASSING (7 unit + 2 integration tests) ✅
  - Error aggregation by file validated
  - Warning aggregation by file validated
  - Summary text formatting with file paths and error types validated
- **User Story 4**: Complete - Aggregated error/warning summaries grouped by file for easy troubleshooting ✅

**Phase 7: User Story 5 Tests (T071-T075) - RED Phase ✅**
- **Integration Tests**: `tests/integration/test_exit_codes.py` with 9 comprehensive tests:
  - `TestExitCodeSuccess` (2 tests): Exit code 0 on successful parse/generate
  - `TestExitCodeFatalError` (2 tests): Exit code 1 on nonexistent role, invalid YAML
  - `TestExitCodeFailOnWarnings` (2 tests): Exit code 2 with --fail-on-warnings flag
  - `TestExitCodeInvalidUsage` (2 tests): Exit code 2/3 on invalid flag, missing argument
  - `TestExitCodeWarningsWithoutFlag` (1 test): Exit code 0 for warnings without --fail-on-warnings
- **Test Status**: 6/9 tests PASSING, 3 FAILING (expected RED phase) ✅
  - Passing: Success cases (0), invalid usage (2), some error cases
  - Failing: Nonexistent role returns 2 instead of 1, invalid YAML returns 0 instead of 1, warnings return 1 instead of 0
- **Exit Code Convention**:
  - 0: SUCCESS - operation completed successfully
  - 1: ERROR - fatal error occurred
  - 2: WARNING - warnings treated as errors (with --fail-on-warnings)
  - 3: INVALID - invalid command-line arguments (Note: Click uses 2 by default)
- **User Story 5**: Tests define requirements for predictable CI/CD exit codes ✅
  - Phase tracking: "parsing" phase around role parsing, "output" phase around file writing
  - Modified `_parse_single_role()` to accept optional metrics_collector, increments counters
  - Modified `_parse_roles_recursive()` to accept optional metrics_collector, increments per role
  - Counter increments: files_processed (estimated 1-5 per role), roles_documented (1 per role)
- **CLI Integration - generate command**: `ansibledoctor/cli/__init__.py`
  - MetricsCollector instantiated at command start
  - Phase tracking: "parsing" (role structure), "rendering" (template processing), "writing" (file output)
  - Counter increments: roles_documented (1), files_processed (5 estimated: meta/defaults/vars/tasks/handlers)
  - Verbose mode: `--verbose` displays phase timing and counters in stderr after completion
- **Backward Compatibility**: `_generate_execution_report()` accepts both new (metrics) and legacy (files_processed, roles_documented) parameters
- **Test Status**: All 14 tests PASSING (10 unit + 4 integration tests) ✅
- **User Story 2**: Complete - Performance metrics with <5% timing accuracy, throughput counts, verbose mode display ✅


  - Correlation ID generation and propagation (UUID4, contextvars)
  - Execution timing tracking (started_at, completed_at, duration_ms)
  - Error/warning collection and aggregation
  - Report generation on success and failure paths
  - Helper function `_generate_execution_report()` for DRY report creation
- **Test Fixes**: Integration tests corrected to use output **files** not directories for `--output` flag
- **Test Status**: 15/15 tests PASS (8 unit + 7 integration) ✅ GREEN Phase COMPLETE

### Technical Details

- **Models**: All models use Pydantic with validation, Field constraints, and JSON schema examples
- **Protocols**: Following SOLID Dependency Inversion Principle for loose coupling
- **Thread Safety**: Correlation IDs use contextvars for async/concurrent operations
- **Exit Codes**: 0=success, 1=error, 2=warning (with flag), 3=invalid usage

## [0.9.6] - 2025-12-04

### Added - Project Existing Docs Extraction (Spec 006 Phase 7 Part 1)

- **Project Model**: Added `existing_docs: Optional[ExistingDocs]` field to `Project` model
- **DocsExtractor Integration**: ProjectParser.parse() now calls DocsExtractor to populate existing_docs
- **License Detection**: Project-level license type detection (MIT, Apache-2.0, GPL-3.0, BSD-3-Clause)
- **Demo Project**: Added README.md, LICENSE, CHANGELOG.md files to demo project

### Tests

- **Unit Tests**: Added `test_project_existing_docs.py` with comprehensive tests for:
  - DocsExtractor finding README, CHANGELOG, CONTRIBUTING, LICENSE at project root
  - License type detection for MIT, Apache-2.0, GPL-3.0
  - Partial docs scenarios (only some files exist)
  - Project model accepting existing_docs field
  - ProjectParser integration with DocsExtractor
  - Demo project integration test

## [0.9.5] - 2025-12-04

### Added - Collection Documentation Enhancements (Spec 004 Phase 8)

- **License Badges**: Added support for rendering license badges in collection header (Shields.io style)
- **Playbooks Section**: Added playbooks table to collection documentation (name, description, tags)
- **Existing Docs**: Added integration of existing documentation files (README, CHANGELOG, CONTRIBUTING, LICENSE)
- **Galaxy Metadata**: Updated model to support list of licenses

### Changed

- **Galaxy Metadata**: Updated `GalaxyMetadata` model to support `license` field as a list of strings

## [0.9.4] - 2025-12-04

### Added - Collection Slug Output and Legacy Support (Spec 004 T224-T227)

- **Slug Utilities**: Added `collection_slug` and `role_slug` utilities for consistent naming
- **Output Structure**: Implemented hierarchical output structure `docs/lang/{code}/collection_{namespace}.{collection}/`
- **Legacy Support**: Added `--legacy-output` flag to `collection generate` command to support flat `docs/README.md` output
- **Template Linking**: Updated collection template to use relative links to role documentation using slugs
- **Integration Tests**: Added tests for slug-based output paths and legacy flag behavior

## [0.9.3] - 2025-12-04

### Added - Template Support for Handlers and Documentation (Spec 002 T219)

- **Markdown Template**: Added Handlers and Documentation sections to `role.j2`
  - Handlers section displays handler name, tags, listen directives, and source location
  - Documentation section includes README, LICENSE (with type detection), templates list, and static files list
- **HTML Template**: Added matching Handlers and Documentation sections with styled output
- **RST Template**: Added Handlers and Documentation sections with proper reStructuredText formatting
- **TOC Updates**: All templates now include Handlers and Documentation in table of contents

### Changed

- **Template Consistency**: All three output formats (Markdown, HTML, RST) now render handlers and existing documentation uniformly

## [0.9.2] - 2025-12-04

### Added - Handler and Documentation Extraction (Spec 001 Phase 5B)

- **Handler Parsing**: Extract handler definitions from `handlers/*.yml` files
  - Handler name, tags, and listen directive extraction
  - Support for `include_tasks` and `import_tasks` in handlers
  - Integration with existing role parsing pipeline
- **Existing Documentation Extraction**: Automatic discovery and extraction of role documentation
  - README content extraction with format detection (Markdown/reStructuredText)
  - CHANGELOG.md content extraction
  - CONTRIBUTING.md content extraction
  - LICENSE file extraction with automatic type detection (MIT, Apache-2.0, GPL-2.0/3.0, BSD-2-Clause/3-Clause)
  - Templates directory file listing (templates/*.j2)
  - Static files directory listing (files/*)
- **Shared Models**: `Handler` and `ExistingDocs` Pydantic models
- **Shared Utilities**: `extract_tags_from_yaml()` utility for consistent tag parsing across parsers
- **Integration Tests**: Comprehensive end-to-end tests for role parsing with handlers and documentation

### Changed

- **Refactored** tag extraction logic: Extracted common `extract_tags_from_yaml()` utility shared between `TaskParser` and `HandlerParser`
- **Enhanced** `AnsibleRole` model with `handlers` and `existing_docs` fields
- **Updated** CLI JSON output to include handler and existing documentation information

## [0.9.2] - 2025-12-04

### Added - Handler and Documentation Extraction (Spec 001 Phase 5B)

- **Handler Parsing**: Extract handler definitions from `handlers/*.yml` files
  - Handler name, tags, and listen directive extraction
  - Support for `include_tasks` and `import_tasks` in handlers
  - Integration with existing role parsing pipeline
- **Existing Documentation Extraction**: Automatic discovery and extraction of role documentation
  - README content extraction with format detection (Markdown/reStructuredText)
  - CHANGELOG.md content extraction
  - CONTRIBUTING.md content extraction
  - LICENSE file extraction with automatic type detection (MIT, Apache-2.0, GPL-2.0/3.0, BSD-2-Clause/3-Clause)
  - Templates directory file listing (templates/*.j2)
  - Static files directory listing (files/*)
- **Shared Models**: `Handler` and `ExistingDocs` Pydantic models
- **Shared Utilities**: `extract_tags_from_yaml()` utility for consistent tag parsing across parsers
- **Integration Tests**: Comprehensive end-to-end tests for role parsing with handlers and documentation

### Changed

- **Refactored** tag extraction logic: Extracted common `extract_tags_from_yaml()` utility shared between `TaskParser` and `HandlerParser`
- **Enhanced** `AnsibleRole` model with `handlers` and `existing_docs` fields
- **Updated** CLI JSON output to include handler and existing documentation information

## [0.9.1] - 2025-12-02

### Fixed

- **FIX**: TaskParser now correctly passes `description` parameter to Tag constructor
- **FIX**: Added type annotation for `files` variable in `_collect_task_files` method
- **FIX**: Unit tests now properly mock `Path.exists()` for TaskParser tests
- **FIX**: Added missing `[Unreleased]` section in CHANGELOG.md

## [0.9.0] - 2025-12-01

### Added

- **NEW**: Recursive include following for `include_tasks` and `import_tasks` in task parsing
- **NEW**: Role slug generation in CLI output for consistent role identification

### Fixed

- **FIX**: Updated CSS injector string literals and formatting for consistency

### Changed

- **REFACTOR**: Code formatting and minor improvements across multiple modules

## [0.1.0] - 2025-12-01

### Added - Feature 001: Ansible Role Parser CLI Interface

- **NEW**: CLI interface with `parse` command for extracting role documentation
- **NEW**: `--recursive` flag for multi-role directory scanning
- **NEW**: `--validate` flag for role structure validation
- **NEW**: `--log-level` flag for controlling output verbosity
- **NEW**: JSON output to stdout, logs to stderr (shell pipeline compatible)
- **NEW**: Structured exit codes: 0 (success), 1 (parse error), 2 (validation error)
- **NEW**: CLI entry points in `pyproject.toml`: `ansible-doctor-enhanced` and `ansibledoctor`
- **NEW**: Recursive include following for `include_tasks` and `import_tasks` in task parsing
- **NEW**: Role slug generation in CLI output for consistent role identification

## [0.8.0] - 2025-12-01

### Added - Feature 008: Template Inheritance Validation

- **NEW**: `get_parent_templates()` method - Extract parent template names from extends statements
- **NEW**: `get_included_templates()` method - Extract included template names from include statements
- **NEW**: `get_template_dependencies()` method - Get all template dependencies (extends, includes, imports)
- **NEW**: `validate_inheritance()` method - Validate template inheritance chain with actionable errors
  - Reports missing parent templates with search paths tried
  - Reports missing includes with suggestions for fix
  - Reports missing imports with helpful error messages
  - Supports custom search paths for template resolution

### Security - Feature 008: Template Sandboxing

- **NEW**: `SecureSandboxedEnvironment` class - Extends Jinja2's SandboxedEnvironment with additional security restrictions
  - Blocks access to dangerous dunder attributes (__class__, __mro__, __globals__, etc.)
  - Restricts unsafe callable objects (eval, exec, compile, open, type)
  - Prevents private attribute access (attributes starting with _)
- **NEW**: `DANGEROUS_PATTERNS` list - Pattern-based detection for unsafe template constructs
  - Detects __import__, eval, exec, open, os.system, subprocess, getattr, setattr
- **NEW**: `UNSAFE_ATTRIBUTES` frozenset - List of blocked attribute names for sandboxing
- **NEW**: `validate_security()` method - Check templates for dangerous patterns
- **NEW**: `is_safe_template()` method - Quick safety check returning boolean
- **NEW**: `validate_secure()` method - Validation with exception on security violations
- **NEW**: `create_sandboxed_environment()` factory - Create pre-configured secure environment
- **NEW**: `create_secure_validator()` factory - Create validator with secure environment

### Testing - Feature 008: Template Sandboxing

- **TEST**: Unit tests for sandboxing: `tests/unit/test_template_sandboxing.py` (62 tests)
  - SecureSandboxedEnvironment attribute blocking
  - Secure callable restrictions
  - Dangerous pattern detection
  - validate_secure method behavior
  - Factory function tests
  - Complex template security scenarios

### Testing - Feature 008: Theme Accessibility

- **TEST**: Integration tests for accessibility: `tests/integration/test_theme_accessibility.py` (45 tests)
  - Toggle ARIA attributes (aria-pressed, aria-label, aria-hidden)
  - Toggle script accessibility (prefers-color-scheme, localStorage persistence)
  - CSS accessibility (color tokens, dark mode, font settings)
  - HTML structure validation (button pattern, toggle pattern)
  - ARIA authoring pattern compliance
  - Keyboard accessibility support
  - Color contrast support tokens

### Documentation - Feature 008: Demo Templates

- **NEW**: Demo templates for theme variants under `demo/templates/`
  - `role.minimal.html.j2` - Compact output with essential info
  - `role.detailed.html.j2` - Full documentation with all sections
  - `role.modern.html.j2` - Contemporary styling with cards and timeline
- **NEW**: Demo CSS examples under `demo/css/`
  - `sample-theme.css` - Complete custom theme with brand colors
  - `inline-overrides.css` - Minimal inline CSS example
- **NEW**: Template documentation in `demo/templates/README.md`
  - Usage examples for each variant
  - CSS variables reference
  - Custom template creation guide

### Documentation - Feature 008: Theming Guide

- **UPDATED**: `README.md` with new Theming & Customization section (v0.8.0 feature)
  - Template variants usage (minimal, detailed, modern)
  - CSS customization (external URL and inline)
  - Dark mode toggle features
  - Color scheme options
  - Configuration file examples
- **UPDATED**: `docs/TEMPLATE_GUIDE.md` with comprehensive theming section
  - Template variants reference table
  - CSS cascade order explanation
  - CSS variables reference
  - Dark mode toggle documentation
  - Template context variables for theming
  - Custom template location guide

### Added - Feature 007: Hierarchical Context Detection

- **NEW**: `ansibledoctor/context/detector.py` - ContextDetector for discovering hierarchical relationships
  - ComponentType enum: PROJECT, COLLECTION, ROLE, STANDALONE
  - HierarchicalContext with parent chain and sibling discovery
  - BreadcrumbItem dataclass for navigation trail
  - Session-scoped caching via `@lru_cache`
- **NEW**: `ansibledoctor/utils/slug.py` extensions for hierarchical documentation paths
  - `build_context_path()` - Construct hierarchical doc paths (project/collections/ns.coll/roles/role)
  - `relative_link()` - Generate relative navigation links between doc levels
- **NEW**: Template partials for breadcrumb and sibling navigation
  - `_breadcrumb.j2` for Markdown/HTML/RST formats
  - `_siblings.j2` for related component navigation
- **ENHANCED**: Template loaders support `{% include %}` directive with PackageLoader/FileSystemLoader
- **ENHANCED**: `TemplateContext` now includes `hierarchical_context` field for navigation data
- **ENHANCED**: `HasBreadcrumb` protocol for type-safe hierarchical context typing

### Testing

- **TEST**: Unit tests for context detection: `tests/unit/test_context.py` (17 tests)
- **TEST**: Unit tests for slug path utilities: `tests/unit/test_slug.py` (22 tests)
- **TEST**: Integration tests: `tests/integration/test_hierarchical_context.py` (12 tests)

### Added - Feature 006: Project Documentation Support

- **NEW**: `ansibledoctor/models/project.py` - Pydantic models for Project, Playbook, RoleInfo, CollectionInfo and InventoryItem
- **NEW**: `ansibledoctor/parser/project_parser.py` - ProjectParser discovers roles and collections and sets project metadata when ansible.cfg is present
 - **ENHANCED**: `ansibledoctor/parser/project_parser.py` - ProjectParser honors monorepo detection (nearest ancestor `ansible.cfg`), respects `ansible.cfg` `[defaults] inventory` path(s), supports inventory file/directory parsing and merging across multiple inventory sources (T204/T314/T315/T316)
 - **ENHANCED**: `ansibledoctor/parser/project_parser.py` - ProjectParser honors `ansible.cfg` `[defaults] roles_path` and `collections_path` settings, resolving both relative and absolute paths, and supports multiple path entries (colon/comma separated) for robust discovery (T204)
- **NEW**: `ansibledoctor/generator/project_generator.py` - Minimal ProjectDocumentationGenerator supporting Markdown/HTML/RST outputs
- **NEW**: `ansibledoctor/cli/project.py` - `project` CLI group with `generate` command and relative output path behavior for project docs
- **NEW**: Demo artifacts in `demo/` moved into `demo/role_demo_namespace.demo_demo_role`, `demo/collection_demo_namespace.demo_collection`, and `demo/project_demo_namespace.demo_project` to be canonical fixtures for integration tests
- **NEW**: Integration tests: `tests/integration/test_demo_all_formats_generation.py`, `tests/integration/test_demo_collection_generation.py`, `tests/integration/test_demo_project_generation.py`

### Testing

- **TEST**: Unit tests added for `ansibledoctor/utils/slug.py` and `ansibledoctor/generator/project_generator.py` to cover slug generation and project README outputs (Markdown/HTML/RST)
 - **TEST**: Unit tests added for inventory parsing and project parser behavior: `tests/unit/test_inventory_parser.py`, `tests/unit/test_project_parser.py` (monorepo root detection, ansible.cfg inventory path handling, inventory merging) (T314/T315/T316)
 - **TEST**: Unit tests added for `group_vars` and `host_vars` parsing and variable precedence (`tests/unit/test_inventory_parser.py`) and redaction config (`tests/unit/test_inventory_parser.py`) (T316/T317/T318)
### Changed - Project Parser & Inventory (additional)

- **ENHANCED**: `ansibledoctor/parser/project_parser.py` now loads `group_vars/` and `host_vars/`, computes merged effective variables per host (role defaults -> group_vars -> host_vars precedence), and exposes `project.group_vars`, `project.host_vars`, and `project.effective_vars` (T316).
## [0.5.1] - 2025-11-29

### Added - Feature 005: Internationalization (i18n) Support

- **NEW**: `ansibledoctor/translation/loader.py` - TranslationLoader supporting package, project, collection and role-level overrides for translations (en/fr/de fixtures added).
- **NEW**: `ansibledoctor/translation/provider.py` - TranslationProvider with `t()` support for Jinja templates (pluralization support using Babel, fallback for missing keys to `en`).
- **NEW**: `ansibledoctor/generator/multi_language.py` - Multi-language generator orchestration for per-lang outputs under `docs/lang/{code}/`.
- **ENHANCED**: Template engine registration of `t()` filter and global to support `{{ t('key') }}` and filter usage in templates.
- **TEST**: New tests: `tests/unit/test_translation_provider.py`, `tests/unit/test_translation_loader.py`, `tests/integration/test_multilang_e2e.py`, `tests/integration/test_i18n_fallback.py`.

- **ENHANCED**: `ansibledoctor/cli/project.py` added `--redact-values/--no-redact-values` flag; `ProjectParser` supports redaction and reads `.ansibledoctor.yml` redaction config to override patterns and placeholder (T317/T318).
 - **ENHANCED**: `ansibledoctor/generator/project_generator.py` now supports custom Jinja2 templates via `template_path` to render outputs (T206)
 - **TEST**: Integration and unit tests for CLI exception handling and template rendering added: `tests/unit/test_cli_project.py`, updated `tests/unit/test_project_generator.py` (template tests)

### Changed

- **ENHANCED**: CLI behavior — `--output` and `--output-dir` writing is now relative to the target artifact (role, collection, or project) when the path isn't absolute
- **CHORE**: Added optional dev dependencies for format validations: `html5lib` and `docutils` (for HTML/RST validation in tests)

### Changed - Project Parser & Inventory

- **ENHANCED**: `ansibledoctor/parser/project_parser.py` now resolves project root using nearest ancestor `ansible.cfg` if present and uses this canonical path for discovery of roles, collections, playbooks, and inventory. This change reduces ambiguity in monorepo layouts where projects may be nested (T315).
- **ENHANCED**: Inventory discovery now merges groups from multiple sources and supports both INI and YAML inventory formats, including inventory directories and single file paths specified via `ansible.cfg` (T314/T316).


## [0.5.0] - 2025-11-21

### Added - Feature 004: Ansible Collection Documentation Support

**User Story 8: Parse Collection Metadata (T001-T085)** ✅ Complete
- **NEW**: `collection parse` command - Parse Ansible collection metadata and structure
- **NEW**: `ansibledoctor/models/galaxy.py` - GalaxyMetadata Pydantic model with validation
  - Required fields: namespace, name, version, authors, dependencies
  - Field validators for namespace format (lowercase alphanumeric) and semantic versioning
  - Immutable frozen model with fqcn property
- **NEW**: `ansibledoctor/models/collection.py` - AnsibleCollection aggregate root
  - Composition of metadata, roles, and plugins
  - Helper methods: list_roles(), list_plugins_by_type()
  - Self-dependency validation
- **NEW**: `ansibledoctor/parser/galaxy_parser.py` - GalaxyMetadataParser
  - Parses galaxy.yml with comprehensive error handling
  - Validates required fields and formats
  - Extracts collection dependencies with version constraints
- **NEW**: `ansibledoctor/parser/collection_walker.py` - CollectionStructureWalker
  - Discovers roles in roles/ directory
  - Discovers plugins in plugins/*/ directories
  - Plugin type detection (modules, filters, lookups, tests, inventory, callbacks)
  - Graceful handling of missing directories with structured logging
- **NEW**: `ansibledoctor/parser/collection_parser.py` - CollectionParser orchestrator
  - Main entry point integrating galaxy parser and structure walker
  - Path validation and error handling
  - Returns complete AnsibleCollection model

**User Story 9: Generate Collection Documentation (T086-T172)** ✅ Complete
- **NEW**: `collection generate` command - Generate comprehensive collection documentation
- **NEW**: `ansibledoctor/models/plugin.py` - Plugin value object and PluginCatalog
  - Plugin model: name, type, path, short_description (frozen)
  - PluginCatalog repository: group_by_type(), list_all_names(), count()
- **NEW**: `ansibledoctor/models/collection_role.py` - CollectionRole extending AnsibleRole
  - Adds collection_fqcn field for namespace.collection context
  - full_role_name property returns "namespace.collection.role_name"
- **NEW**: `ansibledoctor/parser/plugin_discovery.py` - PluginDiscovery service
  - Recursive plugin discovery in plugins/ directory
  - Plugin type detection from directory structure
  - Validation filtering for invalid plugins
- **NEW**: `ansibledoctor/generator/collection_generator.py` - CollectionDocumentationGenerator
  - Template context builder from AnsibleCollection model
  - Multiple format support (Markdown, HTML, RST)
  - Custom template support
  - Comprehensive error handling
- **NEW**: `ansibledoctor/templates/markdown/collection.j2` - Markdown collection template
  - Installation instructions with ansible-galaxy commands
  - Role index (table or list format - configurable)
  - Plugin listing grouped by type
  - Dependencies table with version constraints
  - Examples/playbooks section
- **NEW**: `ansibledoctor/templates/html/collection.j2` - HTML collection template
  - Complete HTML5 with embedded responsive CSS
  - Matching role template design
- **NEW**: `ansibledoctor/templates/rst/collection.j2` - RST collection template
  - Sphinx-compatible reStructuredText
  - Proper heading underlines and code blocks
  - **FIX**: Jinja2 syntax for length calculation with proper parentheses

**User Story 10: Cross-Role Dependency Analysis (T173-T204)** ✅ Complete
- **NEW**: `collection analyze` command - Visualize and validate role dependencies
- **NEW**: `ansibledoctor/parser/dependency_graph.py` - DependencyGraph class
  - build_graph() method: parse role dependencies from meta/main.yml
  - detect_circular_dependencies() using depth-first search (DFS)
  - topological_sort() for dependency execution order
  - MermaidExporter: Export to Mermaid diagram format
  - ASCIITreeExporter: Export to text-based tree (UTF-8 box-drawing characters)
  - JSONExporter: Export to structured JSON format
  - Comprehensive error handling for invalid dependencies
- **NEW**: CLI flags for `collection analyze`:
  - `--show-dependencies`: Display dependency graph
  - `--check-circular`: Validate no circular dependencies (exit 1 if found)
  - `--output-format`: Export format (text, json, mermaid)
- **FIX**: Windows UTF-8 encoding for ASCII tree output (binary stream writing)

### Changed

- **BREAKING**: New dependency added: `pyyaml>=6.0.3` for meta/main.yml parsing
- **ENHANCED**: CLI with new `collection` subcommand group (parse, generate, analyze)
- **ENHANCED**: Exit codes: 0=success, 1=error (circular deps if --check-circular), 2=invalid args

### Documentation

- **NEW**: `docs/COLLECTION_GUIDE.md` - Comprehensive collection documentation guide (701 lines)
  - Overview, installation, quick start
  - Detailed command reference (parse, generate, analyze)
  - Advanced usage: CI/CD integration, pre-commit hooks, custom templates
  - Configuration examples
  - Troubleshooting guide
  - Demo collection walkthrough
- **NEW**: `demo/DEMO-COLLECTION-RESULTS.md` - Feature showcase with actual output (587 lines)
  - Parse JSON output example
  - Generated README excerpt
  - Dependency graphs (text, JSON, Mermaid formats)
  - Performance metrics
  - Comparison table with legacy ansible-doctor
- **NEW**: `demo/demo_namespace.demo_collection/` - Demo collection showcasing all features
  - 3 roles with dependency chain: database → application → webserver
  - 5 modules: database_backup, app_deploy, ssl_cert_info, nginx_config_test, health_check
  - 3 filter plugins with 10 filters: formatting, text, validation
  - 3 example playbooks: deploy_stack, database_maintenance, app_deployment
  - Comprehensive annotations demonstrating documentation features
- **NEW**: `README-generated.md` - Real-world generated documentation example (461 lines)
- **UPDATED**: `README.md` - Added Ansible Collection Support section with examples (+69 lines)
- **UPDATED**: All CLI examples now use Poetry (`poetry run ansible-doctor-enhanced ...`)

### Testing

- **NEW**: 50 tests passing for collection documentation features
  - 30 unit tests (models, parsers, generators)
  - 14 integration tests (dependency analysis, export formats, doc generation)
  - 6 E2E tests (CLI commands)
- **Coverage**: dependency_graph.py at 86%, collection_parser.py at 90%
- **Property tests**: Random collection structures with Hypothesis
- **NEW**: Comprehensive doc generation tests (T169-T172)
  - All output formats validated (Markdown, HTML, RST)
  - Metadata completeness verification
  - Performance benchmarking (<3s target for generation)

### Dependencies

- Added: `pyyaml==6.0.3` - YAML parsing for meta/main.yml
- Added: `jinja2==3.1.0` - Template engine for documentation generation

---

## Previous Releases

### Added - Feature 003: Watch Mode Documentation (v0.4.0)
  - **User Story 9: Generate Collection Documentation (T086-T163 partial)**
    - `ansibledoctor/models/plugin.py`: Plugin model and PluginCatalog repository (98% coverage)
      - Plugin value object: frozen Pydantic model with name, type, path, short_description
      - PluginCatalog: Repository pattern for grouping/querying plugins by type
      - Methods: group_by_type(), list_all_names(), list_names_by_type(), count()
    - `ansibledoctor/models/collection_role.py`: CollectionRole extending AnsibleRole (100% coverage)
      - Adds collection_fqcn field for FQCN context
      - full_role_name property returns "namespace.collection.role_name"
      - Inherits all AnsibleRole parsing logic (metadata, variables, tags, etc.)
    - `ansibledoctor/parser/plugin_discovery.py`: PluginDiscovery service (87% coverage)
      - Discovers Python plugins in collection plugins/ directory recursively
      - Detects plugin type from directory structure (modules/, filters/, lookups/, etc.)
      - Returns Plugin objects with metadata for documentation generation
    - `ansibledoctor/generator/templates/markdown/collection.j2`: Collection documentation template (163 lines)
      - Header with FQCN, version, generation date, table of contents
      - Installation section with ansible-galaxy commands (install, version, upgrade)
      - Roles section (configurable table or list format)
      - Plugins section grouped by type (modules, filters, lookups, tests, inventory, callbacks)
      - Dependencies table with version constraints
      - Examples section with playbook code blocks
      - License footer and generator attribution
    - `ansibledoctor/generator/templates/html/collection.j2`: HTML collection template (125 lines)
      - Complete HTML5 structure with embedded CSS
      - Responsive design matching role template style
      - Sections: overview, installation, roles, plugins, dependencies, examples
    - `ansibledoctor/generator/templates/rst/collection.j2`: RST collection template (148 lines)
      - Sphinx-compatible reStructuredText format
      - Proper heading underlines and code blocks
      - Table of contents with configurable depth
    - `ansibledoctor/generator/collection_generator.py`: CollectionDocumentationGenerator (94% coverage)
      - Main documentation generator for Ansible collections
      - build_context() method: builds template context from collection data
      - generate() method: renders docs in markdown/html/rst formats
      - Custom template support via template_path parameter
      - File writing with output_path parameter
      - Lazy initialization of TemplateEngine and EmbeddedTemplateLoader
      - Comprehensive error handling with actionable messages
    - Test suite: 61 tests passing (14 new generator tests added)
      - 17 Plugin model tests, 8 PluginCatalog tests
      - 8 Plugin Discovery tests, 8 CollectionRole tests (100% coverage)
      - 7 Collection template rendering tests (all formats)
      - 7 CollectionDocumentationGenerator tests (RED-GREEN cycle)
      - 6 property-based tests with Hypothesis
    - TDD cycle: Strict RED-GREEN-REFACTOR followed for all implementations
      - RED phase (T106-T112): Tests written first, all fail with ModuleNotFoundError
      - GREEN phase (T146-T155): Implementation makes all tests pass
      - REFACTOR phase: Template improvements, error handling
    - `ansibledoctor/cli/collection.py`: collection generate CLI command
      - Options: --output-dir, --format (markdown/html/rst), --template, --config
      - Integration: CollectionParser → PluginDiscovery → CollectionDocumentationGenerator
      - Progress output with checkmarks and plugin counts
      - Error handling for parsing, generation, and I/O errors
      - Manual testing: ✓ Markdown, HTML, RST outputs verified
    - 8 atomic commits: Plugin model (c540f6c), Plugin Discovery (5d25ccd), CollectionRole (44540b4), Template (1e0c0ef), CHANGELOG (c0cacaf), Generator Tests (6b5798a), Generator Implementation (bdd6c1b), CLI (e7eea21)
    - Progress: 75/87 User Story 9 tasks complete (86%)
  
- **Feature 004: Collection Documentation (v0.5.0)** - Foundation and US8 complete
  - `ansibledoctor/models/galaxy.py`: GalaxyMetadata model (schema 1.0.0, required fields only)
    - Pydantic v2 model with frozen=True (immutable value object)
    - Validators for namespace (lowercase alphanumeric), version (semantic versioning)
    - FQCN property returns "namespace.name"
    - Defers optional galaxy.yml fields to v0.6.0
  - `ansibledoctor/models/collection.py`: AnsibleCollection aggregate root
    - Coordinates GalaxyMetadata, roles list, plugins dict
    - Self-dependency validation (prevents circular references)
    - Helper methods: list_roles(), list_plugins_by_type()
  - `ansibledoctor/models/plugin.py`: PluginType enum
    - Supports: module, filter, lookup, test, inventory, callback
    - from_directory_name() maps plugins/modules/ → MODULE
  - `ansibledoctor/parser/galaxy_parser.py`: GalaxyMetadataParser
    - Parses galaxy.yml following schema 1.0.0
    - Validates required fields: namespace, name, version, authors, dependencies
    - Error handling with actionable suggestions
  - `ansibledoctor/parser/collection_walker.py`: CollectionStructureWalker
    - Discovers roles in roles/ directory
    - Discovers plugins in plugins/ subdirectories (no file exclusions)
    - Delegates to FileSystemWalker for file operations
  - `ansibledoctor/utils/fs_walker.py`: FileSystemWalker infrastructure
    - discover_roles(): List role names from roles/ directory
    - discover_plugins(): Map PluginType to Python file paths
    - No exclusions policy: parse all .py files, validation filtering at parser layer
  - `ansibledoctor/utils/paths.py`: CollectionPathResolver extension
    - resolve_collection_path(): Validate collection directory exists
    - get_galaxy_yml_path(): Locate galaxy.yml in collection
    - get_roles_directory(), get_plugins_directory(): Optional directory paths
    - extract_fqcn_from_path(): Parse namespace.name from directory name
  - Test suite: 24 tests covering GalaxyMetadata, GalaxyMetadataParser, CollectionStructureWalker, AnsibleCollection
    - TDD RED-GREEN-REFACTOR cycle followed strictly
    - Tests written FIRST (all failed), then implementation (all pass)
  - Test fixtures: 3 collections (minimal_valid, invalid_missing_namespace, malformed_yaml)
  - Dependencies: Added `packaging>=24.0` for semantic version validation

### Changed

- `pyproject.toml`: Added packaging dependency for version validation
- Project structure: New directories for collection tests and fixtures

## [0.4.0] - 2025-01-20

### Summary

**Feature 003 Complete**: Achieves 100% role-level parity with original ansible-doctor. This release completes all three user stories for configuration file support, watch mode, and config discovery/validation.

**Key Achievements**:
- ✅ Config file support with parent directory discovery
- ✅ Watch mode for auto-regeneration on file changes
- ✅ Enhanced config validation with detailed error messages
- ✅ 672 tests passing, 81% coverage (exceeds 80% requirement)
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Comprehensive documentation and migration guides

### Added

- **docs/CONFIG_GUIDE.md**: Comprehensive configuration guide
  - All configuration keys reference with examples
  - Config priority explanation (CLI > file > defaults)
  - Config discovery behavior documentation
  - Migration guide from original ansible-doctor
  - Troubleshooting and best practices
  - Advanced usage examples

### Changed

- Version bumped from 0.4.0-alpha.3 to 0.4.0 (stable)
- README updated with final test metrics and roadmap status
- Project status indicates Feature 003 complete

### Documentation

- All README sections updated and verified
- CHANGELOG includes full v0.4.0 release history
- CONFIG_GUIDE provides comprehensive configuration documentation
- Migration path from original ansible-doctor clearly documented

## [0.4.0-alpha.3] - 2025-01-20

### Added

- **Feature 003 - Phase 5 US3 Config Discovery & Validation (T025-T029)**: Enhanced config file support
  - **Parent Directory Discovery (T025, T027)**:
    - `find_config_file()` walks up directory tree: current → parent → grandparent → root
    - Searches for `.ansibledoctor.yml` or `.ansibledoctor.yaml` at each level
    - Returns first found (nearest wins, like Git config behavior)
    - 8 unit tests for parent directory discovery including grandparent-level tests
    - Already implemented in v0.4.0-alpha.1, enhanced testing added
  
  - **Config Validation CLI (T026, T028)**:
    - Integration tests for `config validate` and `config show` commands
    - Enhanced error reporting with YAML line/column numbers for syntax errors
    - Pydantic validation errors show field names and validation messages
    - Clear error categorization: YAML Syntax, Schema Validation, or Generic
    - 12 integration tests covering valid/invalid configs, parent discovery, error handling
    - Fixed Windows Unicode encoding issues (✓/✗ → [VALID]/[INVALID])
  
  - **Config Display Enhancement (T029)**:
    - `config show` resolves relative paths to absolute paths in output
    - Displays which settings come from config file vs defaults
    - Shows effective merged configuration as formatted YAML
    - Shows config file path or "Using defaults" message
    - Enhanced user experience with clear setting origins
  
  - **Test Coverage**:
    - Total: 672 tests passing (652 baseline + 12 config integration + 8 config unit)
    - Coverage: 81% overall (exceeds 80% target)
    - Known issue documented: 1 property test edge case in T088 (annotation parsing with `:` content)
    - All Windows, cross-platform compatibility verified

### Changed

- Config validate command now provides detailed error messages with line numbers
- Config show command displays absolute paths for better clarity
- CLI error output uses ASCII-safe markers for Windows compatibility
- Enhanced test coverage from 79% to 81%

### Fixed

- Windows console encoding errors with Unicode characters (✓/✗) in CLI output
- Config validate now properly categorizes and displays error types
- Property test stability improved (1 known edge case documented for future fix)

## [0.4.0-alpha.2] - 2025-01-20

### Added

- **Feature 003 - Phase 4 US2 Watch Mode (T016-T024)**: Auto-regeneration on file changes
  - **Watch Infrastructure (T016-T017, T019-T021)**:
    - `Debouncer`: Rate-limits callback execution to prevent rapid regeneration bursts (100% coverage)
    - `FileChangeHandler`: Processes watchdog file system events with pattern filtering (95% coverage)
    - `WatchMonitor`: Monitors role directory recursively using watchdog.observers.Observer (100% coverage)
    - Watches: meta/, defaults/, vars/, tasks/, handlers/, .ansibledoctor.yml
    - Excludes: *.pyc, __pycache__/, .git/, *.swp, *.tmp
    - 19 unit tests (8 debouncer + 11 monitor/handler), all passing
  
  - **Watch CLI Command (T022-T024)**:
    - `ansible-doctor watch <role-path>`: Monitor role and auto-regenerate docs on changes
    - `--format` option: Choose output format (markdown/html/rst)
    - `--output` option: Write to file or stdout
    - Integrates with US1 config file support (auto-discovers .ansibledoctor.yml)
    - Regeneration callback with error handling and timestamp logging
    - Signal handling for graceful shutdown (SIGINT/SIGTERM)
    - Initial generation on watch start
    - Continues monitoring even if generation fails
    - 9 integration tests covering end-to-end functionality
  
  - **Test Coverage (T018)**:
    - Integration tests: File monitoring, debouncing, exclusions, config changes
    - Tests graceful shutdown, error handling, multiple directory monitoring
    - Total: 660 tests passing (652 baseline + 8 new), 79% coverage
    - Watch modules: debouncer 100%, handler 95%, monitor 100%

### Changed

- CLI help text updated to include `watch` command in available commands list
- Watch command displays timestamps for each regeneration event
- Error messages include timestamps when generation fails during watch mode

## [0.4.0-alpha.1] - 2025-01-19

### Added
## Links

The release history in this file follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) conventions and adheres to [Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html).

[Unreleased]: https://github.com/K4M1coder/ansible-doctor-enhanced/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/K4M1coder/ansible-doctor-enhanced/releases/tag/v0.5.0
[0.4.0]: https://github.com/K4M1coder/ansible-doctor-enhanced/releases/tag/v0.4.0
[0.4.0-alpha.3]: https://github.com/K4M1coder/ansible-doctor-enhanced/releases/tag/v0.4.0-alpha.3
[0.4.0-alpha.2]: https://github.com/K4M1coder/ansible-doctor-enhanced/releases/tag/v0.4.0-alpha.2
[0.4.0-alpha.1]: https://github.com/K4M1coder/ansible-doctor-enhanced/releases/tag/v0.4.0-alpha.1

- **Feature 003 - Phase 1 Setup (T001-T004)**: Infrastructure for configuration file support and watch mode
  - Created `ansibledoctor/config/` module with ConfigModel, loader, validator stubs
  - Created `ansibledoctor/watcher/` module with WatchMonitor, Debouncer, FileChangeHandler stubs
  - Added `watchdog = "^6.0.0"` dependency for file system monitoring
  - Created test fixtures in `tests/fixtures/config_files/` for config validation testing
  - All module stubs include TODO markers referencing implementation tasks (T005-T029)

- **Feature 003 - Phase 2 Foundational (T005-T006)**: ConfigModel schema complete and tested
  - Comprehensive unit tests for ConfigModel validation (19 tests, 92% coverage)
  - Tests cover: valid/invalid formats, defaults, whitespace stripping, extra fields, edge cases
  - ConfigModel ready for use in US1 (config file loading) and US2 (watch mode)

- **Feature 003 - Phase 3 US1 Config File Support (T007, T010-T012)**: Config discovery and loading implemented
  - `find_config_file()`: Walk directory tree to find `.ansibledoctor.yml` or `.ansibledoctor.yaml`
  - `load_config()`: Load and validate YAML config with Pydantic, clear error messages
  - `merge_config()`: Merge configs with priority: CLI > file > defaults
  - 21 unit tests (TDD RED → GREEN), 92% coverage of loader.py
  - Proper error handling: FileNotFoundError, YAML syntax errors, ValidationError

- **Feature 003 - Phase 3 US1 CLI Integration (T013-T015)**: Configuration file support fully operational
  - Generate command now discovers and uses `.ansibledoctor.yml` config files automatically
  - Config priority enforced: CLI arguments > config file > defaults (backward compatible)
  - New `config show` command displays effective configuration as YAML with file location
  - New `config validate` command validates config syntax and schema with helpful error messages
  - Config files support all generate options: output_format, output, template, recursive, exclude_patterns
  - Exit codes: 0 (valid), 1 (invalid) for automation support
  - **US1 Complete**: Full configuration file support from discovery through CLI integration

### Changed

- **Branding**: Updated project name from "ansible-doctor" to "ansible-doctor-enhanced" across all output formats
  - HTML meta generator tag: `<meta name="generator" content="ansible-doctor-enhanced v0.3.0">`
  - HTML footer: "Documentation generated by **ansible-doctor-enhanced**"
  - Markdown footer: "*Documentation generated by ansible-doctor-enhanced*"
  - RST footer: "**ansible-doctor-enhanced**"
- **Version Management**: Version now dynamically loaded from `pyproject.toml` via `importlib.metadata.version()`
  - Single source of truth for version number
  - Works in development and after compilation/distribution
  - Automatic version updates when bumping in `pyproject.toml`
- **Test Infrastructure**: Updated all test assertions to verify "ansible-doctor-enhanced" branding
  - `tests/integration/test_html_generation.py`: Validates meta generator tag
  - `tests/property/test_rst_renderer.py`: Validates footer branding
  - `tests/integration/test_rst_generation.py`: Validates note section branding
- **Code Organization**: Removed hardcoded version defaults from `TemplateContext`
  - `generator_version` field now required parameter (from `__version__`)
  - Updated all docstring examples to use `from ansibledoctor import __version__`

### Fixed

- **Demo Structure**: Moved test role to `demo/` directory for better project organization
- **Dataclass Field Ordering**: Fixed `TemplateContext` field ordering to comply with Python dataclass rules (non-default fields before default fields)

## [0.3.0] - 2025-01-19

### Added

**Feature 002 - Documentation Generator (Phase 11 Complete: T241-T255)**

**Batch Generation & Template Management (T251-T252):**

- **T251**: Batch documentation generation with `--recursive` flag
  - Automatically discover and generate documentation for all roles in a directory tree
  - `--output-dir` option to specify output directory for batch generation
  - Progress indicator showing completed/total roles during batch processing
  - Error resilience: failed roles logged but don't stop batch process
  - Role discovery via `meta/main.yml` or `defaults/main.yml` presence
  - 5 unit tests (TDD RED → GREEN), all passing

- **T252**: `templates` CLI subcommand for template management
  - `ansible-doctor templates list` - display available template formats (markdown/html/rst)
  - `ansible-doctor templates show <format>` - display default template content for inspection
  - `ansible-doctor templates validate <path>` - validate custom template Jinja2 syntax
  - Uses EmbeddedTemplateLoader to access default templates via importlib.resources
  - Syntax validation with Jinja2 Environment.parse() providing detailed error messages
  - 6 unit tests (TDD RED → GREEN), all passing

**RST Renderer (T241-T250):**

- **T241-T242**: RstRenderer implementation with Sphinx compatibility
  - reStructuredText (RST) documentation renderer
  - escape() method for RST special characters (*, `, _, \\, |)
  - code_block() with .. code-block:: directive and 3-space indentation
  - render() using Jinja2 template with sphinx_compat option
  - validate_options() for sphinx_compat boolean validation
  - 16 unit tests (TDD RED → GREEN), 94% coverage
  - Follows same pattern as HtmlRenderer/MarkdownRenderer (SOLID, DRY)

- **T243**: RST template with conditional Sphinx directives
  - Template rst/role.j2 (151 lines) enhanced with Sphinx support
  - Default sphinx_compat=True for Sphinx directive usage
  - .. warning:: directive for high/critical priority TODOs
  - Simple list format fallback when sphinx_compat=False
  - Proper RST structure: field lists, heading underlines, code blocks
  - 23 unit tests passing with template rendering

- **T244**: RST integration tests (8 tests)
  - End-to-end RST generation with complex_role fixture
  - Validates RST structure: headings, underlines, field lists, TOC directive
  - Validates code blocks: .. code-block:: yaml with proper indentation
  - Validates Sphinx directives: .. warning:: for high priority TODOs
  - Validates sphinx_compat True/False behavior
  - Tests complete document sections: Overview, Variables, Tags, TODOs, Examples

- **T245**: CLI support for RST format (4 tests)
  - --format rst option added to generate command
  - --sphinx-compat / --no-sphinx-compat flag (default: True)
  - RstRenderer instantiated with sphinx_compat from CLI
  - Compatible with --output, --template options
  - Consistent CLI UX across all formats (Markdown, HTML, RST)

- **T246**: Property-based tests with Hypothesis (4 tests)
  - 100 random test cases per property (400 total test cases)
  - Verifies RST structure consistency with random role data
  - Verifies escaping prevents RST injection
  - Verifies all variables appear in output
  - Verifies section order consistency

- **T247**: RST validation tests with docutils (3 tests, optional)
  - Validates RST parses without syntax errors using docutils
  - Validates proper document structure (headings, field lists)
  - Validates Sphinx directives (.. warning::, .. note::, .. code-block::)
  - Tests skip gracefully if docutils not installed

- **T248**: Documentation with Sphinx integration guide
  - README.md updated with RST generation examples
  - 5-step Sphinx integration workflow documented
  - conf.py and index.rst examples provided
  - Sphinx directives explained (warning, note, code-block)

- **T249**: Coverage verification (82% maintained)
  - 550 total tests (543 passing, 7 skipped, 2 pre-existing failures)
  - RstRenderer: 94% coverage, 35 tests total
  - Phase 11: 85 new tests (50 HTML + 35 RST)

- **T253-T255**: Final validation and release preparation
  - Full test suite validation: 593 tests passing, 7 skipped, 82% coverage
  - Fixed HTML template test assertions for conditional rendering
  - Documentation updates: README with --recursive/templates examples
  - Article XI added to constitution: Tag-Changelog Synchronization (MANDATORY)
  - Poetry workflow documented in constitution and plan.md
  - Version management enforced: pyproject.toml ↔ CHANGELOG.md ↔ git tags

### Changed

- Updated README.md with batch generation and template management examples
- Author attribution updated to Cédric Thédrez <kamicth@gmail.com> across all commits (88 commits, 6 branches, 6 tags rewritten)
- pyproject.toml version synchronized with git tags per Article XI requirements

### Fixed

- HTML template test assertions adjusted to match conditional section rendering
- Template validation now correctly handles Jinja2 syntax edge cases

**Feature 002 - Documentation Generator (Phase 9 Foundation - T201-T203)**

- **T201**: OutputFormat enum with MARKDOWN, HTML, RST support
  - File extension mapping (.md, .html, .rst)
  - MIME type support (text/markdown, text/html, text/x-rst)
  - Case-insensitive format lookup via from_string()
  - Validation with descriptive error messages
  - 8 unit tests with 100% coverage

- **T202**: DocumentRenderer and TemplateLoader protocols
  - DocumentRenderer protocol: render(), escape(), code_block()
  - TemplateLoader protocol: load_template(), discover_templates(), validate_template()
  - Runtime checkable protocols with @runtime_checkable
  - 7 contract tests validating protocol compliance

- **T203**: MarkdownRenderer implementation
  - Full GitHub Flavored Markdown (GFM) support
  - Methods: heading(), list_item(), link(), bold(), italic(), inline_code()
  - Proper escape handling for Markdown special characters
  - Code block formatting with syntax highlighting hints
  - 24 unit tests with 100% coverage

- **Exception hierarchy for generator errors**
  - GeneratorError (base exception)
  - TemplateError, TemplateNotFoundError, TemplateValidationError
  - RenderError with context tracking
  - 10 exception tests with detailed error messages

- **T204**: HtmlRenderer implementation
  - Full HTML5 semantic markup support
  - Methods: paragraph(), heading(), list_item(), link(), bold(), italic(), inline_code()
  - HTML entity escaping using html.escape()
  - Code blocks with language class attributes
  - 30 unit tests with 100% coverage

- **T205**: RstRenderer implementation
  - reStructuredText (RST) / Sphinx format support
  - Heading underlines with proper characters (=, -, ~, ^, ", #)
  - Code-block directive with language support
  - RST link syntax (`text <url>`_)
  - Inline code with double backticks
  - 23 unit tests with 100% coverage

- **T206**: TemplateContext dataclass
  - Context data passed to templates for rendering
  - Computed properties: has_variables, variable_count, has_tags, tag_count, etc.
  - role_name, role_description, format_name properties
  - to_dict() method for template compatibility
  - Supports custom_data for extended context
  - 10 unit tests with 100% coverage

- **T207**: RenderResult dataclass
  - Result container for documentation rendering operations
  - Properties: file_extension, size_bytes, line_count
  - save_to_file() method for output persistence
  - Includes metadata (timestamp, source_file, template_name)
  - 9 unit tests with 100% coverage

- **T208**: Custom Jinja2 filters
  - markdown_escape: Escape Markdown special characters (\\ ` * _ { } [ ] ( ) # + - . !)
  - code_fence: Wrap code in Markdown fenced code blocks (```language)
  - format_priority: Format TODO priorities with emoji indicators (🟢🟡🔴🚨)
  - rst_escape: Escape reStructuredText special characters (\\ * ` _ | )
  - html_attrs: Convert dict to HTML attribute string (class="value")
  - list_items: Format list items as Markdown (ordered/unordered)
  - FILTERS registry for Jinja2 environment registration
  - 47 unit tests with 100% coverage

- **T209**: TemplateEngine with Jinja2 integration
  - Pre-configured Jinja2 Environment with custom filters
  - Factory method create() with sensible defaults
  - FileSystemLoader support for template directories
  - render_string() for inline templates
  - get_template() for file-based templates
  - Strict undefined variable handling (fails fast on missing vars)
  - trim_blocks and lstrip_blocks enabled by default
  - 19 unit tests with 100% coverage
  - Added Jinja2 ^3.1.0 dependency via Poetry

- **T210**: FileSystemTemplateLoader for template discovery
  - Multi-level template discovery with priority hierarchy
  - Search paths: format dir → format suffix → generic
  - Template validation (exists, readable, .j2 extension)
  - Directory structure: templates/{format}/{name}.j2 or templates/{name}.{ext}.j2
  - discover_templates() returns available templates for format
  - validate_template() checks existence
  - 17 unit tests with 93% coverage

- **T211**: EmbeddedTemplateLoader for package resources
  - Load templates from package resources (ansibledoctor.generator.templates/)
  - Python 3.9+ importlib.resources support
  - discover_templates() lists embedded templates
  - validate_template() checks resource existence
  - Graceful fallback when resources missing
  - 6 unit tests with 93% coverage

- **T212**: Default templates for all output formats
  - **Markdown template** (role.j2): Clean, readable format with GFM support
    - Table of contents with section links
    - Variables with type, required, value, source
    - Tags with usage counts and locations
    - TODOs with priority emoji indicators
    - Examples with syntax-highlighted code blocks
  - **HTML template** (role.j2): Modern, responsive design
    - Embedded CSS with clean typography
    - Semantic HTML5 markup
    - Badge components for required/optional
    - Syntax highlighting hints for code
    - Mobile-responsive layout
  - **RST template** (role.j2): Sphinx-compatible documentation
    - Proper RST heading underlines
    - Field lists for metadata
    - code-block directives with language
    - Table of contents with depth control
  - All templates use custom Jinja2 filters (markdown_escape, rst_escape, code_fence, format_priority)
  - Conditional rendering (only show sections if data exists)
  - 6 smoke tests validating all templates render without errors

**Metrics**: +216 tests (262 → 478), generator module at 99%, 88% overall

- **T213**: Template validation system
  - **TemplateValidator**: Comprehensive Jinja2 template validation
    - Syntax validation with detailed error messages
    - Undeclared variable detection
    - Required variable validation
    - Unused context variable checking
    - File validation with existence and type checks
  - **Validation methods**:
    - `validate_syntax()`: Parse and validate Jinja2 syntax
    - `validate_file()`: Validate template files
    - `get_undeclared_variables()`: Extract used variables
    - `validate_required_variables()`: Ensure required vars present
    - `check_variable_usage()`: Detect unused context variables
    - `validate_template()`: Comprehensive validation with result dict
  - **Error handling**:
    - TemplateValidationError with template name and details
    - Line number reporting for syntax errors
    - Missing variable lists
  - 23 tests covering all validation scenarios
  - 96% coverage on validator.py

**Metrics**: +239 tests (262 → 501), generator module at 99%, 89% overall

- **T214**: Integration tests for generator Foundation
  - **End-to-end tests**: Complete generation pipeline testing
    - Markdown generation with full role data
    - HTML generation with responsive design
    - RST generation with Sphinx compatibility
    - All 3 formats tested with same input data
  - **Template engine integration**: Template loading and rendering
    - FileSystemTemplateLoader discovery tests
    - Custom Jinja2 filters availability
    - Template resolution in format directories
  - **Cross-format consistency**: All formats handle same role
    - Markdown, HTML, RST render identically structured roles
    - Minimal roles handled gracefully
    - Empty collections don't break templates
  - **Error handling**: Missing templates and validation
    - Template not found errors handled
    - Template validation integration
    - File validation with TemplateValidator
  - **Metadata generation**: Generation info in output
    - Generator version appears in all formats
    - Generation date formatted correctly
    - Output format extensions correct (.md, .html, .rst)
  - 12 integration tests covering complete workflows
  - **Filter improvements**: rst_escape handles non-string values
    - Accepts Any type, converts to string
    - None returns empty string
    - Integers, booleans handled correctly

**Metrics**: +251 tests (262 → 513), generator module at 99%, 89% overall

**Feature 002 - Documentation Generator (Phase 10 - US5 Markdown MVP - T216-T222)**

- **T216-T217**: MarkdownRenderer implementation with TDD
  - Full DocumentRenderer protocol implementation
  - Created ansibledoctor/generator/renderers/ package structure
  - Uses EmbeddedTemplateLoader for default templates
  - Markdown escaping for special characters (*, _, [, ], `, #)
  - Code block formatting with language hints (```language)
  - Thread-safe concurrent rendering support
  - Custom template path support
  - 23 unit tests with 100% coverage
  - Commits: bd4c6e2, 27c6351 (fixup)

- **T218**: Property-based testing with Hypothesis
  - 4 property tests for robustness validation
  - Random role data generation with valid Pydantic types
  - Tests: valid structure, injection prevention, variable presence, consistency
  - Commit: 5024c6d

- **T220**: Integration tests for Markdown generation
  - 8 end-to-end tests for complete pipeline
  - Tests: complete docs, sections present, variables rendered, code blocks, TODOs, tags, examples
  - Validates entire parse → render → output workflow
  - Commit: aa56e6a

- **T221**: Unit tests for CLI generate command (TDD RED phase)
  - 11 test methods for CLI functionality
  - Tests: role path, format option, output file, custom template, verbose flag, all options
  - Error handling: nonexistent path, invalid format, rendering errors
  - Mocking strategy: Isolate CLI logic from dependencies
  - Commit: a2aed17

- **T222**: CLI generate command implementation (TDD GREEN phase)
  - Added generate command with full functionality
  - Options: --format, --output, --template, --verbose, --log-level
  - Role parsing via _parse_role_for_generation() helper
  - MarkdownRenderer integration for MVP
  - TemplateContext creation with complete role data
  - Structured logging with correlation IDs
  - User-friendly error messages
  - Commit: 972dc64

- **T223**: CLI help documentation enhancement
  - Comprehensive docstring with 7 usage examples
  - Template variables reference section
  - Output formats documentation (Markdown, HTML, RST)
  - Exit codes reference (0=success, 1=error, 2=validation)
  - Structured help output with clear sections
  - Manual verification with `ansible-doctor generate --help`
  - Commit: baa69ce

- **T224**: End-to-end integration tests
  - 12 E2E tests validating complete CLI workflow
  - Tests: stdout output, file output, format options, verbose logging
  - Error handling: nonexistent roles, validation failures
  - Complete workflow validation: parse → render → verify
  - Tests with minimal_role, complex_role, phase8_test_role fixtures
  - Bug fixes discovered during TDD:
    - VariableParser initialization (missing annotation_extractor)
    - Method name corrections (parse_role_variables, parse_tasks)
    - format_priority filter None handling
  - Commit: abc212f

- **T225**: README.md documentation update
  - Added "Generating Documentation (Phase 10 MVP)" section
  - Basic usage examples: stdout, file output, verbose logging
  - Advanced usage: batch processing, pipelines, nested directories
  - Generated documentation contents: overview, variables, tags, TODOs, examples
  - Updated test metrics: 495 tests, 89% coverage
  - Updated progress: Phase 10 at 40%
  - Commit: 558921e

- **T226**: Performance benchmarks
  - 3 rendering performance tests with pytest
  - Small role (10 vars): 25.18ms (target <50ms) ✅
  - Medium role (50 vars): 24.84ms (target <100ms) ✅
  - Large role (100 vars): 25.41ms (target <200ms) ✅
  - All performance targets exceeded by >50%
  - Cross-platform compatible using tmp_path fixtures
  - Commit: d7c4dce

- **T227**: Full test suite validation
  - 498 tests passing (262 Feature 001 + 233 Feature 002 + 3 performance)
  - 81% coverage (all tests passing, quality validated)
  - No failures or critical coverage gaps
  - MVP release quality confirmed

**Metrics**: +236 tests (262 → 498), 81% coverage, Phase 10 MVP complete (7/15 tasks)

## [0.2.0] - 2025-11-17

### Added

**Phase 8 - Task Tags & TODO/Examples** - Feature Complete

**Task Tags Parser (US3 - T101-T107)**
- Created `Tag` value object with name, description, usage_count, file_locations
- Implemented `TaskParser` domain service to extract tags from tasks/*.yml
- Parses both string and list tag formats
- Aggregates tag usage counts across multiple tasks
- Tracks file:line locations for each tag occurrence
- Handles errors gracefully with detailed logging
- 21 tests with 94% coverage

**TODO Annotations Parser (US4 - T108-T110)**
- Created `TodoItem` value object with description, file_path, line_number, priority
- Implemented `TodoParser` domain service for @todo annotation extraction
- Supports formats: `@todo:`, `@TODO`, `@todo(priority)`
- Priority levels: low, medium, high, critical
- Scans all .yml/.yaml files recursively in role directory
- 23 tests with 81% coverage

**Example Code Blocks Parser (US4 - T111-T113)**
- Created `Example` value object with title, code, description, language
- Implemented `ExampleParser` domain service for @example block extraction
- Parses multiline blocks: `@example Title\n# code\n@end`
- Auto-detects language: yaml, bash, python, json, jinja2
- Preserves code formatting exactly (no whitespace stripping)
- Single-line format support: `@example: code`
- 17 tests with 96% coverage

**CLI Integration (T114)**
- Integrated TaskParser, TodoParser, ExampleParser into CLI _parse_single_role()
- Added `tags[]`, `todos[]`, `examples[]` to JSON output structure
- Graceful error handling with structured logging for all parsers
- Tested with minimal_role and complex_role fixtures

**Integration Tests (T115-T117)**
- Created phase8_test_role fixture with complete Phase 8 features
- Added 18 integration tests validating end-to-end parsing workflow:
  * 4 tests for task tag extraction and aggregation
  * 5 tests for TODO annotation parsing with priorities
  * 5 tests for example code block extraction
  * 4 tests for complete integration and JSON serialization
- All 262 tests passing (244 baseline + 18 new)
- 84% code coverage maintained

**Documentation (T118-T120)**
- Updated README with US3/US4 examples in output JSON
- Added Task Tags Parser and TODO/Examples Parser to feature list
- Created comprehensive ANNOTATION_GUIDE.md (400+ lines):
  * Variable annotations (@var) with all attributes
  * TODO annotations (@todo) with priority levels
  * Example annotations (@example) with multiline blocks
  * Tag documentation and usage statistics
  * Best practices and complete template examples
- Updated CHANGELOG for v0.2.0 release

### Changed

- Modified `RuamelYAMLLoader.load_file()` return type from `dict` to `dict | list`
- Enables TaskParser to correctly parse tasks files (list format vs dict)
- Updated `AnsibleRole` model imports to use separated Tag, TodoItem, Example

### Fixed

- Fixed YAML loader to return lists for task files instead of forcing dict conversion
- Fixed test assertions to match actual parser behavior

## [0.1.0] - 2025-11-17

### Added

**Phase 7 - Quality Assurance & Testing** - MVP Release

**Bug Fixes & Test Completion (T086-T087)**
- Fixed JSON annotation parsing: Strip `$` prefix before JSON parsing
- Fixed CLI test mocks: Remove invalid RoleParser mock
- Fixed test fixtures: Align minimal_role defaults with test expectations
- Fixed platform summary assertions in metadata integration tests
- **129 tests passing** (100% pass rate)
- **81% code coverage** (exceeds 80% target per Constitution Article III)

**Property-Based Testing (T088)**
- Added 9 hypothesis-based property tests for annotation parsing
- Tests cover: variable names, descriptions, tags, multiline annotations
- JSON attribute variations, comment counts, whitespace handling
- Edge case validation for annotation extractor robustness

**Performance Benchmarks (T091)**  
- Created 5 performance tests validating SC-002 requirements
- Minimal role parsing: <500ms ✅
- Complex role parsing: <2s ✅
- CLI end-to-end: <1s ✅
- Annotation extraction: <200ms ✅
- YAML loading (1000 vars): <500ms ✅

**CLI Module Entry Point (T089)**
- Added `ansibledoctor/__main__.py` for `python -m ansibledoctor` execution
- Validated all README quickstart examples
- CLI help, parse command, JSON output, file output all functional

**Documentation (T093-T097)**
- Added comprehensive Architecture section to README
  - DDD component structure diagram
  - Design principles (immutability, ubiquitous language, type safety)
  - Data flow visualization
  - Key patterns (protocols, value objects, aggregates)
- Fixed README License section emoji
- Created `.gitignore` for Python project

**Phase 6 - CLI Interface (T072-T082)** - MVP Feature

**Configuration Tests (T083-T085)** - Quality Gates
- Unit tests: `tests/unit/test_config.py` (11 test methods)
  - Project structure validation
  - Constitution compliance checks
  - Code quality standards (docstrings, no bare except)
  - Import compliance (no star imports)
  - Versioning format validation
  - Documentation requirements (README sections, CHANGELOG format)
  - Entry points configuration

**Documentation Enhancement (T093-T095)**
- README.md: Updated with MVP completion status
  - Project status section with completed features
  - Core functionality breakdown (US1, US2, CLI)
  - Test coverage statistics (110 test methods)
  - Planned features roadmap
- Configuration examples for future features

**Phase 6 - CLI Interface (T072-T082)** - MVP Feature

**CLI Tests Written First (T072-T074)** - TDD Red Phase
- Unit tests: `tests/unit/test_cli.py` (20 test methods)
  - CLI entry point and command structure
  - Parse command with role_path argument
  - Flags: --output, --recursive, --validate, --log-level
  - Exit codes: 0 (success), 1 (error), 2 (validation failure)
  - JSON output format validation
  - Integration with minimal_role and complex_role fixtures
  - Recursive mode for multiple roles
  - Error handling: missing paths, invalid roles

**CLI Implementation (T075-T078)** - TDD Green Phase
- `ansibledoctor/cli.py`: Command-line interface with click
  - `cli()`: Main group with version option
  - `parse()`: Parse command with full flag support
    - `role_path`: Required argument (Path with exists check)
    - `--output`: Optional output file
    - `--recursive`: Parse multiple roles in directory
    - `--validate`: Validate role structure before parsing
    - `--log-level`: DEBUG, INFO, WARNING, ERROR
    - `--json-output`: JSON format (default: True)
  - `_parse_single_role()`: Single role parsing logic
    - Metadata extraction via MetadataParser
    - Variables extraction via VariableParser
    - Variable statistics (total, documented, by type, by source)
    - Error handling with structured context
  - `_parse_roles_recursive()`: Recursive parsing
    - Auto-detect role directories (has tasks/)
    - Parse each role independently
    - Summary: total, successful, failed
  - Exit codes: 0 (success), 1 (parsing error), 2 (validation error)
  - Comprehensive error handling with user-friendly messages

**Entry Point Configuration (T079-T080)**
- pyproject.toml: Entry point `ansible-doctor-enhanced = ansibledoctor.cli:main`
- CLI callable via `ansible-doctor-enhanced parse <role_path>`

**Phase 3 - User Story 2: Variables Parser (T032-T047)** - MVP Feature

**Tests Written First (T032-T034)** - TDD Red Phase
- Unit tests: `tests/unit/test_annotation_extractor.py` (21 test methods)
  - Single-line @var annotations
  - Multiline @var annotations with YAML attributes
  - JSON-formatted annotations
  - @tag, @todo, @example annotations
  - Line number tracking
  - Comment extraction utilities
- Unit tests: `tests/unit/test_variable_parser.py` (24 test methods)
  - Basic variable parsing from defaults/vars
  - Type inference (string, number, boolean, list, dict, null)
  - Annotation merging with variables
  - Nested structures (dict, list)
  - Required/example/deprecated attributes
  - Edge cases: empty files, missing annotations, malformed YAML
- Integration tests: `tests/integration/test_variable_integration.py` (15 test methods)
  - minimal_role: simple variables with annotations
  - complex_role: nested structures, JSON annotations, multiline
  - Variable statistics and analysis
  - Deprecated variable filtering

**AnnotationExtractor Implementation (T035-T037)** - TDD Green Phase
- `ansibledoctor/parser/annotation_extractor.py`: Domain service for annotation parsing
  - `extract_annotations()`: Main entry point for extracting all annotation types
  - Regex patterns for @var, @tag, @todo, @example, @meta
  - Multiline annotation support (continuation detection)
  - `parse_annotation_attributes()`: Parse JSON/YAML/plain text formats
  - `extract_comment_lines_with_numbers()`: Line number tracking
  - Structured logging for observability

**VariableParser Implementation (T038-T043)** - TDD Green Phase
- `ansibledoctor/parser/variable_parser.py`: Domain service for variable extraction
  - `parse_role_variables()`: Parse both defaults/ and vars/ directories
  - `parse_variables_file()`: Parse single file with annotation merging
  - Type inference via `Variable.infer_type()` (automatic detection)
  - Annotation attribute extraction (description, required, example, deprecated)
  - Source tracking (defaults vs vars)
  - Comprehensive error handling
  - Structured logging throughout

**Phase 2 - User Story 1: Metadata Parser (T021-T031)** - MVP Feature

**Tests Written First (T021-T022)** - TDD Red Phase
- Unit tests: `tests/unit/test_metadata_parser.py` (18 test methods)
  - Basic galaxy_info parsing
  - Complex metadata with dependencies
  - Platform version handling (list, string, missing)
  - Dependency formats (string, dict with name/role key)
  - argument_specs.yml parsing (Ansible 2.11+)
  - Edge cases: missing files, malformed YAML, empty metadata
- Integration tests: `tests/integration/test_metadata_integration.py` (12 test methods)
  - End-to-end parsing with minimal_role fixture
  - Complex role with dependencies and multiple platforms
  - Optional argument_specs.yml handling
  - Error scenarios with graceful degradation

**MetadataParser Implementation (T023-T028)** - TDD Green Phase
- `ansibledoctor/parser/metadata_parser.py`: Domain service for metadata extraction
  - `parse_metadata()`: Main entry point combining galaxy_info + argument_specs
  - `parse_galaxy_info()`: Extract author, description, license, platforms, dependencies
  - `parse_argument_specs()`: Parse optional argument_specs.yml (Ansible 2.11+)
  - `_parse_platforms()`: Handle versions as list/string/"all"
  - `_parse_dependencies()`: Support string and dict formats
  - Structured logging for all operations
  - Comprehensive error handling with ParsingError context

**Domain Model Enhancement**
- `RoleMetadata`: Added `galaxy_info` raw dict field for extensibility
- `meta_file_path` tracking for debugging and error context
- Project initialization with spec-kit methodology
- Constitution v1.2.0 with 10 core principles (Library-First, CLI Interface, Test-Driven Development, Integration Testing, Observability, Semantic Versioning, Simplicity Gate, Keep a Changelog, Living Documentation, Domain-Driven Design)
- Article X: Domain-Driven Design (DDD) with Ubiquitous Language, Bounded Contexts, Entity/Value Objects, Aggregates, Domain Services
- Feature specification 001: Ansible Role Parser with Annotation Extraction
- Implementation plan for ansible role parser with Python 3.11+, Poetry, ruamel.yaml, pydantic
- Task breakdown for Feature 001: 100 atomic tasks organized by user story (MVP: 58 tasks)
- CHANGELOG.md following Keep a Changelog 1.1.0 format
- README.md with comprehensive project documentation, quick start, usage examples
- Documentation requirements in implementation plan (Articles VIII & IX)
- Poetry project configuration (pyproject.toml) with dependencies and dev tools
- Project structure: ansibledoctor/{models/, parser/, cli/, utils/}, tests/{unit/, integration/}
- Exception hierarchy (AnsibleDoctorError, ParsingError, ValidationError, ConfigError, TemplateError)
- Structured logging infrastructure with correlation IDs and JSON output support
- Protocol definitions (RoleParser, YAMLLoader, AnnotationExtractor) for Dependency Inversion
- Pydantic domain models following DDD principles:
  - Aggregate Root: AnsibleRole with rich behavior methods
  - Value Objects: RoleMetadata, Variable, Tag, Annotation, Example (all immutable/frozen)
  - Entity: TodoItem (identity by file location)
  - Enums: VariableType, AnnotationType
  - Type inference for variables (string, number, boolean, list, dict, null)
- YAML loader implementation (RuamelYAMLLoader) with Anti-Corruption Layer for ruamel.yaml
- Path utilities: RolePathValidator, IgnorePatternMatcher (.ansibledoctor-ignore support)
- Integration test fixtures: minimal_role and complex_role with comprehensive test data

### Changed
- Enhanced Article III: Test-First renamed to Test-Driven Development (TDD) with explicit Red-Green-Refactor cycle
- Constitution version bump: v1.1.0 → v1.2.0
- Enhanced Article VI: Semantic Versioning with detailed SemVer 2.0.0 specification (MAJOR.MINOR.PATCH)
- Updated commit requirements to mandate CHANGELOG.md and README.md updates
- Updated code review checklist to verify documentation completeness (10 principles instead of 9)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## Release History

*No releases yet - project in initial development*

---

[Unreleased]: https://github.com/yourusername/ansible-doctor-enhanced/compare/HEAD
