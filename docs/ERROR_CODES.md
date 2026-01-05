# Error Code Reference

This document provides a comprehensive reference for all error and warning codes in ansible-doctor-enhanced.

## Overview

Error codes follow the pattern `[EW]NNN` where:
- **E** = Error (fatal, blocks processing)
- **W** = Warning (non-fatal, processing continues)
- **NNN** = Three-digit category code

## Error Categories

- **E1xx**: Parsing errors (YAML syntax, file reading)
- **E2xx**: Validation errors (schema violations, missing required fields)
- **E3xx**: Generation errors (template rendering, file writing)
- **E4xx**: I/O errors (file system access, permissions)

## Parsing Errors (E1xx)

### E101: YAML Syntax Error

**Category**: parsing  
**Severity**: error

**Description**: The YAML file contains syntax errors that prevent parsing.

**Common Causes**:
- Missing or extra colons
- Incorrect indentation
- Unclosed quotes or brackets
- Invalid YAML structure

**Example**:
```yaml
# ❌ Bad - extra colon
tasks:
  - name:: Install package
    apt:
      name: nginx
```

**Recovery Suggestion**: Check indentation and YAML syntax. Use a YAML validator.

**Documentation**: [YAML Syntax Guide](https://yaml.org/spec/1.2/spec.html)

---

### E102: File Not Found

**Category**: parsing  
**Severity**: error

**Description**: The specified file or directory does not exist.

**Common Causes**:
- Incorrect file path
- File moved or deleted
- Typo in filename

**Example Error**:
```
[E102] File not found: roles/web/tasks/main.yml
```

**Recovery Suggestion**: Verify the file path exists and is accessible.

---

### E103: Invalid File Format

**Category**: parsing  
**Severity**: error

**Description**: The file format is not supported or cannot be parsed.

**Common Causes**:
- Binary file instead of text
- Corrupted file
- Wrong file extension

**Recovery Suggestion**: Ensure the file is a valid text file in the expected format.

---

### E104: Encoding Error

**Category**: parsing  
**Severity**: error

**Description**: The file encoding is not UTF-8 or cannot be decoded.

**Common Causes**:
- File saved with non-UTF-8 encoding
- Binary data in text file
- Corrupted file

**Recovery Suggestion**: Convert the file to UTF-8 encoding.

---

## Validation Errors (E2xx)

### E201: Missing Required Field

**Category**: validation  
**Severity**: error

**Description**: A required field is missing from the role metadata.

**Common Causes**:
- Incomplete `meta/main.yml`
- Missing required annotations
- Empty required fields

**Example**:
```yaml
# ❌ Bad - missing required 'role_name' in meta/main.yml
galaxy_info:
  author: John Doe
  # role_name is missing!
```

**Recovery Suggestion**: Add the required field to the metadata file.

---

### E202: Invalid Field Value

**Category**: validation  
**Severity**: error

**Description**: A field contains an invalid value according to the schema.

**Common Causes**:
- Wrong data type (string instead of list)
- Value outside allowed range
- Invalid enum value

**Example**:
```yaml
# ❌ Bad - platforms should be a list
galaxy_info:
  platforms: Ubuntu  # Should be [{ name: Ubuntu, versions: [...] }]
```

**Recovery Suggestion**: Check the field type and allowed values in the schema.

---

### E203: Schema Validation Failed

**Category**: validation  
**Severity**: error

**Description**: The document structure does not match the expected schema.

**Recovery Suggestion**: Review the schema requirements and correct the document structure.

---

## Generation Errors (E3xx)

### E301: Template Not Found

**Category**: generation  
**Severity**: error

**Description**: The specified Jinja2 template file cannot be found.

**Common Causes**:
- Template file missing
- Incorrect template path in configuration
- Template directory not configured

**Recovery Suggestion**: Verify the template file exists in the configured template directory.

---

### E302: Template Rendering Error

**Category**: generation  
**Severity**: error

**Description**: An error occurred while rendering the Jinja2 template.

**Common Causes**:
- Undefined variable in template
- Invalid Jinja2 syntax
- Missing filter or function

**Example Error**:
```
[E302] Template error: no filter named 'undefined_filter'
```

**Recovery Suggestion**: Check template syntax and ensure all variables are defined.

---

### E303: Output File Write Error

**Category**: generation  
**Severity**: error

**Description**: Cannot write to the output file.

**Common Causes**:
- Permission denied
- Disk full
- Directory does not exist
- File is read-only

**Recovery Suggestion**: Check file permissions and disk space. Ensure the output directory exists.

---

## I/O Errors (E4xx)

### E401: Permission Denied

**Category**: io  
**Severity**: error

**Description**: Insufficient permissions to read or write a file.

**Recovery Suggestion**: Check file permissions and ensure the user has appropriate access rights.

---

### E402: Disk Full

**Category**: io  
**Severity**: error

**Description**: No space left on device to write output files.

**Recovery Suggestion**: Free up disk space and try again.

---

### E403: Path Too Long

**Category**: io  
**Severity**: error

**Description**: The file path exceeds the maximum length allowed by the operating system.

**Recovery Suggestion**: Shorten the file path or move files to a location with a shorter path.

---

## Warning Codes (W1xx-W4xx)

Warnings follow the same category structure as errors but with 'W' prefix.

### W101: Deprecated Syntax

**Category**: parsing  
**Severity**: warning

**Description**: The file uses deprecated syntax that may not be supported in future versions.

**Recovery Suggestion**: Update to the current syntax. See migration guide for details.

---

### W201: Missing Optional Field

**Category**: validation  
**Severity**: warning

**Description**: An optional but recommended field is missing.

**Example**:
```yaml
# ⚠️ Warning - missing recommended 'license' field
galaxy_info:
  author: John Doe
  role_name: my_role
  # license: MIT  # Recommended but optional
```

**Recovery Suggestion**: Add the recommended field to improve role quality.

---

### W202: Inconsistent Style

**Category**: validation  
**Severity**: warning

**Description**: The code style is inconsistent with project conventions.

**Recovery Suggestion**: Run a linter to fix style issues automatically.

---

### W301: Template Deprecated Variable

**Category**: generation  
**Severity**: warning

**Description**: The template uses a deprecated variable name.

**Recovery Suggestion**: Update variable names to use current naming conventions.

---

## Error Suppression

You can suppress specific error codes using the `--ignore-codes` flag or configuration:

### CLI Usage

```bash
# Suppress single error code
ansible-doctor --ignore-codes E201

# Suppress multiple error codes
ansible-doctor --ignore-codes E201,W101,W202
```

### Configuration File

```yaml
# .ansibledoctor.yml
ignore_codes:
  - E201  # Allow missing optional fields
  - W101  # Ignore deprecated syntax warnings
  - W202  # Skip style consistency checks
```

## Error Output Formats

### Terminal Output (Default)

```
[E101] YAML syntax error: expected <block end>, but found ':' [line 15, col 3]
    💡 Check indentation and YAML syntax at line 15
    📖 https://docs.ansible-doctor.com/errors/E101
```

### Verbose Output (`--verbose`)

Includes source context and stack traces:

```
[E302] Template error: no filter named 'undefined_filter' [line 5, col 47]
    💡 Check template syntax and available filters

    Source Context:
        # Configuration file
        hostname: {{ ansible_hostname }}
        ip_address: {{ ansible_default_ipv4.address }}
      > invalid_syntax: {{ inventory_hostname | undefined_filter }}
        # End of template

    Stack Trace:
        File "template.j2", line 5, in top-level template code
        jinja2.exceptions.UndefinedError: no filter named 'undefined_filter'
```

### SARIF Format (IDE Integration)

For use with VS Code, IntelliJ IDEA, and other IDEs supporting SARIF 2.1.0:

```bash
ansible-doctor --error-format sarif --error-output errors.sarif
```

The SARIF file enables:
- Clickable error locations in IDE
- Integration with Problems panel
- Code navigation from errors
- Automated CI/CD reporting

### JSON Format

Machine-readable output for CI/CD pipelines:

```bash
ansible-doctor --error-format json --error-output errors.json
```

## Best Practices

### 1. Address Errors Before Warnings

Focus on fixing errors (E-codes) first, as they block successful processing. Warnings can be addressed iteratively.

### 2. Use Error Suppression Judiciously

Only suppress errors when:
- You understand the implications
- The error is a false positive
- You have a documented reason

### 3. Enable Verbose Mode for Debugging

Use `--verbose` to get detailed context:

```bash
ansible-doctor --verbose roles/my_role
```

### 4. Integrate with CI/CD

Use SARIF or JSON output for automated quality gates:

```yaml
# GitHub Actions example
- name: Check Ansible Role Documentation
  run: |
    ansible-doctor --error-format sarif --error-output errors.sarif roles/
    if [ -s errors.sarif ]; then
      echo "Documentation errors found"
      exit 1
    fi
```

### 5. Document Suppressed Errors

When suppressing errors, document why:

```yaml
# .ansibledoctor.yml
ignore_codes:
  - E201  # Suppressed: Project allows minimal role metadata
  - W202  # Suppressed: Legacy codebase uses different style
```

## Getting Help

If you encounter an error not documented here or need clarification:

1. Check the [FAQ](https://docs.ansible-doctor.com/faq)
2. Search [GitHub Issues](https://github.com/yourusername/ansible-doctor-enhanced/issues)
3. Open a new issue with error details and context
4. Include the full error message and relevant file snippets

## Version History

- **v0.10.0**: Added comprehensive error reporting with SARIF support, source context, and stack traces (Spec 010)
- **v0.9.0**: Added execution reports and structured logging (Spec 009)
- **v0.5.0**: Initial error code system
