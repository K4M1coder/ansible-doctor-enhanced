# Schema Validation Guide

**Spec 012 - Phase 3: Configuration Validation**

## Overview

Ansible-doctor now provides JSON Schema validation for configuration files, enabling:
- **IDE Autocomplete**: JSON Schema support in VS Code, IntelliJ, and other IDEs
- **Validation**: Catch configuration errors before running documentation generation
- **Error Messages**: Detailed error messages with line numbers and suggestions

## Quick Start

### Validate a Configuration File

```bash
# Basic validation
ansible-doctor schema validate .ansibledoctor.yml

# Strict mode (warnings treated as errors)
ansible-doctor schema validate .ansibledoctor.yml --strict

# Verbose output with suggestions
ansible-doctor schema validate .ansibledoctor.yml --verbose
```

### Example Output

#### Valid Configuration

```
Validation Report: .ansibledoctor.yml
================================================================================
Status: VALID
Errors: 0
Warnings: 0
```

#### Invalid Configuration

```
Validation Report: .ansibledoctor.yml
================================================================================
Status: INVALID
Errors: 2
Warnings: 1

ERRORS:
----------
ERROR: enum - 'pdf' is not one of ['markdown', 'html', 'rst']
  Path: output_format
  Suggestion: Use one of: 'markdown', 'html', 'rst'

ERROR: type - True is not of type 'string'
  Path: template
  Suggestion: Ensure the value is a string (text)

WARNINGS:
----------
WARNING: additionalProperties - Additional properties are not allowed ('unknown_field' was unexpected)
  Path: unknown_field
  Suggestion: Remove this property or check for typos
```

## Configuration Schema

### Supported Properties

The JSON Schema validates all `.ansibledoctor.yml` properties:

```yaml
# Output settings
output_format: markdown  # enum: markdown, html, rst
output_dir: docs        # string: output directory path

# Generator settings
verbose: false          # boolean: enable verbose logging
template: null          # string: custom template path (optional)
exclude_tags: []        # array: tags to exclude (optional)

# Index settings (Spec 011)
include_index: true     # boolean: generate index pages
index_style: tree       # enum: tree, flat
index_format: table     # enum: table, list, nested-table
index_depth: 3          # integer: max depth (1-10)
nested_depth: 2         # integer: nested table depth (1-5)
filter: []              # array: filter expressions (optional)
```

### Validation Rules

1. **Required Properties**: None (all properties are optional with defaults)
2. **Type Checking**: Validates correct types (string, boolean, integer, array)
3. **Enum Values**: Validates allowed values for output_format, index_style, index_format
4. **Range Validation**: Ensures index_depth (1-10) and nested_depth (1-5) are in valid ranges
5. **Additional Properties**: Warns about unknown properties (typos)

## CLI Commands

### validate

Validate a configuration file against JSON Schema.

```bash
ansible-doctor schema validate <config_file> [OPTIONS]
```

**Options:**
- `--strict`: Treat warnings as errors (exit code 1)
- `--verbose`: Show detailed error messages with suggestions

**Exit Codes:**
- `0`: Validation successful
- `1`: Validation failed (errors or warnings with --strict)

**Examples:**

```bash
# Validate with default settings
ansible-doctor schema validate .ansibledoctor.yml

# Strict mode - fail on warnings
ansible-doctor schema validate .ansibledoctor.yml --strict

# Verbose output
ansible-doctor schema validate .ansibledoctor.yml --verbose

# Validate custom config
ansible-doctor schema validate custom-config.yml
```

### export (Coming in Phase 4)

Export JSON Schema for ansible-doctor configuration.

```bash
ansible-doctor schema export config [OPTIONS]
```

**Options:**
- `--format json|openapi`: Output format (default: json)
- `--output FILE`: Write schema to file

### convert (Coming in Phase 5)

Convert between data formats (YAML, JSON, XML).

```bash
ansible-doctor schema convert <input_file> --to <format> [OPTIONS]
```

### docs (Coming in Phase 7)

Generate human-readable schema documentation.

```bash
ansible-doctor schema docs <schema_type> [OPTIONS]
```

## IDE Integration

### VS Code

Add JSON Schema reference to your `.ansibledoctor.yml`:

```yaml
# yaml-language-server: $schema=https://example.com/schema/ansibledoctor.json

output_format: markdown
output_dir: docs
```

### IntelliJ IDEA

1. Go to **Settings** → **Languages & Frameworks** → **Schemas and DTDs** → **JSON Schema Mappings**
2. Add new mapping:
   - **Name**: ansible-doctor config
   - **Schema file**: `path/to/ansibledoctor-schema.json`
   - **File pattern**: `.ansibledoctor.yml`

## Validation Models

