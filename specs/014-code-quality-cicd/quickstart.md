# Quick Start Guide: Code Quality & CI/CD

**Feature**: 014-code-quality-cicd  
**Last Updated**: 2026-01-10

## 🚀 Quick Reference

### For New Contributors

#### 1. First Time Setup (5 minutes)

```bash
# Clone repository
git clone https://github.com/K4M1coder/ansible-doctor-enhanced.git
cd ansible-doctor-enhanced

# Install Poetry (if not already installed)
# Windows PowerShell:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push

# Verify installation
poetry run pre-commit run --all-files
```

**Expected Result**: All hooks pass (formatting, linting, type checking, tests).

---

#### 2. Making Your First Commit (2 minutes)

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes to code
# Edit ansibledoctor/...

# Stage changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "feat: add my feature"

# If hooks fail, they auto-fix most issues
# Stage auto-fixed files and commit again
git add .
git commit -m "feat: add my feature"
```

**What Happens**:
1. **Black** formats your Python code
2. **isort** organizes your imports
3. **Ruff** fixes common linting issues
4. **mypy** checks types (if you edited ansibledoctor/)
5. **README TOC** updates automatically if you edited README.md
6. **Commit succeeds** if all checks pass

---

#### 3. Pushing Your Code (3 minutes)

```bash
# Push to your branch
git push origin feature/my-feature

# Pre-push hooks run (full test suite)
# This takes 3-5 minutes
```

**What Happens**:
1. **Unit tests** run (quick tests only)
2. **Integration tests** run (if applicable)
3. **Performance tests** run (small/medium/large role benchmarks)
4. **Push succeeds** if all tests pass

**If Tests Fail**:
- Review test output in terminal
- Fix failing tests
- Commit fix: `git commit -am "fix: address test failures"`
- Push again

---

### For Maintainers

#### Reviewing Pull Requests

```bash
# Check CI status before review
# GitHub: Actions tab > CI Windows workflow

# Look for:
✅ Pre-commit: All hooks passed
✅ CI Windows (Python 3.11): Tests passed
✅ CI Windows (Python 3.13): Tests passed
✅ Badges: Generated successfully

# Review badge changes in PR
# Badges update automatically after CI completes
```

---

#### Merging Pull Requests

```bash
# Merge to dev branch
# CI runs again on dev

# After CI completes:
# 1. Badges update in README
# 2. Coverage report refreshes
# 3. Performance metrics captured

# Check badges on dev branch:
# https://github.com/K4M1coder/ansible-doctor-enhanced/blob/dev/README.md
```

---

## 🛠️ Common Workflows

### Workflow 1: Fix Pre-commit Hook Failure

**Scenario**: You commit and pre-commit fails.

```bash
# Example: Black formatting failed
❌ black................................................Failed
   - hook id: black
   - files were modified by this hook

# Auto-fixed files are already staged by pre-commit
# Just commit again:
git add .
git commit -m "feat: my feature"

# If issue is NOT auto-fixable (e.g., type error):
❌ mypy.................................................Failed
   error: Argument 1 to "foo" has incompatible type "str"; expected "int"

# Fix the issue manually
# Edit file to fix type error
vim ansibledoctor/module.py

# Commit fix
git add ansibledoctor/module.py
git commit -m "feat: my feature"
```

---

### Workflow 2: Skip Expensive Tests Locally

**Scenario**: You want to commit without running full test suite (pre-push stage).

```bash
# Option 1: Commit and don't push yet
git commit -m "feat: work in progress"
# Pre-commit hooks run (fast: formatting, linting)
# Pre-push hooks DON'T run (you didn't push)

# Option 2: Use SKIP environment variable
SKIP=pytest-precommit git push origin feature/my-feature
# ⚠️ WARNING: Tests WILL run in CI
# Only skip locally if you're confident

# Option 3: Run tests manually before push
poetry run pytest
# If tests pass, then push normally
git push origin feature/my-feature
```

**⚠️ NEVER use `--no-verify`**: See `.github/COMMIT_QUALITY.md` for why.

---

### Workflow 3: Update Tool Versions

**Scenario**: Monthly maintenance, update Black/isort/Ruff/mypy.

```bash
# Check for updates
poetry show --outdated

# Update specific tool (example: Black)
poetry update black

# Update pre-commit hook versions
pre-commit autoupdate

# Test locally
pre-commit run --all-files
poetry run pytest

