"""Playbook analyzer utilities

This module exposes the PlaybookAnalyzer class which parses Ansible
playbooks and constructs simple flow representations used in documentation
generation (Mermaid diagrams, node/edge lists).
"""

from pathlib import Path
from typing import Dict

from ansibledoctor.models.project import Project
from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


class PlaybookAnalyzer:
    """Analyze static playbook structure and produce flow structures.

    Minimal analyzer that can:
    - Read a playbook file, list plays, inline tasks, and roles
    - For role-based tasks, attempt to read role tasks/main.yml and include task names
    - Produce a simple Mermaid flowchart string for visualization
    """

    def __init__(self, project: Project):
        self.project = project
        self.yaml_loader = RuamelYAMLLoader()

    def analyze_playbook(self, playbook_name: str) -> Dict:
        """Return a dictionary representation including mermaid string"""
        # Accept either playbook base name (e.g. 'site') or filename 'site.yml'
        pb = next(
            (
                p
                for p in self.project.playbooks
                if p.name == playbook_name or Path(p.path).name == playbook_name
            ),
            None,
        )
        if pb is None:
            raise FileNotFoundError(f"Playbook not found: {playbook_name}")

        # Parse the playbook file for tasks if necessary
        content = self.yaml_loader.load_file(Path(pb.path))
        plays = content if isinstance(content, list) else [content]

        # Build nodes as ordered steps: play->tasks/roles->(role tasks)
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        node_index = 0

        def node_id(prefix: str, idx: int) -> str:
            return f"{prefix}{idx}"

        # Root project node
        nodes.append({"id": "project", "label": self.project.name, "type": "project"})

        # Add play node
        for i, play in enumerate(plays):
            play_label = play.get("name") if isinstance(play, dict) else f"play_{i}"
            pid = node_id("play", i)
            nodes.append({"id": pid, "label": play_label, "type": "play"})
            edges.append({"from": "project", "to": pid})

            # Collect tasks and roles in play
            if isinstance(play, dict):
                inline_tasks = play.get("tasks", [])
                if inline_tasks:
                    for ti, t in enumerate(inline_tasks):
                        if isinstance(t, dict):
                            task_name = t.get("name", f"task_{ti}")
                        else:
                            task_name = f"task_{ti}"
                        tid = node_id("task", node_index)
                        nodes.append({"id": tid, "label": task_name, "type": "task"})
                        edges.append({"from": pid, "to": tid})
                        node_index += 1
                # Roles list
                roles = play.get("roles", [])
                for r in roles:
                    if isinstance(r, dict):
                        role_name = r.get("role") or r.get("name")
                    else:
                        role_name = r
                    rid = node_id("role", node_index)
                    nodes.append({"id": rid, "label": f"role: {role_name}", "type": "role"})
                    edges.append({"from": pid, "to": rid})
                    node_index += 1

                    # find role directory in project roles
                    role_info = next(
                        (rr for rr in self.project.roles if rr.name == role_name), None
                    )
                    if role_info:
                        # Look for tasks/main.yml
                        tasks_file = Path(role_info.path) / "tasks" / "main.yml"
                        try:
                            role_tasks = self.yaml_loader.load_file(tasks_file)
                        except Exception:
                            role_tasks = None
                        if isinstance(role_tasks, list):
                            for rt_idx, rtask in enumerate(role_tasks):
                                rtask_name = (
                                    rtask.get("name")
                                    if isinstance(rtask, dict)
                                    else f"role_task_{rt_idx}"
                                )
                                rtid = node_id("role_task", node_index)
                                nodes.append({"id": rtid, "label": rtask_name, "type": "role_task"})
                                edges.append({"from": rid, "to": rtid})
                                node_index += 1

        # Build a simplistic mermaid flow string
        mermaid_lines = ["graph TD"]
        for n in nodes:
            lab = str(n["label"]).replace("'", "\\'") if n["label"] else ""
            mermaid_lines.append(f"    {n['id']}[" + lab + "]")
        for e in edges:
            mermaid_lines.append(f"    {e['from']} --> {e['to']}")

        mermaid = "\n".join(mermaid_lines)
        return {"playbook": pb.name, "mermaid": mermaid, "nodes": nodes, "edges": edges}


__all__ = ["PlaybookAnalyzer"]
