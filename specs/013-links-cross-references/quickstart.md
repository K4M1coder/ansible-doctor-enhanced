# Quickstart Guide
## Spec 013: Links & Cross-References

This guide demonstrates how to use the link management and cross-reference features in ansible-doctor.

---

## Overview

The Links & Cross-References feature provides:
- ✅ **Link Validation**: Check all internal and external links in documentation
- 🔗 **Cross-References**: Automatic bidirectional links between related content
- 🧭 **Navigation**: Generate table of contents with section links
- 🔧 **Link Fixing**: Automatically fix broken links where possible
- 📊 **Link Health Reports**: Track link status over time

---

## Basic Usage

### 1. Validate All Links

Check all links in your documentation:

```bash
# Validate internal links only (fast)
ansible-doctor linkcheck check docs/

# Include external link validation (slower)
ansible-doctor linkcheck check docs/ --external

# Use parallel validation for large documentation sets
ansible-doctor linkcheck check docs/ --parallel

# Set custom timeout for external links
ansible-doctor linkcheck check docs/ --external --timeout 30
```

**Output**:
```text
========================================
Link Validation Report
========================================
Total Links: 142
Valid: 138 (97.2%)
Broken: 4
Redirects: 0
External Links Checked: 23
Duration: 1234.56ms

Broken Links:
------------------------------------------

docs/guides/installation.md:
  Line 42: ../roles/nonexistent_role.md
    Error: Target file not found
  Line 89: #invalid-anchor
    Error: Anchor 'invalid-anchor' not found in current file

docs/api/reference.md:
  Line 15: https://example.com/broken-link
    Error: HTTP 404 Not Found
```

---

### 2. Generate Link Health Report

Create detailed reports in multiple formats:

```bash
# Text report (default)
ansible-doctor linkcheck report docs/

# JSON report for CI/CD integration
ansible-doctor linkcheck report docs/ --format json --output link-health.json

# HTML report for human review
ansible-doctor linkcheck report docs/ --format html --output link-health.html
```

**JSON Output Example**:
```json
{
  "total_links": 142,
  "valid_links": 138,
  "broken_links": 4,
  "redirect_links": 0,
  "external_links_checked": 23,
  "success_rate": 0.972,
  "duration_ms": 1234.56,
  "validation_timestamp": "2024-01-15T10:30:00Z",
  "errors_by_file": {
    "docs/guides/installation.md": [
      {
        "source_file": "docs/guides/installation.md",
        "target": "../roles/nonexistent_role.md",
        "link_type": "relative_path",
        "status": "broken",
        "error_message": "Target file not found",
        "line_number": 42
      }
    ]
  }
}
```

---

### 3. Fix Broken Links

Automatically fix common link issues:

```bash
# Dry-run to preview fixes without applying
ansible-doctor linkcheck fix docs/ --dry-run

# Apply fixes with automatic backup
ansible-doctor linkcheck fix docs/ --backup

# Apply fixes without backup (use with caution!)
ansible-doctor linkcheck fix docs/ --no-backup
```

**Supported Fixes**:
- ✅ Update renamed file references
- ✅ Follow redirects to update external URLs
- ✅ Fix case mismatches in file paths
- ✅ Repair relative path errors (`../../file.md` → `../file.md`)
- ✅ Update anchors to match current section titles

**Dry-Run Output**:
```text
Preview of Link Fixes:
------------------------------------------

docs/guides/installation.md (Line 42):
  Current: ../roles/nonexistent_role.md
  Fixed:   ../roles/demo_role.md
  Reason:  File renamed

docs/api/reference.md (Line 15):
  Current: https://example.com/old-url
  Fixed:   https://example.com/new-url
  Reason:  Followed HTTP 301 redirect

Total fixes: 2
Backups will be created at: docs/.backups/
```

---

## Cross-References

### Generate Automatic Cross-References

Cross-references are generated automatically during documentation generation:

