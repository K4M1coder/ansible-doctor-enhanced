# Commit Quality Standards

## Pre-commit Hooks

All commits **MUST** pass pre-commit hooks. Never use `--no-verify` to bypass quality checks.

### Why Pre-commit Hooks Matter

1. **Code Quality**: Ensures consistent formatting and linting
2. **Non-Regression**: Runs tests to catch breaking changes
3. **Standards Compliance**: Validates YAML, updates TOC, syncs versions
4. **Team Consistency**: Everyone follows the same standards

### If a Hook Fails

#### ❌ WRONG Approach
```bash
# Never do this!
git commit --no-verify -m "quick fix"
```

#### ✅ CORRECT Approach
```bash
# 1. Understand WHY it failed
pre-commit run --all-files

# 2. Fix the root cause
#    - Add missing dependencies
#    - Fix failing tests
#    - Update configuration

# 3. Commit properly
git commit -m "fix: proper commit message"
```

### Common Issues and Solutions

#### Missing Dependencies in Pre-commit
**Problem**: `ModuleNotFoundError` in isolated pre-commit environment

**Solution**: Add missing dependencies to `.pre-commit-config.yaml`
```yaml
- id: your-hook
  additional_dependencies: [
    "requests>=2.28",
    "beautifulsoup4>=4.11",
  ]
```

#### Test Failures
**Problem**: Tests fail during pre-commit

**Solution**: 
- Fix the test or code issue
- If test needs environment-specific setup, mark it with `@pytest.mark.skipif`
- Never skip tests without valid reason

#### Slow Hooks
**Problem**: Pre-commit takes too long

**Solution**:
- Use `stages: [pre-push]` for expensive checks
- Keep fast checks in `pre-commit` stage
- Run `pre-commit run` manually before committing

## Historical Note

Commits `46cae80` and `3c160d2` used `--no-verify` due to missing `requests` dependency in pre-commit environment. This was corrected in commit `1a4faa3` by adding proper dependencies.

**Lesson**: Always fix the root cause rather than bypassing quality checks.
