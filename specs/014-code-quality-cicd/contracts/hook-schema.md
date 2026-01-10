# Pre-commit Hook Schema

**Feature**: 014-code-quality-cicd  
**Purpose**: Define the structure and requirements for pre-commit hooks  
**Last Updated**: 2026-01-10

---

## Hook Configuration Schema

### YAML Structure

```yaml
repos:
  - repo: <repository_url>        # Required: URL or 'local'
    rev: <version>                # Required for remote repos, N/A for local
    hooks:
      - id: <hook_id>             # Required: Unique identifier
        name: <hook_name>         # Optional: Display name (defaults to id)
        entry: <command>          # Required: Command to execute
        language: <language>      # Required: Hook environment (python, system, node, etc.)
        types: [<file_type>]      # Optional: File types to run on (python, markdown, yaml)
        types_or: [<file_type>]   # Optional: Alternative to types (OR logic)
        files: <pattern>          # Optional: Regex pattern for files to include
        exclude: <pattern>        # Optional: Regex pattern for files to exclude
        stages: [<stage>]         # Optional: Stages to run on (pre-commit, pre-push, etc.)
        pass_filenames: <bool>    # Optional: Pass filenames to entry command (default: true)
        additional_dependencies: [<pkg>]  # Optional: Dependencies for hook
        args: [<arg>]             # Optional: Arguments to pass to entry
        always_run: <bool>        # Optional: Run even if no files match (default: false)
        verbose: <bool>           # Optional: Show output even on success (default: false)
        require_serial: <bool>    # Optional: Run serially, not in parallel (default: false)
```

---

## Field Definitions

### Required Fields

#### `repo`
- **Type**: String (URL or 'local')
- **Description**: Source repository for the hook
- **Valid Values**:
  - Remote URL: `https://github.com/owner/repo`
  - Local: `local` (for project-specific hooks)
- **Examples**:
  ```yaml
  repo: https://github.com/psf/black
  repo: local
  ```

#### `rev` (for remote repos)
- **Type**: String (version tag)
- **Description**: Version of the remote repository to use
- **Valid Values**: Git tag, branch, or commit SHA
- **Examples**:
  ```yaml
  rev: 24.4.0
  rev: v1.8.0
  rev: main  # Not recommended, prefer pinned versions
  ```
- **Note**: Not applicable for `repo: local`

#### `id`
- **Type**: String
- **Description**: Unique identifier for the hook
- **Naming Convention**: lowercase-with-hyphens
- **Examples**:
  ```yaml
  id: black
  id: pytest-precommit
  id: update-readme-toc
  ```

#### `entry`
- **Type**: String (command)
- **Description**: Command to execute
- **Valid Values**:
  - Binary name: `black`
  - Script path: `python scripts/my_script.py`
  - Full command: `poetry run pytest`
- **Examples**:
  ```yaml
  entry: black
  entry: python scripts/sync_version.py
  entry: poetry run mypy ansibledoctor/
  ```

#### `language`
- **Type**: String (enum)
- **Description**: Environment for running the hook
- **Valid Values**:
  - `python`: Python environment (isolated)
  - `system`: System Python/commands
  - `node`: Node.js environment
  - `docker`: Docker container
  - `script`: Shell script
- **Examples**:
  ```yaml
  language: python
  language: system
  ```

---

### Optional Fields

#### `name`
- **Type**: String
- **Description**: Display name for the hook (shown in output)
- **Default**: Value of `id`
- **Examples**:
  ```yaml
  name: "Black Code Formatter"
  name: "mypy (ansibledoctor only)"
  ```

#### `types` / `types_or`
- **Type**: Array of strings
- **Description**: File types to run on
- **Valid Values**: `python`, `markdown`, `yaml`, `toml`, `json`, `text`, etc.
- **Difference**:
  - `types`: All types must match (AND logic)
  - `types_or`: Any type matches (OR logic)
- **Examples**:
  ```yaml
  types: [python]
  types_or: [python, pyi]
  ```

