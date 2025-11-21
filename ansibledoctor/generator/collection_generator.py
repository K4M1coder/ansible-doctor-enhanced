"""Collection documentation generator.

Generates comprehensive documentation for Ansible collections across multiple
output formats (Markdown, HTML, RST) using Jinja2 templates.

T146-T155: Implementation to pass T106-T112 tests (TDD GREEN phase).
T164: Refactored template context builder to separate class (REFACTOR phase).
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import Plugin, PluginCatalog, PluginType


class RoleInfo:
    """Simple role information container for template rendering.
    
    Provides a minimal interface for role data in templates without
    exposing full role parser complexity. This follows the Interface
    Segregation Principle (ISP) from SOLID.
    
    Attributes:
        name: Role name (required)
        description: Optional role description
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """Initialize role info.
        
        Args:
            name: Role name
            description: Optional role description
        """
        self.name = name
        self.description = description


class CollectionTemplateContext:
    """Builder for collection template context.
    
    Extracts template context building logic into a separate class following
    the Single Responsibility Principle. This improves testability and makes
    the context building logic reusable.
    
    This is the T164 refactoring - extracting context builder to separate class.
    
    Attributes:
        collection: AnsibleCollection instance
        plugins: List of Plugin instances
    
    Example:
        >>> builder = CollectionTemplateContext(collection, plugins)
        >>> context = builder.build()
        >>> context["fqcn"]
        'my_namespace.my_collection'
    """
    
    def __init__(self, collection: AnsibleCollection, plugins: List[Plugin]):
        """Initialize context builder.
        
        Args:
            collection: AnsibleCollection instance
            plugins: List of Plugin instances
        """
        self.collection = collection
        self.plugins = plugins
    
    def build(self) -> Dict[str, Any]:
        """Build template context from collection data.
        
        Constructs a dictionary containing all data needed for template rendering,
        including collection metadata, roles, plugins grouped by type, and
        generation timestamp.
        
        Returns:
            Dictionary with template context:
                - collection: AnsibleCollection instance
                - metadata: GalaxyMetadata instance
                - fqcn: Fully qualified collection name (namespace.name)
                - roles: List of RoleInfo objects
                - plugins_by_type: Dict mapping PluginType to List[Plugin]
                - generation_date: Current datetime
        
        Example:
            >>> context = builder.build()
            >>> context["fqcn"]
            'my_namespace.my_collection'
            >>> context["plugins_by_type"][PluginType.MODULE]
            [Plugin(name="my_module", ...)]
        """
        # Group plugins by type using PluginCatalog
        catalog = PluginCatalog(self.plugins)
        plugins_by_type = catalog.group_by_type()
        
        # Build role data list
        roles_data = [RoleInfo(name=role) for role in self.collection.roles]
        
        return {
            "collection": self.collection,
            "metadata": self.collection.metadata,
            "fqcn": self.collection.fqcn,
            "roles": roles_data,
            "plugins_by_type": plugins_by_type,
            "generation_date": datetime.now(),
        }


