from pathlib import Path

from ansibledoctor.parser.playbook_analyzer import PlaybookAnalyzer
from ansibledoctor.parser.project_parser import ProjectParser


def test_playbook_analyzer_basic_inline_tasks(tmp_path: Path):
    # Create a project with a simple playbook with inline tasks
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    # Create roles
    roles_dir = project_dir / "roles"
    roles_dir.mkdir()
    (roles_dir / "webserver").mkdir(parents=True)

    # Create playbook file
    playbooks_dir = project_dir / "playbooks"
    playbooks_dir.mkdir()
    pb = playbooks_dir / "site.yml"
    pb.write_text(
        """
- name: Site
  hosts: webservers
  tasks:
    - name: Ensure package
      apt:
        name: httpd
""",
        encoding="utf-8",
    )

    parser = ProjectParser()
    project = parser.parse(str(project_dir))
    analyzer = PlaybookAnalyzer(project)
    result = analyzer.analyze_playbook("site")
    assert "graph TD" in result["mermaid"]
    assert "task0" in result["mermaid"] or "task_" in result["mermaid"]


def test_playbook_analyzer_expands_role_tasks(tmp_path: Path):
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    roles_dir = project_dir / "roles"
    roles_dir.mkdir(parents=True)
    web = roles_dir / "webserver"
    web.mkdir(parents=True)
    tasks_dir = web / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "main.yml").write_text(
        """
- name: role set up
  shell: echo hi
""",
        encoding="utf-8",
    )

    playbooks_dir = project_dir / "playbooks"
    playbooks_dir.mkdir()
    pb = playbooks_dir / "site.yml"
    pb.write_text(
        """
- name: Site
  hosts: web
  roles:
    - webserver
""",
        encoding="utf-8",
    )

    parser = ProjectParser()
    project = parser.parse(str(project_dir))
    analyzer = PlaybookAnalyzer(project)
    result = analyzer.analyze_playbook("site")
    # Should include mermaid node for role 'webserver' and its role_task
    assert "role: webserver" in result["mermaid"]
    assert "role_task" in result["mermaid"]