#### `files`
- **Type**: String (regex pattern)
- **Description**: Include only files matching this pattern
- **Examples**:
  ```yaml
  files: ^ansibledoctor/
  files: \.(py|pyi)$
  files: ^(scripts|ansibledoctor)/
  ```

#### `exclude`
- **Type**: String (regex pattern)
- **Description**: Exclude files matching this pattern
- **Examples**:
  ```yaml
  exclude: ^tests/
  exclude: \.pyc$
  exclude: ^(tests|demo)/
  ```

#### `stages`
- **Type**: Array of strings
- **Description**: Git stages when hook should run
- **Valid Values**:
  - `pre-commit`: Before commit (fast checks)
  - `pre-push`: Before push (expensive checks)
  - `pre-merge-commit`: Before merge commit
  - `pre-rebase`: Before rebase
  - `manual`: Only when explicitly run
- **Default**: `[pre-commit]`
- **Examples**:
  ```yaml
  stages: [pre-commit]
  stages: [pre-push]
  stages: [pre-commit, pre-push]
  ```

#### `pass_filenames`
- **Type**: Boolean
- **Description**: Pass matched filenames to entry command
- **Default**: `true`
- **Use Cases**:
  - `true`: Run on specific files (e.g., `black file1.py file2.py`)
  - `false`: Run on entire project (e.g., `python scripts/sync_version.py`)
- **Examples**:
  ```yaml
  pass_filenames: true   # Default
  pass_filenames: false  # For project-wide checks
  ```

#### `additional_dependencies`
- **Type**: Array of strings (package names with optional versions)
- **Description**: Dependencies to install in hook environment
- **Format**: `package>=version` or `package==version`
- **Critical**: Must include ALL dependencies (environment is isolated)
- **Examples**:
  ```yaml
  additional_dependencies:
    - requests>=2.28
    - beautifulsoup4>=4.11
    - types-requests
  ```

#### `args`
- **Type**: Array of strings
- **Description**: Arguments to pass to entry command
- **Examples**:
  ```yaml
  args: [--fix]
  args: [--config, pyproject.toml]
  args: [-r, ansibledoctor/, --skip, B101]
  ```

#### `always_run`
- **Type**: Boolean
- **Description**: Run even if no files match (useful for project-wide checks)
- **Default**: `false`
- **Examples**:
  ```yaml
  always_run: true  # For version sync, TOC update
  ```

#### `verbose`
- **Type**: Boolean
- **Description**: Show output even on success
- **Default**: `false`
- **Examples**:
  ```yaml
  verbose: true  # For debugging
  ```

#### `require_serial`
- **Type**: Boolean
- **Description**: Run serially, not in parallel
- **Default**: `false`
- **Use Cases**: When hooks have dependencies on each other
- **Examples**:
  ```yaml
  require_serial: true  # For database migrations, etc.
  ```

---

## Hook Groups

### Group 1: Basic Formatting
**Stage**: `pre-commit`  
**Purpose**: Fast, universal file formatting

```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
    - id: trailing-whitespace
      types: [python, markdown, yaml, toml]
    - id: end-of-file-fixer
      types: [python, markdown, yaml, toml]
    - id: check-yaml
      exclude: ^tests/fixtures/
```

**Rationale**: These checks are fast (<1s) and apply to all file types.

---

### Group 2: Python Formatting
**Stage**: `pre-commit`  
**Purpose**: Enforce consistent Python code style

```yaml
- repo: https://github.com/psf/black
  rev: 24.4.0
  hooks:
    - id: black
      language_version: python3.11

- repo: https://github.com/pycqa/isort
  rev: 5.13.0
  hooks:
    - id: isort
      args: [--profile, black]
```

**Rationale**: Black and isort must run on pre-commit to catch formatting issues early.

---

### Group 3: Linting
**Stage**: `pre-commit`  
**Purpose**: Catch common code issues

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.1.0
  hooks:
    - id: ruff
      args: [--fix]
