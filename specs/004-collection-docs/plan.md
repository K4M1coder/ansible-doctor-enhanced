# Implementation Plan: Collection Documentation (Feature 004)

**Feature Branch**: `004-collection-support`  
**Created**: 2025-11-20  
**Target Version**: v0.5.0  
**Estimated Effort**: 60-80 hours (2-3 weeks)  
**Prerequisites**: v0.4.0 (Role Parity) ✅ COMPLETE

---

## Overview

This plan follows **Test-Driven Development (TDD)** principles mandated by Constitution Article III. Each phase follows the **RED-GREEN-REFACTOR** cycle:

1. **RED**: Write failing test defining desired behavior
2. **GREEN**: Write minimal code to make test pass
3. **REFACTOR**: Improve code quality while keeping tests green

All implementation tasks are detailed in `tasks.md` with TDD task IDs (T001-T100+).

---

## Clarifications Applied (Session 2025-11-20)

Based on requirements quality review, the following clarifications have been integrated:

1. **galaxy.yml Fields**: Only required fields (namespace, name, version, authors, dependencies) in v0.5.0; optional fields (tags, license, repository) deferred to v0.6.0
2. **Schema Version**: Support galaxy.yml schema version 1.0.0 (Ansible 2.9+ standard)
3. **Plugin Discovery**: No file exclusions (parse all Python files, let validation filter invalid plugins)
4. **Role Index Format**: Template-configurable (table vs list decided by template, not hardcoded)

These clarifications simplify v0.5.0 scope while maintaining flexibility for future enhancements.

---

## Architecture Overview

### Domain-Driven Design (Constitution Article X)

**Bounded Contexts**:
- **Collection Parsing Context** (new): Parse galaxy.yml, discover collection structure
- **Role Parsing Context** (existing): Reuse from Feature 001-003
- **Documentation Generation Context** (existing): Reuse from Feature 002
- **CLI Context** (extend): Add collection subcommands

**Ubiquitous Language**:
- `Collection`: Ansible Galaxy collection (namespace.name format)
- `GalaxyMetadata`: Collection metadata from galaxy.yml
- `CollectionRole`: Role within a collection (extends existing Role concept)
- `Plugin`: Ansible plugin (module, filter, lookup, etc.)
- `PluginType`: Categorization (module, filter, lookup, test, callback, inventory)
- `CollectionDependency`: Dependency on another collection with version constraint

**Aggregates**:
- `AnsibleCollection` (root aggregate): Contains GalaxyMetadata, CollectionRoles, Plugins
- `GalaxyMetadata` (value object): Immutable collection metadata
- `CollectionRole` (entity): Role within collection context
- `Plugin` (value object): Plugin metadata (name, type, path)

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│ CLI Layer (ansibledoctor/cli/collection.py)            │
│ - collection generate, parse, analyze commands         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Application Layer (ansibledoctor/generator/)           │
│ - CollectionDocumentationGenerator                     │
│ - Orchestrates parsing → template rendering           │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Domain Layer (ansibledoctor/models/, parser/)          │
│ - AnsibleCollection, GalaxyMetadata, Plugin models     │
│ - GalaxyMetadataParser, PluginDiscovery                │
│ - CollectionParser (root aggregate)                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│ Infrastructure Layer (ansibledoctor/utils/)            │
│ - YAMLLoader (parse galaxy.yml)                        │
│ - FileSystemWalker (discover plugins/roles)            │
│ - PathResolver (resolve collection paths)              │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Galaxy Metadata Parsing (Week 1: 25-30h)

**Objective**: Parse galaxy.yml and model collection metadata

**Deliverables**:
1. `GalaxyMetadata` Pydantic model with validation (T001-T005)
2. `GalaxyMetadataParser` to parse galaxy.yml (T006-T010)
3. Collection structure discovery (roles/, plugins/ directories) (T011-T015)
4. `AnsibleCollection` aggregate model (T016-T020)
5. Unit tests for all parsers (40+ tests) (T021-T030)

