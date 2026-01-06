# Implementation Tasks: Indexes & Navigation

**Feature**: Spec 011 - Indexes & Navigation  
**Branch**: `011-indexes-navigation`  
**Generated**: 2025-12-03  
**Total Tasks**: 96 (reduced from 105 - US7 moved to Spec 013)  
**Estimated Effort**: 60 hours (~7.5 developer days)

**Cross-Spec Dependencies**:
- **Consumes Spec 013**: CrossReference model and LinkValidator from `ansibledoctor/links/` (US7 functionality)
- **Consumes Spec 012**: MermaidBuilder can use SchemaService for diagram validation
- **Integrates Spec 009**: Index generation metrics feed into ExecutionReport

---

## Phase 1: Setup (4 tasks, ~3 hours)

**Goal**: Initialize module structure, models, and test infrastructure.

- [X] T001 Create index models module at ansibledoctor/models/index.py with IndexItem, IndexPage, SectionIndex models
- [X] T002 [P] Create index generator module skeleton at ansibledoctor/generator/indexes.py with IndexGenerator protocol
- [X] T003 [P] Create test fixtures directory at tests/fixtures/project_structures/ with simple_project/, hierarchical_project/, large_project/ subdirectories

---

## Phase 2: Foundational Tasks (7 tasks, ~5 hours) ⚠️ BLOCKING

**Goal**: Core index infrastructure that all user stories depend on.

**Note**: These tasks MUST complete before any user story work begins.

- [X] T004 Write tests for IndexItem model in tests/unit/test_index_models.py (depth calculation, find_child, find_descendant)
- [X] T005 Implement IndexItem model in ansibledoctor/models/index.py with properties (depth, total_descendants, find_child, find_descendant)
- [X] T006 [P] Write tests for IndexPage model in tests/unit/test_index_models.py (pagination logic, filter tracking)
- [X] T007 [P] Implement IndexPage model in ansibledoctor/models/index.py with render() method
- [X] T008 [P] Write tests for SectionIndex model in tests/unit/test_index_models.py (inline rendering, limit behavior)
- [X] T009 [P] Implement SectionIndex model in ansibledoctor/models/index.py with render_inline() method
- [X] T010 Create test fixture projects in tests/fixtures/project_structures/ (simple: 1 collection/3 roles, hierarchical: 3 collections/15 roles, large: 500+ components)

---

## Phase 3: User Story 1 - Generate Role Index Page (15 tasks, ~12 hours, P1 MVP) 🎯

**Story Goal**: Generate dedicated role index pages with descriptions, tags, and links.

**Independent Test**: Run `ansible-doctor generate collection/ --include-index` → Creates `roles/index.md` with all roles listed.

### Tests First

- [X] T012 [P] [US1] Write test for basic role index generation in tests/integration/test_index_generation.py (5 roles → roles/index.md created)
- [X] T013 [P] [US1] Write test for role index with tags in tests/integration/test_index_generation.py (tags displayed correctly)
- [X] T014 [P] [US1] Write test for role index with dependencies in tests/integration/test_index_generation.py (dependency links rendered)
- [X] T015 [P] [US1] Write test for empty role collection in tests/integration/test_index_generation.py (empty message shown)
- [X] T016 [P] [US1] Write test for multiple index formats in tests/integration/test_index_generation.py (list, table, tree formats)

### Implementation

- [X] T017 [US1] Implement IndexGenerator.generate_index_page() in ansibledoctor/generator/indexes.py (basic page generation)
- [X] T018 [P] [US1] Create list format template at ansibledoctor/templates/index/list.j2 (role list with links)
- [X] T019 [P] [US1] Create table format template at ansibledoctor/templates/index/table.j2 (table with Name|Description|Tags|Dependencies columns)
- [X] T020 [US1] Implement component metadata extraction in IndexGenerator (extract name, description, tags from parsed roles)
- [X] T021 [US1] Implement dependency link generation in IndexGenerator (resolve dependency names to doc links)
- [X] T022 [US1] Add CLI flags to ansibledoctor/cli/__init__.py (--include-index, --index-style, --index-format)
- [X] T023 [US1] Integrate index generation into main generation flow in ansibledoctor/generator/engine.py (call after main docs)
- [X] T024 [US1] Implement empty collection handling in IndexGenerator (detect empty, show message)
- [X] T025 [US1] Write index files to output directory in IndexGenerator (docs/lang/{code}/roles/index.md)
- [X] T026 [US1] Add index generation logging in IndexGenerator (component counts, duration)

