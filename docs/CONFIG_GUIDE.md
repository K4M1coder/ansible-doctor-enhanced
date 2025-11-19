# Configuration Guide

This guide provides comprehensive documentation for configuring `ansible-doctor-enhanced` using `.ansibledoctor.yml` files.

## Quick Start

See the [Configuration section in README.md](../README.md#configuration-file-ansibledoctoryml) for quick examples and common usage patterns.

## Configuration File Format

Configuration files must be named `.ansibledoctor.yml` or `.ansibledoctor.yaml` and use YAML format.

### Complete Configuration Example

```yaml
# Output Settings
output_format: markdown      # Format: markdown, html, or rst
output: README.md            # Output file path (relative or absolute)
output_dir: docs/            # Output directory for recursive mode

# Template Settings
template: custom-template.j2 # Path to custom Jinja2 template
template_dir: ./templates    # Directory containing custom templates

# Processing Options
recursive: false             # Process subdirectories recursively
exclude_patterns:            # Patterns to exclude from processing
  - "*.pyc"
  - "__pycache__"
  - ".git"
  - "test_*"
  - "*.swp"
  - "*.tmp"
```

## Configuration Keys Reference

### `output_format`

**Type**: String (enum)  
**Values**: `markdown`, `html`, `rst`  
**Default**: `markdown`  
**Description**: Output format for generated documentation.

**Example**:
```yaml
output_format: html
```

### `output`

**Type**: String (path)  
**Default**: None (prints to stdout)  
**Description**: Path to output file. Can be relative or absolute. If not specified, output goes to stdout.

**Examples**:
```yaml
# Relative path
output: docs/README.md

# Absolute path (Windows)
output: C:\Projects\my-role\docs\index.html

# Absolute path (Unix)
output: /home/user/roles/my-role/README.md
```

### `output_dir`

**Type**: String (path)  
**Default**: Current directory  
**Description**: Directory for output files when using `--recursive` mode. Each role gets its own output file in this directory.

**Example**:
```yaml
output_dir: documentation/
recursive: true
```

### `template`

**Type**: String (path)  
**Default**: Built-in templates  
**Description**: Path to custom Jinja2 template file. Relative paths are resolved from the config file location.

**Example**:
```yaml
template: templates/custom-markdown.j2
```

### `template_dir`

**Type**: String (path)  
**Default**: Built-in template directory  
**Description**: Directory containing custom templates. Used for template inheritance and includes.

**Example**:
```yaml
template_dir: ./custom-templates
```

### `recursive`

**Type**: Boolean  
**Default**: `false`  
**Description**: When true, processes all subdirectories recursively. Useful for processing multiple roles in a collection.

**Example**:
```yaml
recursive: true
output_dir: docs/
```

### `exclude_patterns`

**Type**: List of strings (glob patterns)  
**Default**: `["*.pyc", "__pycache__", ".git"]`  
**Description**: Glob patterns for files/directories to exclude from processing. Patterns use Python's `fnmatch` syntax.

**Examples**:
```yaml
exclude_patterns:
  - "*.pyc"              # Exclude compiled Python files
  - "__pycache__"        # Exclude Python cache directories
  - ".git"               # Exclude git repository
  - "test_*"             # Exclude test files
  - "*.swp"              # Exclude Vim swap files
  - "node_modules"       # Exclude Node.js dependencies
  - ".terraform"         # Exclude Terraform state
```

## Configuration Priority

Configuration is merged from multiple sources with the following priority (highest to lowest):

1. **CLI Arguments**: Flags passed on command line
2. **Config File**: Settings from `.ansibledoctor.yml`
3. **Defaults**: Built-in default values

**Example**:
```yaml
# .ansibledoctor.yml
output_format: html
output: docs/README.html
```

```bash
# CLI overrides format to markdown (file says html, CLI wins)
ansible-doctor-enhanced generate . --format markdown

# Result: Markdown output to docs/README.html
```

## Config File Discovery

The tool searches for config files in the following order:

1. Current directory (`.ansibledoctor.yml` or `.ansibledoctor.yaml`)
2. Parent directory
3. Grandparent directory
4. Continue up to filesystem root

**Nearest config wins** (like Git's `.gitconfig` behavior).

**Example Directory Structure**:
```
/home/user/projects/
├── .ansibledoctor.yml          # Root config (applies to all roles)
└── ansible-roles/
    ├── role1/
    │   ├── .ansibledoctor.yml  # Role-specific config (overrides root)
    │   ├── meta/
    │   └── tasks/
    └── role2/
        ├── meta/               # No config (uses root config)
        └── tasks/
```

When running from `/home/user/projects/ansible-roles/role1/`, the tool uses `role1/.ansibledoctor.yml`.  
When running from `/home/user/projects/ansible-roles/role2/`, the tool uses `/home/user/projects/.ansibledoctor.yml`.

## Validation

Validate your configuration file before use:

```bash
# Validate config in current directory
ansible-doctor-enhanced config validate

# Validate config in specific directory
ansible-doctor-enhanced config validate --path /path/to/role

# Show effective configuration (merged result)
ansible-doctor-enhanced config show
```

**Validation checks**:
- YAML syntax (indentation, quotes, colons)
- Schema validation (valid keys, value types)
- Value constraints (e.g., `output_format` must be markdown/html/rst)

**Error Examples**:

```yaml
# ❌ Invalid: Unknown format
output_format: json
# Error: Field 'output_format': Input should be 'markdown', 'html', or 'rst'

# ❌ Invalid: Wrong type
recursive: "yes"
# Error: Field 'recursive': Input should be a valid boolean

# ❌ Invalid: YAML syntax
output: README.md
  recursive: true
# Error: YAML Syntax Error: mapping values are not allowed here
# Line 2, Column 13
```

## Migration from Original ansible-doctor

If migrating from the original `ansible-doctor`, note these changes:

### Compatible Settings

These settings work identically:
- `output_format`: Same values (markdown, html, rst)
- `output`: Same behavior for output file path
- `recursive`: Same recursive processing behavior
- `exclude_patterns`: Same pattern matching

### New Settings

These are new in `ansible-doctor-enhanced`:
- `template`: Custom template support (was command-line only)
- `template_dir`: Template directory support
- `output_dir`: Dedicated output directory for recursive mode

### Behavior Changes

1. **Config Discovery**: Now searches parent directories (like Git)
   - Original: Only checked current directory
   - Enhanced: Walks up to filesystem root

2. **Config Priority**: CLI arguments now override config file
   - Original: Config file overrode some CLI args
   - Enhanced: CLI always wins (follows principle of least surprise)

3. **Validation**: Built-in validation command
   - Original: No validation command
   - Enhanced: `config validate` catches errors before generation

### Migration Example

**Original ansible-doctor**:
```bash
# Original workflow
ansible-doctor --format html --output docs/README.html /path/to/role
```

**ansible-doctor-enhanced**:
```yaml
# .ansibledoctor.yml (in role or parent directory)
output_format: html
output: docs/README.html
```

```bash
# Enhanced workflow (shorter, reusable config)
ansible-doctor-enhanced generate /path/to/role

# Validation before generation
ansible-doctor-enhanced config validate
ansible-doctor-enhanced generate .

# Watch mode for continuous updates
ansible-doctor-enhanced watch .
```

## Best Practices

### 1. Use Parent Directory Configs

Place a shared config in your roles directory:

```
ansible-roles/
├── .ansibledoctor.yml    # Shared config for all roles
├── role1/
├── role2/
└── role3/
```

Override in specific roles when needed:

```
ansible-roles/
├── .ansibledoctor.yml    # Shared: markdown output
├── role1/
│   └── .ansibledoctor.yml  # Override: HTML output for this role
├── role2/
└── role3/
```

### 2. Validate Before Committing

Add validation to your CI pipeline:

```bash
# In CI/CD script
ansible-doctor-enhanced config validate
ansible-doctor-enhanced generate . --output README.md
git diff --exit-code README.md  # Fail if docs are out of date
```

### 3. Use Exclude Patterns

Keep your config clean by excluding test and generated files:

```yaml
exclude_patterns:
  - "test_*"
  - "*.pyc"
  - "__pycache__"
  - ".terraform"
  - "*.swp"
  - "node_modules"
```

### 4. Watch Mode for Development

Use watch mode during role development:

```bash
# Auto-regenerate on every save
ansible-doctor-enhanced watch . --output README.md
```

### 5. Version Control Your Configs

Commit `.ansibledoctor.yml` to your repository:

```bash
git add .ansibledoctor.yml
git commit -m "Add ansible-doctor-enhanced configuration"
```

## Troubleshooting

### Config Not Found

**Problem**: "No config file found" message

**Solutions**:
- Check file name: Must be `.ansibledoctor.yml` or `.ansibledoctor.yaml`
- Check file location: Should be in role directory or parent
- Use absolute path: `ansible-doctor-enhanced config validate --path /full/path/to/role`

### YAML Syntax Errors

**Problem**: "YAML Syntax Error: ..." message

**Solutions**:
- Check indentation (use spaces, not tabs)
- Check quotes around strings with special characters
- Validate YAML online: https://www.yamllint.com/

**Example**:
```yaml
# ❌ Wrong (mixing tabs and spaces)
output_format:  markdown  # tab used here

# ✅ Correct (consistent spaces)
output_format: markdown   # 2 spaces
```

### Schema Validation Errors

**Problem**: "Schema Validation Error: Field '...' ..." message

**Solutions**:
- Check field names (case-sensitive)
- Check value types (string, boolean, list)
- Check value constraints (e.g., output_format values)

**Example**:
```yaml
# ❌ Wrong field name
format: markdown
# Error: Unknown field 'format'

# ✅ Correct field name
output_format: markdown
```

### Path Resolution Issues

**Problem**: Output file created in unexpected location

**Solutions**:
- Use absolute paths for clarity
- Check current working directory when running command
- Use `config show` to see resolved paths

**Example**:
```bash
# See where output will be written
ansible-doctor-enhanced config show
# Look for "output: /full/absolute/path/to/README.md"
```

## Advanced Usage

### Multi-Environment Configs

Use different configs for different environments:

```bash
# Development
ansible-doctor-enhanced generate . --format markdown

# Production (override with HTML)
ansible-doctor-enhanced generate . --format html --output docs/index.html

# CI/CD (validate + generate)
ansible-doctor-enhanced config validate && \
ansible-doctor-enhanced generate . --output README.md
```

### Custom Templates with Configs

```yaml
# .ansibledoctor.yml
output_format: html
template: templates/company-theme.j2
template_dir: templates/
exclude_patterns:
  - "templates/"  # Don't process template directory as role content
```

### Recursive Processing with Configs

```yaml
# Parent .ansibledoctor.yml for processing all roles
output_format: markdown
recursive: true
output_dir: documentation/
exclude_patterns:
  - ".git"
  - "*.pyc"
  - "__pycache__"
  - "venv/"
```

```bash
# Process all roles in collection
ansible-doctor-enhanced generate ./roles/
# Creates documentation/role1/README.md, documentation/role2/README.md, etc.
```

## Related Documentation

- [README.md](../README.md): Quick start and usage examples
- [CHANGELOG.md](../CHANGELOG.md): Version history and changes
- [CONTRIBUTING.md](../CONTRIBUTING.md): Development and contribution guidelines

## See Also

- Configuration Validation: `ansible-doctor-enhanced config validate --help`
- Configuration Display: `ansible-doctor-enhanced config show --help`
- Watch Mode: `ansible-doctor-enhanced watch --help`
- Generation: `ansible-doctor-enhanced generate --help`
