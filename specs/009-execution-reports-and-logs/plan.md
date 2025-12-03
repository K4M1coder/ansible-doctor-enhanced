# Implementation Plan: Execution Reports & Structured Logging

**Branch**: `009-execution-reports-and-logs` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-execution-reports-and-logs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the existing structlog-based logging infrastructure to provide comprehensive execution reports with performance metrics, correlation ID tracing, and aggregated error summaries. This feature enables CI/CD integration through structured JSON reports, standardized exit codes, and machine-readable output while maintaining backward compatibility with existing logging behavior.

## Technical Context

**Language/Version**: Python 3.11+ (existing project baseline)  
**Primary Dependencies**: structlog (existing), pydantic (existing), click (existing CLI framework)  
**Storage**: File system for report output (JSON/text files), contextvars for correlation ID propagation  
**Testing**: pytest with fixtures for temporary files, time mocking for metrics validation  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: Single project - CLI application with library architecture  
**Performance Goals**: <100ms report generation overhead, <5% timing accuracy for metrics  
**Constraints**: Must extend existing logging (no new framework), backward compatible (no reports unless flag specified), thread-safe correlation ID handling  
**Scale/Scope**: Handle projects with 100+ roles, 1000+ files, nested operations (project→collection→role)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Library-First Architecture
- **Compliance**: ExecutionReport will be a standalone model with clear serialization interface
- **Interface**: Pydantic models for reports, protocol for report generation, factory for creating from execution context
- **Testability**: Independent unit tests for report generation, serialization, and metrics collection

### ✅ CLI Interface Mandate  
- **Compliance**: New flags `--report`, `--report-format`, `--correlation-id`, `--fail-on-warnings`, `--continue-on-error`
- **Output**: JSON (machine-readable) and text (human-readable) formats supported
- **Exit Codes**: Standard convention: 0=success, 1=error, 2=warnings (with flag), 3=invalid usage
- **Documentation**: All flags documented in `--help` output

### ✅ Test-Driven Development (TDD)
- **TDD Cycle**: Write tests for report model → implement serialization → refactor
- **Coverage Target**: 90% for report generation (core logic), 80% for CLI integration
- **Test Types**: Unit tests for models/metrics, integration tests for CLI commands with report generation

### ✅ Integration & Contract Testing
- **Integration Tests**: Report file writing, JSON validation, concurrent execution handling
- **Contract Tests**: ExecutionReport schema validation, backward compatibility with existing logging

### ✅ Observability & Structured Logging
- **Enhancement**: This feature EXTENDS existing structlog infrastructure
- **Metrics**: Timing collection for parsing/rendering/writing phases
- **Correlation IDs**: Already implemented via contextvars, will be extended to reports

### ✅ Semantic Versioning
- **Version**: v0.9.0 (MINOR - new feature, backward compatible)
- **Compatibility**: No breaking changes, reports only generated when flag specified

### No Violations - All Gates Pass ✅

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
ansibledoctor/
├── models/
│   ├── execution_report.py      # NEW: ExecutionReport, ExecutionMetrics models
│   ├── execution_warning.py     # NEW: ExecutionWarning model
│   └── execution_error.py       # NEW: ExecutionError model with suggestions
├── reporting/                    # NEW: Reporting subsystem
│   ├── __init__.py
│   ├── report_generator.py      # Report generation from execution context
│   ├── metrics_collector.py     # Timing and count collection
│   ├── serializers.py           # JSON/text formatting
│   └── protocols.py             # ReportGenerator protocol
├── cli/
│   └── __init__.py              # MODIFY: Add report flags, exit code handling
├── utils/
│   ├── logging.py               # MODIFY: Enhance with metrics collection hooks
│   └── correlation.py           # NEW: Correlation ID utilities
└── exceptions.py                # MODIFY: Add exit code property to exceptions

tests/
├── unit/
│   ├── models/
│   │   ├── test_execution_report.py
│   │   ├── test_execution_metrics.py
│   │   ├── test_execution_warning.py
│   │   └── test_execution_error.py
│   └── reporting/
│       ├── test_report_generator.py
│       ├── test_metrics_collector.py
│       └── test_serializers.py
└── integration/
    ├── test_report_generation_cli.py
    ├── test_metrics_collection_e2e.py
    ├── test_correlation_propagation.py
    └── test_exit_codes.py
