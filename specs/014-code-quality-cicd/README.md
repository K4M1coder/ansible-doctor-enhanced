# Spec 014: Code Quality & CI/CD Infrastructure

**Status**: ✅ Implemented & Active  
**Created**: 2026-01-10  
**Last Updated**: 2026-01-10

---

## 📋 Overview

This specification documents the comprehensive code quality and CI/CD infrastructure for ansible-doctor-enhanced. The system ensures code quality through automated checks, maintains non-regression through continuous testing, and provides visibility through metrics and badges.

---

## 📚 Documentation Structure

### Core Documents

- **[spec.md](spec.md)** - Complete specification with user scenarios, requirements, and success criteria
- **[plan.md](plan.md)** - Implementation plan with phases, tasks, and lessons learned
- **[tasks.md](tasks.md)** - Ongoing maintenance and improvement tasks
- **[quickstart.md](quickstart.md)** - Quick reference guide for common workflows

### Checklists

- **[checklists/requirements.md](checklists/requirements.md)** - Comprehensive requirements checklist with validation status

### Contracts

- **[contracts/hook-schema.md](contracts/hook-schema.md)** - Pre-commit hook configuration schema and best practices
- **[contracts/workflow-schema.md](contracts/workflow-schema.md)** - GitHub Actions workflow schema and patterns
- **[contracts/badge-format.md](contracts/badge-format.md)** - Badge JSON format specification and generation pipeline

---

## 🎯 Quick Links

### For New Contributors
- Start here: [quickstart.md](quickstart.md) - 5-minute setup guide
- Quality standards: [../../.github/COMMIT_QUALITY.md](../../.github/COMMIT_QUALITY.md)
- Pre-commit hooks: [contracts/hook-schema.md](contracts/hook-schema.md)

### For Maintainers
- Requirements checklist: [checklists/requirements.md](checklists/requirements.md)
- Maintenance tasks: [tasks.md](tasks.md)
- Implementation history: [plan.md](plan.md)