```bash
# Generate docs with cross-references
ansible-doctor generate role \
  --role-name demo_role \
  --output docs/ \
  --enable-cross-references

# Generate collection docs with dependency tracking
ansible-doctor generate collection \
  --collection-path collections/ansible_collections/demo/collection \
  --output docs/ \
  --enable-cross-references \
  --track-dependencies
```

**Generated Cross-References**:

```markdown
## Related Content

### Dependencies
- [common_role](../roles/common_role.md) - Provides shared utilities
- [database_role](../roles/database_role.md) - Required database setup

### Used By
- [app_deployment](../playbooks/app_deployment.md) - Main deployment playbook
- [monitoring_setup](../playbooks/monitoring.md) - Monitoring configuration

### Related Roles
- [backup_role](../roles/backup_role.md) - Similar functionality (80% match)
- [restore_role](../roles/restore_role.md) - Complementary functionality
```

**Bidirectional Links**:
- Forward link: `demo_role.md` → "Depends on: common_role"
- Backward link: `common_role.md` → "Used by: demo_role"

---

## Navigation Generation

### Generate Table of Contents

Automatically generate TOCs from document headers:

```bash
# Generate docs with TOC
ansible-doctor generate role \
  --role-name demo_role \
  --output docs/ \
  --toc \
  --toc-depth 3

# Update TOC in existing documents
ansible-doctor linkcheck update-toc docs/ --max-depth 3
```

**Generated TOC**:

```markdown
## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Basic Setup](#basic-setup)
    - [Configure Variables](#configure-variables)
- [Usage](#usage)
  - [Quick Start](#quick-start)
  - [Advanced Configuration](#advanced-configuration)
- [API Reference](#api-reference)
```

**Features**:
- ✅ Hierarchical structure (nested sections)
- ✅ GitHub-compatible anchors
- ✅ Configurable max depth (1-6)
- ✅ Automatic updates on doc regeneration

---

## External Link Integration

### Link to Ansible Documentation

Automatically generate links to official Ansible docs:

```python
from ansibledoctor.links import ExternalLinkIntegrator

integrator = ExternalLinkIntegrator(ansible_version="2.15")

# Link to module documentation
module_link = integrator.generate_module_link("ansible.builtin.copy")
# → https://docs.ansible.com/ansible/2.15/collections/ansible/builtin/copy_module.html

# Link to collection on Galaxy
collection_link = integrator.generate_collection_link("community", "general")
# → https://galaxy.ansible.com/community/general

# Link to best practices guide
bp_link = integrator.generate_best_practices_link("roles")
# → https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html
```

**Template Usage** (Jinja2):

```jinja2
## Module Documentation

This role uses the following Ansible modules:
{% for module in role.modules %}
- [`{{ module }}`]({{ external_links.module(module) }}) - {{ module | describe }}
{% endfor %}

## Collection Information

This role is part of the [`{{ collection.namespace }}.{{ collection.name }}`]({{ external_links.collection(collection.namespace, collection.name) }}) collection.
```

---

## CI/CD Integration

### GitHub Actions Workflow

Add link validation to your CI/CD pipeline:

```yaml
name: Documentation

on: [push, pull_request]

jobs:
  validate-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install ansible-doctor
        run: pip install ansible-doctor
      
      - name: Validate Internal Links
        run: |
          ansible-doctor linkcheck check docs/ \
            --format json \
            --output link-report.json
      
      - name: Validate External Links (Nightly Only)
        if: github.event_name == 'schedule'
        run: |
          ansible-doctor linkcheck check docs/ \
            --external \
            --timeout 30 \
            --format json \
            --output external-links.json
      
      - name: Upload Link Report
        uses: actions/upload-artifact@v3
        with:
          name: link-validation-report
          path: |
            link-report.json
            external-links.json
      
      - name: Fail on Broken Links
        run: |
          python -c "
          import json
          with open('link-report.json') as f:
              report = json.load(f)
          if report['broken_links'] > 0:
              print(f'❌ Found {report[\"broken_links\"]} broken links')
              exit(1)
          print(f'✅ All {report[\"total_links\"]} links valid')
          "
```

