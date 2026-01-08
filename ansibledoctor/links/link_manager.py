"""Link manager for creating and resolving documentation links.

Manages link creation, resolution, and formatting across different output formats.
"""

from pathlib import Path
from ansibledoctor.models.link import Link, LinkType


class LinkManager:
    """Manages link creation and resolution."""

    def __init__(self, base_path: Path):
        """Initialize link manager.

        Args:
            base_path: Base path for resolving relative links
        """
        self.base_path = Path(base_path).resolve()

    def create_link(
        self,
        source: Path,
        target: Path | str,
        text: str | None = None,
        link_type: LinkType | None = None,
    ) -> Link:
        """Create a link from source to target.

        Args:
            source: Source file containing the link
            target: Target file/URL for the link
            text: Link text (defaults to target)
            link_type: Type of link (auto-detected if None)

        Returns:
            Created Link object
        """
        source_file = Path(source).resolve()
        target_str = str(target) if isinstance(target, Path) else target

        # Auto-detect link type if not provided
        if link_type is None:
            link_type = self._infer_link_type(target_str)

        # Default text to target if not provided
        if text is None:
            if isinstance(target, Path):
                text = target.name
            else:
                text = target_str

        return Link(
            source_file=source_file,
            target=target_str,
            link_type=link_type,
            text=text,
            line_number=None,
        )

    def resolve_link(self, link: Link) -> Path:
        """Resolve a link to an absolute path.

        Args:
            link: Link to resolve

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If link cannot be resolved
        """
        # Remove anchor if present
        target = link.target.split("#")[0]

        # If already absolute, use as-is
        target_path = Path(target)
        if target_path.is_absolute():
            return target_path.resolve()

        # Resolve relative to base path
        resolved = (self.base_path / target_path).resolve()
        return resolved

    def extract_anchor(self, target: str) -> str | None:
        """Extract anchor from link target.

        Args:
            target: Link target (possibly with #anchor)

        Returns:
            Anchor name (without #), or None if no anchor
        """
        if "#" not in target:
            return None

        return target.split("#", 1)[1]

    def format_link(self, link: Link, output_format: str = "markdown") -> str:
        """Format link for specific output format.

        Args:
            link: Link to format
            output_format: Output format ('markdown', 'html', 'rst')

        Returns:
            Formatted link string
        """
        if output_format == "markdown":
            return self._format_markdown(link)
        elif output_format == "html":
            return self._format_html(link)
        elif output_format == "rst":
            return self._format_rst(link)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _format_markdown(self, link: Link) -> str:
        """Format link as Markdown.

        Args:
            link: Link to format

        Returns:
            Markdown formatted link: [text](url)
        """
        text = link.text or link.target
        return f"[{text}]({link.target})"

    def _format_html(self, link: Link) -> str:
        """Format link as HTML.

        Args:
            link: Link to format

        Returns:
            HTML formatted link: <a href="url">text</a>
        """
        text = link.text or link.target
        # Escape HTML special characters
        text_escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        target_escaped = link.target.replace("&", "&amp;").replace('"', "&quot;")
        return f'<a href="{target_escaped}">{text_escaped}</a>'

    def _format_rst(self, link: Link) -> str:
        """Format link as reStructuredText.

        Args:
            link: Link to format

        Returns:
            RST formatted link: `text <url>`_
        """
        text = link.text or link.target
        return f"`{text} <{link.target}>`_"

    def _infer_link_type(self, target: str) -> LinkType:
        """Infer link type from target.

        Args:
            target: Link target

        Returns:
            Inferred LinkType
        """
        if target.startswith(("http://", "https://")):
            return LinkType.EXTERNAL_URL
        elif "#" in target:
            return LinkType.INTERNAL_SECTION
        elif target.startswith("/"):
            return LinkType.ABSOLUTE_PATH
        else:
            return LinkType.RELATIVE_PATH
