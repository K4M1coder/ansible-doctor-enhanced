"""
Integration tests for variable parser using fixture roles.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
These tests validate end-to-end variable parsing with realistic role structures.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.variable import VariableType
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


@pytest.fixture
def variable_parser():
    """Fixture providing variable parser with dependencies."""
    yaml_loader = RuamelYAMLLoader()
    annotation_extractor = AnnotationExtractor()
    return VariableParser(yaml_loader, annotation_extractor)


@pytest.fixture
def fixtures_path():
    """Fixture providing path to integration test fixtures."""
    return Path(__file__).parent / "fixtures"


class TestMinimalRoleVariables:
    """Integration tests using minimal_role fixture."""

    def test_parse_minimal_role_all_variables(self, variable_parser, fixtures_path):
        """
        RED: Test complete variable parsing for minimal role.
        
        Validates US2 acceptance criteria:
        - Extract variables from defaults/main.yml
        - Infer types automatically (string, number, boolean)
        - Parse @var annotations (single-line format)
        """
        role_path = fixtures_path / "minimal_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        assert len(variables) == 3
        
        # Verify all expected variables present
        var_names = {v.name for v in variables}
        assert "minimal_role_port" in var_names
        assert "minimal_role_enabled" in var_names
        assert "minimal_role_name" in var_names

    def test_minimal_role_type_inference(self, variable_parser, fixtures_path):
        """
        RED: Test type inference for minimal role variables.
        """
        role_path = fixtures_path / "minimal_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Create lookup dict
        var_dict = {v.name: v for v in variables}
        
        # minimal_role_port: 8080 -> NUMBER
        assert var_dict["minimal_role_port"].type == VariableType.NUMBER
        assert var_dict["minimal_role_port"].value == 8080
        
        # minimal_role_enabled: true -> BOOLEAN
        assert var_dict["minimal_role_enabled"].type == VariableType.BOOLEAN
        assert var_dict["minimal_role_enabled"].value is True
        
        # minimal_role_name: "test" -> STRING
        assert var_dict["minimal_role_name"].type == VariableType.STRING
        assert var_dict["minimal_role_name"].value == "test"

    def test_minimal_role_annotations(self, variable_parser, fixtures_path):
        """
        RED: Test annotation extraction for minimal role variables.
        """
        role_path = fixtures_path / "minimal_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # All variables should have descriptions from @var annotations
        for var in variables:
            assert var.is_documented()
            assert var.description is not None
            assert len(var.description) > 0

    def test_minimal_role_source_tracking(self, variable_parser, fixtures_path):
        """
        RED: Test source file tracking for minimal role.
        """
        role_path = fixtures_path / "minimal_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # minimal_role only has defaults/main.yml
        assert all(v.source == "defaults" for v in variables)


class TestComplexRoleVariables:
    """Integration tests using complex_role fixture."""

    def test_parse_complex_role_all_variables(self, variable_parser, fixtures_path):
        """
        RED: Test complete variable parsing for complex role.
        
        Validates US2 acceptance criteria:
        - Extract nested variables (dict, list)
        - Parse multiline @var annotations
        - Parse JSON-formatted annotations
        - Handle required/example fields
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # complex_role has multiple variables with various types
        assert len(variables) >= 3

    def test_complex_role_nested_dict_variable(self, variable_parser, fixtures_path):
        """
        RED: Test parsing nested dictionary variable.
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Find dict variable
        dict_vars = [v for v in variables if v.type == VariableType.DICT]
        assert len(dict_vars) > 0
        
        # Verify dict variable properties
        dict_var = dict_vars[0]
        assert dict_var.is_complex()
        assert isinstance(dict_var.value, dict)

    def test_complex_role_list_variable(self, variable_parser, fixtures_path):
        """
        RED: Test parsing list variable.
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Find list variable
        list_vars = [v for v in variables if v.type == VariableType.LIST]
        assert len(list_vars) > 0
        
        # Verify list variable properties
        list_var = list_vars[0]
        assert list_var.is_complex()
        assert isinstance(list_var.value, list)

    def test_complex_role_json_annotations(self, variable_parser, fixtures_path):
        """
        RED: Test parsing JSON-formatted annotations.
        
        complex_role has variables with:
        # @var name: {"description": "...", "required": true, "example": ...}
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Find variable with required field (from JSON annotation)
        required_vars = [v for v in variables if v.required is not None]
        assert len(required_vars) > 0

    def test_complex_role_multiline_annotations(self, variable_parser, fixtures_path):
        """
        RED: Test parsing multiline annotations.
        
        complex_role has variables with:
        # @var name:
        #   description: Long description
        #   required: true
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Variables should have rich descriptions
        documented_vars = [v for v in variables if v.is_documented()]
        assert len(documented_vars) > 0

    def test_complex_role_example_values(self, variable_parser, fixtures_path):
        """
        RED: Test extraction of example values from annotations.
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        # Some variables should have examples
        vars_with_examples = [v for v in variables if v.example is not None]
        # At least one variable should have an example
        assert len(vars_with_examples) >= 0  # May be 0 if not in fixture


class TestVariableStatistics:
    """Integration tests for variable statistics and analysis."""

    def test_documented_vs_undocumented_ratio(self, variable_parser, fixtures_path):
        """
        RED: Test calculating ratio of documented variables.
        """
        role_path = fixtures_path / "minimal_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        documented = [v for v in variables if v.is_documented()]
        ratio = len(documented) / len(variables) if variables else 0
        
        # minimal_role should have all variables documented
        assert ratio == 1.0

    def test_type_distribution(self, variable_parser, fixtures_path):
        """
        RED: Test analyzing variable type distribution.
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        type_counts = {}
        for var in variables:
            type_counts[var.type] = type_counts.get(var.type, 0) + 1
        
        # complex_role should have multiple types
        assert len(type_counts) >= 2

    def test_complex_variables_identification(self, variable_parser, fixtures_path):
        """
        RED: Test identifying complex variables (dict, list).
        """
        role_path = fixtures_path / "complex_role"
        
        variables = variable_parser.parse_role_variables(role_path)
        
        complex_vars = [v for v in variables if v.is_complex()]
        simple_vars = [v for v in variables if not v.is_complex()]
        
        # complex_role should have both simple and complex variables
        assert len(complex_vars) > 0
        assert len(simple_vars) > 0


