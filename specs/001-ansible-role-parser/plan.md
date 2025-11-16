# Implementation Plan: Ansible Role Parser with Annotation Extraction

**Branch**: `001-ansible-role-parser` | **Date**: 2025-11-16 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-ansible-role-parser/spec.md`

## Summary

Build a Python library that parses Ansible role directories, extracting metadata from `meta/main.yml`, variables from `defaults/main.yml` and `vars/main.yml`, task tags, and inline documentation annotations (@var, @tag, @todo, @example). Output structured JSON for downstream documentation generation. Must handle errors gracefully, support CLI interface, and complete typical role parsing in <500ms.

**Technical Approach**: Use `ruamel.yaml` for format-preserving YAML parsing, implement annotation regex patterns for comment extraction, provide Protocol-based interfaces for testability, structure as standalone library with CLI wrapper, leverage Python 3.11+ features (match statements, type hints), and follow Library-First + Test-First constitutional principles.

## Technical Context

**Language/Version**: Python 3.11+ (for improved error messages, match statements, typing improvements)  
**Primary Dependencies**: 
- `ruamel.yaml` (YAML parsing with comment preservation)
- `pydantic` v2 (data validation and serialization)
- `click` (CLI framework with automatic help generation)
- `structlog` (structured logging)
- `pathspec` (gitignore-style path matching)

**Storage**: File system read-only access (no database)  
**Testing**: pytest with pytest-cov (coverage), pytest-mock (mocking), hypothesis (property-based testing for annotation parsing)  
**Target Platform**: Cross-platform (Linux, macOS, Windows), Python 3.11+  
**Project Type**: Single project (library with CLI)  
**Performance Goals**: 
- Parse typical role (30 vars, 50 tasks) in <500ms
- Parse large role (100 vars, 200 tasks) in <2s
- Memory usage <50MB for typical roles
**Constraints**: 
- Must handle malformed YAML gracefully (log + continue)
- Must work with existing ansible-doctor annotation syntax
- CLI must be compatible with shell pipelines (stdin/stdout)
**Scale/Scope**: 
- Support 50+ simultaneous role processing (--recursive mode)
- Handle roles up to 1000 LOC per YAML file
- Support Ansible 2.9+ through 2.17+ (argument_specs.yml)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Article I: Library-First Architecture ✅
- Parser implemented as standalone `ansibledoctor.parser` library
- Clear interface via `RoleParser` protocol
- Independently testable without CLI

### Article II: CLI Interface Mandate ✅
- CLI wrapper in `ansibledoctor.cli.parse`
- JSON output to stdout, logs to stderr
- Exit codes: 0 (success), 1 (error), 2 (usage)

### Article III: Test-First Development ✅
- Tests written before implementation
- Coverage target: 80% minimum, 90% for core parser logic
- TDD cycle enforced via CI

### Article IV: Integration & Contract Testing ✅
- Contract tests for `RoleParser` protocol
- Integration tests with real Ansible role fixtures
- Property-based tests for annotation parsing edge cases

### Article V: Observability & Structured Logging ✅
- structlog with JSON formatting
- Context: file_path, line_number, role_name, operation
- Correlation IDs for multi-role parsing

### Article VI: Versioning & Backward Compatibility ✅
- Semantic versioning from 0.1.0 (pre-1.0 allows breaking changes)
- Existing ansible-doctor annotation syntax fully supported

### Article VII: Simplicity Gate ✅
- Single project: `ansibledoctor/` (no separate projects)
- No speculative features (MVP only: P1 user stories)
- Module count: 6 core modules (roles, metadata, variables, annotations, tags, cli)

### Article VIII: Change Documentation (Keep a Changelog) ✅
- CHANGELOG.md created following keepachangelog.com format
- All tasks MUST update [Unreleased] section with appropriate category
- Release process includes moving Unreleased to versioned section

### Article IX: Living Documentation (README Maintenance) ✅
- README.md created with all required sections
- Quick Start example includes parser usage
- Installation instructions for Poetry and PyPI
- Usage examples for common scenarios

**Status**: All gates PASS - no violations

## Project Structure

### Documentation (this feature)

```text
specs/001-ansible-role-parser/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology decisions and patterns (Phase 0)
├── data-model.md        # Entity definitions and relationships (Phase 1)
├── quickstart.md        # Developer validation scenarios (Phase 1)
└── contracts/           # Protocol definitions (Phase 1)
    ├── role_parser.py   # RoleParser protocol
    ├── yaml_loader.py   # YAMLLoader protocol
    └── annotation_extractor.py  # AnnotationExtractor protocol
