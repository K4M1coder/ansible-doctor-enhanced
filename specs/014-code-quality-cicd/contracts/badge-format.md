# Badge Format Specification

**Feature**: 014-code-quality-cicd  
**Purpose**: Define badge JSON format and generation rules  
**Last Updated**: 2026-01-10

---

## Shields.io Endpoint Format

### JSON Schema

```json
{
  "schemaVersion": 1,
  "label": "string",
  "message": "string",
  "color": "string",
  "labelColor": "string (optional)",
  "isError": "boolean (optional)",
  "namedLogo": "string (optional)",
  "logoSvg": "string (optional)",
  "logoColor": "string (optional)",
  "logoWidth": "number (optional)",
  "logoPosition": "string (optional)",
  "style": "string (optional)",
  "cacheSeconds": "number (optional)"
}
```

**Reference**: https://shields.io/endpoint

---

## Field Definitions

### Required Fields

#### `schemaVersion`
- **Type**: Integer
- **Description**: Schema version for Shields.io endpoint
- **Valid Values**: `1` (current)
- **Example**:
  ```json
  "schemaVersion": 1
  ```

#### `label`
- **Type**: String
- **Description**: Left side of the badge (category)
- **Max Length**: 20 characters recommended
- **Examples**:
  ```json
  "label": "coverage"
  "label": "tests"
  "label": "perf ✓"
  ```

#### `message`
- **Type**: String
- **Description**: Right side of the badge (value)
- **Max Length**: 30 characters recommended
- **Examples**:
  ```json
  "message": "79%"
  "message": "184 passed"
  "message": "S:56ms | M:97ms | L:180ms"
  ```

#### `color`
- **Type**: String (color name or hex)
- **Description**: Background color for message
- **Valid Values**:
  - Named: `brightgreen`, `green`, `yellow`, `orange`, `red`, `blue`, `lightgrey`
  - Hex: `#44cc11`, `#ff6600`
- **Examples**:
  ```json
  "color": "brightgreen"
  "color": "#44cc11"
  ```

---

### Optional Fields

#### `labelColor`
- **Type**: String (color name or hex)
- **Description**: Background color for label
- **Default**: Grey
- **Examples**:
  ```json
  "labelColor": "blue"
  "labelColor": "#555555"
  ```

#### `isError`
- **Type**: Boolean
- **Description**: Mark badge as error state
- **Default**: `false`
- **Use Case**: When metric collection fails
- **Examples**:
  ```json
  "isError": true
  ```

#### `namedLogo`
- **Type**: String
- **Description**: Simple icon name from Simple Icons
- **Valid Values**: See https://simpleicons.org/
- **Examples**:
  ```json
  "namedLogo": "python"
  "namedLogo": "github"
  ```

#### `style`
- **Type**: String (enum)
- **Description**: Badge style
- **Valid Values**: `flat`, `flat-square`, `plastic`, `for-the-badge`, `social`
- **Default**: `flat`
- **Examples**:
  ```json
  "style": "flat"
  "style": "for-the-badge"
  ```

#### `cacheSeconds`
- **Type**: Integer
- **Description**: Cache duration in seconds
- **Default**: 300 (5 minutes)
- **Recommended**: 3600 (1 hour) for stable metrics
- **Examples**:
  ```json
  "cacheSeconds": 3600
  ```

---

## Badge Categories

### Category 1: Static Badges

**Purpose**: Display fixed project information

**Examples**:

#### Version Badge
```json
{
  "schemaVersion": 1,
  "label": "version",
  "message": "0.8.0",
  "color": "blue",
  "namedLogo": "python"
}
```

#### License Badge
```json
{
  "schemaVersion": 1,
  "label": "license",
  "message": "Apache-2.0",
  "color": "blue"
}
```

#### Python Version Badge
```json
{
  "schemaVersion": 1,
  "label": "python",
  "message": "3.11 | 3.13",
  "color": "blue",
  "namedLogo": "python"
}
```

---

### Category 2: Code Style Badges

**Purpose**: Show code quality tool status

**Examples**:

#### Black Badge
```json
{
  "schemaVersion": 1,
  "label": "code style",
  "message": "black",
  "color": "black"
}
```

#### isort Badge
```json
{
  "schemaVersion": 1,
  "label": "imports",
  "message": "isort",
  "color": "blue"
}
```

#### Ruff Badge
```json
{
  "schemaVersion": 1,
  "label": "linter",
  "message": "ruff",
  "color": "blue"
}
```

---

### Category 3: Type Checking Badge

**Purpose**: Show mypy type checking status

