# Quickstart: Ansible Role Parser Validation Scenarios

**Feature**: 001-ansible-role-parser  
**Date**: 2025-12-01  
**Purpose**: Developer validation scenarios for each user story - executable tests to verify parser functionality

## Prerequisites

```bash
# Install dependencies
poetry install

# Run from project root
cd /path/to/ansible-doctor-enhanced

# Use test fixtures
export ROLE_PATH=tests/integration/fixtures/minimal_role
export COMPLEX_ROLE_PATH=tests/integration/fixtures/complex_role
```

## User Story 1: Extract Role Metadata (US1)

**Goal**: Parse meta/main.yml and verify galaxy_info extraction

### Test Scenario 1.1: Basic Metadata Extraction

```bash
# Parse minimal role and check metadata output
poetry run ansible-doctor parse $ROLE_PATH --format json | jq '.metadata'

# Expected output contains:
# {
#   "author": "Your Name",
#   "description": "A minimal Ansible role",
#   "license": "MIT",
#   "platforms": [...],
#   "dependencies": [...]
# }
```

### Test Scenario 1.2: Argument Specs (Ansible 2.11+)

```bash
# If role has meta/argument_specs.yml
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.argument_specs'

# Expected: argument specifications with options
```

## User Story 2: Parse Variables with Annotations (US2)

**Goal**: Extract variables from defaults/vars with @var annotations

### Test Scenario 2.1: Simple Variables

```bash
poetry run ansible-doctor parse $ROLE_PATH --format json | jq '.variables[] | {name, type, value}'

# Expected: Array of variables with inferred types
```

### Test Scenario 2.2: Annotated Variables

```bash
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.variables[] | select(.annotations)'

# Expected: Variables with @var annotations parsed
```

### Test Scenario 2.3: JSON Annotations

```bash
# Check for JSON format annotations
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.variables[] | select(.annotations[].type == "json")'
```

## User Story 3: Extract Task Tags (US3)

**Goal**: Discover tags from tasks/*.yml with @tag annotations

### Test Scenario 3.1: Tag Discovery

```bash
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.tags[] | {name, usage_count}'

# Expected: List of unique tags with counts
```

### Test Scenario 3.2: Tag Descriptions

```bash
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.tags[] | select(.description)'

# Expected: Tags with @tag annotation descriptions
```

## User Story 4: Collect TODOs and Examples (US4)

**Goal**: Extract @todo and @example annotations

### Test Scenario 4.1: TODO Items

```bash
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.todos[]'

# Expected: Array of TODO items with file locations
```

### Test Scenario 4.2: Examples

```bash
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --format json | jq '.examples[]'

# Expected: Code examples with context
```

## Integration Test: Full Role Parsing

```bash
# Complete end-to-end test
poetry run ansible-doctor parse $COMPLEX_ROLE_PATH --output result.json --pretty

# Verify all sections present
cat result.json | jq 'keys'

# Expected keys: metadata, variables, tags, todos, examples
```

## Error Scenarios

### Invalid YAML

```bash
# Create role with invalid YAML
echo "invalid: yaml: content: [" > tests/integration/fixtures/invalid_role/tasks/main.yml

poetry run ansible-doctor parse tests/integration/fixtures/invalid_role

# Expected: Warning logged, partial results returned
```

### Missing Files

```bash
# Role without meta/main.yml
poetry run ansible-doctor parse tests/integration/fixtures/minimal_role

# Expected: Empty metadata, continues processing
```

## Performance Validation

```bash
# Time parsing
time poetry run ansible-doctor parse $COMPLEX_ROLE_PATH > /dev/null

# Expected: <500ms for typical roles
```

## Validation Checklist

- [ ] US1: Metadata extraction works
- [ ] US2: Variable parsing with annotations
- [ ] US3: Tag extraction and descriptions
- [ ] US4: TODO and example collection
- [ ] Error handling: Continues on YAML errors
- [ ] Performance: <500ms typical role
- [ ] Output: Valid JSON with all expected fields</content>
<parameter name="filePath">e:\specify-projects\ansible-doctor-enhanced\specs\001-ansible-role-parser\quickstart.md