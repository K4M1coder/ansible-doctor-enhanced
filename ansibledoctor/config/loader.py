"""Configuration file loader and discovery.

Feature 003 - US1: Configuration File Support
T010-T012: find_config_file(), load_config(), merge_config()
"""

from pathlib import Path
from typing import Any, Optional

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
    Task: T010 - Config file discovery
    """
    current = start_path.resolve()

    # Walk up directory tree until filesystem root
    while True:
        # Check for .yml first (preferred)
        yml_config = current / ".ansibledoctor.yml"
        if yml_config.exists() and yml_config.is_file():
            return yml_config

        # Check for .yaml (alternate extension)
        yaml_config = current / ".ansibledoctor.yaml"
        if yaml_config.exists() and yaml_config.is_file():
            return yaml_config

        # Check if we've reached filesystem root
        parent = current.parent
        if parent == current:
            # Reached root, no config found
            return None

        current = parent


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
    Task: T011 - Config file loading and validation
    """
    # Check file exists
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load YAML content
    yaml = YAML()
    yaml.default_flow_style = False

    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.load(f)

        # Handle empty file
        if data is None:
            data = {}

        # Validate with Pydantic (let ValidationError propagate for testing)
        config = ConfigModel(**data)
        return config

    except FileNotFoundError:
        # Re-raise FileNotFoundError as-is
        raise
    except Exception as e:
        # Check if it's a Pydantic ValidationError - let it propagate
        from pydantic import ValidationError

        if isinstance(e, ValidationError):
            raise
        # Wrap YAML errors with clear message
        error_msg = str(e).lower()
        if "yaml" in error_msg or "scan" in error_msg:
            raise ConfigError(f"YAML syntax error in {config_path}: {e}") from e
        # Wrap other errors
        raise ConfigError(f"Failed to load config from {config_path}: {e}") from e


def merge_config(
    file_config: Optional[ConfigModel],
    cli_config: ConfigModel | dict[str, Any],
) -> ConfigModel:
    """Merge configuration from file and CLI with proper precedence.

    Merges configuration sources with priority: CLI > file > defaults.
    CLI arguments override file settings, file settings override defaults.

    Args:
        file_config: Configuration loaded from file (or None if not found)
        cli_config: Configuration from CLI arguments as ConfigModel or dict

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
    Task: T012 - Config merging with priority
    """
    # Start with defaults from ConfigModel
    defaults = ConfigModel()

    # Build merged dict with priority: CLI > file > defaults
    merged_data: dict[str, Any] = {}

    # Get all fields from ConfigModel
    for field_name in ConfigModel.model_fields.keys():
        # Handle both ConfigModel and dict for cli_config
        if isinstance(cli_config, dict):
            cli_value = cli_config.get(field_name)
        else:
            cli_value = getattr(cli_config, field_name, None)
        file_value = getattr(file_config, field_name, None) if file_config else None
        default_value = getattr(defaults, field_name)

        # Priority: CLI (if not None) > file (if not None/default) > default
        # Special handling for boolean 'recursive' - False is a valid CLI value
        if field_name == "recursive":
            # If CLI explicitly set recursive to True, use it
            if cli_value is True:
                merged_data[field_name] = cli_value
            # Else use file value if available
            elif file_value is not None:
                merged_data[field_name] = file_value
            # Else use default
            else:
                merged_data[field_name] = default_value
        # For exclude_patterns, default is a list - check if CLI differs from default
        elif field_name == "exclude_patterns":
            if cli_value != default_value:
                # CLI has custom patterns
                merged_data[field_name] = cli_value
            elif file_value is not None:
                # Use file patterns
                merged_data[field_name] = file_value
            else:
                # Use default
                merged_data[field_name] = default_value
        # Standard None-aware merging for other fields
        else:
            if cli_value is not None:
                merged_data[field_name] = cli_value
            elif file_value is not None:
                merged_data[field_name] = file_value
            else:
                merged_data[field_name] = default_value

    return ConfigModel(**merged_data)