### TDD Workflow (Example: T001-T002)

**T001 (RED)**: Write failing test for GalaxyMetadata model
```python
# tests/unit/models/test_galaxy_metadata.py
def test_parse_valid_galaxy_yml():
    """Test GalaxyMetadata model with valid galaxy.yml data (required fields only)."""
    data = {
        "namespace": "my_namespace",
        "name": "my_collection",
        "version": "1.0.0",
        "authors": ["Author Name <email@example.com>"],
        "dependencies": {"community.general": ">=3.0.0"}
    }
    # Optional fields (tags, license, repository) deferred to v0.6.0
    
    # This will FAIL - GalaxyMetadata doesn't exist yet
    metadata = GalaxyMetadata(**data)
    
    assert metadata.namespace == "my_namespace"
    assert metadata.name == "my_collection"
    assert metadata.fqcn == "my_namespace.my_collection"
    assert metadata.version == Version("1.0.0")
```

Run: `poetry run pytest tests/unit/models/test_galaxy_metadata.py::test_parse_valid_galaxy_yml -v`  
**Expected**: FAIL (ImportError: GalaxyMetadata doesn't exist)

**T002 (GREEN)**: Implement minimal GalaxyMetadata model
```python
# ansibledoctor/models/galaxy.py
from pydantic import BaseModel, Field
from typing import List, Dict

class GalaxyMetadata(BaseModel):
    """Collection metadata from galaxy.yml (schema version 1.0.0).
    
    Only required fields for v0.5.0. Optional fields (tags, license, 
    repository, description) deferred to v0.6.0.
    """
    
    namespace: str = Field(..., description="Collection namespace")
    name: str = Field(..., description="Collection name")
    version: str = Field(..., description="Semantic version")
    authors: List[str] = Field(default_factory=list)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        frozen = True  # Value object - immutable
    
    @property
    def fqcn(self) -> str:
        """Fully Qualified Collection Name."""
        return f"{self.namespace}.{self.name}"
```

Rerun: `poetry run pytest tests/unit/models/test_galaxy_metadata.py::test_parse_valid_galaxy_yml -v`  
**Expected**: PASS ✅

**T003 (REFACTOR)**: Add validation rules, docstrings, type hints
```python
from pydantic import BaseModel, Field, field_validator
from packaging.version import Version

class GalaxyMetadata(BaseModel):
    """Collection metadata from galaxy.yml (schema version 1.0.0).
    
    Represents immutable collection metadata following Ansible Galaxy
    collection format specification. Only required fields for v0.5.0;
    optional fields deferred to v0.6.0. All fields validated against
    Galaxy requirements.
    
    Examples:
        >>> metadata = GalaxyMetadata(
        ...     namespace="community",
        ...     name="general",
        ...     version="5.0.0"
        ... )
        >>> metadata.fqcn
        'community.general'
    """
    
    namespace: str = Field(
        ...,
        description="Collection namespace (lowercase alphanumeric)",
        min_length=2,
        pattern=r"^[a-z0-9_]+$"
    )
    name: str = Field(
        ...,
        description="Collection name (lowercase alphanumeric)",
        min_length=2,
        pattern=r"^[a-z0-9_]+$"
    )
    version: str = Field(
        ...,
        description="Semantic version (MAJOR.MINOR.PATCH)"
    )
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate semantic versioning format."""
        try:
            Version(v)  # Validate with packaging.version
        except Exception as e:
            raise ValueError(f"Invalid semantic version: {v}") from e
        return v
    
    # ... rest of fields with enhanced validation
```

Rerun tests: `poetry run pytest tests/unit/models/test_galaxy_metadata.py -v`  
**Expected**: All tests still PASS ✅

### Phase 1 Tasks Breakdown

| Task ID | Description | Type | Est. |
|---------|-------------|------|------|
| T001 | Write test: GalaxyMetadata model valid data | RED | 30m |
| T002 | Implement: GalaxyMetadata Pydantic model | GREEN | 1h |
| T003 | Refactor: Add validation, docstrings | REFACTOR | 1h |
| T004 | Write test: GalaxyMetadata invalid data | RED | 30m |
| T005 | Enhance: Validation rules (namespace format, version) | GREEN | 1h |
| T006 | Write test: Parse galaxy.yml file | RED | 30m |
| T007 | Implement: GalaxyMetadataParser class | GREEN | 2h |
| T008 | Write test: Galaxy file not found error | RED | 20m |
| T009 | Enhance: Error handling with actionable messages | GREEN | 1h |
| T010 | Refactor: Extract YAML loading to protocol | REFACTOR | 1h |
| T011 | Write test: Discover roles in collection | RED | 30m |
| T012 | Implement: Collection structure walker | GREEN | 2h |
| T013 | Write test: Discover plugins by type | RED | 30m |
| T014 | Implement: Plugin type detection | GREEN | 1.5h |
| T015 | Refactor: Extract directory discovery to utility | REFACTOR | 1h |
| T016 | Write test: AnsibleCollection aggregate model | RED | 30m |
| T017 | Implement: AnsibleCollection class | GREEN | 2h |
| T018 | Write test: Collection with dependencies | RED | 30m |
| T019 | Enhance: Dependency resolution validation | GREEN | 1.5h |
| T020 | Refactor: Collection model with rich domain logic | REFACTOR | 1h |
| T021-T030 | Unit tests: 30 additional test cases | RED/GREEN | 8h |

**Total Phase 1**: ~28 hours

---

## Phase 2: Plugin & Role Documentation (Week 2: 25-30h)

**Objective**: Parse plugins and integrate role documentation

**Deliverables**:
1. Python module parser (extract DOCUMENTATION block) (T031-T040)
2. `PluginDoc` model for plugin metadata (T041-T045)
3. Filter/lookup/test plugin parsers (T046-T055)
4. Plugin catalog generator (index all plugins) (T056-T060)
5. Integrate existing role parsers for collection roles (T061-T065)
6. Collection role parser (extend Role model) (T066-T070)
7. Integration tests with real collections (T071-T080)

### Plugin Parsing Architecture

**Plugin Types to Support**:
- **Modules** (Priority P1): Custom modules with DOCUMENTATION/EXAMPLES/RETURN blocks
- **Filters** (Priority P2): Jinja2 filters with docstrings
- **Lookups** (Priority P2): Lookup plugins
- **Tests** (Priority P3): Jinja2 test plugins
- **Inventory** (Priority P3): Dynamic inventory plugins
- **Callbacks** (Priority P3): Ansible callback plugins

**Module DOCUMENTATION Block Example**:
```python
# plugins/modules/my_module.py
DOCUMENTATION = r'''
---
module: my_module
short_description: Example module
description:
  - This is an example module
options:
  name:
    description: Name parameter
    required: true
    type: str
'''
```

**Parser Strategy**:
- **No File Exclusions**: Parse all Python files in plugins/ directories (TC-002 clarification)
- **Validation Filtering**: Let validation logic filter out __init__.py, __pycache__, .pyc files
- Use AST (Abstract Syntax Tree) parsing for Python modules
- Extract DOCUMENTATION, EXAMPLES, RETURN string constants
- Parse YAML within those strings to get structured data
- Fallback to regex if AST parsing fails (defensive programming)

### Phase 2 Tasks Breakdown

| Task ID | Description | Type | Est. |
|---------|-------------|------|------|
| T031 | Write test: Parse Python module with DOCUMENTATION | RED | 30m |
| T032 | Implement: Python AST parser for module files | GREEN | 3h |
| T033 | Write test: Extract DOCUMENTATION/EXAMPLES/RETURN | RED | 30m |
| T034 | Implement: Extract documentation blocks | GREEN | 2h |
| T035 | Refactor: Module parser with error recovery | REFACTOR | 1.5h |
| T036 | Write test: PluginDoc model | RED | 30m |
| T037 | Implement: PluginDoc Pydantic model | GREEN | 1.5h |
| T038 | Write test: Plugin catalog (list all plugins) | RED | 30m |
| T039 | Implement: PluginCatalog class | GREEN | 2h |
| T040 | Refactor: Plugin discovery with type detection | REFACTOR | 1h |
| T041 | Write test: Filter plugin parser | RED | 30m |
| T042 | Implement: FilterPluginParser | GREEN | 2h |
| T043 | Write test: Lookup plugin parser | RED | 30m |
| T044 | Implement: LookupPluginParser | GREEN | 2h |
| T045 | Refactor: Unified plugin parser interface | REFACTOR | 1h |
| T046-T055 | Additional plugin types (test, inventory, callback) | RED/GREEN | 6h |
| T056 | Write test: CollectionRole extends Role | RED | 30m |
| T057 | Implement: CollectionRole model | GREEN | 1h |
| T058 | Write test: Parse role within collection context | RED | 30m |
| T059 | Integrate: Existing RoleParser with collection paths | GREEN | 2h |
| T060 | Refactor: Role parser reusability | REFACTOR | 1h |
| T061-T070 | Integration tests: Real collections (community.general subset) | RED/GREEN | 5h |
| T071-T080 | Mock collection tests | RED/GREEN | 3h |

**Total Phase 2**: ~30 hours

---

## Phase 3: Documentation Generation (Week 3: 10-20h)

**Objective**: Generate collection-level documentation

**Deliverables**:
1. Collection template (`collection.md.j2`) (T081-T085)
2. Template context builder for collections (T086-T090)
3. Collection README generator (T091-T095)
4. CLI commands: `collection generate/parse/analyze` (T096-T100)
5. Documentation (COLLECTION_GUIDE.md, README update) (T101-T105)
6. Performance optimization (<5s for typical collection) (T106-T110)
7. Demo collection creation (T111-T115)

### Template Design

**Template Structure** (`ansibledoctor/templates/collection.md.j2`):
```jinja2
# {{ collection.metadata.fqcn }}

{{ collection.metadata.description }}

**Version:** {{ collection.metadata.version }}  
**Authors:** {{ collection.metadata.authors | join(', ') }}  
**License:** {{ collection.metadata.license | join(', ') }}

## Installation

```bash
ansible-galaxy collection install {{ collection.metadata.fqcn }}
```

## Roles

{{ collection.roles|length }} role(s) available:

{# Role index format is template-configurable (Clarification 2025-11-20) #}
{# This example uses heading format; table format also supported #}
{% for role in collection.roles %}
### {{ role.name }}

{{ role.metadata.description }}

**Variables:** {{ role.variables|length }}  
**Tags:** {{ role.tags|length }}  
**Dependencies:** {{ role.metadata.dependencies|length }}

[Full Role Documentation](roles/{{ role.name }}/README.md)

{% endfor %}

## Plugins

### Modules ({{ collection.plugins.modules|length }})

{% for module in collection.plugins.modules %}
- **{{ module.name }}**: {{ module.short_description }}
{% endfor %}

### Filters ({{ collection.plugins.filters|length }})

{% for filter in collection.plugins.filters %}
- **{{ filter.name }}**: {{ filter.description }}
{% endfor %}

## Dependencies

{% for dep_name, dep_version in collection.metadata.dependencies.items() %}
- `{{ dep_name }}` ({{ dep_version }})
{% endfor %}

---

*Documentation generated by ansible-doctor-enhanced v{{ version }}*
```

### Phase 3 Tasks Breakdown

| Task ID | Description | Type | Est. |
|---------|-------------|------|------|
| T081 | Write test: Render collection template | RED | 30m |
| T082 | Implement: collection.md.j2 template | GREEN | 2h |
| T083 | Write test: Template context builder | RED | 30m |
| T084 | Implement: CollectionTemplateContext | GREEN | 1.5h |
| T085 | Refactor: Template with all collection sections | REFACTOR | 1h |
| T086 | Write test: CollectionDocumentationGenerator | RED | 30m |
| T087 | Implement: Generator class | GREEN | 2h |
| T088 | Write test: Generate with multiple output formats | RED | 30m |
| T089 | Enhance: Support Markdown, HTML, RST formats | GREEN | 2h |
| T090 | Refactor: Reuse existing TemplateEngine | REFACTOR | 1h |
| T091 | Write test: CLI collection generate command | RED | 30m |
| T092 | Implement: collection generate subcommand | GREEN | 2h |
| T093 | Write test: CLI collection parse command | RED | 30m |
| T094 | Implement: collection parse subcommand (JSON output) | GREEN | 1.5h |
| T095 | Write test: CLI collection analyze command | RED | 30m |
| T096 | Implement: collection analyze (dependency graph) | GREEN | 2h |
| T097 | Refactor: CLI error handling and help messages | REFACTOR | 1h |
| T098 | Documentation: COLLECTION_GUIDE.md | DOCS | 2h |
| T099 | Documentation: Update README with collection examples | DOCS | 1h |
| T100 | Documentation: Update CHANGELOG for v0.5.0 | DOCS | 30m |
| T101 | Performance: Profile collection parsing | TEST | 1h |
| T102 | Optimize: Parallel role/plugin discovery | GREEN | 2h |
| T103 | Performance test: Parse 50-plugin collection <5s | RED/GREEN | 1h |
| T104 | Create demo collection: showcase all features | GREEN | 3h |
| T105 | Integration test: Generate demo collection docs | RED/GREEN | 1h |
| T106-T110 | Cross-platform testing (Windows, Linux, macOS) | TEST | 3h |
| T111-T115 | Final polish: Error messages, logging, edge cases | REFACTOR | 3h |

**Total Phase 3**: ~30 hours

---

## Testing Strategy

### Test Coverage Targets (Constitution Article III)
- **Minimum**: 80% for all new code
- **Target**: 90% for core logic (parsers, models)
- **Property Tests**: Use Hypothesis for galaxy.yml parsing edge cases

### Test Pyramid

```
                    /\
                   /  \
                  / E2E\     5 tests (CLI full workflow)
                 /______\
                /        \
               /Integration\   20 tests (Real collections)
              /____________\
             /              \
            /   Unit Tests   \  100+ tests (Models, parsers)
           /__________________\
```

### Test Categories

**Unit Tests** (100+ tests):
- `tests/unit/models/test_galaxy_metadata.py` (15 tests)
- `tests/unit/models/test_collection.py` (20 tests)
- `tests/unit/parser/test_galaxy_parser.py` (15 tests)
- `tests/unit/parser/test_plugin_parser.py` (25 tests)
- `tests/unit/parser/test_collection_parser.py` (20 tests)
- `tests/unit/generator/test_collection_generator.py` (10 tests)

**Integration Tests** (20 tests):
- `tests/integration/test_collection_parsing.py` (10 tests with mock collections)
- `tests/integration/test_real_collections.py` (5 tests with community.general subset)
- `tests/integration/test_collection_generation.py` (5 tests with full workflow)

**Property Tests** (10 tests):
- `tests/property/test_galaxy_metadata_properties.py` (Hypothesis for galaxy.yml fuzzing)
- `tests/property/test_collection_structure_properties.py` (Random collection structures)

**End-to-End Tests** (5 tests):
- `tests/e2e/test_collection_cli.py` (Full CLI workflow)

### Real Collections for Testing

**Target Collections** (subset parsing for integration tests):
- `community.general` (10 modules, 3 roles) - Large, well-structured
- `ansible.posix` (5 modules, 2 roles) - Smaller, simpler
- Mock collections (created in tests/fixtures/) - Edge cases

---

## CLI Interface Design

### New Subcommands

**1. `collection generate`** - Generate collection documentation
```bash
ansible-doctor-enhanced collection generate <collection-path> [OPTIONS]

Options:
  --output-dir PATH        Output directory (default: docs/)
  --format FORMAT          Output format: markdown|html|rst (default: markdown)
  --template PATH          Custom template file
  --include-role-docs      Generate individual role docs (default: false)
  --config FILE            Config file path

Examples:
  # Generate collection docs
  ansible-doctor-enhanced collection generate ./my_namespace.my_collection/

  # Generate with role docs
  ansible-doctor-enhanced collection generate ./my_collection/ --include-role-docs

  # Custom template
  ansible-doctor-enhanced collection generate ./my_collection/ --template custom.md.j2
```

**2. `collection parse`** - Parse collection to JSON (machine-readable)
```bash
ansible-doctor-enhanced collection parse <collection-path> [OPTIONS]

Options:
  --output FILE            Output JSON file (default: stdout)
  --pretty                 Pretty-print JSON (default: false)
  --validate               Validate collection structure only (exit code)

Examples:
  # Parse to stdout
  ansible-doctor-enhanced collection parse ./my_collection/

  # Parse to file
  ansible-doctor-enhanced collection parse ./my_collection/ --output collection.json --pretty

  # Validate only
  ansible-doctor-enhanced collection parse ./my_collection/ --validate
```

**3. `collection analyze`** - Analyze collection dependencies
```bash
ansible-doctor-enhanced collection analyze <collection-path> [OPTIONS]

Options:
  --show-dependencies      Show role dependencies graph
  --check-circular         Check for circular dependencies (exit code)
  --output-format FORMAT   Output format: text|json|mermaid (default: text)

Examples:
  # Show dependency graph
  ansible-doctor-enhanced collection analyze ./my_collection/ --show-dependencies

  # Check circular deps
  ansible-doctor-enhanced collection analyze ./my_collection/ --check-circular

  # Mermaid diagram output
  ansible-doctor-enhanced collection analyze ./my_collection/ --output-format mermaid
```

---

## Configuration Schema Extension

Extend `.ansibledoctor.yml` to support collection-level configuration:

```yaml
# Collection-specific configuration
collection:
  # Parse collection instead of single role
  enabled: true
  
  # Include individual role documentation pages
  include_role_docs: false
  
  # Plugin types to document
  plugin_types:
    - module
    - filter
    - lookup
    - test
  
  # Dependency analysis
  analyze_dependencies: true
  check_circular_deps: true
  
  # Output structure
  output:
    collection_readme: "README.md"
    role_docs_dir: "docs/roles/"
    plugin_docs_dir: "docs/plugins/"

# Template selection
template:
  collection: "collection.md.j2"
  # Existing role template still used for individual roles
  role: "role.md.j2"
```

---

## Performance Targets

**Success Criteria SC-006**: Collection documentation generation completes in <5s for typical collection

**Baseline Measurement**:
- v0.4.0 Role parsing: ~200ms per role (measured in performance tests)
- Target: 5 roles + 10 plugins + metadata < 5 seconds

**Optimization Strategies**:
1. **Parallel Discovery**: Use `concurrent.futures` to discover roles/plugins in parallel
2. **Lazy Loading**: Don't parse plugin source unless requested
3. **Caching**: Cache parsed galaxy.yml metadata
4. **Incremental Parsing**: Only re-parse changed files in watch mode

**Performance Tests**:
```python
# tests/performance/test_collection_performance.py
def test_parse_typical_collection_under_5s():
    """Test collection parsing meets performance target."""
    collection_path = create_mock_collection(roles=5, plugins=10)
    
    start = time.time()
    collection = CollectionParser.parse(collection_path)
    duration = time.time() - start
    
    assert duration < 5.0, f"Parsing took {duration:.2f}s, expected <5s"
```

---

## Risk Analysis & Mitigations

### Risk 1: Plugin Parsing Complexity (HIGH)
**Description**: Parsing Python module DOCUMENTATION blocks is complex (AST, YAML-in-strings)

**Impact**: High effort, potential bugs, performance issues

**Mitigation**:
- Start with modules only (Priority P1), defer other plugin types to v0.6.0
- Use defensive parsing: Try AST → Fallback to regex → Fallback to "undocumented"
- Leverage Ansible's existing module documentation (don't reinvent)
- Consider: Just list plugins without detailed parsing for v0.5.0

