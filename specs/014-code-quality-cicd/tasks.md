# Tasks: Code Quality & CI/CD Infrastructure

**Feature**: 014-code-quality-cicd  
**Status**: Implemented & Active  
**Last Updated**: 2026-01-10

## Overview

This document contains ongoing maintenance and improvement tasks for the code quality and CI/CD infrastructure. All initial implementation tasks are complete (see [plan.md](plan.md) for implementation history).

---

## Active Tasks

### Task Group 1: Routine Maintenance

#### TASK-001: Monitor CI Performance
**Priority**: P1  
**Type**: Maintenance  
**Status**: Ongoing  
**Owner**: Maintainers  
**Effort**: 30 minutes/week

**Description**: Monitor CI execution times to ensure workflows complete within acceptable timeframes.

**Acceptance Criteria**:
- [ ] CI Windows workflow completes in <10 minutes for Python 3.13
- [ ] Pre-commit workflow completes in <5 minutes
- [ ] Badge workflow completes in <2 minutes
- [ ] If any workflow exceeds threshold, investigate and optimize

**Notes**:
- Check GitHub Actions > Workflows > Recent runs
- Look for trends (gradual slowdowns indicate bloat)
- Common causes: dependency resolution, network latency, test additions

---

#### TASK-002: Update Tool Versions
**Priority**: P2  
**Type**: Maintenance  
**Status**: Monthly  
**Owner**: Maintainers  
**Effort**: 1 hour/month

**Description**: Keep code quality tools updated to latest stable versions.

**Acceptance Criteria**:
- [ ] Check for updates: Black, isort, Ruff, mypy, pytest, pytest-cov
- [ ] Update pyproject.toml with new versions
- [ ] Update .pre-commit-config.yaml rev: fields
- [ ] Run `poetry update` and test locally
- [ ] Run pre-commit hooks and CI to verify compatibility
- [ ] Commit updates with message: "chore: update quality tool versions"

**Tools to Update**:
- Black (currently 24.4.0)
- isort (currently 5.13.0)
- Ruff (currently ≥0.1.0)
- mypy (currently ≥1.8.0)
- pytest (currently ≥8.0.0)
- pytest-cov (currently ≥4.0.0)

**Update Process**:
```bash
# Check for updates
poetry show --outdated

# Update specific package
poetry update black

# Update pre-commit hooks
pre-commit autoupdate

# Test locally
pre-commit run --all-files
poetry run pytest

# Commit if all pass
git add pyproject.toml poetry.lock .pre-commit-config.yaml
git commit -m "chore: update quality tool versions"
```

---

#### TASK-003: Review Badge Accuracy
**Priority**: P2  
**Type**: Validation  
**Status**: Weekly  
**Owner**: Maintainers  
**Effort**: 15 minutes/week

**Description**: Manually verify that badges accurately reflect current metrics.

**Acceptance Criteria**:
- [ ] Check coverage badge matches latest CI coverage report
- [ ] Check test count badges match latest pytest output
- [ ] Check performance badge matches latest performance-results.json
- [ ] Check mypy badge matches latest mypy output
- [ ] If discrepancies found, investigate badge generation logic

**Verification Steps**:
1. Go to latest CI run: Actions > CI Windows > Latest run
2. Download artifacts (pytest XML, coverage JSON, performance JSON)
3. Compare artifact contents to badge values in README
4. If mismatch, check badges.yml workflow logs

---

### Task Group 2: Quality Improvements

#### TASK-004: Improve Test Coverage
**Priority**: P2  
**Type**: Enhancement  
**Status**: Ongoing  
**Owner**: Developers  
**Effort**: Variable

**Description**: Increase test coverage for core modules (target: 80%+ for ansibledoctor/).

**Current Status**: 79% overall coverage

**Acceptance Criteria**:
- [ ] Identify modules with <70% coverage (use `poetry run pytest --cov-report=html`)
- [ ] Prioritize core modules (ansibledoctor/generator, ansibledoctor/parser)
- [ ] Write tests for uncovered lines
- [ ] Update coverage badge when improvements made

**Priority Modules** (lowest coverage first):
```bash
# Generate coverage report by module
poetry run pytest --cov=ansibledoctor --cov-report=term-missing

# Focus on files with < 70% coverage
# Example priorities:
# - ansibledoctor/links/ (often complex logic)
# - ansibledoctor/validation/ (critical path)
# - ansibledoctor/exceptions/ (error handling)
```

---

#### TASK-005: Optimize Performance Tests
**Priority**: P3  
**Type**: Enhancement  
**Status**: Backlog  
**Owner**: Developers  
**Effort**: 1 day

**Description**: Review and optimize performance test thresholds based on historical data.

**Current Thresholds**:
- Small role: 60ms target, 80ms max (33% tolerance)
- Medium role: 100ms target, 130ms max (30% tolerance)
- Large role: 200ms target, 250ms max (25% tolerance)

