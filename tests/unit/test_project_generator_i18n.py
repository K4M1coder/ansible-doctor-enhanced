from pathlib import Path

from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project(tmp_path: Path) -> Project:
    proj_dir = tmp_path / "myproj_i18n"
    proj_dir.mkdir()
    roles = [RoleInfo(name="webserver", path=str(proj_dir / "roles" / "webserver"))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_generate_markdown_with_translations(tmp_path: Path):
    p = make_project(tmp_path)
    # Create project-level translation file
    trans_dir = Path(p.path) / ".ansibledoctor" / "translations"
    trans_dir.mkdir(parents=True, exist_ok=True)
    fr_file = trans_dir / "fr.yml"
    fr_file.write_text(
        """
project.title: "Mon Projet"
roles.header: "Rôles"
collections.header: "Collections"
architecture.header: "Architecture"
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("fr", Path(p.path))

    gen = ProjectDocumentationGenerator(p, translation_provider=provider)
    output = gen.generate(format="markdown")
    assert output.exists()
    content = read_file(output)
    assert "# Mon Projet" in content
    assert "## Rôles" in content
    assert "## Collections" in content


def test_generate_markdown_with_language_fallback(tmp_path: Path):
    p = make_project(tmp_path)
    # Create project-level translation file missing roles.header (should fallback to 'en')
    trans_dir = Path(p.path) / ".ansibledoctor" / "translations"
    trans_dir.mkdir(parents=True, exist_ok=True)
    fr_file = trans_dir / "fr.yml"
    fr_file.write_text(
        """
project.title: "Mon Projet"
collections.header: "Collections"
architecture.header: "Architecture"
""",
        encoding="utf-8",
    )

    loader = TranslationLoader()
    provider = loader.load("fr", Path(p.path))

    gen = ProjectDocumentationGenerator(p, translation_provider=provider)
    output = gen.generate(format="markdown")
    assert output.exists()
    content = read_file(output)
    # roles.header should fallback to package 'fr' translations where present
    assert "## Rôles" in content
