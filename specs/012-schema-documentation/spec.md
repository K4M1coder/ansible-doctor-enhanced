# Feature Specification: Schema Documentation & Validation

**Feature Branch**: `012-schema-documentation`  
**Created**: 2025-12-02  
**Milestone**: v0.10.0  
**Prerequisites**: v0.9.0 (Execution Reports) COMPLETE ✅  
**Status**: Draft

## Objective

**INFRASTRUCTURE SERVICE** (cross-cutting concern)

Provide unified schema documentation, validation, and serialization services for ansible-doctor-enhanced. Enable reading/writing YAML, JSON, XML, Mermaid formats using state-of-the-art libraries. Provide schema export capabilities and configuration validation. Connect to existing features without duplication, extending them through clean APIs.

## What is Schema Documentation & Validation?

Schema Documentation & Validation provides infrastructure services for:

- **Multi-Format Serialization**: Unified API for reading/writing YAML, JSON, XML, Mermaid
- **Schema Export**: Generate JSON Schema, OpenAPI specs, or custom schemas from data models
- **Configuration Validation**: Validate `.ansibledoctor.yml` against schema (extends Spec 003)
- **Format Conversion**: Convert between formats (e.g., YAML config → JSON schema → Mermaid diagram)
- **State-of-the-Art Libraries**: Use best-in-class libraries (pydantic, jsonschema, ruamel.yaml, etc.)

