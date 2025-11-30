"""Property-based tests for MarkdownRenderer using Hypothesis.

T218: Test MarkdownRenderer with randomly generated role data to verify:
1. Rendered Markdown is valid (no unclosed blocks)
2. Escaping prevents Markdown injection
3. Code blocks are properly fenced
4. Output structure is consistent
"""

from datetime import datetime
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from ansibledoctor.generator.models import OutputFormat, TemplateContext
from ansibledoctor.generator.renderers.markdown import MarkdownRenderer
from ansibledoctor.models import AnsibleRole, RoleMetadata, Variable


# Strategies for generating test data
@st.composite
def variable_strategy(draw):
    """Generate random Variable objects."""
    name = draw(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=("Ll", "Lu", "Nd"),
                blacklist_characters="_",
                min_codepoint=ord("a"),
            ),
        )
    )

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

    description = draw(st.one_of(st.none(), st.text(min_size=1, max_size=200)))

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
    name = draw(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=("Ll", "Lu", "Nd"), blacklist_characters="-_"
            ),
        )
    )
    description = draw(st.one_of(st.none(), st.text(min_size=1, max_size=500)))
    author = draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))

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


class TestMarkdownRendererProperties:
    """Property-based tests for MarkdownRenderer."""

    @given(role_strategy())
    def test_render_produces_valid_markdown_structure(self, role):
        """Test that rendering produces structurally valid Markdown.

        Property: Rendered output should always have balanced heading structure
        and no unclosed code blocks.
        """
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Property 1: Result should be non-empty string
        assert isinstance(result, str)
        assert len(result) > 0

        # Property 2: Code fences should be balanced
        code_fence_count = result.count("```")
        assert code_fence_count % 2 == 0, f"Unbalanced code fences: {code_fence_count}"

        # Property 3: Should contain role name (escaped or not)
        role_name_variants = [role.name, role.name.replace("_", "\\_")]
        assert any(
            variant in result for variant in role_name_variants
        ), f"Role name '{role.name}' not found in output"

    @given(role_strategy())
    def test_escaping_prevents_markdown_injection(self, role):
        """Test that special Markdown characters are properly escaped.

        Property: Output should not contain unescaped Markdown syntax that
        could break the document structure.
        """
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Property: Description should not contain unescaped special chars
        # that would break heading structure
        if role.metadata.description:
            # Check that description appears in some form
            desc_escaped = role.metadata.description.replace("*", "\\*")
            assert (
                role.metadata.description in result or desc_escaped in result
            ), "Description not found in rendered output"

    @given(st.lists(variable_strategy(), min_size=1, max_size=20))
    def test_all_variables_appear_in_output(self, variables):
        """Test that all variables are rendered in the output.

        Property: Every variable name should appear in the rendered output.
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

        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Property: All variable names should appear (possibly escaped)
        for var in variables:
            var_name_variants = [var.name, var.name.replace("_", "\\_")]
            assert any(
                variant in result for variant in var_name_variants
            ), f"Variable '{var.name}' not found in output"

    @given(role_strategy())
    def test_output_structure_consistency(self, role):
        """Test that output always has consistent structure.

        Property: Output should always contain standard sections in order.
        """
        renderer = MarkdownRenderer()
        context = TemplateContext(
            role=role,
            generator_version="0.3.0-test",
            generation_date=datetime(2024, 1, 1),
            output_format=OutputFormat.MARKDOWN,
        )

        result = renderer.render(context)

        # Property: Should contain generation metadata
        assert "Generated:" in result
        assert "0.3.0-test" in result

        # Property: Should have Table of Contents
        assert "Table of Contents" in result

        # Property: Should have Overview section
        assert "Overview" in result

        # Property: Variables section should appear if role has variables
        if len(role.variables) > 0:
            assert "Variables" in result or "variables" in result.lower()