### ValidationError

Represents a single validation error or warning.

**Properties:**
- `path`: JSON path to the error location
- `message`: Error message
- `validator`: Validator that failed (e.g., "enum", "type", "required")
- `severity`: ERROR, WARNING, or INFO
- `expected`: Expected value or type
- `actual`: Actual value found
- `suggestion`: Actionable suggestion (optional)
- `line_number`: Line number in file (optional)
- `column_number`: Column number in file (optional)

### ValidationResult

Aggregates validation errors and warnings.

**Properties:**
- `is_valid`: Boolean indicating if validation passed
- `errors`: List of ValidationError objects with severity ERROR
- `warnings`: List of ValidationError objects with severity WARNING
- `file_path`: Path to validated file

**Methods:**
- `error_count`: Number of errors
- `warning_count`: Number of warnings
- `format_report(verbose=False)`: Format validation report as string
- `raise_if_invalid(strict=False)`: Raise exception if validation failed

## Common Errors and Solutions

### Enum Validation Error

**Error:**
```
ERROR: enum - 'pdf' is not one of ['markdown', 'html', 'rst']
  Path: output_format
```

**Solution:**
Use one of the allowed values: `markdown`, `html`, or `rst`

```yaml
output_format: markdown  # Valid values: markdown, html, rst
```

### Type Mismatch Error

**Error:**
```
ERROR: type - True is not of type 'string'
  Path: template
```

**Solution:**
Ensure the value is the correct type:

```yaml
template: "custom-template.j2"  # Must be a string
```

### Unknown Property Warning

**Warning:**
```
WARNING: additionalProperties - Additional properties are not allowed ('ouput_dir' was unexpected)
  Path: ouput_dir
```

**Solution:**
Check for typos in property names:

```yaml
output_dir: docs  # Correct spelling
# ouput_dir: docs  # Typo: "ouput" instead of "output"
```

### Range Validation Error

**Error:**
```
ERROR: maximum - 15 is greater than the maximum of 10
  Path: index_depth
```

**Solution:**
Use a value within the allowed range:

```yaml
index_depth: 5  # Valid range: 1-10
```

## Programmatic Usage

### Using ConfigurationValidator

```python
from ansibledoctor.validation import ConfigurationValidator
from pathlib import Path

# Create validator
validator = ConfigurationValidator()

# Validate file
config_file = Path(".ansibledoctor.yml")
result = validator.validate_file(config_file, strict=False)

# Check result
if result.is_valid:
    print(f"✓ Configuration is valid")
else:
    print(f"✗ Configuration has {result.error_count} errors")
    
    # Print report
    print(result.format_report(verbose=True))
    
    # Or access errors directly
    for error in result.errors:
        print(f"ERROR at {error.path}: {error.message}")
        if error.suggestion:
            print(f"  Suggestion: {error.suggestion}")
```

### Using SchemaValidator (Generic)

```python
from ansibledoctor.validation import SchemaValidator
from pathlib import Path

# Define custom JSON Schema
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"}
    },
    "required": ["name", "version"]
}

# Create validator
validator = SchemaValidator(schema)

# Validate data
data = {"name": "my-role", "version": "1.0.0"}
result = validator.validate(data)

# Check result
if result.is_valid:
    print("✓ Valid")
else:
    print(result.format_report())
```

## Next Steps

- **Phase 4**: Schema export with `ansible-doctor schema export`
- **Phase 5**: Format conversion with `ansible-doctor schema convert`
- **Phase 6**: Data model validation for roles and collections
- **Phase 7**: Schema documentation generation with `ansible-doctor schema docs`

## Testing

Run schema validation tests:

```bash
# Unit tests
pytest tests/unit/test_schema_models.py -v

# Integration tests
pytest tests/integration/test_config_validator.py -v
pytest tests/integration/test_schema_cli.py -v

# All schema tests
pytest tests/ -k schema -v
```

## Troubleshooting

### jsonschema Module Not Found

Ensure jsonschema is installed:

```bash
poetry install
# or
pip install jsonschema>=4.0
```

### Validation Always Fails

Check that the config file is valid YAML:

```bash
# Use a YAML linter
yamllint .ansibledoctor.yml

# Or check with Python
python -c "import yaml; print(yaml.safe_load(open('.ansibledoctor.yml')))"
```

### File Not Found Error

Ensure the config file path is correct:

```bash
# Check file exists
ls -la .ansibledoctor.yml

# Use absolute path
ansible-doctor schema validate /path/to/.ansibledoctor.yml
```

## See Also

- [Configuration Guide](CONFIG_GUIDE.md) - Complete configuration reference
- [Error Codes](ERROR_CODES.md) - Error code reference
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema) - JSON Schema specification
