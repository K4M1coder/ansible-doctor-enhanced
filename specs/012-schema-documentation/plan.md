# Implementation Plan: Schema Documentation & Validation

**Branch**: `012-schema-documentation` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-schema-documentation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Provide unified schema documentation, validation, and serialization infrastructure for ansible-doctor-enhanced. Validate `.ansibledoctor.yml` configuration files against JSON Schema, export schemas for IDE integration, convert between formats (YAML/JSON/XML/Mermaid), validate internal data models, and generate human-readable schema documentation. Extends Spec 003 (Config) validation with proper JSON Schema support. Provides services to all other specs for schema export and validation. Uses state-of-the-art libraries (pydantic, jsonschema, ruamel.yaml) without reimplementing parsers.

## Technical Context

**Language/Version**: Python 3.11+ (existing project baseline)  
**Primary Dependencies**: pydantic (existing, models/validation), jsonschema (NEW, JSON Schema validation), ruamel.yaml (NEW, YAML parsing with comments), xml.etree.ElementTree (stdlib, XML parsing), json (stdlib, JSON parsing)  
**Storage**: Exported schema files (JSON Schema, OpenAPI specs), cached compiled schemas in memory  
**Testing**: pytest with schema validation fixtures, format conversion round-trip tests, configuration validation integration tests  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) with JSON Schema output compatible with VS Code/IntelliJ  
**Project Type**: Single project - infrastructure service library extending existing config validation and providing services to all features  
**Performance Goals**: <10ms validation overhead for typical configs (<100 properties), <50ms schema export, <100ms format conversion for <1MB files  
**Constraints**: Must use JSON Schema Draft 2020-12, must extend (not replace) Spec 003 validation, must not duplicate Spec 009/011 format generation, must support VS Code JSON Schema integration via $schema property  
**Scale/Scope**: Support configs with 500+ properties, nested objects 10+ levels deep, schema exports for all data models across 15+ specs, format conversions for files up to 10MB

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Test-First Development**: PASS  
  - Rationale: Schema validation is highly testable. Write tests for JSON Schema validation, format conversion round-trips, schema export correctness, then implement SchemaValidator, FormatConverter, SchemaExporter. Fixture-based testing with sample configs and invalid inputs enables TDD workflow.

- **Library-First Architecture**: PASS  
  - Rationale: New `validation/schema_validator.py`, `serialization/format_converter.py`, `serialization/schema_exporter.py` modules are pure Python libraries. SchemaValidator, FormatConverter, SchemaExporter protocols are independent. CLI integration in `cli/schema.py` only wraps library calls.

- **CLI Mandate**: PASS  
  - Rationale: New CLI commands `ansible-doctor schema validate <file>`, `ansible-doctor schema export <type> [--format json|openapi]`, `ansible-doctor schema docs <type>`, `ansible-doctor convert <file> --to <format>`. Extends existing CLI structure.

- **Observability**: PASS  
  - Rationale: Schema validation emits structured logs with validation errors, file paths, schema versions. Format conversion logs source/target formats, data sizes. Schema export logs schema types, output paths. All operations include timing metrics for performance monitoring.

- **Backward Compatibility**: PASS  
  - Rationale: No breaking changes. Extends Spec 003 validation with optional strict mode. Existing configs remain valid. New schema validation is opt-in via `--validate` flag or enabled in config. Schema export is new functionality with no impact on existing features.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
ansibledoctor/
├── models/
│   └── schemas.py           # NEW: SchemaModel, ValidationError base classes
├── validation/
│   ├── __init__.py          # NEW: Validation module
│   ├── schema_validator.py  # NEW: SchemaValidator implementation
│   ├── config_validator.py  # NEW: ConfigurationValidator (extends Spec 003)
│   └── model_validator.py   # NEW: DataModelValidator for internal models
├── serialization/
│   ├── __init__.py          # NEW: Serialization module
│   ├── format_converter.py  # NEW: FormatConverter (YAML/JSON/XML/Mermaid)
│   ├── schema_exporter.py   # NEW: SchemaExporter (JSON Schema, OpenAPI)
│   └── schema_documenter.py # NEW: SchemaDocumenter (Markdown generation)
├── cli/
│   ├── __init__.py          # EXTEND: Add schema commands
│   └── schema.py            # NEW: Schema CLI commands
├── config/
│   └── __init__.py          # EXTEND: Add schema validation to config loading
└── utils/
    └── schema_cache.py      # NEW: Compiled schema caching

