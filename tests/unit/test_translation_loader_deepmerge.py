from pathlib import Path

from ansibledoctor.translation.loader import TranslationLoader


def make_translation_file(path: Path, filename: str, content: str):
    p = path / filename
    p.write_text(content, encoding="utf-8")
    return p


def test_translation_loader_deepmerge(tmp_path: Path):
    proj_dir = tmp_path / "proj"
    proj_dir.mkdir()
    # Create package-level translation file (simulated under ansibledoctor/translations)
    # Simulate nested translations using nested YAML in collection/project translations
    # package default has nested 'meta.author.name' and 'meta.author.email'
    # project-local file overrides only 'meta.author.name'
    loader = TranslationLoader()

    # Create a collection-level nested translation
    coll_tr_dir = proj_dir / "collections" / "my_collection" / "translations"
    coll_tr_dir.mkdir(parents=True)
    # Add nested YAML structure
    coll_tr_file = coll_tr_dir / "en.yml"
    coll_tr_file.write_text(
        """
meta:
    author:
        name: "Collection Author"
        email: "collection@example.com"
""",
        encoding="utf-8",
    )

    # Add a project-level translation overlay that overrides name only
    tr_dir = proj_dir / ".ansibledoctor" / "translations"
    tr_dir.mkdir(parents=True)
    make_translation_file(tr_dir, "en.yml", "meta:\n  author:\n    name: 'Project Author'\n")

    provider = loader.load("en", proj_dir)
    # After loading, we should have both keys: name overridden by project, email from collection
    assert provider.get("meta.author.name") == "Project Author"
    assert provider.get("meta.author.email") == "collection@example.com"
