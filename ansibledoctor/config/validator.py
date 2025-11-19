"""Configuration validation utilities.

Feature 003 - US3: Config Discovery & Validation
T029: Config validation CLI command
"""

from pathlib import Path
from typing import Any

from ansibledoctor.config.loader import load_config
from ansibledoctor.config.models import ConfigModel
from ansibledoctor.exceptions import ConfigError


def validate_config_file(config_path: Path) -> tuple[bool, list[str]]:
    """Validate configuration file syntax and content.
    
    Loads config file and validates using Pydantic schema, collecting
    all validation errors.
    
    Args:
        config_path: Path to .ansibledoctor.yml file
        
    Returns:
        Tuple of (is_valid, list of error messages)
        
    Example:
        >>> valid, errors = validate_config_file(Path(".ansibledoctor.yml"))
        >>> if valid:
        ...     print("Config is valid!")
        ... else:
        ...     print(f"Errors: {errors}")
    
    Feature: US3 - Config Discovery & Validation
    """
    # TODO: Implement in T029
    raise NotImplementedError("T029: validate_config_file() not implemented")


def show_effective_config(config: ConfigModel) -> dict[str, Any]:
    """Show effective configuration with all defaults resolved.
    
    Converts ConfigModel to dict showing all effective settings including
    defaults for display to user.
    
    Args:
        config: ConfigModel instance
        
    Returns:
        Dictionary with all effective configuration values
        
    Example:
        >>> config = ConfigModel(output_format="html")
        >>> effective = show_effective_config(config)
        >>> effective["output_format"]
        'html'
        >>> effective["recursive"]
        False
    
    Feature: US3 - Config Discovery & Validation
    """
    # TODO: Implement in T029
    raise NotImplementedError("T029: show_effective_config() not implemented")
