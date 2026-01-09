# Quickstart: Indexes & Navigation

**Date**: 2025-12-03  
**Feature**: Spec 011 - Indexes & Navigation

## Overview

This quickstart demonstrates how to generate comprehensive indexes for Ansible documentation, including standalone index pages, embedded sections, and various visualization styles.

---

## Basic Usage

### Generate Role Index

```bash
# Simple role index (list format)
ansible-doctor generate collection/ --include-index
```

**Output** (`roles/index.md`):

```markdown
# Role Index

## Available Roles

- **webserver** - Configure web servers with nginx
  - Tags: web, nginx
  - Dependencies: [common](./common/README.md)
  - [Documentation](./webserver/README.md)

- **database** - Install and configure PostgreSQL
  - Tags: database, postgres
  - Dependencies: [common](./common/README.md)
  - [Documentation](./database/README.md)

- **monitoring** - Setup monitoring stack with Prometheus
  - Tags: monitoring, prometheus
  - [Documentation](./monitoring/README.md)
```

---

### Generate Collection Index with Table

```bash
# Table format for easier scanning
ansible-doctor generate project/ --include-index --index-style table
```

**Output** (`collections/index.md`):

```markdown
# Collection Index

| Collection | Description | Roles | Plugins | Documentation |
|------------|-------------|-------|---------|---------------|
| [my_namespace.infrastructure](./my_namespace.infrastructure/README.md) | Infrastructure automation | 5 roles | 2 modules | [View](./my_namespace.infrastructure/README.md) |
| [my_namespace.monitoring](./my_namespace.monitoring/README.md) | Monitoring and alerting | 3 roles | 1 filter | [View](./my_namespace.monitoring/README.md) |
| [my_namespace.security](./my_namespace.security/README.md) | Security hardening | 4 roles | 3 modules | [View](./my_namespace.security/README.md) |
```

---

### Generate Hierarchical Tree

```bash
# Tree view showing project structure
ansible-doctor generate project/ --include-index --index-style tree
```

**Output** (`index.md`):

```text
# Project Index

My Ansible Project/
├── Collections/
│   ├── my_namespace.infrastructure/
│   │   ├── roles/
│   │   │   ├── webserver/
│   │   │   ├── database/
│   │   │   └── load_balancer/
│   │   └── plugins/
│   │       └── modules/
│   │           └── deploy_app.py
│   └── my_namespace.monitoring/
│       ├── roles/
│       │   ├── prometheus/
│       │   └── grafana/
│       └── plugins/
│           └── filters/
│               └── metric_format.py
└── Playbooks/
    ├── site.yml
    ├── deploy.yml
    └── rollback.yml
```

---

## Visualization Styles

### List Style (Simple)

Best for: Small collections (< 20 items), quick overview

```bash
ansible-doctor generate . --include-index --index-style list
```

**Output**:

```markdown
- webserver - Configure web servers
- database - Install databases
- monitoring - Setup monitoring
```

---

### Table Style (Detailed)

Best for: Comparing metadata across components

```bash
ansible-doctor generate . --include-index --index-style table
```

**Output**:

```markdown
| Name | Description | Tags | Dependencies |
|------|-------------|------|--------------|
| webserver | Configure web servers | web, nginx | common |
| database | Install databases | db, postgres | common |
```

---

### Tree Style (Hierarchical)

Best for: Understanding project structure, deep nesting

```bash
ansible-doctor generate . --include-index --index-style tree --index-depth 3
```

**Features**:

- ASCII characters work on all terminals
- `--use-unicode` flag for prettier output (├── └── │)
- `--index-depth N` limits tree depth

---

### Nested Table Style (Compact Hierarchy)

Best for: Large projects with many collections

```bash
ansible-doctor generate . --include-index --index-style nested-table
```

**Output**:

```markdown
| Collection | Roles | Plugins | Documentation |
|------------|-------|---------|---------------|
| infrastructure | webserver, database, loadbalancer | 2 modules | [View](./infrastructure/README.md) |
| monitoring | prometheus, grafana | 1 filter | [View](./monitoring/README.md) |
```

---

### Mermaid Diagram (Visual)

Best for: Visual learners, presentations, high-level overview

```bash
ansible-doctor generate . --include-index --index-style diagram
```

**Output**:

