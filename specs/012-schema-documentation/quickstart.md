# Quickstart Guide: Schema Documentation & Validation

**Date**: 2025-12-03  
**Feature**: Spec 012 - Schema Documentation & Validation

This guide demonstrates how to validate configurations, export schemas, convert formats, and integrate with IDEs.

---

## Basic Usage

### Validate Configuration File

```bash
# Validate .ansibledoctor.yml
ansible-doctor schema validate .ansibledoctor.yml

# Output (valid):
# ✅ Validation passed
# Validation time: 2.15ms

# Output (invalid):
# ❌ Validation failed with 2 error(s)
#
# Errors:
#   - Line 5: $.output_format: must be one of: markdown, html, rst (got: "pdf")
#     Suggestion: Use --output-format markdown or edit .ansibledoctor.yml
#   - Line 8: $.languages.default: must be string (got: null)
#     Suggestion: Set languages.default to "en", "fr", or "de"
#
# Validation time: 2.50ms
```

### Strict Mode (Warnings as Errors)

```bash
# Treat warnings as errors
ansible-doctor schema validate .ansibledoctor.yml --strict

# Output:
# ❌ Validation failed with 1 error(s)
#
# Errors:
#   - $.unknown_field: unknown property (not in schema)
#     Suggestion: Remove unknown_field or check documentation
```

### Custom Schema

```bash
# Validate against custom schema
ansible-doctor schema validate my_config.yml --schema custom_schema.json
```

---

## Schema Export

### Export for VS Code

```bash
# Export config schema for IDE autocomplete
ansible-doctor schema export config --format json-schema --output .vscode/ansibledoctor.schema.json

# Output:
# Exported schema: .vscode/ansibledoctor.schema.json (5.2 KB)
```

### VS Code Integration

Create `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    ".vscode/ansibledoctor.schema.json": ".ansibledoctor.yml"
  }
}
```

Now VS Code provides:
- ✅ Autocomplete for config properties
- ✅ Inline validation errors
- ✅ Hover documentation
- ✅ Enum value suggestions

### Export All Schemas

```bash
# Export schemas for all data models
ansible-doctor schema export all --format json-schema --output schemas/

# Output:
# Exported schemas to schemas/:
#   - config.schema.json (5.2 KB)
#   - role.schema.json (8.1 KB)
#   - collection.schema.json (12.3 KB)
#   - playbook.schema.json (6.7 KB)
#   Total: 4 schemas (32.3 KB)
```

### OpenAPI Export

```bash
# Export as OpenAPI spec for API documentation
ansible-doctor schema export all --format openapi --output docs/api-schema.yaml

# View in Swagger UI
swagger-ui docs/api-schema.yaml
```

### Pretty-Printed JSON Schema

```bash
# Export with pretty formatting
ansible-doctor schema export config --pretty

# Output (stdout):
# {
#   "$schema": "https://json-schema.org/draft/2020-12/schema",
#   "$id": "https://ansibledoctor.com/schemas/config.json",
#   "title": "AnsibleDoctorConfig",
#   "type": "object",
#   "properties": {
#     "output_format": {
#       "type": "string",
#       "enum": ["markdown", "html", "rst"],
#       "default": "markdown"
#     }
#   }
# }
```

---

## Format Conversion

### YAML to JSON

```bash
# Convert YAML config to JSON
ansible-doctor convert .ansibledoctor.yml --to json --output config.json

# Output:
# Converted yaml → json
# Duration: 1.20ms
# Size: 512 → 384 bytes
```

### JSON to YAML

```bash
# Convert JSON to human-readable YAML
ansible-doctor convert config.json --to yaml --output config.yml

# Output:
# Converted json → yaml
# Duration: 0.80ms
# Size: 384 → 512 bytes
```

### With Data Loss Warnings

```bash
# Convert YAML with anchors to JSON
ansible-doctor convert complex.yml --to json

# Output:
# Converted yaml → json
# Duration: 1.50ms
# Size: 1024 → 768 bytes
#
# ⚠️ 2 warning(s):
#   - YAML anchor &defaults lost during conversion
#   - YAML alias *defaults replaced with copy
```

### Pretty-Print JSON

