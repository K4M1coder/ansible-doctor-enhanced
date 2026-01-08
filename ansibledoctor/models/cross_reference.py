"""
Cross-reference model for bidirectional link tracking.

Provides data model for cross-references between components with validation status.
This model is shared between Spec 013 (Links) and Spec 011 (Indexes).

Spec: 013-links-cross-references (T028)
Consumed by: Spec 011 (Indexes & Navigation)
"""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


class CrossReference(BaseModel):
    """Cross-reference link between components with validation status.
    
    Represents a bidirectional relationship between components (roles, collections, plugins)
    with validation tracking. Used by both link generation and index navigation features.
    
    Attributes:
        source_path: Path to source component documentation
        source_name: Name of source component
        target_name: Name of target component  
        target_type: Type of target (role, collection, plugin, etc.)
        link_type: Type of relationship between components
        resolved_path: Resolved path to target documentation (after validation)
        is_valid: Whether link has been validated and target exists
        validation_error: Error message if validation failed
        metadata: Additional metadata about the cross-reference
    
    Examples:
        >>> ref = CrossReference(
        ...     source_path=Path("/roles/web/README.md"),
        ...     source_name="web",
        ...     target_name="common",
        ...     target_type="role",
        ...     link_type="dependency"
        ... )
        >>> ref.is_valid
        False
        >>> ref.validation_error
        None
    """
    
    source_path: Path = Field(
        description="Path to source component documentation"
    )
    source_name: str = Field(
        description="Name of source component"
    )
    target_name: str = Field(
        description="Name of target component"
    )
    target_type: str = Field(
        description="Type of target component (role, collection, plugin, etc.)"
    )
    link_type: Literal["dependency", "used_by", "related", "parent", "child"] = Field(
        description="Type of relationship"
    )
    resolved_path: Path | None = Field(
        default=None,
        description="Resolved path to target documentation (set by validator)"
    )
    is_valid: bool = Field(
        default=False,
        description="Whether link has been validated and target exists"
    )
    validation_error: str | None = Field(
        default=None,
        description="Error message if validation failed"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the cross-reference"
    )
    
    @property
    def link_text(self) -> str:
        """Generate Markdown link text.
        
        Returns:
            Markdown link if valid, plain text with warning if broken
            
        Examples:
            >>> ref = CrossReference(
            ...     source_path=Path("/roles/web/README.md"),
            ...     source_name="web",
            ...     target_name="common",
            ...     target_type="role",
            ...     link_type="dependency",
            ...     is_valid=True,
            ...     resolved_path=Path("/roles/common/README.md")
            ... )
            >>> ref.link_text
            '[common](/roles/common/README.md)'
        """
        if self.is_valid and self.resolved_path:
            return f"[{self.target_name}]({self.resolved_path})"
        return f"{self.target_name} (broken link)"
    
    @property
    def relative_link(self) -> str:
        """Generate relative link from source to target.
        
        Calculates the relative path from source documentation to target documentation.
        Returns "#" if path cannot be resolved.
        
        Returns:
            Relative path string or "#" if unresolved
            
        Examples:
            >>> ref = CrossReference(
            ...     source_path=Path("/docs/roles/web/README.md"),
            ...     source_name="web",
            ...     target_name="common",
            ...     target_type="role",
            ...     link_type="dependency",
            ...     resolved_path=Path("/docs/roles/common/README.md")
            ... )
            >>> ref.relative_link
            '../common/README.md'
        """
        if not self.resolved_path:
            return "#"
        
        try:
            # Calculate relative path from source directory to target
            source_dir = self.source_path.parent
            relative = self.resolved_path.relative_to(source_dir.parent)
            return f"../{relative}"
        except ValueError:
            # Paths don't share common base, use absolute
            return str(self.resolved_path)
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if this cross-reference has a reciprocal relationship.
        
        Returns:
            True if link type implies bidirectional relationship
        """
        return self.link_type in ("dependency", "parent", "child")
    
    def get_inverse_link_type(self) -> str:
        """Get the inverse link type for bidirectional relationships.
        
        Returns:
            Inverse link type string
            
        Examples:
            >>> ref = CrossReference(
            ...     source_path=Path("/roles/web/README.md"),
            ...     source_name="web",
            ...     target_name="common",
            ...     target_type="role",
            ...     link_type="dependency"
            ... )
            >>> ref.get_inverse_link_type()
            'used_by'
        """
        inverse_map = {
            "dependency": "used_by",
            "used_by": "dependency",
            "parent": "child",
            "child": "parent",
            "related": "related",
        }
        return inverse_map.get(self.link_type, "related")
    
    def create_inverse(self) -> "CrossReference":
        """Create the inverse cross-reference for bidirectional tracking.
        
        Returns:
            New CrossReference representing the inverse relationship
            
        Examples:
            >>> ref = CrossReference(
            ...     source_path=Path("/roles/web/README.md"),
            ...     source_name="web",
            ...     target_name="common",
            ...     target_type="role",
            ...     link_type="dependency"
            ... )
            >>> inverse = ref.create_inverse()
            >>> inverse.source_name
            'common'
            >>> inverse.target_name
            'web'
            >>> inverse.link_type
            'used_by'
        """
        inverse_path = self.resolved_path or Path(f"/{self.target_type}s/{self.target_name}/README.md")
        
        return CrossReference(
            source_path=inverse_path,
            source_name=self.target_name,
            target_name=self.source_name,
            target_type=self.source_path.parent.parent.name.rstrip('s'),  # Crude but works for roles/collections
            link_type=self.get_inverse_link_type(),
            resolved_path=self.source_path,
            is_valid=self.is_valid,
            validation_error=self.validation_error,
            metadata={
                "inverse_of": f"{self.source_name}→{self.target_name}",
                **self.metadata
            }
        )
