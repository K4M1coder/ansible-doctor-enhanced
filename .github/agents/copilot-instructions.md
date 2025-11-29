# ansible-doctor-enhanced Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-20

## SpecKit Workflow (Windows)

**SpecKit** is the specification-driven development workflow tool for this project.

### Prerequisites
```powershell
# Install dependencies
pipx install poetry
pipx install uvx
```

### Key Commands (run from workspace root)
```powershell
# Plan a feature from spec
/speckit.plan

# Analyze project consistency
/speckit.analyze

# Create task breakdown
/speckit.break

# Create quality checklist
/speckit.checklist

# Implement tasks (TDD)
/speckit.implement

# Update agent context
.\.specify\scripts\powershell\update-agent-context.ps1
```

### Workflow Pattern
1. Write `specs/{feature-id}/spec.md` (user stories, success criteria)
2. Run `/speckit.plan` → generates `plan.md` (architecture, phases)
3. Run `/speckit.break` → generates `tasks.md` (250+ detailed tasks)
4. Run `/speckit.checklist` → generates quality validation checklist
5. Run `/speckit.analyze` → validate Constitution compliance
6. Run `/speckit.implement` → TDD implementation (RED-GREEN-REFACTOR)

## Active Technologies
- **Python 3.11+**: Primary language (type hints, frozen dataclasses)
- **Poetry**: Dependency management and packaging
- **UVX**: Fast Python package installer (alternative to pip)
- **pipx**: Install Python CLI tools in isolated environments
- **Ansible**: Target documentation platform (roles, collections, projects)
- **Pydantic v2**: Data validation and modeling
- **Jinja2**: Template engine for documentation generation
- **ruamel.yaml**: YAML parsing with comment preservation
- **pytest**: Testing framework (pytest-cov, pytest-mock, Hypothesis)
- **ruff**: Fast Python linter (replaces flake8, pylint)
- **mypy**: Static type checker (--strict mode)
- Filesystem only (config files, role files, generated docs) (003-role-parity)

## Project Structure

```text
ansibledoctor/          # Source code (library-first architecture)
  models/               # Domain models (DDD)
    galaxy.py           # GalaxyMetadata (schema 1.0.0)
    collection.py       # AnsibleCollection aggregate
    plugin.py           # PluginType enum
  parser/               # Parsers (infrastructure layer)
    galaxy_parser.py    # Parse galaxy.yml
    collection_walker.py # Discover collection structure
  generator/            # Documentation generators
  cli/                  # CLI interface
    collection.py       # Collection commands (NEW in 004)
  utils/                # Utilities
    fs_walker.py        # File system operations
    paths.py            # Path resolution

tests/                  # Test suite (>80% coverage release target, 30% minimum acceptable coverage)
  unit/                 # Unit tests (TDD RED-GREEN-REFACTOR)
    models/collection/  # Model tests (NEW in 004)
    parser/collection/  # Parser tests (NEW in 004)
  integration/          # Integration tests
  property/             # Property-based tests (Hypothesis)
  performance/          # Performance benchmarks
  e2e/                  # End-to-end CLI tests
  fixtures/collections/ # Test collections (NEW in 004)

specs/                  # Feature specifications (SDD)
  001-role-parser/      # v0.1.0-v0.2.0 (COMPLETE)
  002-doc-generator/    # v0.3.0 (spec COMPLETE, impl PENDING)
  003-role-parity/      # v0.4.0 (PLANNED)
  004-collection-support/  # v0.5.0 (IN PROGRESS)
    spec.md             # User stories US8-US10
    plan.md             # Implementation phases
    tasks.md            # 250 detailed tasks
    checklists/         # Quality validation
  006-project-docs/     # v0.6.0 (PLANNED)

.specify/               # SpecKit configuration
  memory/
    constitution.md     # Project principles (12 articles)
  scripts/powershell/   # Workflow automation
```

## Commands

### Development
```powershell
# Install dependencies
poetry install

# Run tests (TDD)
poetry run pytest tests/unit/models/collection/ -v
poetry run pytest -k "galaxy or collection" --tb=short

# Coverage report
poetry run pytest --cov=ansibledoctor --cov-report=html

# Linting & Type checking
poetry run ruff check ansibledoctor/
poetry run mypy ansibledoctor/ --strict

# Format code
poetry run black ansibledoctor/
poetry run isort ansibledoctor/
```

### SpecKit Workflows
```powershell
# Create plan from spec
/speckit.plan

# Break plan into tasks
/speckit.break

# Implement with TDD
/speckit.implement

# Analyze consistency
/speckit.analyze
```

