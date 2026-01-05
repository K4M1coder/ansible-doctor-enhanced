# Type Quality Guide

## Overview

This project uses **mypy** for static type checking to catch type errors before runtime. The pre-commit hooks now include mypy checks to ensure type quality.

## Current Status

The codebase is in a **gradual typing adoption** phase. The mypy configuration in `pyproject.toml` has been relaxed to allow:
- Untyped function definitions
- Incomplete type annotations
- Untyped decorators (needed for Click CLI)

## Running Type Checks

### Quick Check
```bash
mypy ansibledoctor --config-file=pyproject.toml
```

### Detailed Report
```bash
python scripts/check_type_quality.py
```

### Pre-commit Hook
Type checking runs automatically on commit:
```bash
pre-commit run mypy --all-files
```

## Common Errors and Fixes

### 1. Variable Type Annotations (`var-annotated`)

**Error:**
```python
warnings_list = []  # Need type annotation
```

**Fix:**
```python
warnings_list: list[str] = []
```

### 2. Function Return Type Annotations

**Error:**
```python
def my_function():
    pass
```

**Fix:**
```python
def my_function() -> None:
    pass
```

### 3. Optional Arguments (`assignment`)

**Error:**
```python
def foo(name: str = None):  # Incompatible default
    pass
```

**Fix:**
```python
def foo(name: str | None = None):
    pass
```

### 4. Dictionary/Collection Type Hints

**Error:**
```python
results = {}  # mypy doesn't know types
results["key"] = "value"  # Unsupported target
```

**Fix:**
```python
results: dict[str, Any] = {}
results["key"] = "value"
```

### 5. Union Types for Multiple Renderers

**Error:**
```python
renderer = MarkdownRenderer()
if format == "html":
    renderer = HtmlRenderer()  # Incompatible types
```

**Fix:**
```python
from typing import Union
renderer: MarkdownRenderer | HtmlRenderer | RstRenderer

renderer = MarkdownRenderer()
if format == "html":
    renderer = HtmlRenderer()
```

### 6. Function Argument Types (`arg-type`)

**Error:**
```python
def process(config: ConfigModel):
    merge_config(file_config, config)  # expects dict, got ConfigModel
```

**Fix:**
```python
def process(config: ConfigModel):
    merge_config(file_config, config.model_dump())
```

## Gradual Migration Strategy

### Phase 1: Critical Paths (Current)
- ✅ Add mypy to pre-commit
- ✅ Configure relaxed mypy settings
- ✅ Create type quality report tool

### Phase 2: Core Modules
Focus on most-used modules:
1. `ansibledoctor/models/` - Data models (mostly done)
2. `ansibledoctor/exceptions/` - Error handling
3. `ansibledoctor/utils/` - Utility functions

### Phase 3: CLI and Parsers
1. Fix variable annotations in CLI
2. Add return types to functions
3. Fix argument type mismatches

### Phase 4: Strict Mode
Once errors are resolved:
1. Re-enable `disallow_untyped_defs = true`
2. Re-enable `disallow_incomplete_defs = true`
3. Remove module-specific overrides

## Ignoring Specific Errors

For third-party libraries without stubs:
```python
import some_library  # type: ignore[import-not-found]
```

For complex cases requiring refactoring:
```python
result = complex_function()  # type: ignore[arg-type]  # TODO: Fix in #123
```

## Benefits of Type Checking

1. **Catch bugs early** - Type errors found before runtime
2. **Better IDE support** - Autocomplete and refactoring
3. **Documentation** - Types serve as inline documentation
4. **Refactoring confidence** - Safe to change code structure
5. **API clarity** - Clear function contracts

## Pre-commit Configuration

The mypy hook is configured in `.pre-commit-config.yaml`:

```yaml
- id: mypy
  name: Type checking with mypy
  entry: mypy
  language: python
  additional_dependencies: [mypy>=1.8.0, ...]
  files: '\.py$'
  args: ["--config-file=pyproject.toml"]
```

## Mypy Configuration

Located in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Relaxed for gradual typing
disallow_incomplete_defs = false  # Relaxed for gradual typing
...
```

## Resources

- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints PEP 484](https://peps.python.org/pep-0484/)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Common Mypy Issues](https://mypy.readthedocs.io/en/stable/common_issues.html)

## Getting Help

If you encounter type errors you don't know how to fix:
1. Run `python scripts/check_type_quality.py` for categorized report
2. Check this guide for common patterns
3. Search mypy documentation
4. Ask in PR reviews - type safety is a team effort!
