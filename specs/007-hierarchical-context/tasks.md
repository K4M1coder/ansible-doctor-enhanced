---
description: "Task breakdown for Feature 007: Hierarchical Context Detection"
---

# Tasks: Hierarchical Context Detection

## Phase 1: Setup
- [x] T308 Add `context_slug` usage guidelines to `ansibledoctor/utils/slug.py` and design tests in `tests/unit/test_slug.py` to ensure path joining preserves slugs across project->collection->role hierarchies
    - Added `build_context_path()` for hierarchical doc paths
    - Added `relative_link()` for cross-component linking
    - 22 tests passing for slug utilities

## Phase 2: Detection & Mapping
- [x] T309 [US-Context] Write unit tests for context detector in `tests/unit/test_context.py` (TDD)
    - 17 tests covering standalone, nested, and full hierarchy detection
    - Tests for breadcrumb generation, sibling discovery, caching
- [x] T310 Implement context mapping that yields hierarchical slugs for each node (project, collection, role) and breadcrumbs
    - Created `ansibledoctor/context/detector.py` with ContextDetector class
    - HierarchicalContext with parent chain and breadcrumb generation
    - ComponentType enum (PROJECT, COLLECTION, ROLE, STANDALONE)
    - Sibling discovery and session-scoped caching

## Phase 3: Templates & Links
- [ ] T311 Update templates to render breadcrumbs and navigation based on slug paths
- [ ] T312 Add integration tests verifying that docs for role inside collection inside project generate links: `docs/lang/{lang}/ansibleproject_proj/collections/collection_ns.collection/role_ns.role/` and that navigation back to project & collection levels works

## Phase 4: Polish
- [ ] T313 Update CHANGELOG and examples to reflect the new slug path layout

## Acceptance
- [ ] T314 E2E test: generate docs for a full project with nested collections and roles, and verify link navigation across all levels is correct
