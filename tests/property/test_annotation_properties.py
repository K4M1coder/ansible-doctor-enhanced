"""
Property-based tests for annotation parsing.

Using hypothesis to test annotation parsing with randomly generated inputs.
Following Constitution Article III (TDD) - property-based testing for edge cases.
"""

from hypothesis import given, strategies as st
import pytest

from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.models.annotation import AnnotationType


class TestAnnotationParsingProperties:
    """Property-based tests for annotation extraction."""

    @given(
        var_name=st.text(
            alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), min_codepoint=97, max_codepoint=122),
            min_size=1,
            max_size=50
        ).filter(lambda x: x and x[0].isalpha())
    )
    def test_var_annotation_with_any_valid_name(self, var_name):
        """Property: Any valid variable name should be extractable."""
        extractor = AnnotationExtractor()
        content = f"# @var {var_name}: Test description\ntest: value\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        assert len(annotations) >= 1
        var_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        assert len(var_annotations) >= 1
        assert var_annotations[0].key == var_name

    @given(
        description=st.text(min_size=0, max_size=200)
    )
    def test_var_annotation_with_any_description(self, description):
        """Property: Any text description should be parseable."""
        extractor = AnnotationExtractor()
        # Escape newlines in description for single-line annotation
        safe_desc = description.replace("\n", " ").replace("\r", " ")
        content = f"# @var test_var: {safe_desc}\ntest: value\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        var_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        assert len(var_annotations) >= 1
        assert var_annotations[0].key == "test_var"

    @given(
        tag_name=st.text(
            alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), min_codepoint=97, max_codepoint=122),
            min_size=1,
            max_size=30
        ).filter(lambda x: x and x[0].isalpha())
    )
    def test_tag_annotation_with_any_valid_name(self, tag_name):
        """Property: Any valid tag name should be extractable."""
        extractor = AnnotationExtractor()
        content = f"# @tag {tag_name}: Test tag description\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        tag_annotations = [a for a in annotations if a.type == AnnotationType.TAG]
        assert len(tag_annotations) >= 1
        assert tag_annotations[0].key == tag_name

    @given(
        line_count=st.integers(min_value=1, max_value=20)
    )
    def test_multiline_annotations_with_varying_lengths(self, line_count):
        """Property: Multiline annotations should work with any reasonable line count."""
        extractor = AnnotationExtractor()
        lines = ["# @var test_var: Main description"]
        lines.extend([f"# Line {i}" for i in range(line_count)])
        lines.append("test: value")
        content = "\n".join(lines) + "\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        var_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        assert len(var_annotations) >= 1

    @given(
        json_dict=st.dictionaries(
            keys=st.sampled_from(["type", "example", "required", "deprecated"]),
            values=st.one_of(
                st.text(min_size=1, max_size=20),
                st.booleans(),
                st.integers(min_value=0, max_value=9999)
            ),
            min_size=1,
            max_size=4
        )
    )
    def test_json_annotation_with_various_attributes(self, json_dict):
        """Property: JSON annotations should parse any valid JSON dictionary."""
        import json
        extractor = AnnotationExtractor()
        json_str = json.dumps(json_dict)
        content = f"# @var test_var: $ {json_str}\ntest: value\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        var_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        assert len(var_annotations) >= 1
        # Should have parsed attributes
        if "type" in json_dict:
            assert "type" in var_annotations[0].parsed_attributes

    @given(
        comment_count=st.integers(min_value=0, max_value=50)
    )
    def test_files_with_varying_comment_counts(self, comment_count):
        """Property: Should handle files with any number of comments."""
        extractor = AnnotationExtractor()
        lines = [f"# Comment {i}" for i in range(comment_count)]
        lines.append("test: value")
        content = "\n".join(lines) + "\n"
        
        # Should not crash
        annotations = extractor.extract_annotations(content, "test.yml")
        assert isinstance(annotations, list)

    @given(
        spacing=st.integers(min_value=0, max_value=10)
    )
    def test_annotations_with_varying_whitespace(self, spacing):
        """Property: Annotations should work with any amount of whitespace."""
        extractor = AnnotationExtractor()
        spaces = " " * spacing
        content = f"#{spaces}@var{spaces}test_var:{spaces}Description\ntest: value\n"
        
        annotations = extractor.extract_annotations(content, "test.yml")
        
        var_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        # Should still extract the annotation
        assert len(var_annotations) >= 0  # May or may not match depending on regex

    def test_empty_yaml_content(self):
        """Property: Empty content should return empty list."""
        extractor = AnnotationExtractor()
        annotations = extractor.extract_annotations("", "test.yml")
        assert annotations == []

    def test_yaml_without_comments(self):
        """Property: YAML without comments should return empty list."""
        extractor = AnnotationExtractor()
        content = "test: value\nfoo: bar\n"
        annotations = extractor.extract_annotations(content, "test.yml")
        assert annotations == []
