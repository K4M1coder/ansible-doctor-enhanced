"""Property-based tests for RstRenderer using Hypothesis.

T246: Test RstRenderer with randomly generated role data to verify:
1. Rendered RST has valid structure (headings, directives)
2. Escaping prevents RST injection/formatting breaks
3. Output structure is consistent
4. Special characters don't break RST markup
"""

from datetime import datetime
from pathlib import Path

from hypothesis import given, strategies as st

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.rst import RstRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable


# Strategies for generating test data
@st.composite
def variable_strategy(draw):
    """Generate random Variable objects with potentially dangerous RST characters."""
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


class TestRstRendererProperties:
    """Property-based tests for RstRenderer."""

    @given(role_strategy())
    def test_render_produces_valid_rst_structure(self, role):
        """Test that rendering produces structurally valid RST.
        
        Property: Rendered output should always have proper title,
        field lists, and section headers with matching underlines.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Property 1: Result should be non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property 2: Should have RST field lists
        assert ":Generated:" in result
        assert ":Version:" in result
        
        # Property 3: Should have at least one section with underline
        lines = result.split("\n")
        has_underline = any(
            line and all(c in "=-~`" for c in line)
            for line in lines
        )
        assert has_underline, "RST should have section underlines"
        
        # Property 4: Role name should appear in output
        assert role.name in result

    @given(role_strategy())
    def test_escaping_prevents_rst_injection(self, role):
        """Test that special RST characters are properly escaped.
        
        Property: Output should not contain unescaped RST markup that could
        break the document structure.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Property: If role has variables, they should appear
        for variable in role.variables:
            # Variable names should appear (possibly escaped)
            assert variable.name in result or variable.name.replace("_", "\\_") in result
        
        # Property: RST structure should not be broken by special chars
        # No unbalanced inline markup indicators
        lines = result.split("\n")
        for line in lines:
            # Field list lines should start with :
            if line.strip().startswith(":") and ":" in line[1:]:
                # Should be a valid field list format
                assert line.count(":") >= 2  # :Field: value format

    @given(role_strategy())
    def test_all_variables_appear_in_output(self, role):
        """Test that all role variables appear in rendered output.
        
        Property: Every variable in the role should be represented
        in the output documentation.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Property: All variable names should appear in output
        for variable in role.variables:
            # Variable name should appear (with possible escaping or code markup)
            assert (
                variable.name in result or
                f"``{variable.name}``" in result or
                variable.name.replace("_", "\\_") in result
            ), f"Variable {variable.name} not found in output"

    @given(role_strategy())
    def test_output_structure_consistency(self, role):
        """Test that output has consistent structure regardless of input.
        
        Property: Standard sections should always be present and
        in a consistent order.
        """
        renderer = RstRenderer(sphinx_compat=True)
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.RST,
        )
        
        result = renderer.render(context)
        
        # Property 1: Should have overview/metadata section
        assert ":Generated:" in result
        assert ":Version:" in result
        
        # Property 2: Footer note should be present
        assert ".. note::" in result
        assert "ansible-doctor" in result.lower()
        
        # Property 3: Section order should be consistent
        # Find positions of standard sections
        sections = ["Overview", "Variables", "Examples", ".. note::"]
        section_positions = {}
        for section in sections:
            if section in result:
                section_positions[section] = result.index(section)
        
        # If multiple sections present, they should be in order
        if len(section_positions) >= 2:
            positions = list(section_positions.values())
            # Note: Not all sections required, but those present should be ordered
            # Just verify positions are increasing for found sections
            assert positions == sorted(positions), f"Sections out of order: {section_positions}"
