"""
Navigation builder for generating table of contents and section navigation.

Provides functionality to:
- Parse document headings
- Generate table of contents with anchor links
- Support nested hierarchical structure
- Output in multiple formats (Markdown, HTML)

Spec: 013-links-cross-references, User Story 3
"""

import re
from typing import Any

from ansibledoctor.utils.slug import slugify


class NavigationBuilder:
    """Build navigation elements for documentation."""

    # Markdown heading pattern: # Heading
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)$", re.MULTILINE)

    # Code block pattern to exclude headings in code
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```", re.MULTILINE)

    def __init__(self) -> None:
        """Initialize the NavigationBuilder."""
        self._heading_counts: dict[str, int] = {}

    def build_toc(
        self,
        content: str,
        format: str = "markdown",
        max_depth: int = 6,
        include_top_level: bool = False,
        mobile_friendly: bool = False,
    ) -> str:
        """
        Build a table of contents from document content.

        Args:
            content: Document content to parse
            format: Output format ("markdown" or "html")
            max_depth: Maximum heading level to include (1-6)
            include_top_level: Include h1 headings in TOC
            mobile_friendly: Add mobile-responsive features for HTML

        Returns:
            Generated table of contents as string

        Examples:
            >>> builder = NavigationBuilder()
            >>> content = "# Title\\n## Section 1\\n## Section 2"
            >>> toc = builder.build_toc(content)
            >>> "Section 1" in toc
            True
        """
        if not content or not content.strip():
            return ""

        # Reset heading counts for duplicate handling
        self._heading_counts = {}

        # Remove code blocks to avoid parsing headings in code
        content_without_code = self.CODE_BLOCK_PATTERN.sub("", content)

        # Extract headings
        headings = self._extract_headings(content_without_code)

        if not headings:
            return ""

        # Filter by depth and top level
        min_level = 1 if include_top_level else 2
        filtered_headings = [h for h in headings if min_level <= h["level"] <= max_depth]

        if not filtered_headings:
            return ""

        # Generate TOC based on format
        if format == "html":
            return self._generate_html_toc(filtered_headings, mobile_friendly)
        else:
            return self._generate_markdown_toc(filtered_headings)

    def _extract_headings(self, content: str) -> list[dict[str, Any]]:
        """
        Extract headings from content.

        Args:
            content: Document content

        Returns:
            List of heading dictionaries with level, text, and anchor
        """
        headings = []
        for match in self.HEADING_PATTERN.finditer(content):
            hashes = match.group(1)
            text = match.group(2).strip()

            # Remove inline code markers but keep the text
            text_clean = re.sub(r"`([^`]+)`", r"\1", text)

            level = len(hashes)
            anchor = self._generate_anchor(text_clean)

            headings.append({"level": level, "text": text_clean, "anchor": anchor})

        return headings

    def _generate_anchor(self, text: str) -> str:
        """
        Generate URL-safe anchor from heading text.

        Handles:
        - Lowercase conversion
        - Special character removal
        - Space to hyphen conversion
        - Duplicate heading names

        Args:
            text: Heading text

        Returns:
            URL-safe anchor string
        """
        # Use slugify utility
        base_anchor = slugify(text)

        # Handle duplicates
        if base_anchor in self._heading_counts:
            self._heading_counts[base_anchor] += 1
            return f"{base_anchor}-{self._heading_counts[base_anchor]}"
        else:
            self._heading_counts[base_anchor] = 0
            return base_anchor

    def _generate_markdown_toc(self, headings: list[dict[str, Any]]) -> str:
        """
        Generate Markdown format table of contents.

        Args:
            headings: List of heading dictionaries

        Returns:
            Markdown formatted TOC
        """
        if not headings:
            return ""

        lines = []
        base_level = min(h["level"] for h in headings)

        for heading in headings:
            # Calculate indentation (2 spaces per level)
            indent_level = heading["level"] - base_level
            indent = "  " * indent_level

            # Create link
            link = f"[{heading['text']}](#{heading['anchor']})"
            lines.append(f"{indent}- {link}")

        return "\n".join(lines)

    def _generate_html_toc(
        self, headings: list[dict[str, Any]], mobile_friendly: bool = False
    ) -> str:
        """
        Generate HTML format table of contents.

        Args:
            headings: List of heading dictionaries
            mobile_friendly: Add mobile-responsive features

        Returns:
            HTML formatted TOC
        """
        if not headings:
            return ""

        # Start with nav wrapper
        nav_class = "toc-nav mobile-friendly" if mobile_friendly else "toc-nav"
        html_parts = [f'<nav class="{nav_class}">']

        if mobile_friendly:
            # Add collapsible structure for mobile
            html_parts.append('  <details class="toc-details">')
            html_parts.append('    <summary class="toc-summary">Table of Contents</summary>')

        # Build nested list structure
        html_parts.append(self._build_nested_html_list(headings))

        if mobile_friendly:
            html_parts.append("  </details>")

        html_parts.append("</nav>")

        return "\n".join(html_parts)

    def _build_nested_html_list(self, headings: list[dict[str, Any]]) -> str:
        """
        Build nested HTML list structure with proper nesting.

        Creates structure like:
        <ul>
          <li>Parent
            <ul>
              <li>Child
                <ul>
                  <li>Grandchild</li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>

        Args:
            headings: List of heading dictionaries

        Returns:
            Nested HTML ul/li structure
        """
        if not headings:
            return ""

        html_parts = []
        stack: list[int] = []  # Stack of heading levels currently open
        base_indent = 1

        for i, heading in enumerate(headings):
            level = heading["level"]
            next_heading = headings[i + 1] if i + 1 < len(headings) else None
            next_level = next_heading["level"] if next_heading else 0

            # Close lists for items at same or shallower level
            while stack and stack[-1] >= level:
                # Close the nested ul that was opened for children
                indent = base_indent + len(stack)
                html_parts.append("  " * indent + "</ul>")
                html_parts.append("  " * (indent - 1) + "</li>")
                stack.pop()

            # Open new list level if needed (first item)
            if not stack:
                html_parts.append("  " * base_indent + "<ul>")

            # Add the list item
            indent = base_indent + len(stack)
            link = f'<a href="#{heading["anchor"]}">{heading["text"]}</a>'

            # Check if this item has children (next level is deeper)
            if next_level and next_level > level:
                # Open item but don't close it - children will be nested inside
                html_parts.append("  " * indent + f"  <li>{link}")
                # Open a nested <ul> for children
                html_parts.append("  " * (indent + 1) + "<ul>")
                # Track this level in the stack
                stack.append(level)
            else:
                # Leaf node - close it immediately
                html_parts.append("  " * indent + f"  <li>{link}</li>")

        # Close all remaining open lists
        while stack:
            indent = base_indent + len(stack)
            html_parts.append("  " * indent + "</ul>")
            html_parts.append("  " * (indent - 1) + "</li>")
            stack.pop()

        # Close the root <ul>
        html_parts.append("  " * base_indent + "</ul>")

        return "\n".join(html_parts)

    def generate_heading_anchors(self, content: str) -> dict[str, str]:
        """
        Generate mapping of heading text to anchors.

        Useful for validating anchor targets exist.

        Args:
            content: Document content

        Returns:
            Dictionary mapping heading text to anchor IDs
        """
        self._heading_counts = {}
        content_without_code = self.CODE_BLOCK_PATTERN.sub("", content)
        headings = self._extract_headings(content_without_code)

        return {h["text"]: h["anchor"] for h in headings}
