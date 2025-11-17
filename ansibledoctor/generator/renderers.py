"""Renderer implementations for different output formats."""
import html
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


class HtmlRenderer:
    """Renderer for HTML5 semantic format.
    
    Implements the DocumentRenderer protocol to generate HTML5-formatted
    documentation with proper semantic markup and HTML entity escaping.
    
    Example:
        >>> renderer = HtmlRenderer()
        >>> renderer.heading("My Role", level=1)
        '<h1>My Role</h1>'
        >>> renderer.code_block("print('hello')", "python")
        '<pre><code class="language-python">print(&#x27;hello&#x27;)</code></pre>'
    """

    def render(self, content: str) -> str:
        """Render content in HTML format.
        
        For HTML, rendering simply returns content as-is since HTML
        is already markup that doesn't require transformation.
        
        Args:
            content: Raw HTML content to render
            
        Returns:
            Content unchanged
        """
        return content

    def escape(self, text: str) -> str:
        """Escape special HTML characters.
        
        Escapes characters that have special meaning in HTML:
        - < (less than) → &lt;
        - > (greater than) → &gt;
        - & (ampersand) → &amp;
        - " (double quote) → &quot;
        - ' (single quote) → &#x27;
        
        Args:
            text: Text potentially containing special HTML characters
            
        Returns:
            Text with special characters escaped as HTML entities
            
        Example:
            >>> renderer.escape("<tag>content & \"quotes\"")
            '&lt;tag&gt;content &amp; &quot;quotes&quot;'
        """
        if not text:
            return text
        
        # Use html.escape for standard entities
        return html.escape(text, quote=True)

    def code_block(self, code: str, language: str = "") -> str:
        """Format code block with optional syntax highlighting class.
        
        Uses HTML5 semantic markup with <pre><code> elements.
        Adds language class for syntax highlighting integration.
        
        Args:
            code: Source code to format
            language: Programming language for syntax highlighting (e.g., 'python', 'yaml')
            
        Returns:
            Formatted code block with proper HTML escaping
            
        Example:
            >>> renderer.code_block("x = 42", "python")
            '<pre><code class="language-python">x = 42</code></pre>'
        """
        escaped_code = self.escape(code)
        if language:
            return f'<pre><code class="language-{language}">{escaped_code}</code></pre>'
        return f"<pre><code>{escaped_code}</code></pre>"

    def heading(self, text: str, level: int = 1) -> str:
        """Generate HTML heading.
        
        Args:
            text: Heading text (will be HTML-escaped)
            level: Heading level (1-6, where 1 is h1)
            
        Returns:
            HTML heading element
            
        Raises:
            ValueError: If level is not between 1 and 6
            
        Example:
            >>> renderer.heading("Title", level=1)
            '<h1>Title</h1>'
            >>> renderer.heading("Subtitle", level=2)
            '<h2>Subtitle</h2>'
        """
        if not 1 <= level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {level}")
        
        escaped_text = self.escape(text)
        return f"<h{level}>{escaped_text}</h{level}>"

    def list_item(self, text: str, ordered: bool = False, number: int = 1) -> str:
        """Generate list item.
        
        Note: In HTML, list items are the same for ordered and unordered lists.
        The <ol> or <ul> parent element determines the style.
        
        Args:
            text: Item text (will be HTML-escaped)
            ordered: Ignored (list type determined by parent element)
            number: Ignored (numbering handled by <ol> element)
            
        Returns:
            HTML list item element
            
        Example:
            >>> renderer.list_item("First item")
            '<li>First item</li>'
        """
        escaped_text = self.escape(text)
        return f"<li>{escaped_text}</li>"

    def link(self, text: str, url: str, title: str = "") -> str:
        """Generate HTML hyperlink.
        
        Args:
            text: Link text (visible to user, will be HTML-escaped)
            url: Link URL (will be HTML-escaped)
            title: Optional title attribute (shown on hover)
            
        Returns:
            HTML anchor element
            
        Example:
            >>> renderer.link("GitHub", "https://github.com")
            '<a href="https://github.com">GitHub</a>'
            >>> renderer.link("GitHub", "https://github.com", "Visit GitHub")
            '<a href="https://github.com" title="Visit GitHub">GitHub</a>'
        """
        escaped_text = self.escape(text)
        escaped_url = self.escape(url)
        
        if title:
            escaped_title = self.escape(title)
            return f'<a href="{escaped_url}" title="{escaped_title}">{escaped_text}</a>'
        return f'<a href="{escaped_url}">{escaped_text}</a>'

    def bold(self, text: str) -> str:
        """Format text as bold.
        
        Uses <strong> for semantic bold text.
        
        Args:
            text: Text to make bold (will be HTML-escaped)
            
        Returns:
            Bold text wrapped in <strong> element
            
        Example:
            >>> renderer.bold("Important")
            '<strong>Important</strong>'
        """
        escaped_text = self.escape(text)
        return f"<strong>{escaped_text}</strong>"

    def italic(self, text: str) -> str:
        """Format text as italic.
        
        Uses <em> for semantic emphasis.
        
        Args:
            text: Text to make italic (will be HTML-escaped)
            
        Returns:
            Italic text wrapped in <em> element
            
        Example:
            >>> renderer.italic("Emphasized")
            '<em>Emphasized</em>'
        """
        escaped_text = self.escape(text)
        return f"<em>{escaped_text}</em>"

    def inline_code(self, text: str) -> str:
        """Format text as inline code.
        
        Args:
            text: Text to format as code (will be HTML-escaped)
            
        Returns:
            Inline code wrapped in <code> element
            
        Example:
            >>> renderer.inline_code("variable_name")
            '<code>variable_name</code>'
        """
        escaped_text = self.escape(text)
        return f"<code>{escaped_text}</code>"

    def paragraph(self, text: str) -> str:
        """Format text as paragraph.
        
        Args:
            text: Paragraph text (will be HTML-escaped)
            
        Returns:
            Text wrapped in <p> element
            
        Example:
            >>> renderer.paragraph("This is a paragraph.")
            '<p>This is a paragraph.</p>'
        """
        escaped_text = self.escape(text)
        return f"<p>{escaped_text}</p>"