tests/
├── unit/
│   ├── test_schema_validator.py      # NEW: SchemaValidator tests
│   ├── test_format_converter.py      # NEW: FormatConverter tests
│   ├── test_schema_exporter.py       # NEW: SchemaExporter tests
│   ├── test_schema_documenter.py     # NEW: SchemaDocumenter tests
│   ├── test_config_validator.py      # NEW: ConfigurationValidator tests
│   └── test_schema_cache.py          # NEW: Schema caching tests
├── integration/
│   ├── test_schema_validation_e2e.py # NEW: End-to-end validation
│   ├── test_format_conversion.py     # NEW: Round-trip conversions
│   └── test_ide_integration.py       # NEW: VS Code schema integration
└── fixtures/
    ├── schemas/                      # NEW: Sample JSON Schemas
    │   ├── config_schema.json
    │   └── role_schema.json
    ├── configs/                      # NEW: Sample configs (valid/invalid)
    │   ├── valid_config.yml
    │   └── invalid_config.yml
    └── conversions/                  # NEW: Format conversion samples
        ├── sample.yml
        ├── sample.json
        └── sample.xml
```

**Structure Decision**: Single project structure extending existing `ansibledoctor/` package. New `validation/` module for all validation logic colocated with existing config. New `serialization/` module for format conversion and schema export. CLI extensions in `cli/schema.py` follow pattern of existing CLI structure. Tests mirror source structure with comprehensive fixture library for validation, conversion, and schema export scenarios.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all gates pass. No additional complexity justification required.

---

## Phase 0: Research & Planning

### Research Tasks

1. **JSON Schema Validation Libraries**: Evaluate Python JSON Schema validators
   - `jsonschema` (reference implementation): Most complete, JSON Schema Draft 2020-12 support
   - `pydantic` schema generation: Convert pydantic models to JSON Schema
   - `fastjsonschema`: Faster validation through code generation
   - Decision criteria: Spec compliance, error message quality, performance, pydantic integration

2. **YAML Parsing with Comment Preservation**: Study YAML libraries for round-trip editing
   - `ruamel.yaml`: Preserves comments, formatting, order
   - `PyYAML`: Fast but loses comments
   - YAML 1.2 spec compliance and anchors/aliases support
   - Decision criteria: Comment preservation, error reporting quality, performance

3. **Schema Export Formats**: Research schema format standards and conversion
   - JSON Schema Draft 2020-12 (primary)
   - OpenAPI 3.1.0 (for API documentation)
   - Pydantic to JSON Schema conversion (`model.model_json_schema()`)
   - IDE integration via `$schema` property in config files
   - Decision criteria: IDE support, spec completeness, conversion fidelity

4. **Format Conversion Strategies**: Investigate data format conversion patterns
   - YAML ↔ JSON: Handle type coercion (null, booleans, numbers)
   - XML ↔ JSON: Element vs attribute mapping, namespace handling
   - Mermaid: Reuse Spec 011 infrastructure (don't duplicate)
   - Round-trip conversion testing (data fidelity verification)
   - Decision criteria: Data preservation, error handling, performance

5. **Schema Caching Performance**: Study schema compilation and caching
   - `jsonschema.validators.validator_for()` compilation
   - In-memory cache with LRU eviction
   - Schema versioning and cache invalidation
   - File watcher for schema hot-reload during development
   - Decision criteria: Validation speedup, memory usage, cache hit rate

**Output**: `research.md` with findings, decisions, and rationale for each topic

---

## Phase 1: Design & Contracts

### Data Model Design

**SchemaModel** (Base):

```python
class SchemaModel(BaseModel):
    \"\"\"Base model for all schema-related data structures.\"\"\"
    schema_version: str = "draft-2020-12"  # JSON Schema version
    id: str | None = Field(default=None, alias="$id")  # Schema URI
    schema_uri: str | None = Field(default=None, alias="$schema")
    
    model_config = ConfigDict(populate_by_name=True)
