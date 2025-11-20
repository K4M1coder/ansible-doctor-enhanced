"""Collection documentation generator.

Generates comprehensive documentation for Ansible collections across multiple
output formats (Markdown, HTML, RST) using Jinja2 templates.

T146-T155: Implementation to pass T106-T112 tests (TDD GREEN phase).
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.generator.loaders import EmbeddedTemplateLoader
from ansibledoctor.generator.models import OutputFormat
from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.plugin import Plugin, PluginCatalog, PluginType


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
        
        Constructs a dictionary containing all data needed for template rendering,
        including collection metadata, roles, plugins grouped by type, and
        generation timestamp.
        
        Returns:
            Dictionary with template context:
                - collection: AnsibleCollection instance
                - metadata: GalaxyMetadata instance
                - fqcn: Fully qualified collection name (namespace.name)
                - roles: List of role data dictionaries
                - plugins_by_type: Dict mapping PluginType to List[Plugin]
                - generation_date: Current datetime
        
        Example:
            >>> context = generator.build_context()
            >>> context["fqcn"]
            'my_namespace.my_collection'
            >>> context["plugins_by_type"][PluginType.MODULE]
            [Plugin(name="my_module", ...)]
        """
        # Group plugins by type using PluginCatalog
        catalog = PluginCatalog(self.plugins)
        plugins_by_type = catalog.group_by_type()
        
        # Build role data list - create simple objects with name attribute
        # This matches the template expectation for role.name and role.description
        class RoleInfo:
            def __init__(self, name: str):
                self.name = name
                self.description = None  # Optional description
        
        roles_data = [RoleInfo(name=role) for role in self.collection.roles]
        
        return {
            "collection": self.collection,
            "metadata": self.collection.metadata,
            "fqcn": self.collection.fqcn,
            "roles": roles_data,
            "plugins_by_type": plugins_by_type,
            "generation_date": datetime.now(),
        }
    
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
            # Custom template provided
            template_path_obj = Path(template_path)
            if not template_path_obj.exists():
                raise FileNotFoundError(
                    f"Custom template not found: {template_path}"
                )
            template_content = template_path_obj.read_text(encoding="utf-8")
            template = engine.environment.from_string(template_content)
        else:
            # Use default embedded template
            loader = self._get_embedded_loader()
            try:
                output_format = OutputFormat[format.upper()]
            except KeyError:
                raise ValueError(
                    f"Unsupported format: {format}. "
                    f"Supported formats: markdown, html, rst"
                )
            template = loader.load_template("collection", output_format)
        
        # Render template with context
        output = template.render(**context)
        
        # Write to file if requested
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding="utf-8")
        
        return output
