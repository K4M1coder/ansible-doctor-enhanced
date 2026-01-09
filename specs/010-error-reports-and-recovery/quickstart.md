# Quickstart: Error Reports & Recovery

**Date**: 2025-12-03  
**Feature**: Spec 010 - Error Reports & Recovery

## Overview

This quickstart demonstrates how to use ansible-doctor's error reporting and recovery features to systematically identify and fix issues in Ansible content.

---

## Basic Usage

### Default Behavior (Fail Fast)

```bash
# Default: stop on first error, output to stderr
ansible-doctor generate roles/webserver
```

**Output** (stderr):

```text
❌ [E101] YAML syntax error
  File: roles/webserver/tasks/main.yml
  Line: 15, Column: 5
  
  💡 Check YAML indentation. Ansible requires 2-space indents.
  📚 https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html

Error: Documentation generation failed
```

**Exit Code**: `1` (error)

---

### Continue on Error (Partial Success)

```bash
# Collect all errors, generate partial documentation
ansible-doctor generate roles/webserver --continue-on-error
```

**Behavior**:

- Processes all files even after errors
- Generates documentation for valid files
- Aggregates all errors in final report
- Exit code `1` if any errors, `2` if warnings only

**Output** (stderr):

```text
⚠️  Processing continues despite errors...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ ERRORS: 5 | ⚠️  WARNINGS: 12 | ✅ PARTIAL SUCCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[E101] YAML syntax error (3 occurrences)
  Most recent: roles/webserver/tasks/main.yml:15
  
[E201] Missing required annotation (2 occurrences)
  Most recent: roles/database/defaults/main.yml:1

[... additional errors ...]

📄 Generated: README.md (partial)
📄 Skipped: 3 files due to errors
```

---

## Output Formats

### Text Format (Default)

Human-readable output for terminal:

```bash
ansible-doctor generate . --error-format text
```

See "Basic Usage" above for example output.

---

### JSON Format

Machine-readable for CI/CD pipelines:

```bash
ansible-doctor generate . \
  --continue-on-error \
  --error-format json \
  --error-output errors.json
```

**errors.json**:

```json
{
  "correlation_id": "01HN7XYKFQJBM3N8YXRW5PTGAQ",
  "timestamp": "2025-12-03T10:30:45.123456Z",
  "errors": [
    {
      "code": "E101",
      "severity": "error",
      "category": "parsing",
      "message": "YAML syntax error",
      "file": "roles/webserver/tasks/main.yml",
      "line": 15,
      "recovery_suggestions": [
        "Check YAML indentation. Ansible requires 2-space indents."
      ]
    }
  ],
  "error_count": 5,
  "warning_count": 12,
  "partial_success": true
}
```

**CI/CD Integration** (GitHub Actions):

```yaml
- name: Generate documentation
  run: |
    ansible-doctor generate . \
      --continue-on-error \
      --error-format json \
      --error-output errors.json
  
- name: Parse errors
  if: failure()
  run: |
    jq -r '.errors[] | "::error file=\(.file),line=\(.line)::\(.message)"' errors.json
```

---

### SARIF Format (IDE Integration)

IDE-friendly format for VS Code, PyCharm, IntelliJ:

```bash
ansible-doctor generate . \
  --error-format sarif \
  --error-output results.sarif
```

**VS Code Integration**:

1. Install "SARIF Viewer" extension (Microsoft)
2. Open Command Palette (`Ctrl+Shift+P`)
3. Select "SARIF: Open SARIF file"
4. Choose `results.sarif`
5. Errors appear in Problems panel (`Ctrl+Shift+M`)

**PyCharm/IntelliJ Integration**:

1. Install "Qodana SARIF Viewer" plugin
2. File → Open → `results.sarif`
3. Errors appear in Problems tool window

**results.sarif** (abbreviated):

```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {
      "driver": {
        "name": "ansible-doctor",
        "version": "0.9.0"
      }
    },
    "results": [{
      "ruleId": "E101",
      "level": "error",
      "message": {"text": "YAML syntax error"},
      "locations": [{
        "physicalLocation": {
          "artifactLocation": {"uri": "roles/webserver/tasks/main.yml"},
          "region": {"startLine": 15}
        }
      }]
    }]
  }]
}
```

