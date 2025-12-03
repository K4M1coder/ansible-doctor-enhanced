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

## Next Steps

1. Set up VS Code integration with exported schemas
2. Add config validation to CI/CD pipeline
3. Generate schema documentation for team
4. Configure pre-commit hooks for validation
5. Monitor validation performance with cache metrics
