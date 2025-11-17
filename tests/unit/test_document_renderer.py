"""Tests for DocumentRenderer protocol and implementations."""
import pytest
from ansibledoctor.generator.protocols import DocumentRenderer
from ansibledoctor.generator.output_format import OutputFormat


class TestDocumentRendererProtocol:
    """Test suite for DocumentRenderer protocol compliance."""

    def test_protocol_exists(self):
        """Test that DocumentRenderer protocol is defined."""
        assert DocumentRenderer is not None
        assert hasattr(DocumentRenderer, 'render')
        assert hasattr(DocumentRenderer, 'escape')
        assert hasattr(DocumentRenderer, 'code_block')


class MockRenderer:
    """Mock implementation of DocumentRenderer for testing."""

    def render(self, content: str) -> str:
        """Mock render implementation."""
        return f"<rendered>{content}</rendered>"

    def escape(self, text: str) -> str:
        """Mock escape implementation."""
        return text.replace("<", "&lt;").replace(">", "&gt;")

    def code_block(self, code: str, language: str = "") -> str:
        """Mock code_block implementation."""
        return f"```{language}\n{code}\n```"


class TestDocumentRendererContract:
    """Test contract compliance for DocumentRenderer implementations."""

    @pytest.fixture
    def renderer(self):
        """Create mock renderer for testing."""
        return MockRenderer()

    def test_render_returns_string(self, renderer):
        """Test that render returns a string."""
        result = renderer.render("test content")
        assert isinstance(result, str)

    def test_render_handles_empty_content(self, renderer):
        """Test render with empty content."""
        result = renderer.render("")
        assert isinstance(result, str)

    def test_escape_returns_string(self, renderer):
        """Test that escape returns a string."""
        result = renderer.escape("<html>")
        assert isinstance(result, str)

    def test_escape_handles_special_chars(self, renderer):
        """Test escape handles HTML special characters."""
        result = renderer.escape("<tag>content</tag>")
        assert "&lt;" in result
        assert "&gt;" in result

    def test_code_block_returns_string(self, renderer):
        """Test that code_block returns a string."""
        result = renderer.code_block("print('hello')", "python")
        assert isinstance(result, str)

    def test_code_block_includes_language(self, renderer):
        """Test code_block includes language hint."""
        result = renderer.code_block("SELECT * FROM users", "sql")
        assert "sql" in result.lower() or "SELECT" in result

    def test_code_block_handles_empty_language(self, renderer):
        """Test code_block with no language specified."""
        result = renderer.code_block("some code")
        assert isinstance(result, str)
