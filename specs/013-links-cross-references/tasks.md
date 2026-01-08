# Tasks: Links & Cross-References

**Input**: Design documents from `/specs/013-links-cross-references/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are MANDATORY per Constitution §III (TDD). All tests must be written BEFORE implementation (Red-Green-Refactor).

**Cross-Spec Dependencies**:
- **Extends Spec 002**: Add link generation to existing `ansibledoctor/generator/` document generation
- **Extends Spec 011**: Enhance index pages with smart cross-referencing (provides CrossReference model)
- **Owns**: CrossReference model, LinkValidator, LinkManager - single source of truth for linking
- **Library Versions**: requests>=2.28, beautifulsoup4>=4.11

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Phase 1: Setup (5 tasks, ~3 hours)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create links module at ansibledoctor/links/__init__.py
- [ ] T002 [P] Create link models at ansibledoctor/models/link.py with Link, LinkType, LinkStatus enums
- [ ] T003 [P] Create link parser utilities at ansibledoctor/utils/link_parser.py for extracting links from Markdown/HTML/RST
- [ ] T004 [P] Create test fixtures directory at tests/fixtures/docs_with_links/ with valid_links.md, broken_links.md, circular_refs.md
- [ ] T005 [P] Install dependencies (add requests, beautifulsoup4 to pyproject.toml)

---

## Phase 2: Foundational (8 tasks, ~6 hours) ⚠️ BLOCKING

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Write tests for Link model in tests/unit/test_link_models.py (is_valid, is_external, is_internal properties)
- [ ] T007 Implement Link model in ansibledoctor/models/link.py with source_file, target, link_type, status, from_markdown(), from_html() methods
- [ ] T008 [P] Write tests for LinkType and LinkStatus enums in tests/unit/test_link_models.py (enum validation)
- [ ] T009 [P] Implement LinkType and LinkStatus enums in ansibledoctor/models/link.py
- [ ] T010 [P] Write tests for link parsing in tests/unit/test_link_parser.py (Markdown, HTML, RST link extraction)
- [ ] T011 [P] Implement link parser in ansibledoctor/utils/link_parser.py (parse links from Markdown using regex, HTML using BeautifulSoup)
- [ ] T012 Create anchor extractor at ansibledoctor/utils/anchor_extractor.py (extract section anchors from files)
- [ ] T013 Create test fixtures with sample docs in tests/fixtures/docs_with_links/ (various link types and scenarios)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Navigate Between Related Documentation (16 tasks, ~13 hours, Priority: P1) 🎯 MVP

**Goal**: Enable seamless navigation between related roles, collections, and projects

**Independent Test**: Generate docs for related roles → Click "Related Roles" link navigates to correct documentation

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US1] Write test for dependency links in tests/integration/test_link_generation.py (role with dependencies shows clickable "Depends On" section)
- [X] T015 [P] [US1] Write test for parent collection links in tests/integration/test_link_generation.py ("Parent Collection" link navigates correctly)
- [X] T016 [P] [US1] Write test for project context links in tests/integration/test_link_generation.py ("Project Context" link shows role's place)
- [X] T017 [P] [US1] Write test for related roles in tests/integration/test_link_generation.py ("See Also" section links to related roles)
- [X] T018 [P] [US1] Write test for browser navigation in tests/integration/test_link_generation.py (back/forward works correctly)

### Implementation for User Story 1

- [X] T019 [US1] Create CrossReferenceGenerator class in ansibledoctor/links/cross_reference_generator.py with generate_references() method ✅ (303 lines, 74% coverage)
- [X] T020 [US1] Implement dependency link generation in CrossReferenceGenerator (extract role dependencies, create links) ✅ Unit tests pass
- [X] T021 [US1] Implement parent collection link generation in CrossReferenceGenerator (link roles to their collections) ✅ Unit tests pass
- [X] T022 [US1] Implement project context link generation in CrossReferenceGenerator (show role's place in hierarchy) ✅ Unit tests pass
- [X] T023 [US1] Implement "See Also" generation in CrossReferenceGenerator (find related roles by tags/functionality) ✅ Unit tests pass
- [X] T024 [US1] Create LinkManager class in ansibledoctor/links/link_manager.py with create_link(), resolve_link() methods ✅ (166 lines, 92% coverage)
- [X] T025 [US1] Implement link resolution in LinkManager (resolve relative paths to absolute, handle anchors) ✅ Core logic complete, unit tests pass
- [X] T026 [US1] Integrate link generation into document generation in ansibledoctor/generator/__init__.py (call CrossReferenceGenerator) ✅ Integrated in CLI
- [X] T027 [US1] Add cross-reference sections to templates (update role/collection templates with "Depends On", "See Also" sections) ✅ Added to markdown/role.j2
- [X] T028 [US1] Implement bidirectional relationships in ansibledoctor/models/cross_reference.py (extend Spec 011 CrossReference model) ✅ Complete (218 lines)
- [X] T029 [US1] Add link formatting for different output formats in LinkManager (Markdown: [text](url), HTML: <a href="url">text</a>) ✅ Unit tests pass (Markdown, HTML, RST)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Detect Broken Links (15 tasks, ~12 hours, Priority: P1) 🎯 MVP

**Goal**: Detect and report broken links in generated documentation

**Independent Test**: Generate docs with broken internal link → `ansible-doctor linkcheck` reports the broken link with location

### Tests for User Story 2 ⚠️

- [X] T030 [P] [US2] Write test for broken internal link detection in tests/integration/test_link_validation_e2e.py (error with file and line number) ✅ 8 tests passing
- [X] T031 [P] [US2] Write test for missing role documentation in tests/integration/test_link_validation_e2e.py (warning shows "Target role not found") ✅ 8 tests passing
- [X] T032 [P] [US2] Write test for invalid section anchor in tests/integration/test_link_validation_e2e.py (error shows "Anchor not found") ✅ 8 tests passing
- [X] T033 [P] [US2] Write test for external 404 link in tests/integration/test_external_links.py (warning reports dead link with HTTP status) ✅ 8 tests passing
- [X] T034 [P] [US2] Write test for valid links in tests/integration/test_link_validation_e2e.py (success message) ✅ 8 tests passing

### Implementation for User Story 2

- [X] T035 [US2] Create LinkValidator class in ansibledoctor/links/link_validator.py with validate() method ✅ Complete (379 lines, 64% coverage)
- [X] T036 [US2] Implement internal file link validation in LinkValidator (check file existence) ✅ Working with tests
- [X] T037 [US2] Implement anchor validation in LinkValidator (parse target file, extract anchors, verify existence) ✅ Working with tests
- [X] T038 [US2] Implement external link validation in LinkValidator (HTTP HEAD requests with timeout/retry) ✅ Working with tests
- [X] T039 [US2] Add validation result formatting in LinkValidator (convert to ValidationError models from Spec 012) ✅ ValidationResult class complete
- [X] T040 [US2] Create CLI command structure at ansibledoctor/cli/linkcheck.py with linkcheck, linkfix, linkreport commands ✅ Structure complete (185 lines)
- [X] T041 [US2] Add `ansible-doctor linkcheck` CLI command in ansibledoctor/cli/linkcheck.py (validate all links in documentation) ✅ Complete with text/json/summary formats
- [X] T042 [US2] Implement link validation report generation in LinkValidator (group errors by file, severity) ✅ Complete with markdown/html/text/json formats, grouping options
- [X] T043 [US2] Add link validation caching in LinkValidator (cache external link results to avoid re-checking) ✅ Persistent cache with TTL, load/save/clear methods
- [X] T044 [US2] Integrate link validation into generation workflow in ansibledoctor/generator/__init__.py (optional --validate-links flag) ✅ Complete with --validate-links flag and inline validation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Navigate Within Documents (12 tasks, ~9 hours, Priority: P2)

**Goal**: Enable quick navigation to specific sections within long documents

**Independent Test**: Generate role docs with multiple sections → Table of contents links jump to correct sections

### Tests for User Story 3 ⚠️

- [X] T045 [P] [US3] Write test for table of contents generation in tests/unit/test_navigation_builder.py (TOC with section links) ✅ Complete with 16 tests
- [ ] T046 [P] [US3] Write test for section link jumping in tests/integration/test_link_generation.py (links jump to correct headings)
- [ ] T047 [P] [US3] Write test for URL anchor updates in tests/integration/test_link_generation.py (URL updates with anchor)
- [ ] T048 [P] [US3] Write test for nested subsections in tests/unit/test_navigation_builder.py (nested TOC structure)
- [ ] T049 [P] [US3] Write test for mobile navigation in tests/integration/test_link_generation.py (works on small screens)

### Implementation for User Story 3

- [ ] T050 [US3] Create NavigationBuilder class in ansibledoctor/links/navigation_builder.py with build_toc() method
- [ ] T051 [US3] Implement table of contents generation in NavigationBuilder (parse headings, generate anchor links)
- [ ] T052 [US3] Implement anchor slug generation in NavigationBuilder (convert heading text to URL-safe anchors)
- [ ] T053 [US3] Add TOC insertion to templates (inject TOC after title in long documents)
- [ ] T054 [US3] Implement nested section handling in NavigationBuilder (hierarchical TOC for h2, h3, h4)
- [ ] T055 [US3] Add smooth scrolling support in HTML output (CSS/JavaScript for smooth scroll to anchor)
- [ ] T056 [US3] Add mobile-responsive navigation in HTML templates (collapsible TOC for small screens)

---

## Phase 6: User Story 4 - Access External Resources (13 tasks, ~10 hours, Priority: P2)

**Goal**: Link to official Ansible documentation and related guides

**Independent Test**: Generate docs with external references → Links point to correct official documentation

### Tests for User Story 4 ⚠️

- [ ] T057 [P] [US4] Write test for module documentation links in tests/integration/test_external_links.py (module names link to Ansible docs)
- [ ] T058 [P] [US4] Write test for Galaxy page links in tests/integration/test_external_links.py (collection links to Galaxy)
- [ ] T059 [P] [US4] Write test for best practices links in tests/integration/test_external_links.py (links to official guides)
- [ ] T060 [P] [US4] Write test for new tab behavior in tests/integration/test_link_generation.py (external links open in new tabs)
- [ ] T061 [P] [US4] Write test for version-specific links in tests/integration/test_external_links.py (links target correct Ansible version)

### Implementation for User Story 4

- [ ] T062 [US4] Create ExternalLinkIntegrator class in ansibledoctor/links/external_link_integrator.py with integrate_links() method
- [ ] T063 [US4] Implement Ansible module documentation linking in ExternalLinkIntegrator (detect module usage, generate docs.ansible.com links)
- [ ] T064 [US4] Implement Galaxy collection linking in ExternalLinkIntegrator (extract namespace.name, link to Galaxy)
- [ ] T065 [US4] Implement best practices guide linking in ExternalLinkIntegrator (detect keywords, link to relevant guides)
- [ ] T066 [US4] Add version-specific URL generation in ExternalLinkIntegrator (use Ansible version from config)
- [ ] T067 [US4] Configure external link targets in HTML templates (add target="_blank" rel="noopener noreferrer")
- [ ] T068 [US4] Create external resource configuration in .ansibledoctor.yml (configurable external link mappings)

---

## Phase 7: User Story 5 - Index-Based Navigation (11 tasks, ~9 hours, Priority: P3)

**Goal**: Provide comprehensive indexes with smart linking for large documentation sets

**Independent Test**: Generate large doc set → Index pages contain working links to all documented items

### Tests for User Story 5 ⚠️

- [ ] T069 [P] [US5] Write test for alphabetical index in tests/integration/test_link_generation.py (letter-based index with working links)
- [ ] T070 [P] [US5] Write test for category index in tests/integration/test_link_generation.py (category-based navigation)
- [ ] T071 [P] [US5] Write test for tag-based navigation in tests/integration/test_link_generation.py (tag links to all tagged content)
- [ ] T072 [P] [US5] Write test for bidirectional relationships in tests/unit/test_link_graph.py (relationship graph showing both directions)
- [ ] T073 [P] [US5] Write test for search index in tests/integration/test_link_generation.py (term search links to relevant sections)

### Implementation for User Story 5

- [ ] T074 [US5] Extend IndexGenerator from Spec 011 in ansibledoctor/generator/indexes.py (add enhanced linking)
- [ ] T075 [US5] Implement alphabetical index linking in IndexGenerator (generate letter-based index with links)
- [ ] T076 [US5] Implement category index linking in IndexGenerator (group by type, link to all items)
- [ ] T077 [US5] Create LinkGraph class in ansibledoctor/utils/link_graph.py (graph data structure for link relationships)
- [ ] T078 [US5] Implement bidirectional relationship tracking in LinkGraph (track both "links to" and "linked by")
- [ ] T079 [US5] Add tag-based navigation to index pages (link tags to all content with that tag)

---

## Phase 8: Polish & Cross-Cutting Concerns (11 tasks, ~7 hours)

**Purpose**: Improvements that affect multiple user stories

- [ ] T080 [P] Update CHANGELOG.md with Spec 013 feature summary (link management, validation, cross-references)
- [ ] T081 [P] Create user guide docs/LINKS_GUIDE.md (usage examples for link validation, cross-references)
- [ ] T082 [P] Update README.md with link feature showcase (broken link detection, navigation)
- [ ] T083 [P] Add quickstart examples to docs/ (linkcheck usage, cross-reference generation)
- [ ] T084 Create LinkHealthMonitor class in ansibledoctor/links/link_health_monitor.py (periodic link health monitoring)
- [ ] T085 Write tests for link health monitoring in tests/unit/test_link_health_monitor.py (report generation, scheduling)
- [ ] T086 Add `ansible-doctor linkreport` CLI command in ansibledoctor/cli/linkcheck.py (generate link health report)
- [ ] T087 [P] Add `ansible-doctor linkfix` CLI command in ansibledoctor/cli/linkcheck.py (attempt to fix broken links with suggestions)
- [ ] T088 Write comprehensive integration test in tests/integration/test_link_validation_e2e.py (end-to-end with all features)
- [ ] T089 Performance test large doc sets in tests/integration/test_link_performance.py (5000+ files < 30s validation)
- [ ] T090 Run quickstart.md validation (ensure all examples work correctly)

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
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May use US1 link generation but testable independently
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but testable independently
- **User Story 5 (P3)**: Depends on US1 (cross-references) and extends Spec 011 (indexes) - Should complete after US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before validators/generators
- Core link logic before CLI integration
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
Task: "Write test for dependency links in tests/integration/test_link_generation.py"
Task: "Write test for parent collection links in tests/integration/test_link_generation.py"
Task: "Write test for project context links in tests/integration/test_link_generation.py"
Task: "Write test for related roles in tests/integration/test_link_generation.py"
Task: "Write test for browser navigation in tests/integration/test_link_generation.py"
```

