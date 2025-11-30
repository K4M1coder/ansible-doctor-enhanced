from pathlib import Path

from ansibledoctor.translation.loader import TranslationLoader


def test_translation_loader_package_and_project_override(tmp_path: Path):
    # Create a fake project-level translation file overriding the package translation
    proj = tmp_path / "proj"
    proj.mkdir()
    trans_dir = proj / ".ansibledoctor" / "translations"
    trans_dir.mkdir(parents=True)
    fr_file = trans_dir / "fr.yml"
    fr_file.write_text(
        """
project:
    title: 'Mon Projet'
roles:
    header: 'Rôles'
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("fr", proj)

    # Package default is available for keys not overridden
    assert provider.get("architecture.header") in ("Architecture", "Architecture")
    # Overridden key from project should be present
    assert provider.get("project.title") == "Mon Projet"
    assert provider.get("roles.header") == "Rôles"
