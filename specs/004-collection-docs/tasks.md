# Tasks: Collection Documentation (Feature 004)

**Feature Branch**: `004-collection-support`  
**Target Version**: v0.5.0  
**Created**: 2025-11-20

**Input**: Design documents from `specs/004-collection-docs/`
- ✅ spec.md (user stories US8-US10)
- ✅ plan.md (implementation phases, architecture)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

**Path Convention**: Single project structure
- Implementation: `ansibledoctor/` (models/, parser/, generator/, cli/)
- Tests: `tests/` (unit/, integration/, property/, e2e/)

**Clarifications Applied (Session 2025-11-20)**:
- galaxy.yml: Only required fields (namespace, name, version, authors, dependencies); optional fields deferred to v0.6.0
- Schema version: 1.0.0 (Ansible 2.9+ standard)
- Plugin discovery: No file exclusions (parse all Python files, let validation filter)
- Role index format: Template-configurable (table vs list decided by template)

---

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US8, US9, US10)
- All tasks include exact file paths

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Prepare project structure for collection documentation feature

- [ ] T001 Create directory structure: ansibledoctor/models/collection.py, ansibledoctor/parser/collection_parser.py
- [ ] T002 Create test directories: tests/unit/models/collection/, tests/unit/parser/collection/
- [ ] T003 [P] Create fixtures directory: tests/fixtures/collections/ with mock collection structure
- [ ] T004 [P] Update pyproject.toml dependencies (verify `packaging` exists for version parsing)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create YAMLLoader protocol extension in ansibledoctor/utils/yaml_loader.py (for galaxy.yml)
- [ ] T006 [P] Create PathResolver utility in ansibledoctor/utils/paths.py (collection path resolution)
- [ ] T007 [P] Create FileSystemWalker in ansibledoctor/utils/fs_walker.py (discover roles/plugins)
- [ ] T008 Create base PluginType enum in ansibledoctor/models/plugin.py (module, filter, lookup, etc.)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 8 - Parse Collection Metadata (Priority: P1) 🎯 MVP

**Goal**: Parse galaxy.yml and extract collection metadata (namespace, name, version, dependencies, authors)

**Independent Test**: Run `ansible-doctor-enhanced collection parse my_namespace.my_collection/` → JSON output with collection metadata

### Tests for User Story 8 (TDD RED Phase)

> **TDD CYCLE**: Write these tests FIRST, ensure they FAIL before implementation

#### T009-T020: Galaxy Metadata Model Tests

- [ ] T009 [P] [US8] Test: GalaxyMetadata model with valid data (required fields: namespace, name, version, authors, dependencies) in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T010 [P] [US8] Test: GalaxyMetadata validates namespace format (lowercase alphanumeric) in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T011 [P] [US8] Test: GalaxyMetadata validates semantic version format in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T012 [P] [US8] Test: GalaxyMetadata rejects invalid namespace (uppercase, special chars) in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T013 [P] [US8] Test: GalaxyMetadata.fqcn property returns "namespace.name" in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T014 [P] [US8] Test: GalaxyMetadata immutability (frozen model) in tests/unit/models/collection/test_galaxy_metadata.py
- [ ] T015 [P] [US8] Test: GalaxyMetadata with minimal required fields only (namespace, name, version) in tests/unit/models/collection/test_galaxy_metadata.py

#### T016-T025: Galaxy Parser Tests

- [ ] T016 [P] [US8] Test: GalaxyMetadataParser parses valid galaxy.yml in tests/unit/parser/collection/test_galaxy_parser.py
- [ ] T017 [P] [US8] Test: GalaxyMetadataParser raises FileNotFoundError for missing galaxy.yml in tests/unit/parser/collection/test_galaxy_parser.py
- [ ] T018 [P] [US8] Test: GalaxyMetadataParser raises YAMLError for malformed galaxy.yml in tests/unit/parser/collection/test_galaxy_parser.py
- [ ] T019 [P] [US8] Test: GalaxyMetadataParser validates required fields (namespace, name, version) in tests/unit/parser/collection/test_galaxy_parser.py
- [ ] T020 [P] [US8] Test: GalaxyMetadataParser extracts dependencies with version constraints in tests/unit/parser/collection/test_galaxy_parser.py

#### T021-T030: Collection Structure Discovery Tests