---

## Phase 4: User Story 2 - Hierarchical Project Index (14 tasks, ~11 hours, P1 MVP) 🎯

**Story Goal**: Generate tree-style indexes showing project → collections → roles hierarchy.

**Independent Test**: Run `ansible-doctor generate project/ --index-style tree` → Creates index with tree visualization.

### Tests First

- [X] T027 [P] [US2] Write test for project hierarchy in tests/integration/test_index_generation.py (2 collections, 3 roles each)
- [X] T028 [P] [US2] Write test for plugin indexing in tests/integration/test_index_generation.py (plugins shown under collection)
- [X] T029 [P] [US2] Write test for depth limiting in tests/integration/test_index_generation.py (--index-depth 2 limits tree)
- [X] T030 [P] [US2] Write test for playbook indexing in tests/integration/test_index_generation.py (playbooks section)
- [X] T031 [P] [US2] Write test for ASCII tree rendering in tests/unit/test_tree_visualizer.py (correct characters used)

### Implementation

- [X] T032 [US2] Create TreeVisualizer class in ansibledoctor/generator/tree_visualizer.py with render_tree() method
- [X] T033 [US2] Implement ASCII tree rendering in TreeVisualizer (├── └── │ characters)
- [X] T034 [P] [US2] Add Unicode tree support in TreeVisualizer (use_unicode flag for box-drawing characters)
- [X] T035 [US2] Implement IndexGenerator.build_hierarchy() in ansibledoctor/generator/indexes.py (convert flat list to tree)
- [X] T036 [US2] Create tree format template at ansibledoctor/templates/index/tree.j2 (use TreeVisualizer output)
- [X] T037 [US2] Implement plugin indexing in IndexGenerator (extract modules, filters, lookups, etc.)
- [X] T038 [US2] Implement playbook indexing in IndexGenerator (parse playbook descriptions)
- [X] T039 [US2] Add depth limiting logic in TreeVisualizer (max_depth parameter)
- [X] T040 [US2] Add --index-depth CLI flag in ansibledoctor/cli/__init__.py (default 5)

---

## Phase 5: User Story 3 - Embed Section Index (12 tasks, ~9 hours, P1 MVP) 🎯

**Story Goal**: Support embedded index sections in documentation via template markers.

**Independent Test**: Generate collection docs → README includes "## Roles" section with role list.

### Tests First

- [X] T041 [P] [US3] Write test for template marker parsing in tests/unit/test_index_generator.py ({{ index('roles') }} parsed)
- [X] T042 [P] [US3] Write test for embedded table format in tests/integration/test_embedded_indexes.py (format='table' works)
- [X] T043 [P] [US3] Write test for group_by in tests/integration/test_embedded_indexes.py (plugins grouped by type)
- [X] T044 [P] [US3] Write test for limit parameter in tests/integration/test_embedded_indexes.py (limit=5 shows 5 + more link)
- [X] T045 [P] [US3] Write test for filter parameter in tests/integration/test_embedded_indexes.py (filter='tag:database' works)

### Implementation

- [X] T046 [US3] Implement IndexGenerator.generate_section_index() in ansibledoctor/generator/indexes.py (section index generation)
- [X] T047 [US3] Register index() function as Jinja2 global in ansibledoctor/generator/engine.py (callable from templates)
- [X] T048 [US3] Implement template marker argument parsing in index() function (parse format, limit, filter, group_by)
- [X] T049 [US3] Implement limit logic in SectionIndex (show N items + "and X more..." link)
- [X] T050 [US3] Implement group_by logic in SectionIndex (group plugins by type)
- [X] T051 [US3] Add filter parameter support in index() function (parse filter string, apply criteria)
- [X] T052 [US3] Create example templates using markers in demo/ (collection README with {{ index('roles') }})