```

### Source Code (repository root)

```text
ansibledoctor/
├── __init__.py          # Package init, version
├── exceptions.py        # Error hierarchy
├── models/              # Pydantic models
│   ├── __init__.py
│   ├── role.py          # AnsibleRole model
│   ├── metadata.py      # RoleMetadata, ArgumentSpec
│   ├── variable.py      # Variable model
│   ├── annotation.py    # Annotation, TodoItem, Example
│   └── tag.py           # Tag model
├── parser/              # Core parsing logic
│   ├── __init__.py
│   ├── role_parser.py   # Main RoleParser implementation
│   ├── yaml_loader.py   # YAML file loading
│   ├── metadata_parser.py  # meta/main.yml parsing
│   ├── variable_parser.py  # defaults/vars parsing
│   ├── annotation_parser.py  # Comment annotation extraction
│   ├── task_parser.py   # tasks/*.yml parsing for tags
│   └── protocols.py     # Protocol definitions (interfaces)
├── cli/                 # Command-line interface
│   ├── __init__.py
│   ├── parse.py         # Parse command
│   └── utils.py         # CLI utilities
└── utils/               # Shared utilities
    ├── __init__.py
    ├── logging.py       # Structured logging setup
    └── paths.py         # Path utilities

tests/
├── unit/                # Fast isolated tests
│   ├── test_models.py
│   ├── test_metadata_parser.py
│   ├── test_variable_parser.py
│   ├── test_annotation_parser.py
│   └── test_task_parser.py
├── integration/         # End-to-end with fixtures
│   ├── fixtures/        # Real Ansible role examples
│   │   ├── minimal_role/
│   │   ├── complex_role/
│   │   └── invalid_role/
│   └── test_role_parser.py
├── contract/            # Protocol contract tests
│   └── test_protocols.py
└── conftest.py          # Pytest configuration

pyproject.toml           # Poetry configuration
README.md                # User documentation
CHANGELOG.md             # Version history
```

**Structure Decision**: Single project structure chosen per Simplicity Gate. Parser is core library, CLI is thin wrapper. Tests organized by type (unit/integration/contract) for clear separation.

## Complexity Tracking

No constitutional violations - all gates pass.

---

## Phase 0: Research & Decisions (OUTPUT: research.md)

### Research Tasks

1. **YAML Parsing Library Comparison**
   - Evaluate: ruamel.yaml vs PyYAML vs strictyaml
   - Requirements: Comment preservation, format handling, error reporting
   - Decision: Document chosen library with rationale

2. **Annotation Parsing Strategy**
   - Evaluate: Regex vs custom parser vs AST-based
   - Requirements: Handle 3 formats (single-line, multiline, JSON)
   - Decision: Document parsing approach with edge case handling

3. **Error Handling Patterns**
   - Evaluate: Fail-fast vs continue-on-error vs partial results
   - Requirements: Constitutional observability, user experience
   - Decision: Document error strategy with recovery mechanisms

4. **Performance Optimization Approach**
   - Evaluate: Lazy loading vs streaming vs caching
   - Requirements: <500ms typical role, <50MB memory
   - Decision: Document optimization strategy

5. **CLI Framework Selection**
   - Evaluate: Click vs Typer vs argparse
   - Requirements: Type hints, auto-help, exit codes
   - Decision: Document framework choice

**Deliverable**: `research.md` with decisions, rationales, alternatives considered

---

## Phase 1: Design & Contracts (OUTPUT: data-model.md, contracts/, quickstart.md)

### Data Model Design (`data-model.md`)

Define Pydantic models for all entities from spec:

1. **AnsibleRole**: Root entity
   - Fields: path, name, metadata, variables, tasks, tags, todos, examples
   - Validation: path exists, name non-empty
   - Serialization: JSON with custom encoder

2. **RoleMetadata**: Galaxy info from meta/main.yml
   - Fields: author, description, license, company, min_ansible_version, platforms, dependencies
   - Validation: platforms list, dependencies format

3. **ArgumentSpec**: Ansible 2.11+ argument specifications
   - Fields: entry_point, options (dict)
   - Validation: options schema

4. **Variable**: Role variable
   - Fields: name, value, type, source, annotations
   - Validation: name required, type inferred
   - Relationships: List[Annotation]

5. **Annotation**: Inline documentation
   - Fields: type, key, content, file_path, line_number, parsed_attributes
   - Validation: type enum, file_path exists

6. **Tag**: Task tag
   - Fields: name, description, usage_count
   - Validation: name non-empty

7. **TodoItem** & **Example**: Supplementary annotations
   - Fields per spec
   - Validation rules

**Deliverable**: Complete Pydantic model definitions with validation

### API Contracts (`contracts/`)

Define Protocol (PEP 544) interfaces:

1. **`contracts/role_parser.py`** - RoleParser Protocol
```python
class RoleParser(Protocol):
    def parse_role(self, role_path: Path) -> AnsibleRole: ...
    def parse_roles(self, paths: List[Path]) -> List[AnsibleRole]: ...
