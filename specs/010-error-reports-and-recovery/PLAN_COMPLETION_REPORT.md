# Spec 010 Implementation Plan - Completion Report

**Date**: 2025-12-03  
**Branch**: `010-error-reports-and-recovery`  
**Status**: ✅ COMPLETE (Phase 0 & Phase 1)

---

## Overview

Successfully created comprehensive implementation plan for **Error Reports & Recovery** feature (Spec 010). This plan provides complete technical foundation for standardizing error reporting across ansible-doctor-enhanced with IDE integration, recovery suggestions, and memory-bounded error aggregation.

---

## Deliverables

### 📋 Core Planning Documents

1. **plan.md** (391 lines)
   - Summary: Feature description and objectives
   - Technical Context: Python 3.11+, pydantic, structlog, SARIF 2.1.0
   - Constitution Check: All gates PASS (TDD, Library-First, CLI Mandate, Observability, Backward Compatibility)
   - Project Structure: Single project with exceptions/, models/, utils/ extensions
   - Phase 0: Research on SARIF, error codes, recovery patterns, aggregation, IDE integration
   - Phase 1: Data models (ErrorReport, ErrorEntry, ErrorCode), protocols (ErrorAggregator), CLI extensions, SARIF output format

2. **research.md** (5 topics, comprehensive findings)
   - SARIF 2.1.0 Format: Industry standard, IDE support, rich metadata
   - Error Code Numbering: Hierarchical E1xx-E4xx, W1xx-W4xx (parsable, stable, extensible)
   - Recovery Suggestions: Static database + dynamic context analysis
   - Error Aggregation: Hash-based deduplication, 1000 error cap, O(1) lookup
   - IDE Integration: SARIF file → Problems panel (VS Code, PyCharm, IntelliJ)

3. **data-model.md** (7 models, state diagrams, ER diagrams)
   - **ErrorReport**: Aggregated report with correlation_id, errors, warnings, counts
   - **ErrorEntry**: Single error with code, location, context, recovery suggestions
   - **ErrorCode**: Enum with E1xx (parsing), E2xx (validation), E3xx (generation), E4xx (I/O)
   - **RecoverySuggestion**: Database mapping codes to recovery actions
   - **ErrorAggregator**: Protocol for bounded memory collection
   - Output Formats: Text (terminal), JSON (CI/CD), SARIF (IDE)
   - State Transitions: Collecting → Capped → Reporting

4. **quickstart.md** (comprehensive usage guide)
   - Basic Usage: Default fail-fast, continue-on-error, partial success
   - Output Formats: text, JSON, SARIF with IDE integration steps
   - Error Recovery Workflow: 5-step process (collect → review → fix → verify → repeat)
   - Advanced Usage: Error caps, correlation IDs, filtering by code
   - Error Code Reference: Complete table of E1xx-E4xx, W1xx-W4xx codes
   - Best Practices: Batch error collection, IDE integration, CI/CD integration, trend tracking
   - Troubleshooting: Common issues and solutions

### 📜 API Contracts

1. **contracts/error-aggregator.yaml** (OpenAPI 3.1.0 specification)
   - **Schemas**: ErrorEntry, ErrorReport, RecoverySuggestion
   - **Protocol Methods**: add_error, add_warning, has_errors, generate_report, get_recovery_suggestions, clear
   - **Examples**: Basic usage workflow with code snippets

2. **contracts/sarif-output.json** (SARIF 2.1.0 sample)
   - **Tool Driver**: ansible-doctor metadata, 3 rule definitions (E101, E201, W201)
   - **Invocations**: Execution metadata (command line, timing, exit code)
   - **Artifacts**: File index for IDE navigation
   - **Results**: 3 example errors/warnings with:
     - Physical locations (file, line, column, snippets)
     - Context regions (surrounding lines)
     - Fixes with artifact changes (auto-fix suggestions)
     - Related locations (parent context)
     - Recovery suggestions in properties

---

## Technical Highlights

### ✅ Constitution Compliance

| Gate | Status | Key Design Decisions |
| ------ | -------- | --------------------- |
| **Test-First Development** | ✅ PASS | Error scenarios are testable fixtures (invalid YAML, missing files) |
| **Library-First Architecture** | ✅ PASS | Pure Python exceptions/, models/, utils/ modules; CLI wraps library |
| **CLI Mandate** | ✅ PASS | New flags: `--error-format`, `--continue-on-error`, `--max-errors`, `--error-output` |
| **Observability** | ✅ PASS | Structured logging with error codes, correlation IDs, execution reports |
| **Backward Compatibility** | ✅ PASS | No breaking changes; default E000 code; opt-in flags |

