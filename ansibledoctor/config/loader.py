"""Configuration file loader and discovery.

Feature 003 - US1: Configuration File Support
T010-T012: find_config_file(), load_config(), merge_config()
"""

from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

from ansibledoctor.config.models import ConfigModel
from ansibledoctor.exceptions import ConfigError


def find_config_file(start_path: Path) -> Optional[Path]:
    """Find .ansibledoctor.yml config file in current or parent directories.
    
    Searches for .ansibledoctor.yml starting from start_path and walking up
    the directory tree until found or reaching filesystem root.
    
    Args:
        start_path: Starting directory path for search
        
    Returns:
        Path to config file if found, None otherwise
        
    Example:
        >>> config_path = find_config_file(Path("/project/roles/nginx"))
        >>> config_path
        Path("/project/.ansibledoctor.yml")
    
    Feature: US1 - Config File Support
    """
    # TODO: Implement in T010
    raise NotImplementedError("T010: find_config_file() not implemented")


def load_config(config_path: Path) -> ConfigModel:
    """Load and validate configuration from YAML file.
    
    Reads .ansibledoctor.yml file, parses YAML content, and validates
    using ConfigModel Pydantic schema.
    
    Args:
        config_path: Path to .ansibledoctor.yml file
        
    Returns:
        Validated ConfigModel instance
        
    Raises:
        ConfigError: If file cannot be read or validation fails
        
    Example:
        >>> config = load_config(Path(".ansibledoctor.yml"))
        >>> config.output_format
        'html'
    
    Feature: US1 - Config File Support
    """
    # TODO: Implement in T011
    raise NotImplementedError("T011: load_config() not implemented")


def merge_config(
    file_config: Optional[ConfigModel],
    cli_config: dict,
) -> ConfigModel:
    """Merge configuration from file and CLI with proper precedence.
    
    Merges configuration sources with priority: CLI > file > defaults.
    CLI arguments override file settings, file settings override defaults.
    
    Args:
        file_config: Configuration loaded from file (or None if not found)
        cli_config: Configuration from CLI arguments as dict
        
    Returns:
        Merged ConfigModel with proper precedence applied
        
    Example:
        >>> file_cfg = ConfigModel(output_format="html")
        >>> cli_cfg = {"output": "custom.html"}
        >>> merged = merge_config(file_cfg, cli_cfg)
        >>> merged.output_format  # from file
        'html'
        >>> merged.output  # from CLI
        'custom.html'
    
    Feature: US1 - Config File Support
    """
    # TODO: Implement in T012
    raise NotImplementedError("T012: merge_config() not implemented")
