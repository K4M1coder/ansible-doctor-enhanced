# Contributing to ansible-doctor-enhanced

Thank you for your interest in contributing! This document provides guidelines and workflows for contributing to ansible-doctor-enhanced.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Constitution & Standards](#constitution--standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

## Code of Conduct

This project follows the principles of respect, collaboration, and constructive feedback. Please be kind and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of Ansible roles

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ansible-doctor-enhanced.git
cd ansible-doctor-enhanced

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Or use Poetry (recommended)
poetry install --with dev

# Verify installation
python -m ansibledoctor --version
pytest tests/ -v
```

### Project Constitution

**IMPORTANT**: This project follows a strict 10-article [Constitution](.specify/memory/constitution.md) that governs all development. Please read it before contributing.

Key principles:
- **Article I**: Specification-Driven Development (SDD)
- **Article III**: Test-Driven Development (TDD) mandatory
- **Article V**: Structured logging required
- **Article VI**: Type safety with mypy --strict
- **Article X**: Domain-Driven Design patterns

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Follow TDD Cycle (MANDATORY)

```bash
# 1. RED: Write failing test first
#    Create test in tests/unit/ or tests/integration/
vim tests/unit/test_your_feature.py

# 2. Run test - should FAIL
pytest tests/unit/test_your_feature.py -v

# 3. GREEN: Implement minimal code to pass
vim ansibledoctor/module/your_feature.py

# 4. Run test - should PASS
pytest tests/unit/test_your_feature.py -v

# 5. REFACTOR: Clean up code
# Improve implementation while keeping tests green

# 6. Verify coverage ≥80%
pytest tests/ --cov=ansibledoctor --cov-report=term
```

### 3. Quality Checks (Pre-Commit)

```bash
# Type checking (MUST pass)
mypy ansibledoctor/ --strict

# Code formatting
black ansibledoctor/ tests/
isort ansibledoctor/ tests/

# Linting
ruff check .

# Run all tests
pytest tests/ -v

### Install pre-commit hooks (recommended)

We provide a `.pre-commit-config.yaml` that includes a hook to validate atomic changelog + README updates when bumping the package version. To enable the hooks locally, run:

```bash
# Install the pre-commit framework (if not already installed)
pip install pre-commit
# Install the hooks defined in the repo
pre-commit install
# Optionally, run the hooks against all files now
pre-commit run --all-files
```
```

## Constitution & Standards

### Article III: Test-Driven Development

**MANDATORY**: All code MUST be written using TDD Red-Green-Refactor cycle.

```python
# ❌ WRONG: Writing code before tests
def parse_variable(var: str) -> Variable:
    return Variable(name=var)

# ✅ CORRECT: Write test first
def test_parse_variable_with_valid_name():
    """RED: Test written BEFORE implementation."""
    result = parse_variable("test_var")
    assert result.name == "test_var"
```

### Article V: Structured Logging

**REQUIRED**: Use structured logging, never print() or logging module directly.

```python
# ❌ WRONG
print(f"Parsing {file_path}")
logging.info("Variable parsed")

# ✅ CORRECT
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)
logger.info("parsing_variable", file_path=file_path, var_name=var_name)
```

### Article VI: Type Safety

**REQUIRED**: All functions must have complete type hints.

```python
# ❌ WRONG
def parse_role(path):
    return role

# ✅ CORRECT
def parse_role(path: Path) -> AnsibleRole:
    """Parse Ansible role from directory."""
    return role
```

### Article X: Domain-Driven Design

Follow DDD patterns:

- **Value Objects**: Immutable Pydantic models with `frozen=True`
- **Entities**: Objects with identity (e.g., RoleMetadata)
- **Aggregates**: Root objects that maintain consistency (e.g., AnsibleRole)
- **Repositories**: Parser classes that retrieve and store domain objects
- **Protocols**: Interfaces for dependency injection

## Testing Requirements

### Coverage Target: ≥80%

All contributions must maintain or improve test coverage.

```bash
# Check current coverage
pytest tests/ --cov=ansibledoctor --cov-report=html
open htmlcov/index.html

