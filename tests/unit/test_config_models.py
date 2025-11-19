"""Unit tests for configuration models.

Feature 003 - Phase 2 Foundational - T005
Tests ConfigModel Pydantic schema validation.

Constitutional compliance:
- Article III: TDD - Tests written first
- Article I: Library-first architecture
"""

import pytest
from pydantic import ValidationError

from ansibledoctor.config.models import ConfigModel


class TestConfigModelValidation:
    """Test suite for ConfigModel field validation."""
    
    def test_config_model_valid_full(self):
        """Test ConfigModel with all fields populated and valid."""
        config = ConfigModel(
            output="docs/role.html",
            output_format="html",
            template="custom_template.j2",
            template_dir="custom_templates/",
            recursive=True,
            output_dir="output/",
            exclude_patterns=["*.pyc", "test_*", ".git"]
        )
        
        assert config.output == "docs/role.html"
        assert config.output_format == "html"
        assert config.template == "custom_template.j2"
        assert config.template_dir == "custom_templates/"
        assert config.recursive is True
        assert config.output_dir == "output/"
        assert config.exclude_patterns == ["*.pyc", "test_*", ".git"]
    
    def test_config_model_valid_minimal(self):
        """Test ConfigModel with only defaults, no optional fields."""
        config = ConfigModel()
        
        assert config.output is None
        assert config.output_format is None
        assert config.template is None
        assert config.template_dir is None
        assert config.recursive is False
        assert config.output_dir is None
        assert config.exclude_patterns == ["*.pyc", "__pycache__", ".git"]
    
    def test_config_model_defaults(self):
        """Test ConfigModel default values are correct."""
        config = ConfigModel()
        
        # Verify defaults match v0.3.0 CLI behavior
        assert config.recursive is False, "recursive should default to False"
        assert config.exclude_patterns == ["*.pyc", "__pycache__", ".git"], \
            "exclude_patterns should have sensible defaults"
    
    def test_config_model_invalid_output_format(self):
        """Test ConfigModel raises ValidationError for invalid output_format."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigModel(output_format="invalid_format")
        
        error = exc_info.value
        assert len(error.errors()) == 1
        assert error.errors()[0]["loc"] == ("output_format",)
        assert "markdown" in str(error).lower() or "html" in str(error).lower()
    
    def test_config_model_valid_output_formats(self):
        """Test all three valid output formats are accepted."""
        for fmt in ["markdown", "html", "rst"]:
            config = ConfigModel(output_format=fmt)
            assert config.output_format == fmt
    
    def test_config_model_exclude_patterns_validation(self):
        """Test exclude_patterns validates as list of strings."""
        # Valid: list of strings
        config = ConfigModel(exclude_patterns=["*.pyc", "*.tmp"])
        assert config.exclude_patterns == ["*.pyc", "*.tmp"]
        
        # Valid: empty list
        config = ConfigModel(exclude_patterns=[])
        assert config.exclude_patterns == []
    
    def test_config_model_exclude_patterns_invalid_types(self):
        """Test exclude_patterns rejects non-list or non-string items."""
        # Invalid: not a list
        with pytest.raises(ValidationError):
            ConfigModel(exclude_patterns="*.pyc")
        
        # Invalid: list with non-string items
        with pytest.raises(ValidationError):
            ConfigModel(exclude_patterns=["*.pyc", 123, "*.tmp"])
    
    def test_config_model_extra_fields_forbidden(self):
        """Test ConfigModel rejects unknown fields (extra='forbid')."""
        with pytest.raises(ValidationError) as exc_info:
            ConfigModel(
                output_format="html",
                unknown_field="invalid",
                another_unknown="also_invalid"
            )
        
        error = exc_info.value
        errors = error.errors()
        
        # Should have errors for unknown fields
        assert len(errors) >= 1
        field_names = [e["loc"][0] for e in errors]
        assert "unknown_field" in field_names or "another_unknown" in field_names
    
    def test_config_model_whitespace_stripping(self):
        """Test str_strip_whitespace config strips leading/trailing spaces."""
        config = ConfigModel(
            output="  docs/role.html  ",
            output_format="  html  ",
            template="  template.j2  "
        )
        
        assert config.output == "docs/role.html"
        assert config.output_format == "html"
        assert config.template == "template.j2"
    
    def test_config_model_none_values_accepted(self):
        """Test None values are accepted for optional fields."""
        config = ConfigModel(
            output=None,
            output_format=None,
            template=None,
            template_dir=None,
            output_dir=None
        )
        
        assert config.output is None
        assert config.output_format is None
        assert config.template is None
        assert config.template_dir is None
        assert config.output_dir is None
    
    def test_config_model_recursive_boolean_coercion(self):
        """Test recursive field accepts boolean values."""
        config_true = ConfigModel(recursive=True)
        config_false = ConfigModel(recursive=False)
        
        assert config_true.recursive is True
        assert config_false.recursive is False
    
    def test_config_model_partial_override(self):
        """Test ConfigModel allows partial field specification."""
        # Only specify output_format, rest use defaults
        config = ConfigModel(output_format="markdown")
        
        assert config.output_format == "markdown"
        assert config.output is None
        assert config.recursive is False
        assert config.exclude_patterns == ["*.pyc", "__pycache__", ".git"]


class TestConfigModelEdgeCases:
    """Test suite for ConfigModel edge cases and boundary conditions."""
    
    def test_empty_strings_treated_as_values(self):
        """Test empty strings are kept, not converted to None."""
        config = ConfigModel(output="", template="")
        
        # Pydantic str_strip_whitespace will strip, but empty string remains
        assert config.output == ""
        assert config.template == ""
    
    def test_output_format_case_sensitive(self):
        """Test output_format validation is case-sensitive."""
        # Lowercase should work
        config = ConfigModel(output_format="html")
        assert config.output_format == "html"
        
        # Uppercase should fail
        with pytest.raises(ValidationError):
            ConfigModel(output_format="HTML")
        
        # Mixed case should fail
        with pytest.raises(ValidationError):
            ConfigModel(output_format="Html")
    
    def test_exclude_patterns_duplicates_allowed(self):
        """Test duplicate patterns in exclude_patterns are allowed."""
        config = ConfigModel(exclude_patterns=["*.pyc", "*.pyc", "*.tmp"])
        
        # Pydantic doesn't deduplicate automatically
        assert config.exclude_patterns == ["*.pyc", "*.pyc", "*.tmp"]
    
    def test_config_model_dict_export(self):
        """Test ConfigModel can be exported to dict."""
        config = ConfigModel(
            output_format="html",
            recursive=True,
            exclude_patterns=["*.pyc"]
        )
        
        config_dict = config.model_dump()
        
        assert isinstance(config_dict, dict)
        assert config_dict["output_format"] == "html"
        assert config_dict["recursive"] is True
        assert config_dict["exclude_patterns"] == ["*.pyc"]
    
    def test_config_model_dict_export_exclude_none(self):
        """Test ConfigModel can export dict excluding None values."""
        config = ConfigModel(output_format="html")
        
        config_dict = config.model_dump(exclude_none=True)
        
        # Only non-None fields should be present
        assert "output_format" in config_dict
        assert "recursive" in config_dict  # False, not None
        assert "exclude_patterns" in config_dict  # Has default
        assert "output" not in config_dict  # None
        assert "template" not in config_dict  # None
    
    def test_config_model_json_serialization(self):
        """Test ConfigModel can be serialized to JSON."""
        config = ConfigModel(
            output_format="markdown",
            recursive=False,
            exclude_patterns=["*.pyc", "__pycache__"]
        )
        
        json_str = config.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "markdown" in json_str
        assert "*.pyc" in json_str
    
    def test_config_model_from_dict(self):
        """Test ConfigModel can be created from dictionary."""
        data = {
            "output_format": "rst",
            "recursive": True,
            "output_dir": "docs/"
        }
        
        config = ConfigModel(**data)
        
        assert config.output_format == "rst"
        assert config.recursive is True
        assert config.output_dir == "docs/"
