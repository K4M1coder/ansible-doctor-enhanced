import pytest
from ansibledoctor.parser.project_parser import ProjectParser
from ansibledoctor.models.project import Project


def test_project_parser_empty_dir(tmp_path):
    parser = ProjectParser()
    project = parser.parse(tmp_path)

    assert isinstance(project, Project)
    assert project.name == '' or project.name is None
    assert project.roles == []
    assert project.collections == []
    assert project.playbooks == []