# Coverage must be ≥80%
pytest tests/ --cov=ansibledoctor --cov-fail-under=80
```

### Test Types

1. **Unit Tests** (tests/unit/)
   - Test individual functions/classes in isolation
   - Mock external dependencies
   - Fast execution (<1s per test)

2. **Integration Tests** (tests/integration/)
   - Test component interactions
   - Use real fixtures (minimal_role, complex_role)
   - Verify end-to-end workflows

3. **Property Tests** (tests/property/)
   - Use hypothesis for edge cases
   - Test invariants hold for random inputs

4. **Performance Tests** (tests/performance/)
   - Verify SC-002 requirements
   - Minimal role: <500ms
   - Complex role: <2s

### Test Naming Convention

```python
# Pattern: test_<what>_<condition>_<expected_result>

def test_parse_variable_with_valid_annotation_returns_variable():
    """Test that valid @var annotation creates Variable object."""
    pass

def test_parse_metadata_with_missing_file_raises_parsing_error():
    """Test that missing meta/main.yml raises ParsingError."""
    pass
```

## Commit Guidelines

### Conventional Commits (REQUIRED)

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code change that neither fixes bug nor adds feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

**Examples**:

```bash
# Feature
git commit -m "feat(parser): add support for YAML list variables"

# Bug fix
git commit -m "fix(cli): handle missing role path gracefully

Previously would crash with AttributeError. Now raises
helpful ValidationError with suggestion.

Fixes #42"

# Documentation
git commit -m "docs(readme): add installation via pip"

# Breaking change
git commit -m "feat(api)!: change Variable.type to enum

BREAKING CHANGE: Variable.type is now VariableType enum instead of string.
Update code: Variable(type='string') -> Variable(type=VariableType.STRING)"
```

## Pull Request Process

### Before Submitting PR

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage ≥80%: `pytest tests/ --cov=ansibledoctor --cov-fail-under=80`
- [ ] Type checking passes: `mypy ansibledoctor/ --strict`
- [ ] Code formatted: `black ansibledoctor/ tests/`
- [ ] Imports sorted: `isort ansibledoctor/ tests/`
- [ ] No linting errors: `ruff check .`
- [ ] CHANGELOG.md updated under `[Unreleased]`
- [ ] Documentation updated (if applicable)

### PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Added property tests (if applicable)
- [ ] Performance tests updated (if applicable)

## Constitution Compliance
- [ ] Article III: TDD Red-Green-Refactor followed
- [ ] Article V: Structured logging used
- [ ] Article VI: Type hints complete
- [ ] Coverage ≥80%

## Checklist
- [ ] Tests pass locally
- [ ] Code formatted (black, isort)
- [ ] Type checking passes (mypy --strict)
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
```

### Review Process

1. Automated checks run (CI pipeline)
2. Maintainer review
3. Address feedback
4. Approval and merge

## Template Development

### Template Authoring Guide

Templates are Jinja2 files that render role documentation. For comprehensive guidance, see [docs/TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md).

**Quick Start:**

```bash
# Show default template
ansible-doctor templates show markdown > my-template.j2

# Edit my-template.j2 with your customizations

# Validate syntax
ansible-doctor templates validate my-template.j2

# Use custom template
ansible-doctor generate /role --template my-template.j2 --output README.md
```

**Template Context:**

All templates receive a `TemplateContext` with these variables:

- `role`: Role object (name, description, metadata, variables, tags, todos, examples)
- `generator_version`: ansibledoctor version string
- `generation_date`: datetime object for timestamp
- `output_format`: OutputFormat enum (MARKDOWN, HTML, RST)

**Custom Filters:**

Templates have access to format-specific filters:

```jinja2
{{ role.name | upper }}  {# Built-in Jinja2 filters #}
{{ role.description | markdown_escape }}  {# Escape Markdown special chars #}
{{ role.description | rst_escape }}  {# Escape RST special chars #}
{{ example.code | code_block(example.language) }}  {# Format code blocks #}
```

**Testing Templates:**

```python
from ansibledoctor.generator import TemplateValidator, TemplateEngine

engine = TemplateEngine.create()
validator = TemplateValidator(engine.environment)

# Validate syntax
result = validator.validate_template(
    template_source,
    template_name="custom.j2",
    required_vars={"role", "generator_version"}
)

assert result["valid"], result["errors"]
```

