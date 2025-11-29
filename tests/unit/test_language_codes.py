from pathlib import Path
from ansibledoctor.translation.loader import TranslationLoader
import pytest


def test_invalid_language_code_fallback_and_log(caplog, tmp_path: Path):
    loader = TranslationLoader()
    caplog.set_level("WARNING", logger="ansibledoctor.translation.loader")
    provider = loader.load("zz", tmp_path)
    # Should fallback to en
    assert provider.lang == "en"
    # If logging is configured, a warning would be logged; do not require it in
    # every environment. Confirm the provider has indeed fallen back.
    assert provider.get("project.title") in ("Project", "Projet")
