"""
Unit tests for variable parser.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
This test suite drives the design of VariableParser through Red-Green-Refactor cycle.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.variable import Variable, VariableType
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor
from ansibledoctor.parser.variable_parser import VariableParser
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


@pytest.fixture
def yaml_loader():
    """Fixture providing YAML loader instance."""
    return RuamelYAMLLoader()


@pytest.fixture
def annotation_extractor():
    """Fixture providing annotation extractor instance."""
    return AnnotationExtractor()


@pytest.fixture
def variable_parser(yaml_loader, annotation_extractor):
    """Fixture providing variable parser instance."""
    return VariableParser(yaml_loader, annotation_extractor)


@pytest.fixture
def minimal_role_path():
    """Fixture providing path to minimal test role."""
    return Path(__file__).parent.parent / "integration" / "fixtures" / "minimal_role"


@pytest.fixture
def complex_role_path():
    """Fixture providing path to complex test role."""
    return Path(__file__).parent.parent / "integration" / "fixtures" / "complex_role"


class TestVariableParsingBasic:
    """Test suite for basic variable parsing."""

    def test_parse_defaults_file(self, variable_parser, minimal_role_path):
        """
        RED: Test parsing simple defaults/main.yml file.
        """
        defaults_file = minimal_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) >= 3
        var_names = [v.name for v in variables]
        assert "minimal_role_port" in var_names
        assert "minimal_role_enabled" in var_names
        assert "minimal_role_name" in var_names

    def test_variable_type_inference(self, variable_parser, minimal_role_path):
        """
        RED: Test automatic type inference from variable values.
        """
        defaults_file = minimal_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # Port should be NUMBER
        port_var = next(v for v in variables if v.name == "minimal_role_port")
        assert port_var.type == VariableType.NUMBER
        
        # Enabled should be BOOLEAN
        enabled_var = next(v for v in variables if v.name == "minimal_role_enabled")
        assert enabled_var.type == VariableType.BOOLEAN
        
        # Name should be STRING
        name_var = next(v for v in variables if v.name == "minimal_role_name")
        assert name_var.type == VariableType.STRING

    def test_variable_with_annotation(self, variable_parser, minimal_role_path):
        """
        RED: Test parsing variable with @var annotation.
        """
        defaults_file = minimal_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # All variables in minimal_role have @var annotations
        port_var = next(v for v in variables if v.name == "minimal_role_port")
        assert port_var.description is not None
        assert "port" in port_var.description.lower()

    def test_variable_source_tracking(self, variable_parser, minimal_role_path):
        """
        RED: Test that variables track their source file.
        """
        defaults_file = minimal_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) > 0
        for var in variables:
            assert var.source == "defaults"

    def test_parse_vars_file(self, variable_parser, tmp_path):
        """
        RED: Test parsing vars/main.yml file (source=vars).
        """
        vars_dir = tmp_path / "vars"
        vars_dir.mkdir()
        vars_file = vars_dir / "main.yml"
        vars_file.write_text("""
# @var internal_port: Internal service port
internal_port: 9000
""")
        
        variables = variable_parser.parse_variables_file(vars_file)
        
        assert len(variables) == 1
        assert variables[0].name == "internal_port"
        assert variables[0].source == "vars"


class TestVariableParsingComplex:
    """Test suite for complex variable structures."""

    def test_parse_nested_dict(self, variable_parser, complex_role_path):
        """
        RED: Test parsing nested dictionary variable.
        """
        defaults_file = complex_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # complex_role has nested database_config
        db_var = next((v for v in variables if v.name == "complex_role_database"), None)
        if db_var:
            assert db_var.type == VariableType.DICT
            assert db_var.is_complex()

    def test_parse_list_variable(self, variable_parser, complex_role_path):
        """
        RED: Test parsing list variable.
        """
        defaults_file = complex_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # complex_role has list variables
        list_vars = [v for v in variables if v.type == VariableType.LIST]
        assert len(list_vars) > 0

    def test_multiline_annotation(self, variable_parser, complex_role_path):
        """
        RED: Test parsing variable with multiline annotation.
        """
        defaults_file = complex_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # complex_role has multiline annotations
        for var in variables:
            if var.description and len(var.description) > 50:
                # Found a variable with substantial description
                assert var.is_documented()
                break

    def test_json_annotation(self, variable_parser, complex_role_path):
        """
        RED: Test parsing variable with JSON-formatted annotation.
        """
        defaults_file = complex_role_path / "defaults" / "main.yml"
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        # complex_role has JSON annotations with required/example fields
        for var in variables:
            if var.required is not None:
                # Found variable with required field from JSON annotation
                assert isinstance(var.required, bool)
                break

    def test_variable_with_example(self, variable_parser, tmp_path):
        """
        RED: Test parsing variable with example value in annotation.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("""
# @var timeout: {"description": "Request timeout", "example": 30}
timeout: 10
""")
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) == 1
        assert variables[0].example is not None