**Template Structure Example:**

```jinja2
# {{ role.name }}

{% if role.metadata %}
**Author:** {{ role.metadata.author }}
**License:** {{ role.metadata.license }}
{% endif %}

## Variables

{% for var in role.variables %}
### `{{ var.name }}`

{{ var.description | default('No description provided.') }}

- **Type:** `{{ var.type | default('any') }}`
- **Default:** `{{ var.value }}`
{% endfor %}
```

**Contributing Templates:**

To contribute new template formats:

1. Create template in `ansibledoctor/generator/templates/<format>/role.j2`
2. Add renderer class in `ansibledoctor/generator/renderers/<format>.py`
3. Update `OutputFormat` enum with new format
4. Write tests following existing patterns (see `tests/unit/test_<format>_renderer.py`)
5. Update docs/TEMPLATE_GUIDE.md with format-specific guidance

## Project Structure

```
ansible-doctor-enhanced/
├── ansibledoctor/           # Main package
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── cli/                 # Application layer
│   │   └── __init__.py      # Click-based CLI
│   ├── models/              # Domain models (DDD)
│   │   ├── annotation.py    # Annotation value objects
│   │   ├── metadata.py      # Role metadata entity
│   │   ├── variable.py      # Variable value object
│   │   ├── tag.py           # Tag value object
│   │   └── role.py          # Aggregate root
│   ├── parser/              # Domain services
│   │   ├── protocols.py     # Parser interfaces
│   │   ├── yaml_loader.py   # YAML loading abstraction
│   │   ├── annotation_extractor.py  # Annotation parsing
│   │   ├── metadata_parser.py       # Metadata parsing
│   │   └── variable_parser.py       # Variable parsing
│   ├── utils/               # Infrastructure
│   │   ├── logging.py       # Structured logging
│   │   └── paths.py         # Path utilities
│   └── exceptions.py        # Domain exceptions
├── tests/
│   ├── unit/                # Unit tests (fast, isolated)
│   ├── integration/         # Integration tests (fixtures)
│   │   └── fixtures/        # Test roles
│   ├── property/            # Property-based tests (hypothesis)
│   └── performance/         # Performance benchmarks
├── docs/                    # Documentation
├── .specify/                # Specification-driven artifacts
│   └── memory/
│       └── constitution.md  # Project constitution
├── specs/                   # Feature specifications
│   └── 001-ansible-role-parser/
│       ├── spec.md          # Feature spec
│       ├── plan.md          # Implementation plan
│       └── tasks.md         # Task breakdown
├── pyproject.toml           # Project config & dependencies
├── README.md                # User-facing documentation
├── CHANGELOG.md             # Keep a Changelog format
└── CONTRIBUTING.md          # This file
```

## Development Tips

### Running Specific Tests

```bash
# Single test file
pytest tests/unit/test_variable_parser.py -v

# Single test function
pytest tests/unit/test_variable_parser.py::test_parse_variable_with_annotation -v

# Tests matching pattern
pytest tests/ -k "annotation" -v

# With coverage for specific module
pytest tests/unit/test_variable_parser.py --cov=ansibledoctor.parser.variable_parser
```

### Debugging Tests

```python
# Add breakpoint in test or code
def test_something():
    result = function_under_test()
    breakpoint()  # Python 3.7+ built-in
    assert result == expected

# Run with pdb
pytest tests/unit/test_file.py --pdb
```

### Performance Profiling

```bash
# Profile test execution
pytest tests/ --profile

# Profile specific code
python -m cProfile -o output.prof -m ansibledoctor parse role_path
python -m pstats output.prof
```

### Documentation Preview

```bash
# Render README locally (if using grip)
grip README.md

# Or use VS Code Markdown Preview
# Ctrl+Shift+V (Windows/Linux)
# Cmd+Shift+V (Mac)
```

## Questions?

- Open a [GitHub Discussion](https://github.com/yourusername/ansible-doctor-enhanced/discussions)
- Check existing [Issues](https://github.com/yourusername/ansible-doctor-enhanced/issues)
- Read the [README](README.md)
- Review the [Constitution](.specify/memory/constitution.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
