# Feature Specification: Ansible Role Parser with Annotation Extraction

**Feature Branch**: `001-ansible-role-parser`  
**Created**: 2025-11-16  
**Status**: Draft  
**Input**: User description: "Parse Ansible roles with annotation extraction, metadata collection, and structured data output for documentation generation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Role Metadata from Galaxy (Priority: P1) 🎯 MVP

As an Ansible role developer, I need to automatically extract role metadata from `meta/main.yml` so that documentation accurately reflects the role's purpose, author, license, supported platforms, and dependencies without manual duplication.

**Why this priority**: This is foundational - every Ansible role has a meta file, and this metadata is essential for any documentation. Without this, documentation cannot identify what the role is or who maintains it.

**Independent Test**: Can be fully tested by providing a role with `meta/main.yml` and verifying that the parser outputs structured JSON containing galaxy_info (author, description, license, platforms) and dependencies. Delivers immediate value for basic role identification.

**Acceptance Scenarios**:

1. **Given** a role directory with `meta/main.yml` containing galaxy_info, **When** parser executes, **Then** output includes author, description, license, company, min_ansible_version, and platforms as structured data
2. **Given** a role with dependencies listed in `meta/main.yml`, **When** parser executes, **Then** output includes array of dependencies with role names and versions
3. **Given** a role with `meta/argument_specs.yml` (Ansible 2.11+), **When** parser executes, **Then** output includes argument specifications with option names, types, required status, and descriptions
4. **Given** a role without `meta/main.yml`, **When** parser executes, **Then** parser logs warning and continues with empty metadata

---

### User Story 2 - Parse Variable Definitions with Annotations (Priority: P1) 🎯 MVP

As an Ansible role developer, I need the parser to extract variables from `defaults/main.yml` and `vars/main.yml` with their associated inline annotations (@var) so that documentation automatically describes variable purpose, type, default values, and usage examples.

**Why this priority**: Variables are the primary interface for configuring roles. Without variable documentation, users cannot effectively use the role. This is essential for MVP.

**Independent Test**: Can be fully tested by providing YAML files with annotated variables and verifying that the parser extracts variable names, values, annotations including type, description, examples, and deprecation status. Delivers standalone value for variable documentation.

**Acceptance Scenarios**:

1. **Given** `defaults/main.yml` with simple variables (strings, booleans, numbers), **When** parser executes, **Then** output includes variable name, value, and type inference
2. **Given** variables with single-line `@var` annotations like `# @var demo_var: Description text`, **When** parser executes, **Then** output includes variable name and associated description
3. **Given** variables with multiline `@var` annotations using `# @var demo_var: > ... @end`, **When** parser executes, **Then** output includes complete multiline description text
4. **Given** variables with JSON-formatted annotations like `# @var demo_var: $ {"type": "string", "example": "value"}`, **When** parser executes, **Then** output includes parsed type, description, example, required, and deprecated fields
5. **Given** variables marked as deprecated with `"deprecated": "Use new_var instead"`, **When** parser executes, **Then** output flags variable as deprecated with migration message
6. **Given** complex nested variables (dictionaries, lists), **When** parser executes, **Then** output preserves structure and annotates nested keys if documented

---

### User Story 3 - Extract Task Tags and Descriptions (Priority: P2)

As an Ansible role developer, I need the parser to discover all task tags from `tasks/*.yml` files and their associated descriptions (via `@tag` annotations) so that documentation explains what each tag controls and when to use it.

**Why this priority**: Task tags enable selective playbook execution. Documenting them helps users understand role capabilities and execution control. This is valuable but not blocking for basic documentation.

**Independent Test**: Can be fully tested by providing task files with tags and `@tag` annotations, verifying that output lists unique tags with descriptions. Delivers value for advanced role usage documentation.

**Acceptance Scenarios**:

1. **Given** task files with `tags: [install, configure]`, **When** parser executes, **Then** output includes list of unique tags found across all tasks
2. **Given** task file with `# @tag install: Installs required packages`, **When** parser executes, **Then** output associates "install" tag with description
3. **Given** tasks with multiple tags on single task, **When** parser executes, **Then** all tags are extracted without duplication
4. **Given** tasks without any tags, **When** parser executes, **Then** parser continues without error, tags section empty

