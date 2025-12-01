"""Variant-aware template resolution.

Feature 008 - Template Customization & Theming
T337: VariantTemplateResolver implementation

Resolves template names based on variant (minimal, detailed, modern)
with fallback chain:
1. role.modern.html.j2  (exact variant)
2. role.html.j2         (format default)
3. role.default.html.j2 (explicit default)
4. role.j2              (generic fallback)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from ansibledoctor.generator.output_format import OutputFormat

if TYPE_CHECKING:
    from ansibledoctor.generator.cascading_loader import CascadingTemplateLoader

log = logging.getLogger(__name__)


class Variant(str, Enum):
    """Template variant styles.

    Controls the level of detail and visual style in generated documentation.

    Attributes:
        MINIMAL: Compact output with essential information only
        DETAILED: Full documentation with all sections (default)
        MODERN: Contemporary styling with enhanced visual elements
        DEFAULT: Explicit default variant marker
    """

    MINIMAL = "minimal"
    DETAILED = "detailed"
    MODERN = "modern"
    DEFAULT = "default"


@dataclass(frozen=True)
class ResolvedTemplate:
    """Result of template resolution with fallback information.

    Attributes:
        name: Full template name that was resolved (e.g., "role.modern.html.j2")
        base_name: Base template name (e.g., "role")
        variant: Resolved variant
        format: Output format
        is_fallback: True if this is a fallback template, not exact match
    """

    name: str
    base_name: str
    variant: Variant
    format: OutputFormat
    is_fallback: bool

    @property
    def candidates(self) -> list[str]:
        """Return list of template names in fallback order.

        Returns:
            Ordered list of template candidates that would be tried
        """
        fmt = self.format.value if hasattr(self.format, "value") else str(self.format)
        # Map format to extension
        ext_map = {"html": "html", "markdown": "md", "rst": "rst"}
        ext = ext_map.get(fmt, fmt)

        return [
            f"{self.base_name}.{self.variant.value}.{ext}.j2",
            f"{self.base_name}.{ext}.j2",
            f"{self.base_name}.default.{ext}.j2",
            f"{self.base_name}.j2",
        ]


class VariantTemplateResolver:
    """Resolves template names based on variant with fallback chain.

    Works in conjunction with CascadingTemplateLoader to find templates
    at the appropriate level with variant-specific or fallback templates.

    Example:
        >>> loader = CascadingTemplateLoader()
        >>> resolver = VariantTemplateResolver(loader)
        >>> result = resolver.resolve("role", OutputFormat.HTML, Variant.MODERN)
        >>> print(result.name)
        'role.modern.html.j2'  # or fallback if not found

    Feature: US25 - Template Variants
    Task: T337 - VariantTemplateResolver implementation
    """

    def __init__(self, loader: "CascadingTemplateLoader") -> None:
        """Initialize with a template loader.

        Args:
            loader: CascadingTemplateLoader instance for finding templates
        """
        self._loader = loader

    @property
    def default_variant(self) -> Variant:
        """Return the default variant.

        Returns:
            Variant.DETAILED as the default
        """
        return Variant.DETAILED

    def resolve(
        self,
        base_name: str,
        format: OutputFormat,
        variant: Variant | None = None,
        context_path: Path | None = None,
    ) -> ResolvedTemplate:
        """Resolve template with fallback chain.

        Tries template candidates in order until one is found:
        1. {base_name}.{variant}.{format}.j2 (exact variant)
        2. {base_name}.{format}.j2 (format default)
        3. {base_name}.default.{format}.j2 (explicit default)
        4. {base_name}.j2 (generic fallback)

        Args:
            base_name: Base template name (e.g., "role", "collection")
            format: Output format (html, markdown, rst)
            variant: Requested variant (defaults to DETAILED)
            context_path: Path for template discovery context

        Returns:
            ResolvedTemplate with the matched template information

        Raises:
            TemplateNotFoundError: If no template matches in fallback chain
        """
        from ansibledoctor.generator.cascading_loader import TemplateNotFoundError

        if variant is None:
            variant = self.default_variant

        candidates = self._build_candidates(base_name, format, variant)
        ctx_path = context_path or Path.cwd()

        for i, candidate in enumerate(candidates):
            try:
                self._loader.find_template(candidate, ctx_path)

                # Determine if this is a fallback
                is_fallback = i > 0

                # Determine the actual variant
                if candidate.startswith(f"{base_name}.{variant.value}"):
                    resolved_variant = variant
                else:
                    resolved_variant = Variant.DEFAULT

                log.debug(
                    "Template resolved",
                    extra={
                        "base_name": base_name,
                        "template": candidate,
                        "variant": resolved_variant.value,
                        "is_fallback": is_fallback,
                    },
                )

                return ResolvedTemplate(
                    name=candidate,
                    base_name=base_name,
                    variant=resolved_variant,
                    format=format,
                    is_fallback=is_fallback,
                )
            except TemplateNotFoundError:
                log.debug("Template not found, trying fallback", extra={"candidate": candidate})
                continue

        raise TemplateNotFoundError(
            f"No template found for {base_name} "
            f"(format={format.value if hasattr(format, 'value') else format}, "
            f"variant={variant.value})"
        )

    def _build_candidates(
        self,
        base_name: str,
        format: OutputFormat,
        variant: Variant,
    ) -> list[str]:
        """Build ordered list of template candidates.

        Args:
            base_name: Base template name
            format: Output format
            variant: Requested variant

        Returns:
            Ordered list of template names to try
        """
        # Get format extension
        fmt = format.value if hasattr(format, "value") else str(format)
        ext_map = {"html": "html", "markdown": "md", "rst": "rst"}
        ext = ext_map.get(fmt, fmt)

        return [
            # 1. Exact variant match
            f"{base_name}.{variant.value}.{ext}.j2",
            # 2. Format-specific default
            f"{base_name}.{ext}.j2",
            # 3. Explicit default variant
            f"{base_name}.default.{ext}.j2",
            # 4. Generic fallback
            f"{base_name}.j2",
        ]

    def list_variants(
        self,
        base_name: str,
        format: OutputFormat,
        context_path: Path | None = None,
    ) -> list[Variant]:
        """List available variants for a template.

        Checks which variant-specific templates exist for the given
        base name and format.

        Args:
            base_name: Base template name
            format: Output format
            context_path: Path for template discovery context

        Returns:
            List of variants that have templates available
        """
        from ansibledoctor.generator.cascading_loader import TemplateNotFoundError

        available: list[Variant] = []
        ctx_path = context_path or Path.cwd()

        # Get format extension
        fmt = format.value if hasattr(format, "value") else str(format)
        ext_map = {"html": "html", "markdown": "md", "rst": "rst"}
        ext = ext_map.get(fmt, fmt)

        for variant in Variant:
            template_name = f"{base_name}.{variant.value}.{ext}.j2"
            try:
                self._loader.find_template(template_name, ctx_path)
                available.append(variant)
            except TemplateNotFoundError:
                pass

        return available
