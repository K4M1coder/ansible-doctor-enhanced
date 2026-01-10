# GitHub Actions Workflow Schema

**Feature**: 014-code-quality-cicd  
**Purpose**: Define the structure and requirements for CI/CD workflows  
**Last Updated**: 2026-01-10

---

## Workflow File Schema

### YAML Structure

```yaml
name: <workflow_name>                # Required: Display name
on:                                  # Required: Trigger events
  <event>:                           # e.g., push, pull_request, workflow_run
    branches: [<branch>]             # Optional: Branch filters
    types: [<type>]                  # Optional: Event types
    paths: [<path>]                  # Optional: Path filters

jobs:                                # Required: Job definitions
  <job_id>:                          # Required: Unique job identifier
    name: <job_name>                 # Optional: Display name
    runs-on: <runner>                # Required: Runner type
    strategy:                        # Optional: Build matrix
      matrix:                        # Optional: Matrix variables
        <variable>: [<value>]        # e.g., python-version: ['3.11', '3.13']
      fail-fast: <bool>              # Optional: Stop all on first failure
    steps:                           # Required: Job steps
      - name: <step_name>            # Optional: Step name
        uses: <action>               # Optional: Action to use
        with:                        # Optional: Action inputs
          <input>: <value>
      - name: <step_name>            # Optional: Step name
        run: <command>               # Optional: Command to run
        env:                         # Optional: Environment variables
          <var>: <value>
    timeout-minutes: <minutes>       # Optional: Job timeout
    continue-on-error: <bool>        # Optional: Continue if job fails
    if: <condition>                  # Optional: Conditional execution
```

---

## Field Definitions

### Top-Level Fields

#### `name`
- **Type**: String
- **Description**: Display name for the workflow
- **Naming Convention**: Title Case with spaces
- **Examples**:
  ```yaml
  name: CI Windows
  name: Pre-commit
  name: Generate Badges
  ```

#### `on`
- **Type**: Object or Array
- **Description**: Events that trigger the workflow
- **Common Events**:
  - `push`: On git push
  - `pull_request`: On PR opened/updated
  - `workflow_run`: After another workflow completes
  - `schedule`: Cron-based trigger
  - `workflow_dispatch`: Manual trigger
- **Examples**:
  ```yaml
  on: [push, pull_request]
  
  on:
    push:
      branches: [dev, main]
    pull_request:
      branches: [dev]
  
  on:
    workflow_run:
      workflows: ["CI Windows"]
      types: [completed]
  ```

---

### Job Fields

#### `jobs.<job_id>`
- **Type**: String (identifier)
- **Description**: Unique identifier for the job
- **Naming Convention**: lowercase-with-hyphens
- **Examples**:
  ```yaml
  jobs:
    test:
    lint:
    generate-badges:
  ```

#### `runs-on`
- **Type**: String (runner label)
- **Description**: Type of runner to use
- **Valid Values**:
  - `ubuntu-latest`: Ubuntu Linux (fast, cheap)
  - `windows-latest`: Windows Server
  - `macos-latest`: macOS
- **Examples**:
  ```yaml
  runs-on: ubuntu-latest
  runs-on: windows-latest
  runs-on: ${{ matrix.os }}
  ```

#### `strategy.matrix`
- **Type**: Object
- **Description**: Build matrix for testing multiple configurations
- **Common Uses**: Python versions, OS types, dependency versions
- **Examples**:
  ```yaml
  strategy:
    matrix:
      python-version: ['3.11', '3.13']
      os: [ubuntu-latest, windows-latest]
  ```

#### `steps`
- **Type**: Array of objects
- **Description**: Sequential steps in the job
- **Required**: At least one step per job

---

### Step Fields

#### `name`
- **Type**: String
- **Description**: Display name for the step
- **Optional but Recommended**: Makes logs easier to read
- **Examples**:
  ```yaml
  - name: Set up Python
  - name: Install dependencies
  - name: Run tests with coverage
  ```

#### `uses`
- **Type**: String (action reference)
- **Description**: Pre-built action to run
- **Format**: `owner/repo@version`
- **Common Actions**:
  - `actions/checkout@v4`: Checkout repository
  - `actions/setup-python@v5`: Install Python
  - `actions/upload-artifact@v4`: Upload artifacts
  - `actions/download-artifact@v4`: Download artifacts
- **Examples**:
  ```yaml
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: '3.11'
  ```

#### `run`
- **Type**: String (shell command)
- **Description**: Command to execute
- **Shell**: Bash (Linux/macOS), PowerShell (Windows)
- **Examples**:
  ```yaml
  - run: poetry install
  - run: poetry run pytest --cov
  - run: |
      echo "Multi-line command"
      poetry run pytest
  ```

#### `with`
- **Type**: Object (action inputs)
- **Description**: Inputs for the action specified in `uses`
- **Examples**:
  ```yaml
  - uses: actions/setup-python@v5
    with:
      python-version: '3.11'
  
  - uses: actions/upload-artifact@v4
    with:
      name: pytest-results
      path: pytest.xml
      retention-days: 7
  ```

