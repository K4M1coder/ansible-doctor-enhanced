# Feature Specification: Code Quality & CI/CD Infrastructure

**Feature Branch**: `014-code-quality-cicd`  
**Created**: 2026-01-10  
**Status**: Implemented & Active  
**Type**: Infrastructure & Quality Assurance
**Milestone**: v0.14.0

## Executive Summary

This specification documents the comprehensive code quality and CI/CD infrastructure to implement for ansible-doctor-enhanced. The system ensures code quality through automated checks, maintains non-regression through continuous testing, and provides visibility through metrics and badges.

## User Scenarios & Testing

### User Story 1 - Developer Commits Code with Quality Checks (Priority: P1)

As a developer, I want every commit to be automatically validated for code quality, so that I maintain high standards and catch issues early before they reach the codebase.

**Why this priority**: This is the foundation of code quality - preventing bad code from entering the repository is more efficient than fixing it later.

**Independent Test**: Developer commits code → Pre-commit hooks run → Code is formatted/validated → Commit succeeds only if all checks pass.

**Acceptance Scenarios**:

1. **Given** a developer has modified Python files, **When** they commit, **Then** Black automatically formats the code
2. **Given** a developer commits code with incorrect imports, **When** pre-commit runs, **Then** isort organizes imports correctly
3. **Given** code has linting issues, **When** pre-commit runs, **Then** Ruff auto-fixes common issues
4. **Given** code has type errors, **When** pre-commit runs, **Then** mypy reports type issues and blocks commit
5. **Given** README.md is modified, **When** committing, **Then** Table of Contents is auto-updated
6. **Given** version changes in pyproject.toml, **When** committing, **Then** version is synced to CHANGELOG and README, block commit if inconsistent with python source code

---

### User Story 2 - CI Pipeline Validates All Changes (Priority: P1)

As a maintainer, I want every push to trigger comprehensive CI checks on multiple Python versions, so that I can ensure compatibility and catch platform-specific issues.

**Why this priority**: Automated CI is essential for maintaining quality at scale and catching issues that local checks might miss.

**Independent Test**: Code is pushed → CI runs on Windows (Python 3.11, 3.13) → All tests pass → Coverage is measured → Artifacts are uploaded.

**Acceptance Scenarios**:

1. **Given** code is pushed to dev branch, **When** CI runs, **Then** tests execute on Python 3.11 and 3.13
2. **Given** tests complete, **When** CI finishes, **Then** coverage report is generated and uploaded
3. **Given** tests include performance benchmarks, **When** CI runs, **Then** performance metrics are captured (small: 60ms, medium: 100ms, large: 200ms targets)
4. **Given** CI detects failures, **When** reviewing results, **Then** detailed test output and error messages are available
5. **Given** all tests pass, **When** CI completes, **Then** test results artifact includes pytest XML and performance JSON

---

### User Story 3 - Badge System Provides Real-Time Metrics (Priority: P2)

As a project stakeholder, I want to see real-time code quality metrics displayed as badges in the README, so that I can quickly assess the project's health status.

**Why this priority**: Visibility drives accountability and helps maintainers prioritize quality improvements.

**Independent Test**: CI completes → Badge workflow runs → Metrics are parsed → Badges are generated → README displays updated badges.

**Acceptance Scenarios**:

1. **Given** CI completes successfully, **When** badge workflow runs, **Then** 16 badges are generated (version, license, Python, code style, coverage, tests, performance, CI status)
2. **Given** test results are available, **When** generating badges, **Then** test counts (passed/skipped/failed/warnings) are accurate
3. **Given** coverage data exists, **When** badge is generated, **Then** coverage percentage is displayed with color coding (red <80%, yellow 80-89%, green ≥90%)
4. **Given** performance tests run, **When** badge is generated, **Then** timings are displayed (S:56ms | M:57ms | L:58ms format)
5. **Given** mypy runs, **When** badge workflow completes, **Then** type checking errors count is displayed

---

### User Story 4 - Performance Regression Detection (Priority: P2)

