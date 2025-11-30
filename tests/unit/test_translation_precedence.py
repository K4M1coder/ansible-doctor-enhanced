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
    (col_trans_dir / "fr.yml").write_text(
        """
roles:
  header: 'Collection Roles'
""",
        encoding="utf-8",
    )
    # Create project-level translation overriding it
    proj_trans_dir = proj / ".ansibledoctor" / "translations"
    proj_trans_dir.mkdir(parents=True)
    (proj_trans_dir / "fr.yml").write_text(
        """
roles:
  header: 'Project Roles'
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("fr", proj)
    assert provider.get("roles.header") == "Project Roles"


def test_translation_deep_merge_preserves_nested_keys(tmp_path: Path):
    proj = make_project(tmp_path)
    # Collection-level provides nested structure with multiple keys
    col_trans_dir = proj / "collections" / "ns" / "collection1" / "translations"
    col_trans_dir.mkdir(parents=True)
    (col_trans_dir / "fr.yml").write_text(
        """
roles:
  header: 'Collection Roles'
  description: 'Roles description'
""",
        encoding="utf-8",
    )
    # Project-level only overrides header
    proj_trans_dir = proj / ".ansibledoctor" / "translations"
    proj_trans_dir.mkdir(parents=True)
    (proj_trans_dir / "fr.yml").write_text(
        """
roles:
  header: 'Project Roles'
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("fr", proj)

    # Header comes from project override
    assert provider.get("roles.header") == "Project Roles"
    # Description is preserved from collection-level because it wasn't overridden
    assert provider.get("roles.description") == "Roles description"