```

**Rationale**: Ruff is fast (<2s) and auto-fixes most issues.

---

### Group 4: Type Checking
**Stage**: `pre-commit`  
**Purpose**: Static type checking

```yaml
- repo: local
  hooks:
    - id: mypy
      name: mypy
      entry: poetry run mypy
      language: system
      types: [python]
      files: ^ansibledoctor/
      pass_filenames: false
      additional_dependencies:
        - types-PyYAML
        - types-colorama
        - types-Jinja2
        - types-requests
        - types-setuptools
        - types-tabulate
        - types-toml
        - pytest
        - pytest-mock
        - httpx
        - respx
        - types-jsonschema
```

**Rationale**: mypy only on ansibledoctor/ (not tests/) to catch production code issues.

---

### Group 5: Documentation
**Stage**: `pre-commit`  
**Purpose**: Keep documentation synchronized

```yaml
- repo: local
  hooks:
    - id: sync-version
      name: sync-version
      entry: python scripts/sync_version.py
      language: system
      pass_filenames: false
      always_run: true
      additional_dependencies:
        - tomli>=2.0.1

    - id: update-readme-toc
      name: update-readme-toc
      entry: python scripts/update_readme_toc.py
      language: system
      files: ^README\.md$
      pass_filenames: false
      additional_dependencies:
        - md-toc>=9.0.0

    - id: check-changelog-atomic
      name: check-changelog-atomic
      entry: python scripts/validate_atomic_changelog.py
      language: system
      pass_filenames: false
      always_run: true
```

**Rationale**: Documentation must stay in sync with code (version, TOC, changelog).

---

### Group 6: Testing
**Stage**: `pre-push`  
**Purpose**: Comprehensive testing before push

```yaml
- repo: local
  hooks:
    - id: pytest-unit
      name: pytest-unit
      entry: poetry run pytest tests/unit/
      language: system
      pass_filenames: false
      stages: [pre-push]

    - id: pytest-integration
      name: pytest-integration
      entry: poetry run pytest tests/integration/
      language: system
      pass_filenames: false
      stages: [pre-push]

    - id: pytest-performance
      name: pytest-performance
      entry: poetry run pytest tests/performance/
      language: system
      pass_filenames: false
      stages: [pre-push]
      additional_dependencies:
        - requests>=2.28
        - beautifulsoup4>=4.11

    - id: demo-run
      name: demo-run
      entry: python scripts/run_demo_in_precommit.py
      language: system
      pass_filenames: false
      stages: [pre-push]
```

**Rationale**: Full tests are expensive (3-5 min), run only before push to avoid slowing down commits.

---

## Best Practices

### 1. Dependency Management
```yaml
# ❌ BAD: Missing dependency
- id: my-hook
  entry: python scripts/my_script.py
  language: system
  # Script imports 'requests' but not listed

# ✅ GOOD: All dependencies declared
- id: my-hook
  entry: python scripts/my_script.py
  language: system
  additional_dependencies:
    - requests>=2.28
    - beautifulsoup4>=4.11
```

### 2. Stage Separation
```yaml
# ❌ BAD: Slow tests on pre-commit
- id: pytest-all
  entry: poetry run pytest
  language: system
  stages: [pre-commit]  # Too slow!

# ✅ GOOD: Fast checks on pre-commit, slow tests on pre-push
- id: pytest-unit
  entry: poetry run pytest tests/unit/
  language: system
  stages: [pre-push]  # Only run before push
```

### 3. File Patterns
```yaml
# ❌ BAD: Running mypy on tests (strict mode not applicable)
- id: mypy
  entry: poetry run mypy
  language: system
  types: [python]

# ✅ GOOD: Only run mypy on production code
- id: mypy
  entry: poetry run mypy
  language: system
  types: [python]
  files: ^ansibledoctor/
```

### 4. Pass Filenames
```yaml
# ❌ BAD: pass_filenames: true for project-wide check
- id: sync-version
  entry: python scripts/sync_version.py
  pass_filenames: true  # Script doesn't accept file args