class CollectionDocumentationGenerator:
    """Generator for Ansible collection documentation.
    
    Provides comprehensive documentation generation for Ansible collections,
    supporting multiple output formats and custom templates. Follows the same
    pattern as MarkdownRenderer/HtmlRenderer for consistency.
    
    Attributes:
        collection: AnsibleCollection instance with metadata, roles, plugins
        plugins: Optional list of Plugin instances for detailed plugin info
    
    Example:
        >>> metadata = GalaxyMetadata(namespace="my", name="coll", version="1.0.0", ...)
        >>> collection = AnsibleCollection(metadata=metadata, roles=["web"], plugins={})
        >>> generator = CollectionDocumentationGenerator(collection=collection)
        >>> markdown = generator.generate(format="markdown")
        >>> generator.generate(format="html", output_path=Path("docs/README.html"))
    """
    
    def __init__(
        self,
        collection: AnsibleCollection,
        plugins: Optional[List[Plugin]] = None
    ):
        """Initialize collection documentation generator.
        
        Args:
            collection: AnsibleCollection instance with metadata and structure
            plugins: Optional list of Plugin instances for detailed documentation
        """
        self.collection = collection
        self.plugins = plugins or []
        self._engine: Optional[TemplateEngine] = None
        self._embedded_loader: Optional[EmbeddedTemplateLoader] = None
    
    def _get_engine(self) -> TemplateEngine:
        """Get or create template engine instance (lazy initialization).
        
        Returns:
            TemplateEngine instance configured for collection templates
        """
        if self._engine is None:
            self._engine = TemplateEngine.create()
        return self._engine
    
    def _get_embedded_loader(self) -> EmbeddedTemplateLoader:
        """Get or create embedded template loader (lazy initialization).
        
        Returns:
            EmbeddedTemplateLoader for default collection templates
        """
        if self._embedded_loader is None:
            self._embedded_loader = EmbeddedTemplateLoader()
        return self._embedded_loader
    
    def build_context(self) -> Dict[str, Any]:
        """Build template context from collection data.
        
        Delegates to CollectionTemplateContext builder (T164 refactoring).
        
        Returns:
            Dictionary with template context
        
        Example:
            >>> context = generator.build_context()
            >>> context["fqcn"]
            'my_namespace.my_collection'
        """
        builder = CollectionTemplateContext(self.collection, self.plugins)
        return builder.build()
    
    def generate(
        self,
        format: str = "markdown",
        output_path: Optional[Path] = None,
        template_path: Optional[str] = None
    ) -> str:
        """Generate collection documentation.
        
        Renders collection documentation in the specified format using either
        a custom template (if provided) or the default embedded template.
        Optionally writes output to a file.
        
        Args:
            format: Output format ("markdown", "html", or "rst")
            output_path: Optional file path to write output
            template_path: Optional custom template path
        
        Returns:
            Rendered documentation as string
        
        Raises:
            ValueError: If format is not supported
            FileNotFoundError: If template_path doesn't exist
        
        Example:
            >>> output = generator.generate(format="markdown")
            >>> generator.generate(format="html", output_path=Path("docs/index.html"))
            >>> generator.generate(format="markdown", template_path="custom.j2")
        """
        # Build template context
        context = self.build_context()
        
        # Get template engine
        engine = self._get_engine()
        
        # Determine template to use
        if template_path:
            # Custom template provided (T167: improved error messages)
            template_path_obj = Path(template_path)
            if not template_path_obj.exists():
                raise FileNotFoundError(
                    f"Custom template not found: {template_path}\n"
                    f"  → Check that the template file exists and the path is correct.\n"
                    f"  → Use an absolute path or path relative to current directory.\n"
                    f"  → Default templates are embedded and available without path."
                )
            try:
                template_content = template_path_obj.read_text(encoding="utf-8")
                template = engine.environment.from_string(template_content)
            except Exception as e:
                raise ValueError(
                    f"Failed to load custom template: {template_path}\n"
                    f"  → Error: {str(e)}\n"
                    f"  → Ensure the template is valid Jinja2 syntax.\n"
                    f"  → Check for proper template block structure."
                ) from e
        else:
            # Use default embedded template (T167: improved error messages)
            loader = self._get_embedded_loader()
            try:
                output_format = OutputFormat[format.upper()]
            except KeyError:
                supported_formats = ", ".join([f.name.lower() for f in OutputFormat])
                raise ValueError(
                    f"Unsupported output format: '{format}'\n"
                    f"  → Supported formats: {supported_formats}\n"
                    f"  → Use lowercase format names (e.g., 'markdown', not 'MARKDOWN')\n"
                    f"  → Check the --format CLI option or format parameter."
                )
            try:
                template = loader.load_template("collection", output_format)
            except Exception as e:
                raise ValueError(
                    f"Failed to load embedded collection template for format '{format}'\n"
                    f"  → Error: {str(e)}\n"
                    f"  → This may indicate a bug in the template loader.\n"
                    f"  → Try using a custom template with --template option."
                ) from e
        
        # Render template with context (T167: improved error handling)
        try:
            output = template.render(**context)
        except Exception as e:
            raise ValueError(
                f"Failed to render collection documentation template\n"
                f"  → Error: {str(e)}\n"
                f"  → Collection: {self.collection.fqcn}\n"
                f"  → Check template syntax and context data.\n"
                f"  → Enable debug logging for more details."
            ) from e
        
        # Write to file if requested (T167: improved error handling)
        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(output, encoding="utf-8")
            except Exception as e:
                raise IOError(
                    f"Failed to write documentation to file: {output_path}\n"
                    f"  → Error: {str(e)}\n"
                    f"  → Check write permissions for the output directory.\n"
                    f"  → Ensure the path is valid and accessible."
                ) from e
        
        return output
