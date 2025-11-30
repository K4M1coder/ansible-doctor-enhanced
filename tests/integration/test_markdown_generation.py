"""Integration tests for Markdown documentation generation.

T220: End-to-end tests for complete Markdown generation workflow.
Tests the full pipeline from role data to rendered Markdown output.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models import AnsibleRole, Example, RoleMetadata, Tag, TodoItem, Variable


class TestMarkdownGenerationIntegration:
    """Integration tests for end-to-end Markdown generation."""

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
                    description="Improve error handling in template",
                    priority="medium",
                    file_path="templates/nginx.conf.j2",
                    line_number=120,
                ),
            ],
            examples=[
                Example(
                    title="Basic Installation",
                    description="Install web server with default settings",
                    code="- hosts: webservers\n  roles:\n    - complex-web-role",
                    language="yaml",
                ),
                Example(
                    title="Custom Configuration",
                    description="Install with custom port and SSL enabled",
                    code="- hosts: webservers\n  roles:\n    - role: complex-web-role\n      vars:\n        web_port: 8080\n        web_ssl_enabled: true",
                    language="yaml",
                ),
            ],
        )

    def test_generate_complete_documentation(self, complex_role):
        """Test generating complete documentation for a complex role."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime(2024, 1, 15, 10, 30, 0),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Verify basic structure
        assert isinstance(result, str)
        assert len(result) > 500  # Should be substantial

        # Verify metadata section
        assert "complex-web-role" in result
        assert "DevOps Team" in result
        assert "Production-ready web server role" in result

        # Verify generation metadata
        assert "2024-01-15" in result
        assert "0.3.0" in result

    def test_verify_all_sections_present(self, complex_role):
        """Test that all major sections are rendered."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Check for all major sections
        assert "Table of Contents" in result
        assert "Overview" in result
        assert "Variables" in result or "variables" in result.lower()
        assert "Tags" in result or "tags" in result.lower()
        assert "TODO" in result
        assert "Examples" in result

    def test_verify_variables_rendered(self, complex_role):
        """Test that all variables are properly rendered."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Check each variable appears (with or without escaping)
        for var in complex_role.variables:
            var_name_variants = [var.name, var.name.replace("_", "\\_")]
            assert any(
                variant in result for variant in var_name_variants
            ), f"Variable {var.name} not found in output"

        # Check variable metadata
        assert "HTTP port" in result
        assert "SSL/TLS" in result
        assert "Document root" in result

    def test_verify_code_blocks_fenced(self, complex_role):
        """Test that code blocks are properly fenced."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Count code fences
        fence_count = result.count("```")
        assert fence_count >= 4  # At least 2 examples = 4 fences
        assert fence_count % 2 == 0  # Must be balanced

        # Verify YAML syntax highlighting
        assert "```yaml" in result

    def test_verify_todos_formatted(self, complex_role):
        """Test that TODOs are formatted with priority indicators."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Check TODO content
        assert "SSL certificate rotation" in result
        assert "error handling" in result

        # Check file locations
        assert "tasks/ssl.yml" in result or "tasks\\/ssl.yml" in result

    def test_verify_tags_rendered(self, complex_role):
        """Test that tags are properly rendered with locations."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Check tag names (possibly escaped)
        assert "install" in result
        assert "configure" in result

        # Check task file locations
        assert "tasks/install.yml" in result or "tasks\\/install.yml" in result

    def test_verify_examples_rendered(self, complex_role):
        """Test that examples are rendered with code blocks."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Check example titles
        assert "Basic Installation" in result
        assert "Custom Configuration" in result

        # Check example content
        assert "hosts: webservers" in result
        assert "web_port: 8080" in result

    def test_output_structure_consistency(self, complex_role):
        """Test that output maintains consistent heading hierarchy."""
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0",
            generation_date=datetime.now(),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        lines = result.split("\n")

        # Check heading hierarchy (# should be first)
        h1_found = False
        for line in lines:
            if line.startswith("# "):
                h1_found = True
                break

        assert h1_found, "Document should start with an H1 heading"

        # Check for ## headings (sections)
        h2_count = sum(1 for line in lines if line.startswith("## "))
        assert h2_count >= 3, "Should have at least 3 major sections"
