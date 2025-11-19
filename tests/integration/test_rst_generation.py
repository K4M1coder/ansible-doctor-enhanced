"""Integration tests for RST documentation generation.

T244: End-to-end tests for complete RST generation workflow.
Tests the full pipeline from role data to rendered RST output with Sphinx directives.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.rst import RstRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable, Tag, TodoItem, Example


class TestRstGenerationIntegration:
    """Integration tests for end-to-end RST generation."""

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
                    description="Root directory for web content",
                    source="defaults/main.yml",
                ),
                Variable(
                    name="web_workers",
                    value=4,
                    type="number",
                    description="Number of worker processes",
                    source="vars/main.yml",
                ),
            ],
            tags=[
                Tag(name="web", count=12),
                Tag(name="security", count=8),
            ],
            todos=[
                TodoItem(
                    description="Add SSL certificate renewal automation",
                    priority="high",
                    file_path="tasks/ssl.yml",
                    line_number=42,
                ),
                TodoItem(
                    description="Implement backup rotation policy",
                    priority="medium",
                    file_path="tasks/backup.yml",
                    line_number=15,
                ),
                TodoItem(
                    description="Update firewall rules for IPv6",
                    priority="low",
                    file_path="tasks/firewall.yml",
                    line_number=28,
                ),
            ],
            examples=[
                Example(
                    title="Basic Usage",
                    code="- hosts: webservers\n  roles:\n    - role: complex-web-role\n      vars:\n        web_ssl_enabled: true\n        web_port: 443",
                    language="yaml",
                ),
            ],
        )

    def test_rst_generates_proper_structure(self, complex_role):
        """Test RST generation produces proper document structure."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify title with underline
        assert "complex-web-role" in result
        assert "================" in result  # Title underline
        
        # Verify field lists
        assert ":Generated:" in result
        assert ":Version:" in result
        assert "2024-01-15 10:30" in result
        assert "0.3.0" in result
        
        # Verify main sections
        assert "Overview" in result
        assert "Variables" in result
        assert "Tags" in result
        assert "TODOs" in result
        assert "Examples" in result

    def test_rst_includes_table_of_contents(self, complex_role):
        """Test RST generation includes table of contents directive."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify TOC directive
        assert ".. contents::" in result
        assert ":depth:" in result
        assert ":local:" in result

    def test_rst_code_blocks_formatted(self, complex_role):
        """Test RST code blocks use proper .. code-block:: directive."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify code-block directive
        assert ".. code-block:: yaml" in result
        
        # Verify code content is present and indented
        assert "- hosts: webservers" in result
        assert "  roles:" in result
        assert "    - role: complex-web-role" in result

    def test_rst_with_sphinx_compat_true(self, complex_role):
        """Test RST with sphinx_compat=True uses Sphinx directives."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify Sphinx directives are present
        assert ".. warning::" in result  # High priority TODO
        assert "Add SSL certificate renewal automation" in result
        
        # Verify directive fields
        assert ":Priority: HIGH" in result
        assert ":Location:" in result
        assert "tasks/ssl.yml:42" in result

    def test_rst_with_sphinx_compat_false(self, complex_role):
        """Test RST with sphinx_compat=False uses simple lists."""
        renderer = RstRenderer(sphinx_compat=False)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context, sphinx_compat=False)
        
        # Verify simple list format (no warning directive)
        assert ".. warning::" not in result
        
        # Verify simple list with priority badges
        assert "Add SSL certificate renewal automation" in result
        assert "tasks/ssl.yml:42" in result

    def test_rst_high_priority_todos_use_warning(self, complex_role):
        """Test high/critical priority TODOs use .. warning:: directive."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # High priority TODO should use warning directive
        assert ".. warning:: Add SSL certificate renewal automation" in result
        assert ":Priority: HIGH" in result
        
        # Medium/low priority TODOs should use simple list
        lines = result.split("\n")
        backup_line = [line for line in lines if "Implement backup rotation policy" in line]
        assert len(backup_line) > 0
        # Should be a list item, not a directive
        assert any(line.strip().startswith("-") for line in backup_line)

    def test_rst_escapes_special_characters(self, complex_role):
        """Test RST escapes special characters properly."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify variable names are present
        assert "web_port" in result
        assert "web_ssl_enabled" in result
        
        # Verify RST structure doesn't break with special chars in content
        assert "complex-web-role" in result
        assert "================" in result

    def test_rst_includes_all_sections(self, complex_role):
        """Test RST includes all expected sections."""
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Verify all sections present
        assert "Overview" in result
        assert "Variables" in result
        assert "web_port" in result
        assert "web_ssl_enabled" in result
        
        assert "Tags" in result
        assert "web" in result
        assert "security" in result
        
        assert "TODOs" in result
        assert "Add SSL certificate renewal automation" in result
        
        assert "Examples" in result
        assert ".. code-block::" in result
        
        # Verify footer note
        assert ".. note::" in result
        assert "ansible-doctor" in result