---

## Implementation Strategy

TDD GREEN RED REFACTOR CYCLE MANDATORY PER CONSTITUTION §III
DDD PATTERN MANDATORY PER CONSTITUTION §IV
DRY PRINCIPLE MANDATORY PER CONSTITUTION §IV
SOLID PRINCIPLES MANDATORY PER CONSTITUTION §IV
KISS PRINCIPLE MANDATORY PER CONSTITUTION §IV
SMART GOALS MANDATORY PER CONSTITUTION §V

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (cross-references between docs)
4. Complete Phase 4: User Story 2 (broken link detection)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready

**MVP Deliverable**: Cross-reference navigation between related documentation + broken link detection and reporting

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (navigation works!)
3. Add User Story 2 → Test independently → Deploy/Demo (link validation enabled!)
4. Add User Story 3 → Test independently → Deploy/Demo (section navigation available)
5. Add User Story 4 → Test independently → Deploy/Demo (external resource integration)
6. Add User Story 5 → Test independently → Deploy/Demo (index-based navigation)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (cross-references)
   - Developer B: User Story 2 (broken link detection)
   - Developer C: User Story 3 (section navigation)
3. After US1+US2 complete:
   - Developer D: User Story 4 (external resources)
   - Developer E: User Story 5 (index navigation)
