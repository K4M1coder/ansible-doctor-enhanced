# Implementation Plan: Code Quality & CI/CD Infrastructure

**Feature**: 014-code-quality-cicd  
**Status**: Implemented & Active  
**Last Updated**: 2026-01-10

## Overview

This document outlines the implementation plan for the comprehensive code quality and CI/CD infrastructure. **Note**: This feature is already implemented. This plan serves as:
1. Historical reference for how the system was built
2. Guide for teams adopting similar infrastructure
3. Checklist for maintaining and extending the system

## Implementation Phases

### Phase 1: Foundation - Code Quality Tools (COMPLETED)

**Objective**: Establish core code quality tools for Python development

**Duration**: 1 week  
**Dependencies**: None

#### Tasks

1. **Install and configure Black**
   - Add Black 24.4.0 to pyproject.toml dependencies
   - Configure Black settings in pyproject.toml:
     ```toml
     [tool.black]
     line-length = 100
     target-version = ['py311']
     ```
   - Test Black on existing codebase
   - Document Black configuration rationale

2. **Install and configure isort**
   - Add isort 5.13.0 to dependencies
   - Configure isort for Black compatibility:
     ```toml
     [tool.isort]
     profile = "black"
     line_length = 100
     ```
   - Ensure isort doesn't conflict with Black
   - Test on ansibledoctor/ imports

3. **Install and configure Ruff**
   - Add Ruff ≥0.1.0 to dependencies
   - Configure Ruff rules in pyproject.toml:
     ```toml
     [tool.ruff]
     line-length = 100
     select = ["E", "F", "I", "N", "W"]
     ```
   - Enable auto-fix for common issues
   - Run Ruff on codebase and fix violations

4. **Install and configure mypy**
   - Add mypy ≥1.8.0 to dependencies
   - Configure mypy for strict type checking:
     ```toml
     [tool.mypy]
     strict = true
     warn_return_any = true
     warn_unused_configs = true
     ```
   - Add type stubs for dependencies
   - Run mypy on ansibledoctor/ (not tests/)

**Deliverables**:
- ✅ pyproject.toml with tool configurations
- ✅ Clean codebase passing all quality checks
- ✅ Documentation of tool choices and settings

**Success Metrics**:
- ✅ 100% of Python files formatted with Black
- ✅ 0 isort violations
- ✅ 0 Ruff errors (warnings acceptable)
- ✅ 0 mypy errors in ansibledoctor/

---

### Phase 2: Pre-commit Hook Integration (COMPLETED)

**Objective**: Automate quality checks on every commit

**Duration**: 1 week  
**Dependencies**: Phase 1

#### Tasks

1. **Install pre-commit framework**
   - Add pre-commit to dev dependencies
   - Initialize .pre-commit-config.yaml
   - Install hooks: `pre-commit install`

2. **Configure formatting hooks (Group 1: Basic Formatting)**
   ```yaml
   - repo: https://github.com/pre-commit/pre-commit-hooks
     hooks:
       - id: trailing-whitespace
       - id: end-of-file-fixer
       - id: check-yaml
   ```
   - Test on sample commits

3. **Configure Python formatting hooks (Group 2)**
   ```yaml
   - repo: https://github.com/psf/black
     rev: 24.4.0
     hooks:
       - id: black
   - repo: https://github.com/pycqa/isort
     rev: 5.13.0
     hooks:
       - id: isort
   ```
   - Verify Black and isort don't conflict

4. **Configure linting hooks (Group 3)**
   ```yaml
   - repo: https://github.com/astral-sh/ruff-pre-commit
     rev: v0.1.0
     hooks:
       - id: ruff
         args: [--fix]
   ```

5. **Configure type checking hooks (Group 4)**
   ```yaml
   - repo: local
     hooks:
       - id: mypy
         name: mypy
         entry: poetry run mypy
         language: system
         types: [python]
         files: ^ansibledoctor/
   ```
   - Note: mypy runs only on ansibledoctor/, not tests/

