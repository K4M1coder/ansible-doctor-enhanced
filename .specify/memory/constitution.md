<!--
Sync Impact Report:
- Version change: Initial → 1.0.0
- Initial constitution ratification
- Principles defined: 7 core principles
- Templates: ✅ All templates ready for use
- Follow-up: None
-->

# Ansible Doctor Enhanced Constitution

## Core Principles

### I. Library-First Architecture
Every feature MUST be implemented as a standalone, reusable library with clear boundaries:
- Libraries are self-contained with minimal external dependencies
- Each library has a single, well-defined responsibility (Single Responsibility Principle)
- Libraries MUST be independently testable without complex mocking
- Clear interfaces defined using Python protocols/abstract base classes (Dependency Inversion Principle)
- No "organizational-only" libraries - each must provide concrete value

**Rationale**: Enables code reuse, simplifies testing, and maintains clear architectural boundaries aligned with SOLID principles.

### II. CLI Interface Mandate
Every library MUST expose its functionality through a command-line interface:
- Text-based input/output protocol: stdin/args → stdout, errors → stderr
- Support both JSON (machine-readable) and human-readable formats
- Exit codes follow standard conventions (0=success, 1=error, 2=usage error)
- All CLI options documented with `--help`
- Configuration via CLI args, environment variables, and config files (priority order)

**Rationale**: Ensures debuggability, scriptability, and integration with CI/CD pipelines.

### III. Test-First Development (NON-NEGOTIABLE)
Test-Driven Development is MANDATORY for all code:
- Tests MUST be written BEFORE implementation
- Red-Green-Refactor cycle strictly enforced: Write failing test → Implement → Refactor
- Minimum code coverage: 80% for all new code, 90% for core logic
- Tests MUST be readable and serve as living documentation
- No code review approval without accompanying tests

**Rationale**: Prevents regression, documents intended behavior, and ensures code quality from the start.

### IV. Integration & Contract Testing
Integration tests are REQUIRED for:
- New library contract definitions (API boundaries)
- Changes to existing contracts or interfaces
- Inter-module communication patterns
- File I/O operations (YAML parsing, template rendering)
- External dependencies (Git operations, file system)

**Philosophy**: Prefer real integration tests over mocks where practical (Integration-First Testing). Mocks are acceptable for external services beyond our control (network APIs, slow operations).

**Rationale**: Catches real-world failures that unit tests miss, validates assumptions about external dependencies.

### V. Observability & Structured Logging
All code MUST be observable and debuggable:
- Structured logging using Python's `logging` module with JSON formatters
- Log levels used consistently: DEBUG (detailed), INFO (lifecycle), WARNING (recoverable), ERROR (failures), CRITICAL (system-level issues)
- Contextual information in all log entries (role name, file path, operation type)
- Performance metrics collected for key operations (parsing duration, template rendering time)
- Correlation IDs for tracing operations across modules
- Error messages MUST include actionable recovery suggestions

**Rationale**: Enables troubleshooting in production, performance optimization, and understanding system behavior.

### VI. Versioning & Backward Compatibility
Semantic versioning (MAJOR.MINOR.PATCH) is MANDATORY:
- **MAJOR**: Breaking changes to CLI interface, configuration schema, or library contracts
- **MINOR**: New features, new CLI options (backward compatible)
- **PATCH**: Bug fixes, documentation updates, refactoring
- Deprecation warnings MUST precede breaking changes by at least one MINOR version
- Maintain compatibility with ansible-doctor configuration files for 2+ major versions
- Migration guides REQUIRED for all MAJOR version bumps

**Rationale**: Users depend on stable interfaces; predictable versioning builds trust and eases upgrades.

