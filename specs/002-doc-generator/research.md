# Research: Template Engine & Documentation Formats

**Feature**: 002-doc-generator  
**Phase**: 9 - Foundation & Research  
**Date**: 2025-11-17

## Objective

Research Jinja2 template engine capabilities, best practices for documentation generation, and format-specific requirements (Markdown, HTML, reStructuredText) to inform implementation decisions.

## Jinja2 Template Engine Analysis

### Core Capabilities

**Version**: Jinja2 3.1+ (Python 3.11+ compatible)

**Key Features**:

- Template inheritance (`{% extends "base.j2" %}`)
- Block overrides (`{% block content %}`)
- Filters for transformations (`{{ var|escape }}`)
- Custom filters registration
- Macros for reusable components
- Conditional rendering (`{% if %}`, `{% for %}`)
- Auto-escaping by output format

**Performance**:

- Compiled templates cached in memory
- ~10-50ms for typical role documentation
- Template preloading reduces first-render cost

### Custom Filters Needed

```python
# markdown_escape: Escape Markdown special characters
{{ description|markdown_escape }}
# Input: "Variable with * and _"
# Output: "Variable with \\* and \\_"

# html_escape: Escape HTML (built-in via markupsafe)
{{ description|escape }}

# rst_escape: Escape reStructuredText
{{ text|rst_escape }}

# format_priority: Convert priority to display text
{{ todo.priority|format_priority }}
# Input: "critical"
# Output: "🔴 CRITICAL"

# code_fence: Add language-specific fencing
{{ code|code_fence(language) }}
# Markdown: ```yaml\n{code}\n```
# HTML: <pre><code class="yaml">{code}</code></pre>
# RST: .. code-block:: yaml\n   {code}
```

### Template Structure

**Base Template** (`base.j2`):

```jinja2
{# Common structure for all formats #}
{% block header %}{% endblock %}
{% block metadata %}{% endblock %}
{% block variables %}{% endblock %}
{% block tags %}{% endblock %}
{% block examples %}{% endblock %}
{% block todos %}{% endblock %}
{% block footer %}{% endblock %}
```

**Format-Specific Templates** extend base:

```jinja2
{% extends "base.j2" %}
{% block header %}
# {{ role.name }}
{{ role.description }}
{% endblock %}
```

## Output Format Requirements

### Markdown

**Target**: GitHub-Flavored Markdown (GFM)

**Structure**:

```markdown
# Role Name
Description

## Requirements
- Platform requirements
- Dependencies

## Role Variables
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| var1 | string | "default" | Description |

## Example Playbook
```yaml
- hosts: servers
  roles:
    - role: my-role
```

## Tags
- `tag1`: Description (used in 5 tasks)

## TODOs
- 🔴 CRITICAL: Fix security issue (tasks/main.yml:42)
- 🟡 MEDIUM: Refactor handler (handlers/main.yml:10)
```

**Escaping**:

- `*`, `_`, `[`, `]`, `#`, `` ` ``, `>`, `-`, `+`, `!` in text
- Code blocks: Use triple backticks with language hint
- Tables: Pipe `|` escaping in cell content

### HTML

**Target**: Standalone HTML5 with embedded CSS

**Structure**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Role: {{ role.name }}</title>
    <style>
        /* Embedded CSS for styling */
        body { font-family: sans-serif; max-width: 900px; margin: 0 auto; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #f8f8f8; padding: 15px; overflow-x: auto; }
        .toc { background: #f0f0f0; padding: 15px; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <nav class="toc">
        <h2>Table of Contents</h2>
        <ul>
            <li><a href="#metadata">Metadata</a></li>
            <li><a href="#variables">Variables</a></li>
            <!-- Auto-generated TOC -->
        </ul>
    </nav>
    <h1>{{ role.name|escape }}</h1>
    <p>{{ role.description|escape }}</p>
    <!-- Content sections -->
</body>
</html>
```

**Features**:

- Responsive layout (mobile-friendly)
- Syntax highlighting for code blocks (highlight.js or Prism.js via CDN)
- Collapsible sections for large variable lists
- Anchor links in TOC

**Escaping**: Use `|escape` filter (markupsafe)

### reStructuredText

**Target**: Sphinx-compatible RST

**Structure**:

```rst
================
Role: role-name
================

:Description: Role description
:Author: Author Name
:License: MIT

Requirements
============

* Platform: Ubuntu 20.04+
* Dependencies: See meta/main.yml

Role Variables
==============

.. list-table::
   :header-rows: 1
   :widths: 20 15 20 45

   * - Variable
     - Type
     - Default
     - Description
   * - ``var1``
     - string
     - ``"default"``
     - Variable description

Example Playbook
================

.. code-block:: yaml

   - hosts: servers
     roles:
       - role: my-role

Tags
====

.. note::
   
   **tag1** (5 tasks)
      Description of tag usage

TODOs
=====

.. warning::
   
   **CRITICAL** (tasks/main.yml:42)
      Fix security vulnerability
```

**Directives**:

- `.. code-block:: <lang>` for code
- `.. note::` for informational blocks
- `.. warning::` for high-priority TODOs
- `.. list-table::` for structured data

**Escaping**: RST special chars: `*`, `` ` ``, `_`, `\`, `[`, `]`, `<`, `>`

## Template Discovery Logic

**Search Order**:

1. `--template <path>` (explicit CLI argument)
2. `.ansible-doctor/templates/<format>.j2` (project-local)
3. `~/.ansible-doctor/templates/<format>.j2` (user global)
4. `ansibledoctor/generator/templates/<format>.j2` (embedded defaults)

**Implementation**:

```python
def discover_template(format: OutputFormat, custom_path: Path | None) -> Path:
    """Find template with fallback chain."""
    if custom_path and custom_path.exists():
        return custom_path
    
    # Project-local
    local = Path.cwd() / ".ansible-doctor" / "templates" / f"{format.value}.j2"
    if local.exists():
        return local
    
    # User global
    user = Path.home() / ".ansible-doctor" / "templates" / f"{format.value}.j2"
    if user.exists():
        return user
    
    # Embedded default (using importlib.resources)
    return get_embedded_template(format)
```

## Template Context Data Model

**Input**: JSON from Feature 001 parser

```json
{
  "name": "my-role",
  "description": "Role description",
  "author": "Author Name",
  "license": "MIT",
  "variables": [
    {
      "name": "var1",
      "value": "default",
      "type": "string",
      "description": "Variable description",
      "source": "defaults"
    }
  ],
  "tags": [
    {
      "name": "config",
      "description": "Configuration tasks",
      "usage_count": 5,
      "file_locations": ["tasks/main.yml:10", "tasks/main.yml:25"]
    }
  ],
  "todos": [
    {
      "description": "Fix security issue",
      "file_path": "tasks/main.yml",
      "line_number": 42,
      "priority": "critical"
    }
  ],
  "examples": [
    {
      "title": "Basic Usage",
      "code": "- hosts: all\n  roles:\n    - my-role",
      "language": "yaml"
    }
  ]
}
```

**Template Context Wrapper**:

```python
class TemplateContext:
    """Wrapper with helper methods for templates."""
    
    def __init__(self, role_data: dict):
        self.role = role_data
    
    def has_variables(self) -> bool:
        return len(self.role.get("variables", [])) > 0
    
    def has_examples(self) -> bool:
        return len(self.role.get("examples", [])) > 0
    
    def critical_todos(self) -> list:
        return [t for t in self.role.get("todos", []) 
                if t["priority"] == "critical"]
    
    def group_tags_by_file(self) -> dict:
        """Group tags by source file."""
        # Implementation
```

## Performance Considerations

**Benchmarks** (expected):

- Template loading: <5ms (first time), <1ms (cached)
- Rendering small role (10 vars): ~20ms
- Rendering large role (100 vars): ~80ms
- Batch 10 roles: <2s total

**Optimizations**:

1. Precompile templates at initialization
2. Cache Jinja2 environment
3. Lazy-load embedded templates
4. Stream output for large roles

## Security Considerations

**Template Injection**: Not a concern (no user-provided template code execution)

**XSS in HTML**: Mitigated by Jinja2 auto-escaping + markupsafe

**Path Traversal**: Validate custom template paths, no `../` allowed

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Template Engine | Jinja2 3.1+ | Industry standard, excellent docs, mature |
| Template Inheritance | Base + format-specific | DRY, maintainable |
| Default Templates | Embedded via importlib.resources | Zero-config experience |
| Custom Filters | 5 filters (escape, format, fence) | Minimal, focused |
| HTML Styling | Embedded CSS | No external deps, portable |
| RST Target | Sphinx-compatible | Most common RST use case |
| Template Discovery | 4-level fallback | Flexibility + defaults |

## Next Steps

1. Implement OutputFormat enum
2. Create DocumentRenderer protocol
3. Build TemplateEngine with filter registration
4. Create base.j2 template structure
5. Implement template discovery logic
6. Unit test custom filters
