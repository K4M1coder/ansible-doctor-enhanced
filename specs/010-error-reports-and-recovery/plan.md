# Implementation Plan: Error Reports & Recovery

**Branch**: `010-error-reports-and-recovery` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-error-reports-and-recovery/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Standardize error reporting and recovery in ansible-doctor-enhanced by extending the existing `AnsibleDoctorError` hierarchy. Provide aggregated error reports with unique error codes, intelligent recovery suggestions, graceful degradation for partial success, and IDE-friendly output formats (text, JSON, SARIF). Enable users to systematically fix issues without re-running commands and integrate errors into development workflows.

## Technical Context

**Language/Version**: Python 3.11+ (existing project baseline)  
**Primary Dependencies**: pydantic (existing), structlog (existing), click (CLI framework)  
**Storage**: Error code database (JSON/YAML file), in-memory error aggregation during processing  
**Testing**: pytest with error scenario fixtures, SARIF schema validation  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) with IDE integration  
**Project Type**: Single project - CLI application extending existing exception hierarchy  
**Performance Goals**: <50ms error report generation overhead, O(1) error lookup by code  
**Constraints**: Cap at 1000 errors per run (memory bounded), backward compatible error messages, stable error codes across versions  
**Scale/Scope**: Handle 100+ roles with multiple errors per file, aggregate duplicate errors, support IDE integration (VS Code, PyCharm, IntelliJ)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Test-First Development**: PASS  
  - Rationale: Error scenarios are inherently testable. We can write test fixtures for invalid YAML, missing files, parser errors, etc., then implement ErrorAggregator and recovery suggestion logic to make tests pass. SARIF schema validation ensures output correctness.

- **Library-First Architecture**: PASS  
  - Rationale: New `exceptions/` module with error codes, `ErrorReport` model, and `ErrorAggregator` protocol are pure Python. CLI integration only wraps library calls (`--error-format`, `--continue-on-error`). Library functions raise structured exceptions with recovery data.

- **CLI Mandate**: PASS  
  - Rationale: New CLI flags `--error-format {text,json,sarif}`, `--continue-on-error`, `--max-errors N`, `--error-output FILE`. Extends existing CLI in `ansibledoctor/cli/__init__.py` with error handling configuration options.

- **Observability**: PASS  
  - Rationale: Error aggregation emits structured logs via existing structlog integration. Each error logged with code, location, recovery suggestion. Execution reports (Spec 009) include error counts and top errors. SARIF format enables IDE telemetry integration.

- **Backward Compatibility**: PASS  
  - Rationale: No breaking changes. Existing exceptions inherit error codes (E000 for unknown). Default behavior unchanged (fail fast). New flags opt-in to error aggregation and alternative formats. Error messages preserve existing text with added metadata.

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
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
ansibledoctor/
├── exceptions/
│   ├── __init__.py         # Existing exception hierarchy (AnsibleDoctorError)
│   ├── codes.py            # NEW: Error code definitions and mappings
│   ├── aggregator.py       # NEW: ErrorAggregator implementation
│   └── recovery.py         # NEW: Recovery suggestion database
├── models/
│   └── error_report.py     # NEW: ErrorReport pydantic model
├── cli/
│   └── __init__.py         # EXTEND: Add error handling CLI flags
└── utils/
    └── sarif.py            # NEW: SARIF 2.1.0 output formatter

tests/
├── unit/
│   ├── test_error_codes.py          # NEW: Error code mapping tests
│   ├── test_aggregator.py           # NEW: Error aggregation tests
│   └── test_recovery_suggestions.py # NEW: Recovery logic tests
├── integration/
│   └── test_error_reporting.py      # NEW: End-to-end error scenarios
└── fixtures/
    └── error_scenarios/             # NEW: Invalid YAML, missing files, etc.
