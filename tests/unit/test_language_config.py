import pytest
from pydantic import ValidationError

from ansibledoctor.config.language import LanguageConfig


def test_language_config_defaults():
    cfg = LanguageConfig()
    assert cfg.default == "en"
    assert cfg.fallback == "en"
    assert cfg.enabled == ["en"]
    assert cfg.detect_system is False


def test_language_config_enabled_list_valid():
    cfg = LanguageConfig(enabled=["en", "fr"])
    assert cfg.enabled == ["en", "fr"]


def test_language_config_invalid_codes_error():
    with pytest.raises(ValidationError):
        LanguageConfig(default="eng")

    with pytest.raises(ValidationError):
        LanguageConfig(enabled=["en", "invalid"])  # invalid code in list


def test_language_config_valid_custom():
    c = LanguageConfig(default="fr", enabled=["en", "fr"], fallback="en", detect_system=True)
    assert c.default == "fr"
    assert c.fallback == "en"
    assert set(c.enabled) == {"en", "fr"}
    assert c.detect_system is True
