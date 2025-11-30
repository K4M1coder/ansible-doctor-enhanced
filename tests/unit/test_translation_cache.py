from pathlib import Path

from ansibledoctor.translation.loader import TranslationLoader


def test_translation_loader_caching(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    loader = TranslationLoader()
    p1 = loader.load("en", proj)
    p2 = loader.load("en", proj)
    assert p1 is p2
