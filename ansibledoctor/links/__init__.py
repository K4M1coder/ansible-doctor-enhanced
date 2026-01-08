"""
Link management and cross-reference module for ansible-doctor.

This module provides comprehensive link management capabilities:
- Link parsing from Markdown, HTML, and RST
- Link validation (internal and external)
- Cross-reference generation between related documentation
- Navigation building (table of contents, section links)
- External resource integration (Ansible docs, Galaxy)
- Link health monitoring and reporting

Spec: 013-links-cross-references
"""

from ansibledoctor.links.cross_reference_generator import CrossReferenceGenerator
from ansibledoctor.links.link_manager import LinkManager
from ansibledoctor.links.link_validator import LinkValidator, ValidationResult
from ansibledoctor.models.cross_reference import CrossReference

__all__ = [
    "CrossReferenceGenerator",
    "LinkManager",
    "LinkValidator",
    "ValidationResult",
    "CrossReference",
]