### Git Workflow (Hybrid GitFlow)
```powershell
# Feature branches from dev
git checkout dev
git checkout -b 004-collection-support

# Atomic commits (one logical change per commit)
git add ansibledoctor/models/galaxy.py tests/unit/models/collection/test_galaxy_metadata.py
git commit -m "feat(models): add GalaxyMetadata model (schema 1.0.0)

- Pydantic model with required fields only (namespace, name, version, authors, dependencies)
- Frozen value object (DDD pattern)
- Namespace/version validators
- FQCN property
- Tests: 9/9 passing (TDD GREEN phase)

Relates-to: #US8
Part-of: Feature-004-collection-support"

# Update CHANGELOG.md before commits
# Version bump in pyproject.toml before release tags
```

## Code Style

### Methodologies (Constitution-Enforced)
- **SDD (Specification-Driven Development)**: Start with specs/{feature}/spec.md
- **DDD (Domain-Driven Design)**: Ubiquitous Language, Bounded Contexts, Aggregates
  - Value Objects: GalaxyMetadata (immutable, frozen=True)
  - Aggregates: AnsibleCollection (root), Role, Metadata
  - Anti-Corruption Layer: YAMLLoader protocol shields from ruamel.yaml
- **TDD (Test-Driven Development)**: RED-GREEN-REFACTOR cycle (NON-NEGOTIABLE)
  - Write failing tests FIRST
  - Implement minimal code to pass
  - Refactor while keeping tests green
- **KISS (Keep It Simple, Stupid)**: Max 3 top-level modules, no speculative features
- **SOLID Principles**:
  - Single Responsibility: Each class has one reason to change
  - Dependency Inversion: Depend on protocols, not concrete implementations
- **SMART Goals**: Specific, Measurable, Achievable, Relevant, Time-bound
- **Keep a Changelog**: CHANGELOG.md follows 1.1.0 format (Added/Changed/Fixed/etc.)
- **Semantic Versioning**: MAJOR.MINOR.PATCH (2.0.0 format)
  - v0.5.0 = Feature 004 (Collection Documentation)
  - Breaking changes = MAJOR bump
  - New features = MINOR bump
  - Bug fixes = PATCH bump

### Git Strategy
- **Hybrid GitFlow**: 
  - `main`: Production releases (tags: 0.1.0, 0.2.0, etc.)
  - `dev`: Integration branch for features
  - `{feature-id}-{name}`: Feature branches (e.g., 004-collection-support)
  - `specs/{feature-id}`: Specification branches (merged after planning)
- **Atomic Commits**: One logical change per commit
  - Commit message format: `<type>(<scope>): <subject>` 
  - Types: feat, fix, docs, test, refactor, chore
  - Include "Relates-to: #US8" and "Part-of: Feature-004" in body

### Python Style
- Python 3.11+ with type hints (mypy --strict)
- Pydantic v2 models for validation
- Frozen models for value objects (immutability)
- Structured logging (structlog) with context
- Error handling with actionable suggestions
- Docstrings: Google style with examples

### Testing
- Minimum 80% coverage (target: 90% for core)
- TDD: Tests written BEFORE implementation
- Unit tests: Isolated logic (no external dependencies)
- Integration tests: File I/O, YAML parsing, template rendering
- Property-based tests: Hypothesis for edge cases
- Test naming: `test_{what_is_tested}_{expected_behavior}`

## Recent Changes
- 003-role-parity: Added Python 3.11+

### Feature 004: Collection Documentation (v0.5.0) - IN PROGRESS (2025-11-20)

**Objective**: Document Ansible collections (namespace.name bundles of roles/plugins/modules)

**User Stories**:
- US8 (P1 MVP): Parse Collection Metadata - Extract galaxy.yml (schema 1.0.0, required fields only)
- US9 (P1): Generate Collection Documentation - README with overview, role index, plugin list

**Clarifications Applied** (Session 2025-11-20):
1. galaxy.yml: Only required fields (namespace, name, version, authors, dependencies); optional deferred to v0.6.0
2. Schema version: 1.0.0 (Ansible 2.9+ standard)
3. Plugin discovery: No file exclusions (validation filtering at parser layer)
4. Role index format: Template-configurable (not hardcoded)

**Implementation Progress** (24/250 tasks, 40% of US8):

✅ **Phase 1: Setup (T001-T004)** - COMPLETE

✅ **Phase 2: Foundation (T005-T008)** - COMPLETE (BLOCKING prerequisites)

✅ **Phase 3: US8 Tests - RED Phase (T009-T030)** - COMPLETE

✅ **Phase 4: US8 Implementation - GREEN Phase (T034-T065 partial)** - COMPLETE

**Test Results**: 24/24 passing (100%)

**Files Created** (19 files):

**Next Steps** (Remaining 61 tasks for US8):

**Deferred to v0.6.0**:

---

**Previous Features**:

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