**Acceptance Criteria**:
- [ ] Collect 30 days of performance data from CI
- [ ] Calculate P50, P95, P99 percentiles for each test
- [ ] Adjust targets if tests consistently beat current targets
- [ ] Adjust max if tests consistently trigger warnings
- [ ] Document rationale for threshold changes

**Data Collection**:
```bash
# Download performance-results.json from last 30 CI runs
# Analyze timings:
# - Are tests consistently <target? (target too high)
# - Are tests frequently >target but <max? (target too low, tolerance too high)
# - Are tests occasionally >max? (flaky performance, investigate)
```

---

#### TASK-006: Add Security Scanning
**Priority**: P2  
**Type**: Enhancement  
**Status**: Backlog  
**Owner**: Maintainers  
**Effort**: 1 day

**Description**: Add bandit (security linter) and safety (dependency scanner) to pre-commit hooks.

**Acceptance Criteria**:
- [ ] Install bandit and safety as dev dependencies
- [ ] Add bandit hook to .pre-commit-config.yaml (Group 3: Linting)
- [ ] Add safety hook to .pre-commit-config.yaml (Group 3: Linting)
- [ ] Configure bandit to skip tests/ directory
- [ ] Configure safety to ignore known false positives
- [ ] Add security badges to README (bandit: 0 issues, safety: 0 vulnerabilities)
- [ ] Update badges.yml to parse bandit/safety output

**Hook Configuration**:
```yaml
# Add to Group 3: Linting
- repo: https://github.com/PyCQA/bandit
  rev: '1.7.5'
  hooks:
    - id: bandit
      args: ['-r', 'ansibledoctor/', '--skip', 'B101']
      exclude: ^tests/

- repo: local
  hooks:
    - id: safety
      name: safety
      entry: poetry run safety check --json
      language: system
      pass_filenames: false
```

---

### Task Group 3: Documentation

#### TASK-007: Document Common Pre-commit Issues
**Priority**: P2  
**Type**: Documentation  
**Status**: Ongoing  
**Owner**: Maintainers  
**Effort**: 30 minutes/issue

**Description**: Expand .github/COMMIT_QUALITY.md with solutions to newly encountered pre-commit issues.

**Acceptance Criteria**:
- [ ] When new pre-commit issue is reported, document it
- [ ] Include: Issue description, root cause, solution, prevention
- [ ] Add example error messages for easy searching
- [ ] Link to relevant tool documentation

**Common Issues to Document** (add as encountered):
- Hook timeout on large files
- Conflicting hook changes (e.g., Black vs Ruff formatting)
- Network issues (e.g., downloading large dependencies)
- Platform-specific failures (Windows vs Linux)

---

#### TASK-008: Create Video Tutorials
**Priority**: P3  
**Type**: Documentation  
**Status**: Backlog  
**Owner**: Maintainers  
**Effort**: 1 day

**Description**: Create short video tutorials demonstrating quality infrastructure usage.

**Acceptance Criteria**:
- [ ] Video 1: "Setting Up Pre-commit Hooks" (5 minutes)
- [ ] Video 2: "Understanding CI Workflows" (7 minutes)
- [ ] Video 3: "Reading Badge Metrics" (3 minutes)
- [ ] Video 4: "Debugging Pre-commit Failures" (10 minutes)
- [ ] Videos uploaded to project documentation or YouTube
- [ ] Links added to README and COMMIT_QUALITY.md

**Video Content**:
- Screen recording with voiceover
- Show actual workflow: edit code → commit → pre-commit runs → CI runs → badges update
- Demonstrate common failures and fixes
- Keep videos short and focused

---

### Task Group 4: Monitoring & Alerting

#### TASK-009: Set Up CI Failure Notifications
**Priority**: P2  
**Type**: Enhancement  
**Status**: Backlog  
**Owner**: Maintainers  
**Effort**: 2 hours

**Description**: Configure GitHub Actions to send notifications on CI failures.

**Acceptance Criteria**:
- [ ] Add notification step to ci-windows.yml (on failure)
- [ ] Configure notification destination (Slack, Discord, Email)
- [ ] Test notification by intentionally failing a test
- [ ] Document notification setup in COMMIT_QUALITY.md

