# Research Findings: Error Reports & Recovery

**Date**: 2025-12-03  
**Feature**: Spec 010 - Error Reports & Recovery

## 1. SARIF 2.1.0 Format Specification

### Decision

Adopt SARIF 2.1.0 as the IDE-friendly output format with full schema compliance.

### Rationale

- **Industry Standard**: SARIF is OASIS standard for static analysis results, supported by GitHub, VS Code, Azure DevOps
- **Rich Metadata**: Supports code locations, fix suggestions, rule metadata, related locations
- **Tool Interoperability**: IDEs can consume SARIF from any tool without custom parsers
- **Extensibility**: Allows tool-specific properties while maintaining core compatibility

### Key Findings

- **Required Fields**: `version`, `runs[]`, `runs[].tool.driver.name`, `runs[].results[]`
- **Result Levels**: `error`, `warning`, `note`, `none` (maps to our E/W code prefixes)
- **Physical Locations**: Support file URI, line/column ranges, context regions
- **Fixes**: Can include automated fix suggestions with replacement text
- **IDE Support**:
  - VS Code: SARIF Viewer extension (Microsoft official)
  - IntelliJ/PyCharm: SARIF support via plugins
  - GitHub: Native SARIF upload in code scanning

### Alternatives Considered

- **JSON Lines**: Simpler but no IDE integration, requires custom parsing
- **LSP Diagnostics**: Requires language server, too heavyweight for CLI tool
- **Custom XML**: No tooling support, reinventing the wheel

### Implementation Notes

- Use `pydantic` model for SARIF schema validation
- Include `informationUri` pointing to our documentation
- Map error codes to `ruleId` field
- Include context lines in `region.snippet.text`

---

## 2. Error Code Numbering Conventions

### Decision

Hierarchical error codes with category prefixes: `E1xx` (parsing), `E2xx` (validation), `E3xx` (generation), `E4xx` (I/O). Warnings use `W1xx-W4xx`.

### Rationale

- **Scannable**: Prefix indicates error category at a glance
- **Extensible**: Room for 99 errors per category (E101-E199)
- **Industry Standard**: Matches Ansible, Python linters (flake8, pylint), ESLint patterns
- **Stable**: Can add new codes without breaking existing tooling

### Key Findings

- **Ansible**: Uses `E0xx` for syntax, `E1xx` for variables, etc.
- **Python PEP 8**: `E1xx` indentation, `E2xx` whitespace, `E3xx` blank lines, etc.
- **Rust Compiler**: `E0001-E9999` with hierarchical grouping by feature area
- **TypeScript**: `TS1xxx` syntax, `TS2xxx` semantic, `TS3xxx` options

### Implementation Strategy

```python
# exceptions/codes.py
class ErrorCode(str, Enum):
    # Parsing (E1xx)
    E101 = "YAML syntax error"
    E102 = "Invalid metadata structure"
    E103 = "Unsupported Ansible version"
    
    # Validation (E2xx)
    E201 = "Missing required annotation"
    E202 = "Invalid annotation syntax"
    E203 = "Duplicate annotation key"
    
    # Generation (E3xx)
    E301 = "Template rendering failed"
    E302 = "Output file write error"
    E303 = "Invalid output format"
    
    # I/O (E4xx)
    E401 = "File not found"
    E402 = "Permission denied"
    E403 = "Invalid path"
```

### Stability Guarantee

- Error codes are part of public API
- Never reuse retired codes (mark as deprecated)
- Add codes in gaps (E104, E105) or at end (E199)
- Document code changes in CHANGELOG

---

## 3. Recovery Suggestion Patterns

### Decision

Context-sensitive recovery suggestions with static suggestion database plus dynamic context analysis.

### Rationale

- **User Experience**: Actionable suggestions reduce debugging time
- **Learnability**: Users learn correct patterns from suggestions
- **Automation Potential**: Suggestions can evolve into auto-fixes (future)

### Key Findings

- **ESLint**: `--fix` mode applies auto-fixes for safe rules
- **Rust Compiler**: Detailed "try this instead" code examples
- **Mypy**: "Perhaps you meant X?" with Levenshtein distance
- **Ansible-lint**: Links to rule documentation with examples

### Implementation Strategy

**Static Suggestion Database**:

```python
# exceptions/recovery.py
RECOVERY_SUGGESTIONS = {
    "E101": RecoverySuggestion(
        error_code="E101",
        primary_suggestion="Check YAML indentation. Ansible requires 2-space indents.",
        alternative_suggestions=[
            "Validate YAML syntax with `yamllint tasks/main.yml`",
            "Check for tabs (YAML requires spaces)",
            "Ensure quotes around strings with special characters (: [ ] { })"
        ],
        documentation_link="https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html",
        auto_fixable=False,
    ),
    "E201": RecoverySuggestion(
        error_code="E201",
        primary_suggestion="Add required @meta annotation to file header",
        alternative_suggestions=[
            "Example: @meta description: Role configures web server",
            "See documentation for required annotations",
        ],
        documentation_link="https://ansible-doctor.example.com/annotations",
        auto_fixable=False,  # Future: could insert template
    ),
}
```

