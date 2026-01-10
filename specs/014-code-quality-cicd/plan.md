# Implementation Plan: Code Quality & CI/CD Infrastructure

**Branch**: `014-code-quality-cicd` | **Date**: 2026-01-10 | **Spec**: [specs/014-code-quality-cicd/spec.md](specs/014-code-quality-cicd/spec.md)
**Input**: Feature specification from `/specs/014-code-quality-cicd/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements a comprehensive code quality and CI/CD infrastructure for the `ansible-doctor-enhanced` project. It aims to enforce high standards through automated pre-commit hooks (formatting, linting, type checking) and rigorous CI pipelines on GitHub Actions. The solution includes a custom badge generation system for real-time visibility into project health (coverage, performance, test counts) and progressive performance testing to catch regressions.

## Technical Context

**Language/Version**: Python 3.11, 3.13  
**Primary Dependencies**: 
- **Quality**: `black` (24.4.0), `isort` (5.13.0), `ruff` (>=0.1.0), `mypy` (>=1.8.0), `pre-commit` (3.5.0)
- **Testing**: `pytest` (8.0.0), `pytest-cov`, `pytest-benchmark`
- **CI/CD**: GitHub Actions (Windows runners)
**Storage**: N/A (Project is a CLI tool)
**Testing**: `pytest` for unit/integration/perf, `coverage` for metrics.
**Target Platform**: Windows 11 (Dev), GitHub Actions (Windows/Ubuntu).
**Project Type**: Python CLI Tool
**Performance Goals**: 
- Small role rendering: target 60ms (max 80ms)
- Medium role rendering: target 100ms (max 130ms)
- Large role rendering: target 200ms (max 250ms)
**Constraints**: 
- CI must complete in <10 minutes
- Pre-commit checks must be fast (<30s)
- Badges must depend only on GHA artifacts (no external services)
**Scale/Scope**: ~3000 LOC, supporting Ansible roles/collections documentation.

## Constitution Check

*GATE: Passed.*

- **Code Quality**: Adheres to strict type checking and linting as per project constitution.
- **Efficiency**: CI optimization via Artifact retention and separation of concerns.
- **Local-First**: Pre-commit hooks ensure quality locally before pushing.

## Project Structure

### Documentation (this feature)

```text
specs/014-code-quality-cicd/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
├── quickstart.md        # Developer guide
├── checklists/          # Validation checklists
│   └── requirements.md
└── contracts/           # Technical schemas
    ├── hook-schema.md
    ├── workflow-schema.md
    └── badge-format.md
```

### Source Code (repository root)

```text
# Configuration Files
pyproject.toml                # Tool configuration (Black, Ruff, Mypy)
.pre-commit-config.yaml       # Pre-commit hook definitions
.github/
├── workflows/
│   ├── ci-windows.yml        # Main CI
│   ├── pre-commit.yml        # Hook validation
│   ├── badges.yml            # Badge generation
│   └── check-changelog-atomic.yml # Atomic updates
└── COMMIT_QUALITY.md         # Guide

# Scripts
scripts/
├── generate_badge_metrics.py # Badge generator
├── check_type_quality.py     # Custom type checker
└── ...

# Tests
tests/
├── performance/              # Performance tests
│   ├── conftest.py           # Pytest plugin for perf
│   └── test_perf.py
└── ...
```

**Structure Decision**: Standard Python project structure with tool configuration in root and CI workflows in `.github/workflows`. Custom scripts are centralized in `scripts/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Custom Badge Script | No external service (Shields.io/Coveralls) integration desired | Reliance on external services introduces latency/privacy concerns; Gists are flaky. |
| Progressive Perf Tolerance | Avoid flaky CI on shared runners | Fixed thresholds cause false positives on busy runners. |