---

### User Story 4 - Collect TODO Comments and Examples (Priority: P3)

As an Ansible role developer, I want the parser to extract `@todo` annotations and `@example` code blocks so that documentation includes known limitations and usage examples for future reference.

**Why this priority**: TODOs and examples enhance documentation quality but are not essential for initial release. These are nice-to-have features that improve developer experience.

**Independent Test**: Can be fully tested by providing files with `@todo` and `@example` annotations, verifying extraction into structured output. Delivers supplementary documentation value.

**Acceptance Scenarios**:

1. **Given** files with `# @todo: Implement feature X`, **When** parser executes, **Then** output includes list of TODO items with file location and line number
2. **Given** files with `# @example: > ... @end` blocks, **When** parser executes, **Then** output includes example code with associated context
3. **Given** files without TODO or example annotations, **When** parser executes, **Then** parser completes successfully with empty sections

---

### Edge Cases

- What happens when YAML files contain syntax errors?
  - Parser MUST log specific error with file path and line number, continue processing other files, mark role as partially parsed
- How does system handle circular role dependencies?
  - Parser MUST detect cycles in `meta/main.yml` dependencies, log warning, include dependencies in output with cycle flag
- What happens when annotation syntax is malformed?
  - Parser MUST log warning with file location, skip malformed annotation, continue processing remaining annotations
- How does parser handle extremely large roles (100+ variables, 1000+ lines)?
  - Parser MUST complete within performance requirements (<500ms per role), use streaming YAML parser for memory efficiency
- What happens when files use inconsistent YAML formatting (flow style vs block style)?
  - Parser MUST handle both YAML styles correctly using ruamel.yaml which preserves formatting context
- How does parser handle roles with multiple entry points (e.g., `tasks/main.yml` including other files)?
  - Parser MUST follow all includes/imports recursively, aggregate all tasks/tags/annotations from included files
- What happens when role directory structure is non-standard?
  - Parser MUST validate expected directories exist (tasks/, defaults/, vars/, meta/), log warnings for missing standard directories, continue processing available files

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Parser MUST accept role directory path as input (absolute or relative path)
- **FR-002**: Parser MUST discover and load all relevant YAML files: `meta/main.yml`, `meta/argument_specs.yml`, `defaults/main.yml`, `vars/main.yml`, `tasks/*.yml`
- **FR-003**: Parser MUST extract galaxy metadata including author, description, license, company, min_ansible_version, platforms, and dependencies from `meta/main.yml`
- **FR-004**: Parser MUST parse argument specifications from `meta/argument_specs.yml` when present (Ansible 2.11+)
- **FR-005**: Parser MUST extract all variables from `defaults/main.yml` and `vars/main.yml` with names, values, and inferred types
- **FR-006**: Parser MUST detect and parse annotation comments in format `# @type key: value` for types: var, tag, todo, example, meta
- **FR-007**: Parser MUST support three annotation formats: single-line (`# @var name: text`), multiline (`# @var name: > ... @end`), and JSON (`# @var name: $ {...}`)
- **FR-008**: Parser MUST extract annotation attributes including: type, description, example, required, deprecated, default
- **FR-009**: Parser MUST discover all task tags from task files and collect unique tag list
- **FR-010**: Parser MUST associate `@tag` annotations with corresponding tag names for descriptions
- **FR-011**: Parser MUST collect all `@todo` annotations with file location (path and line number)
- **FR-012**: Parser MUST extract `@example` code blocks with associated context
- **FR-013**: Parser MUST output structured data in JSON format containing all extracted metadata, variables, tags, todos, and examples
- **FR-014**: Parser MUST log warnings for: missing expected files, YAML syntax errors, malformed annotations, circular dependencies
- **FR-015**: Parser MUST log informational messages for: files processed, annotations found, processing completion
- **FR-016**: Parser MUST continue processing remaining files when individual file parsing fails (resilient parsing)
- **FR-017**: Parser MUST provide CLI interface with options: `--role-path <path>`, `--output <file>`, `--format json`, `--log-level <level>`
- **FR-018**: Parser MUST validate role directory structure exists before processing
- **FR-019**: Parser MUST handle YAML files in both block style and flow style formats
- **FR-020**: Parser MUST recursively follow task includes/imports to aggregate all tasks
- **FR-021**: Parser MUST support recursive role directory scanning with `--recursive` flag
- **FR-022**: Parser MUST respect `.ansibledoctor-ignore` patterns for excluding files
- **FR-023**: Parser MUST infer variable types from values: string, number, boolean, list, dictionary, null
- **FR-024**: Parser MUST preserve variable structure for complex nested types