**Notification Options**:
- GitHub Actions: [Slack notification action](https://github.com/marketplace/actions/slack-notify)
- GitHub Actions: [Discord notification action](https://github.com/marketplace/actions/discord-message-notify)
- GitHub native: Email notifications (Settings > Notifications)

---

#### TASK-010: Track Performance Trends
**Priority**: P3  
**Type**: Enhancement  
**Status**: Backlog  
**Owner**: Developers  
**Effort**: 5 days

**Description**: Implement performance trend tracking to visualize performance over time.

**Acceptance Criteria**:
- [ ] Design database schema for performance metrics (time series)
- [ ] Create API to ingest performance-results.json from CI
- [ ] Build dashboard to visualize trends (line charts, anomaly detection)
- [ ] Set up alerts for significant performance degradation (>10% slowdown)
- [ ] Document dashboard usage

**Technical Approach**:
- Database: SQLite or PostgreSQL (time series data)
- API: FastAPI or Flask (ingest endpoint)
- Dashboard: Grafana, Plotly Dash, or custom React app
- Hosting: GitHub Pages (static) or Heroku (dynamic)

---

### Task Group 5: Tool Evaluation

#### TASK-011: Evaluate Mutation Testing
**Priority**: P3  
**Type**: Research  
**Status**: Backlog  
**Owner**: Developers  
**Effort**: 2 days

**Description**: Evaluate mutmut or similar mutation testing tools to assess test quality.

**Acceptance Criteria**:
- [ ] Install mutmut as dev dependency
- [ ] Run mutation testing on sample module (e.g., ansibledoctor/utils/)
- [ ] Analyze results: mutation score, uncaught mutations
- [ ] Assess value: Does it find real test gaps?
- [ ] Decide: Integrate into CI or use periodically?
- [ ] Document findings in specs/014-code-quality-cicd/

**Mutation Testing Basics**:
- Mutmut modifies code (e.g., `if x > 0` → `if x >= 0`)
- Tests should fail when code is mutated
- If tests still pass, mutation "survives" (test gap)
- Mutation score = (killed mutations) / (total mutations)

---

#### TASK-012: Evaluate Code Complexity Tools
**Priority**: P3  
**Type**: Research  
**Status**: Backlog  
**Owner**: Developers  
**Effort**: 1 day

**Description**: Evaluate radon (complexity metrics) or similar tools to identify overly complex code.

**Acceptance Criteria**:
- [ ] Install radon as dev dependency
- [ ] Run radon on ansibledoctor/ directory
- [ ] Identify functions with cyclomatic complexity >10
- [ ] Identify functions with maintainability index <20
- [ ] Assess value: Does it find real complexity issues?
- [ ] Decide: Integrate into pre-commit or use periodically?
- [ ] Document findings in specs/014-code-quality-cicd/

**Radon Metrics**:
- Cyclomatic Complexity: Number of decision paths (if, while, for, etc.)
- Maintainability Index: Overall maintainability score (0-100)
- Thresholds: CC >10 = refactor, MI <20 = technical debt

---

## Completed Tasks

### ✅ TASK-000: Initial Implementation
**Completed**: 2026-01-10  
**Description**: Implemented all code quality tools, pre-commit hooks, CI workflows, badge system, performance testing.  
**See**: [plan.md](plan.md) for detailed implementation phases.

---

## Task Dependencies

```
TASK-002 (Update Tools) → TASK-003 (Review Badges)
TASK-004 (Coverage) → TASK-010 (Performance Trends)
TASK-006 (Security) → TASK-003 (Review Badges)
TASK-009 (Notifications) → TASK-010 (Trends)
TASK-011 (Mutation) → TASK-004 (Coverage)
```

---

## Task Prioritization Matrix

| Task | Priority | Effort | Value | Status |
|------|----------|--------|-------|--------|
| TASK-001 | P1 | 30m/week | High | Ongoing |
| TASK-002 | P2 | 1h/month | High | Monthly |
| TASK-003 | P2 | 15m/week | Medium | Weekly |
| TASK-004 | P2 | Variable | High | Ongoing |
| TASK-005 | P3 | 1 day | Medium | Backlog |
| TASK-006 | P2 | 1 day | High | Backlog |
| TASK-007 | P2 | 30m/issue | Medium | Ongoing |
| TASK-008 | P3 | 1 day | Low | Backlog |
| TASK-009 | P2 | 2 hours | High | Backlog |
| TASK-010 | P3 | 5 days | Medium | Backlog |
| TASK-011 | P3 | 2 days | Low | Backlog |
| TASK-012 | P3 | 1 day | Low | Backlog |

**Priority Legend**:
- P1: Critical, must be done regularly
- P2: Important, should be done soon
- P3: Nice to have, can be deferred

**Value Legend**:
- High: Directly improves code quality or prevents regressions
- Medium: Improves developer experience or visibility
- Low: Research or optional enhancements

---

## Sprint Planning

### Sprint 1 (Next 2 weeks)
- TASK-001: Monitor CI Performance (ongoing)
- TASK-002: Update Tool Versions (if updates available)
- TASK-003: Review Badge Accuracy (weekly)
- TASK-004: Improve Test Coverage (target: +5% coverage)
- TASK-006: Add Security Scanning (high value, 1 day effort)

### Sprint 2 (2-4 weeks)
- TASK-007: Document Common Pre-commit Issues (add 3 new issues)
- TASK-009: Set Up CI Failure Notifications
- TASK-005: Optimize Performance Tests (if data available)

### Sprint 3 (4-6 weeks)
- TASK-011: Evaluate Mutation Testing
- TASK-012: Evaluate Code Complexity Tools
- TASK-004: Improve Test Coverage (target: 85%+ total)

### Backlog (6+ weeks)
- TASK-008: Create Video Tutorials
- TASK-010: Track Performance Trends (larger effort)

---

## Revision History

| Date       | Version | Changes                              | Author |
|------------|---------|--------------------------------------|--------|
| 2026-01-10 | 1.0     | Initial task list created            | GitHub Copilot |
