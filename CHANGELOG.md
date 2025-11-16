# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
