# Badge System Setup and Configuration

This document explains how the dynamic badge system works and how to configure it for `ansible-doctor-enhanced`.

## 🎯 Overview

The badge system automatically updates README badges with real-time metrics from CI/CD pipelines:

- **Python version** - From `pyproject.toml`
- **Package version** - From `pyproject.toml`
- **Test coverage** - With color coding (red <80%, orange 80-90%, green >90%)
- **Code quality tools** - Black, isort, Ruff, mypy status
- **Test results** - Unit/Integration/Performance test status
- **Build status** - Overall CI/CD pipeline status

## 🏗️ Architecture

```
┌─────────────────────┐
│  Pre-commit.yml     │──┐
│  - Black, isort     │  │
│  - Ruff, mypy       │  │
│  - Unit tests       │  │
└─────────────────────┘  │
                         │ artifacts
┌─────────────────────┐  │
│  CI-Windows.yml     │──┤
│  - Coverage data    │  │
│  - Test results     │  │
└─────────────────────┘  │
                         ↓
         ┌───────────────────────────┐
         │     badges.yml            │
         │  1. Download artifacts    │
         │  2. Generate JSON files   │
         │  3. Update GitHub Gist    │
         └───────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  GitHub Gist (Public)     │
         │  - coverage.json          │
         │  - mypy.json              │
         │  - black.json, etc.       │
         └───────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │  Shields.io Endpoints     │
         │  img.shields.io/endpoint  │
         └───────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │     README.md Badges      │
         └───────────────────────────┘
```

## 🔧 Setup Instructions

### Step 1: Create a Public Gist

1. Go to [gist.github.com](https://gist.github.com)
2. Create a new **public** gist named `ansible-doctor-enhanced-badges`
3. Add placeholder files (they'll be overwritten by CI):
   - `coverage.json`
   - `mypy.json`
   - `black.json`
   - `isort.json`
   - `ruff.json`
   - `tests.json`
   - `python-version.json`
   - `package-version.json`

Example placeholder content for each file:
```json
{
  "schemaVersion": 1,
  "label": "coverage",
  "message": "initializing...",
  "color": "lightgrey"
}
```

4. **Save the Gist ID** from the URL:
   ```
   https://gist.github.com/K4M1coder/1234567890abcdef1234567890abcdef
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                              This is your GIST_ID
   ```

### Step 2: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → [Personal access tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: `ansible-doctor-badges`
4. Select scope: **`gist`** (only this scope is needed)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 3: Configure Repository Secrets

1. Go to your repository: `https://github.com/K4M1coder/ansible-doctor-enhanced`
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add two secrets:

   **Secret 1:**
   - Name: `GIST_TOKEN`
   - Value: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (your token from Step 2)

   **Secret 2:**
   - Name: `BADGE_GIST_ID`
   - Value: `1234567890abcdef1234567890abcdef` (your gist ID from Step 1)

### Step 4: Verify Workflow Execution

1. Push a commit to `dev` or `main` branch
2. Check Actions tab for running workflows:
   - `Pre-commit` should run first
   - `CI - Windows` should run in parallel
   - `Update Badges` should trigger after both complete
3. Check workflow logs for "Generated badge files"
4. Verify your gist has been updated with new JSON data

### Step 5: Update README Badges

The badges are already configured in `README.md`. Replace `<GIST_ID>` placeholders with your actual gist ID:

```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/<YOUR_GIST_ID>/raw/coverage.json)
```

Example with real gist ID `abc123def456`:
```markdown
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/abc123def456/raw/coverage.json)
```

## 📊 Badge Examples

### Coverage Badge Colors
- **Red** (<80%): `{"color": "red", "message": "72.5%"}`
- **Orange** (80-90%): `{"color": "orange", "message": "85.3%"}`
- **Green** (>90%): `{"color": "brightgreen", "message": "94.1%"}`

### Mypy Badge
- **Success**: `{"message": "✨ 0 errors (122 files)", "color": "brightgreen"}`
- **Errors**: `{"message": "5 errors", "color": "red"}`

### Tool Status Badges
- **Passing**: `{"message": "passing", "color": "brightgreen"}`
- **Failing**: `{"message": "failing", "color": "red"}`
- **Unknown**: `{"message": "unknown", "color": "lightgrey"}`

## 🐛 Troubleshooting

### Badges Show "initializing..."
- Check that the `Update Badges` workflow has run successfully
- Verify secrets `GIST_TOKEN` and `BADGE_GIST_ID` are set correctly
- Check workflow logs for errors

### Badges Show "unknown"
- Workflow may have failed to parse artifacts
- Check that `Pre-commit` and `CI - Windows` workflows completed successfully
- Verify artifact upload/download steps in workflow logs

### Gist Not Updating
- Check that `GIST_TOKEN` has correct permissions (scope: `gist`)
- Verify token hasn't expired
- Check workflow logs for "Update Gist with badges" step

### Manual Badge Update
You can manually trigger badge updates:
1. Go to Actions tab
2. Select "Update Badges" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

## 🔄 Badge Update Frequency

Badges update automatically when:
- ✅ Any commit pushed to `dev` or `main` branches
- ✅ `Pre-commit` workflow completes
- ✅ `CI - Windows` workflow completes
- ✅ Manual workflow dispatch triggered

Typical latency: **2-5 minutes** from commit to badge update.

## 📝 Maintenance

### Adding New Badges

1. Edit `scripts/generate_badge_metrics.py`:
   ```python
   def generate_new_badge(data: dict) -> dict:
       return {
           "schemaVersion": 1,
           "label": "my-metric",
           "message": "value",
           "color": "blue"
       }
   
   # In main():
   badges["new-metric.json"] = generate_new_badge(data)
   ```

2. Add placeholder file to gist: `new-metric.json`

3. Add badge to README.md:
   ```markdown
   ![My Metric](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/<GIST_ID>/raw/new-metric.json)
   ```

### Customizing Badge Colors

Edit color thresholds in `generate_badge_metrics.py`:

```python
# Coverage colors
if percent < 75:  # Changed from 80
    color = "red"
elif percent < 85:  # Changed from 90
    color = "orange"
```

### Badge Styles

Shields.io supports multiple styles. Change in badge generation:

```python
"style": "flat-square"  # Current
"style": "flat"         # Flatter
"style": "for-the-badge"  # Larger, bolder
"style": "social"       # GitHub style
```

## 🔗 Useful Links

- [Shields.io Documentation](https://shields.io/)
- [Shields.io Endpoint Format](https://shields.io/endpoint)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- [GitHub Gists API](https://docs.github.com/en/rest/gists)

## 📞 Support

If badges aren't updating correctly:

1. Check workflow runs in Actions tab
2. Review workflow logs for errors
3. Verify all secrets are configured
4. Check gist contents for valid JSON
5. Test with manual workflow dispatch

For issues with this badge system, open an issue in the repository.
