from pathlib import Path

from ansibledoctor.translation.loader import TranslationLoader


def test_loader_merges_project_fallback_over_package(tmp_path: Path):
    proj_dir = tmp_path / "myproj"
    proj_dir.mkdir()
    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "xx.yml").write_text(
        """
roles:
  header: 'Rôles-XX'
""",
        encoding="utf-8",
    )
    (translations_dir / "en.yml").write_text(
        """
project:
  title: 'My Project'
roles:
  header: 'Roles'
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("xx", proj_dir)

    assert provider.get("project.title") == "My Project"
    assert provider.get("roles.header") == "Rôles-XX"