As a developer, I want performance tests to detect regressions with progressive tolerance, so that I'm alerted to significant slowdowns without false positives from minor variance.

**Why this priority**: Performance is a key quality metric, but tests need tolerance to avoid flaky failures.

**Independent Test**: Performance tests run → Timings are compared against thresholds → Status (pass/warn/fail) is determined → Badge reflects current performance.

**Acceptance Scenarios**:

1. **Given** small role rendering test runs, **When** time ≤60ms, **Then** status is "pass" (green)
2. **Given** small role rendering test runs, **When** 60ms < time ≤80ms, **Then** status is "warn" (orange) with warning message
3. **Given** small role rendering test runs, **When** time >80ms, **Then** status is "fail" (red) and test fails
4. **Given** medium role test completes in 115ms, **When** results are recorded, **Then** warning is issued but test passes (target 100ms, max 130ms)
5. **Given** performance results are captured, **When** badge is generated, **Then** only failing/warning tests are highlighted in badge

---

### User Story 5 - Commit Quality Standards Enforcement (Priority: P1)

As a maintainer, I want documented standards for commit quality with pre-commit enforcement, so that all contributors follow the same quality practices.

**Why this priority**: Consistency in commit quality prevents technical debt and maintains codebase health.

**Independent Test**: Contributor attempts to bypass pre-commit with --no-verify → Documentation clearly states this is forbidden → CI catches formatting issues → Contributor is guided to fix properly.

**Acceptance Scenarios**:

1. **Given** a contributor uses --no-verify, **When** code reaches CI, **Then** CI detects formatting issues and fails
2. **Given** pre-commit hook fails, **When** developer investigates, **Then** clear documentation explains how to fix the root cause
3. **Given** new dependency is needed, **When** adding to .pre-commit-config.yaml, **Then** documentation guides proper configuration
4. **Given** commit standards document exists, **When** contributor reads it, **Then** examples show correct vs incorrect approaches
5. **Given** pre-commit fails with missing dependency, **When** error occurs, **Then** solution is documented in COMMIT_QUALITY.md

---

### Edge Cases

- **What happens when pre-commit hooks fail on Windows due to encoding issues?**
  - Scripts must force UTF-8 encoding (e.g., `sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)`)
  - Documented in update_readme_toc.py as reference implementation

- **How does system handle pre-commit environment isolation?**
  - Each hook declares its own `additional_dependencies` in .pre-commit-config.yaml
  - Dependencies must be complete and correct for hook to run in isolated environment
  - Example: pytest-performance hook requires requests and beautifulsoup4

- **What if CI takes too long and times out?**
  - Expensive checks (full test suite) run only on pre-push stage
  - Fast checks (formatting, linting) run on pre-commit stage
  - Demo runs are marked "non-fatal" to prevent blocking on flaky external dependencies

- **How to handle flaky performance tests?**
  - Progressive tolerance system: Target → Warning → Failure thresholds
  - Tests emit warnings instead of failing for acceptable variance
  - Badge shows only failures/warnings, not all tests

## Requirements

### Functional Requirements

#### Code Quality Tools

- **FR-001**: System MUST format all Python code with Black (version 24.4.0) automatically on commit
- **FR-002**: System MUST organize imports with isort (version 5.13.0) following configured style
- **FR-003**: System MUST lint Python code with Ruff with auto-fix enabled for common issues
- **FR-004**: System MUST type-check core ansibledoctor/ code with mypy in strict mode
- **FR-005**: System MUST validate YAML files syntax before commit (excluding test fixtures)
- **FR-006**: System MUST remove trailing whitespace from .py, .md, .toml, .yaml files
- **FR-007**: System MUST ensure all files end with a newline character

#### Pre-commit Hooks Structure

- **FR-008**: Hooks MUST be organized into 6 logical groups: Formatting, Code Style, Linting, Type Checking, Documentation, Testing
- **FR-009**: Fast checks (formatting, linting) MUST run on pre-commit stage
- **FR-010**: Expensive checks (full test suite) MUST run on pre-push stage
- **FR-011**: Each hook MUST declare complete dependencies in `additional_dependencies`
- **FR-012**: Hooks MUST NOT use --no-verify bypass (documented in COMMIT_QUALITY.md)