```

2. **`contracts/yaml_loader.py`** - YAMLLoader Protocol
```python
class YAMLLoader(Protocol):
    def load(self, file_path: Path) -> Dict[str, Any]: ...
    def load_all(self, file_paths: List[Path]) -> List[Dict[str, Any]]: ...
```

3. **`contracts/annotation_extractor.py`** - AnnotationExtractor Protocol
```python
class AnnotationExtractor(Protocol):
    def extract_annotations(self, content: str, file_path: Path) -> List[Annotation]: ...
```

**Deliverable**: Protocol definitions with type hints

### Validation Scenarios (`quickstart.md`)

Quick tests for each user story:

1. **US1 Test**: Parse minimal role with meta/main.yml
2. **US2 Test**: Parse role with annotated variables
3. **US3 Test**: Parse role with task tags
4. **US4 Test**: Parse role with TODOs and examples

**Deliverable**: Executable validation scenarios (can run as doctests)

---

## Phase 2: Task Breakdown

**Command**: `/speckit.tasks` (generates `tasks.md`)

This phase is handled by the spec-kit tasks command, which will:
- Break down implementation into atomic tasks
- Organize by user story (P1, P2, P3)
- Add dependency markers and parallelization hints
- Create testing tasks (write tests first per TDD)

**Not generated by this plan** - see `/speckit.tasks` command.

---

## Assumptions

- Python 3.11+ available in target environments
- Role directories follow standard Ansible structure
- UTF-8 file encoding
- Local file system access (no SSH/remote)
- Annotation syntax matches existing ansible-doctor patterns
- Users familiar with command-line tools

## Documentation Requirements (Constitution Articles VIII & IX)

Every task implementing this feature MUST:

### CHANGELOG.md Updates
- Add entry to `[Unreleased]` section under appropriate category:
  - **Added**: New parser modules, new annotation types
  - **Changed**: Modifications to parsing behavior
  - **Fixed**: Bug fixes in parsing logic
  - **Security**: Security-related parser fixes
- Format: `- Brief description of change ([#issue](link) if applicable)`
- Example: `- Add support for meta/argument_specs.yml parsing for Ansible 2.11+`

### README.md Updates
Update when:
- Adding new CLI commands or options → Update **Usage** section
- Changing installation dependencies → Update **Installation** section
- Adding new features → Update **Key Features** section
- Changing Quick Start example → Validate example still works

### Commit Message Format
```
type(scope): description

- Update CHANGELOG.md [Unreleased] section
- Update README.md if user-facing changes
```

Example:
```
feat(parser): add meta/argument_specs.yml support

- Update CHANGELOG.md: Added Ansible 2.11+ argument specs parsing
- Update README.md: Add example showing argument specs in output
```

## Non-Functional Requirements Mapping

| NFR | Implementation Approach |
|-----|-------------------------|
| **Performance** | Lazy YAML loading, compiled regex patterns, minimal object allocation |
| **Reliability** | Try/except per file, continue-on-error, partial result handling |
| **Maintainability** | Protocol-based design, comprehensive docstrings, type hints |
| **Observability** | structlog with context, correlation IDs, performance metrics |
| **Compatibility** | Support Ansible 2.9+, existing annotation syntax |
| **Documentation** | CHANGELOG.md updated per task, README.md kept current |

## Success Criteria Verification

- **SC-001**: Test suite includes 50+ real Galaxy roles
- **SC-002**: Pytest benchmarks validate <500ms performance
- **SC-003**: Error handling tests cover all edge cases
- **SC-004**: Property-based tests verify annotation extraction accuracy
- **SC-005**: Integration tests validate JSON output schema
- **SC-006**: Memory profiling validates <50MB constraint
- **SC-007**: Unit tests explicitly test circular dependency detection
- **SC-008**: Error message tests validate clarity
- **SC-009**: Fuzzing tests validate malformed annotation handling
- **SC-010**: JSON schema documented and validated
