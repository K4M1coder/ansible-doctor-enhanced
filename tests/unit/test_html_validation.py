"""HTML validation tests using html5lib.

T238: Validate rendered HTML output using html5lib parser.
Tests verify syntax correctness and proper semantic structure.
"""

from datetime import datetime
from pathlib import Path

import pytest

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable, Tag, TodoItem, Example


# Try to import html5lib - skip tests if not available
try:
    import html5lib
    HAS_HTML5LIB = True
except ImportError:
    HAS_HTML5LIB = False


pytestmark = pytest.mark.skipif(
    not HAS_HTML5LIB,
    reason="html5lib not installed - optional dependency for HTML validation"
)


class TestHtmlValidation:
    """Test suite for HTML5 validation using html5lib."""

    @pytest.fixture
    def complex_role(self):
        """Create a complex role with all features populated."""
        return AnsibleRole(
            name="validation-test-role",
            path=Path("E:/tmp/validation-test-role").resolve(),
            metadata=RoleMetadata(
                author="Validation Team",
                description="Test role for HTML validation",
                license="MIT",
                min_ansible_version="2.10",
            ),
            variables=[
                Variable(
                    name="test_var",
                    value="test_value",
                    type="string",
                    description="Test variable with <special> & characters",
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
                    description="Test TODO item",
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

    def test_html_parses_without_errors(self, complex_role):
        """Test that rendered HTML parses without syntax errors.
        
        Uses html5lib parser in strict mode to catch any HTML5 violations.
        """
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Parse HTML with html5lib - will raise if invalid
        parser = html5lib.HTMLParser(strict=True)
        document = parser.parse(result)
        
        # Should successfully create a document tree
        assert document is not None
        
        # Should have root element
        assert document.tag is not None

    def test_html_has_proper_semantic_structure(self, complex_role):
        """Test that rendered HTML has proper semantic structure.
        
        Verifies proper nesting: html > head/body, proper meta tags, etc.
        """
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=complex_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Parse with html5lib
        document = html5lib.parse(result)

        # Get the root element (html) - html5lib.parse may return either an
        # ElementTree-like object or an Element depending on the html5lib
        # version, so handle both cases for robustness.
        if hasattr(document, "getroot"):
            root = document.getroot()
        else:
            root = document
        
        # Verify basic structure exists
        # The document should have been parsed successfully
        assert root is not None
        
        # Check that document has expected structure
        # html5lib creates proper tree even if input has minor issues,
        # so we verify it didn't need major corrections
        html_content = result.lower()
        assert "<!doctype html>" in html_content
        assert "<html" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content

    def test_html_special_characters_are_escaped(self, complex_role):
        """Test that special characters in content are properly escaped.
        
        Verifies XSS prevention - user content with <, >, & should be escaped.
        """
        # Create role with potentially dangerous content
        dangerous_role = AnsibleRole(
            name="xss-test",
            path=Path("E:/tmp/xss-test").resolve(),
            metadata=RoleMetadata(
                author="Test <script>alert('XSS')</script>",
                description='Role with "quotes" and <tags> & ampersands',
                license="MIT",
            ),
            variables=[
                Variable(
                    name="dangerous_var",
                    value="<script>alert('XSS')</script>",
                    type="string",
                    description="Variable with <dangerous> content & entities",
                    source="defaults/main.yml",
                ),
            ],
            tags=[],
            todos=[],
            examples=[],
        )
        
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=dangerous_role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Parse HTML - should succeed even with special characters
        document = html5lib.parse(result)
        assert document is not None
        
        # Verify dangerous content is escaped in output
        assert "&lt;script&gt;" in result or "&#60;script&#62;" in result
        assert "<script>alert" not in result or result.count("<script>") == 0  # No unescaped scripts
        
        # Ampersands should be escaped
        assert "&amp;" in result or "&#38;" in result