**Existing Capabilities** (don't duplicate):
- Spec 009: JSON report generation (consume this service)
- Spec 011: Mermaid diagram generation (consume this service)
- Spec 003: Basic config validation (extend with proper schema validation)

**Enhancement Goals**:
- Provide schema validation for all configuration files
- Enable schema export for IDE integration and documentation
- Support format conversion for interoperability
- Provide unified serialization API for all features

**Schema Export Example**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AnsibleDoctorConfig",
  "type": "object",
  "properties": {
    "output_format": {
      "type": "string",
      "enum": ["markdown", "html", "rst"],
      "default": "markdown"
    },
    "languages": {
      "type": "object",
      "properties": {
        "default": {"type": "string", "enum": ["en", "fr", "de"]},
        "enabled": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

## User Scenarios & Testing

### User Story 1 - Validate Configuration Files (Priority: P1) 🎯 MVP

As a user configuring ansible-doctor, I want my `.ansibledoctor.yml` files to be validated against a schema so that I catch configuration errors early with helpful messages.

**Why this priority**: Configuration errors are common and hard to debug. Schema validation provides immediate feedback.

**Independent Test**: Create invalid `.ansibledoctor.yml` → `ansible-doctor config validate` shows specific validation errors with line numbers.

**Acceptance Scenarios**:

1. **Given** `.ansibledoctor.yml` with invalid `output_format: "invalid"`, **When** validating, **Then** error shows "output_format must be one of: markdown, html, rst"
2. **Given** config with unknown property `custom_field: value`, **When** validating, **Then** warning shows "Unknown property 'custom_field' ignored"
3. **Given** config with type mismatch `verbose: "true"` (should be boolean), **When** validating, **Then** error shows "verbose must be boolean, got string"
4. **Given** valid config, **When** validating, **Then** success message shows "Configuration is valid"
5. **Given** config with deprecated property, **When** validating, **Then** warning shows deprecation notice with migration path

---

### User Story 2 - Export Configuration Schema (Priority: P1) 🎯 MVP

As an IDE developer, I want to access the JSON Schema for ansible-doctor configuration so that I can provide autocomplete and validation in my editor.

**Why this priority**: IDE integration improves developer experience. JSON Schema is the standard for configuration validation.

**Independent Test**: Run `ansible-doctor schema export config` → JSON Schema file generated for `.ansibledoctor.yml`.

**Acceptance Scenarios**:

1. **Given** request for config schema, **When** exporting, **Then** valid JSON Schema generated with all properties, types, defaults, and descriptions
2. **Given** `--format openapi` flag, **When** exporting, **Then** OpenAPI 3.0 spec generated instead of JSON Schema
3. **Given** `--output schema.json` flag, **When** exporting, **Then** schema written to specified file
4. **Given** schema export, **When** used in VS Code, **Then** provides autocomplete for `.ansibledoctor.yml` files
5. **Given** schema includes examples, **When** viewed in documentation, **Then** examples show valid configuration patterns

---

### User Story 3 - Convert Between Formats (Priority: P2)

As a tool integrator, I want to convert ansible-doctor data between formats so that I can integrate with different systems and workflows.

**Why this priority**: Format conversion enables interoperability. Different tools expect different formats.

**Independent Test**: Run `ansible-doctor convert config.yml --to json` → YAML config converted to JSON format.

**Acceptance Scenarios**:

1. **Given** YAML config file, **When** converting to JSON, **Then** equivalent JSON produced with proper formatting
2. **Given** parsed role data, **When** converting to XML, **Then** valid XML structure generated
3. **Given** project hierarchy, **When** converting to Mermaid, **Then** flowchart diagram generated (extends Spec 011)
4. **Given** execution report, **When** converting to YAML, **Then** human-readable YAML format produced
5. **Given** conversion with `--pretty` flag, **When** outputting JSON/XML, **Then** properly indented and formatted

---

### User Story 4 - Validate Data Models (Priority: P2)

As a developer extending ansible-doctor, I want to validate my data structures against schemas so that I ensure data consistency and catch bugs early.

**Why this priority**: Data validation prevents runtime errors. Schemas serve as documentation and contracts.

**Independent Test**: Create invalid role data → Schema validation catches the error with specific path and message.

**Acceptance Scenarios**:

1. **Given** role data with missing required field, **When** validating against schema, **Then** error shows "meta.main.yml: missing required field 'author'"
2. **Given** collection data with invalid dependency format, **When** validating, **Then** error shows "galaxy.yml: dependencies[0] must be string or object"
3. **Given** valid data, **When** validating, **Then** success returned with no errors
4. **Given** schema validation in tests, **When** data changes, **Then** tests fail with clear validation errors
5. **Given** `--strict-validation` flag, **When** warnings exist, **Then** treated as errors

---

### User Story 5 - Generate Schema Documentation (Priority: P3)

As a documentation maintainer, I want to generate human-readable schema documentation so that users understand configuration options and their effects.

**Why this priority**: Schema documentation helps users understand complex configurations. Auto-generated docs stay in sync.

**Independent Test**: Run `ansible-doctor schema docs config` → Markdown documentation generated from schema.

**Acceptance Scenarios**:

1. **Given** config schema, **When** generating docs, **Then** Markdown file created with sections for each property, types, defaults, examples
2. **Given** schema with descriptions, **When** generating docs, **Then** descriptions included in the documentation
3. **Given** nested objects, **When** generating docs, **Then** proper heading hierarchy created
4. **Given** enum values, **When** generating docs, **Then** all possible values listed with descriptions
5. **Given** deprecated properties, **When** generating docs, **Then** marked as deprecated with migration notes

---

### Edge Cases

- What happens when schema library is not installed? → Graceful fallback with warning, basic validation only
- What happens when converting between incompatible formats? → Clear error explaining incompatibility
- How does system handle very large schemas (1000+ properties)? → Streaming generation, pagination for docs
- What happens when config has recursive references? → Cycle detection with clear error message
- How does system handle format-specific features (YAML anchors, XML namespaces)? → Preserve features when possible, warn when lost in conversion

## Requirements

### Functional Requirements

- **FR-001**: System MUST validate `.ansibledoctor.yml` files against JSON Schema with detailed error messages
- **FR-002**: System MUST export JSON Schema for all configuration options with descriptions and examples
- **FR-003**: System MUST support format conversion between YAML, JSON, XML, Mermaid using state-of-the-art libraries
- **FR-004**: System MUST validate internal data models against schemas for consistency
- **FR-005**: System MUST generate human-readable schema documentation from JSON Schema
- **FR-006**: System MUST support schema export in multiple formats (JSON Schema, OpenAPI, custom)
- **FR-007**: System MUST provide CLI commands: `schema validate <file>`, `schema export <type>`, `schema docs <type>`, `convert <file> --to <format>`
- **FR-008**: System MUST use best-in-class libraries: `pydantic` (models), `jsonschema` (validation), `ruamel.yaml` (YAML), `xml.etree` (XML), `mermaid-py` (Mermaid)
- **FR-009**: System MUST provide schema validation for all existing data models (extends Specs 001-011)
- **FR-010**: System MUST support custom schema extensions for user-defined configurations
- **FR-011**: System MUST cache compiled schemas for performance
- **FR-012**: System MUST provide migration assistance for deprecated configuration options
- **FR-013**: System MUST support schema versioning with backward compatibility
- **FR-014**: System MUST integrate with IDEs via Language Server Protocol for real-time validation
- **FR-015**: System MUST provide schema diff functionality for configuration changes

### Key Entities

- **SchemaValidator**: Validates data against JSON Schema with detailed error reporting
- **SchemaExporter**: Exports schemas in various formats (JSON Schema, OpenAPI, Mermaid)
- **FormatConverter**: Converts between supported formats while preserving data
- **SchemaDocumenter**: Generates human-readable documentation from schemas
- **ConfigurationValidator**: Specialized validator for `.ansibledoctor.yml` files
- **DataModelValidator**: Validates internal data structures against schemas

## Success Criteria

### Measurable Outcomes

- **SC-001**: Configuration validation catches 100% of syntax errors with actionable messages
- **SC-002**: Schema export enables full IDE autocomplete for configuration files
- **SC-003**: Format conversion preserves 100% of data fidelity between supported formats
- **SC-004**: Schema documentation stays in sync with code (no manual updates needed)
- **SC-005**: Validation performance overhead <10ms for typical configurations
- **SC-006**: Exported schemas are valid according to their respective specifications
- **SC-007**: IDE integration provides real-time validation without performance impact

## Technical Constraints

- **TC-001**: MUST use state-of-the-art libraries (no custom parsing implementations)
- **TC-002**: MUST extend existing validation in Spec 003 (not replace)
- **TC-003**: MUST consume existing format generation from Specs 009/011 (not duplicate)
- **TC-004**: MUST provide read-only APIs for other specs to access schemas
- **TC-005**: MUST support JSON Schema Draft 2020-12 as primary schema format
- **TC-006**: MUST maintain backward compatibility with existing configurations
- **TC-007**: MUST not break existing functionality when adding validation

## Integration Points

**Extends Spec 003**: Adds proper schema validation to the existing config validation TODO
**Consumes Spec 009**: Uses JSON serialization for reports
**Consumes Spec 011**: Uses Mermaid generation for schema diagrams
**Provides to All Specs**: Schema validation and export services

## Required Tasks in Other Specs

To enable this feature, other specs need to expose their data models:

**Spec 003** (Config): Add T104-T106 for schema exposure
**Spec 001/004/006** (Parsers): Add T104-T106 for data model schemas
**Spec 009** (Reports): Add T104-T106 for report schema export

