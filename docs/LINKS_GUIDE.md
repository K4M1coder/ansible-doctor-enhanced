# Links & Cross-References Guide

Complete guide to using the link management, validation, and cross-reference features in Ansible Doctor.

## Table of Contents

- [Overview](#overview)
- [Link Generation](#link-generation)
- [Link Validation](#link-validation)
- [Cross-References](#cross-references)
- [Navigation Features](#navigation-features)
- [External Links](#external-links)
- [Index-Based Navigation](#index-based-navigation)
- [Configuration](#configuration)
- [CLI Commands](#cli-commands)
- [Advanced Features](#advanced-features)

## Overview

The Links & Cross-References feature (Spec 013) provides comprehensive link management for Ansible documentation:

- **Automatic Cross-References**: Links between related roles, collections, and projects
- **Link Validation**: Detect broken internal and external links
- **Section Navigation**: Table of contents with anchor links
- **External Resources**: Integration with Ansible docs and Galaxy
- **Index Navigation**: Alphabetical, category, tag, and search indexes
- **Bidirectional Relationships**: Track "links to" and "linked by"

### Key Benefits

✅ **Never Ship Broken Links**: Automated validation catches all broken links  
✅ **Easy Navigation**: Multiple pathways to discover content  
✅ **Smart Cross-References**: Automatic relationship detection  
✅ **External Integration**: Links to official Ansible resources  
✅ **Fast Validation**: < 30 seconds for 1000+ documents  

## Link Generation

### Automatic Link Creation

Links are automatically generated during documentation generation:

```bash
ansible-doctor role --output ./docs
```

**Generated Links Include**:
- Dependency links (roles that depend on other roles)
- Parent collection links (roles → their collection)
- Project context links (breadcrumb navigation)
- Related roles (by tags or functionality)
- Section anchors (table of contents)

### Manual Link Creation

Use the `LinkManager` API for custom link generation:

```python
from ansibledoctor.links.link_manager import LinkManager
from pathlib import Path

manager = LinkManager(base_path=Path("./docs"))

# Create internal link
link = manager.create_link(
    source_file=Path("role1/README.md"),
    target_path="role2/README.md",
    link_text="Role 2"
)
print(link)  # Output: [Role 2](../role2/README.md)

# Create anchor link
link = manager.create_link(
    source_file=Path("README.md"),
    target_path="README.md#configuration",
    link_text="Configuration"
)
print(link)  # Output: [Configuration](#configuration)

# Format for different outputs
markdown_link = manager.format_link("docs.ansible.com", "Ansible Docs", "markdown")
html_link = manager.format_link("docs.ansible.com", "Ansible Docs", "html")
```

## Link Validation

### Basic Validation

Validate all links in generated documentation:

```bash
# Validate all links (internal + external)
ansible-doctor linkcheck ./docs

# Internal links only (fast)
ansible-doctor linkcheck ./docs --internal-only

# External links only (slow)
ansible-doctor linkcheck ./docs --external-only
```

### Validation During Generation

Enable automatic validation during documentation generation:

```bash
ansible-doctor role --output ./docs --validate-links
```

### Validation Output Formats

**Text Format** (default):
```bash
ansible-doctor linkcheck ./docs --format text
```

**JSON Format** (for CI/CD):
```bash
ansible-doctor linkcheck ./docs --format json
```

**Summary Format** (counts only):
```bash
ansible-doctor linkcheck ./docs --format summary
```

**Markdown Report**:
```bash
ansible-doctor linkcheck ./docs --format markdown --output validation-report.md
```

### Exit Codes

- `0`: All links valid
- `1`: Broken links found
- `2`: Validation error occurred

Perfect for CI/CD pipelines:

```yaml
# .github/workflows/docs.yml
- name: Validate Documentation Links
  run: |
    ansible-doctor linkcheck ./docs --format json
    if [ $? -ne 0 ]; then
      echo "❌ Broken links detected!"
      exit 1
    fi
```

## Cross-References

### Dependency Links

Roles automatically link to their dependencies:

```yaml
# meta/main.yml
dependencies:
  - role: common
  - role: database
```

**Generated Output**:
```markdown
## Dependencies

- [common](../common/README.md)
- [database](../database/README.md)
```

### Parent Collection Links

Roles link back to their parent collection:

```markdown
**Part of Collection**: [namespace.collection](../../README.md)
```

### Related Roles

Similar roles are automatically linked based on:
- Shared tags
- Similar names
- Common functionality keywords

```markdown
## Related Roles

- [nginx](../nginx/README.md) - Web server configuration
- [haproxy](../haproxy/README.md) - Load balancer setup
```

### Cross-Reference API

Generate custom cross-references:

```python
from ansibledoctor.links.cross_reference_generator import CrossReferenceGenerator
from ansibledoctor.models.role import AnsibleRole

generator = CrossReferenceGenerator()
role = AnsibleRole(name="web_server", path=Path("roles/web_server"))

# Generate all cross-references
references = generator.generate_references(role)

# Access specific reference types
dependencies = references.depends_on
parent = references.parent_collection
related = references.see_also
```

## Navigation Features

### Table of Contents

Automatically generated for long documents:

```python
from ansibledoctor.links.navigation_builder import NavigationBuilder

builder = NavigationBuilder()
content = Path("README.md").read_text()

# Generate Markdown TOC
toc = builder.build_toc(content, format="markdown", max_depth=3)

# Generate HTML TOC
toc_html = builder.build_toc(content, format="html", mobile_friendly=True)
```

**Configuration Options**:
- `max_depth`: Maximum heading level (1-6)
- `include_top_level`: Include H1 headings
- `mobile_friendly`: Responsive design (HTML only)

### Section Anchors

Section links use URL-safe slugs:

```markdown
# My Section Name → #my-section-name
## API Reference → #api-reference
### Getting Started → #getting-started
```

**Special Cases**:
- Duplicate headings: `#section`, `#section-1`, `#section-2`
- Special characters: Removed or replaced
- Unicode: Normalized (ñ → n)

## External Links

### Ansible Module Documentation

Automatically link to official module docs:

```yaml
# tasks/main.yml
- name: Install package
  ansible.builtin.apt:
    name: nginx
```

**Generated Link**: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html

### Galaxy Links

Link roles and collections to Ansible Galaxy:

```yaml
# meta/main.yml
galaxy_info:
  namespace: community
  name: general
```

**Generated Link**: https://galaxy.ansible.com/community/general

### Best Practices Guides

Keyword detection links to official guides:

```markdown
**Keywords**: security, vault, secrets, molecule, testing
```

**Generated Links**:
- `security` → Ansible Security Best Practices
- `vault` → Using Ansible Vault
- `molecule` → Testing with Molecule

### Version-Specific URLs

Configure Ansible version for documentation URLs:

```yaml
# .ansibledoctor.yml
ansible_version: "2.15"
```

**Result**: https://docs.ansible.com/ansible/2.15/...

### Configuration

Full external link configuration:

```yaml
# .ansibledoctor.yml
ansible_version: "latest"

external_links:
  # Feature flags
  enable_module_docs: true
  enable_galaxy_links: true
  enable_best_practices: true
  
  # Custom base URLs
  ansible_docs_base: "https://docs.ansible.com"
  galaxy_base: "https://galaxy.ansible.com"
  
  # Module override URLs
  module_docs:
    "ansible.builtin.apt": "https://custom-docs.example.com/apt"
  
  # Custom keyword mappings
  best_practices:
    "custom_keyword": "https://your-guide.example.com"
```

## Index-Based Navigation

### Alphabetical Index

Group content by first letter:

```python
from ansibledoctor.generator.indexes import DefaultIndexGenerator
from pathlib import Path

generator = DefaultIndexGenerator(output_dir=Path("./docs"))

items = [
    {"name": "apache", "type": "role", "path": "./apache/README.md"},
    {"name": "backup", "type": "role", "path": "./backup/README.md"},
    {"name": "cache", "type": "module", "path": "./cache/README.md"},
]

index = generator.generate_alphabetical_index(items)
# Result: {"A": [apache], "B": [backup], "C": [cache]}
```

**Features**:
- Unicode normalization (ñ → N)
- Special character handling (_private → P)
- Number grouping (123 → #)
- Case-insensitive sorting

### Category Index

Group by component type:

```python
category_index = generator.generate_category_index(items)
# Result: {
#   "role": {"items": [apache, backup], "count": 2},
#   "module": {"items": [cache], "count": 1}
# }
```

**Supported Categories**:
- `role`: Ansible roles
- `module`: Ansible modules
- `plugin`: Ansible plugins
- `filter`: Filter plugins
- `lookup`: Lookup plugins
- `playbook`: Playbooks

### Tag Index

Group by tags with popularity sorting:

```python
tagged_items = [
    {"name": "web", "tags": ["webserver", "production"], "path": "./web/README.md"},
    {"name": "api", "tags": ["webserver", "api"], "path": "./api/README.md"},
    {"name": "db", "tags": ["database"], "path": "./db/README.md"},
]

tag_index = generator.generate_tag_index(tagged_items)
# Result: {
#   "webserver": {"items": [web, api], "count": 2},  # Most popular first
#   "database": {"items": [db], "count": 1},
#   "production": {"items": [web], "count": 1},
#   "api": {"items": [api], "count": 1}
# }
```

**Features**:
- Multi-tag membership (items can have multiple tags)
- Untagged category for items without tags
- Popularity sorting (most items first)

### Search Index

Full-text search with relevance scoring:

```python
search_index = generator.generate_search_index(items)

# Search for items
results = generator.search(search_index, "apache web server")
# Results sorted by relevance score
```

**Scoring Algorithm**:
- Base score: Term frequency
- +10: Term in item name
- +20: Exact name match
- Stop words filtered (the, and, or, etc.)
- Partial matching supported

### Tag Navigation Page

Generate a standalone tag navigation page:

```python
page_content = generator.generate_tag_navigation_page(items)
Path("./docs/tags.md").write_text(page_content)
```

**Output**:
```markdown
# Tags

## webserver (2)
- [web](./web/README.md) *role*
- [api](./api/README.md) *role*

## database (1)
- [db](./db/README.md) *role*
```

### Clickable Tag Links

Tags in documentation are automatically linked:

```markdown
**Tags**: [`webserver`](../tags.md#tag-webserver), [`production`](../tags.md#tag-production)
```

## Configuration

### Complete Configuration Example

```yaml
# .ansibledoctor.yml
ansible_version: "2.15"

# External link configuration
external_links:
  enable_module_docs: true
  enable_galaxy_links: true
  enable_best_practices: true
  ansible_docs_base: "https://docs.ansible.com"
  galaxy_base: "https://galaxy.ansible.com"
  
  module_docs:
    "ansible.builtin.apt": "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html"
  
  best_practices:
    "security": "https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#security"
    "vault": "https://docs.ansible.com/ansible/latest/user_guide/vault.html"

# Link validation configuration
link_validation:
  enabled: true
  check_external: true
  timeout: 10
  max_retries: 3
  cache_ttl: 3600
  ignore_patterns:
    - "http://localhost:*"
    - "http://127.0.0.1:*"
```

## CLI Commands

### linkcheck

Validate all links in documentation:

```bash
ansible-doctor linkcheck <path> [OPTIONS]
```

**Options**:
- `--format TEXT|JSON|SUMMARY|MARKDOWN`: Output format
- `--output FILE`: Write report to file
- `--internal-only`: Check internal links only
- `--external-only`: Check external links only
- `--ignore-pattern PATTERN`: Ignore URLs matching pattern
- `--no-cache`: Disable external link caching
- `--timeout SECONDS`: HTTP request timeout
- `--max-retries N`: Maximum retry attempts

**Examples**:
```bash
# Basic validation
ansible-doctor linkcheck ./docs

# JSON output for CI/CD
ansible-doctor linkcheck ./docs --format json --output validation.json

# Internal links only (fast)
ansible-doctor linkcheck ./docs --internal-only

# Ignore localhost links
ansible-doctor linkcheck ./docs --ignore-pattern "http://localhost:*"
```

### linkreport

Generate link health report:

```bash
ansible-doctor linkreport <path> [OPTIONS]
```

**Options**:
- `--format MARKDOWN|HTML|JSON`: Report format
- `--output FILE`: Write report to file
- `--group-by FILE|TYPE|STATUS`: Group results
- `--include-valid`: Include valid links in report

**Examples**:
```bash
# Markdown report
ansible-doctor linkreport ./docs --format markdown --output report.md

# HTML report with all links
ansible-doctor linkreport ./docs --format html --include-valid --output report.html

# JSON report grouped by file
ansible-doctor linkreport ./docs --format json --group-by file
```

### linkfix

Attempt to fix broken links (interactive):

```bash
ansible-doctor linkfix <path> [OPTIONS]
```

**Options**:
- `--dry-run`: Show suggestions without modifying files
- `--auto-fix`: Apply fixes automatically without prompts
- `--backup`: Create backup before fixing

**Examples**:
```bash
# Dry run (show suggestions)
ansible-doctor linkfix ./docs --dry-run

# Interactive fixing
ansible-doctor linkfix ./docs

# Automatic fixing with backup
ansible-doctor linkfix ./docs --auto-fix --backup
```

## Advanced Features

### Link Health Monitoring

Monitor link health over time:

```python
from ansibledoctor.links.link_health_monitor import LinkHealthMonitor
from pathlib import Path

monitor = LinkHealthMonitor(docs_path=Path("./docs"))

# Run health check
report = monitor.check_health()

# Access results
print(f"Valid: {report.valid_count}")
print(f"Broken: {report.broken_count}")
print(f"Warnings: {report.warning_count}")

# Get detailed results
for result in report.broken_links:
    print(f"Broken: {result.url} in {result.source_file}")
```

### Bidirectional Relationships

Track "links to" and "linked by":

```python
from ansibledoctor.utils.link_graph import LinkGraph, RelationshipType

graph = LinkGraph()

# Add relationships
graph.add_relationship("role_a", "role_b", RelationshipType.DEPENDS_ON)
graph.add_relationship("role_a", "role_c", RelationshipType.INCLUDES)

# Query relationships
outgoing = graph.get_outgoing("role_a")  # role_b, role_c
incoming = graph.get_incoming("role_b")  # role_a

# Check for cycles
has_cycle = graph.has_cycle()
cycles = graph.find_cycles()

# Visualize as Mermaid diagram
mermaid = graph.to_mermaid()
```

### Link Caching

External link validation results are cached:

```python
from ansibledoctor.links.link_validator import LinkValidator
from pathlib import Path

validator = LinkValidator(base_path=Path("./docs"))

# Cache is automatically loaded
validator.load_cache()

# Validate (uses cache)
result = validator.validate_external_link("https://docs.ansible.com")

# Save cache for next run
validator.save_cache()

# Clear cache if needed
validator.clear_cache()
```

**Cache Configuration**:
```yaml
# .ansibledoctor.yml
link_validation:
  cache_ttl: 3600  # 1 hour
  cache_file: ".link-cache.json"
```

## Troubleshooting

### Common Issues

**Issue**: Links to parent collection not generated  
**Solution**: Ensure `galaxy.yml` or `MANIFEST.json` exists in collection root

**Issue**: External links not validated  
**Solution**: Use `--external-only` flag or enable in config:
```yaml
link_validation:
  check_external: true
```

**Issue**: Too many HTTP requests (rate limiting)  
**Solution**: Enable caching and increase cache TTL:
```yaml
link_validation:
  cache_ttl: 7200  # 2 hours
```

**Issue**: False positive broken links  
**Solution**: Add ignore patterns:
```yaml
link_validation:
  ignore_patterns:
    - "http://localhost:*"
    - "http://internal-server/*"
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
ansible-doctor linkcheck ./docs --verbose --debug
```

## Best Practices

1. **Validate Early**: Run `linkcheck` in CI/CD before merging
2. **Cache External Links**: Use caching to avoid rate limiting
3. **Ignore Test URLs**: Add localhost/internal URLs to ignore list
4. **Version URLs**: Use version-specific documentation URLs
5. **Monitor Health**: Run periodic link health checks
6. **Use Relative Links**: Prefer relative paths for internal links
7. **Anchor Consistency**: Use consistent heading formats for anchors

## See Also

- [README.md](../README.md): Main documentation
- [CHANGELOG.md](../CHANGELOG.md): Version history
- [CONFIG_GUIDE.md](./CONFIG_GUIDE.md): Configuration reference
- [Spec 013](../specs/013-links-cross-references/spec.md): Full specification
