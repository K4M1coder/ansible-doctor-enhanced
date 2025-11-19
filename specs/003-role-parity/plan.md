# Implementation Plan: ansible-doctor Parity - Config & Watch Mode

**Branch**: `003-role-parity` | **Date**: 2025-11-19 | **Spec**: [spec.md](spec.md)  
**Milestone**: v0.4.0  
**Prerequisites**: v0.3.0 (Documentation Generator) COMPLETE

## Summary

Implement configuration file support (`.ansibledoctor.yml`) and watch mode to achieve 100% feature parity with original ansible-doctor for role documentation. Config files enable storing documentation settings persistently, eliminating repetitive CLI flags. Watch mode provides real-time documentation regeneration during development, improving developer experience.

**Technical Approach**:
- Configuration: Pydantic models for schema validation, hierarchical discovery (current → parent dirs)
- Watch Mode: `watchdog` library for cross-platform file monitoring with debouncing
- CLI: New `config` and `watch` command groups extending Click CLI
- Backward compatibility with original ansible-doctor config format

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+  
**Primary Dependencies**: 
- `pydantic` (2.x) - Configuration schema validation
- `watchdog` (6.x) - Cross-platform file system monitoring
- `click` (8.x) - CLI framework (existing)
- `ruamel.yaml` (existing) - YAML parsing with comments

**Storage**: Filesystem only (config files, role files, generated docs)  
**Testing**: pytest with 80%+ coverage target (constitutional requirement)  
**Target Platform**: Windows, macOS, Linux (cross-platform via watchdog)  
**Project Type**: CLI tool (single project structure)  
**Performance Goals**: 
- Config file loading: <50ms
- Watch mode latency: <2s from file save to regeneration complete
- Debounce period: 500ms (configurable)

**Constraints**: 
- Backward compatible with original ansible-doctor `.ansibledoctor.yml` format
- No breaking changes to v0.3.0 CLI interface
- Must work offline (no external services)

**Scale/Scope**: 
- Config files: up to 100 keys (current: ~7 keys)
- Watch mode: monitor up to 1000 files per role
- Debouncing: handle burst of 100+ file events

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
ansibledoctor/
├── models/              # Existing domain models
├── parser/              # Existing parsers
├── generator/           # Existing doc generator
├── config/              # NEW: Configuration management
│   ├── __init__.py
│   ├── loader.py        # Config file discovery & loading
│   ├── models.py        # Config schema (Pydantic)
│   └── validator.py     # Config validation
├── watcher/             # NEW: Watch mode functionality
│   ├── __init__.py
│   ├── monitor.py       # File system monitoring (watchdog)
│   ├── debouncer.py     # Event debouncing
│   └── handler.py       # Regeneration handler
├── cli/                 # Extend existing CLI
│   └── __init__.py      # Add 'config' and 'watch' commands
└── utils/               # Existing utilities

tests/
├── unit/
│   ├── test_config_loader.py        # NEW
│   ├── test_config_models.py        # NEW
│   ├── test_watcher.py               # NEW
│   └── test_cli_config_watch.py     # NEW
├── integration/
│   ├── test_config_integration.py   # NEW
│   └── test_watch_integration.py    # NEW
└── fixtures/
    └── config_files/                 # NEW: Sample config files
```

**Structure Decision**: Extending existing single-project CLI structure with two new modules (`config/`, `watcher/`). Follows established patterns from `parser/` and `generator/` modules.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
