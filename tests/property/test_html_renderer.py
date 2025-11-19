"""Property-based tests for HtmlRenderer using Hypothesis.

T237: Test HtmlRenderer with randomly generated role data to verify:
1. Rendered HTML is valid (proper DOCTYPE, balanced tags)
2. Escaping prevents XSS injection
3. Output structure is consistent
4. Special characters don't break HTML structure
"""

from datetime import datetime
from pathlib import Path

from hypothesis import given, strategies as st

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.html import HtmlRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable


# Strategies for generating test data
@st.composite
def variable_strategy(draw):
    """Generate random Variable objects with potentially dangerous characters."""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        blacklist_characters='_',
        min_codepoint=ord('a')
    )))
    
    # Generate value and matching type
    value_type_pairs = [
        (st.integers(), "number"),
        (st.floats(allow_nan=False, allow_infinity=False), "number"),
        (st.booleans(), "boolean"),
        (st.text(max_size=100), "string"),
        (st.lists(st.text(max_size=20), max_size=5), "list"),
    ]
    value_strategy, var_type = draw(st.sampled_from(value_type_pairs))
    value = draw(value_strategy)
    
    description = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=200)
    ))
    
    return Variable(
        name=name,
        value=value,
        type=var_type,
        description=description,
        source="defaults/main.yml",
    )


@st.composite
def role_strategy(draw):
    """Generate random AnsibleRole objects."""
    name = draw(st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), blacklist_characters='-_')
    ))
    description = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=500)
    ))
    author = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=100)
    ))
    
    variables = draw(st.lists(variable_strategy(), max_size=10))
    
    # Use absolute path that's valid on Windows
    role_path = Path("E:/tmp") / name
    
    return AnsibleRole(
        name=name,
        path=role_path.resolve(),
        metadata=RoleMetadata(
            author=author,
            description=description,
            license="MIT",
        ),
        variables=variables,
        tags=[],
        todos=[],
        examples=[],
    )


class TestHtmlRendererProperties:
    """Property-based tests for HtmlRenderer."""

    @given(role_strategy())
    def test_render_produces_valid_html_structure(self, role):
        """Test that rendering produces structurally valid HTML.
        
        Property: Rendered output should always have proper DOCTYPE,
        html, head, and body tags.
        """
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Property 1: Result should be non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property 2: Should have proper HTML5 structure
        assert "<!DOCTYPE html>" in result
        assert "<html" in result
        assert "</html>" in result
        assert "<head>" in result
        assert "</head>" in result
        assert "<body>" in result
        assert "</body>" in result
        
        # Property 3: Basic tag balance check
        assert result.count("<html") == result.count("</html>")
        assert result.count("<head>") == result.count("</head>")
        assert result.count("<body>") == result.count("</body>")

    @given(role_strategy())
    def test_escaping_prevents_xss_injection(self, role):
        """Test that special HTML characters are properly escaped.
        
        Property: Output should not contain unescaped HTML that could
        lead to XSS vulnerabilities.
        """
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Property: Raw script tags should not appear in output
        # (legitimate script tags are in template, but user content should be escaped)
        # Check that if role name contains <script>, it's escaped
        if "<script>" in role.name.lower():
            assert "&lt;script&gt;" in result or "&#60;script&#62;" in result, \
                "Script tag not properly escaped in role name"
        
        # Property: Description should not contain unescaped HTML
        if role.metadata.description and "<" in role.metadata.description:
            # Should be escaped as &lt; or &#60;
            assert "&lt;" in result or "&#60;" in result, \
                "HTML special characters not escaped in description"

    @given(st.lists(variable_strategy(), min_size=1, max_size=20))
    def test_all_variables_appear_in_output(self, variables):
        """Test that all variables are rendered in the output.
        
        Property: Every variable name should appear in the rendered HTML output.
        """
        role = AnsibleRole(
            name="test-role",
            path=Path("E:/tmp/test-role").resolve(),
            metadata=RoleMetadata(
                author="Test Author",
                description="Test description",
            ),
            variables=variables,
            tags=[],
            todos=[],
            examples=[],
        )
        
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Property: All variable names should appear in output
        for var in variables:
            assert var.name in result, \
                f"Variable '{var.name}' not found in output"

    @given(role_strategy())
    def test_output_structure_consistency(self, role):
        """Test that output always has consistent HTML structure.
        
        Property: Output should always contain standard HTML sections.
        """
        renderer = HtmlRenderer(embed_css=True, generate_toc=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.HTML,
        )
        
        result = renderer.render(context)
        
        # Property: Should contain meta tags
        assert '<meta charset="UTF-8">' in result
        assert '<meta name="viewport"' in result
        assert '<meta name="generator"' in result
        
        # Property: Should have proper title
        assert "<title>" in result
        assert "</title>" in result
        
        # Property: Should have style or link tag
        assert "<style>" in result or '<link rel="stylesheet"' in result
        
        # Property: Should have TOC section
        assert '<nav id="toc">' in result or "Table of Contents" in result
        
        # Property: Should have Overview section with proper ID
        assert '<h2 id="overview">' in result or "Overview" in result
        
        # Property: Variables section should appear if role has variables
        if len(role.variables) > 0:
            assert '<h2 id="variables">' in result or "Variables" in result
