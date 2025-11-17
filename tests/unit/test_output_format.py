"""Tests for OutputFormat enum."""
import pytest
from ansibledoctor.generator.output_format import OutputFormat


class TestOutputFormat:
    """Test suite for OutputFormat enum."""

    def test_output_format_values(self):
        """Test that all expected formats exist."""
        assert OutputFormat.MARKDOWN.value == "markdown"
        assert OutputFormat.HTML.value == "html"
        assert OutputFormat.RST.value == "rst"

    def test_output_format_from_string(self):
        """Test conversion from string to enum."""
        assert OutputFormat("markdown") == OutputFormat.MARKDOWN
        assert OutputFormat("html") == OutputFormat.HTML
        assert OutputFormat("rst") == OutputFormat.RST

    def test_output_format_case_insensitive(self):
        """Test case-insensitive lookup."""
        assert OutputFormat.from_string("MARKDOWN") == OutputFormat.MARKDOWN
        assert OutputFormat.from_string("Html") == OutputFormat.HTML
        assert OutputFormat.from_string("RsT") == OutputFormat.RST

    def test_output_format_invalid(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid output format"):
            OutputFormat.from_string("pdf")

    def test_output_format_file_extension(self):
        """Test getting file extension for each format."""
        assert OutputFormat.MARKDOWN.file_extension == ".md"
        assert OutputFormat.HTML.file_extension == ".html"
        assert OutputFormat.RST.file_extension == ".rst"

    def test_output_format_mime_type(self):
        """Test MIME type for each format."""
        assert OutputFormat.MARKDOWN.mime_type == "text/markdown"
        assert OutputFormat.HTML.mime_type == "text/html"
        assert OutputFormat.RST.mime_type == "text/x-rst"

    def test_output_format_is_markup(self):
        """Test markup format detection."""
        assert OutputFormat.MARKDOWN.is_markup is True
        assert OutputFormat.HTML.is_markup is True
        assert OutputFormat.RST.is_markup is True

    def test_output_format_all_formats(self):
        """Test getting all available formats."""
        formats = OutputFormat.all_formats()
        assert len(formats) == 3
        assert OutputFormat.MARKDOWN in formats
        assert OutputFormat.HTML in formats
        assert OutputFormat.RST in formats
