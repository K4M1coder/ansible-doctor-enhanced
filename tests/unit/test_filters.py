"""Tests for custom Jinja2 filters."""
import pytest
from ansibledoctor.generator.filters import (
    FILTERS,
    code_fence,
    format_priority,
    html_attrs,
    list_items,
    markdown_escape,
    rst_escape,
)


class TestMarkdownEscape:
    """Tests for markdown_escape filter."""

    def test_escape_asterisk(self):
        """Test escaping asterisk."""
        assert markdown_escape("*bold*") == "\\*bold\\*"

    def test_escape_underscore(self):
        """Test escaping underscore."""
        assert markdown_escape("_italic_") == "\\_italic\\_"

    def test_escape_backtick(self):
        """Test escaping backtick."""
        assert markdown_escape("`code`") == "\\`code\\`"

    def test_escape_brackets(self):
        """Test escaping brackets."""
        assert markdown_escape("[link](url)") == "\\[link\\]\\(url\\)"

    def test_escape_hash(self):
        """Test escaping hash."""
        assert markdown_escape("# Heading") == "\\# Heading"

    def test_escape_backslash(self):
        """Test escaping backslash."""
        # Backslash is escaped but colon is not (colon not in special_chars)
        assert markdown_escape("path\\to\\file") == "path\\\\to\\\\file"
        result = markdown_escape("C:\\path")
        assert "\\\\" in result  # Backslash is escaped

    def test_escape_multiple_chars(self):
        """Test escaping multiple special characters."""
        text = "**bold** _italic_ `code`"
        result = markdown_escape(text)
        assert "\\*\\*bold\\*\\*" in result
        assert "\\_italic\\_" in result
        assert "\\`code\\`" in result

    def test_escape_empty_string(self):
        """Test with empty string."""
        assert markdown_escape("") == ""

    def test_escape_none(self):
        """Test with None."""
        assert markdown_escape(None) is None


class TestCodeFence:
    """Tests for code_fence filter."""

    def test_code_fence_with_language(self):
        """Test code fence with language."""
        code = "print('hello')"
        result = code_fence(code, "python")
        assert result == "```python\nprint('hello')\n```"

    def test_code_fence_without_language(self):
        """Test code fence without language."""
        code = "echo hello"
        result = code_fence(code)
        assert result == "```\necho hello\n```"

    def test_code_fence_multiline(self):
        """Test code fence with multiline code."""
        code = "def hello():\n    print('world')"
        result = code_fence(code, "python")
        assert "```python\n" in result
        assert "def hello():" in result
        assert "    print('world')" in result
        assert result.endswith("\n```")

    def test_code_fence_empty(self):
        """Test code fence with empty code."""
        result = code_fence("")
        assert result == "```\n\n```"

    def test_code_fence_preserves_whitespace(self):
        """Test that code fence preserves indentation."""
        code = "    indented\n  less indented"
        result = code_fence(code)
        assert "    indented" in result
        assert "  less indented" in result


class TestFormatPriority:
    """Tests for format_priority filter."""

    def test_format_priority_low(self):
        """Test low priority formatting."""
        assert format_priority("low") == "🟢 Low"

    def test_format_priority_medium(self):
        """Test medium priority formatting."""
        assert format_priority("medium") == "🟡 Medium"

    def test_format_priority_high(self):
        """Test high priority formatting."""
        assert format_priority("high") == "🔴 High"

    def test_format_priority_critical(self):
        """Test critical priority formatting."""
        assert format_priority("critical") == "🚨 Critical"

    def test_format_priority_case_insensitive(self):
        """Test priority formatting is case-insensitive."""
        assert format_priority("LOW") == "🟢 Low"
        assert format_priority("High") == "🔴 High"
        assert format_priority("CRITICAL") == "🚨 Critical"

    def test_format_priority_unknown(self):
        """Test unknown priority gets default format."""
        result = format_priority("unknown")
        assert result == "⚪ Unknown"

    def test_format_priority_custom(self):
        """Test custom priority value."""
        result = format_priority("urgent")
        assert result == "⚪ Urgent"