**Color Rules**:
- 0 errors: `brightgreen`
- 1-5 errors: `yellow`
- >5 errors: `red`

**Examples**:

#### No Errors
```json
{
  "schemaVersion": 1,
  "label": "mypy",
  "message": "0 errors",
  "color": "brightgreen"
}
```

#### Some Errors
```json
{
  "schemaVersion": 1,
  "label": "mypy",
  "message": "3 errors",
  "color": "yellow"
}
```

#### Many Errors
```json
{
  "schemaVersion": 1,
  "label": "mypy",
  "message": "12 errors",
  "color": "red"
}
```

---

### Category 4: Coverage Badge

**Purpose**: Show test coverage percentage

**Color Rules**:
- <80%: `red`
- 80-89%: `yellow`
- 90-94%: `yellowgreen`
- ≥95%: `brightgreen`

**Examples**:

#### Low Coverage
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "65%",
  "color": "red"
}
```

#### Medium Coverage
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "85%",
  "color": "yellow"
}
```

#### High Coverage
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "92%",
  "color": "yellowgreen"
}
```

#### Excellent Coverage
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "97%",
  "color": "brightgreen"
}
```

---

### Category 5: Test Count Badges

**Purpose**: Show test execution results

**Color Rules**:
- **Passed**: >0 = `brightgreen`, 0 = `red`
- **Skipped**: Any = `yellow`
- **Failed**: 0 = `brightgreen`, >0 = `red`
- **Warnings**: 0 = `brightgreen`, >0 = `yellow`

**Examples**:

#### Tests Passed
```json
{
  "schemaVersion": 1,
  "label": "tests",
  "message": "184 passed",
  "color": "brightgreen"
}
```

#### Tests Skipped
```json
{
  "schemaVersion": 1,
  "label": "tests",
  "message": "3 skipped",
  "color": "yellow"
}
```

#### Tests Failed
```json
{
  "schemaVersion": 1,
  "label": "tests",
  "message": "0 failed",
  "color": "brightgreen"
}
```

#### Tests Warnings
```json
{
  "schemaVersion": 1,
  "label": "tests",
  "message": "2 warnings",
  "color": "yellow"
}
```

---

### Category 6: Performance Badge

**Purpose**: Show performance test results with timings

**Color Rules**:
- All tests pass (≤target): `brightgreen`
- Some tests warn (target < time ≤ max): `orange`
- Any test fails (>max): `red`

**Label Rules**:
- Pass: `perf ✓`
- Warn: `perf ⚠️`
- Fail: `perf ❌`

**Message Format**: `S:[time]ms | M:[time]ms | L:[time]ms`
- **S**: Small role (target 60ms, max 80ms)
- **M**: Medium role (target 100ms, max 130ms)
- **L**: Large role (target 200ms, max 250ms)

**Examples**:

#### All Pass
```json
{
  "schemaVersion": 1,
  "label": "perf ✓",
  "message": "S:56ms | M:97ms | L:180ms",
  "color": "brightgreen"
}
```

#### Some Warn
```json
{
  "schemaVersion": 1,
  "label": "perf ⚠️",
  "message": "S:56ms | M:115ms | L:180ms",
  "color": "orange"
}
```

#### Some Fail
```json
{
  "schemaVersion": 1,
  "label": "perf ❌",
  "message": "S:56ms | M:97ms | L:260ms",
  "color": "red"
}
```

---

### Category 7: CI Status Badges

**Purpose**: Show GitHub Actions workflow status

**Format**: Use GitHub's native workflow status badges

**Examples**:

#### Pre-commit Status
```markdown
![Pre-commit](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/pre-commit.yml/badge.svg)
```

#### CI Windows Status
```markdown
![CI Windows](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/ci-windows.yml/badge.svg)
```

#### Badges Status
```markdown
![Badges](https://github.com/K4M1coder/ansible-doctor-enhanced/actions/workflows/badges.yml/badge.svg)
```

**Note**: These use GitHub's built-in badge generation, not custom JSON.

---

## Badge Generation Pipeline

### Step 1: Parse Source Data

**Inputs**:
- `pytest.xml`: Test counts (passed, skipped, failed, warnings)
- `coverage.json`: Coverage percentage
- `mypy-output.txt`: Error count
- `performance-results.json`: Timings and status

