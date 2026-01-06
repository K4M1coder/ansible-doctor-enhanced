# Tasks: Schema Documentation & Validation

**Input**: Design documents from `/specs/012-schema-documentation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per Constitution §III (TDD). All tests must be written BEFORE implementation (Red-Green-Refactor).

**Cross-Spec Dependencies**:
- **Extends Spec 003**: Add proper schema validation to existing `ansibledoctor/config/` module
- **Provides to All Specs**: SchemaService for format conversion and validation
- **Library Versions**: pydantic>=2.0, jsonschema>=4.0, ruamel.yaml>=0.17

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (5 tasks, ~3 hours) ✅ COMPLETE

**Purpose**: Project initialization and basic structure

- [X] T001 Create validation module at ansibledoctor/validation/__init__.py
- [X] T002 [P] Create serialization module at ansibledoctor/serialization/__init__.py
- [X] T003 [P] Create schema models at ansibledoctor/models/schemas.py with SchemaModel, ValidationError, ValidationResult base classes
- [X] T004 [P] Create test fixtures directory at tests/fixtures/schemas/ with config_schema.json
- [X] T005 [P] Create test fixtures for configs at tests/fixtures/configs/ with valid_config.yml and invalid_config.yml

---

## Phase 2: Foundational (9 tasks, ~7 hours) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Write tests for ValidationError model in tests/unit/test_schema_models.py (formatted_message, severity properties)
- [X] T007 Implement ValidationError model in ansibledoctor/models/schemas.py with path, message, validator, expected, actual, suggestion, line_number fields
- [X] T008 [P] Write tests for ValidationResult model in tests/unit/test_schema_models.py (error_count, format_report, raise_if_invalid)
- [X] T009 [P] Implement ValidationResult model in ansibledoctor/models/schemas.py with is_valid, errors, warnings, format_report() method
- [X] T010 [P] Write tests for SchemaModel base class in tests/unit/test_schema_models.py (schema_version, id fields)
- [X] T011 [P] Implement SchemaModel base class in ansibledoctor/models/schemas.py with schema_version, id, schema_uri fields
- [X] T012 Install jsonschema library (add to pyproject.toml dependencies)
- [X] T013 [P] Install ruamel.yaml library (add to pyproject.toml dependencies) - already present
- [X] T014 Create test fixtures with sample schemas and configs in tests/fixtures/ (valid/invalid examples)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - Configuration Validation (15 tasks, ~8 hours, Priority: P1) 🎯 MVP - ✅ COMPLETE

**Goal**: Validate `.ansibledoctor.yml` files against JSON Schema with detailed error messages

**Independent Test**: Create invalid `.ansibledoctor.yml` → `ansible-doctor config validate` shows specific validation errors with line numbers

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T015 [P] [US1] Write test for invalid output_format in tests/integration/test_config_validator.py (enum validation error)
- [X] T016 [P] [US1] Write test for unknown property in tests/integration/test_config_validator.py (warning for unknown field)
- [X] T017 [P] [US1] Write test for type mismatch in tests/integration/test_config_validator.py (verbose: "true" string instead of boolean)
- [X] T018 [P] [US1] Write test for valid config in tests/integration/test_config_validator.py (success message)
- [X] T019 [P] [US1] Write test for deprecated property in tests/integration/test_config_validator.py (deprecation warning with migration path)

### Implementation for User Story 1

- [X] T020 [US1] Create SchemaValidator class in ansibledoctor/validation/schema_validator.py with validate() method
- [X] T021 [US1] Implement JSON Schema validation logic in SchemaValidator using jsonschema library
- [X] T022 [US1] Implement line number extraction from YAML parser in SchemaValidator (use ruamel.yaml for source tracking)
- [X] T023 [US1] Create ConfigurationValidator class in ansibledoctor/validation/config_validator.py extending SchemaValidator
- [X] T024 [US1] Implement config schema definition in ConfigurationValidator (JSON Schema for .ansibledoctor.yml)
- [X] T025 [US1] Add validation error formatting in ConfigurationValidator (convert jsonschema errors to ValidationError models)
- [X] T026 [US1] Implement suggestion generation for common errors in ConfigurationValidator
- [X] T027 [US1] Create CLI command structure at ansibledoctor/cli/schema.py with schema command group
- [X] T028 [US1] Add `ansible-doctor config validate <file>` CLI command in ansibledoctor/cli/schema.py
- [X] T029 [US1] Integrate validation into config loading in ansibledoctor/cli/__init__.py (registered schema command group)

**Checkpoint**: ✅ User Story 1 COMPLETE - 29 tests passing (21 validation + 8 CLI), validation functional

---

## Phase 4: User Story 2 - Export Configuration Schema (14 tasks, ~11 hours, Priority: P1) 🎯 MVP

**Goal**: Export JSON Schema for ansible-doctor configuration to enable IDE autocomplete

**Independent Test**: Run `ansible-doctor schema export config` → JSON Schema file generated for `.ansibledoctor.yml`

### Tests for User Story 2 ⚠️

- [ ] T030 [P] [US2] Write test for JSON Schema export in tests/integration/test_schema_exporter.py (valid schema with all properties)
- [ ] T031 [P] [US2] Write test for OpenAPI format export in tests/integration/test_schema_exporter.py (--format openapi)
- [ ] T032 [P] [US2] Write test for file output in tests/integration/test_schema_exporter.py (--output schema.json)
- [ ] T033 [P] [US2] Write test for VS Code integration in tests/integration/test_ide_integration.py (schema provides autocomplete)
- [ ] T034 [P] [US2] Write test for schema examples in tests/unit/test_schema_exporter.py (examples included in schema)

### Implementation for User Story 2

- [ ] T035 [US2] Create SchemaExporter class in ansibledoctor/serialization/schema_exporter.py with export_schema() method
- [ ] T036 [US2] Implement pydantic to JSON Schema conversion in SchemaExporter (use model.model_json_schema())
- [ ] T037 [US2] Implement OpenAPI 3.1 schema export in SchemaExporter (convert JSON Schema to OpenAPI format)
- [ ] T038 [US2] Add schema metadata enrichment in SchemaExporter (descriptions, examples, default values)
- [ ] T039 [US2] Implement $schema property injection in SchemaExporter (for IDE recognition)
- [ ] T040 [US2] Add `ansible-doctor schema export <type>` CLI command in ansibledoctor/cli/schema.py
- [ ] T041 [US2] Add --format flag to schema export command (json, openapi options)
- [ ] T042 [US2] Add --output flag to schema export command (write to file)
- [ ] T043 [US2] Create example VS Code settings.json in docs/ for schema integration

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Convert Between Formats (13 tasks, ~10 hours, Priority: P2)

**Goal**: Convert ansible-doctor data between formats (YAML, JSON, XML, Mermaid)

**Independent Test**: Run `ansible-doctor convert config.yml --to json` → YAML config converted to JSON format

### Tests for User Story 3 ⚠️

- [ ] T044 [P] [US3] Write test for YAML to JSON conversion in tests/integration/test_format_conversion.py (round-trip preserves data)
- [ ] T045 [P] [US3] Write test for JSON to XML conversion in tests/integration/test_format_conversion.py (valid XML structure)
- [ ] T046 [P] [US3] Write test for Mermaid diagram generation in tests/integration/test_format_conversion.py (extends Spec 011)
- [ ] T047 [P] [US3] Write test for YAML to JSON round-trip in tests/integration/test_format_conversion.py (data fidelity)
- [ ] T048 [P] [US3] Write test for pretty formatting in tests/unit/test_format_converter.py (--pretty flag)

### Implementation for User Story 3

- [ ] T049 [US3] Create FormatConverter class in ansibledoctor/serialization/format_converter.py with convert() method
- [ ] T050 [US3] Implement YAML to JSON conversion in FormatConverter using ruamel.yaml and json
- [ ] T051 [US3] Implement JSON to XML conversion in FormatConverter using xml.etree.ElementTree
- [ ] T052 [US3] Implement XML to JSON conversion in FormatConverter
- [ ] T053 [US3] Implement Mermaid diagram generation in FormatConverter (delegate to Spec 011 MermaidBuilder)
- [ ] T054 [US3] Add pretty formatting support in FormatConverter (indentation, line breaks)
- [ ] T055 [US3] Add `ansible-doctor convert <file> --to <format>` CLI command in ansibledoctor/cli/schema.py
- [ ] T056 [US3] Add --pretty flag to convert command

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Validate Data Models (12 tasks, ~9 hours, Priority: P2)

**Goal**: Validate internal data structures against schemas to ensure consistency

**Independent Test**: Create invalid role data → Schema validation catches the error with specific path and message

### Tests for User Story 4 ⚠️

- [ ] T057 [P] [US4] Write test for missing required field in tests/unit/test_model_validator.py (role missing author)
- [ ] T058 [P] [US4] Write test for invalid dependency format in tests/unit/test_model_validator.py (collection dependencies)
- [ ] T059 [P] [US4] Write test for valid data validation in tests/unit/test_model_validator.py (success with no errors)
- [ ] T060 [P] [US4] Write test for strict validation mode in tests/unit/test_model_validator.py (warnings as errors)
- [ ] T061 [P] [US4] Write test for schema validation in tests in tests/integration/test_schema_validation_e2e.py (test failures with validation errors)

### Implementation for User Story 4

- [ ] T062 [US4] Create DataModelValidator class in ansibledoctor/validation/model_validator.py with validate_model() method
- [ ] T063 [US4] Implement schema generation from pydantic models in DataModelValidator
- [ ] T064 [US4] Implement validation of role data against schema in DataModelValidator
- [ ] T065 [US4] Implement validation of collection data against schema in DataModelValidator
- [ ] T066 [US4] Add strict validation mode in DataModelValidator (--strict-validation flag treats warnings as errors)
- [ ] T067 [US4] Add --strict-validation CLI flag in ansibledoctor/cli/schema.py
- [ ] T068 [US4] Create integration examples showing data model validation in tests/

---

## Phase 7: User Story 5 - Generate Schema Documentation (11 tasks, ~9 hours, Priority: P3)

**Goal**: Generate human-readable schema documentation from JSON Schema

**Independent Test**: Run `ansible-doctor schema docs config` → Markdown documentation generated from schema

### Tests for User Story 5 ⚠️

- [ ] T069 [P] [US5] Write test for Markdown generation in tests/unit/test_schema_documenter.py (sections for each property)
- [ ] T070 [P] [US5] Write test for descriptions in docs in tests/unit/test_schema_documenter.py (schema descriptions included)
- [ ] T071 [P] [US5] Write test for nested objects in tests/unit/test_schema_documenter.py (proper heading hierarchy)
- [ ] T072 [P] [US5] Write test for enum values in tests/unit/test_schema_documenter.py (all values listed)
- [ ] T073 [P] [US5] Write test for deprecated properties in tests/unit/test_schema_documenter.py (marked as deprecated)

### Implementation for User Story 5

- [ ] T074 [US5] Create SchemaDocumenter class in ansibledoctor/serialization/schema_documenter.py with generate_docs() method
- [ ] T075 [US5] Implement Markdown generation from JSON Schema in SchemaDocumenter
- [ ] T076 [US5] Implement property documentation in SchemaDocumenter (type, default, description, examples)
- [ ] T077 [US5] Implement nested object handling in SchemaDocumenter (recursive documentation with proper heading levels)
- [ ] T078 [US5] Implement enum documentation in SchemaDocumenter (list all possible values)
- [ ] T079 [US5] Add `ansible-doctor schema docs <type>` CLI command in ansibledoctor/cli/schema.py

---

## Phase 8: Polish & Cross-Cutting Concerns (12 tasks, ~8 hours)

**Purpose**: Improvements that affect multiple user stories

- [ ] T080 [P] Update CHANGELOG.md with Spec 012 feature summary (schema validation, export, conversion)
- [ ] T081 [P] Create user guide docs/SCHEMA_GUIDE.md (usage examples for all schema commands)
- [ ] T082 [P] Update README.md with schema feature showcase (validation, IDE integration, format conversion)
- [ ] T083 [P] Add quickstart examples to docs/ (config validation, schema export, format conversion)
- [ ] T084 Create schema cache implementation in ansibledoctor/utils/schema_cache.py (compiled schema caching with LRU eviction)
- [ ] T085 Write tests for schema caching in tests/unit/test_schema_cache.py (cache hit/miss, invalidation)
- [ ] T086 Implement schema versioning in SchemaExporter (support multiple schema versions)
- [ ] T087 [P] Add schema diff functionality in SchemaExporter (compare schema versions, show changes)
- [ ] T088 Write comprehensive integration test in tests/integration/test_schema_validation_e2e.py (end-to-end with all features)
- [ ] T089 Performance test large configs in tests/integration/test_schema_performance.py (500+ properties < 10ms)
- [ ] T090 Update cli help text in ansibledoctor/cli/schema.py (document all schema commands with examples)
- [ ] T091 Run quickstart.md validation (ensure all examples work correctly)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May use US2 schema export but testable independently
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - May use US1 validation but testable independently
- **User Story 5 (P3)**: Depends on US2 (schema export) - Uses exported schemas to generate docs

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before validators/converters
- Core validation/conversion logic before CLI integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and US2 can start in parallel (both P1 MVP)
- All tests for a user story marked [P] can run in parallel
- US3 and US4 can run in parallel after Foundational phase
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write test for invalid output_format in tests/integration/test_config_validator.py"
Task: "Write test for unknown property in tests/integration/test_config_validator.py"
Task: "Write test for type mismatch in tests/integration/test_config_validator.py"
Task: "Write test for valid config in tests/integration/test_config_validator.py"
Task: "Write test for deprecated property in tests/integration/test_config_validator.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (config validation)
4. Complete Phase 4: User Story 2 (schema export)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready

**MVP Deliverable**: Configuration validation with helpful error messages + schema export for IDE integration

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (config validation works!)
3. Add User Story 2 → Test independently → Deploy/Demo (IDE integration enabled!)
4. Add User Story 3 → Test independently → Deploy/Demo (format conversion available)
5. Add User Story 4 → Test independently → Deploy/Demo (data model validation)
6. Add User Story 5 → Test independently → Deploy/Demo (schema documentation)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (config validation)
   - Developer B: User Story 2 (schema export)
   - Developer C: User Story 3 (format conversion)
3. After US1+US2 complete:
   - Developer D: User Story 4 (model validation)
   - Developer E: User Story 5 (schema docs)
4. Stories complete and integrate independently

---

## Backward Compatibility Regression Tasks

These tasks ensure existing functionality is not broken:

- [ ] T092 [REGRESSION] Run existing Spec 001-008 test suites to verify no regressions
- [ ] T093 [REGRESSION] Verify existing `.ansibledoctor.yml` configs remain valid without changes
- [ ] T094 [REGRESSION] Test that existing config loading behavior unchanged without validation flag

---

## Success Metrics

- ✅ Configuration validation catches 100% of syntax errors (SC-001)
- ✅ Schema export enables full IDE autocomplete (SC-002)
- ✅ Format conversion preserves 100% of data fidelity (SC-003)
- ✅ Schema documentation stays in sync with code (SC-004)
- ✅ Validation performance overhead <10ms (SC-005)
- ✅ Exported schemas are valid per specifications (SC-006)
- ✅ IDE integration provides real-time validation (SC-007)
- ✅ Test coverage >85% for new code
- ✅ All 15 functional requirements (FR-001 to FR-015) implemented
- ✅ Constitution compliance verified (TDD, Library-First, CLI Mandate, Observability, Backward Compatibility)

---

## Notes

- **jsonschema library**: Use for JSON Schema Draft 2020-12 validation (Phase 2, T012)
- **ruamel.yaml**: Use for YAML parsing with comment preservation and line number tracking (Phase 2, T013)
- **Extends Spec 003**: Add proper schema validation to existing config validation (Phase 3, T029)
- **Consumes Spec 011**: Reuse MermaidBuilder for diagram generation (Phase 5, T053)
- **IDE Integration**: Use $schema property in config files for VS Code autocomplete (Phase 4, T039)
- **Performance**: Target <10ms validation for typical configs, <50ms schema export, <100ms conversions
- **Caching**: Compile and cache schemas in memory with LRU eviction (Phase 8, T084-T085)
- **Error Messages**: Provide actionable suggestions for common errors (Phase 3, T026)
- **Backward Compatibility**: Existing configs remain valid, validation is opt-in (no breaking changes)
