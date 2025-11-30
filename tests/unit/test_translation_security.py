import os
from pathlib import Path

from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


def test_yaml_loader_safe_tag(monkeypatch, tmp_path: Path):
    # Monkeypatch os.system to detect if it would be invoked
    called = {"flag": False}

    def fake_system(cmd):
        called["flag"] = True
        return 0

    monkeypatch.setattr(os, "system", fake_system)

    yaml_file = tmp_path / "danger.yml"
    # Attempt to load a YAML file with a python object apply tag which could
    # execute system commands if loaded unsafely. Ensure our loader doesn't
    # execute arbitrary code.
    yaml_file.write_text(
        """
danger: !!python/object/apply:os.system ['echo danger']
""",
        encoding="utf-8",
    )

    loader = RuamelYAMLLoader()
    # If loader was unsafe, os.system would be called. We just assert it is not called.
    loaded = loader.load_file(yaml_file)
    assert isinstance(loaded, dict)
    # No code executed
    assert called["flag"] is False


def test_translation_formatting_safe(tmp_path: Path):
    # Ensure that simple translation formatting with kwargs doesn't allow
    # arbitrary attribute or code execution; format should safely substitute.
    from ansibledoctor.translation.provider import TranslationProvider

    translations = {"hello": "Hello {name}"}
    provider = TranslationProvider(translations, lang="en")
    assert provider.t("hello", name="World") == "Hello World"

    # When formatting has placeholders for fields not provided, return key or default
    assert provider.t("missing", default="DEFAULT") == "DEFAULT"