#### CI/CD Workflows

- **FR-013**: CI MUST run tests on Windows with Python 3.11 and 3.13
- **FR-014**: CI MUST generate coverage reports in JSON and term formats
- **FR-015**: CI MUST capture performance test results in tests/tmp/performance-results.json
- **FR-016**: CI MUST upload test results (pytest XML) and coverage as artifacts (7-day retention)
- **FR-017**: CI MUST run on push to dev branch and pull requests to dev

#### Badge System

- **FR-018**: System MUST generate 16 badges: version, license, Python version, Black, isort, Ruff, mypy, coverage, tests (passed/skipped/failed/warnings), performance, pre-commit status, CI status, badges status
- **FR-019**: Badge generation MUST parse pytest XML for test counts
- **FR-020**: Badge generation MUST parse performance-results.json for timing metrics
- **FR-021**: Badge generation MUST parse coverage.json for coverage percentage
- **FR-022**: Badge generation MUST parse mypy output for error counts
- **FR-023**: Badges MUST use color coding: red (<80%), yellow (80-89%), green (≥90%) for coverage
- **FR-024**: Performance badge MUST show status emoji (✓/⚠️/❌) and compact timings (S:56ms | M:57ms | L:58ms)

#### Performance Testing

- **FR-025**: System MUST test small role rendering with 60ms target, 80ms max (33% tolerance)
- **FR-026**: System MUST test medium role rendering with 100ms target, 130ms max (30% tolerance)
- **FR-027**: System MUST test large role rendering with 200ms target, 250ms max (25% tolerance)
- **FR-028**: Performance tests MUST emit warnings for times between target and max
- **FR-029**: Performance tests MUST fail only when exceeding max threshold
- **FR-030**: Performance results MUST be saved to tests/tmp/performance-results.json with status field

#### Documentation Automation

- **FR-031**: System MUST auto-update README Table of Contents on commit if README.md changes
- **FR-032**: TOC generator MUST create GitHub-compatible anchors (emojis → hyphens, lowercase)
- **FR-033**: System MUST sync version from pyproject.toml to CHANGELOG.md and README.md on commit
- **FR-034**: System MUST validate atomic changelog entries match README badge URLs

### Key Entities

- **Pre-commit Hook**: Configuration unit with id, name, entry command, language, dependencies, file patterns, and stage
- **CI Workflow**: GitHub Actions workflow with trigger events, jobs, steps, matrix builds, and artifact uploads
- **Badge**: Visual indicator with schema (label, message, color, style) generated from metrics
- **Performance Metric**: Test timing with test_name, time_ms, target_ms, max_ms, and status (pass/warn/fail)
- **Test Result**: Pytest outcome with counts (passed, skipped, failed, errors, warnings) and optional coverage data

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of commits MUST pass pre-commit hooks before entering repository (measured by CI success rate)
- **SC-002**: CI MUST complete full test suite in under 10 minutes on Windows Python 3.13
- **SC-003**: Badge generation MUST complete in under 2 minutes after CI completion
- **SC-004**: Performance tests MUST detect >30% slowdowns with 95% confidence (few false positives)
- **SC-005**: All 16 badges MUST update automatically within 15 minutes of code push
- **SC-006**: Pre-commit hook failure rate MUST be <5% (excluding intentional test failures)
- **SC-007**: README Table of Contents MUST be 100% accurate (all headings linked correctly)
- **SC-008**: Version sync MUST maintain 100% consistency across pyproject.toml, CHANGELOG.md, README.md
- **SC-009**: Type checking with mypy MUST maintain 0 errors in core ansibledoctor/ code
- **SC-010**: Code coverage MUST be visible and tracked over time (target: 80%+ for core modules)

## Implementation Notes

### Current Tool Versions

- Black: 24.4.0
- isort: 5.13.0
- Ruff: ≥0.1.0
- mypy: ≥1.8.0
- pytest: ≥8.0.0
- pytest-cov: ≥4.0.0
- Python: 3.11, 3.13 (CI matrix)