#### `env`
- **Type**: Object (environment variables)
- **Description**: Environment variables for the step or job
- **Examples**:
  ```yaml
  - run: poetry run pytest
    env:
      PYTHONPATH: ./ansibledoctor
      CI: true
  ```

#### `if`
- **Type**: String (expression)
- **Description**: Conditional execution of step or job
- **Examples**:
  ```yaml
  - if: matrix.python-version == '3.13'
    run: echo "Running on Python 3.13"
  
  - if: success()
    name: Upload artifacts
    uses: actions/upload-artifact@v4
  ```

---

## Workflow Templates

### Template 1: Test Workflow (CI Windows)

**Purpose**: Run tests on multiple Python versions

```yaml
name: CI Windows

on:
  push:
    branches: [dev]
  pull_request:
    branches: [dev]

jobs:
  test:
    name: Test Python ${{ matrix.python-version }}
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.13']
      fail-fast: false

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Poetry
        run: |
          (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

      - name: Install dependencies
        run: poetry install

      - name: Run tests with coverage
        run: |
          poetry run pytest --cov=ansibledoctor --cov-report=json --cov-report=term --junitxml=pytest-${{ matrix.python-version }}.xml

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: pytest-results-${{ matrix.python-version }}
          path: |
            pytest-${{ matrix.python-version }}.xml
            coverage.json
            tests/tmp/performance-results.json
          retention-days: 7
```

**Key Features**:
- Matrix build: Python 3.11 and 3.13
- Artifact upload: pytest XML, coverage JSON, performance JSON
- `if: always()`: Upload artifacts even if tests fail

---

### Template 2: Pre-commit Workflow

**Purpose**: Validate pre-commit hooks on push

```yaml
name: Pre-commit

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: pre-commit/action@v3.0.0
```

**Key Features**:
- Simple workflow: Checkout → Setup Python → Run pre-commit
- Uses official pre-commit action

---

### Template 3: Badge Generation Workflow

**Purpose**: Generate badges from test results

```yaml
name: Generate Badges

on:
  workflow_run:
    workflows: ["CI Windows"]
    types: [completed]

jobs:
  badges:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-badges.txt

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Find pytest XML
        id: find-pytest
        run: |
          PYTEST_XML=$(find artifacts -name "pytest-*.xml" | head -n 1)
          echo "pytest_xml=$PYTEST_XML" >> $GITHUB_OUTPUT

      - name: Find coverage JSON
        id: find-coverage
        run: |
          COVERAGE_JSON=$(find artifacts -name "coverage.json" | head -n 1)
          echo "coverage_json=$COVERAGE_JSON" >> $GITHUB_OUTPUT

      - name: Find performance JSON
        id: find-perf
        run: |
          PERF_JSON=$(find artifacts -name "performance-results.json" | head -n 1)
          echo "perf_json=$PERF_JSON" >> $GITHUB_OUTPUT

      - name: Generate badges
        run: |
          python scripts/generate_badge_metrics.py \
            --pytest ${{ steps.find-pytest.outputs.pytest_xml }} \
            --coverage ${{ steps.find-coverage.outputs.coverage_json }} \
            --performance ${{ steps.find-perf.outputs.perf_json }}

      - name: Upload badges
        uses: actions/upload-artifact@v4
        with:
          name: badges
          path: badges/
          retention-days: 7
```

**Key Features**:
- Triggered by workflow_run (after CI completes)
- Downloads artifacts from previous workflow
- Finds artifacts using shell commands
- Uses step outputs to pass values between steps

---

### Template 4: Changelog Validation Workflow

**Purpose**: Validate atomic changelog entries

```yaml
name: Check Changelog Atomic

on:
  push:
    branches: [dev]
  pull_request:
    branches: [dev]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Validate changelog
        run: |
          python scripts/validate_atomic_changelog.py
```

**Key Features**:
- Simple validation workflow
- Runs on push and PR
- Fails if changelog is invalid

---

## Workflow Best Practices

### 1. Artifact Management

```yaml
# ❌ BAD: No retention policy (keeps forever)
- uses: actions/upload-artifact@v4
  with:
    name: results
    path: results/

# ✅ GOOD: Specify retention (7 days sufficient for debugging)
- uses: actions/upload-artifact@v4
  with:
    name: pytest-results-${{ matrix.python-version }}
    path: |
      pytest-${{ matrix.python-version }}.xml
      coverage.json
    retention-days: 7
```

---

### 2. Conditional Steps

```yaml
# ❌ BAD: Upload artifacts only on success (can't debug failures)
- name: Upload artifacts
  uses: actions/upload-artifact@v4

# ✅ GOOD: Upload artifacts always (for debugging)
- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v4
```

---

### 3. Matrix Strategy

```yaml
# ❌ BAD: fail-fast: true (stops all jobs if one fails)
strategy:
  matrix:
    python-version: ['3.11', '3.13']
  fail-fast: true

# ✅ GOOD: fail-fast: false (run all jobs)
strategy:
  matrix:
    python-version: ['3.11', '3.13']
  fail-fast: false
```