---

## Error Recovery Workflow

### Step 1: Collect All Errors

```bash
# Generate comprehensive error report
ansible-doctor generate . \
  --continue-on-error \
  --error-format text \
  --error-output error-report.txt
```

### Step 2: Review Error Summary

```bash
# View aggregated errors by category
cat error-report.txt | grep "Summary by Category"
```

**Output**:

```text
Summary by Category:
  Parsing (E1xx):      12 errors
  Validation (E2xx):   8 errors
  Generation (E3xx):   0 errors
  I/O (E4xx):          2 errors
```

**Priority**: Fix parsing errors first (E1xx), then validation (E2xx).

### Step 3: Fix Individual Errors

Focus on most common error first:

```bash
# Find all E101 (YAML syntax) errors
cat error-report.txt | grep -A 10 "\[E101\]"
```

**Example**:

```text
[E101] YAML syntax error
  File: roles/webserver/tasks/main.yml
  Line: 15, Column: 5
  
  💡 Suggestions:
    1. Check YAML indentation. Ansible requires 2-space indents.
    2. Validate YAML syntax with `yamllint tasks/main.yml`
```

**Action**:

```bash
# Validate YAML
yamllint roles/webserver/tasks/main.yml

# Fix indentation (add colon after "name")
sed -i '15s/name nginx/name: nginx/' roles/webserver/tasks/main.yml
```

### Step 4: Re-run and Verify

```bash
# Re-run to verify fix
ansible-doctor generate . --continue-on-error

# Check if error count decreased
echo "Errors fixed: $((OLD_ERROR_COUNT - NEW_ERROR_COUNT))"
```

### Step 5: Repeat Until Clean

```bash
# Goal: zero errors and warnings
ansible-doctor generate .
# Exit code 0 = success! 🎉
```

---

## Advanced Usage

### Limit Error Collection

```bash
# Cap at 100 errors (faster on large projects)
ansible-doctor generate . \
  --continue-on-error \
  --max-errors 100
```

**Output**:

```text
⚠️  Max errors reached (100), further errors suppressed.
See error report for details.
```

### Correlation ID Tracking

```bash
# Link error report to execution report (Spec 009)
CORRELATION_ID=$(uuidgen)

ansible-doctor generate . \
  --correlation-id "$CORRELATION_ID" \
  --continue-on-error \
  --error-output "errors-$CORRELATION_ID.json" \
  --report-output "report-$CORRELATION_ID.json"

# Both reports share same correlation_id
jq -r '.correlation_id' "errors-$CORRELATION_ID.json"
jq -r '.correlation_id' "report-$CORRELATION_ID.json"
```

### Filter Errors by Code

```bash
# Show only validation errors (E2xx)
ansible-doctor generate . \
  --error-format json \
  --error-output errors.json

jq '.errors[] | select(.code | startswith("E2"))' errors.json
```

---

## Error Code Reference

### Parsing Errors (E1xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E101 | YAML syntax error | Indentation, missing colons, special characters |
| E102 | Invalid metadata structure | Malformed galaxy_info, meta/main.yml issues |
| E103 | Unsupported Ansible version | Version constraints not met |
| E104 | Invalid task syntax | Missing `name`, invalid module parameters |
| E105 | Circular role dependency | Role depends on itself (direct or indirect) |

### Validation Errors (E2xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E201 | Missing required annotation | No `@meta description` or `@var` for defaults |
| E202 | Invalid annotation syntax | Typo in annotation keyword, wrong format |
| E203 | Duplicate annotation key | Same annotation key repeated |
| E204 | Invalid annotation value | Value doesn't match expected type/format |
| E205 | Conflicting annotations | Mutually exclusive annotations present |

### Generation Errors (E3xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E301 | Template rendering failed | Jinja2 syntax error, undefined variable |
| E302 | Output file write error | Permission denied, disk full |
| E303 | Invalid output format | Unsupported format requested |
| E304 | Unsupported template variable | Template uses unavailable data |
| E305 | Template syntax error | Jinja2 parsing error |

### I/O Errors (E4xx)