- [ ] T021 [P] [US8] Test: Discover roles/ directory and list role names in tests/unit/parser/collection/test_collection_structure.py
- [ ] T022 [P] [US8] Test: Discover plugins/modules/ directory and list modules in tests/unit/parser/collection/test_collection_structure.py
- [ ] T023 [P] [US8] Test: Handle missing roles/ directory gracefully in tests/unit/parser/collection/test_collection_structure.py
- [ ] T024 [P] [US8] Test: Handle missing plugins/ directory gracefully in tests/unit/parser/collection/test_collection_structure.py
- [ ] T025 [P] [US8] Test: Discover multiple plugin types (modules, filters, lookups) in tests/unit/parser/collection/test_collection_structure.py

#### T026-T035: Collection Model Tests

- [ ] T026 [P] [US8] Test: AnsibleCollection model with metadata + roles + plugins in tests/unit/models/collection/test_collection.py
- [ ] T027 [P] [US8] Test: AnsibleCollection.fqcn delegates to metadata.fqcn in tests/unit/models/collection/test_collection.py
- [ ] T028 [P] [US8] Test: AnsibleCollection lists role names in tests/unit/models/collection/test_collection.py
- [ ] T029 [P] [US8] Test: AnsibleCollection lists plugin names by type in tests/unit/models/collection/test_collection.py
- [ ] T030 [P] [US8] Test: AnsibleCollection validates dependencies (no circular self-reference) in tests/unit/models/collection/test_collection.py

#### T031-T035: Property-Based Tests (Hypothesis)

- [ ] T031 [P] [US8] Property test: GalaxyMetadata with random valid namespaces/names in tests/property/test_galaxy_metadata_properties.py
- [ ] T032 [P] [US8] Property test: GalaxyMetadata rejects invalid versions in tests/property/test_galaxy_metadata_properties.py
- [ ] T033 [P] [US8] Property test: Random collection structures (0-10 roles, 0-20 plugins) in tests/property/test_collection_structure_properties.py

### Implementation for User Story 8 (TDD GREEN Phase)

#### T034-T040: GalaxyMetadata Model Implementation

- [ ] T034 [P] [US8] Implement GalaxyMetadata Pydantic model (schema 1.0.0, required fields only: namespace, name, version, authors, dependencies) in ansibledoctor/models/galaxy.py
- [ ] T035 [US8] Add field validators for namespace (pattern r"^[a-z0-9_]+$") in ansibledoctor/models/galaxy.py
- [ ] T036 [US8] Add field validator for version (packaging.version.Version) in ansibledoctor/models/galaxy.py
- [ ] T037 [US8] Add fqcn property (returns f"{namespace}.{name}") in ansibledoctor/models/galaxy.py
- [ ] T038 [US8] Make GalaxyMetadata immutable (frozen=True in Config) in ansibledoctor/models/galaxy.py
- [ ] T039 [US8] Add docstrings with examples to GalaxyMetadata in ansibledoctor/models/galaxy.py
- [ ] T040 [US8] Add __str__ and __repr__ methods in ansibledoctor/models/galaxy.py

#### T041-T048: GalaxyMetadataParser Implementation

- [ ] T041 [P] [US8] Implement GalaxyMetadataParser class in ansibledoctor/parser/galaxy_parser.py
- [ ] T042 [US8] Implement parse_galaxy_file() method (read galaxy.yml, validate) in ansibledoctor/parser/galaxy_parser.py
- [ ] T043 [US8] Add error handling for FileNotFoundError with actionable message in ansibledoctor/parser/galaxy_parser.py
- [ ] T044 [US8] Add error handling for YAML parsing errors in ansibledoctor/parser/galaxy_parser.py
- [ ] T045 [US8] Add validation for required fields (namespace, name, version) in ansibledoctor/parser/galaxy_parser.py
- [ ] T046 [US8] Extract dependencies dict and validate format in ansibledoctor/parser/galaxy_parser.py
- [ ] T047 [US8] Add structured logging (logger.info for successful parse) in ansibledoctor/parser/galaxy_parser.py
- [ ] T048 [US8] Add docstrings and type hints to all methods in ansibledoctor/parser/galaxy_parser.py

#### T049-T056: Collection Structure Discovery Implementation

