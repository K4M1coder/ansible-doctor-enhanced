from pathlib import Path

from ansibledoctor.generator.multi_language import MultiLanguageGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo
from ansibledoctor.translation.loader import TranslationLoader


def make_project(tmp_path: Path) -> Project:
    proj_dir = tmp_path / "myproj"
    proj_dir.mkdir()
    roles = [RoleInfo(name="webserver", path=str(proj_dir / "roles" / "webserver"))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def test_multi_language_generation(tmp_path: Path):
    p = make_project(tmp_path)
    loader = TranslationLoader()
    gen = MultiLanguageGenerator(loader=loader)
    gen.generate(p, ["en", "fr"])  # Generate default markdown for en and fr

    out_en = Path(p.path) / "docs" / "lang" / "en" / "ansibleproject_my-project" / "README.md"
    out_fr = Path(p.path) / "docs" / "lang" / "fr" / "ansibleproject_my-project" / "README.md"
    assert out_en.exists()
    assert out_fr.exists()
