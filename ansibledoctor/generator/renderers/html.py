"""HTML renderer for Ansible role documentation.

This module provides the HtmlRenderer class that renders role documentation
in HTML format with support for CSS embedding and table of contents generation.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from markupsafe import Markup, escape

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.protocols import DocumentRenderer


class HtmlRenderer(DocumentRenderer):
    """Renders role documentation in HTML format.
    
    This renderer produces well-structured HTML5 documents with optional
    embedded CSS styling and table of contents navigation. It properly
    escapes HTML entities to prevent XSS vulnerabilities.
    
    Attributes:
        embed_css: Whether to embed CSS in <style> tag (default: True)
        generate_toc: Whether to generate table of contents (default: True)
    """
    
    def __init__(self, embed_css: bool = True, generate_toc: bool = True):
        """Initialize HTML renderer.
        
        Args:
            embed_css: Embed CSS in document (default: True)
            generate_toc: Generate table of contents (default: True)
        """
        self.embed_css = embed_css
        self.generate_toc = generate_toc
    
    @property
    def format(self) -> OutputFormat:
        """Return the output format for this renderer.
        
        Returns:
            OutputFormat.HTML
        """
        return OutputFormat.HTML
    
    def escape(self, text: Optional[str]) -> str:
        """Escape HTML entities in text.
        
        Uses markupsafe.escape to safely escape HTML special characters
        (<, >, &, ", ') to prevent XSS attacks.
        
        Args:
            text: Text to escape (None returns empty string)
            
        Returns:
            HTML-escaped string
        """
        if text is None:
            return ""
        return str(escape(text))
    
    def code_block(self, code: Optional[str], language: Optional[str] = None) -> str:
        """Format code in HTML <pre><code> block.
        
        Args:
            code: Code content (None returns empty block)
            language: Language hint for syntax highlighting (optional)
            
        Returns:
            HTML pre/code block with escaped content
        """
        if code is None:
            code = ""
        
        escaped_code = self.escape(code)
        
        if language:
            return f'<pre><code class="language-{self.escape(language)}">{escaped_code}</code></pre>'
        return f"<pre><code>{escaped_code}</code></pre>"
    
    def render(self, context: TemplateContext, **options: Any) -> str:
        """Render role documentation as HTML.
        
        Args:
            context: Template context with role data
            **options: Additional rendering options (overrides instance settings)
            
        Returns:
            Complete HTML document string
            
        Raises:
            TemplateNotFoundError: If html template not found
            TemplateRenderError: If rendering fails
        """
        # Merge instance settings with options
        render_options = {
            "embed_css": options.get("embed_css", self.embed_css),
            "generate_toc": options.get("generate_toc", self.generate_toc),
        }
        
        # Validate options before rendering
        self.validate_options(render_options)
        
        # Load CSS content if embedding
        css_content = ""
        if render_options["embed_css"]:
            css_content = self._load_css()
        
        # Build HTML structure
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            f"  <meta charset=\"UTF-8\">",
            f"  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
            f"  <title>{self.escape(context.role.name)} - Ansible Role Documentation</title>",
        ]
        
        # Embed CSS if requested
        if render_options["embed_css"] and css_content:
            html_parts.extend([
                "  <style>",
                css_content,
                "  </style>",
            ])
        
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Generate TOC if requested
        if render_options["generate_toc"]:
            html_parts.extend([
                "  <nav id=\"toc\">",
                "    <h2>Table of Contents</h2>",
                "    <ul>",
                "      <li><a href=\"#description\">Description</a></li>",
                "      <li><a href=\"#variables\">Variables</a></li>",
                "      <li><a href=\"#examples\">Examples</a></li>",
                "    </ul>",
                "  </nav>",
            ])
        
        # Main content
        html_parts.extend([
            "  <main>",
            f"    <h1>{self.escape(context.role.name)}</h1>",
            f"    <section id=\"description\">",
            f"      <h2>Description</h2>",
            f"      <p>{self.escape(context.role.metadata.description)}</p>",
            "    </section>",
        ])
        
        # Variables section
        if context.role.variables:
            html_parts.append("    <section id=\"variables\">")
            html_parts.append("      <h2>Variables</h2>")
            html_parts.append("      <table>")
            html_parts.append("        <thead>")
            html_parts.append("          <tr>")
            html_parts.append("            <th>Variable</th>")
            html_parts.append("            <th>Description</th>")
            html_parts.append("            <th>Default</th>")
            html_parts.append("          </tr>")
            html_parts.append("        </thead>")
            html_parts.append("        <tbody>")
            
            for var in context.role.variables:
                html_parts.append("          <tr>")
                html_parts.append(f"            <td><code>{self.escape(var.name)}</code></td>")
                
                # Description from annotation if available
                desc = ""
                if var.annotation and var.annotation.description:
                    desc = var.annotation.description
                html_parts.append(f"            <td>{self.escape(desc)}</td>")
                
                # Default value
                default = str(var.default_value) if var.default_value is not None else "—"
                html_parts.append(f"            <td><code>{self.escape(default)}</code></td>")
                html_parts.append("          </tr>")
            
            html_parts.append("        </tbody>")
            html_parts.append("      </table>")
            html_parts.append("    </section>")
        
        # Examples section
        if context.role.examples:
            html_parts.append("    <section id=\"examples\">")
            html_parts.append("      <h2>Examples</h2>")
            
            for example in context.role.examples:
                if example.description:
                    html_parts.append(f"      <h3>{self.escape(example.description)}</h3>")
                html_parts.append(f"      {self.code_block(example.content, 'yaml')}")
            
            html_parts.append("    </section>")
        
        html_parts.extend([
            "  </main>",
            "  <footer>",
            f"    <p>Generated by ansible-doctor v{context.generator_version}</p>",
            "  </footer>",
            "</body>",
            "</html>",
        ])
        
        return "\n".join(html_parts)
    
    def validate_options(self, options: Dict[str, Any]) -> None:
        """Validate rendering options.
        
        Args:
            options: Options dictionary to validate
            
        Raises:
            TypeError: If option types are invalid
            ValueError: If option values are invalid
        """
        if "embed_css" in options and not isinstance(options["embed_css"], bool):
            raise TypeError(f"embed_css must be bool, got {type(options['embed_css'])}")
        
        if "generate_toc" in options and not isinstance(options["generate_toc"], bool):
            raise TypeError(f"generate_toc must be bool, got {type(options['generate_toc'])}")
    
    def _load_css(self) -> str:
        """Load CSS content for embedding.
        
        Returns:
            CSS stylesheet content
        """
        # Basic embedded CSS for documentation
        return """
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        color: #333;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    
    h2 {
        color: #34495e;
        margin-top: 30px;
    }
    
    nav#toc {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 30px;
    }
    
    nav#toc ul {
        list-style: none;
        padding-left: 0;
    }
    
    nav#toc li {
        margin: 5px 0;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    th, td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    
    th {
        background-color: #3498db;
        color: white;
        font-weight: 600;
    }
    
    tr:hover {
        background-color: #f5f5f5;
    }
    
    code {
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "Courier New", Courier, monospace;
    }
    
    pre {
        background: #2d2d2d;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: inherit;
    }
    
    footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        text-align: center;
        color: #666;
        font-size: 0.9em;
    }
    
    @media (max-width: 768px) {
        body {
            padding: 10px;
        }
        
        table {
            font-size: 0.9em;
        }
        
        th, td {
            padding: 8px;
        }
    }
        """
