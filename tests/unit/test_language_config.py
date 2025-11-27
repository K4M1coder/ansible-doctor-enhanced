from ansibledoctor.config.language import LanguageConfig
import pytest


def test_language_config_defaults():
    c = LanguageConfig()
    assert c.default == "en"
    assert c.fallback == "en"
    assert c.enabled == ["en"]
    assert c.detect_system is False


def test_language_config_valid_custom():
    c = LanguageConfig(default="fr", enabled=["en", "fr"], fallback="en", detect_system=True)
    assert c.default == "fr"
    assert c.fallback == "en"
    assert set(c.enabled) == {"en", "fr"}
    assert c.detect_system is True


def test_language_config_invalid_code_raises():
    with pytest.raises(ValueError):
        LanguageConfig(default="eng")
    with pytest.raises(ValueError):
        LanguageConfig(enabled=["en", "french"])  # invalid code in list