6. **Configure documentation hooks (Group 5)**
   ```yaml
   - repo: local
     hooks:
       - id: sync-version
         name: sync-version
         entry: python scripts/sync_version.py
       - id: update-readme-toc
         name: update-readme-toc
         entry: python scripts/update_readme_toc.py
   ```

7. **Configure testing hooks (Group 6)**
   ```yaml
   - repo: local
     hooks:
       - id: pytest-precommit
         name: pytest-precommit
         entry: python scripts/run_pytest_precommit.py
         stages: [pre-push]
   ```
   - Note: Full tests run on pre-push, not pre-commit

8. **Optimize hook performance**
   - Separate fast checks (pre-commit stage) from slow checks (pre-push stage)
   - Configure parallel hook execution where possible
   - Add `pass_filenames: false` for project-wide hooks

**Deliverables**:
- ✅ .pre-commit-config.yaml with 6 logical groups
- ✅ All hooks passing on existing codebase
- ✅ Documentation: .github/COMMIT_QUALITY.md

**Success Metrics**:
- ✅ Pre-commit hooks run in <30 seconds for typical commit
- ✅ Pre-push hooks (full tests) run in <5 minutes
- ✅ 0 commits bypass hooks with --no-verify

---

### Phase 3: CI/CD Workflows (COMPLETED)

**Objective**: Automate testing and validation on GitHub

**Duration**: 1 week  
**Dependencies**: Phase 2

#### Tasks

1. **Create main CI workflow (ci-windows.yml)**
   ```yaml
   name: CI Windows
   on:
     push:
       branches: [dev]
     pull_request:
       branches: [dev]
   jobs:
     test:
       runs-on: windows-latest
       strategy:
         matrix:
           python-version: ['3.11', '3.13']
       steps:
         - uses: actions/checkout@v4
         - name: Set up Python
           uses: actions/setup-python@v5
         - name: Install dependencies
         - name: Run tests with coverage
         - name: Upload artifacts
   ```

2. **Create pre-commit validation workflow (pre-commit.yml)**
   ```yaml
   name: Pre-commit
   on: [push, pull_request]
   jobs:
     pre-commit:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
         - uses: pre-commit/action@v3.0.0
   ```

3. **Create changelog validation workflow (check-changelog-atomic.yml)**
   ```yaml
   name: Check Changelog Atomic
   on: [push, pull_request]
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Validate changelog entries
   ```

4. **Configure artifact retention**
   - Set artifact retention to 7 days
   - Upload pytest XML, coverage JSON, performance JSON
   - Structure artifacts by Python version

5. **Test CI workflows**
   - Push test commits to trigger workflows
   - Verify all matrix builds complete
   - Verify artifacts are uploaded correctly

**Deliverables**:
- ✅ 3 GitHub Actions workflows (ci-windows, pre-commit, check-changelog-atomic)
- ✅ Artifact upload/download working
- ✅ CI status badges in README

**Success Metrics**:
- ✅ CI completes in <10 minutes for Python 3.13
- ✅ CI runs on every push to dev and every PR
- ✅ Artifacts retained for 7 days

---

### Phase 4: Badge System (COMPLETED)

**Objective**: Visualize code quality metrics in README

**Duration**: 1 week  
**Dependencies**: Phase 3

#### Tasks

1. **Create badge generation script (generate_badge_metrics.py)**
   - Function: `parse_pytest_xml()` - Extract test counts
   - Function: `parse_coverage_json()` - Extract coverage percentage
   - Function: `parse_mypy_output()` - Extract error count
   - Function: `generate_badge_json()` - Create Shields.io endpoint JSON
   - CLI: Accept --pytest, --coverage, --mypy, --performance arguments

2. **Create badge workflow (badges.yml)**
   ```yaml
   name: Generate Badges
   on:
     workflow_run:
       workflows: ["CI Windows"]
       types: [completed]
   jobs:
     badges:
       runs-on: ubuntu-latest
       steps:
         - name: Download artifacts
         - name: Parse metrics
         - name: Generate badge JSONs
         - name: Upload to badges/ artifact
   ```