**Code Example** (Python):
```python
import xml.etree.ElementTree as ET
import json

def parse_pytest_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    testsuite = root.find("testsuite")
    return {
        "passed": int(testsuite.attrib.get("tests", 0)) - int(testsuite.attrib.get("failures", 0)) - int(testsuite.attrib.get("errors", 0)) - int(testsuite.attrib.get("skipped", 0)),
        "skipped": int(testsuite.attrib.get("skipped", 0)),
        "failed": int(testsuite.attrib.get("failures", 0)) + int(testsuite.attrib.get("errors", 0)),
        "warnings": len(root.findall(".//warning"))
    }

def parse_coverage_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return round(data["totals"]["percent_covered"], 1)

def parse_performance_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    short_labels = {"small_role": "S", "medium_role": "M", "large_role": "L"}
    results = {}
    for test_name, metrics in data.items():
        short = short_labels.get(test_name, test_name[:1].upper())
        results[short] = {
            "time_ms": metrics["time_ms"],
            "status": metrics["status"]
        }
    return results
```

---

### Step 2: Apply Color Rules

**Code Example**:
```python
def get_coverage_color(percentage):
    if percentage < 80:
        return "red"
    elif percentage < 90:
        return "yellow"
    elif percentage < 95:
        return "yellowgreen"
    else:
        return "brightgreen"

def get_mypy_color(error_count):
    if error_count == 0:
        return "brightgreen"
    elif error_count <= 5:
        return "yellow"
    else:
        return "red"

def get_performance_color(results):
    statuses = [r["status"] for r in results.values()]
    if any(s == "fail" for s in statuses):
        return "red"
    elif any(s == "warn" for s in statuses):
        return "orange"
    else:
        return "brightgreen"

def get_performance_emoji(results):
    statuses = [r["status"] for r in results.values()]
    if any(s == "fail" for s in statuses):
        return "❌"
    elif any(s == "warn" for s in statuses):
        return "⚠️"
    else:
        return "✓"
```

---

### Step 3: Generate Badge JSON

**Code Example**:
```python
def generate_coverage_badge(percentage):
    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percentage}%",
        "color": get_coverage_color(percentage)
    }

def generate_test_count_badge(test_data):
    badges = []
    
    # Passed badge
    badges.append({
        "schemaVersion": 1,
        "label": "tests",
        "message": f"{test_data['passed']} passed",
        "color": "brightgreen" if test_data["passed"] > 0 else "red"
    })
    
    # Skipped badge
    if test_data["skipped"] > 0:
        badges.append({
            "schemaVersion": 1,
            "label": "tests",
            "message": f"{test_data['skipped']} skipped",
            "color": "yellow"
        })
    
    # Failed badge
    badges.append({
        "schemaVersion": 1,
        "label": "tests",
        "message": f"{test_data['failed']} failed",
        "color": "brightgreen" if test_data["failed"] == 0 else "red"
    })
    
    # Warnings badge
    if test_data["warnings"] > 0:
        badges.append({
            "schemaVersion": 1,
            "label": "tests",
            "message": f"{test_data['warnings']} warnings",
            "color": "yellow"
        })
    
    return badges

def generate_performance_badge(perf_data):
    emoji = get_performance_emoji(perf_data)
    color = get_performance_color(perf_data)
    
    # Format: "S:56ms | M:97ms | L:180ms"
    timings = " | ".join([f"{k}:{v['time_ms']}ms" for k, v in perf_data.items()])
    
    return {
        "schemaVersion": 1,
        "label": f"perf {emoji}",
        "message": timings,
        "color": color
    }
```

---

### Step 4: Save Badge JSON

**Code Example**:
```python
import json
from pathlib import Path

def save_badge(badge_data, output_dir, filename):
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(badge_data, f, indent=2)

# Example usage
coverage_badge = generate_coverage_badge(79.2)
save_badge(coverage_badge, "badges", "coverage.json")
```

---

## Badge Display in README

### Markdown Format

```markdown
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/K4M1coder/ansible-doctor-enhanced/dev/badges/coverage.json)
```

**URL Structure**:
- Base: `https://img.shields.io/endpoint?url=`
- Badge JSON URL: `https://raw.githubusercontent.com/.../badges/coverage.json`

**Alternative (Gist)**:
```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/abc123/raw/coverage.json)
```

---

### Badge Order in README

**Recommended Order** (ansible-doctor-enhanced):

1. Version (static)
2. License (static)
3. Python version (static)
4. Code style: Black (static)
5. Imports: isort (static)
6. Linter: Ruff (static)
7. Type checking: mypy (dynamic)
8. Coverage (dynamic)
9. Tests passed (dynamic)
10. Tests skipped (dynamic)
11. Tests failed (dynamic)
12. Tests warnings (dynamic)
13. Performance (dynamic)
14. Pre-commit status (GitHub native)
15. CI Windows status (GitHub native)
16. Badges status (GitHub native)