**Decision**: List plugins by name/type for v0.5.0, detailed parsing in v0.6.0

### Risk 2: Collection Structure Variability (MEDIUM)
**Description**: Collections may not follow standard structure strictly

**Impact**: Parser fails on non-standard collections

**Mitigation**:
- Defensive directory discovery (gracefully handle missing dirs)
- Log warnings for non-standard structure, continue parsing
- Validate against ansible-galaxy collection spec
- Test with real-world collections (community.general, ansible.posix)

### Risk 3: Dependency Resolution Complexity (MEDIUM)
**Description**: Resolving collection dependencies recursively is complex

**Impact**: Dependency graph may be incomplete or incorrect

**Mitigation**:
- v0.5.0: Parse dependencies from galaxy.yml, no recursive resolution
- v0.6.0: Implement full dependency resolution
- Use packaging.specifiers for version constraint parsing
- Detect circular dependencies with graph traversal (simple DFS)

### Risk 4: Template Reusability (LOW)
**Description**: Collection template may conflict with role template

**Impact**: Duplicated template logic, inconsistent output

**Mitigation**:
- Reuse TemplateEngine from Feature 002 (proven stable)
- Collection template includes role sections via template composition
- Test template rendering in isolation before integration

---

## Dependencies & Prerequisites

### Internal Dependencies (ansible-doctor-enhanced)
- ✅ Feature 001: Role Parser (models, parsers) - COMPLETE
- ✅ Feature 002: Template Engine (renderer, formats) - COMPLETE
- ✅ Feature 003: Config system, CLI framework - COMPLETE