```

**Structure Decision**: Single project structure (Option 1) extending existing `ansibledoctor/` package. New `exceptions/` module components colocated with existing error hierarchy for tight coupling. SARIF formatter in `utils/` aligns with existing utility modules. Tests mirror source structure with unit tests for each component and integration tests for CLI error handling flows.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all gates pass. No additional complexity justification required.

---

## Phase 0: Research & Planning

### Research Tasks

1. **SARIF 2.1.0 Format Specification**: Study SARIF schema for IDE integration
   - Official SARIF 2.1.0 JSON schema structure
   - Required vs optional fields (runs, results, locations, codeFlows)
   - Best practices for result.level (error, warning, note)
   - IDE support matrix (VS Code, PyCharm, IntelliJ SARIF extensions)

2. **Error Code Numbering Conventions**: Research error code patterns in CLI tools
   - Ansible error codes (<https://docs.ansible.com/ansible/latest/reference_appendices/error_codes.html>)
   - Python PEP 8 (E/W codes for linters like flake8, pylint)
   - ESLint, rustc, tsc error code patterns
   - Hierarchical numbering schemes (E1xx=parsing, E2xx=validation, E3xx=generation)

3. **Recovery Suggestion Patterns**: Investigate intelligent error recovery
   - Static analysis tools with auto-fix suggestions (eslint --fix, rustfmt)
   - Context-sensitive suggestions based on error type
   - Multi-step recovery workflows ("try X, if fails try Y")
   - Levenshtein distance for "did you mean?" suggestions

4. **Error Aggregation Strategies**: Study memory-bounded error collection
   - Deduplication strategies (hash-based, structural similarity)
   - Priority-based truncation (keep critical errors, drop duplicates)
   - Error grouping by file/type/severity
   - Performance impact of error tracking vs fast-fail

5. **IDE Integration Standards**: Research IDE error panel conventions
   - VS Code Problems API expectations
   - Language Server Protocol (LSP) diagnostic format
   - Quick fix actions and code actions
   - Error severity mapping (error, warning, info, hint)

**Output**: `research.md` with findings, decisions, and rationale for each topic

---

## Phase 1: Design & Contracts

### Data Model Design

**ErrorReport** (Primary Aggregate):

```python
class ErrorReport(BaseModel):
    """Aggregated error report for a single execution run."""
    correlation_id: str  # Links to ExecutionReport from Spec 009
    timestamp: datetime
    errors: list[ErrorEntry]
    warnings: list[ErrorEntry]
    error_count: int
    warning_count: int
    max_errors_reached: bool
    partial_success: bool  # True if some files processed successfully
    
    def to_text(self) -> str: ...
    def to_json(self) -> str: ...
    def to_sarif(self) -> dict: ...
```

**ErrorEntry**:

```python
class ErrorEntry(BaseModel):
    """Single error or warning with full context."""
    code: str  # E001, W001, etc.
    severity: Literal["error", "warning"]
    category: str  # "parsing", "validation", "generation", "io"
    message: str
    file: Path | None
    line: int | None
    column: int | None
    context_lines: list[str]  # Surrounding source lines
    recovery_suggestions: list[str]
    related_errors: list[str]  # Other error codes to check
```

**ErrorCode** (Enumeration):

```python
class ErrorCode(str, Enum):
    # Parsing errors (E1xx)
    E101 = "YAML syntax error"
    E102 = "Invalid metadata structure"
    E103 = "Unsupported Ansible version"
    
    # Validation errors (E2xx)
    E201 = "Missing required annotation"
    E202 = "Invalid annotation syntax"
    E203 = "Duplicate annotation key"
    
    # Generation errors (E3xx)
    E301 = "Template rendering failed"
    E302 = "Output file write error"
    E303 = "Invalid output format"
    
    # I/O errors (E4xx)
    E401 = "File not found"
    E402 = "Permission denied"
    E403 = "Invalid path"
    
    # Warnings (W1xx-W4xx)
    W101 = "Deprecated annotation syntax"
    W201 = "Missing recommended annotation"
    W301 = "Output file already exists"
```

**RecoverySuggestion** (Database Entry):

```python
class RecoverySuggestion(BaseModel):
    """Maps error codes to recovery actions."""
    error_code: str
    primary_suggestion: str
    alternative_suggestions: list[str]
    documentation_link: str | None
    auto_fixable: bool