**Rationale**:
- Static first (project info)
- Code quality tools next (developer-focused)
- Test metrics (CI-focused)
- CI status last (workflow health)

---

## Badge Update Frequency

| Badge Type | Update Frequency | Trigger |
|------------|------------------|---------|
| Static (version, license, Python) | Manual | When values change |
| Code style (Black, isort, Ruff) | Never | Always ✓ |
| mypy | Per commit | Pre-commit hook + CI |
| Coverage | Per CI run | CI Windows workflow |
| Test counts | Per CI run | CI Windows workflow |
| Performance | Per CI run | CI Windows workflow |
| CI status | Per workflow | GitHub native |

---

## Badge Caching

### Shields.io Caching

**Default**: 300 seconds (5 minutes)

**Recommendation**: Set `cacheSeconds: 3600` (1 hour) for stable metrics.

**Why**: Reduces Shields.io load, improves badge load times.

**Example**:
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "79%",
  "color": "yellow",
  "cacheSeconds": 3600
}
```

---

## Troubleshooting Badges

### Issue 1: Badge Shows "invalid"

**Symptom**: Badge displays "invalid" instead of expected value.

**Cause**: Badge JSON format error or URL inaccessible.

**Solutions**:
1. Validate JSON syntax: `jq . badges/coverage.json`
2. Check URL accessibility: `curl <badge-json-url>`
3. Ensure `schemaVersion: 1` is present
4. Verify all required fields: `schemaVersion`, `label`, `message`, `color`

---

### Issue 2: Badge Not Updating

**Symptom**: Badge shows old value after CI completes.

**Cause**: Caching (Shields.io or browser).

**Solutions**:
1. Wait 5 minutes (default cache expiry)
2. Force refresh: `Ctrl+Shift+R` (browser)
3. Check badge workflow logs (ensure new JSON uploaded)
4. Verify badge JSON URL points to latest commit

---

### Issue 3: Badge Color Wrong

**Symptom**: Badge shows green but metric is bad (e.g., 50% coverage).

**Cause**: Color rule logic error in badge generation script.

**Solutions**:
1. Review `get_*_color()` functions in generate_badge_metrics.py
2. Add unit tests for color rules
3. Manually verify badge JSON: `cat badges/coverage.json`

---

### Issue 4: Emoji Not Displaying

**Symptom**: Performance badge shows `?` instead of emoji.

**Cause**: Encoding issue (Windows) or font issue.

**Solutions**:
1. Ensure UTF-8 encoding in badge generation script
2. Use Unicode escape sequences: `\u2705` (✓), `\u26a0` (⚠️), `\u274c` (❌)
3. Verify GitHub renders emojis correctly (test in README)

---

## Badge Quality Checklist

Use this checklist when adding a new badge:

- [ ] Badge JSON follows Shields.io endpoint schema
- [ ] All required fields present: `schemaVersion`, `label`, `message`, `color`
- [ ] Label is concise (<20 characters)
- [ ] Message is readable (<30 characters)
- [ ] Color follows project color rules (see categories above)
- [ ] `cacheSeconds` set to 3600 for stable metrics
- [ ] Badge generation script has color rule function
- [ ] Badge generation script has unit tests
- [ ] Badge JSON saved to badges/ directory
- [ ] Badge displayed in README in correct order
- [ ] Badge tested locally before commit
- [ ] Badge documented in specs/014-code-quality-cicd/spec.md

---

## Complete Badge Set (16 Badges)

**Static (3)**:
1. Version: `0.8.0` (blue)
2. License: `Apache-2.0` (blue)
3. Python: `3.11 | 3.13` (blue)

**Code Quality (4)**:
4. Black: `black` (black)
5. isort: `isort` (blue)
6. Ruff: `ruff` (blue)
7. mypy: `0 errors` (green/yellow/red)

**Test Metrics (6)**:
8. Coverage: `79%` (red/yellow/green based on %)
9. Tests Passed: `184 passed` (green)
10. Tests Skipped: `3 skipped` (yellow)
11. Tests Failed: `0 failed` (green/red)
12. Tests Warnings: `2 warnings` (yellow)
13. Performance: `perf ✓ - S:56ms | M:97ms | L:180ms` (green/orange/red)

**CI Status (3)**:
14. Pre-commit: GitHub workflow badge
15. CI Windows: GitHub workflow badge
16. Badges: GitHub workflow badge

---

**Last Updated**: 2026-01-10  
**Version**: 1.0  
**Maintainer**: GitHub Copilot