---

## Phase 6: User Story 4 - Nested Tables (10 tasks, ~8 hours, P2)

**Story Goal**: Generate nested table format showing collections with inline children.

**Independent Test**: Generate project index with `--index-style nested-table` → Table shows collections with role/plugin summaries.

### Tests First

- [ ] T053 [P] [US4] Write test for nested table in tests/integration/test_index_generation.py (collections with child counts)
- [ ] T054 [P] [US4] Write test for nested depth in tests/unit/test_index_generator.py (--nested-depth 2 limits)
- [ ] T055 [P] [US4] Write test for HTML nested table in tests/integration/test_index_generation.py (expandable rows)
- [ ] T056 [P] [US4] Write test for Markdown nested table in tests/integration/test_index_generation.py (inline children)

### Implementation

- [ ] T057 [US4] Create nested_table.j2 template at ansibledoctor/templates/index/nested_table.j2 (collection|roles|plugins columns)
- [ ] T058 [US4] Implement nested table logic in IndexGenerator (calculate child summaries)
- [ ] T059 [US4] Add nested-depth parameter to IndexPage model (limit nesting levels)
- [ ] T060 [P] [US4] Implement HTML expandable rows in nested_table.j2 (JavaScript for expand/collapse)
- [ ] T061 [P] [US4] Implement Markdown static nested table in nested_table.j2 (comma-separated children)
- [ ] T062 [US4] Add --nested-depth CLI flag in ansibledoctor/cli/__init__.py (default 2)

---

## Phase 7: User Story 5 - Mermaid Diagrams (11 tasks, ~9 hours, P2)

**Story Goal**: Generate Mermaid diagrams showing project structure visually.

**Independent Test**: Generate project docs with `--index-style diagram` → Mermaid graph with clickable nodes.

### Tests First

- [ ] T063 [P] [US5] Write test for Mermaid flowchart in tests/unit/test_mermaid_builder.py (correct syntax generated)
- [ ] T064 [P] [US5] Write test for dependency arrows in tests/unit/test_mermaid_builder.py (dependencies shown)
- [ ] T065 [P] [US5] Write test for mindmap diagram in tests/unit/test_mermaid_builder.py (mindmap syntax)
- [ ] T066 [P] [US5] Write test for clickable nodes in tests/unit/test_mermaid_builder.py (click links included)
- [ ] T067 [P] [US5] Write test for large project clustering in tests/integration/test_index_generation.py (100+ components clustered)

### Implementation

- [ ] T068 [US5] Create MermaidBuilder class in ansibledoctor/utils/mermaid_builder.py with build_flowchart() method
- [ ] T069 [US5] Implement Mermaid flowchart generation in MermaidBuilder (graph TD syntax)
- [ ] T070 [US5] Implement dependency arrow rendering in MermaidBuilder (role1 -.depends.-> role2)
- [ ] T071 [P] [US5] Implement mindmap diagram in MermaidBuilder.build_mindmap() (mindmap syntax)
- [ ] T072 [US5] Add clickable node support in MermaidBuilder (click directive with doc links)
- [ ] T073 [US5] Create diagram.j2 template at ansibledoctor/templates/index/diagram.j2 (wrap Mermaid code)

---

## Phase 8: User Story 6 - Filter and Search (11 tasks, ~9 hours, P2)

**Story Goal**: Support filtering indexes by tag, namespace, type, and custom metadata.

**Independent Test**: Generate index with `--filter 'tag:web'` → Only matching components included.

### Tests First

- [ ] T074 [P] [US6] Write test for tag filtering in tests/unit/test_index_filters.py (tag:database filter)
- [ ] T075 [P] [US6] Write test for namespace filtering in tests/unit/test_index_filters.py (namespace:my_namespace filter)
- [ ] T076 [P] [US6] Write test for multiple filters in tests/unit/test_index_filters.py (AND logic)
- [ ] T077 [P] [US6] Write test for empty filter results in tests/integration/test_index_generation.py (no matches message)
- [ ] T078 [P] [US6] Write test for HTML client-side filtering in tests/integration/test_index_generation.py (filter box rendered)