| Code | Description | Common Causes |
| ------ | ------------- | --------------- |
| E401 | File not found | Missing required file (meta/main.yml, defaults/main.yml) |
| E402 | Permission denied | Insufficient permissions to read/write file |
| E403 | Invalid path | Path contains invalid characters or too long |
| E404 | Directory not found | Expected directory missing (tasks/, defaults/) |
| E405 | Disk full | Insufficient disk space for output |

### Warnings (W1xx-W4xx)

| Code | Description | Action |
| ------ | ------------- | -------- |
| W101 | Deprecated YAML syntax | Update to current Ansible syntax |
| W201 | Missing recommended annotation | Add `@var` descriptions for better docs |
| W202 | Deprecated annotation syntax | Update to current annotation format |
| W301 | Output file already exists | Use `--force` to overwrite |

---

## Best Practices

### 1. Run with `--continue-on-error` First

Collect all errors in one pass instead of fixing one at a time:

```bash
# ❌ Slow: Fix one error, re-run, repeat
ansible-doctor generate .  # Error 1
# ... fix ...
ansible-doctor generate .  # Error 2
# ... fix ...

# ✅ Fast: Collect all errors, fix batch
ansible-doctor generate . --continue-on-error > errors.txt
# ... fix all errors ...
ansible-doctor generate .  # Verify all fixed
```

### 2. Use SARIF in IDEs

Enable real-time error navigation:

```bash
# Generate SARIF once
ansible-doctor generate . \
  --error-format sarif \
  --error-output results.sarif

# Open in IDE → Problems panel
# Click error → jump to line
# Fix → re-run → refresh
```

### 3. Integrate in CI/CD

Fail build on errors, but allow warnings:

```yaml
# .github/workflows/docs.yml
- name: Generate documentation
  run: |
    ansible-doctor generate . \
      --error-format json \
      --error-output errors.json \
      --continue-on-error
  
- name: Check error count
  run: |
    ERROR_COUNT=$(jq '.error_count' errors.json)
    if [ "$ERROR_COUNT" -gt 0 ]; then
      echo "::error::$ERROR_COUNT errors found"
      jq -r '.errors[] | "::error file=\(.file),line=\(.line)::\(.message)"' errors.json
      exit 1
    fi
```

### 4. Track Error Trends

Monitor error counts over time:

```bash
# Store historical data
DATE=$(date +%Y-%m-%d)
ansible-doctor generate . \
  --error-format json \
  --error-output "errors-$DATE.json"

# Compare trends
jq '.error_count' errors-*.json | awk '{print NR, $1}' | gnuplot -e "plot '-'"
```

---

## Troubleshooting

### Problem: Too Many Errors

**Symptom**: Output shows "Max errors reached (1000)"

**Solution**:

```bash
# Increase cap (use cautiously, may consume memory)
ansible-doctor generate . --max-errors 5000

# Or filter by category first
ansible-doctor generate . \
  --error-format json \
  --error-output errors.json

# Fix parsing errors first
jq '.errors[] | select(.code | startswith("E1"))' errors.json
```

### Problem: Errors Not Appearing in IDE

**Symptom**: SARIF file generated but no errors in Problems panel

**Solution**:

1. Verify SARIF extension installed (VS Code: "SARIF Viewer")
2. Check file paths are absolute or relative to workspace root
3. Validate SARIF schema:

   ```bash
   jq -e '.version == "2.1.0"' results.sarif
   ```

4. Re-open SARIF file: Command Palette → "SARIF: Open SARIF file"

### Problem: Unhelpful Error Messages

**Symptom**: Error message lacks context or suggestions

**Solution**:

```bash
# Enable debug logging for more context
ansible-doctor generate . --log-level debug

# Check related errors
jq '.errors[] | select(.code == "E201") | .related_errors' errors.json

# Read documentation link
jq -r '.errors[0].recovery_suggestions[]' errors.json
```

---

## See Also

- [Spec 010: Error Reports & Recovery](./spec.md) - Full feature specification
- [Spec 009: Execution Reports & Logs](../009-execution-reports-and-logs/spec.md) - Execution telemetry
- [SARIF 2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Ansible Error Codes](https://docs.ansible.com/ansible/latest/reference_appendices/error_codes.html)