```

**ValidationError**:

```python
class ValidationError(BaseModel):
    \"\"\"Single validation error with location and context.\"\"\"
    path: str  # JSONPath to error location (e.g., "$.languages.default")
    message: str  # Human-readable error message
    schema_path: str  # Schema path that failed (e.g., "#/properties/languages/properties/default")
    validator: str  # Validator type (e.g., "enum", "type", "required")
    expected: Any | None  # Expected value/type
    actual: Any | None  # Actual value from config
    suggestion: str | None  # Recovery suggestion
    
    @property
    def formatted_message(self) -> str:
        \"\"\"Format error with line number and context.\"\"\"
        return f\"{self.path}: {self.message}\"
```

**ValidationResult**:

```python
class ValidationResult(BaseModel):
    \"\"\"Result of schema validation with errors and warnings.\"\"\"
    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationError] = Field(default_factory=list)
    schema_id: str  # Schema used for validation
    validated_at: datetime = Field(default_factory=datetime.now)
    
    def raise_if_invalid(self) -> None:
        \"\"\"Raise exception if validation failed.\"\"\"
        if not self.is_valid:
            error_summary = "\\n".join(e.formatted_message for e in self.errors)
            raise ValueError(f"Validation failed:\\n{error_summary}")
```

**SchemaDefinition**:

```python
class SchemaDefinition(SchemaModel):
    \"\"\"JSON Schema definition for data models.\"\"\"
    title: str
    description: str | None
    type: Literal["object", "array", "string", "number", "boolean", "null"]
    properties: dict[str, "SchemaDefinition"] | None
    required: list[str] = Field(default_factory=list)
    additional_properties: bool | "SchemaDefinition" = True
    examples: list[dict[str, Any]] = Field(default_factory=list)
    definitions: dict[str, "SchemaDefinition"] = Field(default_factory=dict)
    
    @classmethod
    def from_pydantic(cls, model: type[BaseModel]) -> "SchemaDefinition":
        \"\"\"Generate schema from pydantic model.\"\"\"
        schema_dict = model.model_json_schema()
        return cls(**schema_dict)
```

**FormatType**:

```python
class FormatType(str, Enum):
    \"\"\"Supported serialization formats.\"\"\"
    YAML = "yaml"
    JSON = "json"
    XML = "xml"
    MERMAID = "mermaid"  # Reuses Spec 011
    TOML = "toml"  # Bonus: for Python projects
```

**ConversionResult**:

```python
class ConversionResult(BaseModel):
    \"\"\"Result of format conversion with metadata.\"\"\"
    source_format: FormatType
    target_format: FormatType
    output: str  # Converted content
    warnings: list[str] = Field(default_factory=list)  # Data loss warnings
    duration_ms: float
    
    @property
    def has_data_loss(self) -> bool:
        \"\"\"Check if conversion lost data.\"\"\"
        return len(self.warnings) > 0
```

### API Contracts

**SchemaValidator Protocol**:

```python
class SchemaValidator(Protocol):
    \"\"\"Protocol for validating data against JSON Schema.\"\"\"
    
    def validate(
        self,
        data: dict[str, Any] | BaseModel,
        schema: SchemaDefinition | dict[str, Any],
        strict: bool = False,
    ) -> ValidationResult:
        \"\"\"
        Validate data against JSON Schema.
        
        Args:
            data: Data to validate (dict or pydantic model)
            schema: JSON Schema definition
            strict: Treat warnings as errors
        
        Returns:
            ValidationResult with errors and warnings
        \"\"\"
        ...
    
    def validate_file(
        self,
        file_path: Path,
        schema: SchemaDefinition | dict[str, Any],
        strict: bool = False,
    ) -> ValidationResult:
        \"\"\"Validate file content against schema.\"\"\"
        ...
```

**ConfigurationValidator**:

```python
class ConfigurationValidator:
    \"\"\"Validates ansible-doctor configuration files.\"\"\"
    
    def __init__(self, schema_cache: SchemaCache):
        self.schema_cache = schema_cache
        self.config_schema = self._load_config_schema()
    
    def validate_config(
        self,
        config_path: Path,
        strict: bool = False,
    ) -> ValidationResult:
        \"\"\"
        Validate .ansibledoctor.yml file.
        
        Extends Spec 003 validation with full JSON Schema support.
        \"\"\"
        ...
    
    def migrate_config(
        self,
        config_path: Path,
        backup: bool = True,
    ) -> Path:
        \"\"\"
        Migrate deprecated config options to current schema.
        
        Returns:
            Path to migrated config (or backup if errors)
        \"\"\"
        ...
