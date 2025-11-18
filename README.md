# Ansible Doctor Enhanced

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A modernized fork of ansible-doctor with enhanced logging, error handling, documentation generation, and reporting capabilities built on KISS, SMART, and SOLID principles.

## 🎯 Project Description

Ansible Doctor Enhanced is a comprehensive tool for automatically generating documentation from Ansible roles. It parses role structures, extracts metadata, variables, task tags, and inline annotations to produce high-quality, structured documentation in multiple formats. Built with specification-driven development using GitHub spec-kit methodology.

## ✨ Key Features

- **Test-Driven Development (TDD)**: Mandatory Red-Green-Refactor cycle with 80%+ code coverage
- **Domain-Driven Design (DDD)**: Ubiquitous Language from Ansible domain, Bounded Contexts, rich domain models
- **Intelligent Role Parsing**: Extract metadata from `meta/main.yml`, variables from `defaults/` and `vars/`, task tags, and inline documentation annotations
- **Annotation System**: Support for `@var`, `@tag`, `@todo`, `@example`, and `@meta` annotations with multiple formats (single-line, multiline, JSON)
- **Structured Logging**: Advanced observability with structured logging, correlation IDs, and performance metrics
- **Error Handling**: Graceful error recovery with actionable suggestions and detailed context
- **Multiple Output Formats**: Generate documentation in Markdown, HTML, reStructuredText, and custom templates
- **CLI-First Design**: Scriptable command-line interface with JSON output for pipeline integration
- **Type-Safe**: Full type hints with mypy strict mode validation
- **Constitutional Governance**: 10 core principles ensuring quality, maintainability, and SOLID architecture

## 🏗️ Architecture

Ansible Doctor Enhanced follows **Domain-Driven Design (DDD)** principles with clean architecture:

### Core Components

```
ansibledoctor/
├── models/           # Domain Models (DDD Value Objects & Entities)
│   ├── annotation.py    - Annotation value objects (@var, @tag, @todo, @example, @meta)
│   ├── metadata.py      - Role metadata entity (author, platforms, dependencies)
│   ├── variable.py      - Variable value object (name, type, value, annotations)
│   ├── tag.py           - Task tag value object
│   └── role.py          - Aggregate root combining all role information
├── parser/           # Domain Services (Anti-Corruption Layer)
│   ├── annotation_extractor.py  - Extract annotations from YAML comments
│   ├── metadata_parser.py       - Parse meta/main.yml into Metadata entity
│   ├── variable_parser.py       - Parse defaults/vars with type inference
│   ├── yaml_loader.py           - YAML loading abstraction (ruamel.yaml)
│   └── protocols.py             - Parser protocols (interfaces)
├── generator/        # Documentation Generation (NEW in v0.3.0)
│   ├── engine.py        - Jinja2 template engine with custom filters
│   ├── loaders.py       - Template loaders (filesystem, embedded)
│   ├── renderers.py     - Format-specific renderers (Markdown, HTML, RST)
│   ├── validator.py     - Template validation and variable checking
│   ├── filters.py       - Custom Jinja2 filters (rst_escape, code_block, etc.)
│   ├── models.py        - Generation models (TemplateContext, RenderResult)
│   ├── templates/       - Default templates for all output formats
│   └── protocols.py     - Generator protocols (TemplateLoader interface)
├── cli/              # Application Layer (CLI Interface)
│   └── __init__.py      - Click-based CLI with parse command
├── utils/            # Infrastructure Layer (Cross-cutting concerns)
│   ├── logging.py       - Structured logging with correlation IDs
│   └── paths.py         - Path validation and role structure checks
└── exceptions.py     # Domain Exceptions (AnsibleDoctorError hierarchy)
```

### Design Principles

1. **Immutability**: All domain models are frozen Pydantic models (value objects)
2. **Ubiquitous Language**: Terminology from Ansible domain (role, variable, meta, defaults, handlers)
3. **Bounded Contexts**: Clear separation between parsing (input) and generation (output - Phase 2)
4. **Type Safety**: 100% type hints with mypy --strict validation
5. **Testability**: Protocol-based design enabling dependency injection and mocking

### Data Flow

```
Role Directory → YAMLLoader → Parsers → Domain Models → CLI Output (JSON/Text)
                    ↓            ↓           ↓
                  YAML     Annotations  Immutable
                 Content    Extraction   Entities
```

### Key Patterns

