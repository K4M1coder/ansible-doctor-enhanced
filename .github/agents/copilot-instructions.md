# ansible-doctor-enhanced Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-11-20

## SpecKit Workflow (Windows)

**SpecKit** is the specification-driven development workflow tool for this project.

### Prerequisites
```powershell
# Install dependencies
pipx install poetry
pipx install uvx
poetry install  # Install / update project dependencies
npm install -g speckit
```

### Key Commands order (run from copilot cli or switch to agents)
```powershell
specify 
/constitution	# Create project governing principles and development guidelines	Run first to establish project standards
/specify      #	Define what you want to build (requirements and user stories)	Focus on the what and why, not tech stack
/clarify	    # Clarify underspecified areas through structured questioning	Must run before /plan unless explicitly skipped
/plan	        # Create technical implementation plans with chosen tech stack	Specify architecture, frameworks, and technical decisions
/tasks	      # Generate actionable task lists for implementation	Breaks down plan into executable steps
/analyze	    # Cross-artifact consistency & coverage analysis	Run after /tasks, before /implement
/implement	  # Execute all tasks to build the feature according to plan	Generates working code from specifications

# Update agent context
.\.specify\scripts\powershell\update-agent-context.ps1
```

### Workflow Pattern
1. Run `/constitution` → generates `.specify/memory/constitution.md` (governing principles)
2. Run `/speckit.specify` → generates `specs/{feature-id}/spec.md` (user stories, success criteria)
3. Run `/speckit.clarify` → refines spec with Q&A (if needed)
4. Run `/speckit.plan` → generates `plan.md` (architecture, phases)
5. Run `/speckit.tasks` → generates `tasks.md` (250+ detailed tasks)
6. Run `/speckit.checklist` → generates quality validation checklist
7. Run `/speckit.analyze` → validates cross-artifacts consistency and constitution compliance
8. Run `/speckit.tasktoissues` → OPTIONAL (only if explicitely required) creates GitHub issues for each task in the repository
9. Run `/speckit.implement` → TDD implementation (RED-GREEN-REFACTOR)

## Active Technologies
- **PowerShell**: Primary scripting language for workflows and automation
- **Python 3.11+**: Primary language (app, type hints, frozen dataclasses)
- **Git**: Version control (Hybrid GitFlow workflow)
- **Node.js**: For SpecKit
- **Poetry**: Dependency management and packaging
- **UVX**: Fast Python package installer (alternative to pip)
- **pipx**: Install Python CLI tools in isolated environments
- **Ansible**: Target documentation platform (roles, collections, projects, playbooks, modules, plugins, inventories)
- **Pydantic v2**: Data validation and modeling
- **Jinja2**: Template engine for documentation generation
- **ruamel.yaml**: YAML parsing with comment preservation
- **pytest**: Testing framework (pytest-cov, pytest-mock, Hypothesis)
- **ruff**: Fast Python linter (replaces flake8, pylint)
- **mypy**: Static type checker (--strict mode)
- **JSON Schema**: Configuration schema validation
- **SpecKit**: Specification-driven development workflow tool
- **markdownlint**: Markdown style linter for docs
- **Mermaid**: Diagram generation in documentation
- **html5lib**: HTML parsing and validation in tests
- **structlog**: Structured logging with context support
- **Filesystem only** (config files, ansible files, generated docs)

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

tests/                  # Test suite (>80% coverage target)
  unit/                 # Unit tests (TDD RED-GREEN-REFACTOR)
    models/collection/  # Model tests (NEW in 004)
    parser/collection/  # Parser tests (NEW in 004)
  integration/          # Integration tests
  property/             # Property-based tests (Hypothesis)
  e2e/                  # End-to-end CLI tests
  fixtures/collections/ # Test collections (NEW in 004)

demo/                   # Demo project for users
  demo-role/            # Sample role
    docs/               # Generated docs
  demo-collection/      # Sample collection
    docs/               # Generated docs
  demo-project/         # Sample project
    docs/               # Generated docs

specs/                  # Feature specifications (build with speckit)
  001-role-parser/      # v0.1.0-v0.2.0
  002-doc-generator/    # v0.3.0
  003-role-parity/      # v0.4.0
  004-collection-support/  # v0.5.0
    plan.md             # Implementation phases
    spec.md             # User stories
    tasks.md            # detailed tasks
    checklists/         # Quality validation
  006-project-docs/     # v0.6.0
  007-hierarchical-context
  007-project-navigation
  008-template-customization

.specify/               # SpecKit configuration (build with speckit)
  memory/
    constitution.md     # Project principles (12 articles)
  scripts/powershell/   # Workflow automation

.github/                # GitHub configuration
  agents/               # GitHub Agents instructions
    copilot-instructions.md  # GitHub Copilot instructions
    speckit.*.agent.md  # SpecKit Agents instructions
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
```
Command	Description	Usage
/constitution	Create project governing principles and development guidelines	Run first to establish project standards (spec branch)
/specify	Define what you want to build (requirements and user stories)	Focus on the what and why, not tech stack (spec branch)
/clarify	Clarify underspecified areas through structured questioning	Must run before /plan unless explicitly skipped (spec branch)
/plan	Create technical implementation plans with chosen tech stack	Specify architecture, frameworks, and technical decisions (spec branch)
/tasks	Generate actionable task lists for implementation	Breaks down plan into executable steps (spec branch)
/analyze	Cross-artifact consistency & coverage analysis	Run after /tasks, before /implement (spec branch)
/implement	Execute all tasks to build the feature according to plan	Generates working code from specifications (code branches)
```

### Git Workflow (Hybrid GitFlow)

- **Hybrid GitFlow**:
  - `main`: Production releases (tags: v0.1.0, v0.1.100 v0.11.0 v1.0.0 etc.)
  - `dev`: Integration branch for features (tags: v0.1.0-dev, v0.1.0-rcX etc.)
  - `{feature-id}-{name}`: coding Feature branches (e.g., 004-collection-support)
  - `specs/{feature-id}-{name}`: Specification branches (merged after planning)
- **Atomic Commits**: One logical change per commit
  - Commit message format: `<type>(<scope>): <subject>` 
  - Types: feat, fix, docs, test, refactor, chore
  - Include "Relates-to: #US8" and "Part-of: Feature-004" in body

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
  - Breaking changes = MAJOR bump
  - New features = MINOR bump
  - Bug fixes = PATCH bump

### Python Style
- Python 3.11+ with type hints (mypy --strict)
- Pydantic v2 models for validation
- Frozen models for value objects (immutability)
- Structured logging (structlog) with context
- Error handling with actionable suggestions
- Docstrings: Google style with examples

### Testing
- Minimum 80% coverage (target: 90% for core)
- TDD: Tests written BEFORE implementation (RED-GREEN-REFACTOR)
- Unit tests: Isolated logic (no external dependencies)
- Integration tests: File I/O, YAML parsing, template rendering
- Property-based tests: Hypothesis for edge cases
- Test naming: `test_{what_is_tested}_{expected_behavior}`

## Recent Changes
- read the changelog

---

