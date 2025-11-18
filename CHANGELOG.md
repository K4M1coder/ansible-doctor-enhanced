# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
