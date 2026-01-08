"""
Link parser utilities for extracting links from documentation.

Supports parsing links from:
- Markdown files ([text](url))
- HTML files (<a href="url">text</a>)
- RST files (`text <url>`_)

Spec: 013-links-cross-references
"""

import re
from pathlib import Path

from ansibledoctor.models.link import Link


class LinkParser:
    """Parse links from documentation files."""

    # Markdown link pattern: [text](url)
    MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")

    # Markdown reference link pattern: [text][ref]
    MARKDOWN_REF_PATTERN = re.compile(r"\[([^\]]+)\]\[([^\]]+)\]")

    # RST link pattern: `text <url>`_
    RST_LINK_PATTERN = re.compile(r"`([^`]+)<([^>]+)>`_")

    def __init__(self) -> None:
        """Initialize link parser."""
        self.links: list[Link] = []

    def parse_markdown(self, file_path: Path, content: str) -> list[Link]:
        """
        Parse links from Markdown content.

        Args:
            file_path: Path to the Markdown file
            content: File content as string

        Returns:
            List of Link objects found in content

        Examples:
            >>> parser = LinkParser()
            >>> content = "See [documentation](../docs/guide.md) for details."
            >>> links = parser.parse_markdown(Path("/project/README.md"), content)
            >>> len(links)
            1
            >>> links[0].text
            'documentation'
        """
        links: list[Link] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Find Markdown links: [text](url)
            for match in self.MARKDOWN_LINK_PATTERN.finditer(line):
                link = Link.from_markdown(
                    source=file_path.resolve(),
                    match=match,
                    line_number=line_num,
                )
                links.append(link)

        return links

    def parse_html(self, file_path: Path, content: str) -> list[Link]:
        """
        Parse links from HTML content using BeautifulSoup.

        Args:
            file_path: Path to the HTML file
            content: File content as string

        Returns:
            List of Link objects found in content
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # BeautifulSoup not available, return empty list
            return []

        links: list[Link] = []
        soup = BeautifulSoup(content, "html.parser")

        # Find all <a> tags with href
        for anchor in soup.find_all("a", href=True):
            # Estimate line number by counting newlines before tag
            tag_str = str(anchor)
            offset = content.find(tag_str)
            line_number = content[:offset].count("\n") + 1 if offset != -1 else None

            link = Link.from_html(
                source=file_path.resolve(),
                element=anchor,
                line_number=line_number,
            )
            links.append(link)

        return links

    def parse_rst(self, file_path: Path, content: str) -> list[Link]:
        """
        Parse links from reStructuredText content.

        Args:
            file_path: Path to the RST file
            content: File content as string

        Returns:
            List of Link objects found in content

        Examples:
            >>> parser = LinkParser()
            >>> content = "See `documentation <../docs/guide.rst>`_ for details."
            >>> links = parser.parse_rst(Path("/project/README.rst"), content)
            >>> len(links)
            1
        """
        links: list[Link] = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Find RST links: `text <url>`_
            for match in self.RST_LINK_PATTERN.finditer(line):
                text = match.group(1).strip()
                target = match.group(2).strip()
                link_type = Link._infer_link_type(target)

                link = Link(
                    source_file=file_path.resolve(),
                    target=target,
                    link_type=link_type,
                    text=text,
                    line_number=line_num,
                )
                links.append(link)

        return links

    def parse_file(self, file_path: Path) -> list[Link]:
        """
        Parse links from file based on extension.

        Args:
            file_path: Path to documentation file

        Returns:
            List of Link objects found in file

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file type is not supported
        """
        if not file_path.exists():
            msg = f"File not found: {file_path}"
            raise FileNotFoundError(msg)

        content = file_path.read_text(encoding="utf-8")
        suffix = file_path.suffix.lower()

        if suffix in {".md", ".markdown"}:
            return self.parse_markdown(file_path, content)
        if suffix in {".html", ".htm"}:
            return self.parse_html(file_path, content)
        if suffix in {".rst", ".rest"}:
            return self.parse_rst(file_path, content)

        msg = f"Unsupported file type: {suffix}"
        raise ValueError(msg)

    def parse_directory(self, directory: Path, extensions: set[str] | None = None) -> list[Link]:
        """
        Parse links from all documentation files in directory.

        Args:
            directory: Directory to scan for documentation
            extensions: Set of file extensions to parse (default: {'.md', '.html', '.rst'})

        Returns:
            List of all links found in directory
        """
        if extensions is None:
            extensions = {".md", ".markdown", ".html", ".htm", ".rst", ".rest"}

        all_links: list[Link] = []

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                try:
                    links = self.parse_file(file_path)
                    all_links.extend(links)
                except (FileNotFoundError, ValueError):
                    # Skip files that can't be parsed
                    continue

        return all_links
