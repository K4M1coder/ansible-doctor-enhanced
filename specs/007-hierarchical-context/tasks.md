---
description: "Task breakdown for Feature 007: Hierarchical Context Detection"
---

# Tasks: Hierarchical Context Detection

## Phase 1: Setup
- [ ] T308 Add `context_slug` usage guidelines to `ansibledoctor/utils/slug.py` and design tests in `tests/unit/test_slug.py` to ensure path joining preserves slugs across project->collection->role hierarchies

## Phase 2: Detection & Mapping
-- [ ] T309 [US-Context] Write unit tests for context detector in `tests/unit/test_context.py` (TDD)
-- [ ] T310 Implement context mapping that yields hierarchical slugs for each node (project, collection, role) and breadcrumbs

## Phase 3: Templates & Links
-- [ ] T311 Update templates to render breadcrumbs and navigation based on slug paths
-- [ ] T312 Add integration tests verifying that docs for role inside collection inside project generate links: `docs/lang/{lang}/ansibleproject_proj/collections/collection_ns.collection/role_ns.role/` and that navigation back to project & collection levels works

## Phase 4: Polish
-- [ ] T313 Update CHANGELOG and examples to reflect the new slug path layout

## Acceptance
-- [ ] T314 E2E test: generate docs for a full project with nested collections and roles, and verify link navigation across all levels is correct
