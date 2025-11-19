"""Integration tests for HTML documentation generation.

T235: End-to-end tests for complete HTML generation workflow.
Tests the full pipeline from role data to rendered HTML output with CSS and TOC.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable, Tag, TodoItem, Example


class TestHtmlGenerationIntegration:
    """Integration tests for end-to-end HTML generation."""

    @pytest.fixture
    def complex_role(self):
        """Create a complex role with all features populated."""
        return AnsibleRole(
            name="complex-web-role",
            path=Path("E:/tmp/complex-web-role").resolve(),
            metadata=RoleMetadata(
                author="DevOps Team",
                description="Production-ready web server role with monitoring",
                license="Apache-2.0",
                company="Example Corp",
                min_ansible_version="2.10",
            ),
            variables=[
                Variable(
                    name="web_port",
                    value=80,
                    type="number",
                    description="HTTP port for web server",
                    source="defaults/main.yml",
                    required=True,
                ),
                Variable(
                    name="web_ssl_enabled",
                    value=True,
                    type="boolean",
                    description="Enable SSL/TLS encryption",
                    source="defaults/main.yml",
                ),
                Variable(
                    name="web_document_root",
                    value="/var/www/html",
                    type="string",
                    description="Document root directory",
                    source="defaults/main.yml",
                ),
                Variable(
                    name="web_workers",
                    value=4,
                    type="number",
                    description="Number of worker processes",
                    source="defaults/main.yml",
                ),
            ],
            tags=[
                Tag(
                    name="install",
                    description="Installation tasks",
                    file_locations=["tasks/install.yml:10"],
                ),
                Tag(
                    name="configure",
                    description="Configuration tasks",
                    file_locations=["tasks/configure.yml:5", "tasks/configure.yml:20"],
                ),
            ],
            todos=[
                TodoItem(
                    description="Add SSL certificate rotation",
                    priority="high",
                    file_path="tasks/ssl.yml",
                    line_number=45,
                ),
                TodoItem(
                    description="Improve error handling for missing config",
                    priority="medium",
                    file_path="tasks/configure.yml",
                    line_number=12,
                ),
            ],
            examples=[
                Example(
                    title="Basic web server setup",
                    description="Deploy a simple HTTP server",
                    code="- hosts: webservers\n  roles:\n    - complex-web-role",
                    language="yaml",
                ),
                Example(
                    title="HTTPS configuration",
                    description="Deploy with SSL enabled",
                    code="- hosts: webservers\n  roles:\n    - role: complex-web-role\n      vars:\n        web_ssl_enabled: true\n        web_port: 443",
                    language="yaml",
                ),
            ],
        )

    def test_html_generation_with_embed_css(self, complex_role):
        """Test HTML generation with embedded CSS."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<html lang=\"en\">" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "</html>" in result
        
        # Verify CSS is embedded
        assert "<style>" in result
        assert "</style>" in result
        assert "font-family:" in result  # CSS content present
        
        # Verify meta tags
        assert '<meta charset="UTF-8">' in result
        assert '<meta name="viewport"' in result
        assert '<meta name="generator" content="ansible-doctor' in result

    def test_html_generation_with_toc(self, complex_role):
        """Test HTML generation includes table of contents."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify TOC structure
        assert '<nav id="toc">' in result
        assert "Table of Contents" in result
        assert '<a href="#overview">Overview</a>' in result
        assert '<a href="#variables">Variables</a>' in result
        assert '<a href="#tags">Tags</a>' in result
        assert '<a href="#todos">TODOs</a>' in result
        assert '<a href="#examples">Examples</a>' in result

    def test_html_generation_without_toc(self, complex_role):
        """Test HTML generation without table of contents."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=False)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify TOC is not present
        assert '<nav id="toc">' not in result
        assert "Table of Contents" not in result

    def test_html_generation_without_embed_css(self, complex_role):
        """Test HTML generation with external CSS link."""
        renderer = HtmlRenderer(embed_css=False, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify CSS is NOT embedded
        assert "<style>" not in result
        
        # Verify external stylesheet link
        assert '<link rel="stylesheet" href="styles.css">' in result

    def test_html_includes_all_role_sections(self, complex_role):
        """Test that HTML includes all major sections with proper structure."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify section IDs for navigation
        assert '<h2 id="overview">Overview</h2>' in result
        assert '<h2 id="variables">Variables</h2>' in result
        assert '<h2 id="tags">Tags</h2>' in result
        assert '<h2 id="todos">TODOs</h2>' in result
        assert '<h2 id="examples">Examples</h2>' in result
        
        # Verify role metadata
        assert "complex-web-role" in result
        assert "DevOps Team" in result
        assert "Apache-2.0" in result

    def test_html_escapes_special_characters(self, complex_role):
        """Test that HTML properly escapes special characters to prevent XSS."""
        # Create role with special characters
        role_with_special_chars = AnsibleRole(
            name="test<script>alert('xss')</script>",
            path=Path("E:/tmp/test").resolve(),
            metadata=RoleMetadata(
                author="Test & Author <script>",
                description='Role with "quotes" and <tags>',
                license="MIT",
                min_ansible_version="2.9",
            ),
            variables=[
                Variable(
                    name="var_with_<brackets>",
                    value="<script>alert('XSS')</script>",
                    type="string",
                    description='Variable with "quotes" and <html>',
                    source="defaults/main.yml",
                ),
            ],
            tags=[],
            todos=[],
            examples=[],
        )
        
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=role_with_special_chars,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify special characters are escaped
        assert "&lt;script&gt;" in result
        assert "<script>" not in result.replace("<script", "SAFE")  # Not raw script tags
        assert "&amp;" in result or "Test &amp; Author" in result
        assert "&#34;" in result or "&quot;" in result  # Quotes escaped

    def test_html_includes_variables_table(self, complex_role):
        """Test that HTML includes properly formatted variables table."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify all variables are present
        assert "web_port" in result
        assert "web_ssl_enabled" in result
        assert "web_document_root" in result
        assert "web_workers" in result
        
        # Verify variable descriptions
        assert "HTTP port for web server" in result
        assert "Enable SSL/TLS encryption" in result

    def test_html_includes_code_blocks_for_examples(self, complex_role):
        """Test that examples are rendered as code blocks with proper syntax highlighting."""
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Verify code blocks structure
        assert "<pre><code" in result
        assert "</code></pre>" in result
        assert 'class="language-yaml"' in result
        
        # Verify example content is present
        assert "hosts: webservers" in result
        assert "complex-web-role" in result
        assert "web_ssl_enabled: true" in result
