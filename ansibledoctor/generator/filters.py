"""Custom Jinja2 filters for template rendering."""
import re
from typing import Any

from markupsafe import escape


def markdown_escape(text: str) -> str:
    """Escape special Markdown characters.
    
    Escapes: \\ ` * _ { } [ ] ( ) # + - . !
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Markdown
        
    Example:
        >>> markdown_escape("Hello *world*")
        'Hello \\*world\\*'
    """
    if not text:
        return text
    
    special_chars = r"\`*_{}[]()#+-.!"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


def code_fence(code: str, language: str = "") -> str:
    """Wrap code in Markdown fenced code block.
    
    Args:
        code: Code to wrap
        language: Optional language identifier
        
    Returns:
        Markdown code fence (```language\\ncode\\n```)
        
    Example:
        >>> code_fence("print('hello')", "python")
        '```python\\nprint(\\'hello\\')\\n```'
    """
    if not code:
        return "```\n\n```"
    
    return f"```{language}\n{code}\n```"


def format_priority(priority: str) -> str:
    """Format TODO priority with emoji indicators.
    
    Args:
        priority: Priority level (low, medium, high, critical)
        
    Returns:
        Formatted priority string with emoji
        
    Example:
        >>> format_priority("high")
        '🔴 High'
        >>> format_priority("low")
        '🟢 Low'
    """
    if priority is None:
        return "⚪ Unknown"
    
    priority_map = {
        "low": "🟢 Low",
        "medium": "🟡 Medium",
        "high": "🔴 High",
        "critical": "🚨 Critical",
    }
    
    return priority_map.get(priority.lower(), f"⚪ {priority.capitalize()}")


def rst_escape(text: Any) -> str:
    """Escape special reStructuredText characters.
    
    Escapes: \\ * ` _ |
    
    Args:
        text: Text to escape (will be converted to string)
        
    Returns:
        Escaped text safe for RST
        
    Example:
        >>> rst_escape("Hello *world*")
        'Hello \\*world\\*'
    """
    if not text:
        return str(text) if text is not None else ""
    
    text = str(text)
    special_chars = r"\*`_|"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


def html_attrs(attrs: dict[str, Any]) -> str:
    """Convert dictionary to HTML attribute string.
    
    Args:
        attrs: Dictionary of attribute name-value pairs
        
    Returns:
        HTML attribute string (key="value" key2="value2")
        
    Example:
        >>> html_attrs({"class": "btn", "id": "submit"})
        'class="btn" id="submit"'
        >>> html_attrs({"disabled": True, "hidden": False})
        'disabled'
    """
    if not attrs:
        return ""
    
    parts = []
    for key, value in attrs.items():
        if value is True:
            parts.append(key)
        elif value is False or value is None:
            continue
        else:
            # Escape quotes in value
            escaped_value = str(value).replace('"', '&quot;')
            parts.append(f'{key}="{escaped_value}"')
    
    return " ".join(parts)


def list_items(items: list[Any], ordered: bool = False, start: int = 1) -> str:
    """Format list items as Markdown list.
    
    Args:
        items: List of items to format
        ordered: Use ordered list (1. 2. 3.) vs unordered (- - -)
        start: Starting number for ordered lists
        
    Returns:
        Markdown-formatted list
        
    Example:
        >>> list_items(["one", "two"], ordered=False)
        '- one\\n- two'
        >>> list_items(["first", "second"], ordered=True)
        '1. first\\n2. second'
    """
    if not items:
        return ""
    
    lines = []
    for i, item in enumerate(items, start=start if ordered else 0):
        if ordered:
            lines.append(f"{i}. {item}")
        else:
            lines.append(f"- {item}")
    
    return "\n".join(lines)


def html_escape(text: str) -> str:
    """Escape HTML entities to prevent XSS attacks.
    
    Uses markupsafe.escape to safely escape HTML special characters:
    < > & " '
    
    Args:
        text: Text to escape
        
    Returns:
        HTML-escaped text
        
    Example:
        >>> html_escape("<script>alert('XSS')</script>")
        '&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;'
    """
    if not text:
        return text
    
    return str(escape(text))


# Filter registry for Jinja2 environment
FILTERS = {
    "markdown_escape": markdown_escape,
    "code_fence": code_fence,
    "format_priority": format_priority,
    "rst_escape": rst_escape,
    "html_attrs": html_attrs,
    "html_escape": html_escape,
    "list_items": list_items,
}
