# Protocol: TemplateLoader

**Feature**: 002-doc-generator  
**Purpose**: Define contract for template discovery and loading

## Protocol Definition

```python
from typing import Protocol, runtime_checkable
from pathlib import Path
from ansibledoctor.models.output_format import OutputFormat

@runtime_checkable
class TemplateLoader(Protocol):
    """Protocol for discovering and loading documentation templates.
    
    Implementations handle template resolution with fallback chain:
    1. Explicit path (--template flag)
    2. Project-local (.ansible-doctor/templates/)
    3. User global (~/.ansible-doctor/templates/)
    4. Embedded defaults (package resources)
    """
    
    def discover_template(
        self,
        format: OutputFormat,
        custom_path: Path | None = None,
        search_dirs: list[Path] | None = None
    ) -> Path:
        """Discover template file with fallback chain.
        
        Args:
            format: Output format to find template for
            custom_path: Explicit template path (highest priority)
            search_dirs: Additional directories to search (before defaults)
        
        Returns:
            Path to template file (may be embedded resource path)
        
        Raises:
            TemplateNotFoundError: If no template found in fallback chain
        
        Search order:
            1. custom_path (if provided)
            2. search_dirs (if provided)
            3. .ansible-doctor/templates/<format>.j2 (project-local)
            4. ~/.ansible-doctor/templates/<format>.j2 (user global)
            5. embedded default (package resource)
        """
        ...
    
    def load_template_content(self, template_path: Path) -> str:
        """Load template file content.
        
        Args:
            template_path: Path to template (file or embedded resource)
        
        Returns:
            Template content as string
        
        Raises:
            TemplateNotFoundError: If path doesn't exist
            PermissionError: If file not readable
        """
        ...
    
    def list_available_templates(
        self,
        format: OutputFormat | None = None
    ) -> dict[str, list[Path]]:
        """List all available templates by location.
        
        Args:
            format: Optional filter by format (None = all formats)
        
        Returns:
            Dict mapping location to template paths:
                {
                    "project": [Path(".ansible-doctor/templates/markdown.j2")],
                    "user": [Path("~/.ansible-doctor/templates/html.j2")],
                    "embedded": [Path("ansibledoctor/generator/templates/markdown.j2")]
                }
        """
        ...
    
    def get_embedded_template_path(self, format: OutputFormat) -> Path:
        """Get path to embedded default template.
        
        Args:
            format: Output format
        
        Returns:
            Path to embedded template (via importlib.resources)
        
        Raises:
            TemplateNotFoundError: If embedded template missing (shouldn't happen)
        """
        ...
    
    def validate_template(self, template_path: Path) -> tuple[bool, list[str]]:
        """Validate template syntax and structure.
        
        Args:
            template_path: Path to template file
        
        Returns:
            Tuple of (is_valid, list_of_issues)
            - is_valid: True if template has no errors
            - list_of_issues: Warning/error messages (empty if valid)
        
        Example:
            (True, []) - Valid template
            (False, ["Line 42: Unexpected end of block", "Line 55: Unknown filter"]) - Invalid
        """
        ...
```

## Implementation Contract

**TemplateLoader implementations MUST**:

1. **Follow search order**: Respect fallback chain priority
2. **Handle embedded resources**: Use `importlib.resources` for package templates
3. **Cross-platform paths**: Use `pathlib.Path` consistently
4. **Cache results**: Memoize template discovery for performance
5. **Thread-safe**: Support concurrent template loading
6. **Validate syntax**: Check Jinja2 syntax before returning
7. **Provide diagnostics**: Clear error messages with search paths

## Default Implementation