3. **Implement 16 badges**
   - Static badges: version, license, Python version
   - Code quality badges: Black (✓), isort (✓), Ruff (✓), mypy (error count)
   - Test badges: coverage (percentage), passed, skipped, failed, warnings
   - Performance badge: perf (✓/⚠️/❌ + timings)
   - CI status badges: pre-commit, CI Windows, badges

4. **Add badges to README**
   ```markdown
   ![Version](https://img.shields.io/badge/version-0.8.0-blue)
   ![License](https://img.shields.io/badge/license-Apache--2.0-blue)
   ![Python](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue)
   ![Black](https://img.shields.io/badge/code%20style-black-black)
   ![isort](https://img.shields.io/badge/imports-isort-blue)
   ![Ruff](https://img.shields.io/badge/linter-ruff-blue)
   ![mypy](https://img.shields.io/badge/mypy-0%20errors-green)
   ![Coverage](https://img.shields.io/badge/coverage-79%25-yellow)
   ![Tests Passed](https://img.shields.io/badge/tests-184%20passed-green)
   ![Tests Skipped](https://img.shields.io/badge/tests-3%20skipped-yellow)
   ![Tests Failed](https://img.shields.io/badge/tests-0%20failed-green)
   ![Tests Warnings](https://img.shields.io/badge/tests-2%20warnings-yellow)
   ![Performance](https://img.shields.io/badge/perf%20✓-S%3A56ms%20%7C%20M%3A57ms%20%7C%20L%3A58ms-green)
   ![Pre-commit](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/pre-commit.yml/badge.svg)
   ![CI Windows](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/ci-windows.yml/badge.svg)
   ![Badges](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/badges.yml/badge.svg)
   ```

5. **Test badge generation**
   - Trigger CI completion
   - Verify badge workflow runs
   - Check all 16 badges render correctly

**Deliverables**:
- ✅ scripts/generate_badge_metrics.py (372 lines)
- ✅ .github/workflows/badges.yml
- ✅ 16 badges in README.md

**Success Metrics**:
- ✅ Badges update within 15 minutes of CI completion
- ✅ Badge colors match status (green=good, yellow=warning, red=error)
- ✅ All badges display correct metrics

---

### Phase 5: Performance Testing (COMPLETED)

**Objective**: Monitor and prevent performance regressions

**Duration**: 1 week  
**Dependencies**: Phase 3, Phase 4

#### Tasks

1. **Create pytest plugin for performance metrics (tests/performance/conftest.py)**
   ```python
   def pytest_configure(config):
       config._perf_results = {}
   
   def pytest_unconfigure(config):
       results_file = Path("tests/tmp/performance-results.json")
       results_file.parent.mkdir(exist_ok=True)
       with open(results_file, "w") as f:
           json.dump(config._perf_results, f, indent=2)
   
   @pytest.fixture
   def record_perf(request):
       def _record(name, time_ms, target_ms, max_ms):
           if time_ms <= target_ms:
               status = "pass"
           elif time_ms <= max_ms:
               status = "warn"
           else:
               status = "fail"
           request.config._perf_results[name] = {
               "time_ms": time_ms,
               "target_ms": target_ms,
               "max_ms": max_ms,
               "status": status
           }
       return _record
   ```

2. **Implement performance tests**
   ```python
   def test_small_role_rendering(record_perf):
       start = time.perf_counter()
       # ... test code ...
       elapsed_ms = (time.perf_counter() - start) * 1000
       record_perf("small_role", elapsed_ms, 60, 80)
       assert elapsed_ms <= 80, f"Small role too slow: {elapsed_ms}ms"
   ```

3. **Define progressive tolerance**
   - Small role: 60ms target, 80ms max (33% tolerance)
   - Medium role: 100ms target, 130ms max (30% tolerance)
   - Large role: 200ms target, 250ms max (25% tolerance)

4. **Update badge generation for performance**
   ```python
   def parse_performance_results(perf_json_path):
       with open(perf_json_path) as f:
           results = json.load(f)
       short_labels = {"small_role": "S", "medium_role": "M", "large_role": "L"}
       # ...
   
   def generate_performance_badge(perf_json_path):
       results = parse_performance_results(perf_json_path)
       overall_status = determine_overall_status(results)
       timings = format_timings(results)
       return {
           "schemaVersion": 1,
           "label": f"perf {status_emoji}",
           "message": timings,
           "color": status_color
       }
   ```