4. Stories complete and integrate independently

---

## Backward Compatibility Regression Tasks

These tasks ensure existing functionality is not broken:

- [ ] T091 [REGRESSION] Run existing Spec 001-008 test suites to verify no regressions
- [ ] T092 [REGRESSION] Verify existing generated documentation unchanged without link features
- [ ] T093 [REGRESSION] Test that document generation works without --validate-links flag

---

## Success Metrics

- ✅ 100% of internal links in generated documentation are valid (SC-001)
- ✅ Link validation completes in under 30 seconds (SC-002)
- ✅ Users can navigate to any related documentation within 3 clicks (SC-003)
- ✅ Broken link detection identifies 100% of invalid links (SC-004)
- ✅ External link integration covers all major Ansible resources (SC-005)
- ✅ Section navigation enables reach any content within 2 clicks (SC-006)
- ✅ Link health monitoring with <1% false positive rate (SC-007)
- ✅ Test coverage >85% for new code
- ✅ All 15 functional requirements (FR-001 to FR-015) implemented
- ✅ Constitution compliance verified (TDD, Library-First, CLI Mandate, Observability, Backward Compatibility)

---

## Notes

- **requests library**: Use for HTTP link validation with timeout/retry support (Phase 1, T005)
- **beautifulsoup4**: Use for HTML anchor parsing and extraction (Phase 1, T005)
- **Extends Spec 002**: Add link generation to existing document generation (Phase 3, T026)
- **Extends Spec 011**: Enhance index pages with smart cross-referencing (Phase 7, T074)
- **Link Types**: Support internal files, section anchors, external URLs, cross-references
- **Validation**: Internal file links checked during generation, external links optional (--validate-links flag)
- **Performance**: Target <30s validation for 1000+ docs, cache external link results
- **Cycle Detection**: Detect circular references in dependency graphs, prevent infinite recursion
- **Format Support**: Generate appropriate link syntax for Markdown, HTML, RST outputs
- **Caching**: Cache external link validation results to avoid repeated HTTP requests (Phase 4, T043)