- **Parser Protocol**: Abstract interface for all parsers (metadata, variable, tag)
- **Value Objects**: Annotation, Variable, Tag (immutable, equality by value)
- **Entity**: Metadata (identity by role name)
- **Aggregate Root**: Role (composition of metadata + variables + tags)
- **Anti-Corruption Layer**: Parsers shield domain from YAML library changes

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (for development)

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/ansible-doctor-enhanced.git
cd ansible-doctor-enhanced

# Install with Poetry
poetry install

# Activate virtual environment
poetry shell
```

### From PyPI (Coming Soon)

```bash
pip install ansible-doctor-enhanced
```

## 🏃 Quick Start

Parse an Ansible role and generate documentation:

```bash
# Parse a single role
ansible-doctor-enhanced parse --role-path ./my-ansible-role --output role-docs.json

# Parse with structured logging
ansible-doctor-enhanced parse --role-path ./my-ansible-role --log-level INFO

# Recursive parsing
ansible-doctor-enhanced parse --role-path ./roles/ --recursive

# Generate Markdown documentation
ansible-doctor-enhanced generate --input role-docs.json --output README.md --template readme
```

**Example Output:**

```json
{
  "name": "my-role",
  "metadata": {
    "author": "John Doe",
    "description": "Configures web server",
    "license": "MIT"
  },
  "variables": [
    {
      "name": "web_port",
      "value": 80,
      "type": "number",
      "description": "HTTP port for web server"
    }
  ],
  "tags": [
    {
      "name": "installation",
      "description": null,
      "usage_count": 3,
      "file_locations": ["tasks/main.yml:5", "tasks/install.yml:2"]
    },
    {
      "name": "configuration",
      "description": null,
      "usage_count": 2,
      "file_locations": ["tasks/main.yml:15", "tasks/configure.yml:1"]
    }
  ],
  "todos": [
    {
      "description": "Add SSL certificate validation",
      "file_path": "tasks/main.yml",
      "line_number": 42,
      "priority": "high"
    }
  ],
  "examples": [
    {
      "title": "Basic web server setup",
      "code": "web_port: 8080\nweb_ssl_enabled: true",
      "description": null,
      "language": "yaml"
    }
  ]
}
```

## 📖 Usage

### Library API (Phase 2 Complete)

```python
from pathlib import Path
from ansibledoctor.parser import MetadataParser, RuamelYAMLLoader

# Initialize parser
yaml_loader = RuamelYAMLLoader()
metadata_parser = MetadataParser(yaml_loader)

# Parse role metadata
role_meta_dir = Path("/path/to/ansible-role/meta")
metadata = metadata_parser.parse_metadata(role_meta_dir)

# Access parsed metadata
print(f"Author: {metadata.author}")
print(f"License: {metadata.license}")
print(f"Platforms: {metadata.get_supported_platforms_summary()}")
print(f"Has dependencies: {metadata.has_dependencies()}")
```

### Generator API (Phase 9 Foundation Complete - NEW in v0.3.0)

```python
from pathlib import Path
from datetime import datetime
from ansibledoctor.generator import (
    TemplateEngine,
    TemplateContext,
    OutputFormat,
    TemplateValidator,
)
from ansibledoctor.models import Role

# Create template engine with custom template directory
engine = TemplateEngine.create(
    template_dir="/path/to/templates",
    auto_reload=True  # Reload templates on change
)

# Validate template before rendering
validator = TemplateValidator(engine.environment)
template_source = Path("templates/custom.j2").read_text()
result = validator.validate_template(
    template_source,
    required_vars={"role", "generator_version"}
)
if not result["valid"]:
    print(f"Template errors: {result['errors']}")

# Create rendering context
context = TemplateContext(
    role=role_obj,  # Parsed Role object
    generator_version="0.3.0",
    generation_date=datetime.now(),
    output_format=OutputFormat.MARKDOWN,
)

# Load and render template
template = engine.get_template("markdown/role.j2")
content = template.render(**context.to_dict())

# Write to file
output_path = Path("README.md")
output_path.write_text(content, encoding="utf-8")
```

### Template Validation

```python
from ansibledoctor.generator import TemplateValidator, TemplateEngine

engine = TemplateEngine.create()
validator = TemplateValidator(engine.environment)

# Validate template syntax
try:
    validator.validate_syntax(
        "{{ role.name | upper }}",
        template_name="custom.j2"
    )
except TemplateValidationError as e:
    print(f"Syntax error: {e}")

