from pathlib import Path
from ansibledoctor.translation.loader import TranslationLoader


def make_project(tmp_path: Path):
    proj = tmp_path / "proj"
    (proj / "collections" / "ns" / "collection1").mkdir(parents=True)
    (proj / "roles" / "webserver").mkdir(parents=True)
    return proj


def test_translation_precedence(tmp_path: Path):
    proj = make_project(tmp_path)
    # Create collection-level translation
    col_trans_dir = proj / "collections" / "ns" / "collection1" / "translations"
    col_trans_dir.mkdir(parents=True)
    (col_trans_dir / "fr.yml").write_text("roles.header: 'Collection Roles'", encoding="utf-8")
    # Create project-level translation overriding it
    proj_trans_dir = proj / ".ansibledoctor" / "translations"
    proj_trans_dir.mkdir(parents=True)
    (proj_trans_dir / "fr.yml").write_text("roles.header: 'Project Roles'", encoding="utf-8")

    loader = TranslationLoader()
    provider = loader.load("fr", proj)
    assert provider.get("roles.header") == "Project Roles"