# ✅ GOOD: pass_filenames: false for project-wide check
- id: sync-version
  entry: python scripts/sync_version.py
  pass_filenames: false
  always_run: true
```

### 5. Version Pinning
```yaml
# ❌ BAD: Unpinned version (can break)
- repo: https://github.com/psf/black
  rev: main

# ✅ GOOD: Pinned to specific version
- repo: https://github.com/psf/black
  rev: 24.4.0
```

---

## Common Pitfalls

### Pitfall 1: Missing Dependencies
**Symptom**: `ModuleNotFoundError: No module named 'requests'`

**Cause**: Hook runs in isolated environment, dependency not declared.

**Solution**: Add to `additional_dependencies`:
```yaml
- id: my-hook
  entry: python scripts/my_script.py
  additional_dependencies:
    - requests>=2.28
```

---

### Pitfall 2: Slow Pre-commit Hooks
**Symptom**: `git commit` takes >1 minute

**Cause**: Expensive checks (tests, linting large codebase) on pre-commit stage.

**Solution**: Move to pre-push stage:
```yaml
- id: pytest-all
  entry: poetry run pytest
  stages: [pre-push]  # Not pre-commit
```

---

### Pitfall 3: File Pattern Mismatch
**Symptom**: Hook doesn't run on expected files

**Cause**: Incorrect `files:` or `types:` pattern.

**Solution**: Test regex pattern:
```bash
# Test if pattern matches files
pre-commit run my-hook --files ansibledoctor/config/loader.py
```

---

### Pitfall 4: Windows Encoding Issues
**Symptom**: `UnicodeEncodeError: 'charmap' codec can't encode character`

**Cause**: Script prints Unicode characters on Windows (cp1252 default).

**Solution**: Force UTF-8 in script:
```python
import sys
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
```

---

## Validation Checklist

Use this checklist when adding a new hook:

- [ ] `repo` is valid URL or 'local'
- [ ] `rev` is pinned version (if remote repo)
- [ ] `id` is unique and descriptive
- [ ] `entry` command exists and works
- [ ] `language` is correct for hook environment
- [ ] `files` or `types` patterns are correct
- [ ] `stages` appropriate (fast=pre-commit, slow=pre-push)
- [ ] `pass_filenames` correct (true for per-file, false for project-wide)
- [ ] `additional_dependencies` includes ALL dependencies
- [ ] Hook tested locally: `pre-commit run hook-id --all-files`
- [ ] Hook runs in <5 seconds (if pre-commit stage)
- [ ] Hook provides clear error messages on failure
- [ ] Hook documented in .github/COMMIT_QUALITY.md (if complex)

---

## Example: Adding a New Hook

**Goal**: Add `bandit` security linter to pre-commit.

**Step 1: Research**
- Tool: `bandit` (Python security linter)
- Repo: `https://github.com/PyCQA/bandit`
- Latest version: `1.7.5`

**Step 2: Write Configuration**
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: '1.7.5'
  hooks:
    - id: bandit
      name: bandit (security linter)
      args: ['-r', 'ansibledoctor/', '--skip', 'B101']
      exclude: ^tests/
```

**Step 3: Test Locally**
```bash
# Test on all files
pre-commit run bandit --all-files

# Test on specific file
pre-commit run bandit --files ansibledoctor/cli/__main__.py
```

**Step 4: Validate**
- [ ] Hook runs successfully
- [ ] Hook runs in <5 seconds (fast enough for pre-commit)
- [ ] Hook provides clear output
- [ ] Hook doesn't conflict with other hooks

**Step 5: Document**
- Add to specs/014-code-quality-cicd/spec.md
- Add to .github/COMMIT_QUALITY.md if complex
- Update README badges (add security badge)

---

**Last Updated**: 2026-01-10  
**Version**: 1.0  
**Maintainer**: GitHub Copilot