### Implementation

- [ ] T079 [US6] Create IndexFilter model in ansibledoctor/models/index.py (field, operator, value, matches())
- [ ] T080 [US6] Implement filter parsing in CLI in ansibledoctor/cli/__init__.py (parse 'field:value' strings)
- [ ] T081 [US6] Implement filter application in IndexGenerator (apply filters before rendering)
- [ ] T082 [US6] Add --filter CLI flag in ansibledoctor/cli/__init__.py (multiple=True)
- [ ] T083 [US6] Implement empty filter message in templates (show when filtered_count=0)

---

## Phase 9: Polish & Cross-Cutting Concerns (10 tasks, ~8 hours)

**Goal**: Documentation, optimization, integration testing, and release preparation.

**Note**: Cross-reference functionality (US7) has been moved to Spec 013 (Links & Cross-References).
Spec 011 should consume CrossReference and LinkValidator from Spec 013's `ansibledoctor/links/` module.

- [ ] T084 [P] Update CHANGELOG.md with Spec 011 feature summary (index pages, embedded sections, multiple formats)
- [ ] T085 [P] Create user guide docs/INDEX_GUIDE.md (usage examples for all index styles)
- [ ] T086 [P] Update README.md with index feature showcase (examples of list, tree, nested-table, diagram)
- [ ] T087 [P] Add quickstart examples to docs/ (basic role index, hierarchical project, embedded sections)
- [ ] T088 Write comprehensive integration test in tests/integration/test_full_index_workflow.py (end-to-end with all features)
- [ ] T089 Performance test large project in tests/integration/test_index_performance.py (500+ components < 500ms)
- [ ] T090 [P] Add index generation metrics to execution reports (integrate with Spec 009 ExecutionReport)
- [ ] T091 Create demo projects in demo/ showing index features (collection with indexes, project with tree)
- [ ] T092 Update cli help text in ansibledoctor/cli/__init__.py (document all index flags with examples)
- [ ] T093 Final code review and cleanup (remove debug logging, optimize imports, fix style)

---

## Dependencies & Execution Strategy

### User Story Completion Order

```mermaid
graph TD
    Setup[Phase 1: Setup]
    Foundation[Phase 2: Foundation]
    US1[US1: Role Index Page]
    US2[US2: Hierarchical Index]
    US3[US3: Embedded Sections]
    US4[US4: Nested Tables]
    US5[US5: Mermaid Diagrams]
    US6[US6: Filtering]
    Spec013[Spec 013: Links & Cross-Refs]
    Polish[Phase 9: Polish]
    
    Setup --> Foundation
    Foundation --> US1
    Foundation --> US2
    Foundation --> US3
    US1 --> US4
    US1 --> US5
    US2 --> US4
    US2 --> US5
    US3 --> US6
    US4 --> Polish
    US5 --> Polish
    US6 --> Polish
    Spec013 -.provides.-> US1
    Spec013 -.provides.-> US2
```

### Parallel Execution Opportunities

**After Foundation Phase (T010 complete)**:

- **Group A** (Independent): T011-T015 (US1 tests), T026-T030 (US2 tests), T040-T044 (US3 tests)
- **Group B** (After US1 implementation): T017-T018 (templates), T052-T055 (US4 tests), T062-T066 (US5 tests)
- **Group C** (After US3 implementation): T073-T077 (US6 tests)
- **Group D** (Documentation): T084-T087 (docs updates can happen in parallel with late-stage implementation)

**Note**: Cross-reference functionality is provided by Spec 013 - integrate via `from ansibledoctor.links import CrossReference, LinkValidator`

### MVP Scope (US1 + US2 + US3)