class RstRenderer:
    """Renderer for reStructuredText (RST) format.
    
    Implements the DocumentRenderer protocol to generate RST-formatted
    documentation compatible with Sphinx and other RST processors.
    
    Example:
        >>> renderer = RstRenderer()
        >>> renderer.heading("My Role", level=1)
        'My Role\\n======='
        >>> renderer.code_block("print('hello')", "python")
        '.. code-block:: python\\n\\n    print(\\'hello\\')'
    """

    # RST heading characters by level
    HEADING_CHARS = {
        1: "=",  # Title (overline and underline)
        2: "-",  # Subtitle
        3: "~",  # Section
        4: "^",  # Subsection
        5: "\"", # Subsubsection
        6: "#",  # Paragraph
    }

    def render(self, content: str) -> str:
        """Render content in RST format.
        
        For RST, rendering simply returns content as-is since RST
        is already a text format that doesn't require transformation.
        
        Args:
            content: Raw RST content to render
            
        Returns:
            Content unchanged
        """
        return content

    def escape(self, text: str) -> str:
        """Escape special RST characters.
        
        Escapes characters that have special meaning in RST:
        - Backslash (\\)
        - Asterisk (*)
        - Backtick (`)
        - Underscore (_) at end of word
        - Vertical bar (|)
        
        Args:
            text: Text potentially containing special characters
            
        Returns:
            Text with special characters escaped using backslash
            
        Example:
            >>> renderer.escape("Text with *asterisks*")
            'Text with \\\\*asterisks\\\\*'
        """
        if not text:
            return text
        
        # Escape backslashes first
        text = text.replace("\\", "\\\\")
        
        # Escape other special RST characters
        special_chars = "*`_|"
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        
        return text

    def code_block(self, code: str, language: str = "") -> str:
        """Format code block with optional syntax highlighting.
        
        Uses RST code-block directive or literal block (::).
        
        Args:
            code: Source code to format
            language: Programming language for syntax highlighting
            
        Returns:
            Formatted RST code block
            
        Example:
            >>> renderer.code_block("x = 42", "python")
            '.. code-block:: python\\n\\n    x = 42'
        """
        if language:
            # Use code-block directive with language
            indented_code = "\n".join(f"    {line}" if line else "" for line in code.split("\n"))
            return f".. code-block:: {language}\n\n{indented_code}"
        else:
            # Use literal block (::)
            indented_code = "\n".join(f"    {line}" if line else "" for line in code.split("\n"))
            return f"::\n\n{indented_code}"

    def heading(self, text: str, level: int = 1) -> str:
        """Generate RST heading with underline.
        
        RST headings use underlines (and sometimes overlines) with specific characters:
        - Level 1: ======= (equals)
        - Level 2: ------- (hyphens)
        - Level 3: ~~~~~~~ (tildes)
        - Level 4: ^^^^^^^ (carets)
        - Level 5: """"""" (double quotes)
        - Level 6: ####### (hash)
        
        Args:
            text: Heading text
            level: Heading level (1-6)
            
        Returns:
            RST heading with appropriate underline
            
        Raises:
            ValueError: If level is not between 1 and 6
            
        Example:
            >>> renderer.heading("Title", level=1)
            'Title\\n====='
            >>> renderer.heading("Subtitle", level=2)
            'Subtitle\\n--------'
        """
        if not 1 <= level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {level}")
        
        char = self.HEADING_CHARS[level]
        underline = char * len(text)
        return f"{text}\n{underline}"

    def list_item(self, text: str, ordered: bool = False, number: int = 1) -> str:
        """Generate RST list item.
        
        Args:
            text: Item text
            ordered: If True, create numbered list item; if False, bullet point
            number: Number for ordered list items
            
        Returns:
            Formatted RST list item
            
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
        """Generate RST hyperlink.
        
        Note: RST doesn't support title attributes on links.
        
        Args:
            text: Link text (visible to user)
            url: Link URL
            title: Ignored (RST doesn't support title attribute)
            
        Returns:
            RST link in format `text <url>`_
            
        Example:
            >>> renderer.link("GitHub", "https://github.com")
            '`GitHub <https://github.com>`_'
        """
        return f"`{text} <{url}>`_"

    def bold(self, text: str) -> str:
        """Format text as bold.
        
        Uses ** for bold text in RST.
        
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
        
        Uses * for italic text in RST.
        
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
        
        Uses double backticks for inline code in RST.
        
        Args:
            text: Text to format as code
            
        Returns:
            Inline code wrapped in double backticks
            
        Example:
            >>> renderer.inline_code("variable_name")
            '``variable_name``'
        """
        return f"``{text}``"