### External Dependencies (New)
- `packaging` (already in deps): For semantic version parsing and comparison
- `ast` (stdlib): For Python module AST parsing (plugin DOCUMENTATION extraction)

**No new external dependencies required** - leverage existing Poetry dependencies.

---

## Acceptance Criteria (Definition of Done)

**For v0.5.0 release, ALL criteria MUST be met**:

- [ ] **SC-001**: Parse galaxy.yml and extract all metadata fields
- [ ] **SC-002**: Discover all roles within collection automatically
- [ ] **SC-003**: Generate collection-level README with role index and plugin list
- [ ] **SC-004**: Document collection dependencies with version constraints
- [ ] **SC-007**: Reuse template system from v0.3.0 (TemplateEngine)
- [ ] **SC-008**: CLI commands: `collection generate`, `collection parse`, `collection analyze`
- [ ] **SC-006**: Performance: Parse typical collection (5 roles, 10 plugins) in <5s
- [ ] **Testing**: 130+ tests (100 unit, 20 integration, 10 property, 5 e2e)
- [ ] **Coverage**: 80%+ overall, 90%+ for core parsing logic
- [ ] **Documentation**: COLLECTION_GUIDE.md created, README updated, CHANGELOG updated
- [ ] **Demo**: Demo collection created with generated documentation
- [ ] **Cross-platform**: Tests pass on Windows, Linux, macOS
- [ ] **Constitution Compliance**: 
  - [ ] TDD followed (all tasks have RED-GREEN-REFACTOR)
  - [ ] DDD principles applied (Ubiquitous Language, Bounded Contexts)
  - [ ] CLI interface for all features (collection subcommands)
  - [ ] Structured logging added
  - [ ] CHANGELOG.md updated following Keep a Changelog
  - [ ] Version bumped to 0.5.0 in pyproject.toml