class TestVariableParsingEdgeCases:
    """Test suite for edge cases and error scenarios."""

    def test_empty_defaults_file(self, variable_parser, tmp_path):
        """
        RED: Test parsing empty defaults file.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("")
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert variables == []

    def test_defaults_without_annotations(self, variable_parser, tmp_path):
        """
        RED: Test parsing defaults without any @var annotations.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("""
web_port: 80
web_host: localhost
""")
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) == 2
        # Variables should still be parsed, just without descriptions
        assert variables[0].description is None
        assert variables[1].description is None

    def test_variable_with_null_value(self, variable_parser, tmp_path):
        """
        RED: Test parsing variable with null/None value.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("""
# @var optional_feature: Optional feature flag
optional_feature: null
""")
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) == 1
        assert variables[0].type == VariableType.NULL

    def test_missing_defaults_file(self, variable_parser, tmp_path):
        """
        RED: Test graceful handling when defaults file doesn't exist.
        """
        non_existent = tmp_path / "defaults" / "main.yml"
        
        # Should return empty list, not crash
        variables = variable_parser.parse_variables_file(non_existent)
        
        assert variables == []

    def test_malformed_yaml_handling(self, variable_parser, tmp_path):
        """
        RED: Test error handling for malformed YAML.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("""
web_port: 80
  invalid: indentation
""")
        
        # Should handle gracefully (log error and return empty or partial)
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert isinstance(variables, list)


class TestRoleVariableParsing:
    """Test suite for complete role variable parsing."""

    def test_parse_role_variables(self, variable_parser, minimal_role_path):
        """
        RED: Test parsing all variables from a role (defaults + vars).
        """
        variables = variable_parser.parse_role_variables(minimal_role_path)
        
        assert len(variables) >= 3
        # All should be from defaults or vars
        for var in variables:
            assert var.source in ["defaults", "vars"]

    def test_parse_role_with_both_defaults_and_vars(self, variable_parser, tmp_path):
        """
        RED: Test parsing role with both defaults/ and vars/ directories.
        """
        role_path = tmp_path
        
        # Create defaults
        defaults_dir = role_path / "defaults"
        defaults_dir.mkdir()
        (defaults_dir / "main.yml").write_text("default_var: 1")
        
        # Create vars
        vars_dir = role_path / "vars"
        vars_dir.mkdir()
        (vars_dir / "main.yml").write_text("vars_var: 2")
        
        variables = variable_parser.parse_role_variables(role_path)
        
        assert len(variables) == 2
        sources = [v.source for v in variables]
        assert "defaults" in sources
        assert "vars" in sources

    def test_parse_role_defaults_only(self, variable_parser, minimal_role_path):
        """
        RED: Test parsing role with only defaults/ directory.
        """
        variables = variable_parser.parse_role_variables(minimal_role_path)
        
        # minimal_role only has defaults
        assert all(v.source == "defaults" for v in variables)

    def test_deprecated_variable_detection(self, variable_parser, tmp_path):
        """
        RED: Test detection of deprecated variables from annotations.
        """
        defaults_file = tmp_path / "defaults" / "main.yml"
        defaults_file.parent.mkdir()
        defaults_file.write_text("""
# @var old_var: {"description": "Old variable", "deprecated": true}
old_var: legacy_value
""")
        
        variables = variable_parser.parse_variables_file(defaults_file)
        
        assert len(variables) == 1
        assert variables[0].deprecated is True
        assert variables[0].is_deprecated()
