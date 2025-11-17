# Data Model: Template Context & Output Formats

**Feature**: 002-doc-generator  
**Phase**: 9 - Foundation  
**Date**: 2025-11-17

## Overview

This document defines the data structures that flow through the documentation generator: input from parser, template context, and output specifications.

## Input: Parsed Role Data

**Source**: JSON output from Feature 001 `ansible-doctor parse` command

**Schema** (from AnsibleRole model):

```python
{
    "name": str,                    # Role name
    "description": str,             # Galaxy role description
    "author": str,                  # Role author
    "license": str,                 # License identifier
    "min_ansible_version": str,     # Minimum Ansible version
    "galaxy_tags": list[str],       # Galaxy tags
    "platforms": [                  # Supported platforms
        {
            "name": str,            # Platform name (e.g., "Ubuntu")
            "versions": list[str]   # Versions (e.g., ["20.04", "22.04"])
        }
    ],
    "dependencies": [               # Role dependencies
        {
            "name": str,            # Dependency role name
            "version": str | None,  # Version constraint
            "source": str | None    # Source (galaxy, github, etc.)
        }
    ],
    "variables": [                  # Role variables
        {
            "name": str,            # Variable name
            "value": Any,           # Default value
            "type": str,            # Inferred type (string, int, list, dict)
            "description": str,     # From @var annotation
            "source": str,          # "defaults" or "vars"
            "required": bool,       # From @var required attribute
            "deprecated": bool,     # From @var deprecated attribute
            "example": str | None   # From @var example attribute
        }
    ],
    "tags": [                       # Task tags
        {
            "name": str,            # Tag name
            "description": str,     # Tag description (if documented)
            "usage_count": int,     # Number of tasks using this tag
            "file_locations": list[str]  # ["tasks/main.yml:10", ...]
        }
    ],
    "todos": [                      # TODO annotations
        {
            "description": str,     # TODO text
            "file_path": str,       # Relative path to file
            "line_number": int,     # Line number
            "priority": str         # "low", "medium", "high", "critical"
        }
    ],
    "examples": [                   # Example code blocks
        {
            "title": str | None,    # Example title (from @example)
            "code": str,            # Example code content
            "description": str | None,  # Example description
            "language": str         # Detected language (yaml, bash, python, etc.)
        }
    ],
    "argument_specs": dict | None   # Argument specifications (if present)
}
```

## Template Context Wrapper

**Purpose**: Provide helper methods and computed properties for templates

```python
@dataclass
class TemplateContext:
    """Enriched context for template rendering."""
    
    role: dict  # Raw parsed role data
    
    # Computed properties
    @property
    def has_variables(self) -> bool:
        """Check if role has any variables."""
        return len(self.role.get("variables", [])) > 0
    
    @property
    def has_tags(self) -> bool:
        """Check if role uses any tags."""
        return len(self.role.get("tags", [])) > 0
    
    @property
    def has_examples(self) -> bool:
        """Check if role has example code."""
        return len(self.role.get("examples", [])) > 0
    
    @property
    def has_todos(self) -> bool:
        """Check if role has TODO items."""
        return len(self.role.get("todos", [])) > 0
    
    @property
    def required_variables(self) -> list[dict]:
        """Get variables marked as required."""
        return [v for v in self.role.get("variables", []) 
                if v.get("required", False)]
    
    @property
    def deprecated_variables(self) -> list[dict]:
        """Get variables marked as deprecated."""
        return [v for v in self.role.get("variables", []) 
                if v.get("deprecated", False)]
    
    @property
    def critical_todos(self) -> list[dict]:
        """Get high-priority TODO items."""
        return [t for t in self.role.get("todos", []) 
                if t["priority"] in ("critical", "high")]
    
    def group_variables_by_source(self) -> dict[str, list[dict]]:
        """Group variables by source (defaults vs vars)."""
        result = {"defaults": [], "vars": []}
        for var in self.role.get("variables", []):
            result[var["source"]].append(var)
        return result
    
    def group_tags_by_file(self) -> dict[str, list[dict]]:
        """Group tags by primary file location."""
        result = {}
        for tag in self.role.get("tags", []):
            if tag["file_locations"]:
                primary_file = tag["file_locations"][0].split(":")[0]
                result.setdefault(primary_file, []).append(tag)
        return result
    
    def sort_todos_by_priority(self) -> list[dict]:
        """Sort TODOs by priority (critical → high → medium → low)."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(
            self.role.get("todos", []),
            key=lambda t: priority_order.get(t["priority"], 3)
        )
```

## Output Format Enum

```python
from enum import Enum

class OutputFormat(str, Enum):
    """Supported documentation output formats."""
    
    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"
    
    @property
    def extension(self) -> str:
        """Get file extension for this format."""
        return {
            OutputFormat.MARKDOWN: ".md",
            OutputFormat.HTML: ".html",
            OutputFormat.RST: ".rst"
        }[self]
    
    @property
    def default_filename(self) -> str:
        """Get default output filename."""
        return {
            OutputFormat.MARKDOWN: "README.md",
            OutputFormat.HTML: "index.html",
            OutputFormat.RST: "index.rst"
        }[self]
    
    @property
    def mime_type(self) -> str:
        """Get MIME type for this format."""
        return {
            OutputFormat.MARKDOWN: "text/markdown",
            OutputFormat.HTML: "text/html",
            OutputFormat.RST: "text/x-rst"
        }[self]
```