---

## Advanced Features

### Link Graph Analysis

Analyze link relationships in your documentation:

```python
from ansibledoctor.links import LinkGraph, LinkValidator

# Build link graph
graph = LinkGraph()
validator = LinkValidator()

# Validate all files and build graph
for file in docs_dir.glob("**/*.md"):
    result = validator.validate_file(file, docs_dir)
    for link in result.links:
        graph.add_link(link)

# Detect circular dependencies
cycles = graph.find_cycles()
if cycles:
    print(f"⚠️ Found {len(cycles)} circular link dependencies")
    for cycle in cycles:
        print(f"  Cycle: {' → '.join(str(f) for f in cycle)}")

# Find related documents
related = graph.get_related_files(Path("docs/index.md"), max_depth=2)
print("Related documents:")
for file, distance in related[:5]:
    print(f"  {file} (distance: {distance})")

# Compute PageRank scores (importance ranking)
scores = graph.compute_page_rank()
top_pages = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
print("\nMost important pages:")
for page, score in top_pages:
    print(f"  {page}: {score:.4f}")
```

**Output**:
```text
⚠️ Found 1 circular link dependency
  Cycle: docs/guide.md → docs/api.md → docs/guide.md

Related documents:
  docs/installation.md (distance: 1)
  docs/configuration.md (distance: 1)
  docs/api/reference.md (distance: 2)
  docs/examples/basic.md (distance: 2)

Most important pages:
  docs/index.md: 0.1523
  docs/installation.md: 0.0892
  docs/api/reference.md: 0.0745
  docs/configuration.md: 0.0634
```

---

### Custom Link Validators

Extend the link validator with custom validation rules:

```python
from ansibledoctor.links import LinkValidator, Link, LinkStatus

class CustomLinkValidator(LinkValidator):
    """Custom validator with additional rules."""
    
    def validate_link(self, link: Link, output_dir: Path, check_external: bool = False) -> Link:
        """Validate link with custom rules."""
        # Run standard validation
        link = super().validate_link(link, output_dir, check_external)
        
        # Custom rule: Warn about links to deprecated content
        if "deprecated" in str(link.target).lower():
            link.status = LinkStatus.VALID
            link.error_message = "Warning: Link points to deprecated content"
        
        # Custom rule: Require HTTPS for external links
        if link.is_external and link.target.startswith("http://"):
            link.status = LinkStatus.BROKEN
            link.error_message = "Error: External links must use HTTPS"
        
        return link

# Use custom validator
validator = CustomLinkValidator()
result = validator.validate_all(docs_dir, check_external=True)
```

---

## Configuration

### .ansibledoctor.yml

Configure link validation behavior:

```yaml
links:
  # Link validation settings
  validation:
    check_external: false        # Check external links by default
    timeout: 10                  # HTTP request timeout (seconds)
    parallel: true               # Use parallel validation
    max_workers: 10              # Max parallel workers
  
  # External link settings
  external:
    cache_ttl: 86400            # Cache TTL (seconds, 24 hours)
    cache_dir: ~/.cache/ansible-doctor/links/
    rate_limit: 10              # Max requests/sec per domain
    retry_count: 3              # Retry attempts
    retry_delay: [1, 2, 4]      # Retry delays (seconds)
    respect_robots_txt: true    # Respect robots.txt
  
  # Cross-reference settings
  cross_references:
    enabled: true
    bidirectional: true         # Generate bidirectional links
    max_related: 5              # Max related items to show
    similarity_threshold: 0.7   # Min similarity for "related" links
  
  # Navigation settings
  navigation:
    toc_enabled: true
    toc_max_depth: 3            # Max heading depth in TOC
    generate_anchors: true      # Generate section anchors
    anchor_style: github        # Anchor generation style
  
  # Link fixing settings
  fixing:
    auto_backup: true           # Create backups before fixing
    backup_dir: .backups/       # Backup directory
    fix_redirects: true         # Follow redirects
    fix_case: true              # Fix case mismatches
    fix_relative_paths: true    # Fix relative path errors
```