# Check for undeclared variables
template_source = "{{ role.name }} by {{ role.metadata.author }}"
vars_used = validator.get_undeclared_variables(template_source)
print(f"Variables used: {vars_used}")  # {'role'}

# Validate required variables are present
validator.validate_required_variables(
    template_source,
    required_vars={"role"},
    template_name="custom.j2"
)

# Comprehensive validation
result = validator.validate_template(
    template_source,
    template_name="custom.j2",
    required_vars={"role"}
)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print(f"Warnings: {result['warnings']}")
print(f"Variables: {result['undeclared_variables']}")
```

### CLI Interface (Coming in Phase 6)

```bash
# Basic parsing
ansible-doctor-enhanced parse --role-path /path/to/role

# With custom output file
ansible-doctor-enhanced parse --role-path /path/to/role --output custom.json

# Recursive mode for multiple roles
ansible-doctor-enhanced parse --role-path /path/to/roles --recursive

# Adjust log verbosity
ansible-doctor-enhanced parse --role-path /path/to/role --log-level DEBUG
```

### Generating Documentation (Phase 9 Foundation - NEW in v0.3.0)

```bash
# Generate Markdown documentation (coming in Phase 10)
ansible-doctor-enhanced generate --input role-data.json --output README.md --format markdown

# Generate HTML documentation
ansible-doctor-enhanced generate --input role-data.json --output index.html --format html

# Generate reStructuredText for Sphinx
ansible-doctor-enhanced generate --input role-data.json --output role.rst --format rst

# Use custom templates
ansible-doctor-enhanced generate --input role-data.json --template-dir ./templates --output README.md

# Validate templates before generation
ansible-doctor-enhanced validate-template --template custom.j2 --required-vars role,version
```

**Foundation Components Available (v0.3.0):**

- ✅ **Template Engine**: Jinja2-based rendering with custom filters
- ✅ **Template Loaders**: Filesystem and embedded template support
- ✅ **Output Formats**: Markdown, HTML, reStructuredText
- ✅ **Custom Filters**: `rst_escape`, `code_block`, `header_anchor`, `format_date`, `pluralize`, `wordwrap_filter`
- ✅ **Template Validation**: Syntax checking, variable detection, required variable validation
- ✅ **Default Templates**: Production-ready templates for all 3 formats
- ✅ **Integration Tests**: End-to-end validation for complete workflows

## ⚙️ Configuration

Configuration via `.ansibledoctor.yml` in role directory or project root:

```yaml
# Annotation types to extract
annotations:
  - var
  - tag
  - todo
  - example

# Output formatting
output:
  format: json
  pretty: true

# Logging configuration
logging:
  level: INFO
  format: structured
  
# Template settings
template:
  provider: local
  path: ./templates
```

Environment variables (override config file):

- `ANSIBLE_DOCTOR_LOG_LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR)
- `ANSIBLE_DOCTOR_OUTPUT`: Default output file path
- `ANSIBLE_DOCTOR_TEMPLATE`: Default template name

## 📚 Documentation

