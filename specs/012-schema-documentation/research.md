# Research Findings: Schema Documentation & Validation

**Date**: 2025-12-03  
**Feature**: Spec 012 - Schema Documentation & Validation

This document presents research findings from Phase 0, documenting technology decisions for schema validation, format conversion, and documentation generation.

---

## 1. JSON Schema Validation Libraries

### Question
Which Python library should we use for JSON Schema validation with best error messages, performance, and pydantic integration?

### Options Evaluated

#### Option A: `jsonschema` (Python JSON Schema)
- **Pros**: Reference implementation, Draft 2020-12 support, comprehensive error reporting, widely adopted
- **Cons**: Slower than compiled validators, verbose API
- **Performance**: ~1ms per validation for typical configs
- **Error Quality**: Excellent (JSONPath, expected vs actual, schema path)

#### Option B: `fastjsonschema`
- **Pros**: 10x faster than jsonschema (code generation), good for high-volume validation
- **Cons**: Draft 07 only (no 2020-12), basic error messages, no pydantic integration
- **Performance**: ~0.1ms per validation
- **Error Quality**: Basic (single error message, no context)

#### Option C: `pydantic` Built-in Validation
- **Pros**: Already used in project, generates JSON Schema via `.model_json_schema()`, excellent DX
- **Cons**: Not a pure JSON Schema validator (validates Python objects), limited custom schema support
- **Performance**: ~0.5ms per validation
- **Error Quality**: Good (field names, type errors, clear messages)

### Decision: **jsonschema + pydantic**

**Rationale**:
- Use `pydantic` for data model validation (existing pattern)
- Use `pydantic.model_json_schema()` to generate JSON Schema from models
- Use `jsonschema` to validate external files (`.ansibledoctor.yml`) against generated schemas
- `jsonschema` provides best error messages for user-facing config validation
- Draft 2020-12 support ensures future compatibility with IDE tooling
- Performance overhead (<10ms) acceptable for config validation use case

**Implementation Pattern**:
```python
from pydantic import BaseModel
from jsonschema import validate, ValidationError as JSValidationError

# Generate schema from pydantic model
schema = ConfigModel.model_json_schema()

# Validate external config file
try:
    validate(instance=config_data, schema=schema)
except JSValidationError as e:
    # Convert to our ValidationError with better messages
    ...
```

**Alternatives Considered**: Hybrid approach (fastjsonschema for hot paths) rejected due to complexity and Draft 07 limitation.

---

## 2. YAML Parsing with Comment Preservation

### Question
Which YAML library preserves comments and formatting for round-trip config editing and migration?

### Options Evaluated