---

## Performance Tips

### Optimize Link Validation

1. **Skip External Links in CI** (check nightly instead):
   ```bash
   ansible-doctor linkcheck check docs/  # Internal only, fast
   ```

2. **Use Caching for Repeated Validations**:
   ```yaml
   links:
     external:
       cache_ttl: 86400  # 24 hours
   ```

3. **Increase Parallelism for Large Documentation**:
   ```bash
   ansible-doctor linkcheck check docs/ --parallel --max-workers 20
   ```

4. **Filter by File Pattern**:
   ```bash
   # Only check files matching pattern
   ansible-doctor linkcheck check docs/ --include "docs/api/**/*.md"
   ```

---

## Troubleshooting

### Common Issues

**Issue**: "Target file not found" for valid files

**Solution**: Ensure output directory is set correctly:
```bash
ansible-doctor linkcheck check docs/ --output-dir /path/to/output
```

---

**Issue**: External link validation times out

**Solution**: Increase timeout or skip slow domains:
```bash
ansible-doctor linkcheck check docs/ --external --timeout 30
```

---

**Issue**: False positives for redirects

**Solution**: Configure redirect handling:
```yaml
links:
  validation:
    treat_redirects_as_valid: true
```

---

**Issue**: Circular dependency warnings

**Solution**: Review link graph and break cycles:
```bash
ansible-doctor linkcheck report docs/ --show-cycles
```

---

## Examples

### Example 1: Weekly Link Health Report

```bash
#!/bin/bash
# weekly-link-check.sh

# Generate comprehensive link report
ansible-doctor linkcheck check docs/ \
  --external \
  --parallel \
  --format html \
  --output weekly-link-report.html

# Email report to team
mail -s "Weekly Link Health Report" \
  -a weekly-link-report.html \
  team@example.com < /dev/null
```

---

### Example 2: Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate links in staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.md$')

if [ -n "$STAGED_FILES" ]; then
  echo "Validating links in staged files..."
  
  for file in $STAGED_FILES; do
    ansible-doctor linkcheck check "$file" || {
      echo "❌ Link validation failed for $file"
      echo "Run 'ansible-doctor linkcheck fix $file' to fix issues"
      exit 1
    }
  done
  
  echo "✅ All links valid"
fi
```

---

### Example 3: Documentation Dashboard

```python
# dashboard.py - Generate link health dashboard

from pathlib import Path
from ansibledoctor.links import LinkValidator, LinkGraph

docs_dir = Path("docs/")
validator = LinkValidator()
graph = LinkGraph()

# Validate all links
result = validator.validate_all(docs_dir, check_external=False, parallel=True)

# Build graph
for link in result.links:
    graph.add_link(link)

# Generate dashboard
print("=" * 60)
print("Documentation Health Dashboard")
print("=" * 60)
print(f"Total Files: {len(list(docs_dir.glob('**/*.md')))}")
print(f"Total Links: {result.total_links}")
print(f"Success Rate: {result.success_rate:.1%}")
print(f"Broken Links: {result.broken_links}")
print(f"Circular Dependencies: {len(graph.find_cycles())}")
print()

# Top 10 most linked-to pages
scores = graph.compute_page_rank()
top_pages = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most Important Pages:")
for i, (page, score) in enumerate(top_pages, 1):
    print(f"  {i}. {page.name}: {score:.4f}")
```

---

## Next Steps

- **Explore Link Graph**: Use `LinkGraph` for advanced analysis
- **Customize Validators**: Extend `LinkValidator` for project-specific rules
- **Integrate with CI/CD**: Add link validation to your pipeline
- **Monitor Link Health**: Set up regular link checking (nightly/weekly)
- **Optimize Performance**: Use caching and parallel validation

For more examples, see the [demo directory](../../demo/) in the repository.