- [Full Documentation](https://ansible-doctor-enhanced.readthedocs.io/) *(coming soon)*
- [API Reference](docs/api.md) *(coming soon)*
- [Contributing Guide](CONTRIBUTING.md) *(coming soon)*
- [Architecture Overview](docs/architecture.md) *(coming soon)*
- [Changelog](CHANGELOG.md)

## 🏗️ Project Architecture

Built with **Specification-Driven Development (SDD)** using GitHub spec-kit:

- **Constitution**: Governance principles (KISS, SMART, SOLID)
- **Specifications**: Feature specs with user stories and acceptance criteria
- **Plans**: Technical implementation plans with architecture decisions
- **Tasks**: Atomic, dependency-ordered task breakdowns

See [Constitution](​.specify/memory/constitution.md) for development principles.

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/ansible-doctor-enhanced.git
cd ansible-doctor-enhanced

# Install dependencies including dev tools
poetry install --with dev

# Run tests
poetry run pytest

# Run type checking
poetry run mypy ansibledoctor/

# Run linting
poetry run ruff check .

# Format code
poetry run black ansibledoctor/ tests/
poetry run isort ansibledoctor/ tests/
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# With coverage report
pytest --cov=ansibledoctor --cov-report=html
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key principles:
- Follow the [Constitution](​.specify/memory/constitution.md) (all 9 principles)
- Test-First Development (TDD mandatory)
- Update CHANGELOG.md for all changes
- Maintain 80%+ test coverage
- Use Conventional Commits format

## 📊 Project Status

**Current Phase**: Initial Development

- ✅ Project initialization with spec-kit
- ✅ Constitution defined (v1.1.0)
- ✅ Feature 001 specified: Ansible Role Parser
- ✅ Implementation plan created
- 🔄 Task breakdown (in progress)
- ⏳ Implementation (pending)

## 🔄 Version Compatibility

| ansible-doctor-enhanced | Python | Ansible | Status |
|------------------------|--------|---------|--------|
| 0.1.x (dev)           | 3.11+  | 2.9+    | MVP Complete |

## 📊 Project Status

**MVP Status**: ✅ **COMPLETE**

### Completed Features (51/100 tasks)

#### ✅ Core Functionality (MVP)
- **Metadata Parser (US1)**: Extract role metadata from `meta/main.yml`
  - Author, description, license, company
  - Platform support with versions
  - Role dependencies with version constraints
  - Argument specs (Ansible 2.11+)
  - 30 test methods ensuring correctness

- **Variables Parser (US2)**: Parse role variables with annotations
  - Extract from `defaults/main.yml` and `vars/main.yml`
  - Automatic type inference (string, number, boolean, list, dict, null)
  - Support 3 annotation formats: plain text, JSON, YAML
  - Required/example/deprecated attributes
  - 60 test methods ensuring correctness

- **Task Tags Parser (US3)**: Extract and analyze task tags
  - Parse tags from `tasks/*.yml` and `handlers/*.yml`
  - Track tag usage counts across tasks
  - Record file locations for each tag occurrence
  - Support both string and list tag formats
  - 21 test methods ensuring correctness

- **TODO & Examples Parser (US4)**: Extract inline documentation
  - Parse `@todo` annotations with priority levels (low, medium, high, critical)
  - Extract `@example` code blocks with language detection
  - Support multiline blocks with `@example...@end` syntax
  - Track file paths and line numbers for all annotations
  - 40 test methods ensuring correctness

- **CLI Interface**: Command-line tool ready for production
  - `parse` command with role_path argument
  - Flags: `--output`, `--recursive`, `--validate`, `--log-level`
  - JSON output to stdout or file
  - Exit codes for automation (0=success, 1=error, 2=validation)
  - Recursive mode for parsing multiple roles
  - 20 test methods ensuring correctness

#### 🎯 Roadmap to v1.0.0

**v0.3.0 - Role Documentation Generator** (Feature 002 - 93% COMPLETE)
- ✅ Phase 9 Foundation: Template engine, loaders, renderers, validators
- ✅ Markdown/HTML/RST output formats with Jinja2 templates
- ✅ Default templates with responsive HTML and Sphinx-compatible RST
- ✅ Custom filters: rst_escape, code_block, header_anchor, etc.
- ✅ Template validation: syntax checking, variable detection
- ✅ Integration tests: 12 end-to-end workflow tests
- ⏳ Phase 10: CLI `generate` command integration (NEXT)
- ⏳ Phase 11: Custom template support and template inheritance
- ⏳ Phase 12: Testing, polish, and documentation finalization

**v0.4.0 - Documentation Parity** (Remaining Role Features)
- All features from original ansible-doctor for roles
- Performance optimization (<500ms per role)
- Cross-platform validation (Windows, macOS, Linux)
- Template system stabilization

**v0.5.0 - Collection Documentation** (NEW - Not in original)
- Parse Ansible collections (multiple roles, plugins, modules)
- Collection-level metadata (galaxy.yml, requirements.yml)
- Cross-role dependency visualization
- Collection README generation

**v0.6.0 - Project Documentation** (NEW - Not in original)
- Full Ansible project parsing (roles, collections, playbooks)
- Project-level documentation (architecture, inventory, vars)
- Playbook documentation with task flow
- Multi-format project reports

**v1.0.0 - Production Release**
- Complete Ansible documentation solution (Role → Collection → Project)
- Stable API and CLI interface
- Comprehensive test coverage (90%+)
- Production-ready templates and themes
- Complete user documentation

**Post v1.0.0**
- Web UI for interactive browsing
- CI/CD integration templates
- Plugin ecosystem for custom renderers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original [ansible-doctor](https://github.com/thegeeklab/ansible-doctor) by thegeeklab
- [GitHub spec-kit](https://github.com/github/spec-kit) for Specification-Driven Development methodology
- Ansible community for role structure conventions

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/ansible-doctor-enhanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ansible-doctor-enhanced/discussions)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Built with ❤️ following KISS, SMART, and SOLID principles**
