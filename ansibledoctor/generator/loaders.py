"""Template loaders for discovering and loading templates."""

import importlib.resources as pkg_resources
from pathlib import Path
from typing import Protocol, runtime_checkable

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, Template

from ansibledoctor.generator.errors import TemplateNotFoundError
from ansibledoctor.generator.filters import FILTERS
from ansibledoctor.generator.output_format import OutputFormat


@runtime_checkable
class TemplateLoader(Protocol):
    """Protocol for template loading implementations."""

    def load_template(self, template_name: str, output_format: OutputFormat) -> Template:
        """Load template by name and format.

        Args:
            template_name: Template identifier (e.g., "role", "collection")
            output_format: Target output format

        Returns:
            Loaded Jinja2 Template

        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        ...

    def discover_templates(self, output_format: OutputFormat) -> list[str]:
        """Discover available templates for format.

        Args:
            output_format: Target output format

        Returns:
            List of template names (without extension/format)
        """
        ...

    def validate_template(self, template_name: str, output_format: OutputFormat) -> bool:
        """Check if template exists.

        Args:
            template_name: Template identifier
            output_format: Target output format

        Returns:
            True if template exists
        """
        ...


class FileSystemTemplateLoader:
    """Load templates from filesystem directory hierarchy.

    Supports 4-level directory structure:
    - templates/{format}/{type}.j2
    - templates/{format}/{category}/{type}.j2
    - templates/{type}.{format}.j2
    - templates/{type}.j2

    Example structure:
        templates/
        ├── markdown/
        │   ├── role.j2
        │   └── collection.j2
        ├── html/
        │   └── role.j2
        └── role.md.j2
    """

    def __init__(self, template_dir: str | Path):
        """Initialize loader with template directory.

        Args:
            template_dir: Root directory containing templates

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        self.template_dir = Path(template_dir)
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        if not self.template_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {template_dir}")

    def load_template(self, template_name: str, output_format: OutputFormat) -> Template:
        """Load template by name and format.

        Searches in order:
        1. {format}/{template_name}.j2
        2. {template_name}.{format}.j2
        3. {template_name}.j2

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            Loaded template

        Raises:
            TemplateNotFoundError: If template not found
        """
        template_path = self._find_template(template_name, output_format)
        if template_path is None:
            search_paths = self._get_search_paths(template_name, output_format)
            raise TemplateNotFoundError(template_name, [str(p) for p in search_paths])

        # Create loader that can resolve includes from format-specific and root dirs
        format_dir = self.template_dir / output_format.value
        search_dirs = []
        if format_dir.exists():
            search_dirs.append(str(format_dir))
        search_dirs.append(str(self.template_dir))

        loader = FileSystemLoader(search_dirs)
        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.filters.update(FILTERS)

        # Load template using the loader (supports {% include %})
        template_filename = template_path.name
        if template_path.parent == format_dir:
            # Template is in format dir, use just the filename
            return env.get_template(template_filename)
        else:
            # Template is in root or other location, use relative path
            rel_path = template_path.relative_to(self.template_dir)
            return env.get_template(str(rel_path))

    def discover_templates(self, output_format: OutputFormat) -> list[str]:
        """Discover available templates for format.

        Args:
            output_format: Target format

        Returns:
            List of template names
        """
        templates = set()

        # Search format-specific directory
        format_dir = self.template_dir / output_format.value
        if format_dir.exists():
            for template_file in format_dir.glob("*.j2"):
                templates.add(template_file.stem)

        # Get format extension (e.g., "md" for markdown)
        format_ext = output_format.file_extension.lstrip(".")

        # Search root directory for format-specific templates
        # Pattern: {name}.{ext}.j2 (e.g., "collection.md.j2")
        for template_file in self.template_dir.glob(f"*.{format_ext}.j2"):
            # Extract name without format suffix
            name = template_file.stem.removesuffix(f".{format_ext}")
            templates.add(name)

        # Search root directory for generic templates
        for template_file in self.template_dir.glob("*.j2"):
            name = template_file.stem
            # Skip if it's a format-specific template (contains extension in name)
            # Check for .md, .html, .rst in the stem
            if any(f".{fmt.file_extension.lstrip('.')}" in name for fmt in OutputFormat):
                continue
            templates.add(name)

        return sorted(templates)

    def validate_template(self, template_name: str, output_format: OutputFormat) -> bool:
        """Check if template exists.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            True if template exists
        """
        return self._find_template(template_name, output_format) is not None

    def _find_template(self, template_name: str, output_format: OutputFormat) -> Path | None:
        """Find template file in search hierarchy.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            Path to template file or None if not found
        """
        search_paths = self._get_search_paths(template_name, output_format)

        for path in search_paths:
            if path.exists() and path.is_file():
                return path

        return None

    def _get_search_paths(self, template_name: str, output_format: OutputFormat) -> list[Path]:
        """Get ordered list of paths to search.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            List of paths in priority order
        """
        # Get format extension (e.g., "md" for markdown)
        format_ext = output_format.file_extension.lstrip(".")

        return [
            # 1. Format-specific directory
            self.template_dir / output_format.value / f"{template_name}.j2",
            # 2. Root with format suffix
            self.template_dir / f"{template_name}.{format_ext}.j2",
            # 3. Root generic
            self.template_dir / f"{template_name}.j2",
        ]