```python
from pathlib import Path
from importlib import resources
import structlog

logger = structlog.get_logger()

class DefaultTemplateLoader:
    """Default template discovery with 4-level fallback."""
    
    def __init__(self):
        self._cache: dict[OutputFormat, Path] = {}
    
    def discover_template(
        self,
        format: OutputFormat,
        custom_path: Path | None = None,
        search_dirs: list[Path] | None = None
    ) -> Path:
        """Discover template with fallback chain."""
        # Cache check
        cache_key = (format, custom_path, tuple(search_dirs or []))
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 1. Explicit custom path
        if custom_path and custom_path.exists():
            logger.info("template_discovered", source="custom", path=str(custom_path))
            self._cache[cache_key] = custom_path
            return custom_path
        
        # 2. Additional search directories
        if search_dirs:
            for search_dir in search_dirs:
                candidate = search_dir / f"{format.value}.j2"
                if candidate.exists():
                    logger.info("template_discovered", source="search_dir", path=str(candidate))
                    self._cache[cache_key] = candidate
                    return candidate
        
        # 3. Project-local
        project_template = Path.cwd() / ".ansible-doctor" / "templates" / f"{format.value}.j2"
        if project_template.exists():
            logger.info("template_discovered", source="project", path=str(project_template))
            self._cache[cache_key] = project_template
            return project_template
        
        # 4. User global
        user_template = Path.home() / ".ansible-doctor" / "templates" / f"{format.value}.j2"
        if user_template.exists():
            logger.info("template_discovered", source="user", path=str(user_template))
            self._cache[cache_key] = user_template
            return user_template
        
        # 5. Embedded default
        embedded = self.get_embedded_template_path(format)
        logger.info("template_discovered", source="embedded", format=format.value)
        self._cache[cache_key] = embedded
        return embedded
    
    def load_template_content(self, template_path: Path) -> str:
        """Load template file content."""
        try:
            return template_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise TemplateNotFoundError(
                template_path=template_path,
                searched_paths=[template_path]
            )
        except PermissionError as e:
            raise PermissionError(
                f"Cannot read template {template_path}: {e}"
            )
    
    def get_embedded_template_path(self, format: OutputFormat) -> Path:
        """Get embedded template using importlib.resources."""
        # For Python 3.9+
        from importlib.resources import files
        
        template_name = f"{format.value}.j2"
        templates_dir = files("ansibledoctor.generator") / "templates"
        template_path = templates_dir / template_name
        
        if not template_path.is_file():
            raise TemplateNotFoundError(
                template_path=Path(template_name),
                searched_paths=[Path(str(templates_dir))]
            )
        
        return Path(str(template_path))
    
    def list_available_templates(
        self,
        format: OutputFormat | None = None
    ) -> dict[str, list[Path]]:
        """List all available templates by location."""
        result = {
            "project": [],
            "user": [],
            "embedded": []
        }
        
        formats = [format] if format else list(OutputFormat)
        
        for fmt in formats:
            # Project-local
            project = Path.cwd() / ".ansible-doctor" / "templates" / f"{fmt.value}.j2"
            if project.exists():
                result["project"].append(project)
            
            # User global
            user = Path.home() / ".ansible-doctor" / "templates" / f"{fmt.value}.j2"
            if user.exists():
                result["user"].append(user)
            
            # Embedded
            try:
                embedded = self.get_embedded_template_path(fmt)
                result["embedded"].append(embedded)
            except TemplateNotFoundError:
                pass
        
        return result
    
    def validate_template(self, template_path: Path) -> tuple[bool, list[str]]:
        """Validate template syntax."""
        from jinja2 import Environment, TemplateSyntaxError
        
        issues = []
        
        try:
            content = self.load_template_content(template_path)
            env = Environment()
            env.parse(content)
            return (True, [])
        except TemplateSyntaxError as e:
            issues.append(f"Line {e.lineno}: {e.message}")
            return (False, issues)
        except Exception as e:
            issues.append(f"Validation error: {e}")
            return (False, issues)
```

## Usage Example

```python
from ansibledoctor.generator.template_loader import DefaultTemplateLoader
from ansibledoctor.models.output_format import OutputFormat

loader = DefaultTemplateLoader()

# Discover template with fallback
markdown_template = loader.discover_template(OutputFormat.MARKDOWN)

# Load content
content = loader.load_template_content(markdown_template)

# List available templates
available = loader.list_available_templates()
print(f"Project templates: {available['project']}")
print(f"User templates: {available['user']}")
print(f"Embedded templates: {available['embedded']}")

# Validate custom template
is_valid, issues = loader.validate_template(Path("custom.j2"))
if not is_valid:
    print(f"Template has issues: {issues}")
```

## CLI Integration

```bash
# Use default template (embedded)
ansible-doctor generate role/ --format markdown

# Use custom template (explicit)
ansible-doctor generate role/ --template my-template.j2

# Use project-local template (auto-discovered)
# .ansible-doctor/templates/markdown.j2
ansible-doctor generate role/ --format markdown

# List available templates
ansible-doctor templates list

# Validate custom template
ansible-doctor templates validate my-template.j2
```

## Testing Contract

**Tests MUST verify**:

1. **Fallback chain order**: Custom → project → user → embedded
2. **Cache behavior**: Repeated calls use cache
3. **Embedded resource loading**: Works with package resources
4. **Cross-platform paths**: Windows and Unix paths
5. **Permission handling**: Graceful errors for unreadable files
6. **Validation**: Catches syntax errors with line numbers
7. **Listing**: Finds all templates in all locations
8. **Thread safety**: Concurrent discoveries don't conflict

## Error Handling

```python
# Template not found anywhere
raise TemplateNotFoundError(
    template_path=Path("custom.j2"),
    searched_paths=[
        Path.cwd() / ".ansible-doctor/templates",
        Path.home() / ".ansible-doctor/templates",
        Path("ansibledoctor/generator/templates")
    ]
)

# Permission denied
raise PermissionError(
    "Cannot read template custom.j2: Permission denied"
)

# Syntax error
raise TemplateSyntaxError(
    template_path=Path("custom.j2"),
    line_number=42,
    message="Unexpected end of block"
)
```

## Performance Considerations

**Optimizations**:

1. **Caching**: Memoize discovery results (cleared on format change)
2. **Lazy loading**: Don't read embedded templates until needed
3. **Batch validation**: Validate multiple templates concurrently
4. **Path normalization**: Resolve paths once, cache result

**Benchmarks**:

- Discovery (cached): <1ms
- Discovery (uncached, embedded): <5ms
- Discovery (uncached, filesystem): <10ms
- Validation: <20ms per template

## Summary

**TemplateLoader protocol provides**:

- ✅ Flexible template discovery (4-level fallback)
- ✅ Embedded defaults for zero-config
- ✅ Custom template support
- ✅ Syntax validation before rendering
- ✅ Clear error messages with search paths
- ✅ Performance through caching