```

**FormatConverter**:

```python
class FormatConverter:
    \"\"\"Convert between supported data formats.\"\"\"
    
    def convert(
        self,
        source: str | Path,
        source_format: FormatType,
        target_format: FormatType,
        preserve_comments: bool = True,
    ) -> ConversionResult:
        \"\"\"
        Convert data between formats.
        
        Args:
            source: Source data (string or file path)
            source_format: Source format
            target_format: Target format
            preserve_comments: Keep comments when possible (YAML only)
        
        Returns:
            ConversionResult with converted data and warnings
        \"\"\"
        ...
    
    def convert_file(
        self,
        input_path: Path,
        output_path: Path,
        target_format: FormatType | None = None,
    ) -> ConversionResult:
        \"\"\"
        Convert file, auto-detecting source format.
        
        If target_format is None, infer from output_path extension.
        \"\"\"
        ...
    
    def round_trip_test(
        self,
        data: dict[str, Any],
        format: FormatType,
    ) -> bool:
        \"\"\"
        Test format conversion fidelity.
        
        Returns:
            True if data identical after round-trip conversion
        \"\"\"
        ...
```

**SchemaExporter**:

```python
class SchemaExporter:
    \"\"\"Export schemas in various formats for IDE integration.\"\"\"
    
    def export_json_schema(
        self,
        model: type[BaseModel],
        output_path: Path | None = None,
    ) -> str:
        \"\"\"
        Export pydantic model as JSON Schema.
        
        Args:
            model: Pydantic model to export
            output_path: Optional file path to write schema
        
        Returns:
            JSON Schema as string
        \"\"\"
        ...
    
    def export_openapi(
        self,
        models: dict[str, type[BaseModel]],
        info: dict[str, str],
        output_path: Path | None = None,
    ) -> str:
        \"\"\"
        Export models as OpenAPI 3.1.0 specification.
        
        Args:
            models: Dict of model name to pydantic model
            info: API metadata (title, version, description)
            output_path: Optional file path to write spec
        
        Returns:
            OpenAPI spec as YAML string
        \"\"\"
        ...
    
    def export_all_schemas(
        self,
        output_dir: Path,
        format: Literal["json-schema", "openapi"] = "json-schema",
    ) -> list[Path]:
        \"\"\"
        Export schemas for all ansible-doctor models.
        
        Returns:
            List of generated schema files
        \"\"\"
        ...
```

**SchemaDocumenter**:

```python
class SchemaDocumenter:
    \"\"\"Generate human-readable documentation from schemas.\"\"\"
    
    def document_schema(
        self,
        schema: SchemaDefinition | dict[str, Any],
        format: Literal["markdown", "html", "rst"] = "markdown",
    ) -> str:
        \"\"\"
        Generate documentation from JSON Schema.
        
        Args:
            schema: JSON Schema to document
            format: Output format
        
        Returns:
            Formatted documentation
        \"\"\"
        ...
    
    def document_model(
        self,
        model: type[BaseModel],
        format: Literal["markdown", "html", "rst"] = "markdown",
    ) -> str:
        \"\"\"Generate documentation from pydantic model.\"\"\"
        schema = SchemaDefinition.from_pydantic(model)
        return self.document_schema(schema, format)
    
    def generate_property_table(
        self,
        schema: SchemaDefinition,
    ) -> str:
        \"\"\"
        Generate Markdown table of properties.
        
        | Property | Type | Required | Default | Description |
        | ---------- | ------ | ---------- | --------- | ------------- |
        \"\"\"
        ...