5. **Update CI to upload performance results**
   ```yaml
   - name: Upload artifacts
     uses: actions/upload-artifact@v4
     with:
       path: |
         pytest-${{ matrix.python-version }}.xml
         tests/tmp/performance-results.json
   ```

6. **Update badge workflow to parse performance**
   ```yaml
   - name: Find performance results
     run: |
       PERF_JSON=$(find artifacts -name "performance-results.json" | head -n 1)
       echo "perf_json=$PERF_JSON" >> $GITHUB_OUTPUT
   - name: Generate performance badge
     if: steps.find-perf.outputs.perf_json != ''
     run: |
       python scripts/generate_badge_metrics.py --performance ${{ steps.find-perf.outputs.perf_json }}
   ```

**Deliverables**:
- ✅ tests/performance/conftest.py (pytest plugin)
- ✅ Performance tests with progressive tolerance
- ✅ Performance badge with color-coded status

**Success Metrics**:
- ✅ Performance badge shows timings: "S:56ms | M:57ms | L:58ms"
- ✅ Tests emit warnings (not failures) for acceptable variance
- ✅ Badge turns red only for >max threshold

---

### Phase 6: Documentation & Standards (COMPLETED)

**Objective**: Document quality standards and common issues

**Duration**: 3 days  
**Dependencies**: All previous phases

#### Tasks

1. **Create COMMIT_QUALITY.md**
   - Document why pre-commit hooks matter
   - Explain correct vs incorrect commit practices
   - List common issues and solutions:
     * Missing dependencies in pre-commit hooks
     * Windows encoding issues
     * Test failures in pre-commit environment
     * Slow hooks (stage separation)
   - Historical note: Why --no-verify was used (and corrected)

2. **Create spec 014 (this document)**
   - Document all 16 tools with versions
   - Document pre-commit hook architecture (6 groups)
   - Document 4 CI/CD workflows
   - Document 16 badges and generation pipeline
   - Document performance testing approach
   - Include user scenarios and acceptance criteria

3. **Update README**
   - Add all 16 badges at top
   - Add "Code Quality" section explaining tools
   - Add "CI/CD" section explaining workflows
   - Add "Contributing" section referencing COMMIT_QUALITY.md
   - Auto-update Table of Contents

4. **Create this implementation plan**
   - Document historical implementation phases
   - Provide checklist for maintenance
   - Guide teams adopting similar infrastructure

**Deliverables**:
- ✅ .github/COMMIT_QUALITY.md (70 lines)
- ✅ specs/014-code-quality-cicd/spec.md (comprehensive)
- ✅ specs/014-code-quality-cicd/plan.md (this file)
- ✅ Updated README with badges and sections

**Success Metrics**:
- ✅ Documentation covers all tools and workflows
- ✅ Common issues documented with solutions
- ✅ New contributors can understand quality standards

---

## Maintenance Checklist

### Weekly Tasks

- [ ] Review CI failures and investigate root causes
- [ ] Check badge accuracy (manually verify metrics)
- [ ] Monitor performance trends (are tests getting slower?)
- [ ] Review pre-commit hook execution times (any slow hooks?)

### Monthly Tasks

- [ ] Update tool versions (Black, isort, Ruff, mypy, pytest)
- [ ] Review and update .pre-commit-config.yaml versions
- [ ] Check for new pre-commit hooks available
- [ ] Review GitHub Actions versions (checkout@v5, setup-python@v5)
- [ ] Audit artifact storage usage (7-day retention sufficient?)

### Quarterly Tasks

- [ ] Review quality metrics trends (coverage, performance, test counts)
- [ ] Evaluate new quality tools (mutation testing, security scanning)
- [ ] Review and update quality standards documentation
- [ ] Survey team on pre-commit hook pain points

### Yearly Tasks

- [ ] Major version updates for all tools
- [ ] Re-evaluate Python version support (add 3.14, drop 3.11?)
- [ ] Review CI/CD architecture (migrate to Linux runners?)
- [ ] Benchmark performance against previous year