class TestRstEscape:
    """Tests for rst_escape filter."""

    def test_escape_asterisk(self):
        """Test escaping asterisk in RST."""
        assert rst_escape("*emphasis*") == "\\*emphasis\\*"

    def test_escape_underscore(self):
        """Test escaping underscore in RST."""
        assert rst_escape("_private") == "\\_private"

    def test_escape_backtick(self):
        """Test escaping backtick in RST."""
        assert rst_escape("`code`") == "\\`code\\`"

    def test_escape_pipe(self):
        """Test escaping pipe in RST."""
        assert rst_escape("col1|col2") == "col1\\|col2"

    def test_escape_backslash(self):
        """Test escaping backslash in RST."""
        # Colon is not a special RST character
        assert rst_escape("path\\to\\file") == "path\\\\to\\\\file"

    def test_escape_multiple(self):
        """Test escaping multiple special chars."""
        text = "*bold* `code` _var"
        result = rst_escape(text)
        assert "\\*bold\\*" in result
        assert "\\`code\\`" in result
        assert "\\_var" in result

    def test_escape_empty_string(self):
        """Test with empty string."""
        assert rst_escape("") == ""

    def test_escape_none(self):
        """Test with None."""
        assert rst_escape(None) == ""


class TestHtmlAttrs:
    """Tests for html_attrs filter."""

    def test_html_attrs_simple(self):
        """Test simple attribute conversion."""
        attrs = {"class": "btn", "id": "submit"}
        result = html_attrs(attrs)
        assert 'class="btn"' in result
        assert 'id="submit"' in result

    def test_html_attrs_boolean_true(self):
        """Test boolean True attribute."""
        attrs = {"disabled": True, "required": True}
        result = html_attrs(attrs)
        assert "disabled" in result
        assert "required" in result
        assert "=" not in result  # No value for boolean attrs

    def test_html_attrs_boolean_false(self):
        """Test boolean False attribute (excluded)."""
        attrs = {"disabled": False, "class": "btn"}
        result = html_attrs(attrs)
        assert "disabled" not in result
        assert 'class="btn"' in result

    def test_html_attrs_none_value(self):
        """Test None value (excluded)."""
        attrs = {"title": None, "id": "test"}
        result = html_attrs(attrs)
        assert "title" not in result
        assert 'id="test"' in result

    def test_html_attrs_quote_escaping(self):
        """Test quote escaping in attribute values."""
        attrs = {"title": 'Hello "world"'}
        result = html_attrs(attrs)
        assert 'title="Hello &quot;world&quot;"' in result

    def test_html_attrs_empty(self):
        """Test empty attributes dict."""
        assert html_attrs({}) == ""

    def test_html_attrs_none(self):
        """Test None attributes."""
        assert html_attrs(None) == ""

    def test_html_attrs_numeric_value(self):
        """Test numeric attribute values."""
        attrs = {"width": 100, "height": 50}
        result = html_attrs(attrs)
        assert 'width="100"' in result
        assert 'height="50"' in result


class TestListItems:
    """Tests for list_items filter."""

    def test_list_items_unordered(self):
        """Test unordered list formatting."""
        items = ["one", "two", "three"]
        result = list_items(items)
        assert result == "- one\n- two\n- three"

    def test_list_items_ordered(self):
        """Test ordered list formatting."""
        items = ["first", "second", "third"]
        result = list_items(items, ordered=True)
        assert result == "1. first\n2. second\n3. third"

    def test_list_items_ordered_custom_start(self):
        """Test ordered list with custom start number."""
        items = ["a", "b"]
        result = list_items(items, ordered=True, start=5)
        assert result == "5. a\n6. b"

    def test_list_items_single_item(self):
        """Test list with single item."""
        items = ["only"]
        result = list_items(items)
        assert result == "- only"

    def test_list_items_empty(self):
        """Test empty list."""
        assert list_items([]) == ""

    def test_list_items_none(self):
        """Test None list."""
        assert list_items(None) == ""

    def test_list_items_preserves_content(self):
        """Test that list items preserve their content."""
        items = ["**bold**", "_italic_", "`code`"]
        result = list_items(items)
        assert "- **bold**" in result
        assert "- _italic_" in result
        assert "- `code`" in result


class TestFiltersRegistry:
    """Tests for FILTERS registry."""

    def test_filters_registry_contains_all(self):
        """Test that FILTERS contains all expected filters."""
        expected_filters = [
            "markdown_escape",
            "code_fence",
            "format_priority",
            "rst_escape",
            "html_attrs",
            "list_items",
        ]
        
        for filter_name in expected_filters:
            assert filter_name in FILTERS

    def test_filters_registry_callable(self):
        """Test that all filters in registry are callable."""
        for filter_name, filter_func in FILTERS.items():
            assert callable(filter_func)

    def test_filters_registry_matches_functions(self):
        """Test that registry functions match imported functions."""
        assert FILTERS["markdown_escape"] is markdown_escape
        assert FILTERS["code_fence"] is code_fence
        assert FILTERS["format_priority"] is format_priority
        assert FILTERS["rst_escape"] is rst_escape
        assert FILTERS["html_attrs"] is html_attrs
        assert FILTERS["list_items"] is list_items