```

**Structure Decision**: Single project structure with new `reporting/` module for report generation logic. Models extend existing `models/` directory. CLI modifications add report flags to existing commands. Tests follow existing pattern (unit/integration split).

## Phase 0: Research & Planning

### Research Tasks

1. **Timing Mechanisms**: Evaluate Python timing approaches for accurate phase metrics
   - `time.perf_counter()` vs `time.time()` for wall-clock vs monotonic timing
   - Context managers for automatic phase timing
   - Thread-safe accumulation for nested operations

2. **Report Serialization**: Determine best practices for JSON report format
   - Pydantic JSON schema generation for self-documenting reports
   - Date/time formatting (ISO 8601 with timezone)
   - File path representation (absolute vs relative)

3. **Exit Code Standards**: Research CLI exit code conventions
   - POSIX standards (0=success, non-zero=error)
   - Common practices for warnings vs errors (exit code 2 for warnings)
   - Sysexits.h conventions for specific error types

4. **Atomic File Writes**: Research safe file writing patterns
   - Temp file + rename pattern for atomicity
   - File locking considerations for concurrent access
   - Handling of existing file backups

5. **Correlation ID Best Practices**: Investigate correlation ID formats and propagation
   - UUID4 vs ULID vs custom formats (tradeoff: randomness vs sortability)
   - Contextvars for thread-local storage in async/concurrent operations
   - HTTP header patterns (X-Correlation-ID, X-Request-ID)

**Output**: `research.md` with findings, decisions, and rationale for each topic

## Phase 1: Design & Contracts

### Data Model Design

**ExecutionReport** (Primary Aggregate):
```python
class ExecutionReport(BaseModel):
    correlation_id: str
    command: str  # "generate", "parse", "watch"
    status: Literal["completed", "completed_with_warnings", "failed", "interrupted"]
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    metrics: ExecutionMetrics
    warnings: list[ExecutionWarning]
    errors: list[ExecutionError]
    output_files: list[Path]
```

**ExecutionMetrics**:
```python
class ExecutionMetrics(BaseModel):
    files_processed: int
    roles_documented: int = 0
    collections_documented: int = 0
    projects_documented: int = 0
    warnings_count: int
    errors_count: int
    phase_timing: dict[str, int]  # {"parsing_ms": 1200, "rendering_ms": 800}
```

**ExecutionWarning**:
```python
class ExecutionWarning(BaseModel):
    file: Path
    line: int | None
    message: str
    warning_type: str  # "missing_annotation", "deprecated_syntax", etc.
```

**ExecutionError**:
```python
class ExecutionError(BaseModel):
    file: Path
    line: int | None
    error_type: str
    message: str
    suggestion: str | None
    stack_trace: str | None
```

### API Contracts

**ReportGenerator Protocol**:
```python
class ReportGenerator(Protocol):
    def generate(self, context: ExecutionContext) -> ExecutionReport: ...
    def write_report(self, report: ExecutionReport, path: Path, format: str) -> None: ...
```

**MetricsCollector Protocol**:
```python
class MetricsCollector(Protocol):
    def start_phase(self, phase_name: str) -> None: ...
    def end_phase(self, phase_name: str) -> None: ...
    def increment_counter(self, counter_name: str, value: int = 1) -> None: ...
    def get_metrics(self) -> ExecutionMetrics: ...
```

### CLI Integration

**New Flags**:
- `--report PATH`: Generate execution report at specified path
- `--report-format {json,text,summary}`: Report output format (default: json)
- `--correlation-id ID`: Use provided correlation ID instead of auto-generated
- `--fail-on-warnings`: Exit with code 2 if warnings occur
- `--continue-on-error`: Process all files despite individual failures
- `--verbose` (existing, enhanced): Show phase timing and progress

**Exit Code Convention**:
- `0`: Success
- `1`: Fatal error (parsing failure, invalid config, exception)
- `2`: Warnings present (only with `--fail-on-warnings`)
- `3`: Invalid usage (bad arguments, missing required flags)

**Output**: `data-model.md`, `contracts/` directory with API specs, `quickstart.md` with usage examples

## Complexity Tracking

> **No violations - all gates pass**