- [ ] T049 [P] [US8] Implement CollectionStructureWalker in ansibledoctor/parser/collection_walker.py
- [ ] T050 [US8] Implement discover_roles() method (find roles/ subdirs) in ansibledoctor/parser/collection_walker.py
- [ ] T051 [US8] Implement discover_plugins() method (find plugins/*/*) in ansibledoctor/parser/collection_walker.py
- [ ] T052 [US8] Add plugin type detection (modules, filters, lookups); no file exclusions - parse all Python files, validation filters invalid plugins in ansibledoctor/parser/collection_walker.py
- [ ] T053 [US8] Handle missing directories gracefully (return empty list, log warning) in ansibledoctor/parser/collection_walker.py
- [ ] T054 [US8] Add caching for discovered structures (performance) in ansibledoctor/parser/collection_walker.py
- [ ] T055 [US8] Add structured logging for discovery operations in ansibledoctor/parser/collection_walker.py
- [ ] T056 [US8] Add docstrings and type hints in ansibledoctor/parser/collection_walker.py

#### T057-T065: AnsibleCollection Model Implementation

- [ ] T057 [P] [US8] Implement AnsibleCollection Pydantic model in ansibledoctor/models/collection.py
- [ ] T058 [US8] Add metadata: GalaxyMetadata field in ansibledoctor/models/collection.py
- [ ] T059 [US8] Add roles: List[str] field (role names) in ansibledoctor/models/collection.py
- [ ] T060 [US8] Add plugins: Dict[PluginType, List[str]] field in ansibledoctor/models/collection.py
- [ ] T061 [US8] Add fqcn property (delegates to metadata.fqcn) in ansibledoctor/models/collection.py
- [ ] T062 [US8] Add validator to prevent self-dependencies in ansibledoctor/models/collection.py
- [ ] T063 [US8] Add helper methods: list_roles(), list_plugins_by_type() in ansibledoctor/models/collection.py
- [ ] T064 [US8] Add docstrings with examples in ansibledoctor/models/collection.py
- [ ] T065 [US8] Add __str__ and __repr__ methods in ansibledoctor/models/collection.py

#### T066-T072: CollectionParser (Main Entry Point)

- [ ] T066 [US8] Implement CollectionParser class in ansibledoctor/parser/collection_parser.py
- [ ] T067 [US8] Implement parse() method (orchestrate galaxy + structure parsing) in ansibledoctor/parser/collection_parser.py
- [ ] T068 [US8] Add path validation (check collection_path exists) in ansibledoctor/parser/collection_parser.py
- [ ] T069 [US8] Integrate GalaxyMetadataParser in ansibledoctor/parser/collection_parser.py
- [ ] T070 [US8] Integrate CollectionStructureWalker in ansibledoctor/parser/collection_parser.py
- [ ] T071 [US8] Build and return AnsibleCollection model in ansibledoctor/parser/collection_parser.py
- [ ] T072 [US8] Add structured logging and error handling in ansibledoctor/parser/collection_parser.py

#### T073-T078: CLI Parse Command (US8)

- [ ] T073 [US8] Create collection subcommand group in ansibledoctor/cli/collection.py
- [ ] T074 [US8] Implement `collection parse` command in ansibledoctor/cli/collection.py
- [ ] T075 [US8] Add --output option (default stdout) in ansibledoctor/cli/collection.py
- [ ] T076 [US8] Add --pretty option for JSON formatting in ansibledoctor/cli/collection.py
- [ ] T077 [US8] Add --validate flag (parse only, no output) in ansibledoctor/cli/collection.py
- [ ] T078 [US8] Add error handling and exit codes in ansibledoctor/cli/collection.py

### Refactoring for User Story 8 (TDD REFACTOR Phase)

- [ ] T079 [US8] Refactor: Extract common validation logic to base validator
- [ ] T080 [US8] Refactor: Improve error messages with actionable suggestions
- [ ] T081 [US8] Refactor: Add type hints to all public APIs
- [ ] T082 [US8] Refactor: Optimize path resolution performance

### Integration Tests for User Story 8

- [ ] T083 [US8] Integration test: Parse real community.general metadata in tests/integration/test_real_collections.py
- [ ] T084 [US8] Integration test: Parse mock collection with all fields in tests/integration/test_collection_parsing.py
- [ ] T085 [US8] Integration test: CLI parse command end-to-end in tests/e2e/test_collection_cli.py

**Checkpoint**: User Story 8 complete - can parse collection metadata and structure independently

---

## Phase 4: User Story 9 - Generate Collection Documentation (Priority: P1)

**Goal**: Generate comprehensive collection README with overview, installation, role index, plugin list

**Independent Test**: Run `ansible-doctor-enhanced collection generate my_namespace.my_collection/` → README.md with collection overview

### Tests for User Story 9 (TDD RED Phase)

#### T086-T095: Plugin Model Tests

- [ ] T086 [P] [US9] Test: Plugin model with name, type, path, description in tests/unit/models/collection/test_plugin.py
- [ ] T087 [P] [US9] Test: PluginType enum (module, filter, lookup, test, inventory, callback) in tests/unit/models/collection/test_plugin.py
- [ ] T088 [P] [US9] Test: Plugin immutability (frozen model) in tests/unit/models/collection/test_plugin.py
- [ ] T089 [P] [US9] Test: PluginCatalog groups plugins by type in tests/unit/models/collection/test_plugin_catalog.py
- [ ] T090 [P] [US9] Test: PluginCatalog lists all plugin names in tests/unit/models/collection/test_plugin_catalog.py

#### T091-T100: Plugin Discovery Tests

- [ ] T091 [P] [US9] Test: Discover Python modules in plugins/modules/ in tests/unit/parser/collection/test_plugin_discovery.py
- [ ] T092 [P] [US9] Test: Extract plugin name from filename in tests/unit/parser/collection/test_plugin_discovery.py
- [ ] T093 [P] [US9] Test: Detect plugin type from directory path in tests/unit/parser/collection/test_plugin_discovery.py
- [ ] T094 [P] [US9] Test: Handle empty plugin directories in tests/unit/parser/collection/test_plugin_discovery.py
- [ ] T095 [P] [US9] Test: Validate and filter invalid plugins (validation filtering instead of file exclusions) in tests/unit/parser/collection/test_plugin_discovery.py

#### T096-T105: CollectionRole Model Tests

- [ ] T096 [P] [US9] Test: CollectionRole extends existing Role model in tests/unit/models/collection/test_collection_role.py
- [ ] T097 [P] [US9] Test: CollectionRole adds collection_fqcn field in tests/unit/models/collection/test_collection_role.py
- [ ] T098 [P] [US9] Test: CollectionRole computes full role name (fqcn.role_name) in tests/unit/models/collection/test_collection_role.py
- [ ] T099 [P] [US9] Test: CollectionRole reuses existing role parsing logic in tests/unit/models/collection/test_collection_role.py

#### T100-T110: Template Tests

- [ ] T100 [P] [US9] Test: Render collection template with metadata in tests/unit/generator/test_collection_template.py
- [ ] T101 [P] [US9] Test: Template includes installation instructions in tests/unit/generator/test_collection_template.py
- [ ] T102 [P] [US9] Test: Template includes role index with descriptions (format configurable: table or list) in tests/unit/generator/test_collection_template.py
- [ ] T103 [P] [US9] Test: Template includes plugin list grouped by type in tests/unit/generator/test_collection_template.py
- [ ] T104 [P] [US9] Test: Template includes dependencies section in tests/unit/generator/test_collection_template.py
- [ ] T105 [P] [US9] Test: Template includes examples/playbooks section in tests/unit/generator/test_collection_template.py

#### T106-T115: CollectionDocumentationGenerator Tests

- [ ] T106 [P] [US9] Test: Generator accepts AnsibleCollection model in tests/unit/generator/test_collection_generator.py
- [ ] T107 [P] [US9] Test: Generator builds template context in tests/unit/generator/test_collection_generator.py
- [ ] T108 [P] [US9] Test: Generator renders Markdown output in tests/unit/generator/test_collection_generator.py
- [ ] T109 [P] [US9] Test: Generator supports HTML output format in tests/unit/generator/test_collection_generator.py
- [ ] T110 [P] [US9] Test: Generator supports RST output format in tests/unit/generator/test_collection_generator.py
- [ ] T111 [P] [US9] Test: Generator writes to output file in tests/unit/generator/test_collection_generator.py
- [ ] T112 [P] [US9] Test: Generator uses custom template if provided in tests/unit/generator/test_collection_generator.py

### Implementation for User Story 9 (TDD GREEN Phase)

#### T113-T120: Plugin Model Implementation

- [ ] T113 [P] [US9] Implement Plugin Pydantic model in ansibledoctor/models/plugin.py
- [ ] T114 [US9] Implement PluginType enum (module, filter, lookup, test, inventory, callback) in ansibledoctor/models/plugin.py
- [ ] T115 [US9] Add fields: name, type, path, short_description (optional) in ansibledoctor/models/plugin.py
- [ ] T116 [US9] Make Plugin immutable (frozen=True) in ansibledoctor/models/plugin.py
- [ ] T117 [US9] Implement PluginCatalog class in ansibledoctor/models/plugin_catalog.py
- [ ] T118 [US9] Add group_by_type() method in ansibledoctor/models/plugin_catalog.py
- [ ] T119 [US9] Add list_all_names() method in ansibledoctor/models/plugin_catalog.py
- [ ] T120 [US9] Add docstrings and type hints in ansibledoctor/models/plugin.py

#### T121-T128: Plugin Discovery Implementation

- [ ] T121 [P] [US9] Implement PluginDiscovery class in ansibledoctor/parser/plugin_discovery.py
- [ ] T122 [US9] Implement discover_plugins() method (scan plugins/ tree) in ansibledoctor/parser/plugin_discovery.py
- [ ] T123 [US9] Add plugin type detection from path in ansibledoctor/parser/plugin_discovery.py
- [ ] T124 [US9] Parse all Python files; add validation to filter invalid plugins (no file exclusions per TC-002) in ansibledoctor/parser/plugin_discovery.py
- [ ] T125 [US9] Extract plugin name from filename in ansibledoctor/parser/plugin_discovery.py
- [ ] T126 [US9] Build Plugin models for discovered plugins in ansibledoctor/parser/plugin_discovery.py
- [ ] T127 [US9] Add structured logging in ansibledoctor/parser/plugin_discovery.py
- [ ] T128 [US9] Add docstrings and type hints in ansibledoctor/parser/plugin_discovery.py

#### T129-T135: CollectionRole Implementation

- [ ] T129 [P] [US9] Create CollectionRole model extending Role in ansibledoctor/models/collection_role.py
- [ ] T130 [US9] Add collection_fqcn: str field in ansibledoctor/models/collection_role.py
- [ ] T131 [US9] Add full_role_name property (f"{collection_fqcn}.{role_name}") in ansibledoctor/models/collection_role.py
- [ ] T132 [US9] Implement CollectionRoleParser in ansibledoctor/parser/collection_role_parser.py
- [ ] T133 [US9] Integrate existing RoleParser for parsing role structure in ansibledoctor/parser/collection_role_parser.py
- [ ] T134 [US9] Add collection context to parsed roles in ansibledoctor/parser/collection_role_parser.py
- [ ] T135 [US9] Add docstrings and type hints in ansibledoctor/models/collection_role.py

#### T136-T145: Collection Template Implementation

- [ ] T136 [US9] Create collection.md.j2 template in ansibledoctor/templates/collection.md.j2
- [ ] T137 [US9] Add template header: title, description, version in ansibledoctor/templates/collection.md.j2
- [ ] T138 [US9] Add installation section with ansible-galaxy command in ansibledoctor/templates/collection.md.j2
- [ ] T139 [US9] Add roles section (format configurable: table or heading-based list) in ansibledoctor/templates/collection.md.j2
- [ ] T140 [US9] Add plugins section grouped by type in ansibledoctor/templates/collection.md.j2
- [ ] T141 [US9] Add dependencies section with version constraints in ansibledoctor/templates/collection.md.j2
- [ ] T142 [US9] Add examples/playbooks section in ansibledoctor/templates/collection.md.j2
- [ ] T143 [US9] Add footer with generator version in ansibledoctor/templates/collection.md.j2
- [ ] T144 [US9] Add Jinja2 filters for formatting (markdown_escape, etc.) in ansibledoctor/templates/collection.md.j2
- [ ] T145 [US9] Validate template syntax with test render in ansibledoctor/templates/collection.md.j2

#### T146-T155: CollectionDocumentationGenerator Implementation

- [ ] T146 [P] [US9] Implement CollectionDocumentationGenerator in ansibledoctor/generator/collection_generator.py
- [ ] T147 [US9] Implement generate() method (main entry point) in ansibledoctor/generator/collection_generator.py
- [ ] T148 [US9] Build template context from AnsibleCollection model in ansibledoctor/generator/collection_generator.py
- [ ] T149 [US9] Integrate existing TemplateEngine from Feature 002 in ansibledoctor/generator/collection_generator.py
- [ ] T150 [US9] Support output formats: markdown, html, rst in ansibledoctor/generator/collection_generator.py
- [ ] T151 [US9] Support custom template path option in ansibledoctor/generator/collection_generator.py
- [ ] T152 [US9] Write rendered output to file in ansibledoctor/generator/collection_generator.py
- [ ] T153 [US9] Add structured logging for generation steps in ansibledoctor/generator/collection_generator.py
- [ ] T154 [US9] Add error handling with actionable messages in ansibledoctor/generator/collection_generator.py
- [ ] T155 [US9] Add docstrings and type hints in ansibledoctor/generator/collection_generator.py

#### T156-T163: CLI Generate Command (US9)

- [ ] T156 [US9] Implement `collection generate` command in ansibledoctor/cli/collection.py
- [ ] T157 [US9] Add --output-dir option (default: docs/) in ansibledoctor/cli/collection.py
- [ ] T158 [US9] Add --format option (markdown|html|rst, default: markdown) in ansibledoctor/cli/collection.py
- [ ] T159 [US9] Add --template option (custom template path) in ansibledoctor/cli/collection.py
- [ ] T160 [US9] Add --include-role-docs flag in ansibledoctor/cli/collection.py
- [ ] T161 [US9] Add --config option (config file path) in ansibledoctor/cli/collection.py
- [ ] T162 [US9] Integrate CollectionParser and CollectionDocumentationGenerator in ansibledoctor/cli/collection.py
- [ ] T163 [US9] Add progress output and success messages in ansibledoctor/cli/collection.py

### Refactoring for User Story 9 (TDD REFACTOR Phase)

- [ ] T164 [US9] Refactor: Extract template context builder to separate class
- [ ] T165 [US9] Refactor: Optimize plugin discovery with parallel scanning
- [ ] T166 [US9] Refactor: Add template caching for performance
- [ ] T167 [US9] Refactor: Improve error messages in generator

### Integration Tests for User Story 9

- [ ] T168 [US9] Integration test: Generate docs for mock collection in tests/integration/test_collection_generation.py
- [ ] T169 [US9] Integration test: Generate docs for community.general subset in tests/integration/test_real_collections.py
- [ ] T170 [US9] Integration test: Generate HTML/RST formats in tests/integration/test_collection_generation.py
- [ ] T171 [US9] Integration test: CLI generate command end-to-end in tests/e2e/test_collection_cli.py
- [ ] T172 [US9] Integration test: Custom template usage in tests/integration/test_collection_generation.py

**Checkpoint**: User Story 9 complete - can generate collection documentation independently

---

## Phase 5: User Story 10 - Cross-Role Dependency Analysis (Priority: P2)

**Goal**: Visualize role dependencies within collection, detect circular dependencies

**Independent Test**: Run `ansible-doctor-enhanced collection analyze my_namespace.my_collection/ --show-dependencies` → Dependency graph

### Tests for User Story 10 (TDD RED Phase)

#### T173-T182: Dependency Graph Tests

- [ ] T173 [P] [US10] Test: Build dependency graph from roles in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T174 [P] [US10] Test: Detect role dependencies from meta/main.yml in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T175 [P] [US10] Test: Detect circular dependencies (A→B→C→A) in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T176 [P] [US10] Test: Handle missing dependencies gracefully in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T177 [P] [US10] Test: Build dependency tree (topological sort) in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T178 [P] [US10] Test: Export graph to Mermaid diagram format in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T179 [P] [US10] Test: Export graph to ASCII tree format in tests/unit/parser/collection/test_dependency_graph.py
- [ ] T180 [P] [US10] Test: Export graph to JSON format in tests/unit/parser/collection/test_dependency_graph.py

### Implementation for User Story 10 (TDD GREEN Phase)

#### T181-T190: DependencyGraph Implementation

- [ ] T181 [P] [US10] Implement DependencyGraph class in ansibledoctor/parser/dependency_graph.py
- [ ] T182 [US10] Implement build_graph() method (parse role dependencies) in ansibledoctor/parser/dependency_graph.py
- [ ] T183 [US10] Add detect_circular_dependencies() using DFS in ansibledoctor/parser/dependency_graph.py
- [ ] T184 [US10] Add topological_sort() for dependency order in ansibledoctor/parser/dependency_graph.py
- [ ] T185 [US10] Implement MermaidExporter in ansibledoctor/parser/dependency_graph.py
- [ ] T186 [US10] Implement ASCIITreeExporter in ansibledoctor/parser/dependency_graph.py
- [ ] T187 [US10] Implement JSONExporter in ansibledoctor/parser/dependency_graph.py
- [ ] T188 [US10] Add structured logging for dependency analysis in ansibledoctor/parser/dependency_graph.py
- [ ] T189 [US10] Add error handling for invalid dependencies in ansibledoctor/parser/dependency_graph.py
- [ ] T190 [US10] Add docstrings and type hints in ansibledoctor/parser/dependency_graph.py

#### T191-T197: CLI Analyze Command (US10)

- [ ] T191 [US10] Implement `collection analyze` command in ansibledoctor/cli/collection.py
- [ ] T192 [US10] Add --show-dependencies flag in ansibledoctor/cli/collection.py
- [ ] T193 [US10] Add --check-circular flag (exit code 1 if circular) in ansibledoctor/cli/collection.py
- [ ] T194 [US10] Add --output-format option (text|json|mermaid) in ansibledoctor/cli/collection.py
- [ ] T195 [US10] Integrate DependencyGraph parser in ansibledoctor/cli/collection.py
- [ ] T196 [US10] Display graph in requested format in ansibledoctor/cli/collection.py
- [ ] T197 [US10] Add colored output for warnings (circular deps) in ansibledoctor/cli/collection.py

### Refactoring for User Story 10 (TDD REFACTOR Phase)

- [ ] T198 [US10] Refactor: Optimize graph traversal for large collections
- [ ] T199 [US10] Refactor: Extract exporters to strategy pattern
- [ ] T200 [US10] Refactor: Add graph caching for repeated analyses

### Integration Tests for User Story 10

- [ ] T201 [US10] Integration test: Analyze mock collection with dependencies in tests/integration/test_dependency_analysis.py
- [ ] T202 [US10] Integration test: Detect circular dependencies in tests/integration/test_dependency_analysis.py
- [ ] T203 [US10] Integration test: Export to all formats in tests/integration/test_dependency_analysis.py
- [ ] T204 [US10] Integration test: CLI analyze command end-to-end in tests/e2e/test_collection_cli.py

**Checkpoint**: User Story 10 complete - can analyze dependencies independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, performance optimization, documentation

### T205-T210: Performance Optimization

- [ ] T205 [P] Profile collection parsing with cProfile in tests/performance/test_collection_performance.py
- [ ] T206 Optimize: Parallel role/plugin discovery with concurrent.futures
- [ ] T207 Optimize: Cache parsed galaxy.yml metadata
- [ ] T208 Optimize: Lazy load plugin details (don't parse source unless needed)
- [ ] T209 Performance test: Parse typical collection (5 roles, 10 plugins) in <5s
- [ ] T210 Performance test: Generate docs for 50-plugin collection in <10s

### T211-T220: Demo Collection Creation

- [ ] T211 Create demo collection structure: demo_namespace.demo_collection/
- [ ] T212 [P] Create demo galaxy.yml with comprehensive metadata
- [ ] T213 [P] Create 3 demo roles with dependencies
- [ ] T214 [P] Create 5 demo modules in plugins/modules/
- [ ] T215 [P] Create 3 demo filters in plugins/filters/
- [ ] T216 [P] Create example playbooks in playbooks/
- [ ] T217 Generate documentation for demo collection
- [ ] T218 Validate generated docs (manual review)
- [ ] T219 Add demo to tests/fixtures/collections/
- [ ] T220 Create DEMO-COLLECTION-RESULTS.md showcasing output

### T221-T230: Documentation

- [ ] T221 Create COLLECTION_GUIDE.md with usage examples
- [ ] T222 Add collection examples to README.md
- [ ] T223 Update CHANGELOG.md with v0.5.0 entries
- [ ] T224 Update CONFIG_GUIDE.md with collection config options
- [ ] T225 Add CLI reference for collection commands to README.md
- [ ] T226 Create migration guide from single roles to collections
- [ ] T227 Add troubleshooting section for common issues
- [ ] T228 Update API documentation with collection models
- [ ] T229 Add architecture diagram for collection parsing
- [ ] T230 Review and polish all documentation

### T231-T240: Cross-Platform Testing

- [ ] T231 [P] Run all tests on Windows in CI
- [ ] T232 [P] Run all tests on Linux in CI
- [ ] T233 [P] Run all tests on macOS in CI
- [ ] T234 Fix path separator issues (Windows backslashes)
- [ ] T235 Fix encoding issues (UTF-8 handling)
- [ ] T236 Test CLI on PowerShell (Windows)
- [ ] T237 Test CLI on Bash (Linux/macOS)
- [ ] T238 Validate demo collection on all platforms
- [ ] T239 Update CI/CD pipeline for cross-platform tests
- [ ] T240 Document platform-specific considerations

### T241-T250: Final Polish

- [ ] T241 Review all error messages for clarity and actionability
- [ ] T242 Enhance structured logging across all modules
- [ ] T243 Add progress bars for long operations (optional with tqdm)
- [ ] T244 Improve CLI help text and examples
- [ ] T245 Add shell completion scripts (bash, zsh, fish)
- [ ] T246 Review and update all docstrings
- [ ] T247 Run mypy --strict and fix all type errors
- [ ] T248 Run ruff linter and fix all issues
- [ ] T249 Verify test coverage meets 80% minimum (target 85%)
- [ ] T250 Final code review and cleanup

---

## Dependency Graph

**Story Completion Order** (based on priorities and dependencies):

```
Setup (Phase 1) → Foundational (Phase 2)
                        ↓
    ┌──────────────────┴──────────────────┐
    ↓                                      ↓
US8: Parse Metadata (P1) ────────→  US9: Generate Docs (P1)
                                            ↓
                                    US10: Dependency Analysis (P2)
                                            ↓
                                    Phase 6: Polish
```

**Independent Stories**: US8 and US9 can be partially parallelized (different files), but US9 depends on US8 models being complete.

**Critical Path**: Setup → Foundation → US8 → US9 → US10 → Polish

---

## Parallel Execution Examples

### Phase 3 (US8) Parallel Tasks:
Run simultaneously (different files, no dependencies):
- T009-T015 (galaxy metadata tests)
- T016-T020 (galaxy parser tests)  
- T021-T025 (structure discovery tests)
- T026-T030 (collection model tests)

Implementation:
- T034, T041, T049, T057 (all model/parser classes can start in parallel)

### Phase 4 (US9) Parallel Tasks:
Run simultaneously:
- T086-T090 (plugin model tests)
- T091-T095 (plugin discovery tests)
- T096-T099 (collection role tests)
- T100-T105 (template tests)

Implementation:
- T113, T121, T129, T136, T146 (all models/parsers/templates start in parallel)

### Phase 6 (Polish) Parallel Tasks:
Run simultaneously:
- T205, T212-T216 (performance + demo creation)
- T221-T228 (all documentation files)
- T231-T233 (cross-platform CI runs)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Target**: US8 + US9 (Parse + Generate) = Complete v0.5.0 MVP
- Parse collection metadata ✓
- Generate collection README ✓
- Basic plugin listing ✓
- Defer US10 to v0.6.0 if needed for timeline

### Incremental Delivery
**Week 1**: US8 complete (can parse collections, output JSON)
**Week 2**: US9 complete (can generate docs)
**Week 3**: US10 + polish (dependency analysis, performance, demo)

### TDD Workflow
Every task follows RED-GREEN-REFACTOR:
1. **RED**: Write failing test (T009-T033, T086-T115, T173-T180)
2. **GREEN**: Implement minimal code to pass (T034-T082, T113-T172, T181-T204)
3. **REFACTOR**: Improve code quality (T079-T082, T164-T167, T198-T200)

---

## Validation Criteria

### Test Coverage
- [ ] 130+ tests written (100 unit, 20 integration, 10 property, 5 e2e)
- [ ] All tests passing (poetry run pytest -v)
- [ ] Coverage ≥80% overall (poetry run pytest --cov)
- [ ] Coverage ≥90% for parsers and models

### Code Quality
- [ ] No mypy errors (poetry run mypy ansibledoctor --strict)
- [ ] No ruff linting errors (poetry run ruff check ansibledoctor)
- [ ] All docstrings present (public APIs)
- [ ] Type hints on all functions

### Performance
- [ ] Parse typical collection (5 roles, 10 plugins) in <5s
- [ ] Generate docs in <3s
- [ ] Memory usage <200MB for typical collection

### Documentation
- [ ] COLLECTION_GUIDE.md created (3000+ words)
- [ ] README.md updated with collection examples
- [ ] CHANGELOG.md updated for v0.5.0
- [ ] Demo collection with generated docs

### CLI
- [ ] All commands functional: parse, generate, analyze
- [ ] Help text clear and accurate (--help)
- [ ] Exit codes correct (0=success, 1=error, 2=usage)
- [ ] Error messages actionable

---

## Success Metrics

**Quantitative**:
- 250 tasks completed (T001-T250)
- 130+ tests passing
- 80%+ code coverage
- <5s collection parsing
- 0 critical bugs
- 0 mypy/ruff errors

**Qualitative**:
- First comprehensive Ansible collection documentation tool
- Competitive advantage over ansible-doctor
- Foundation for v0.6.0 (Project Documentation)
- Positive user feedback on generated documentation

---

## Task Summary

**Total Tasks**: 250
- **Setup**: 4 tasks (T001-T004)
- **Foundational**: 4 tasks (T005-T008)
- **User Story 8**: 85 tasks (T009-T085) - Parse collection metadata
- **User Story 9**: 87 tasks (T086-T172) - Generate documentation
- **User Story 10**: 32 tasks (T173-T204) - Dependency analysis
- **Polish**: 46 tasks (T205-T250) - Performance, demo, docs, testing

**By Type**:
- Tests (RED): ~80 tasks
- Implementation (GREEN): ~140 tasks
- Refactoring (REFACTOR): ~15 tasks
- Documentation: ~15 tasks

**Estimated Duration**: 60-80 hours (2-3 weeks)

---

**Tasks Status**: ✅ READY FOR IMPLEMENTATION

**Next Action**: Begin T001 - Create directory structure

*Tasks created following Constitution Article III (TDD), Article VI (SemVer), Article X (DDD), and SpecKit task generation workflow*