```bash
# Pretty-print minified JSON
ansible-doctor convert minified.json --to json --pretty --output pretty.json
```

### Convert to XML

```bash
# Convert YAML to XML (for tool integration)
ansible-doctor convert role_metadata.yml --to xml --output role_metadata.xml

# Output XML:
# <?xml version="1.0" encoding="UTF-8"?>
# <root>
#   <name>webserver</name>
#   <description>Configure web servers</description>
#   <tags>
#     <item>web</item>
#     <item>nginx</item>
#   </tags>
# </root>
```

### Auto-Detect Format

```bash
# Auto-detect source format from extension
ansible-doctor convert config.yml --to json

# Infer target format from output extension
ansible-doctor convert config.json --output config.yml
```

---

## Schema Documentation

### Generate Markdown Documentation

```bash
# Generate schema docs from config schema
ansible-doctor schema docs config --format markdown --output docs/CONFIG_SCHEMA.md

# Output file:
# # Configuration Schema
#
# ## Properties
#
# ### output_format
#
# - **Type**: string
# - **Required**: yes
# - **Default**: "markdown"
# - **Allowed values**: "markdown", "html", "rst"
# - **Description**: Documentation output format
#
# **Example**:
# ```yaml
# output_format: markdown
# ```
```

### Generate HTML Documentation

```bash
# Generate HTML docs with styling
ansible-doctor schema docs role --format html --output docs/role_schema.html
```

### Generate RST Documentation

```bash
# Generate ReStructuredText for Sphinx
ansible-doctor schema docs collection --format rst --output docs/collection_schema.rst
```

---

## Python API

### Example 1: Validate Config Programmatically

```python
from pathlib import Path
from ansibledoctor.validation import ConfigurationValidator
from ansibledoctor.utils import SchemaCache

# Initialize validator
validator = ConfigurationValidator(schema_cache=SchemaCache())

# Validate config file
result = validator.validate_config(Path(".ansibledoctor.yml"))

if result.is_valid:
    print("✅ Configuration is valid")
else:
    print(result.format_report())
    for error in result.errors:
        print(f"  Path: {error.path}")
        print(f"  Message: {error.message}")
        print(f"  Suggestion: {error.suggestion}")
```

### Example 2: Convert Formats

```python
from ansibledoctor.serialization import FormatConverter, FormatType

converter = FormatConverter()

# Convert YAML to JSON
result = converter.convert_file(
    input_path=Path("config.yml"),
    output_path=Path("config.json"),
    target_format=FormatType.JSON,
)

if result.has_data_loss:
    print(f"⚠️ Warnings: {result.warnings}")

print(result.output)
```

### Example 3: Export Schema

```python
from ansibledoctor.serialization import SchemaExporter
from ansibledoctor.config import ConfigModel

exporter = SchemaExporter()

# Export JSON Schema
schema_json = exporter.export_json_schema(
    model=ConfigModel,
    output_path=Path(".vscode/ansibledoctor.schema.json"),
)

print(f"Exported schema to .vscode/ansibledoctor.schema.json")
```

### Example 4: Generate Schema Documentation

```python
from ansibledoctor.serialization import SchemaDocumenter
from ansibledoctor.models import SchemaDefinition

documenter = SchemaDocumenter()

# Generate Markdown docs
docs = documenter.document_model(
    model=ConfigModel,
    format="markdown",
)

with open("docs/CONFIG_SCHEMA.md", "w") as f:
    f.write(docs)
```

---

## Advanced Usage

### Migrate Configuration

```python
from ansibledoctor.validation import ConfigurationValidator

validator = ConfigurationValidator(schema_cache=SchemaCache())

# Migrate config to latest schema (handles deprecated options)
migrated_path = validator.migrate_config(
    config_path=Path(".ansibledoctor.yml"),
    backup=True,  # Create backup before migration
)

print(f"Config migrated: {migrated_path}")
```

### Round-Trip Test

```python
from ansibledoctor.serialization import FormatConverter, FormatType

converter = FormatConverter()

# Test YAML → JSON → YAML preserves data
data = {"key": "value", "list": [1, 2, 3]}

success = converter.round_trip_test(data, FormatType.YAML)