### 🎯 Key Architectural Decisions

1. **Error Code System**
   - Hierarchical numbering: E1xx (parsing), E2xx (validation), E3xx (generation), E4xx (I/O)
   - Stable codes (never reuse retired codes)
   - Scannable prefixes (E vs W immediately identifies severity)

2. **Recovery Suggestions**
   - Static database for common errors (YAML syntax, missing annotations)
   - Dynamic context analysis (Levenshtein distance for "did you mean?")
   - Multi-step suggestions (try X, if fails try Y)
   - Documentation links for deeper guidance

3. **Memory-Bounded Aggregation**
   - Cap at 1000 unique errors (prevents OOM on large codebases)
   - Hash-based deduplication (O(1) lookup, 2KB per error)
   - First occurrence priority (root cause often most informative)
   - LRU eviction when cap reached

4. **IDE Integration**
   - SARIF 2.1.0 standard format
   - Support for VS Code, PyCharm, IntelliJ
   - Physical locations with snippets
   - Auto-fix suggestions (future-ready)

### 🔗 Integration Points

1. **Spec 009 (Execution Reports)**
   - Shared `correlation_id` for linking error reports to execution reports
   - Error counts included in execution metrics
   - Combined telemetry for complete observability

2. **Existing Exception Hierarchy**
   - Extends `AnsibleDoctorError` with `error_code` attribute
   - Backward compatible: default code E000 for unknown errors
   - All exceptions map to error codes

3. **CLI Integration**
   - New flags in `ansibledoctor/cli/__init__.py`
   - Exit codes: 0 (success), 1 (errors), 2 (warnings only)
   - Optional error output file (default: stderr)

4. **Parser Integration**
   - YAML parser: `yaml.YAMLError` → E101
   - Annotation parser: validation failures → E201-E205
   - File operations: `OSError` → E401-E405

---

## File Structure

```text
specs/010-error-reports-and-recovery/
├── spec.md                         # Original specification
├── plan.md                         # ⭐ Implementation plan (this execution)
├── research.md                     # ⭐ Phase 0 research findings
├── data-model.md                   # ⭐ Phase 1 data models
├── quickstart.md                   # ⭐ User guide and examples
├── contracts/
│   ├── error-aggregator.yaml       # ⭐ OpenAPI protocol specification
│   └── sarif-output.json           # ⭐ SARIF 2.1.0 sample output
└── checklists/                     # Quality checklists (existing)
```

**Total Deliverables**: 6 new files (1 plan, 3 documentation, 2 contracts)

---

## Error Code Catalog

### Parsing Errors (E1xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E101 | YAML syntax error | Indentation, missing colons, special characters |
| E102 | Invalid metadata structure | Malformed galaxy_info, meta/main.yml issues |
| E103 | Unsupported Ansible version | Version constraints not met |
| E104 | Invalid task syntax | Missing `name`, invalid module parameters |
| E105 | Circular role dependency | Role depends on itself (direct or indirect) |

### Validation Errors (E2xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E201 | Missing required annotation | No `@meta description` or `@var` for defaults |
| E202 | Invalid annotation syntax | Typo in annotation keyword, wrong format |
| E203 | Duplicate annotation key | Same annotation key repeated |
| E204 | Invalid annotation value | Value doesn't match expected type/format |
| E205 | Conflicting annotations | Mutually exclusive annotations present |

### Generation Errors (E3xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E301 | Template rendering failed | Jinja2 syntax error, undefined variable |
| E302 | Output file write error | Permission denied, disk full |
| E303 | Invalid output format | Unsupported format requested |
| E304 | Unsupported template variable | Template uses unavailable data |
| E305 | Template syntax error | Jinja2 parsing error |

### I/O Errors (E4xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E401 | File not found | Missing required file (meta/main.yml, defaults/main.yml) |
| E402 | Permission denied | Insufficient permissions to read/write file |
| E403 | Invalid path | Path contains invalid characters or too long |
| E404 | Directory not found | Expected directory missing (tasks/, defaults/) |
| E405 | Disk full | Insufficient disk space for output |