```markdown
# Project Structure

\`\`\`mermaid
graph TD
    Project[\"My Ansible Project\"]
    Infra[\"infrastructure\"]
    Monitor[\"monitoring\"]
    Web[\"webserver\"]
    DB[\"database\"]
    Prom[\"prometheus\"]
    
    Project --> Infra
    Project --> Monitor
    Infra --> Web
    Infra --> DB
    Monitor --> Prom
    
    Web -.depends.-> DB
    
    click Web \"./roles/webserver/README.md\"
    click DB \"./roles/database/README.md\"
\`\`\`
```

**Renders as**: Interactive diagram with clickable nodes (GitHub/GitLab)

---

## Embedded Section Indexes

### Basic Embedding

**Template** (`collection/README.md.j2`):

```jinja2
# {{ collection.name }}

{{ collection.description }}

## Available Roles

{{ index('roles') }}

## Plugins

{{ index('plugins', format='table') }}
```

**Generated Output**:

```markdown
# my_namespace.infrastructure

Infrastructure automation collection

## Available Roles

- **webserver** - Configure web servers
- **database** - Install databases
- **monitoring** - Setup monitoring

## Plugins

| Name | Type | Description |
|------|------|-------------|
| deploy_app | module | Deploy application to servers |
| metric_format | filter | Format Prometheus metrics |
```

---

### With Limit and "View More" Link

**Template**:

```jinja2
## Featured Roles

{{ index('roles', limit=5, show_more=True) }}
```

**Output**:

```markdown
## Featured Roles

- webserver - Configure web servers
- database - Install databases
- monitoring - Setup monitoring
- load_balancer - Configure load balancing
- cache - Setup Redis cache

... and 12 more roles. [View all roles](./roles/index.md)
```

---

### With Filtering

**Template**:

```jinja2
## Database Roles

{{ index('roles', filter='tag:database', format='table') }}
```

**Output**:

```markdown
## Database Roles

| Name | Description | Documentation |
|------|-------------|---------------|
| postgres | Install PostgreSQL | [View](./postgres/README.md) |
| mysql | Install MySQL | [View](./mysql/README.md) |
| mongodb | Install MongoDB | [View](./mongodb/README.md) |
```

---

### Grouped by Type

**Template**:

```jinja2
## Plugins

{{ index('plugins', group_by='type') }}
```

**Output**:

```markdown
## Plugins

### Modules

- deploy_app - Deploy application
- manage_service - Manage system services

### Filters

- metric_format - Format Prometheus metrics
- time_delta - Calculate time differences

### Callbacks

- slack_notify - Send notifications to Slack
```

---

## Filtering

### Filter by Tag

```bash
# Show only roles with 'database' tag
ansible-doctor generate . --include-index --filter 'tag:database'
```

**Output**: Index contains only database-tagged roles

---

### Filter by Namespace

```bash
# Show only components in my_namespace
ansible-doctor generate . --include-index --filter 'namespace:my_namespace'
```

---

### Multiple Filters (AND Logic)

```bash
# Roles that are both 'web' and 'stable'
ansible-doctor generate . --include-index \
  --filter 'tag:web' \
  --filter 'status:stable'
```

---

### Filter with Wildcards

```bash
# All namespaces starting with 'my_'
ansible-doctor generate . --include-index --filter 'namespace:my_*'
```

---

## Link Validation

### Enable Link Validation

```bash
# Validate all cross-reference links
ansible-doctor generate . --include-index --validate-links
```

**Output**:

```text
⚠️  Broken link detected: webserver depends on 'common' but no documentation found
⚠️  Broken link detected: database links to './mysql/README.md' which doesn't exist

✅ Generated index with 3 warnings
📄 Index: roles/index.md
```

**Exit Code**: `2` (warning) if broken links found

---

### Strict Validation (Fail on Broken Links)

```bash
# Fail build if any links are broken
ansible-doctor generate . --include-index --validate-links --strict
```

**Exit Code**: `1` (error) if broken links found

---

## Pagination

### Automatic Pagination

```bash
# Default: 50 items per page
ansible-doctor generate large-project/ --include-index
```

**Output** (if 150 roles):

```text
Generated:
  - roles/index.md (page 1, roles 1-50)
  - roles/index-2.md (page 2, roles 51-100)
  - roles/index-3.md (page 3, roles 101-150)
```

**Navigation** (`roles/index.md`):

```markdown
# Role Index (Page 1 of 3)

[... 50 roles ...]

---

[Previous](#) | [1](#) [2](./index-2.md) [3](./index-3.md) | [Next](./index-2.md)
```

---

### Custom Page Size

```bash
# 25 items per page
ansible-doctor generate . --include-index --page-size 25
```