if success:
    print("✅ Round-trip test passed (no data loss)")
else:
    print("❌ Round-trip test failed (data loss detected)")
```

### Cache Performance Monitoring

```python
from ansibledoctor.utils import SchemaCache

cache = SchemaCache(max_size=100)

# Use cache for validation
# ... perform validations ...

# Check cache performance
print(f"Cache hit rate: {cache.hit_rate:.2%}")
print(f"Cache size: {len(cache._cache)}/{cache.max_size}")
print(f"Hits: {cache.hit_count}, Misses: {cache.miss_count}")
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Validate Configuration

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install ansible-doctor
        run: pip install ansible-doctor-enhanced
      
      - name: Validate config
        run: ansible-doctor schema validate .ansibledoctor.yml --strict
      
      - name: Export schemas (for artifact)
        run: ansible-doctor schema export all --output schemas/
      
      - name: Upload schemas
        uses: actions/upload-artifact@v3
        with:
          name: schemas
          path: schemas/
```

### GitLab CI

```yaml
validate-config:
  stage: test
  script:
    - pip install ansible-doctor-enhanced
    - ansible-doctor schema validate .ansibledoctor.yml --strict
  only:
    changes:
      - .ansibledoctor.yml
```

### Pre-commit Hook

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-config
        name: Validate ansible-doctor config
        entry: ansible-doctor schema validate
        language: system
        files: \.ansibledoctor\.yml$
        pass_filenames: true
```

---

## IDE Integration

### VS Code Setup

1. **Export Schema**:
```bash
ansible-doctor schema export config --output .vscode/ansibledoctor.schema.json
```

2. **Configure YAML Extension** (`.vscode/settings.json`):
```json
{
  "yaml.schemas": {
    ".vscode/ansibledoctor.schema.json": ".ansibledoctor.yml"
  },
  "yaml.validate": true,
  "yaml.completion": true
}
```

3. **Enable IntelliSense**:
   - Autocomplete for properties
   - Inline error messages
   - Hover documentation
   - Enum value suggestions

### IntelliJ IDEA / PyCharm

1. **Export Schema**:
```bash
ansible-doctor schema export config --output schemas/config.schema.json
```

2. **Configure JSON Schema** (Settings → JSON Schemas):
   - Add new schema
   - Schema file: `schemas/config.schema.json`
   - File path pattern: `.ansibledoctor.yml`

### Vim / Neovim (with coc.nvim)

`coc-settings.json`:
```json
{
  "json.schemas": [
    {
      "fileMatch": [".ansibledoctor.yml"],
      "url": "file://${workspaceFolder}/.vscode/ansibledoctor.schema.json"
    }
  ]
}
```

---

## Best Practices

### 1. Always Validate in CI

Add config validation to CI pipeline to catch errors early:

```bash
ansible-doctor schema validate .ansibledoctor.yml --strict
```

### 2. Export Schemas for Team

Share schemas with team for consistent IDE experience:

```bash
# Export to version control
ansible-doctor schema export config --output .vscode/ansibledoctor.schema.json
git add .vscode/ansibledoctor.schema.json
```

### 3. Use Strict Mode in Production

Enable strict validation to catch configuration issues:

```bash
# In production deployment scripts
ansible-doctor schema validate $CONFIG_FILE --strict || exit 1
```

### 4. Document Schema Changes

Generate schema docs after model changes:

```bash
ansible-doctor schema docs config --output docs/CONFIG_SCHEMA.md
```

### 5. Test Format Conversions

Verify data fidelity with round-trip tests:

```python
converter.round_trip_test(data, FormatType.YAML)
```

---

## Troubleshooting

### Issue: Validation Errors Not Helpful

**Problem**: Error messages don't include line numbers

**Solution**: Ensure YAML files are parsed with line number tracking (ruamel.yaml):

```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

with open(file_path) as f:
    data = yaml.load(f)  # Preserves line numbers
```

### Issue: Schema Export Missing Properties

**Problem**: Some model fields not in exported schema

**Solution**: Add descriptions to pydantic fields:

```python
class Config(BaseModel):
    output_format: str = Field(
        default="markdown",
        description="Documentation output format",
        examples=["markdown", "html", "rst"],
    )
```