---

## Deferred to v0.6.0 (Out of Scope for v0.5.0)

To keep v0.5.0 focused and achievable in 2-3 weeks:

**Deferred Features**:
- [ ] **Optional galaxy.yml Fields**: tags, license, repository, description, homepage, issues, documentation (required fields only in v0.5.0)
- [ ] **US10**: Cross-role dependency analysis (Priority P2) - Basic analysis only in v0.5.0
- [ ] **Plugin Source Parsing**: Detailed DOCUMENTATION/EXAMPLES extraction (list plugins only)
- [ ] **Recursive Dependency Resolution**: Parse dependencies of dependencies
- [ ] **Per-Plugin Documentation Pages**: Individual docs per plugin (only index in v0.5.0)
- [ ] **Watch Mode for Collections**: Auto-regenerate on collection changes
- [ ] **Collection Validation**: Lint collection structure against best practices
- [ ] **Plugin Types**: Test, inventory, callback plugins (modules/filters only in v0.5.0)
- [ ] **Galaxy Schema Versions**: Support for newer schema versions beyond 1.0.0

These features add significant complexity and can be incrementally added in v0.6.0 without breaking v0.5.0 functionality.

---

## Timeline & Milestones

**Week 1** (Nov 20-26, 2025): Phase 1 - Galaxy Metadata Parsing
- **Milestone M1** (Day 3): GalaxyMetadata model complete + tests
- **Milestone M2** (Day 5): GalaxyMetadataParser working with real galaxy.yml files
- **Milestone M3** (Day 7): Collection structure discovery complete

