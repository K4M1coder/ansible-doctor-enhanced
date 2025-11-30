from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project_with_files(tmp_path: Path, name: str = "concurrency_project") -> Project:
    proj_dir = tmp_path / name
    proj_dir.mkdir()

    roles_dir = proj_dir / "roles" / "webserver"
    roles_dir.mkdir(parents=True)
    (roles_dir / "tasks").mkdir()
    (roles_dir / "tasks" / "main.yml").write_text('- name: noop\n  debug: msg="noop"\n')

    collections_dir = proj_dir / "collections" / "my_collection"
    collections_dir.mkdir(parents=True)
    (collections_dir / "roles").mkdir(parents=True)

    # Write project-local translation files for en/fr/de
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
    collections = [CollectionInfo(name="my_collection", path=str(collections_dir))]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def run_gen(gen, p, lang):
    gen.generate(p, [lang])
    # return path to generated README
    return Path(p.path) / "docs" / "lang" / lang / "ansibleproject_my-project" / "README.md"


def test_i18n_concurrency(tmp_path: Path):
    p = make_project_with_files(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)

    languages = ["en", "fr", "de"]
    results = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(run_gen, gen, p, lang) for lang in languages]
        for future in as_completed(futures):
            # Verify each future completed successfully and file exists
            readme = future.result()
            assert readme.exists()
            txt = readme.read_text(encoding="utf-8")
            assert "Project" in txt or "Projet" in txt or "Mein Projekt" in txt
            results.append(readme)

    # Ensure at least one README per language exists
    assert (Path(p.path) / "docs" / "lang" / "en").exists()
    assert (Path(p.path) / "docs" / "lang" / "fr").exists()
    assert (Path(p.path) / "docs" / "lang" / "de").exists()
