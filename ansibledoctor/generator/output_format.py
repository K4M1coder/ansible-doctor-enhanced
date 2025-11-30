"""Output format enumeration for documentation generation."""

from enum import Enum
from typing import List


class OutputFormat(Enum):
    """Supported output formats for documentation generation.

    Each format has associated metadata for file handling and MIME types.

    Attributes:
        MARKDOWN: GitHub Flavored Markdown format (.md)
        HTML: HTML5 semantic format (.html)
        RST: reStructuredText format for Sphinx (.rst)
    """

    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"

    @property
    def file_extension(self) -> str:
        """Get the file extension for this format.

        Returns:
            File extension with leading dot (e.g., '.md')
        """
        extensions = {
            OutputFormat.MARKDOWN: ".md",
            OutputFormat.HTML: ".html",
            OutputFormat.RST: ".rst",
        }
        return extensions[self]

    @property
    def mime_type(self) -> str:
        """Get the MIME type for this format.

        Returns:
            MIME type string (e.g., 'text/markdown')
        """
        mime_types = {
            OutputFormat.MARKDOWN: "text/markdown",
            OutputFormat.HTML: "text/html",
            OutputFormat.RST: "text/x-rst",
        }
        return mime_types[self]

    @property
    def is_markup(self) -> bool:
        """Check if this format is a markup language.

        Returns:
            True for all current formats (all are markup)
        """
        return True

    @classmethod
    def from_string(cls, format_str: str) -> "OutputFormat":
        """Convert string to OutputFormat enum (case-insensitive).

        Args:
            format_str: Format name as string

        Returns:
            OutputFormat enum member

        Raises:
            ValueError: If format_str is not a valid format

        Example:
            >>> OutputFormat.from_string("markdown")
            <OutputFormat.MARKDOWN: 'markdown'>
            >>> OutputFormat.from_string("HTML")
            <OutputFormat.HTML: 'html'>
        """
        format_lower = format_str.lower()
        for member in cls:
            if member.value == format_lower:
                return member

        valid_formats = [m.value for m in cls]
        raise ValueError(
            f"Invalid output format: '{format_str}'. "
            f"Valid formats are: {', '.join(valid_formats)}"
        )

    @classmethod
    def all_formats(cls) -> List["OutputFormat"]:
        """Get list of all available formats.

        Returns:
            List of all OutputFormat enum members

        Example:
            >>> OutputFormat.all_formats()
            [<OutputFormat.MARKDOWN: 'markdown'>, ...]
        """
        return list(cls)