### Issue: Format Conversion Data Loss

**Problem**: YAML anchors lost when converting to JSON

**Solution**: Use warnings to detect data loss:

```python
result = converter.convert(...)
if result.has_data_loss:
    for warning in result.warnings:
        logger.warning(warning)
```

### Issue: Slow Validation

**Problem**: Validation takes >100ms

**Solution**: Use schema cache:

```python
cache = SchemaCache(max_size=100)
validator = ConfigurationValidator(schema_cache=cache)

# First validation: ~5ms (compile schema)
# Subsequent: ~1ms (use cached validator)
```

### Issue: Unknown Properties Warning

**Problem**: Config has properties not in schema

**Solution**: Either remove unknown properties or update schema:

```yaml
# Option 1: Remove unknown property
# unknown_field: value  # Remove this line

# Option 2: Update schema to allow additional properties
```

---

## Examples Repository

See `tests/fixtures/` for complete examples:

- `configs/valid_config.yml` - Valid configuration example
- `configs/invalid_config.yml` - Common validation errors
- `schemas/config_schema.json` - Exported config schema
- `conversions/sample.yml` - Format conversion examples

---

## Complete End-to-End Examples

### Example 1: New Project Setup with Schema Validation

**Scenario**: Setting up a new Ansible project with validation and autocomplete.

**Steps**:

```bash
# 1. Create new project structure
mkdir my-ansible-project
cd my-ansible-project
mkdir -p roles/webserver/{defaults,meta,tasks,templates}

# 2. Create initial config
cat > .ansibledoctor.yml <<EOF
output_format: markdown
recursive: true
output_dir: docs/
template_dir: .ansibledoctor/templates
languages:
  default: en
  enabled: [en, fr]
EOF

# 3. Export schema for IDE
python -m ansibledoctor schema export config --output config-schema.json

# 4. Configure VS Code
mkdir -p .vscode
cat > .vscode/settings.json <<EOF
{
  "yaml.schemas": {
    "./config-schema.json": ".ansibledoctor.yml"
  }
}
EOF

# 5. Validate config
python -m ansibledoctor schema validate .ansibledoctor.yml --strict

# 6. Generate documentation
python -m ansibledoctor role generate ./roles/webserver
```

**Result**:
- ✅ Schema validation in CI/CD
- ✅ IDE autocomplete for .ansibledoctor.yml
- ✅ Type-safe configuration
- ✅ Professional documentation

---

### Example 2: CI/CD Pipeline Integration

**Scenario**: Add schema validation to GitHub Actions workflow.

**`.github/workflows/validate.yml`**:

```yaml
name: Validate Configuration

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install ansible-doctor
        run: |
          pip install poetry
          poetry install
      
      - name: Validate Configuration
        run: |
          poetry run python -m ansibledoctor schema validate .ansibledoctor.yml --strict --verbose
      
      - name: Validate Role Data
        run: |
          for role in roles/*; do
            if [ -f "$role/meta/main.yml" ]; then
              echo "Validating $role..."
              poetry run python -m ansibledoctor schema validate-model role "$role/meta/main.yml" --strict-validation
            fi
          done
      
      - name: Export Schema (cache for next run)
        run: |
          poetry run python -m ansibledoctor schema export config --output config-schema.json
      
      - name: Upload Schema Artifact
        uses: actions/upload-artifact@v3
        with:
          name: config-schema
          path: config-schema.json
```

**Result**:
- ✅ Automated validation on every commit
- ✅ Strict mode catches all issues
- ✅ Fail fast on configuration errors
- ✅ Schema artifact for documentation

---

### Example 3: Multi-Format Documentation Pipeline

**Scenario**: Generate documentation in multiple formats for different audiences.

**`scripts/generate_docs.sh`**:

```bash
#!/bin/bash
set -e

PROJECT_DIR="."
DOCS_DIR="docs"

echo "=== Ansible Doctor Documentation Pipeline ==="

# 1. Validate all configs
echo "Step 1: Validating configurations..."
python -m ansibledoctor schema validate .ansibledoctor.yml --strict

# 2. Generate schema documentation
echo "Step 2: Generating schema documentation..."
python -m ansibledoctor schema docs config --output "$DOCS_DIR/schema/config-schema.md"

# 3. Convert config to multiple formats
echo "Step 3: Converting config to formats..."
python -m ansibledoctor schema convert .ansibledoctor.yml --to json --output "$DOCS_DIR/config.json" --pretty
python -m ansibledoctor schema convert .ansibledoctor.yml --to xml --output "$DOCS_DIR/config.xml"
python -m ansibledoctor schema convert .ansibledoctor.yml --to mermaid --output "$DOCS_DIR/diagrams/config-structure.mmd"

# 4. Generate project documentation
echo "Step 4: Generating project docs..."
python -m ansibledoctor project generate "$PROJECT_DIR" --languages en,fr --output "$DOCS_DIR"

# 5. Generate collection documentation
echo "Step 5: Generating collection docs..."
for collection in collections/ansible_collections/*/*; do
  if [ -f "$collection/galaxy.yml" ]; then
    echo "  - Processing $(basename $(dirname $collection)).$(basename $collection)"
    python -m ansibledoctor collection generate "$collection" --format html --include-index
  fi
done

# 6. Generate role documentation
echo "Step 6: Generating role docs..."
for role in roles/*; do
  if [ -d "$role/tasks" ]; then
    echo "  - Processing $(basename $role)"
    python -m ansibledoctor role generate "$role"
  fi
done

echo "=== Documentation generation complete ==="
echo "Output directory: $DOCS_DIR/"
```

**Usage**:

```bash
chmod +x scripts/generate_docs.sh
./scripts/generate_docs.sh
```

**Result**:
- ✅ Markdown for developers
- ✅ HTML for stakeholders
- ✅ JSON/XML for integrations
- ✅ Mermaid diagrams for architecture
- ✅ Multi-language support

---

### Example 4: Pre-commit Hook for Validation

**Scenario**: Prevent invalid configs from being committed.

**`.pre-commit-config.yaml`**:

```yaml
# See https://pre-commit.com for more information
repos:
  - repo: local
    hooks:
      - id: validate-ansible-doctor-config
        name: Validate ansible-doctor config
        entry: poetry run python -m ansibledoctor schema validate
        language: system
        files: \.ansibledoctor\.yml$
        pass_filenames: true
        args: ['--strict']
      
      - id: validate-role-metadata
        name: Validate role metadata
        entry: bash -c 'for f in "$@"; do poetry run python -m ansibledoctor schema validate-model role "$f" --strict-validation; done'
        language: system
        files: roles/.*/meta/main\.yml$
        pass_filenames: true
      
      - id: validate-collection-metadata
        name: Validate collection metadata
        entry: poetry run python -m ansibledoctor schema validate-model collection
        language: system
        files: galaxy\.yml$
        pass_filenames: true
```

**Setup**:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

**Result**:
- ✅ Automatic validation before commit
- ✅ Prevents invalid configs in repo
- ✅ Fast feedback loop
- ✅ Team-wide consistency

---

### Example 5: Custom Validation Script

**Scenario**: Validate all project files in one script.

**`scripts/validate_all.py`**:

```python
#!/usr/bin/env python3
"""Validate all Ansible project configurations."""

import sys
from pathlib import Path
from ansibledoctor.validation import ConfigurationValidator, DataModelValidator

def main():
    project_root = Path(".")
    errors = []
    
    # 1. Validate main config
    config_file = project_root / ".ansibledoctor.yml"
    if config_file.exists():
        print(f"Validating {config_file}...")
        validator = ConfigurationValidator()
        result = validator.validate_file(str(config_file), strict=True)
        if not result.is_valid:
            errors.append(f"{config_file}: {result.format_report()}")
    
    # 2. Validate all roles
    roles_dir = project_root / "roles"
    if roles_dir.exists():
        for role_dir in roles_dir.iterdir():
            meta_file = role_dir / "meta" / "main.yml"
            if meta_file.exists():
                print(f"Validating {meta_file}...")
                validator = DataModelValidator()
                result = validator.validate_role(str(meta_file), strict=True)
                if not result.is_valid:
                    errors.append(f"{meta_file}: {result.format_report()}")
    
    # 3. Validate all collections
    collections_dir = project_root / "collections" / "ansible_collections"
    if collections_dir.exists():
        for namespace in collections_dir.iterdir():
            for collection in namespace.iterdir():
                galaxy_file = collection / "galaxy.yml"
                if galaxy_file.exists():
                    print(f"Validating {galaxy_file}...")
                    validator = DataModelValidator()
                    result = validator.validate_collection(str(galaxy_file), strict=True)
                    if not result.is_valid:
                        errors.append(f"{galaxy_file}: {result.format_report()}")
    
    # Report results
    if errors:
        print("\n❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ All validations passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Usage**:

```bash
chmod +x scripts/validate_all.py
python scripts/validate_all.py
```

**Result**:
- ✅ Single script validates everything
- ✅ Clear error reporting
- ✅ Exit code for CI/CD
- ✅ Extensible for custom checks

---

### Example 6: IDE Integration Complete Setup

**Scenario**: Full IDE setup with autocomplete, validation, and documentation.

**For VS Code**:

```bash
# 1. Export all schemas
python -m ansibledoctor schema export config --output schemas/config-schema.json

# 2. Create VS Code settings
cat > .vscode/settings.json <<EOF
{
  "yaml.schemas": {
    "./schemas/config-schema.json": [
      ".ansibledoctor.yml",
      ".ansibledoctor.yaml"
    ]
  },
  "yaml.validate": true,
  "yaml.completion": true,
  "yaml.hover": true,
  "files.associations": {
    ".ansibledoctor.yml": "yaml",
    ".ansibledoctor.yaml": "yaml"
  }
}
EOF

# 3. Install VS Code extension
code --install-extension redhat.vscode-yaml
```

**For IntelliJ IDEA / PyCharm**:

```bash
# 1. Export schema
python -m ansibledoctor schema export config --output schemas/config-schema.json

# 2. Configure in IDE:
# Settings → Languages & Frameworks → Schemas and DTDs → JSON Schema Mappings
# - Schema file: schemas/config-schema.json
# - Schema version: JSON Schema version 7
# - File path pattern: .ansibledoctor.yml
```

**Result**:
- ✅ Autocomplete for all properties
- ✅ Real-time validation
- ✅ Hover documentation
- ✅ Enum value dropdowns
- ✅ Error highlighting with suggestions

---

### Example 7: Performance Benchmarking

**Scenario**: Measure and optimize validation performance.

**`scripts/benchmark_validation.py`**:

```python
#!/usr/bin/env python3
"""Benchmark schema validation performance."""

import time
from pathlib import Path
from ansibledoctor.validation import ConfigurationValidator

def benchmark(iterations: int = 100):
    validator = ConfigurationValidator()
    config_file = Path(".ansibledoctor.yml")
    
    # Warmup
    for _ in range(10):
        validator.validate_file(str(config_file), strict=False)
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(iterations):
        validator.validate_file(str(config_file), strict=False)
    end = time.perf_counter()
    
    total_ms = (end - start) * 1000
    avg_ms = total_ms / iterations
    
    print(f"Validation Performance Benchmark")
    print(f"================================")
    print(f"Iterations: {iterations}")
    print(f"Total time: {total_ms:.2f}ms")
    print(f"Average: {avg_ms:.2f}ms per validation")
    print(f"Throughput: {1000 / avg_ms:.0f} validations/second")

if __name__ == "__main__":
    benchmark()
```

**Expected Output**:
```
Validation Performance Benchmark
================================
Iterations: 100
Total time: 215.34ms
Average: 2.15ms per validation
Throughput: 465 validations/second
```

**Result**:
- ✅ Sub-10ms validation for typical configs
- ✅ Performance monitoring
- ✅ Identify bottlenecks
- ✅ Validate performance requirements

---

## Next Steps

1. Set up VS Code integration with exported schemas
2. Add config validation to CI/CD pipeline
3. Generate schema documentation for team
4. Configure pre-commit hooks for validation
5. Monitor validation performance with cache metrics
6. Create custom validation scripts for your workflow
7. Integrate with your documentation pipeline
