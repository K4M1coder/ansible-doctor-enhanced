"""Renderer implementations for different output formats."""
import re
from ansibledoctor.generator.protocols import DocumentRenderer


class MarkdownRenderer:
    """Renderer for GitHub Flavored Markdown (GFM) format.
    
    Implements the DocumentRenderer protocol to generate Markdown-formatted
    documentation. Follows GFM specification for compatibility with GitHub,
    GitLab, and other Markdown processors.
    
    Example:
        >>> renderer = MarkdownRenderer()
        >>> renderer.heading("My Role", level=1)
        '# My Role'
        >>> renderer.code_block("print('hello')", "python")
        '```python\\nprint(\\'hello\\')\\n```'
    """

    def render(self, content: str) -> str:
        """Render content in Markdown format.
        
        For Markdown, rendering simply returns content as-is since Markdown
        is already a text format that doesn't require transformation.
        
        Args:
            content: Raw Markdown content to render
            
        Returns:
            Content unchanged
        """
        return content

    def escape(self, text: str) -> str:
        """Escape special Markdown characters.
        
        Escapes characters that have special meaning in Markdown:
        - Backslash (\\)
        - Backtick (`)
        - Asterisk (*)
        - Underscore (_)
        - Brackets ([ ])
        - Braces ({ })
        - Parentheses (( ))
        - Hash (#)
        - Plus (+)
        - Minus (-)
        - Dot after number (.)
        - Exclamation mark (!)
        
        Args:
            text: Text potentially containing special characters
            
        Returns:
            Text with special characters escaped using backslash
            
        Example:
            >>> renderer.escape("Text with [link]")
            'Text with \\\\[link\\\\]'
        """
        if not text:
            return text
        
        # Characters that need escaping in Markdown
        special_chars = r'\`*_{}[]()#+-.!'
        
        # Escape each special character with backslash
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        
        return text

    def code_block(self, code: str, language: str = "") -> str:
        """Format code block with optional syntax highlighting.
        
        Uses GitHub Flavored Markdown fenced code blocks with triple backticks.
        
        Args:
            code: Source code to format
            language: Programming language for syntax highlighting (e.g., 'python', 'yaml')
            
        Returns:
            Formatted code block with language hint
            
        Example:
            >>> renderer.code_block("x = 42", "python")
            '```python\\nx = 42\\n```'
        """
        return f"```{language}\n{code}\n```"

    def heading(self, text: str, level: int = 1) -> str:
        """Generate Markdown heading.
        
        Args:
            text: Heading text
            level: Heading level (1-6, where 1 is h1)
            
        Returns:
            Markdown heading with appropriate number of # symbols
            
        Raises:
            ValueError: If level is not between 1 and 6
            
        Example:
            >>> renderer.heading("Title", level=1)
            '# Title'
            >>> renderer.heading("Subtitle", level=2)
            '## Subtitle'
        """
        if not 1 <= level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {level}")
        
        return f"{'#' * level} {text}"

    def list_item(self, text: str, ordered: bool = False, number: int = 1) -> str:
        """Generate list item (ordered or unordered).
        
        Args:
            text: Item text
            ordered: If True, create numbered list item; if False, bullet point
            number: Number for ordered list items (ignored for unordered)
            
        Returns:
            Formatted list item
            
        Example:
            >>> renderer.list_item("First item")
            '- First item'
            >>> renderer.list_item("First item", ordered=True, number=1)
            '1. First item'
        """
        if ordered:
            return f"{number}. {text}"
        return f"- {text}"

    def link(self, text: str, url: str, title: str = "") -> str:
        """Generate Markdown link.
        
        Args:
            text: Link text (visible to user)
            url: Link URL
            title: Optional title attribute (shown on hover)
            
        Returns:
            Markdown link in format [text](url) or [text](url "title")
            
        Example:
            >>> renderer.link("GitHub", "https://github.com")
            '[GitHub](https://github.com)'
            >>> renderer.link("GitHub", "https://github.com", "Visit GitHub")
            '[GitHub](https://github.com "Visit GitHub")'
        """
        if title:
            return f'[{text}]({url} "{title}")'
        return f"[{text}]({url})"

    def bold(self, text: str) -> str:
        """Format text as bold.
        
        Args:
            text: Text to make bold
            
        Returns:
            Bold text wrapped in **
            
        Example:
            >>> renderer.bold("Important")
            '**Important**'
        """
        return f"**{text}**"

    def italic(self, text: str) -> str:
        """Format text as italic.
        
        Args:
            text: Text to make italic
            
        Returns:
            Italic text wrapped in *
            
        Example:
            >>> renderer.italic("Emphasized")
            '*Emphasized*'
        """
        return f"*{text}*"

    def inline_code(self, text: str) -> str:
        """Format text as inline code.
        
        Args:
            text: Text to format as code
            
        Returns:
            Inline code wrapped in backticks
            
        Example:
            >>> renderer.inline_code("variable_name")
            '`variable_name`'
        """
        # If text contains backticks, use double backticks
        if "`" in text:
            return f"`` {text} ``"
        return f"`{text}`"