### Configuration Files

- `.pre-commit-config.yaml`: Pre-commit hook definitions (222 lines, 6 groups, 13 hooks)
- `pyproject.toml`: Tool configurations (black, isort, ruff, mypy, pytest, coverage)
- `.github/workflows/pre-commit.yml`: Pre-commit validation workflow
- `.github/workflows/ci-windows.yml`: Test execution workflow (Python 3.11, 3.13)
- `.github/workflows/badges.yml`: Badge generation workflow
- `.github/workflows/check-changelog-atomic.yml`: Changelog validation workflow

### Scripts

- `scripts/update_readme_toc.py`: README Table of Contents generator (279 lines)
- `scripts/sync_version.py`: Version synchronization across files
- `scripts/generate_badge_metrics.py`: Badge JSON generation from metrics (372 lines)
- `scripts/check_yaml.py`: YAML validation script
- `scripts/run_pytest_precommit.py`: Pytest wrapper for pre-commit
- `scripts/parse_precommit_results.py`: Metrics extraction from pre-commit output

### Badge System Architecture

```
CI Completion
    ↓
Badge Workflow Triggered
    ↓
Download Artifacts (pytest XML, coverage JSON, performance JSON)
    ↓
Parse Metrics (generate_badge_metrics.py)
    ↓
Generate 16 Badge JSONs (Shields.io endpoint format)
    ↓
Upload to badges/ artifact
    ↓
(Optional) Update Gist for dynamic badges
```

### Performance Testing Flow

```
pytest tests/performance/
    ↓
conftest.py pytest_configure() - Initialize _perf_results dict
    ↓
Test runs → record_perf(name, time_ms, target_ms, max_ms)
    ↓
Status calculated: pass (≤target), warn (target<time≤max), fail (>max)
    ↓
pytest_unconfigure() - Save to tests/tmp/performance-results.json
    ↓
CI uploads performance-results.json as artifact
    ↓
Badge workflow parses JSON and generates performance badge
```

## Assumptions

- **A-001**: Developers have Git and pre-commit installed locally
- **A-002**: GitHub Actions runners have sufficient resources (2-core, 7GB RAM for Windows runner)
- **A-003**: Badge images from shields.io are accessible (external dependency)
- **A-004**: Performance tests run on consistent hardware (CI runners)
- **A-005**: Artifacts are retained for 7 days (sufficient for debugging)

## Dependencies

- **External**: shields.io for badge rendering, GitHub Actions for CI/CD
- **Python Packages**: All tools versioned in pyproject.toml and .pre-commit-config.yaml
- **Workflows**: pre-commit.yml must complete before badges.yml runs
- **Scripts**: Badge generation depends on pytest XML and coverage JSON formats

## Risks & Mitigations

- **Risk**: Pre-commit hooks too slow → **Mitigation**: Stage separation (fast on pre-commit, slow on pre-push)
- **Risk**: CI environment drift → **Mitigation**: Explicit dependency versioning, Poetry lock file
- **Risk**: Flaky performance tests → **Mitigation**: Progressive tolerance (33%/30%/25%) instead of strict thresholds
- **Risk**: Badge generation fails → **Mitigation**: Non-fatal badge workflow, manual badge updates documented
- **Risk**: Windows encoding issues → **Mitigation**: Force UTF-8 encoding in scripts (codecs.getwriter)

## Future Enhancements

- **FE-001**: Add macOS and Linux CI workflows for cross-platform testing
- **FE-002**: Implement mutation testing with mutmut for test quality assessment
- **FE-003**: Add security scanning with bandit and safety
- **FE-004**: Implement automatic dependency updates with Dependabot
- **FE-005**: Add code complexity metrics with radon
- **FE-006**: Implement automatic changelog generation from conventional commits
- **FE-007**: Add performance trend tracking over time (database storage)
- **FE-008**: Implement automatic PR labeling based on changed files
- **FE-009**: Add spell checking for documentation files
- **FE-010**: Implement automatic code review with AI tools