**Dynamic Context Analysis**:

- File/variable name typos: Levenshtein distance < 3 → "Did you mean `webserver_port`?"
- Missing imports: Scan available modules → "Import from `ansible.builtin.copy`?"
- Type mismatches: Show expected vs actual types

### Alternatives Considered

- **LLM-based suggestions**: Too slow, requires API key, non-deterministic
- **No suggestions**: User-hostile, increases support burden
- **Auto-fix only**: Risky, could corrupt user files

---

## 4. Error Aggregation Strategies

### Decision

Hash-based deduplication with LRU eviction when max_errors (1000) reached. Keep first occurrence of each unique error.

### Rationale

- **Memory Bounded**: Cap at 1000 errors prevents OOM on large codebases
- **Performance**: Hash-based lookup is O(1), minimal overhead
- **User Value**: First occurrence often most informative (root cause)

### Key Findings

- **Rust Compiler**: Caps at 100 errors by default (`--error-limit`)
- **TypeScript**: No hard cap, but emits summary after 100 errors
- **GCC**: `-fmax-errors=N` flag (default unlimited)
- **Mypy**: `--show-error-end` collapses duplicate errors

### Implementation Strategy

**Deduplication Key**:

```python
def error_hash(entry: ErrorEntry) -> str:
    """Generate unique hash for error deduplication."""
    return hashlib.sha256(
        f"{entry.code}:{entry.file}:{entry.line}:{entry.message}".encode()
    ).hexdigest()[:16]
```

**Eviction Policy**:

- When max_errors reached, stop collecting new unique errors
- Continue counting duplicates of existing errors
- Emit warning: "Max errors reached (1000), further errors suppressed"

**Grouping Display**:

```
Errors by Category:
  Parsing (E1xx):      45 errors
  Validation (E2xx):   123 errors
  Generation (E3xx):   2 errors

Top 5 Errors:
  E201 (Missing annotation): 78 occurrences
  E101 (YAML syntax):        23 occurrences
  E402 (Permission denied):  12 occurrences
```

### Performance Impact

- Hash computation: ~1μs per error (negligible)
- Memory: ~2KB per unique error × 1000 = 2MB max
- Acceptable overhead for CLI tool

---

## 5. IDE Integration Standards

### Decision

Provide SARIF 2.1.0 output for IDE Problems panel integration. Support VS Code, PyCharm, IntelliJ via standard formats.

### Rationale

- **Developer Workflow**: Errors appear in IDE where code is edited
- **Quick Fixes**: IDEs can present recovery suggestions as code actions
- **Navigation**: Click error → jump to file/line
- **Persistence**: Error panel survives across terminal sessions

### Key Findings

**VS Code Problems API**:

- Consumes SARIF via SARIF Viewer extension
- Maps `result.level` to severity icons (red X, yellow triangle)
- Displays `message.text` in problems panel
- Links `physicalLocation.artifactLocation.uri` to editor

**Language Server Protocol (LSP)**:

- Diagnostic format: `{range, severity, message, source, code}`
- Real-time diagnostics require language server (out of scope)
- CLI tools use file-based integration (SARIF, checkstyle XML)

**IDE Support Matrix**:

| IDE | SARIF Support | Notes |
| ----- | --------------- | ------- |
| VS Code | ✅ Native (SARIF Viewer) | Official Microsoft extension |
| IntelliJ IDEA | ✅ Plugin | Qodana SARIF viewer |
| PyCharm | ✅ Plugin | Qodana SARIF viewer |
| Vim/Neovim | ⚠️ Manual | Parse JSON with jq/ALE |
| Emacs | ⚠️ Manual | Flycheck custom checker |

### Implementation Notes

- Generate `.sarif` file in project root or specified path
- Include `invocations[].executionSuccessful` for build status
- Add `artifacts[]` for file index (speeds up IDE loading)
- Use `file://` URIs for absolute paths, relative paths for portability

### User Flow

```bash
# Generate SARIF report
ansible-doctor generate . --error-format sarif --error-output results.sarif

# VS Code: Open Command Palette → "SARIF: Open SARIF file" → results.sarif
# PyCharm: File → Open → results.sarif → View in Problems panel
```

---

## Summary

| Topic | Decision | Rationale |
| ------- | ---------- | ----------- |
| **Output Format** | SARIF 2.1.0 | Industry standard, IDE support, rich metadata |
| **Error Codes** | Hierarchical E1xx-E4xx, W1xx-W4xx | Scannable, extensible, stable |
| **Recovery** | Static DB + dynamic context | Actionable, learnable, automation-ready |
| **Aggregation** | Hash-based dedup, 1000 cap | Memory bounded, O(1) lookup, root cause focus |
| **IDE Integration** | SARIF file + Problems panel | Developer workflow, quick fixes, navigation |

All decisions align with constitution gates (TDD, library-first, CLI mandate, observability).