## Rendering Result

```python
@dataclass
class RenderResult:
    """Result of template rendering operation."""
    
    content: str                # Generated documentation content
    format: OutputFormat        # Output format used
    template_path: Path         # Template file path (for debugging)
    render_time_ms: float       # Rendering duration in milliseconds
    warnings: list[str]         # Non-fatal issues (e.g., missing optional fields)
    
    def write_to_file(self, output_path: Path) -> None:
        """Write rendered content to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content, encoding="utf-8")
    
    def to_dict(self) -> dict:
        """Serialize for logging/debugging."""
        return {
            "format": self.format.value,
            "template": str(self.template_path),
            "render_time_ms": self.render_time_ms,
            "content_length": len(self.content),
            "warnings": self.warnings
        }
```

## Template Filter Context

**Custom filters receive these parameters**:

```python
# markdown_escape(text: str) -> str
{{ variable.description | markdown_escape }}

# html_escape(text: str) -> str (built-in)
{{ variable.description | escape }}

# rst_escape(text: str) -> str
{{ variable.description | rst_escape }}

# format_priority(priority: str) -> str
{{ todo.priority | format_priority }}
# Returns: "🔴 CRITICAL", "🟡 MEDIUM", etc.

# code_fence(code: str, language: str, format: OutputFormat) -> str
{{ example.code | code_fence(example.language, output_format) }}
# Markdown: ```yaml\n{code}\n```
# HTML: <pre><code class="language-yaml">{code}</code></pre>
# RST: .. code-block:: yaml\n\n   {code}

# format_file_location(location: str) -> str
{{ tag.file_locations[0] | format_file_location }}
# Input: "tasks/main.yml:42"
# Markdown: `tasks/main.yml:42`
# HTML: <code>tasks/main.yml:42</code>
# RST: ``tasks/main.yml:42``

# truncate_description(text: str, length: int = 100) -> str
{{ variable.description | truncate_description(80) }}
# Returns: "Long description text that..." (with ellipsis)
```

## Template Inheritance Structure

```
base.j2 (abstract base)
    ├── markdown.j2 (extends base)
    ├── html.j2 (extends base)
    └── rst.j2 (extends base)
```

**Base Template Blocks**:

```jinja2
{# base.j2 - Common structure #}
{% block document_start %}{% endblock %}
{% block header %}{% endblock %}
{% block toc %}{% endblock %}
{% block metadata %}{% endblock %}
{% block requirements %}{% endblock %}
{% block variables %}{% endblock %}
{% block tags %}{% endblock %}
{% block examples %}{% endblock %}
{% block todos %}{% endblock %}
{% block footer %}{% endblock %}
{% block document_end %}{% endblock %}
```

## Error Handling Data

```python
@dataclass
class TemplateError:
    """Template rendering error details."""
    
    error_type: str             # "TemplateNotFound", "TemplateSyntaxError", etc.
    message: str                # Error message
    template_path: Path | None  # Template file (if known)
    line_number: int | None     # Line number in template (if applicable)
    context: dict               # Additional context for debugging
    
    def to_user_message(self) -> str:
        """Format error for CLI output."""
        if self.line_number:
            return f"{self.error_type} in {self.template_path}:{self.line_number}\n{self.message}"
        return f"{self.error_type}: {self.message}"
```

## Validation Schema

**JSON Schema for validating parser output**:

```python
ROLE_DATA_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "author": {"type": "string"},
        "license": {"type": "string"},
        "variables": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "value", "type", "source"],
                "properties": {
                    "name": {"type": "string"},
                    "value": {},  # Any type
                    "type": {"type": "string"},
                    "description": {"type": "string"},
                    "source": {"enum": ["defaults", "vars"]},
                    "required": {"type": "boolean"},
                    "deprecated": {"type": "boolean"}
                }
            }
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "usage_count"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "usage_count": {"type": "integer", "minimum": 0},
                    "file_locations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "todos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "file_path", "line_number", "priority"],
                "properties": {
                    "description": {"type": "string"},
                    "file_path": {"type": "string"},
                    "line_number": {"type": "integer", "minimum": 1},
                    "priority": {"enum": ["low", "medium", "high", "critical"]}
                }
            }
        },
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["code", "language"],
                "properties": {
                    "title": {"type": ["string", "null"]},
                    "code": {"type": "string", "minLength": 1},
                    "description": {"type": ["string", "null"]},
                    "language": {"type": "string"}
                }
            }
        }
    }
}
```

## Summary

**Data Flow**:

1. Parser JSON → Validation against schema
2. Valid JSON → TemplateContext wrapper (adds helpers)
3. TemplateContext → Jinja2 template (with custom filters)
4. Rendered string → RenderResult (with metadata)
5. RenderResult → File output

**Key Design Decisions**:

- **Immutable input**: Parser JSON is never modified
- **Rich context**: TemplateContext provides computed properties for templates
- **Type safety**: OutputFormat enum prevents invalid format strings
- **Error enrichment**: TemplateError captures full context for debugging
- **Validation**: JSON schema ensures parser output compatibility