---

### Disable Pagination

```bash
# Single page for all items (not recommended for 100+ items)
ansible-doctor generate . --include-index --page-size 9999
```

---

## Advanced Usage

### Hierarchical Project Index

```bash
# Full project hierarchy with 3 levels
ansible-doctor generate project/ \
  --include-index \
  --index-style tree \
  --index-depth 3
```

**Output**: Tree showing Project → Collections → Roles (3 levels)

---

### Mermaid Diagram with Dependencies

```bash
# Diagram showing role dependencies
ansible-doctor generate . \
  --include-index \
  --index-style diagram \
  --show-dependencies
```

**Output**: Mermaid graph with dependency arrows

---

### Multiple Output Formats

```bash
# Generate both Markdown and HTML indexes
ansible-doctor generate . \
  --include-index \
  --output-format markdown,html
```

**Output**:

- `roles/index.md` (Markdown)
- `roles/index.html` (HTML with interactive features)

---

### HTML with Interactive Features

HTML output includes:

- **Sortable Tables**: Click column headers to sort
- **Expandable Rows**: Click collection to show roles
- **Client-Side Filtering**: Filter box at top of page
- **Virtual Scrolling**: Smooth scrolling for large indexes

---

## Integration with CI/CD

### GitHub Actions

```yaml
name: Generate Documentation

on: [push]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate documentation
        run: |
          pip install ansible-doctor
          ansible-doctor generate . \
            --include-index \
            --index-style tree \
            --validate-links
      
      - name: Publish to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

### GitLab CI

```yaml
pages:
  script:
    - pip install ansible-doctor
    - ansible-doctor generate . --include-index --output-format html
    - mv docs public
  artifacts:
    paths:
      - public
  only:
    - main
```

---

## Best Practices

### 1. Use Appropriate Visualization Style

| Project Size | Recommended Style | Rationale |
| -------------- | ------------------ | ----------- |
| < 20 items | List | Quick and simple |
| 20-50 items | Table | Compare metadata |
| 50-100 items | Tree or Nested Table | Show structure |
| 100+ items | Pagination + Filtering | Manage complexity |

---

### 2. Add Tags for Better Filtering

```yaml
# roles/webserver/meta/main.yml
# @meta tags: web, nginx, production
galaxy_info:
  galaxy_tags:
    - web
    - nginx
```

**Benefit**: Users can filter by tag to find relevant roles quickly

---

### 3. Validate Links in CI/CD

Always run with `--validate-links` in CI to catch broken links early:

```bash
ansible-doctor generate . --include-index --validate-links --strict
```

---

### 4. Use Section Indexes for Discoverability

Embed role list in collection README for immediate visibility:

```jinja2
## Quick Start

{{ index('roles', limit=5, format='list') }}

[View all {{ total_roles }} roles](./roles/index.md)
```

---

### 5. Optimize for Large Projects

- Use pagination (default 50 items/page)
- Enable filtering by namespace/tag
- Generate separate index per collection
- Use nested table style for compact overview

---

## Troubleshooting

### Problem: Index Not Generated

**Symptom**: No `index.md` file created

**Solution**:

1. Ensure `--include-index` flag is set
2. Check that components have metadata (roles have `meta/main.yml`)
3. Verify output directory is writable

---

### Problem: Broken Links in Index

**Symptom**: Links show as plain text or 404

**Solution**:

1. Run with `--validate-links` to identify broken links
2. Ensure all dependencies are documented
3. Check relative path calculations

---

### Problem: Tree Too Deep

**Symptom**: Tree output is unreadable with 10+ levels

**Solution**:

```bash
# Limit depth to 3 levels
ansible-doctor generate . --include-index --index-style tree --index-depth 3
```

---

### Problem: Index Too Large

**Symptom**: Single index file is huge (> 1MB)

**Solution**:

```bash
# Enable pagination with smaller page size
ansible-doctor generate . --include-index --page-size 25
```

---

### Problem: Mermaid Diagram Not Rendering

**Symptom**: Diagram shows as code block in GitHub

**Solution**:

1. Verify Mermaid syntax is valid
2. Check GitHub/GitLab Mermaid support
3. Reduce node count if diagram is too large (> 100 nodes)

---

## See Also

- [Spec 011: Indexes & Navigation](./spec.md) - Full feature specification
- [Spec 002: Flexible Templates](../002-flexible-templates/spec.md) - Template customization
- [Spec 013: Links & Cross-References](../013-links-cross-references/spec.md) - Link management
