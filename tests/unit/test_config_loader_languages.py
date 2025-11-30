"""Unit tests for language configuration within the config loader.

Ensures that `load_config` correctly parses `languages` nested structure and validates
it as the `LanguageConfig` Pydantic model.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from ansibledoctor.config.language import LanguageConfig
from ansibledoctor.config.loader import load_config


def test_load_config_parses_language_config(tmp_path: Path):
    config_file = tmp_path / ".ansibledoctor.yml"
    config_file.write_text(
        """
languages:
  default: fr
  enabled:
    - fr
    - en
  fallback: en
  detect_system: false
"""
    )

    cfg = load_config(config_file)

    assert cfg.languages is not None
    assert isinstance(cfg.languages, LanguageConfig)
    assert cfg.languages.default == "fr"
    assert cfg.languages.enabled == ["fr", "en"]
    assert cfg.languages.fallback == "en"
    assert cfg.languages.detect_system is False


def test_load_config_raises_on_invalid_language_code(tmp_path: Path):
    config_file = tmp_path / ".ansibledoctor.yml"
    config_file.write_text(
        """
languages:
  default: fra
  enabled:
    - fr
    - en
"""
    )

    with pytest.raises(ValidationError):
        load_config(config_file)
