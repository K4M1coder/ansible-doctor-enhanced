from pathlib import Path

from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo


def make_project(tmp_path: Path) -> Project:
    proj_dir = tmp_path / "myproj"
    proj_dir.mkdir()
    roles = [RoleInfo(name="webserver", path=str(proj_dir / "roles" / "webserver"))]
    collections = [
        CollectionInfo(name="my_collection", path=str(proj_dir / "collections" / "my_collection"))
    ]
    return Project(name="My Project", path=str(proj_dir), roles=roles, collections=collections)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_generate_markdown_default_dir(tmp_path: Path):
    p = make_project(tmp_path)
    gen = ProjectDocumentationGenerator(p)
    output = gen.generate(format="markdown")
    assert output.exists()
    content = read_file(output)
    assert "# My Project" in content
    assert "## Roles" in content
    assert "webserver" in content
    assert "## Collections" in content
    assert "my_collection" in content


def test_generate_html_explicit_dir(tmp_path: Path):
    p = make_project(tmp_path)
    out_dir = tmp_path / "out"
    gen = ProjectDocumentationGenerator(p)
    output = gen.generate(format="html", output_dir=out_dir)
    assert output.exists()
    content = read_file(output)
    assert "<!DOCTYPE html>" in content
    assert "<h1>My Project</h1>" in content
    assert "webserver" in content
    assert "my_collection" in content


def test_generate_rst_case_insensitive(tmp_path: Path):
    p = make_project(tmp_path)
    gen = ProjectDocumentationGenerator(p)
    output = gen.generate(format="RSt")
    assert output.exists()
    content = read_file(output)
    assert "My Project" in content
    assert "Roles" in content
    assert "webserver" in content
    assert "Collections" in content
    assert "my_collection" in content


def test_generate_with_custom_template(tmp_path: Path):
    p = make_project(tmp_path)
    # create a simple Jinja2 template file
    tpl = tmp_path / "custom_template.j2"
    tpl.write_text(
        "Project: {{ project.name }} - roles: {% for r in roles %}{{ r.name }} {% endfor %}"
    )
    gen = ProjectDocumentationGenerator(p)
    output = gen.generate(format="markdown", template_path=str(tpl))
    assert output.exists()
    content = read_file(output)
    assert "Project: My Project - roles: webserver" in content


def test_generate_markdown_includes_mermaid_diagram(tmp_path: Path):
    p = make_project(tmp_path)
    gen = ProjectDocumentationGenerator(p)
    output = gen.generate(format="markdown")
    assert output.exists()
    content = read_file(output)
    assert "## Architecture" in content
    assert "```mermaid" in content
    assert "graph TD" in content
    assert "[My Project]" in content
    assert "[Roles (1)]" in content
    assert "[Collections (1)]" in content