class EmbeddedTemplateLoader:
    """Load templates from package resources.

    Templates embedded in the package under:
    ansibledoctor.generator.templates/
    """

    def __init__(self, package: str = "ansibledoctor.generator"):
        """Initialize loader with package name.

        Args:
            package: Package containing templates directory
        """
        self.package = package
        self.templates_path = "templates"

    def load_template(self, template_name: str, output_format: OutputFormat) -> Template:
        """Load embedded template.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            Loaded template

        Raises:
            TemplateNotFoundError: If template not found
        """
        # Check if template exists first
        content = self._read_template(template_name, output_format)
        if content is None:
            raise TemplateNotFoundError(
                template_name,
                [f"{self.package}.{self.templates_path}/{output_format.value}/{template_name}.j2"],
            )

        # Create environment with PackageLoader for include support
        # The loader searches format-specific dir first, then root templates
        try:
            format_loader = PackageLoader(
                self.package, f"{self.templates_path}/{output_format.value}"
            )
            root_loader = PackageLoader(self.package, self.templates_path)
            loader = ChoiceLoader([format_loader, root_loader])
        except (ModuleNotFoundError, ValueError):
            # Fallback if package loader doesn't work
            loader = None

        env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.filters.update(FILTERS)

        # If we have a loader, use get_template for include support
        if loader:
            return env.get_template(f"{template_name}.j2")
        else:
            # Fallback to string template (no include support)
            return env.from_string(content)

    def discover_templates(self, output_format: OutputFormat) -> list[str]:
        """Discover embedded templates.

        Args:
            output_format: Target format

        Returns:
            List of template names
        """
        templates = set()

        try:
            # Access package resources
            if hasattr(pkg_resources, "files"):
                # Python 3.9+
                files = pkg_resources.files(self.package)
                templates_dir = files / self.templates_path / output_format.value

                if templates_dir.is_dir():
                    for item in templates_dir.iterdir():
                        if item.name.endswith(".j2"):
                            templates.add(item.name.removesuffix(".j2"))
        except (ModuleNotFoundError, FileNotFoundError, AttributeError):
            pass

        return sorted(templates)

    def validate_template(self, template_name: str, output_format: OutputFormat) -> bool:
        """Check if embedded template exists.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            True if template exists
        """
        return self._read_template(template_name, output_format) is not None

    def _read_template(self, template_name: str, output_format: OutputFormat) -> str | None:
        """Read template content from package resources.

        Args:
            template_name: Template identifier
            output_format: Target format

        Returns:
            Template content or None if not found
        """
        try:
            if hasattr(pkg_resources, "files"):
                # Python 3.9+
                files = pkg_resources.files(self.package)
                template_file = (
                    files / self.templates_path / output_format.value / f"{template_name}.j2"
                )

                if template_file.is_file():
                    return template_file.read_text(encoding="utf-8")
        except (ModuleNotFoundError, FileNotFoundError, AttributeError):
            pass

        return None
