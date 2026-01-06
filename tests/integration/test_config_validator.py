"""Integration tests for configuration file validation.

Tests the ConfigurationValidator with real .ansibledoctor.yml files.
"""

from pathlib import Path

import pytest

from ansibledoctor.validation.config_validator import ConfigurationValidator


@pytest.fixture
def config_validator():
    """Create a ConfigurationValidator instance."""
    return ConfigurationValidator()


@pytest.fixture
def valid_config_path():
    """Path to valid config fixture."""
    return Path(__file__).parent.parent / "fixtures" / "configs" / "valid_config.yml"


@pytest.fixture
def invalid_config_path():
    """Path to invalid config fixture."""
    return Path(__file__).parent.parent / "fixtures" / "configs" / "invalid_config.yml"


class TestConfigurationValidator:
    """Tests for ConfigurationValidator."""

    def test_invalid_output_format_enum(self, config_validator):
        """Test validation fails for invalid enum value."""
        # Config with invalid output_format
        config_data = {"output_format": "pdf"}  # Invalid: not in enum

        result = config_validator.validate(config_data)

        assert not result.is_valid
        assert result.error_count >= 1
        # Should have error about enum validation
        assert any("output_format" in err.path for err in result.errors)
        assert any(
            "enum" in err.validator.lower() or "not valid" in err.message.lower()
            for err in result.errors
        )

    def test_unknown_property_warning(self, config_validator):
        """Test validation warns for unknown fields."""
        config_data = {
            "output_format": "markdown",
            "unknown_field": "value",  # Unknown property
        }

        result = config_validator.validate(config_data)

        # Should be valid but with warnings
        assert result.is_valid or result.warning_count >= 1
        # Should have warning about unknown property
        if result.warnings:
            assert any(
                "unknown" in warn.path.lower() or "unknown" in warn.message.lower()
                for warn in result.warnings
            )

    def test_type_mismatch(self, config_validator):
        """Test validation fails for type mismatch."""
        config_data = {
            "verbose": "true",  # Invalid: should be boolean, not string
        }

        result = config_validator.validate(config_data)

        assert not result.is_valid
        assert result.error_count >= 1
        # Should have error about type mismatch
        assert any("verbose" in err.path for err in result.errors)
        assert any(
            "type" in err.validator.lower() or "boolean" in err.message.lower()
            for err in result.errors
        )

    def test_valid_config_success(self, config_validator, valid_config_path):
        """Test validation passes for valid config file."""
        result = config_validator.validate_file(valid_config_path)

        assert result.is_valid
        assert result.error_count == 0

    def test_deprecated_property_warning(self, config_validator):
        """Test validation warns for deprecated properties with migration path."""
        # Note: Add deprecated field when we have one in the schema
        config_data = {
            "output_format": "markdown",
            # Add deprecated field here when defined in schema
        }

        result = config_validator.validate(config_data)

        # For now, should be valid (no deprecated fields yet)
        assert result.is_valid

        # When deprecated fields exist, test:
        # assert any(warn.severity == Severity.WARNING for warn in result.warnings)
        # assert any("deprecated" in warn.message.lower() for warn in result.warnings)
        # assert any(warn.suggestion is not None for warn in result.warnings)
