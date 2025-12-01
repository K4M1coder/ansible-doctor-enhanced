"""Performance tests for project documentation generation."""

import time
from pathlib import Path

import pytest

from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.generator.output_format import OutputFormat
from ansibledoctor.models.project import CollectionInfo, Project, RoleInfo


def make_test_project(tmp_path: Path, num_roles: int = 5, num_collections: int = 2) -> Project:
    """Create a test project with specified number of roles and collections."""
    proj_dir = tmp_path / "test_project"
    proj_dir.mkdir()
    
    # Create ansible.cfg
    (proj_dir / "ansible.cfg").write_text("""[defaults]
inventory = inventory
roles_path = roles
""")
    
    # Create roles
    roles = []
    for i in range(num_roles):
        role_name = f"role_{i}"
        role_dir = proj_dir / "roles" / role_name
        role_dir.mkdir(parents=True)
        
        # Create basic role structure
        (role_dir / "tasks").mkdir()
        (role_dir / "tasks" / "main.yml").write_text(f"""---
- name: Task for {role_name}
  debug:
    msg: "Running {role_name}"
""")
        
        (role_dir / "defaults").mkdir()
        (role_dir / "defaults" / "main.yml").write_text(f"""---
# @var {role_name}_var: Default value
{role_name}_var: "default"
# @var {role_name}_enabled: Enable {role_name}
{role_name}_enabled: true
""")
        
        (role_dir / "meta").mkdir()
        (role_dir / "meta" / "main.yml").write_text(f"""---
galaxy_info:
  author: test
  description: Test role {role_name}
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
""")
        
        roles.append(RoleInfo(name=role_name, path=str(role_dir)))
    
    # Create collections
    collections = []
    for i in range(num_collections):
        coll_name = f"collection_{i}"
        coll_dir = proj_dir / "collections" / f"test_namespace.{coll_name}"
        coll_dir.mkdir(parents=True)
        
        (coll_dir / "galaxy.yml").write_text(f"""---
namespace: test_namespace
name: {coll_name}
version: 1.0.0
readme: README.md
authors:
  - Test Author
description: Test collection {coll_name}
""")
        
        collections.append(CollectionInfo(
            name=f"test_namespace.{coll_name}",
            path=str(coll_dir)
        ))
    
    # Create inventory
    inv_dir = proj_dir / "inventory"
    inv_dir.mkdir()
    (inv_dir / "hosts.yml").write_text("""---
all:
  hosts:
    localhost:
      ansible_connection: local
  children:
    webservers:
      hosts:
        web1:
        web2:
    dbservers:
      hosts:
        db1:
""")
    
    return Project(
        name="Test Project",
        path=str(proj_dir),
        roles=roles,
        collections=collections,
    )


def test_project_generation_performance_small(tmp_path: Path):
    """Test that small project (5 roles) generates in under 2 seconds."""
    project = make_test_project(tmp_path, num_roles=5, num_collections=2)
    generator = ProjectDocumentationGenerator(project)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    start = time.perf_counter()
    generator.generate(format=OutputFormat.MARKDOWN.value, output_dir=output_dir)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 2.0, f"Small project generation took too long: {elapsed:.2f}s"
    assert (output_dir / "README.md").exists()


def test_project_generation_performance_medium(tmp_path: Path):
    """Test that medium project (15 roles) generates in under 5 seconds."""
    project = make_test_project(tmp_path, num_roles=15, num_collections=3)
    generator = ProjectDocumentationGenerator(project)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    start = time.perf_counter()
    generator.generate(format=OutputFormat.MARKDOWN.value, output_dir=output_dir)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 5.0, f"Medium project generation took too long: {elapsed:.2f}s"


def test_project_generation_performance_large(tmp_path: Path):
    """Test that large project (30 roles) generates in under 10 seconds."""
    project = make_test_project(tmp_path, num_roles=30, num_collections=5)
    generator = ProjectDocumentationGenerator(project)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    start = time.perf_counter()
    generator.generate(format=OutputFormat.MARKDOWN.value, output_dir=output_dir)
    elapsed = time.perf_counter() - start
    
    assert elapsed < 10.0, f"Large project generation took too long: {elapsed:.2f}s"


def test_project_generation_all_formats_performance(tmp_path: Path):
    """Test that generating all formats for typical project is under 10 seconds total."""
    project = make_test_project(tmp_path, num_roles=10, num_collections=2)
    
    total_time = 0.0
    for fmt in [OutputFormat.MARKDOWN, OutputFormat.HTML, OutputFormat.RST]:
        generator = ProjectDocumentationGenerator(project)
        output_dir = tmp_path / f"output_{fmt.value}"
        output_dir.mkdir()
        
        start = time.perf_counter()
        generator.generate(format=fmt.value, output_dir=output_dir)
        elapsed = time.perf_counter() - start
        total_time += elapsed
    
    assert total_time < 10.0, f"All formats generation took too long: {total_time:.2f}s"


def test_project_generation_performance_stress(tmp_path: Path):
    """Stress test: Large project with 50 roles should still complete in reasonable time."""
    project = make_test_project(tmp_path, num_roles=50, num_collections=10)
    generator = ProjectDocumentationGenerator(project)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    start = time.perf_counter()
    generator.generate(format=OutputFormat.MARKDOWN.value, output_dir=output_dir)
    elapsed = time.perf_counter() - start
    
    # More generous timeout for stress test
    assert elapsed < 30.0, f"Stress test took too long: {elapsed:.2f}s"