### Warnings (W1xx-W4xx)

| Code | Description | Action |
| ------ | ------------- | -------- |
| W101 | Deprecated YAML syntax | Update to current Ansible syntax |
| W102 | Unused variable | Remove or document variable |
| W103 | Empty metadata block | Add metadata or remove block |
| W201 | Missing recommended annotation | Add `@var` descriptions for better docs |
| W202 | Deprecated annotation syntax | Update to current annotation format |
| W203 | Annotation could be more specific | Enhance annotation detail |
| W301 | Output file already exists | Use `--force` to overwrite |
| W302 | Large output file (>10MB) | Review template complexity |
| W303 | Template using deprecated filter | Update to current filter |
| W401 | File ignored (no matching pattern) | Check file naming conventions |
| W402 | Symlink detected | Consider resolving symlink |

---

## Next Steps

### Phase 2: Task Breakdown (separate `/speckit.tasks` command)

The plan provides complete foundation for implementation. Next step is to break down Phase 0 and Phase 1 into concrete tasks:

1. **Phase 0 Tasks** (Research validation):
   - Create test project with error scenarios
   - Prototype SARIF output generation
   - Benchmark error aggregation performance
   - Test IDE integration (VS Code, PyCharm)

2. **Phase 1 Tasks** (Implementation):
   - Define `ErrorCode` enum with all 20+ codes
   - Implement `ErrorEntry` and `ErrorReport` pydantic models
   - Build `ErrorAggregator` with hash-based deduplication
   - Create recovery suggestion database (JSON/YAML)
   - Implement `SARIFFormatter` with schema validation
   - Add CLI flags and error handling logic
   - Write unit tests (error codes, aggregator, suggestions)
   - Write integration tests (end-to-end error scenarios)

### Implementation Workflow

```bash
# 1. Review and refine plan
cd specs/010-error-reports-and-recovery
git checkout -b 010-error-reports-and-recovery

# 2. Run research validation
# (Verify SARIF format, test IDE integration, benchmark performance)

# 3. Break down into tasks
# /speckit.tasks command (creates tasks.md)

# 4. Implement TDD cycle for each task
# RED → GREEN → REFACTOR

# 5. Integration testing
pytest tests/integration/test_error_reporting.py

# 6. Documentation updates
# Update main README with error reporting features

# 7. Merge to dev
git push origin 010-error-reports-and-recovery
# Create PR → merge to dev
```

---

## Dependencies

### Prerequisites

- ✅ Spec 003: Core documentation generation (existing)
- ✅ Spec 009: Execution reports and logging (planned)

### Enables

- 🔮 Spec 011: Watch mode and incremental updates (error reporting during watch)
- 🔮 Spec 012: Schema documentation (validation error reporting)
- 🔮 Spec 013: Links & cross-references (broken link error reporting)

---

## Quality Metrics

| Metric | Target | Notes |
| -------- | -------- | ------- |
| **Constitution Gates** | 5/5 PASS | All gates satisfied |
| **Error Codes Defined** | 20+ codes | E1xx-E4xx, W1xx-W4xx |
| **Recovery Suggestions** | 15+ entries | Static database coverage |
| **Output Formats** | 3 formats | text, JSON, SARIF |
| **IDE Support** | 3 IDEs | VS Code, PyCharm, IntelliJ |
| **Performance Overhead** | <50ms | Report generation time |
| **Memory Cap** | 1000 errors | Bounded memory usage |
| **Test Coverage Target** | 90%+ | Core error handling logic |

---

## Conclusion

Implementation plan for Spec 010 is **COMPLETE** and ready for task breakdown and implementation. The plan provides:

- ✅ Comprehensive research on SARIF, error codes, recovery patterns
- ✅ Complete data models with validation rules
- ✅ Protocol definitions for error aggregation
- ✅ CLI integration design with backward compatibility
- ✅ User documentation with examples and best practices
- ✅ API contracts (OpenAPI + SARIF sample)
- ✅ Constitution compliance verification
- ✅ Integration points with Spec 009 (execution reports)

**All Phase 0 and Phase 1 artifacts generated.** Ready to proceed with `/speckit.tasks` for Phase 2 task breakdown.

**Branch**: `010-error-reports-and-recovery`  
**Artifacts**: 6 files in `specs/010-error-reports-and-recovery/`  
**Status**: ✅ PLAN COMPLETE
