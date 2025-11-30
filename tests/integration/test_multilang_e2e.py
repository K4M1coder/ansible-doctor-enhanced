"""End-to-end integration test for MultiLanguageGenerator.

This test ensures that generating a sample project with a project-local
translation file produces localized READMEs for `en`, `fr`, and `de`.
"""

from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project_with_files(tmp_path: Path, name: str = "myproj") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    # Minimal roles/collections structure
    roles_dir = proj_dir / "roles" / "webserver"
    roles_dir.mkdir(parents=True)
    (roles_dir / "tasks").mkdir()
    (roles_dir / "tasks" / "main.yml").write_text('- name: do nothing\n  debug: msg="noop"\n')

    collections_dir = proj_dir / "collections" / "my_collection"
    collections_dir.mkdir(parents=True)
    (collections_dir / "roles").mkdir(parents=True)

    # Write project-local translation files for en/fr/de
    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "en.yml").write_text(
        'project.title: "My Project"\nroles.header: "Roles"\n', encoding="utf-8"
    )
    (translations_dir / "fr.yml").write_text(
        'project.title: "Mon Projet"\nroles.header: "Rôles"\n', encoding="utf-8"
    )
    (translations_dir / "de.yml").write_text(
        'project.title: "Mein Projekt"\nroles.header: "Rollen"\n', encoding="utf-8"
    )

    roles = [RoleInfo(name="webserver", path=str(roles_dir))]
    collections = [CollectionInfo(name="my_collection", path=str(collections_dir))]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_multilang_e2e(tmp_path: Path):
    p = make_project_with_files(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)
    gen.generate(p, ["en", "fr", "de"])  # Generate for three languages

    # Check README exists and content localized
    out_en = Path(p.path) / "docs" / "lang" / "en" / "ansibleproject_my-project" / "README.md"
    out_fr = Path(p.path) / "docs" / "lang" / "fr" / "ansibleproject_my-project" / "README.md"
    out_de = Path(p.path) / "docs" / "lang" / "de" / "ansibleproject_my-project" / "README.md"

    assert out_en.exists()
    assert out_fr.exists()
    assert out_de.exists()

    assert out_en.read_text(encoding="utf-8").startswith("# My Project"), out_en.read_text(
        encoding="utf-8"
    )
    assert out_fr.read_text(encoding="utf-8").startswith("# Mon Projet"), out_fr.read_text(
        encoding="utf-8"
    )
    assert out_de.read_text(encoding="utf-8").startswith("# Mein Projekt"), out_de.read_text(
        encoding="utf-8"
    )