# If all pass, commit
git add pyproject.toml poetry.lock .pre-commit-config.yaml
git commit -m "chore: update code quality tools"
git push origin dev
```

---

### Workflow 4: Investigate Badge Discrepancy

**Scenario**: Coverage badge shows 79% but you think it should be higher.

```bash
# Step 1: Run coverage locally
poetry run pytest --cov=ansibledoctor --cov-report=term-missing

# Step 2: Compare to badge value
# Badge value: 79%
# Local value: 81%

# Step 3: Check CI artifacts
# GitHub: Actions > CI Windows > Latest run > Artifacts
# Download: pytest-results-3.13.zip
# Extract: coverage.json

# Step 4: Parse coverage.json
cat artifacts/pytest-results-3.13/coverage.json | jq '.totals.percent_covered'
# Output: 79.2

# Step 5: Identify discrepancy source
# Local coverage (81%) includes tests you wrote but haven't pushed
# CI coverage (79%) is from dev branch (before your changes)

# Solution: Push your changes, wait for CI, badge updates
```

---

### Workflow 5: Debug Performance Test Failure

**Scenario**: Performance test failed in CI but passes locally.

```bash
# Step 1: Check performance results in CI
# GitHub: Actions > CI Windows > Latest run > Artifacts
# Download: pytest-results-3.13.zip
# Extract: tests/tmp/performance-results.json

# Step 2: Compare timings
cat performance-results.json | jq
{
  "small_role": {
    "time_ms": 85,
    "target_ms": 60,
    "max_ms": 80,
    "status": "fail"
  },
  ...
}

# Step 3: Understand the failure
# CI: 85ms (> 80ms max) → FAIL
# Local: 55ms (< 60ms target) → PASS
# Root cause: CI runners are slower/busier

# Step 4: Decide on action
# Option A: Accept variance, re-run CI (might pass next time)
# Option B: Increase max_ms threshold (if consistently failing)
# Option C: Investigate performance regression in code

# Step 5: If increasing threshold, update test
# Edit tests/performance/test_generator_benchmarks.py
def test_small_role_rendering(record_perf):
    # ...
    record_perf("small_role", elapsed_ms, 60, 90)  # Changed from 80 to 90
    assert elapsed_ms <= 90  # Updated assertion
```

---

## 🔧 Troubleshooting

### Issue 1: Pre-commit Hooks Too Slow

**Symptom**: `git commit` takes >1 minute.

**Diagnosis**:
```bash
# Run hooks with timing
pre-commit run --all-files --verbose

# Look for slow hooks (>10 seconds)
```

**Solutions**:
- **Slow linting**: Check Ruff configuration, ensure `--fix` is efficient
- **Slow type checking**: mypy caches results, ensure `.mypy_cache/` exists
- **Slow tests**: Tests run on pre-push, not pre-commit (check `.pre-commit-config.yaml`)

**Prevention**: Separate fast checks (pre-commit) from slow checks (pre-push).

---

### Issue 2: Pre-commit Hook Missing Dependency

**Symptom**:
```
ModuleNotFoundError: No module named 'requests'
```

**Diagnosis**: Hook runs in isolated environment, missing dependency.

**Solution**:
```yaml
# Edit .pre-commit-config.yaml
- repo: local
  hooks:
    - id: my-hook
      name: my-hook
      entry: python scripts/my_script.py
      language: system
      additional_dependencies:
        - requests>=2.28  # Add missing dependency
```

**Prevention**: Always declare dependencies in `additional_dependencies`.

---

### Issue 3: Windows Encoding Error

**Symptom**:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'
```

**Diagnosis**: Script prints Unicode (emoji, special chars) on Windows.

**Solution**: Force UTF-8 encoding at start of script.

```python
# Add to top of script (e.g., update_readme_toc.py)
import sys
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
```

**Prevention**: Always use UTF-8 encoding for scripts that print Unicode.

---

### Issue 4: CI Passes but Badges Don't Update

**Symptom**: CI completes successfully but badges show old values.

**Diagnosis**: Badge workflow failed or didn't trigger.

**Solution**:
```bash
# Step 1: Check badge workflow status
# GitHub: Actions > Generate Badges > Latest run

# Step 2: Check workflow logs
# Look for:
# - Artifact download failures
# - Parsing errors in generate_badge_metrics.py
# - Upload failures

# Step 3: Manually trigger badge workflow
# GitHub: Actions > Generate Badges > Run workflow

# Step 4: If workflow succeeded but badges still wrong
# Check README.md badge URLs
# Ensure they point to correct endpoint (shields.io or gist)
```

**Prevention**: Monitor badge workflow regularly (see [tasks.md](tasks.md) TASK-003).