### For Developers
- Troubleshooting pre-commit: [quickstart.md#-troubleshooting](quickstart.md#-troubleshooting)
- Workflow patterns: [contracts/workflow-schema.md](contracts/workflow-schema.md)
- Badge generation: [contracts/badge-format.md](contracts/badge-format.md)

---

## 🛠️ Infrastructure Summary

### Code Quality Tools (4)
- **Black 24.4.0**: Code formatting
- **isort 5.13.0**: Import sorting
- **Ruff ≥0.1.0**: Fast linting with auto-fix
- **mypy ≥1.8.0**: Static type checking (strict mode)

### Pre-commit Hooks (6 Groups)
1. **Basic Formatting**: trailing whitespace, newlines, YAML validation
2. **Python Formatting**: Black, isort
3. **Linting**: Ruff with auto-fix
4. **Type Checking**: mypy on ansibledoctor/
5. **Documentation**: version sync, TOC update, changelog validation
6. **Testing**: unit, integration, performance (pre-push stage)

### CI/CD Workflows (4)
1. **pre-commit.yml**: Validates all hooks on GitHub
2. **ci-windows.yml**: Runs tests on Python 3.11 & 3.13
3. **badges.yml**: Generates 16 badges from metrics
4. **check-changelog-atomic.yml**: Validates changelog format

### Badge System (16 Badges)
- **Static (3)**: version, license, Python version
- **Code Quality (4)**: Black, isort, Ruff, mypy
- **Test Metrics (6)**: coverage, passed, skipped, failed, warnings, performance
- **CI Status (3)**: pre-commit, CI Windows, badges

---

## 📊 Current Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Pre-commit pass rate | 95%+ | ~98% | ✅ |
| CI completion time | <10 min | ~8 min | ✅ |
| Badge update time | <15 min | ~10-12 min | ✅ |
| Coverage (core) | 80%+ | 79% | ⚠️ (close) |
| mypy errors | 0 | 0 | ✅ |
| Test failures | 0 | 0 | ✅ |

---

## 🚀 Getting Started

### For New Contributors

```bash
# 1. Install dependencies
poetry install

# 2. Install pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push

# 3. Verify setup
poetry run pre-commit run --all-files

# 4. Make your first commit
git add .
git commit -m "feat: my feature"
```

**Time**: 5-10 minutes  
**See**: [quickstart.md](quickstart.md) for detailed instructions

---

### For Maintainers

```bash
# Weekly: Monitor CI performance
# GitHub Actions > Workflows > Recent runs

# Monthly: Update tool versions
poetry update
pre-commit autoupdate

# Review: Badge accuracy
# Compare badges to latest CI artifacts
```

**See**: [tasks.md](tasks.md) for full maintenance checklist

---

## 🔍 Key Features

### 1. Automatic Code Formatting
- Black formats all Python code on commit
- isort organizes imports
- No manual formatting needed

### 2. Progressive Performance Testing
- Small role: 60ms target, 80ms max (33% tolerance)
- Medium role: 100ms target, 130ms max (30% tolerance)
- Large role: 200ms target, 250ms max (25% tolerance)
- Warnings instead of failures for acceptable variance

### 3. Comprehensive Badge System
- 16 badges showing project health
- Real-time updates from CI
- Color-coded status (green/yellow/red)

### 4. Multi-version Testing
- Tests run on Python 3.11 and 3.13
- Windows CI ensures cross-platform compatibility
- Artifact retention for debugging (7 days)

### 5. Documentation Automation
- README Table of Contents auto-updates
- Version synchronization across files
- Atomic changelog validation

---

## 📈 Success Stories

### What Went Well

✅ **Pre-commit stage separation**: Fast checks on commit (<30s), slow checks on push (3-5 min) keeps developers productive

✅ **Progressive tolerance**: Performance tests with warnings (not failures) reduce flaky test frustration

✅ **Artifact-based workflow**: CI → artifacts → badges ensures badge accuracy

✅ **UTF-8 encoding enforcement**: Prevents Windows-specific encoding errors

✅ **Comprehensive documentation**: COMMIT_QUALITY.md reduces support burden

### Lessons Learned

💡 **Quality tools catch different issues**: Black (formatting), Ruff (logic), mypy (types) - need all three

💡 **Automation is critical**: Manual quality checks are forgotten, automated checks are consistent

💡 **Developer experience matters**: Fast feedback loops (pre-commit) beat slow feedback (CI only)

💡 **Visibility drives improvement**: Badges make quality visible, visibility drives accountability

---

## 🛡️ Quality Standards

### Never Use `--no-verify`

**Why**: Bypassing pre-commit hooks violates quality standards and allows bad code to enter the repository.

**Correct Approach**:
1. Fix the root cause (missing dependency, code issue)
2. Commit properly with all hooks passing
3. Document issues in .github/COMMIT_QUALITY.md

**See**: [../../.github/COMMIT_QUALITY.md](../../.github/COMMIT_QUALITY.md) for detailed standards

---

### UTF-8 Encoding on Windows

**Issue**: Windows uses cp1252 encoding by default, causing `UnicodeEncodeError`.

**Solution**: Force UTF-8 in scripts that print Unicode:

```python
import sys
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
```

**Example**: [../../scripts/update_readme_toc.py](../../scripts/update_readme_toc.py)

---

### Pre-commit Dependencies

**Issue**: Each hook runs in isolated environment, dependencies must be declared.

**Solution**: Add ALL dependencies to `additional_dependencies`:

```yaml
- id: my-hook
  entry: python scripts/my_script.py
  additional_dependencies:
    - requests>=2.28
    - beautifulsoup4>=4.11
```

**Example**: [../../.pre-commit-config.yaml](../../.pre-commit-config.yaml) lines 135-137 (pytest-performance hook)

---

## 🔗 Related Specifications

- **Spec 001**: Ansible Role Parser (testing infrastructure)
- **Spec 002**: Documentation Generator (performance benchmarks)
- **Spec 003**: Role Parity (quality standards)
- **Spec 009**: Execution Reports (logging infrastructure)
- **Spec 010**: Error Reports (error handling patterns)

---

## 📞 Support

### Getting Help

1. **Pre-commit issues**: Check [quickstart.md#-troubleshooting](quickstart.md#-troubleshooting)
2. **CI failures**: Review workflow logs in GitHub Actions
3. **Badge issues**: Check [contracts/badge-format.md](contracts/badge-format.md)
4. **Performance issues**: See [quickstart.md - Workflow 5](quickstart.md#workflow-5-debug-performance-test-failure)

### Reporting Issues

**GitHub Issues**: https://github.com/K4M1coder/ansible-doctor-enhanced/issues

**Include**:
- Error message (full output)
- Command that failed
- Pre-commit hook output (if applicable)
- CI workflow logs (if CI-related)

---

## 📝 Revision History

| Date       | Version | Changes                          | Author |
|------------|---------|----------------------------------|--------|
| 2026-01-10 | 1.0     | Initial spec 014 documentation   | GitHub Copilot |

---

## 📄 License

This specification is part of ansible-doctor-enhanced and is licensed under the Apache License 2.0.

See [../../LICENSE](../../LICENSE) for details.

---

**Maintainer**: GitHub Copilot  
**Last Review**: 2026-01-10  
**Next Review**: 2026-04-10 (quarterly)