```

### API Contracts

**ErrorAggregator Protocol**:

```python
class ErrorAggregator(Protocol):
    """Collects errors during execution with bounded memory."""
    
    def add_error(
        self,
        code: str,
        message: str,
        file: Path | None = None,
        line: int | None = None,
        column: int | None = None,
        context: list[str] | None = None,
    ) -> None:
        """Add error to aggregator. May drop if max_errors reached."""
        ...
    
    def add_warning(
        self,
        code: str,
        message: str,
        file: Path | None = None,
        line: int | None = None,
    ) -> None:
        """Add warning to aggregator."""
        ...
    
    def has_errors(self) -> bool:
        """Check if any errors collected."""
        ...
    
    def generate_report(self) -> ErrorReport:
        """Generate final error report."""
        ...
    
    def get_recovery_suggestions(self, error_code: str) -> list[str]:
        """Retrieve recovery suggestions for error code."""
        ...
```

**SARIFFormatter**:

```python
class SARIFFormatter:
    """Converts ErrorReport to SARIF 2.1.0 format."""
    
    def format(self, report: ErrorReport) -> dict:
        """Generate SARIF JSON structure."""
        ...
    
    def _create_result(self, entry: ErrorEntry) -> dict:
        """Convert ErrorEntry to SARIF result."""
        ...
    
    def _create_location(self, entry: ErrorEntry) -> dict:
        """Create SARIF location with physical location."""
        ...
```

### CLI Extensions

**New Flags in `ansibledoctor/cli/__init__.py`**:

```python
@click.option(
    "--error-format",
    type=click.Choice(["text", "json", "sarif"]),
    default="text",
    help="Error report output format (default: text)",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    help="Continue processing after errors (generate partial output)",
)
@click.option(
    "--max-errors",
    type=int,
    default=1000,
    help="Maximum errors to collect before stopping (default: 1000)",
)
@click.option(
    "--error-output",
    type=click.Path(),
    help="Write error report to file instead of stderr",
)
```

### Output Contracts

**SARIF 2.1.0 Structure**:

```json
{
  "version": "2.1.0",
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "ansible-doctor",
          "version": "0.9.0",
          "informationUri": "https://github.com/thegeeklab/ansible-doctor"
        }
      },
      "results": [
        {
          "ruleId": "E101",
          "level": "error",
          "message": {
            "text": "YAML syntax error: expected <block end>, but found '<scalar>'"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "roles/webserver/tasks/main.yml"
                },
                "region": {
                  "startLine": 15,
                  "startColumn": 5
                }
              }
            }
          ],
          "fixes": [
            {
              "description": {
                "text": "Check YAML indentation and quote special characters"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

### Integration Points

1. **Exception Hierarchy Extension**:
   - Modify `ansibledoctor/exceptions/__init__.py` to include `error_code` attribute
   - Backward compatible: default code is `"E000"` for unknown errors

2. **Parser Integration**:
   - YAML parser catches `yaml.YAMLError` → maps to E101
   - Annotation parser validates structure → maps to E201-E203
   - File operations catch `OSError` → maps to E401-E403

3. **Execution Report Integration** (Spec 009):
   - `ExecutionReport.errors` field populated from `ErrorAggregator`
   - Error count included in metrics
   - Correlation ID shared between execution report and error report

4. **CLI Exit Codes**:
   - `0`: Success (no errors or warnings)
   - `1`: Errors encountered (even with `--continue-on-error`)
   - `2`: Warnings only (no errors)

### Quickstart Example

**Basic Error Reporting**:

```bash
# Default: fail fast with text errors to stderr
ansible-doctor generate .

# Collect all errors and generate JSON report
ansible-doctor generate . --continue-on-error --error-format json --error-output errors.json

# IDE integration with SARIF
ansible-doctor generate . --error-format sarif --error-output results.sarif
```

**Output**: `quickstart.md`, `data-model.md`, `contracts/error-aggregator.yaml`, `contracts/sarif-output.json`
