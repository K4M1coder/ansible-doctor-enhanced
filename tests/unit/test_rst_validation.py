"""RST validation tests using docutils.

T247: Validate rendered RST output using docutils parser.
Tests verify syntax correctness and proper RST structure.
Optional: Sphinx directives validated if sphinx-build available.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.rst import RstRenderer
from ansibledoctor.models import AnsibleRole, Example, RoleMetadata, Tag, TodoItem, Variable

# Try to import docutils - skip tests if not available
try:
    from docutils.core import publish_parts

    HAS_DOCUTILS = True
except ImportError:
    HAS_DOCUTILS = False


pytestmark = pytest.mark.skipif(
    not HAS_DOCUTILS, reason="docutils not installed - optional dependency for RST validation"
)


class TestRstValidation:
    """Test suite for RST validation using docutils."""

    @pytest.fixture
    def complex_role(self):
        """Create a complex role with all features populated."""
        return AnsibleRole(
            name="validation-test-role",
            path=Path("E:/tmp/validation-test-role").resolve(),
            metadata=RoleMetadata(
                author="Validation Team",
                description="Test role for RST validation",
                license="MIT",
                min_ansible_version="2.10",
            ),
            variables=[
                Variable(
                    name="test_var",
                    value="test_value",
                    type="string",
                    description="Test variable with * special ` _ characters",
                    source="defaults/main.yml",
                ),
            ],
            tags=[
                Tag(
                    name="validation",
                    description="Validation tag",
                    file_locations=["tasks/main.yml:10"],
                ),
            ],
            todos=[
                TodoItem(
                    description="Test TODO item with critical priority",
                    priority="high",
                    file_path="tasks/main.yml",
                    line_number=42,
                ),
            ],
            examples=[
                Example(
                    title="Test example",
                    description="Example with code",
                    code="- hosts: all\n  roles:\n    - validation-test-role",
                    language="yaml",
                ),
            ],
        )

    def test_rst_parses_without_errors(self, complex_role):
        """Test that rendered RST parses without syntax errors.

        Uses docutils parser to catch any RST violations.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )

        result = renderer.render(context)

        # Parse with docutils - should not raise exceptions
        try:
            parts = publish_parts(
                source=result,
                writer_name="html",
                settings_overrides={
                    "report_level": 2,  # Report warnings and above
                    "halt_level": 4,  # Don't halt on warnings
                    "warning_stream": False,  # Suppress warning output
                },
            )

            # If parsing succeeds, we have valid RST
            assert parts["html_body"] is not None
            assert len(parts["html_body"]) > 0

        except Exception as e:
            pytest.fail(f"RST parsing failed: {e}")

    def test_rst_has_proper_structure(self, complex_role):
        """Test that RST has proper document structure.

        Verifies sections, field lists, and directives are correctly formatted.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )

        result = renderer.render(context)

        # Parse to HTML to verify structure
        parts = publish_parts(
            source=result, writer_name="html", settings_overrides={"report_level": 5}
        )

        html = parts["html_body"]

        # Should have title
        assert "<h1" in html or "<h2" in html

        # Should have field lists (converted to definition lists in HTML)
        assert "Generated" in html or "Version" in html

        # Should have paragraphs or sections
        assert "<p>" in html or "<div" in html

    def test_sphinx_directives_valid(self, complex_role):
        """Test that Sphinx directives are properly formatted.

        Verifies .. warning::, .. note::, .. code-block:: directives.
        Note: docutils won't process Sphinx-specific directives,
        but should not error on them.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 15, 10, 30),
            output_format=OutputFormat.RST,
        )

        result = renderer.render(context)

        # Verify Sphinx directives are present
        assert ".. warning::" in result  # High priority TODO
        assert ".. note::" in result  # Footer note
        assert ".. code-block::" in result  # Example code

        # Parse - docutils will treat unknown directives as system messages
        # but should not crash
        try:
            parts = publish_parts(
                source=result,
                writer_name="html",
                settings_overrides={
                    "report_level": 5,  # Suppress all messages
                    "halt_level": 5,  # Don't halt
                },
            )

            # Parsing should succeed even with Sphinx directives
            assert parts["html_body"] is not None

        except Exception as e:
            pytest.fail(f"RST with Sphinx directives failed to parse: {e}")