#### Option A: `PyYAML`
- **Pros**: Fast, standard library-like, widely used
- **Cons**: **Loses comments**, loses formatting, YAML 1.1 only (deprecated)
- **Use Case**: One-way parsing (read config, don't write back)

#### Option B: `ruamel.yaml`
- **Pros**: **Preserves comments**, preserves formatting, YAML 1.2 support, round-trip editing
- **Cons**: Slower than PyYAML (2-3x), more complex API
- **Use Case**: Config migration, format conversion with comment preservation

#### Option C: `strictyaml`
- **Pros**: Type-safe, security-focused (no arbitrary Python objects)
- **Cons**: No comment preservation, limited YAML features (no anchors), restrictive
- **Use Case**: Security-critical parsing (not needed for our use case)

### Decision: **ruamel.yaml for config, PyYAML for internal data**

**Rationale**:
- **Config files** (.ansibledoctor.yml): Use `ruamel.yaml` to preserve user comments during migration and validation
- **Internal data** (role metadata, parsed structures): Use `PyYAML` for speed
- Comment preservation critical for config migration tool (Spec 003 enhancement)
- Example: User adds `# TODO: configure this later` → migration preserves comment

**Implementation Pattern**:
```python
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False

# Load with comments
with open('.ansibledoctor.yml') as f:
    config = yaml.load(f)

# Modify
config['new_field'] = 'value'

# Write back (preserves comments)
with open('.ansibledoctor.yml', 'w') as f:
    yaml.dump(config, f)
```

**Performance Impact**: Config loading happens once per run, so 2-3x slowdown (~10ms → ~30ms) is acceptable.

**Alternatives Considered**: Use PyYAML only, then parse comments separately (rejected: too fragile, doesn't preserve formatting).

---

## 3. Schema Export Formats

### Question
What schema formats should we support for IDE integration and what standards ensure compatibility?

### Formats Researched

#### JSON Schema Draft 2020-12
- **Standard**: https://json-schema.org/draft/2020-12/schema
- **IDE Support**: VS Code, IntelliJ IDEA, WebStorm (via YAML extension)
- **Features**: $schema, $id, $ref, definitions, allOf/anyOf/oneOf, examples, $comment
- **Use Case**: Primary schema format for config validation

**VS Code Integration**:
```json
{
  "yaml.schemas": {
    ".vscode/ansibledoctor.schema.json": ".ansibledoctor.yml"
  }
}
```

#### OpenAPI 3.1.0
- **Standard**: https://spec.openapi.org/oas/v3.1.0
- **Compatibility**: OpenAPI 3.1+ uses JSON Schema Draft 2020-12 for schemas
- **Use Case**: API documentation, Swagger UI for data models
- **Benefit**: Can document internal data models as if they were API endpoints

#### Pydantic JSON Schema Generation
- **Method**: `BaseModel.model_json_schema(mode='serialization')`
- **Output**: JSON Schema Draft 2020-12 compatible
- **Features**: Automatic description from docstrings, Field(..., description=...), examples, constraints
- **Limitation**: Some pydantic features don't map to JSON Schema (validators, custom types)

### Decision: **JSON Schema as primary, OpenAPI for docs**

**Rationale**:
- **Primary format**: JSON Schema Draft 2020-12 for all schema exports
- **Documentation format**: OpenAPI 3.1.0 for human-readable schema docs (Swagger UI)
- Pydantic → JSON Schema conversion via `.model_json_schema()` for all data models
- IDE integration requires `$schema` property in exported schemas
- OpenAPI useful for visualizing data model relationships (components section)

**Schema Export Strategy**:
```python
# Export config schema for VS Code
config_schema = ConfigModel.model_json_schema()
config_schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
config_schema['$id'] = 'https://ansibledoctor.com/schemas/config.json'

# Export OpenAPI spec for docs
openapi_spec = {
    'openapi': '3.1.0',
    'info': {'title': 'Ansible Doctor Models', 'version': '1.0.0'},
    'components': {
        'schemas': {
            'Config': ConfigModel.model_json_schema(),
            'Role': RoleModel.model_json_schema(),
            # ... all models
        }
    }
}
```

**Alternatives Considered**: Custom schema format (rejected: reinventing wheel, no IDE support).

---

## 4. Format Conversion Strategies

### Question
How do we handle data format conversion (YAML/JSON/XML) while preserving data fidelity and detecting loss?

### Conversion Challenges

#### Type Coercion
- **YAML/JSON**: YAML has more types (octal, timestamps, null variants: ~, null)
- **JSON → YAML**: Safe (JSON is subset of YAML)
- **YAML → JSON**: Potential loss (YAML tags, anchors, complex keys)
- **Solution**: Warn on data loss, preserve as strings when possible

#### XML ↔ JSON
- **Element vs Attribute**: `<tag attr="val">content</tag>` maps to `{"tag": {"@attr": "val", "#text": "content"}}`
- **Convention**: Use `@` prefix for attributes, `#text` for text content
- **Arrays**: XML doesn't distinguish single element vs array → heuristic needed

#### Comment Preservation
- **YAML**: ruamel.yaml preserves comments
- **JSON**: No comment support (use `// ...` but non-standard)
- **XML**: `<!-- ... -->` comments preserved via `xml.etree` with `method='html'`
- **Solution**: Best effort, warn when comments lost

### Decision: **Structured conversion with data loss warnings**

**Rationale**:
- Implement conversion with **explicit data loss detection**
- Return `ConversionResult` with warnings list
- Support round-trip testing: `data == convert(convert(data, to=X), to=original)`
- For YAML/JSON: Use native types, warn on YAML-specific features
- For XML: Use convention (`@attr`, `#text`) with documentation

**Conversion Rules**:
```python
# YAML → JSON
- Preserve: scalars, lists, dicts, booleans, null
- Warn: anchors/aliases (replace with copies), tags (remove), complex keys (stringify)

# JSON → YAML
- Preserve: all (JSON is subset)
- Style: Use ruamel.yaml for human-readable formatting

# XML ↔ JSON
- Preserve: structure, text, attributes (as @attr)
- Warn: namespaces (strip), mixed content (flatten)
```

**Round-Trip Test**:
```python
def test_yaml_json_round_trip():
    yaml_data = {"key": "value", "list": [1, 2, 3]}
    
    # YAML → JSON → YAML
    json_str = converter.convert(yaml_data, to="json")
    back_to_yaml = converter.convert(json_str, to="yaml")
    
    assert yaml_data == back_to_yaml  # No data loss
```

**Alternatives Considered**: Lossy conversion without warnings (rejected: silently corrupts data), custom unified format (rejected: too complex).

---

## 5. Schema Caching Performance

### Question
How do we cache compiled JSON Schema validators for performance without excessive memory usage?

### Caching Strategies

#### In-Memory Cache with LRU
- **Strategy**: Cache compiled validators (jsonschema.validators.Draft202012Validator)
- **Size**: Compiled validator ~10KB, limit to 100 schemas (~1MB memory)
- **Eviction**: LRU (Least Recently Used) when cache full
- **Hit Rate**: Expected >90% (most validation uses same config/role schemas)

#### File-Based Cache
- **Strategy**: Serialize compiled validators to disk
- **Problem**: `jsonschema` validators not picklable (contain closures)
- **Workaround**: Cache schema dict, compile on load (defeats purpose)
- **Conclusion**: Not viable

#### Schema Versioning
- **Problem**: Schema changes during development invalidate cache
- **Solution**: Include schema hash in cache key: `cache_key = f"{schema_id}:{hash(schema_json)}"`
- **Benefit**: Automatic invalidation on schema change

### Decision: **In-memory LRU cache with monitoring**

**Rationale**:
- In-memory cache with 100-schema limit (configurable)
- LRU eviction via `collections.OrderedDict` or `functools.lru_cache`
- Cache key: `f"{schema['$id']}:{hash(json.dumps(schema))}"`
- Expose cache metrics (hit rate, size) for observability
- No disk cache (complexity not worth it)

**Implementation**:
```python
from functools import lru_cache
import hashlib
import json

class SchemaCache:
    def __init__(self, max_size: int = 100):
        self._cache = {}
        self._lru = []
        self.max_size = max_size
        self.hit_count = 0
        self.miss_count = 0
    
    def _cache_key(self, schema: dict) -> str:
        schema_json = json.dumps(schema, sort_keys=True)
        schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()[:16]
        schema_id = schema.get('$id', 'unknown')
        return f"{schema_id}:{schema_hash}"
    
    def get_validator(self, schema: dict):
        key = self._cache_key(schema)
        
        if key in self._cache:
            self.hit_count += 1
            self._lru.remove(key)
            self._lru.append(key)
            return self._cache[key]
        
        # Cache miss
        self.miss_count += 1
        validator = jsonschema.validators.validator_for(schema)(schema)
        
        # Evict LRU if full
        if len(self._cache) >= self.max_size:
            evict_key = self._lru.pop(0)
            del self._cache[evict_key]
        
        self._cache[key] = validator
        self._lru.append(key)
        return validator
```

**Performance Impact**:
- First validation: ~5ms (compile schema)
- Cached validation: ~1ms (use compiled validator)
- Memory: ~1MB for 100 schemas (acceptable)

**Metrics**:
```python
# Log cache performance
logger.info("Schema cache stats", extra={
    "hit_rate": cache.hit_rate,
    "size": len(cache._cache),
    "max_size": cache.max_size,
})
```

**Alternatives Considered**: No caching (rejected: 5x slowdown), persistent cache (rejected: complexity, serialization issues).

---

## Summary of Decisions

| Research Topic | Decision | Rationale |
|----------------|----------|-----------|
| JSON Schema Validation | jsonschema + pydantic | Best error messages, Draft 2020-12, pydantic integration |
| YAML Parsing | ruamel.yaml (config), PyYAML (internal) | Comment preservation for config migration |
| Schema Export | JSON Schema primary, OpenAPI for docs | IDE integration, standard compliance |
| Format Conversion | Structured conversion with warnings | Data loss detection, round-trip testing |
| Schema Caching | In-memory LRU cache | 5x speedup, <1MB memory, simple implementation |

**Next Steps**: Proceed to Phase 1 data model design and contract specification.