---

### 4. Action Versioning

```yaml
# ❌ BAD: Using @main or @latest (can break)
- uses: actions/checkout@main

# ✅ GOOD: Pinned to specific major version
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
```

---

### 5. Job Dependencies

```yaml
# ✅ GOOD: Explicit job dependencies
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]

  badges:
    needs: test  # Wait for test job to complete
    runs-on: ubuntu-latest
    steps: [...]
```

---

### 6. Environment Variables

```yaml
# ❌ BAD: Hardcoded values
- run: pytest --cov=ansibledoctor

# ✅ GOOD: Use environment variables or matrix
- run: pytest --cov=${{ env.COVERAGE_SOURCE }}
  env:
    COVERAGE_SOURCE: ansibledoctor
```

---

## Common Patterns

### Pattern 1: Multi-line Commands

```yaml
- name: Multi-step command
  run: |
    echo "Starting..."
    poetry install
    poetry run pytest
    echo "Done!"
```

---

### Pattern 2: Step Output

```yaml
- name: Find file
  id: find-file
  run: |
    FILE=$(find . -name "pytest.xml" | head -n 1)
    echo "file=$FILE" >> $GITHUB_OUTPUT

- name: Use file
  run: echo "Found file: ${{ steps.find-file.outputs.file }}"
```

---

### Pattern 3: Conditional Job

```yaml
jobs:
  test:
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps: [...]
```

---

### Pattern 4: Artifact Download

```yaml
- name: Download all artifacts
  uses: actions/download-artifact@v4
  with:
    path: artifacts

- name: List artifacts
  run: |
    ls -R artifacts/
```

---

## Troubleshooting Workflows

### Issue 1: Workflow Not Triggering

**Symptom**: Workflow doesn't run after push/PR.

**Diagnosis**: Check `on:` trigger configuration.

**Solutions**:
- Verify branch name: `branches: [dev]` matches pushed branch
- Check path filters: `paths:` might be excluding changed files
- Check workflow file syntax: `yamllint .github/workflows/ci-windows.yml`

---

### Issue 2: Artifact Not Found

**Symptom**: `Error: Unable to find artifact`

**Diagnosis**: Artifact name mismatch or not uploaded.

**Solutions**:
```yaml
# Ensure artifact name matches in upload and download
- uses: actions/upload-artifact@v4
  with:
    name: my-artifact  # Must match

- uses: actions/download-artifact@v4
  with:
    name: my-artifact  # Must match
```

---

### Issue 3: Matrix Job Failures

**Symptom**: One matrix job fails, others succeed.

**Diagnosis**: Platform-specific or version-specific issue.

**Solutions**:
- Check workflow logs for failing job
- Reproduce locally with same Python version/OS
- Use `if: matrix.python-version == '3.11'` to skip on specific versions

---

### Issue 4: Timeout

**Symptom**: `Error: The operation was canceled.`

**Diagnosis**: Job exceeded default 360-minute timeout.

**Solutions**:
```yaml
jobs:
  test:
    timeout-minutes: 10  # Set explicit timeout
```

---

## Workflow Validation Checklist

Use this checklist when creating a new workflow:

- [ ] `name` is descriptive
- [ ] `on` triggers are correct (push, pull_request, workflow_run)
- [ ] Branch filters match target branches (dev, main)
- [ ] `runs-on` is appropriate (ubuntu-latest for most, windows-latest if needed)
- [ ] Steps have descriptive `name` fields
- [ ] Actions use pinned versions (`@v4`, not `@main`)
- [ ] Artifacts have retention policy (7 days default)
- [ ] Artifacts uploaded with `if: always()` for debugging
- [ ] Matrix strategy uses `fail-fast: false`
- [ ] Environment variables used for configurable values
- [ ] Workflow tested on push to dev branch
- [ ] Workflow logs reviewed for errors/warnings
- [ ] Workflow documented in specs/014-code-quality-cicd/

---

## Workflow Dependencies

```
Push to dev
    ↓
pre-commit.yml (validates hooks)
    ↓
ci-windows.yml (runs tests on Python 3.11 & 3.13)
    ↓
badges.yml (generates badges from test results)

check-changelog-atomic.yml (validates changelog, parallel to above)
```

---

## Performance Benchmarks

| Workflow | Average Duration | Max Duration | Notes |
|----------|------------------|--------------|-------|
| pre-commit.yml | 3-5 min | 7 min | Depends on pre-commit hook changes |
| ci-windows.yml (Python 3.11) | 8-10 min | 15 min | Includes test suite |
| ci-windows.yml (Python 3.13) | 8-10 min | 15 min | Similar to 3.11 |
| badges.yml | 1-2 min | 3 min | Fast, just parsing |
| check-changelog-atomic.yml | <1 min | 2 min | Very fast |

**Total Pipeline**: ~10-15 minutes (CI + badges)

---

**Last Updated**: 2026-01-10  
**Version**: 1.0  
**Maintainer**: GitHub Copilot
