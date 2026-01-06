# IDE Integration Examples

This directory contains examples for integrating ansible-doctor schema validation with various IDEs.

## VS Code Integration

VS Code can provide autocomplete and validation for `.ansibledoctor.yml` configuration files using JSON Schema.

### Setup Steps

1. **Export the configuration schema:**

```bash
ansible-doctor schema export config --output config-schema.json
```

2. **Place the schema file in your project root** or a `.vscode/` directory.

3. **Add the schema mapping to your VS Code settings:**

   - **Workspace settings** (`.vscode/settings.json`):
     
     Copy the contents from [`vscode-settings.json`](./vscode-settings.json) in this directory.

   - **User settings** (File > Preferences > Settings > Extensions > YAML):
     
     Add the schema mapping manually in the YAML extension settings.

### What You Get

- **Autocomplete**: Press `Ctrl+Space` to see available configuration options
- **Validation**: Invalid values are highlighted with error messages
- **Documentation**: Hover over properties to see descriptions
- **IntelliSense**: Smart suggestions based on context

### Example Configuration

```yaml
# .ansibledoctor.yml
output_format: markdown  # ← Autocomplete suggests: markdown, html, rst
output_dir: docs/        # ← Validated path format
recursive: true          # ← Boolean validation
exclude_patterns:        # ← Array validation
  - "*.pyc"
  - "__pycache__"
theme:
  primary_color: "#007acc"
languages:
  default: en
  available:
    - en
    - de
```

### Troubleshooting

**Autocomplete not working:**
- Ensure the YAML extension is installed: `redhat.vscode-yaml`
- Reload VS Code after adding schema mappings
- Check that the schema file path is correct (relative to workspace root)

**Schema not updating:**
- Re-export the schema after updating ansible-doctor
- Clear VS Code's cache: `Developer: Reload Window`

**Validation errors:**
- Check the schema format matches JSON Schema Draft 2020-12
- Verify the schema file is valid JSON: `jq . config-schema.json`

## IntelliJ/PyCharm Integration

IntelliJ IDEA and PyCharm also support JSON Schema validation.

### Setup Steps

1. Export the schema as above:

```bash
ansible-doctor schema export config --output config-schema.json
```

2. Open **Settings** > **Languages & Frameworks** > **Schemas and DTDs** > **JSON Schema Mappings**

3. Add a new mapping:
   - **Name**: ansible-doctor Configuration
   - **Schema file or URL**: Point to your `config-schema.json`
   - **Schema version**: JSON Schema version 7
   - **File path pattern**: `.ansibledoctor.yml`

4. Click **OK** and reload the IDE.

### Features

- Schema-aware code completion
- Inline validation and error reporting
- Quick documentation (Ctrl+Q / Cmd+J)
- Structure view with property hierarchy

## OpenAPI Integration

For API documentation tools, export the schema in OpenAPI format:

```bash
ansible-doctor schema export config --format openapi --output openapi-config.json
```

This can be used with:
- **Swagger UI**: Interactive API documentation
- **Redoc**: Modern API documentation
- **Postman**: API testing and development

## Schema Updates

After updating ansible-doctor or adding new configuration options:

```bash
# Re-export schema
ansible-doctor schema export config --output config-schema.json

# Verify schema is valid
jq '.properties | keys' config-schema.json
```

Your IDE should automatically pick up the changes. If not, reload the window or restart the IDE.