### Key Entities

- **AnsibleRole**: Represents a complete Ansible role with metadata, variables, tasks, and annotations
  - Attributes: path, name, metadata (galaxy_info), dependencies, variables, tasks, tags, todos, examples
  - Root entity containing all parsed information

- **RoleMetadata**: Galaxy metadata from `meta/main.yml`
  - Attributes: author, description, license, company, min_ansible_version, platforms (list), dependencies (list)
  - Relationships: Belongs to one AnsibleRole

- **ArgumentSpec**: Role argument specification from `meta/argument_specs.yml`
  - Attributes: entry_point (main/alternate), options (dict of option definitions)
  - Relationships: Belongs to one AnsibleRole

- **Variable**: Role variable definition
  - Attributes: name, value, type (inferred), source (defaults/vars), annotations
  - Relationships: Belongs to one AnsibleRole, has zero or more Annotations

- **Annotation**: Inline documentation comment
  - Attributes: type (@var, @tag, @todo, @example, @meta), key, content, file_path, line_number, parsed_attributes (dict)
  - Relationships: Associated with Variable, Tag, or standalone

- **Tag**: Ansible task tag
  - Attributes: name, description (from @tag annotation), usage_count
  - Relationships: Belongs to one AnsibleRole, may have one Annotation

- **TodoItem**: Open task annotation
  - Attributes: description, file_path, line_number, priority (if specified)
  - Relationships: Belongs to one AnsibleRole

- **Example**: Usage example code block
  - Attributes: title, code, description, language (yaml/jinja2)
  - Relationships: Belongs to one AnsibleRole

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Parser successfully extracts metadata from 95%+ of valid Ansible roles (tested against 50+ real-world roles from Ansible Galaxy)
- **SC-002**: Parser completes processing of typical role (10-30 variables, 20-50 tasks) in under 500ms on standard hardware
- **SC-003**: Parser handles YAML syntax errors gracefully, logging error and continuing for 100% of test cases
- **SC-004**: Parser extracts all annotation types (@var, @tag, @todo, @example) with 100% accuracy when properly formatted
- **SC-005**: Developers can integrate parser output into documentation generation pipeline without manual data transformation
- **SC-006**: Parser memory usage remains under 50MB for roles with up to 100 variables and 200 tasks
- **SC-007**: Parser correctly identifies and warns about circular dependencies in 100% of test cases
- **SC-008**: Parser CLI provides clear error messages that enable users to resolve issues without reading source code in 90%+ of error scenarios
- **SC-009**: Parser handles malformed annotations by logging warning and continuing without crash in 100% of cases
- **SC-010**: Parser output JSON schema is consistent and documented, enabling third-party tool integration

## Assumptions

- Roles follow standard Ansible role directory structure (tasks/, defaults/, vars/, meta/)
- YAML files are encoded in UTF-8
- Annotation syntax follows documented convention (existing ansible-doctor patterns)
- Roles use Ansible 2.9+ (minimum supported version)
- File system is readable and accessible
- Role directories are on local file system (no remote parsing in MVP)
- Python 3.11+ runtime environment is available

## Non-Functional Requirements

- **Performance**: Process typical role in <500ms, large role (100+ vars) in <2 seconds
- **Reliability**: Graceful error handling with no uncaught exceptions, continue-on-error semantics
- **Maintainability**: Code follows constitutional principles (Library-First, Test-First, SOLID)
- **Observability**: Structured logging with context (file paths, line numbers, operation types)
- **Compatibility**: Compatible with existing ansible-doctor annotation syntax for smooth migration