**Week 2** (Nov 27 - Dec 3, 2025): Phase 2 - Plugin & Role Integration
- **Milestone M4** (Day 10): Plugin discovery and catalog complete
- **Milestone M5** (Day 12): CollectionRole parser integrated with existing Role parser
- **Milestone M6** (Day 14): Integration tests passing with real collections

**Week 3** (Dec 4-10, 2025): Phase 3 - Documentation Generation
- **Milestone M7** (Day 17): Collection template and generator complete
- **Milestone M8** (Day 19): CLI commands implemented and tested
- **Milestone M9** (Day 20): Demo collection created with generated docs
- **Milestone M10** (Day 21): All acceptance criteria met, v0.5.0 ready

**Release Date**: December 10, 2025 (Target)

---

## Success Metrics

**Code Quality**:
- Test coverage: 80%+ (target: 85%)
- All 130+ tests passing
- 0 critical bugs
- 0 mypy type errors with --strict

**Performance**:
- Collection parsing (5 roles, 10 plugins): <5s
- Demo collection generation: <3s
- Memory usage: <200MB for typical collection

**Documentation**:
- COLLECTION_GUIDE.md: 3000+ words
- README.md updated with collection examples
- CHANGELOG.md with v0.5.0 entry
- 5+ code examples in documentation

**User Value**:
- First comprehensive Ansible collection documentation tool
- Competitive advantage over ansible-doctor (no collection support)
- Enables organizations to document their private collections
- Foundation for v0.6.0 (Project Documentation)

---

## Next Steps

**Immediate actions to start Phase 1**:

1. **Review and approve this plan** with stakeholders
2. **Create tasks.md** with detailed TDD task breakdown (T001-T115+)
3. **Set up test fixtures** in `tests/fixtures/collections/`
4. **Begin T001**: Write first failing test for GalaxyMetadata model (TDD RED)
5. **Update Constitution** if any new principles discovered during implementation

**Before starting implementation**:
- [ ] Plan reviewed and approved
- [ ] tasks.md created with full task breakdown
- [ ] Branch `004-collection-support` confirmed clean and up-to-date
- [ ] Development environment verified (Python 3.11+, Poetry, all deps installed)
- [ ] v0.4.0 confirmed stable (all tests passing on dev branch)

---

**Plan Status**: ✅ READY FOR IMPLEMENTATION

*Plan created following Constitution Article III (TDD), Article VI (SemVer), Article VII (KISS), Article X (DDD)*
