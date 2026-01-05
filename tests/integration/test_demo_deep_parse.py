"""Integration test for deep parsing using demo project (T335).

This integration test will parse the demo project with deep_parse=True and verify
that parsed_roles and parsed_collections are populated with detailed models.
"""

from pathlib import Path

from ansibledoctor.models.collection import AnsibleCollection
from ansibledoctor.models.role import AnsibleRole
from ansibledoctor.parser.project_parser import ProjectParser


def test_demo_project_deep_parsing():
    demo_path = Path(__file__).parent.parent.parent / "demo" / "project_demo_namespace.demo_project"
    parser = ProjectParser()
    project = parser.parse(str(demo_path), deep_parse=True)

    assert project.parsed_roles is not None
    assert any(isinstance(r, AnsibleRole) for r in project.parsed_roles)

    assert project.parsed_collections is not None
    assert any(isinstance(c, AnsibleCollection) for c in project.parsed_collections)