---

### Issue 5: Performance Test Flaky in CI

**Symptom**: Performance test passes sometimes, fails other times.

**Diagnosis**: CI runner performance variance.

**Solution**: Check if timing is within warning range.

```bash
# View performance-results.json from CI
{
  "medium_role": {
    "time_ms": 115,
    "target_ms": 100,
    "max_ms": 130,
    "status": "warn"
  }
}

# Status: "warn" (not "fail") = acceptable variance
# Badge shows warning emoji (⚠️) but test passes

# If status is "fail", investigate:
# - Recent code changes (performance regression?)
# - CI runner issues (GitHub status page)
# - Threshold too strict (consider increasing max_ms)
```

**Prevention**: Use progressive tolerance (target → warning → failure).

---

## 📊 Understanding Badges

### Badge Color Coding

| Badge | Green | Yellow | Red |
|-------|-------|--------|-----|
| **Coverage** | ≥90% | 80-89% | <80% |
| **Tests Passed** | >0 | N/A | 0 |
| **Tests Failed** | 0 | N/A | >0 |
| **Performance** | All pass | Some warn | Any fail |
| **mypy** | 0 errors | N/A | >0 errors |
| **CI Status** | Passing | N/A | Failing |

### Badge Refresh Timeline

```
Code Push → CI Runs (8 min) → Artifacts Uploaded → Badge Workflow Triggers (2 min) → Badges Update
Total: ~10-15 minutes
```

### Reading the Performance Badge

**Format**: `perf [emoji] - S:[time] | M:[time] | L:[time]`

**Examples**:
- ✅ `perf ✓ - S:56ms | M:97ms | L:180ms` → All tests pass (green)
- ⚠️ `perf ⚠️ - S:56ms | M:115ms | L:180ms` → Medium warns (orange)
- ❌ `perf ❌ - S:56ms | M:97ms | L:260ms` → Large fails (red)

**Key**:
- **S**: Small role (target 60ms, max 80ms)
- **M**: Medium role (target 100ms, max 130ms)
- **L**: Large role (target 200ms, max 250ms)

---

## 📚 Resources

### Documentation
- **[spec.md](spec.md)**: Complete specification
- **[plan.md](plan.md)**: Implementation plan and phases
- **[tasks.md](tasks.md)**: Ongoing tasks and maintenance
- **[.github/COMMIT_QUALITY.md](../../.github/COMMIT_QUALITY.md)**: Commit quality standards

### Configuration Files
- **[.pre-commit-config.yaml](../../.pre-commit-config.yaml)**: Pre-commit hook definitions
- **[pyproject.toml](../../pyproject.toml)**: Tool configurations
- **[.github/workflows/](../../.github/workflows/)**: CI/CD workflows

### Scripts
- **[generate_badge_metrics.py](../../scripts/generate_badge_metrics.py)**: Badge generation
- **[update_readme_toc.py](../../scripts/update_readme_toc.py)**: TOC generation
- **[sync_version.py](../../scripts/sync_version.py)**: Version synchronization

### External Links
- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 🆘 Getting Help

### Where to Look First
1. **Error in pre-commit hook?** → Check [.github/COMMIT_QUALITY.md](../../.github/COMMIT_QUALITY.md)
2. **CI failure?** → Check workflow logs in GitHub Actions
3. **Badge issue?** → Check [Troubleshooting](#-troubleshooting) section above
4. **Performance issue?** → Check [Workflow 5](#workflow-5-debug-performance-test-failure)

### Asking for Help
When reporting issues, include:
- Error message (full output)
- Command that failed
- Pre-commit hook output (if applicable)
- CI workflow logs (if CI-related)
- Badge values vs expected values (if badge-related)

### Contact
- **GitHub Issues**: https://github.com/K4M1coder/ansible-doctor-enhanced/issues
- **Maintainers**: See CONTRIBUTING.md

---

## ⚡ Cheat Sheet

```bash
# Install everything
poetry install && poetry run pre-commit install

# Run all quality checks locally
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run tests with coverage
poetry run pytest --cov=ansibledoctor --cov-report=term-missing

# Update all tools
poetry update && pre-commit autoupdate

# Check for outdated packages
poetry show --outdated

# Generate badges locally
poetry run python scripts/generate_badge_metrics.py --pytest pytest.xml --coverage coverage.json

# Force UTF-8 on Windows (in scripts)
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
```

---

**Last Updated**: 2026-01-10  
**Version**: 1.0  
**Maintainer**: GitHub Copilot
