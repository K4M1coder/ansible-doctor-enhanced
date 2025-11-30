---
description: "Task breakdown for Feature 007: Project Navigation & Breadcrumbs"
---

# Tasks: Project Navigation & Breadcrumbs

## Phase 1: Setup
- [ ] T401 Define breadcrumb naming & path format (spec / tests)
- [ ] T402 Create Pydantic models/utility changes to expose parent relationships

## Phase 2: Rendering & Template Integration
- [ ] T403 Add Breadcrumb helper to Template Engine and Jinja2 helpers
- [ ] T404 Add default breadcrumb templates for Markdown/HTML/RST

## Phase 3: CLI & Tests
- [ ] T405 Add `--breadcrumb-style` CLI flag and tests for `generate` commands
- [ ] T406 Integration tests for generated breadcrumbs and navigation links

## Phase 4: Polish
- [ ] T407 Update README and CHANGELOG with navigation usage examples

---

## Side work: 2025-11-30 (Integration & merge)

- [x] T408 [P] Merged `005-i18n-support` into `007-project-navigation` to integrate i18n features with navigation templates and rewrote a subset of templates to support `t()` usage
- [x] T409 [P] Added helper scripts & `ansibledoctor` CLI alias; ensured `python -m ansibledoctor` runs CLI from source


---

<!-- Side work entries moved to the end of file and renumbered as T408 and T409. -->