**Tasks**: T001-T051 (51 tasks)  
**Effort**: ~32 hours (~4 developer days)  
**Deliverable**: Basic index generation with role indexes, hierarchical views, and embedded sections

**Why these stories**: Role indexes (US1) enable discovery, hierarchical views (US2) show structure, embedded sections (US3) improve UX. These three provide complete core indexing functionality. US4-US6 add advanced features. Cross-referencing (former US7) is now provided by Spec 013.

---

## Implementation Strategy

### TDD Workflow

1. **Test First**: Write tests for models/generators before implementation (T005-T010 for foundation, T012-T016 for US1, etc.)
2. **Implement**: Build features to pass tests
3. **Integrate**: Wire into CLI and generation engine
4. **Validate**: Run integration tests

### Incremental Delivery

1. **Sprint 1** (Setup + Foundation): T001-T010 (~8 hours) - Models, fixtures, basic infrastructure
2. **Sprint 2** (US1 MVP): T011-T025 (~12 hours) - Role index pages working
3. **Sprint 3** (US2 + US3 MVP): T026-T051 (~20 hours) - Hierarchical and embedded indexes
4. **Sprint 4** (US4 + US5): T052-T072 (~17 hours) - Advanced visualizations
5. **Sprint 5** (US6): T073-T083 (~9 hours) - Filtering
6. **Sprint 6** (Polish): T084-T093 (~8 hours) - Documentation and optimization

**Note**: Cross-references now provided by Spec 013 (implement after or in parallel)

### Testing Strategy

- **Unit Tests**: Models (IndexItem, IndexPage), TreeVisualizer, MermaidBuilder, IndexFilter
- **Integration Tests**: Full index generation workflows, template marker integration, CLI flag combinations
- **Performance Tests**: 500+ component projects, pagination, large tree rendering
- **Fixture-Based**: Reusable test projects (simple/hierarchical/large) for consistent testing
- **Cross-Spec**: Integration with Spec 013 CrossReference/LinkValidator via imports

---

## Success Metrics

- ✅ All 12 functional requirements (FR-001 to FR-012) implemented and tested (FR-013 to FR-015 moved to Spec 013)
- ✅ All 6 user stories deliver expected behavior with acceptance criteria met
- ✅ Index generation <200ms per 100 components (SC-001)
- ✅ Tree visualizations support 5+ hierarchy levels (SC-004)
- ✅ Cross-reference links provided by Spec 013 integration (SC-005)
- ✅ Mermaid diagrams render in GitHub/GitLab (SC-006)
- ✅ HTML indexes support client-side filtering (SC-007)
- ✅ Test coverage >85% for new code
- ✅ All edge cases handled (circular dependencies, missing descriptions, 500+ components)
- ✅ Constitution compliance verified (TDD, Library-First, CLI Mandate, Observability, Backward Compatibility)

---

## Backward Compatibility Regression Tasks

These tasks ensure existing functionality is not broken:

- [ ] T094 [REGRESSION] Run existing Spec 001-008 test suites to verify no regressions
- [ ] T095 [REGRESSION] Verify existing generated documentation structure unchanged
- [ ] T096 [REGRESSION] Test that document generation works without --include-index flag

---

## Notes

- **anytree library**: Add to dependencies for tree data structures (Phase 2, T032)
- **ASCII vs Unicode**: Default to ASCII (├── └── │), --use-unicode flag enables Unicode box-drawing
- **Pagination**: Default 50 items/page, configurable via --page-size flag
- **Circular Dependencies**: Detect during build_hierarchy(), log warning, prevent infinite recursion
- **Empty Descriptions**: Show "[No description]" placeholder, log warning for missing metadata
- **Language Support**: Generate language-specific indexes, link to same-language docs
- **Performance**: Target <200ms/100 components for index generation, <500ms for 500+ component projects
- **Mermaid Compatibility**: Test with GitHub/GitLab Markdown renderers, use standard Mermaid syntax
- **Template Marker Validation**: Validate syntax, show helpful error messages with line numbers
- **Link Validation**: Provided by Spec 013 - use `from ansibledoctor.links import LinkValidator` when integrating
