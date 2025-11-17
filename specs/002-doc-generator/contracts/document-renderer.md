# Protocol: DocumentRenderer

**Feature**: 002-doc-generator  
**Purpose**: Define contract for format-specific documentation renderers

## Protocol Definition

```python
from typing import Protocol, runtime_checkable
from pathlib import Path
from ansibledoctor.models.output_format import OutputFormat

@runtime_checkable
class DocumentRenderer(Protocol):
    """Protocol for rendering role documentation in specific formats.
    
    Implementations must provide format-specific rendering logic while
    maintaining consistent behavior across all formats.
    """
    
    @property
    def format(self) -> OutputFormat:
        """The output format this renderer produces.
        
        Returns:
            OutputFormat enum value (MARKDOWN, HTML, RST)
        """
        ...
    
    def render(
        self,
        role_data: dict,
        template_path: Path | None = None,
        **options
    ) -> str:
        """Render role documentation in this format.
        
        Args:
            role_data: Parsed role data from Feature 001 (JSON dict)
            template_path: Optional custom template path (overrides default)
            **options: Format-specific options:
                - embed_css (HTML): bool = True
                - generate_toc (HTML): bool = True
                - sphinx_compat (RST): bool = True
                - gfm_mode (Markdown): bool = True
        
        Returns:
            Rendered documentation content as string
        
        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateSyntaxError: If template has syntax errors
            ValidationError: If role_data doesn't match expected schema
        """
        ...
    
    def escape(self, text: str) -> str:
        """Escape text for this output format.
        
        Args:
            text: Raw text to escape
        
        Returns:
            Escaped text safe for this format
        
        Examples:
            Markdown: escape *, _, [, ], etc.
            HTML: escape <, >, &, etc.
            RST: escape *, `, _, \\, etc.
        """
        ...
    
    def code_block(self, code: str, language: str) -> str:
        """Format code block for this output format.
        
        Args:
            code: Source code content
            language: Programming language (yaml, bash, python, etc.)
        
        Returns:
            Formatted code block for this format
        
        Examples:
            Markdown: ```yaml\\ncode\\n```
            HTML: <pre><code class="language-yaml">code</code></pre>
            RST: .. code-block:: yaml\\n\\n   code
        """
        ...
    
    def validate_options(self, options: dict) -> None:
        """Validate format-specific options.
        
        Args:
            options: Options dict from render() call
        
        Raises:
            ValueError: If options are invalid for this renderer
        """
        ...
```

## Implementation Contract

**All DocumentRenderer implementations MUST**:

1. **Be stateless**: No instance variables affecting render output
2. **Be thread-safe**: Support concurrent rendering
3. **Validate input**: Check role_data schema before rendering
4. **Handle missing fields**: Gracefully handle optional fields
5. **Log operations**: Use structured logging for debugging
6. **Provide defaults**: Work with zero configuration
7. **Support custom templates**: Allow template override
8. **Escape correctly**: Prevent injection vulnerabilities

## Usage Example

```python
from ansibledoctor.generator.renderers import MarkdownRenderer
from pathlib import Path

# Initialize renderer
renderer = MarkdownRenderer()

# Load parsed role data
role_data = json.loads(Path("role.json").read_text())

# Render with default template
markdown = renderer.render(role_data)

# Render with custom template
custom_md = renderer.render(
    role_data,
    template_path=Path("custom-template.md.j2"),
    gfm_mode=True
)

# Write output
Path("README.md").write_text(markdown)
```

## Concrete Implementations

### MarkdownRenderer

```python
class MarkdownRenderer:
    """Render role documentation as Markdown (GFM)."""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.MARKDOWN
    
    def render(
        self,
        role_data: dict,
        template_path: Path | None = None,
        **options
    ) -> str:
        # Implementation
        gfm_mode = options.get("gfm_mode", True)
        # ... render logic
    
    def escape(self, text: str) -> str:
        # Escape: *, _, [, ], #, `, >, -, +, !
        return text.replace("*", "\\*").replace("_", "\\_")...
    
    def code_block(self, code: str, language: str) -> str:
        return f"```{language}\n{code}\n```"
```

### HtmlRenderer

```python
class HtmlRenderer:
    """Render role documentation as HTML5 with embedded CSS."""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.HTML
    
    def render(
        self,
        role_data: dict,
        template_path: Path | None = None,
        **options
    ) -> str:
        embed_css = options.get("embed_css", True)
        generate_toc = options.get("generate_toc", True)
        # ... render logic with CSS injection
    
    def escape(self, text: str) -> str:
        # Use markupsafe.escape
        from markupsafe import escape
        return escape(text)
    
    def code_block(self, code: str, language: str) -> str:
        escaped = self.escape(code)
        return f'<pre><code class="language-{language}">{escaped}</code></pre>'
    
    def generate_toc(self, role_data: dict) -> str:
        """Generate HTML table of contents."""
        # Implementation
```

### RstRenderer

```python
class RstRenderer:
    """Render role documentation as reStructuredText (Sphinx-compatible)."""
    
    @property
    def format(self) -> OutputFormat:
        return OutputFormat.RST
    
    def render(
        self,
        role_data: dict,
        template_path: Path | None = None,
        **options
    ) -> str:
        sphinx_compat = options.get("sphinx_compat", True)
        # ... render logic with Sphinx directives
    
    def escape(self, text: str) -> str:
        # Escape: *, `, _, \, [, ], <, >
        return text.replace("*", "\\*").replace("`", "\\`")...
    
    def code_block(self, code: str, language: str) -> str:
        indented = "\n".join(f"   {line}" for line in code.split("\n"))
        return f".. code-block:: {language}\n\n{indented}"
```

## Testing Contract

**Unit tests for DocumentRenderer implementations MUST verify**:

1. **Protocol compliance**: `isinstance(renderer, DocumentRenderer)`
2. **Format property**: Returns correct OutputFormat
3. **Render with defaults**: Works with no template_path
4. **Render with custom**: Accepts template_path
5. **Escape correctness**: All format-specific chars escaped
6. **Code block formatting**: Language hint and proper fencing
7. **Missing fields**: Handles optional fields gracefully
8. **Invalid input**: Raises appropriate exceptions
9. **Thread safety**: Concurrent renders produce identical output
10. **Options validation**: Rejects invalid options

## Integration Points

**DocumentRenderer interacts with**:

- **TemplateEngine**: Loads and compiles templates
- **TemplateContext**: Receives wrapped role data
- **CLI**: Invoked by `generate` command
- **FileSystem**: Reads templates, writes output

## Performance Requirements

**Each renderer MUST**:

- Render typical role (10 vars) in <50ms
- Render large role (100 vars) in <100ms
- Support template caching for repeated renders
- Use lazy evaluation for expensive operations (TOC generation, syntax highlighting)

## Error Handling

**Renderers MUST raise**:

```python
# Template not found
raise TemplateNotFoundError(
    template_path=path,
    searched_paths=[path1, path2, path3]
)

# Template syntax error
raise TemplateSyntaxError(
    template_path=path,
    line_number=42,
    message="Unexpected end of template"
)

# Invalid role data
raise ValidationError(
    field="variables[3].name",
    message="Missing required field"
)

# Invalid options
raise ValueError(
    f"Invalid option 'unknown_option' for {self.format.value} renderer"
)
```

## Extension Points

**Custom renderers can**:

1. Implement DocumentRenderer protocol
2. Register in RendererRegistry
3. Use custom template discovery logic
4. Provide format-specific options
5. Add custom filters to TemplateEngine

## Summary

**DocumentRenderer protocol provides**:

- ✅ Consistent interface across formats
- ✅ Type safety with runtime checking
- ✅ Clear contract for implementations
- ✅ Testable behavior specification
- ✅ Extension mechanism for custom formats