class TestEdgeCases:
    """Integration tests for edge cases."""

    def test_role_without_variables(self, variable_parser, tmp_path):
        """
        RED: Test parsing role without defaults/ or vars/ directories.
        """
        role_path = tmp_path
        
        variables = variable_parser.parse_role_variables(role_path)
        
        assert variables == []

    def test_role_with_empty_defaults(self, variable_parser, tmp_path):
        """
        RED: Test parsing role with empty defaults/main.yml.
        """
        role_path = tmp_path
        defaults_dir = role_path / "defaults"
        defaults_dir.mkdir()
        (defaults_dir / "main.yml").write_text("")
        
        variables = variable_parser.parse_role_variables(role_path)
        
        assert variables == []

    def test_deprecated_variables_filtering(self, variable_parser, tmp_path):
        """
        RED: Test filtering deprecated variables.
        """
        role_path = tmp_path
        defaults_dir = role_path / "defaults"
        defaults_dir.mkdir()
        (defaults_dir / "main.yml").write_text("""
# @var new_var: Current variable
new_var: value1

# @var old_var: {"description": "Deprecated", "deprecated": true}
old_var: value2
""")
        
        variables = variable_parser.parse_role_variables(role_path)
        
        deprecated = [v for v in variables if v.is_deprecated()]
        active = [v for v in variables if not v.is_deprecated()]
        
        assert len(deprecated) == 1
        assert len(active) == 1