```

**SchemaCache**:

```python
class SchemaCache:
    \"\"\"Cache compiled schemas for performance.\"\"\"
    
    def __init__(self, max_size: int = 100):
        self._cache: dict[str, Any] = {}
        self._lru: list[str] = []
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
    
    def get_validator(
        self,
        schema: SchemaDefinition | dict[str, Any],
    ) -> jsonschema.Validator:
        \"\"\"
        Get compiled validator from cache.
        
        Returns:
            Compiled JSON Schema validator
        \"\"\"
        ...
    
    def invalidate(self, schema_id: str) -> None:
        \"\"\"Invalidate cached schema.\"\"\"
        ...
    
    @property
    def hit_rate(self) -> float:
        \"\"\"Cache hit rate for monitoring.\"\"\"
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
```

### CLI Extensions

**New Commands in `ansibledoctor/cli/schema.py`**:

```python
@click.group()
def schema():
    \"\"\"Schema validation, export, and documentation commands.\"\"\"
    pass

@schema.command(\"validate\")
@click.argument(\"file\", type=click.Path(exists=True))
@click.option(\"--strict\", is_flag=True, help=\"Treat warnings as errors\")
@click.option(\"--schema\", type=click.Path(exists=True), help=\"Custom schema file\")
def validate_command(file: str, strict: bool, schema: str | None):
    \"\"\"Validate configuration file against schema.\"\"\"
    ...

@schema.command(\"export\")
@click.argument(\"type\", type=click.Choice([\"config\", \"role\", \"collection\", \"all\"]))
@click.option(\"--format\", type=click.Choice([\"json-schema\", \"openapi\"]), default=\"json-schema\")
@click.option(\"--output\", \"-o\", type=click.Path(), help=\"Output file/directory\")
@click.option(\"--pretty\", is_flag=True, help=\"Pretty-print output\")
def export_command(type: str, format: str, output: str | None, pretty: bool):
    \"\"\"Export schemas for IDE integration.\"\"\"
    ...

@schema.command(\"docs\")
@click.argument(\"type\", type=click.Choice([\"config\", \"role\", \"collection\"]))
@click.option(\"--format\", type=click.Choice([\"markdown\", \"html\", \"rst\"]), default=\"markdown\")
@click.option(\"--output\", \"-o\", type=click.Path(), help=\"Output file\")
def docs_command(type: str, format: str, output: str | None):
    \"\"\"Generate schema documentation.\"\"\"
    ...

@click.command(\"convert\")
@click.argument(\"file\", type=click.Path(exists=True))
@click.option(\"--to\", \"target_format\", required=True, type=click.Choice([\"yaml\", \"json\", \"xml\", \"toml\"]))
@click.option(\"--output\", \"-o\", type=click.Path(), help=\"Output file (default: stdout)\")
@click.option(\"--pretty\", is_flag=True, help=\"Pretty-print output\")
def convert_command(file: str, target_format: str, output: str | None, pretty: bool):
    \"\"\"Convert between data formats.\"\"\"
    ...
```

### Integration with Spec 003 (Config)

**Enhanced Config Validation**:

```python
# In ansibledoctor/config/__init__.py

class Config:
    def __init__(self, config_path: Path | None = None):
        self.validator = ConfigurationValidator(schema_cache=SchemaCache())
        
        if config_path:
            # Validate before loading (extends Spec 003)
            validation_result = self.validator.validate_config(config_path)
            if not validation_result.is_valid:
                logger.error(\"Configuration validation failed\")
                for error in validation_result.errors:
                    logger.error(error.formatted_message)
                raise ValueError(\"Invalid configuration\")
            
            # Log warnings
            for warning in validation_result.warnings:
                logger.warning(warning.formatted_message)
        
        # Existing config loading logic...
```

### Output Contracts

**JSON Schema Export** (for `.ansibledoctor.yml`):

```json
{
  \"$schema\": \"https://json-schema.org/draft/2020-12/schema\",
  \"$id\": \"https://ansibledoctor.com/schemas/config.json\",
  \"title\": \"AnsibleDoctorConfig\",
  \"description\": \"Configuration schema for ansible-doctor-enhanced\",
  \"type\": \"object\",
  \"properties\": {
    \"output_format\": {
      \"type\": \"string\",
      \"enum\": [\"markdown\", \"html\", \"rst\"],
      \"default\": \"markdown\",
      \"description\": \"Documentation output format\"
    },
    \"languages\": {
      \"type\": \"object\",
      \"properties\": {
        \"default\": {
          \"type\": \"string\",
          \"enum\": [\"en\", \"fr\", \"de\"],
          \"default\": \"en\"
        },
        \"enabled\": {
          \"type\": \"array\",
          \"items\": {\"type\": \"string\"},
          \"default\": [\"en\"]
        }
      }
    },
    \"template_dirs\": {
      \"type\": \"array\",
      \"items\": {\"type\": \"string\"},
      \"description\": \"Custom template directories\"
    }
  },
  \"required\": [\"output_format\"],
  \"additionalProperties\": false
}
```

**Validation Error Output**:

```text
Configuration validation failed:

$.output_format: must be one of: markdown, html, rst (got: "pdf")
  Expected: "markdown" | "html" | "rst"
  Actual: "pdf"
  Suggestion: Use --output-format markdown or edit .ansibledoctor.yml

$.languages.default: must be string (got: null)
  Expected: string
  Actual: null
  Suggestion: Set languages.default to "en", "fr", or "de"

$.unknown_field: unknown property (not in schema)
  Suggestion: Remove unknown_field or check documentation for correct property name
```

**Schema Documentation** (Markdown):

```markdown
# Configuration Schema

## Properties

### output_format

- **Type**: string
- **Required**: yes
- **Default**: \"markdown\"
- **Allowed values**: \"markdown\", \"html\", \"rst\"
- **Description**: Documentation output format

**Example**:
```yaml
output_format: markdown
```

### languages

- **Type**: object
- **Required**: no
- **Description**: Language configuration for multi-language documentation

#### languages.default

- **Type**: string
- **Default**: \"en\"
- **Allowed values**: \"en\", \"fr\", \"de\"

**Example**:

```yaml
languages:
  default: en
  enabled:
    - en
    - fr
```

```

### Integration Points

1. **Spec 003 (Config) Extension**:
   - Add schema validation to config loading
   - Provide migration tool for deprecated options
   - Export config schema for IDE integration

2. **All Data Model Specs** (001, 004, 006, etc.):
   - Export JSON Schema for each model
   - Enable validation in tests
   - Generate documentation from schemas

3. **Spec 009 (Execution Reports)**:
   - Use FormatConverter for JSON report generation
   - Validate report structure against schema
   - Enable report format conversion (JSON → YAML)

4. **Spec 011 (Indexes)**:
   - Reuse MermaidBuilder for schema diagrams
   - Don't duplicate Mermaid generation logic
   - Convert index data to Mermaid via FormatConverter

### Quickstart Example

**Validate Configuration**:
```bash
# Validate .ansibledoctor.yml
ansible-doctor schema validate .ansibledoctor.yml

# Strict mode (warnings as errors)
ansible-doctor schema validate .ansibledoctor.yml --strict

# Custom schema
ansible-doctor schema validate my_config.yml --schema custom_schema.json
```

**Export Schemas**:

```bash
# Export config schema for VS Code
ansible-doctor schema export config --format json-schema --output .vscode/ansibledoctor.schema.json

# Export all schemas as OpenAPI spec
ansible-doctor schema export all --format openapi --output docs/api-schema.yaml

# Pretty-printed JSON Schema
ansible-doctor schema export role --pretty
```

**Convert Formats**:

```bash
# Convert YAML to JSON
ansible-doctor convert .ansibledoctor.yml --to json --output config.json

# Convert to XML (for tool integration)
ansible-doctor convert role_data.yml --to xml --output role_data.xml

# Pretty-print JSON
ansible-doctor convert data.json --to json --pretty --output pretty_data.json
```

**Generate Schema Documentation**:

```bash
# Generate Markdown docs from config schema
ansible-doctor schema docs config --format markdown --output docs/CONFIG_SCHEMA.md

# Generate HTML docs
ansible-doctor schema docs role --format html --output docs/role_schema.html
```

**VS Code Integration** (`.vscode/settings.json`):

```json
{
  \"yaml.schemas\": {
    \".vscode/ansibledoctor.schema.json\": \".ansibledoctor.yml\"
  }
}
```

**Output**: `quickstart.md`, `data-model.md`, `contracts/schema-validator.yaml`, `contracts/format-converter.yaml`, `contracts/config-schema.json`

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
