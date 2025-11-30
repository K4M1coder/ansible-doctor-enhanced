from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_demo_project(tmp_path: Path, name: str = "myproj") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    roles_dir = proj_dir / "roles" / "webserver"
    roles_dir.mkdir(parents=True)
    (roles_dir / "tasks").mkdir()
    (roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')

    translations_dir = proj_dir / ".ansibledoctor" / "translations"
    translations_dir.mkdir(parents=True)
    (translations_dir / "en.yml").write_text(
        """
project:
    title: "My Project"
roles:
    header: "Roles"
""",
        encoding="utf-8",
    )
    (translations_dir / "fr.yml").write_text(
        """
project:
    title: "Mon Projet"
roles:
    header: "Rôles"
""",
        encoding="utf-8",
    )
    (translations_dir / "de.yml").write_text(
        """
project:
    title: "Mein Projekt"
roles:
    header: "Rollen"
""",
        encoding="utf-8",
    )

    roles = [RoleInfo(name="webserver", path=str(roles_dir))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_multilang_e2e_three_languages(tmp_path: Path):
    p = make_demo_project(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)
    gen.generate(p, ["en", "fr", "de"])  # generate in three languages

    # Check per-language README contains correct translations
    out_en = Path(p.path) / "docs" / "lang" / "en" / "ansibleproject_my-project" / "README.md"
    out_fr = Path(p.path) / "docs" / "lang" / "fr" / "ansibleproject_my-project" / "README.md"
    out_de = Path(p.path) / "docs" / "lang" / "de" / "ansibleproject_my-project" / "README.md"
    assert out_en.exists()
    assert out_fr.exists()
    assert out_de.exists()

    assert out_en.read_text(encoding="utf-8").startswith("# My Project")
    assert out_fr.read_text(encoding="utf-8").startswith("# Mon Projet")
    assert out_de.read_text(encoding="utf-8").startswith("# Mein Projekt")