---

## Extension Opportunities

### High Priority

1. **Add Linux CI workflow**
   - Rationale: Most production environments are Linux
   - Effort: 1 day (copy ci-windows.yml, change runner)
   - Benefit: Catch Linux-specific issues early

2. **Implement security scanning with bandit**
   - Rationale: Security is critical for Ansible tools
   - Effort: 1 day (add bandit hook, configure rules)
   - Benefit: Catch security vulnerabilities

3. **Add dependency vulnerability scanning with safety**
   - Rationale: Keep dependencies secure
   - Effort: 1 day (add safety hook, configure ignore list)
   - Benefit: Early warning of vulnerable dependencies

### Medium Priority

4. **Implement mutation testing with mutmut**
   - Rationale: Assess test quality (do tests actually catch bugs?)
   - Effort: 2 days (install mutmut, configure, baseline)
   - Benefit: Improve test effectiveness

5. **Add code complexity metrics with radon**
   - Rationale: Identify overly complex functions
   - Effort: 1 day (add radon hook, set thresholds)
   - Benefit: Maintain code maintainability

6. **Implement automatic changelog generation**
   - Rationale: Reduce manual changelog maintenance
   - Effort: 3 days (conventional commits, changelog generator)
   - Benefit: Consistent, automated changelogs

### Low Priority

7. **Add spell checking for documentation**
   - Rationale: Professional documentation
   - Effort: 1 day (add codespell hook, configure dictionary)
   - Benefit: Catch typos in docs

8. **Implement performance trend tracking**
   - Rationale: Visualize performance over time
   - Effort: 5 days (database, graphing, dashboard)
   - Benefit: Early warning of gradual slowdowns

9. **Add automatic PR labeling**
   - Rationale: Organize PRs by area (docs, tests, features)
   - Effort: 2 days (labeler action, label configuration)
   - Benefit: Easier PR triage

---

## Lessons Learned

### What Went Well

- **Pre-commit stage separation**: Fast checks on commit, slow checks on push keeps developers productive
- **Progressive tolerance**: Performance tests with warnings (not failures) reduce flaky test frustration
- **Artifact-based workflow**: CI → artifacts → badges ensures badge accuracy
- **UTF-8 encoding enforcement**: Prevents Windows-specific encoding errors
- **Comprehensive documentation**: COMMIT_QUALITY.md reduces support burden

### What Could Be Improved

- **Initial --no-verify usage**: Early commits bypassed hooks, required rework (now documented)
- **Pre-commit dependency management**: Each hook needs complete dependencies, easy to miss
- **Badge workflow complexity**: Finding artifacts requires complex shell logic, could be simplified
- **mypy strict mode**: Caught many issues but required significant initial effort

### Key Insights

- **Quality tools catch different issues**: Black (formatting), Ruff (logic), mypy (types) - need all three
- **Automation is critical**: Manual quality checks are forgotten, automated checks are consistent
- **Developer experience matters**: Fast feedback loops (pre-commit) beat slow feedback (CI only)
- **Visibility drives improvement**: Badges make quality visible, visibility drives accountability

---

## Support & Resources

### Documentation

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Shields.io Documentation](https://shields.io/)

### Internal Resources

- `.github/COMMIT_QUALITY.md` - Commit quality standards
- `specs/014-code-quality-cicd/spec.md` - Complete specification
- `scripts/generate_badge_metrics.py` - Badge generation script
- `.pre-commit-config.yaml` - Pre-commit hook configuration

### Getting Help

- **Pre-commit issues**: Check `.github/COMMIT_QUALITY.md` common issues section
- **CI failures**: Review workflow logs in GitHub Actions tab
- **Badge issues**: Check badges.yml workflow, verify artifact upload
- **Performance issues**: Review tests/tmp/performance-results.json

---

## Revision History

| Date       | Version | Changes                                      | Author |
|------------|---------|----------------------------------------------|--------|
| 2026-01-10 | 1.0     | Initial implementation plan created          | GitHub Copilot |