### VII. Simplicity Gate (KISS Principle)
Start simple, add complexity only when proven necessary:
- Maximum 3 top-level projects/modules for initial implementation
- No speculative features or "we might need this later" code (YAGNI - You Aren't Gonna Need It)
- Prefer composition over inheritance (favor Has-A over Is-A relationships)
- Avoid premature optimization - measure before optimizing
- Each module should fit in working memory (~300-500 lines ideal, 1000 lines maximum)
- Complex logic MUST include inline documentation explaining "why"

**Rationale**: Simple code is maintainable code. Complexity is a liability that must be justified by concrete requirements.

## Technical Standards

### Python & Tooling Requirements
- **Python Version**: 3.11+ (for improved error messages, performance, typing features)
- **Package Manager**: Poetry for dependency management and packaging
- **Code Quality**: 
  - Type hints REQUIRED for all public APIs (validated with mypy --strict)
  - Code formatting: Black (line length 100)
  - Import sorting: isort (compatible with Black)
  - Linting: ruff (replaces flake8, pylint, with faster performance)
- **Testing Framework**: pytest with pytest-cov for coverage reporting
- **Documentation**: 
  - Docstrings required for all public functions/classes (Google style)
  - Sphinx-compatible for auto-generated API docs
  - Examples in docstrings verified by doctest where practical

### Dependency Management
- Minimize external dependencies - each dependency MUST be justified
- Pin major versions in pyproject.toml, exact versions in poetry.lock
- Security: Automated dependency vulnerability scanning (GitHub Dependabot)
- Compatibility: Support latest 3 Ansible major versions
- Preserve compatibility with existing ansible-doctor configuration patterns

### Error Handling Standards
All errors MUST follow a structured hierarchy:
- Base exception: `AnsibleDoctorError` (extends `Exception`)
- Specific exceptions: `ParsingError`, `TemplateError`, `ConfigError`, `ValidationError`
- All exceptions MUST include:
  - Clear error message describing what went wrong
  - Contextual information (file path, role name, line number)
  - Suggested recovery action (e.g., "Check YAML syntax in defaults/main.yml")
- No bare `except:` clauses - catch specific exceptions
- Errors logged before raising for debugging traceability

### Performance Requirements
- Role parsing: < 500ms per role on typical hardware
- Template rendering: < 100ms per template
- Memory usage: < 100MB for typical workloads (processing ~10 roles)
- Large role support: Must handle roles with 100+ variables, 50+ tasks
- Progress indicators for operations > 2 seconds

## Development Workflow

### Atomic Commits & Change Management
Every commit MUST:
- Follow Conventional Commits format: `type(scope): description`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`
  - Scope: module name or feature area
  - Examples: `feat(parser): add support for meta/argument_specs.yml`, `fix(logging): correct correlation ID propagation`
- Be independently buildable and testable (no broken intermediate states)
- Include tests for new functionality or bug fixes
- Update relevant documentation (README, CHANGELOG)
- Pass all CI checks (tests, linting, type checking)

### Branch Strategy
- **main**: Production-ready code, tagged releases only
- **develop**: Integration branch for features
- **feature/###-description**: Feature branches following spec-kit numbering
- Merge strategy: Squash feature branches to develop, merge develop to main with merge commit
- No direct commits to main except hotfixes

### Code Review Requirements
All changes require review approval with verification of:
- Constitutional compliance (follows all 7 core principles)
- Test coverage meets 80% minimum threshold
- No security vulnerabilities introduced
- Documentation updated (inline docs, README, changelog)
- Breaking changes flagged and justified in PR description
- Performance implications assessed for hot paths

### Quality Gates (CI/CD Pipeline)
Before merge, ALL must pass:
1. **Unit Tests**: pytest suite, 80%+ coverage
2. **Integration Tests**: Key workflows end-to-end
3. **Type Checking**: mypy --strict (no errors)
4. **Linting**: ruff check (no violations)
5. **Formatting**: Black + isort validation
6. **Security**: Safety check for vulnerable dependencies
7. **Documentation**: Docs build without warnings

## Governance

This constitution supersedes all other development practices and serves as the authoritative source for project standards.

### Amendment Process
Constitution amendments require:
1. Proposal documented in GitHub issue with rationale
2. Discussion period (minimum 7 days for MAJOR, 3 days for MINOR)
3. Approval from project maintainers (2+ approvals)
4. Version bump following semantic versioning
5. Migration plan for breaking changes (MAJOR version)
6. Update to all dependent templates and documentation

### Compliance Verification
- All pull requests MUST verify constitutional compliance in PR checklist
- Complexity violations (e.g., exceeding simplicity gate) MUST be explicitly justified with:
  - Concrete requirement driving the complexity
  - Alternative approaches considered and rejected
  - Plan to reduce complexity in future refactoring
- Constitutional violations without justification result in PR rejection

### Living Document
This constitution evolves with the project. Regular reviews (quarterly) ensure principles remain aligned with project goals and community needs.

**Version**: 1.0.0 | **Ratified**: 2025-11-16 | **Last Amended**: 2025-11-16
