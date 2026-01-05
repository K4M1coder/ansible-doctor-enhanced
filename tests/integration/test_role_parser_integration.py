"""
Integration tests for complete role parsing with handlers and existing docs.

Tests end-to-end role parsing including:
- Metadata extraction
- Variable extraction
- Task parsing
- Handler parsing
- Existing documentation extraction
"""

import json
from pathlib import Path

import pytest

from ansibledoctor.cli import _parse_single_role
from ansibledoctor.parser import RuamelYAMLLoader


@pytest.fixture
def role_with_docs(tmp_path: Path) -> Path:
    """Create a complete test role with handlers and documentation."""
    role_path = tmp_path / "test_role"
    role_path.mkdir()

    # Create meta/main.yml
    (role_path / "meta").mkdir()
    (role_path / "meta" / "main.yml").write_text(
        """---
galaxy_info:
  author: Test Author
  description: A test role with comprehensive documentation
  company: Test Company
  license: MIT
  min_ansible_version: "2.9"
  platforms:
    - name: Ubuntu
      versions:
        - focal
        - jammy
  galaxy_tags:
    - test
    - demo

dependencies:
  - role: common
    vars:
      common_var: value
"""
    )

    # Create defaults/main.yml
    (role_path / "defaults").mkdir()
    (role_path / "defaults" / "main.yml").write_text(
        """---
# @var test_port:description: Port for test service
# @var test_port:type: int
test_port: 8080

# @var test_enabled:description: Enable test service
test_enabled: true
"""
    )

    # Create vars/main.yml
    (role_path / "vars").mkdir()
    (role_path / "vars" / "main.yml").write_text(
        """---
# @var internal_var:description: Internal configuration
internal_var: "internal_value"
"""
    )

    # Create tasks/main.yml
    (role_path / "tasks").mkdir()
    (role_path / "tasks" / "main.yml").write_text(
        """---
- name: Install test package
  apt:
    name: test-package
    state: present
  tags:
    - installation
    - packages

- name: Configure test service
  template:
    src: test.conf.j2
    dest: /etc/test/test.conf
  notify: restart test service
  tags:
    - configuration
"""
    )

    # Create handlers/main.yml
    (role_path / "handlers").mkdir()
    (role_path / "handlers" / "main.yml").write_text(
        """---
- name: restart test service
  systemd:
    name: test
    state: restarted
  tags:
    - restart
    - service
  listen: service config changed

- name: reload test service
  systemd:
    name: test
    state: reloaded
  tags:
    - reload
"""
    )

    # Create README.md
    (role_path / "README.md").write_text(
        """# Test Role

A comprehensive test role for ansible-doctor-enhanced.

## Features

- Package installation
- Service configuration
- Handler support

## Requirements

- Ansible 2.9+
- Ubuntu 20.04 or 22.04
"""
    )

    # Create CHANGELOG.md
    (role_path / "CHANGELOG.md").write_text(
        """# Changelog

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Package installation
- Service configuration
"""
    )

    # Create CONTRIBUTING.md
    (role_path / "CONTRIBUTING.md").write_text(
        """# Contributing Guide

Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request
"""
    )

    # Create LICENSE
    (role_path / "LICENSE").write_text(
        """MIT License

Copyright (c) 2025 Test Author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    )

    # Create templates directory with sample template
    (role_path / "templates").mkdir()
    (role_path / "templates" / "test.conf.j2").write_text(
        """# Test configuration
port={{ test_port }}
enabled={{ test_enabled }}
"""
    )

    # Create files directory with static files
    (role_path / "files").mkdir()
    (role_path / "files" / "example.txt").write_text("Example static file")

    return role_path


def test_complete_role_parsing(role_with_docs: Path) -> None:
    """Test end-to-end parsing of a role with all components."""
    yaml_loader = RuamelYAMLLoader()
    result = _parse_single_role(role_with_docs, yaml_loader)

    # Verify result structure
    assert isinstance(result, dict)
    assert "metadata" in result
    assert "variables" in result
    assert "tags" in result
    assert "handlers" in result
    assert "existing_docs" in result

    # Verify metadata
    metadata = result["metadata"]
    assert metadata["author"] == "Test Author"
    assert metadata["license"] == "MIT"
    assert metadata["description"] == "A test role with comprehensive documentation"

    # Verify variables
    variables = result["variables"]
    assert len(variables) >= 3
    var_names = {v["name"] for v in variables}
    assert "test_port" in var_names
    assert "test_enabled" in var_names
    assert "internal_var" in var_names

    # Verify tags
    tags = result["tags"]
    assert len(tags) >= 2
    tag_names = {t["name"] for t in tags}
    assert "installation" in tag_names
    assert "configuration" in tag_names

    # Verify handlers
    handlers = result["handlers"]
    assert len(handlers) == 2
    handler_names = {h["name"] for h in handlers}
    assert "restart test service" in handler_names
    assert "reload test service" in handler_names

    # Check handler details
    restart_handler = next(h for h in handlers if h["name"] == "restart test service")
    assert "restart" in restart_handler["tags"]
    assert "service" in restart_handler["tags"]
    assert "service config changed" in restart_handler["listen"]

    # Verify existing docs
    existing_docs = result["existing_docs"]
    assert existing_docs["readme_content"] is not None
    assert "Test Role" in existing_docs["readme_content"]
    assert existing_docs["readme_format"] == "markdown"

    assert existing_docs["changelog_content"] is not None
    assert "[1.0.0]" in existing_docs["changelog_content"]

    assert existing_docs["contributing_content"] is not None
    assert "Contributing Guide" in existing_docs["contributing_content"]

    assert existing_docs["license_content"] is not None
    assert "MIT License" in existing_docs["license_content"]
    assert existing_docs["license_type"] == "MIT"

    # Verify templates and files lists
    assert "test.conf.j2" in existing_docs["templates_list"]
    assert "example.txt" in existing_docs["files_list"]


def test_role_json_serialization(role_with_docs: Path) -> None:
    """Test that parsed role can be serialized to JSON."""
    yaml_loader = RuamelYAMLLoader()
    result = _parse_single_role(role_with_docs, yaml_loader)

    # Attempt JSON serialization
    json_output = json.dumps(result, indent=2)
    assert json_output is not None
    assert len(json_output) > 100

    # Verify JSON can be deserialized
    parsed = json.loads(json_output)
    assert parsed["metadata"]["author"] == "Test Author"
    assert len(parsed["handlers"]) == 2
    assert parsed["existing_docs"]["license_type"] == "MIT"


def test_role_with_missing_handlers(tmp_path: Path) -> None:
    """Test role parsing when handlers directory is missing."""
    role_path = tmp_path / "role_no_handlers"
    role_path.mkdir()

    # Create minimal role structure
    (role_path / "meta").mkdir()
    (role_path / "meta" / "main.yml").write_text(
        """---
galaxy_info:
  author: Test
  description: Minimal role
  license: MIT
"""
    )

    (role_path / "tasks").mkdir()
    (role_path / "tasks" / "main.yml").write_text(
        """---
- name: Test task
  debug:
    msg: test
"""
    )

    yaml_loader = RuamelYAMLLoader()
    result = _parse_single_role(role_path, yaml_loader)

    # Handlers should be empty list, not error
    assert "handlers" in result
    assert result["handlers"] == []


def test_role_with_missing_docs(tmp_path: Path) -> None:
    """Test role parsing when documentation files are missing."""
    role_path = tmp_path / "role_no_docs"
    role_path.mkdir()

    # Create minimal role structure
    (role_path / "meta").mkdir()
    (role_path / "meta" / "main.yml").write_text(
        """---
galaxy_info:
  author: Test
  description: Minimal role
  license: MIT
"""
    )

    yaml_loader = RuamelYAMLLoader()
    result = _parse_single_role(role_path, yaml_loader)

    # Existing docs should have None values for missing files
    existing_docs = result["existing_docs"]
    assert existing_docs["readme_content"] is None
    assert existing_docs["changelog_content"] is None
    assert existing_docs["contributing_content"] is None
    assert existing_docs["license_content"] is None
    assert existing_docs["license_type"] is None  # No LICENSE file, so None not "Unknown"
    assert existing_docs["templates_list"] == []
    assert existing_docs["files_list"] == []


def test_handler_with_include(tmp_path: Path) -> None:
    """Test handler parsing with include_tasks."""
    role_path = tmp_path / "role_handler_include"
    role_path.mkdir()

    # Create meta
    (role_path / "meta").mkdir()
    (role_path / "meta" / "main.yml").write_text(
        """---
galaxy_info:
  author: Test
  description: Handler include test
  license: MIT
"""
    )

    # Create handlers with include
    (role_path / "handlers").mkdir()
    (role_path / "handlers" / "main.yml").write_text(
        """---
- name: main handler
  debug:
    msg: main
  tags: [main]

- include_tasks: extra.yml
"""
    )

    (role_path / "handlers" / "extra.yml").write_text(
        """---
- name: included handler
  debug:
    msg: included
  tags: [included]
"""
    )

    yaml_loader = RuamelYAMLLoader()
    result = _parse_single_role(role_path, yaml_loader)

    handlers = result["handlers"]
    assert len(handlers) == 2
    handler_names = {h["name"] for h in handlers}
    assert "main handler" in handler_names
    assert "included handler" in handler_names


def test_license_type_detection(tmp_path: Path) -> None:
    """Test detection of various license types."""
    test_cases = [
        ("Apache-2.0", "Apache License\nVersion 2.0"),
        ("GPL-3.0", "GNU GENERAL PUBLIC LICENSE\nVersion 3"),
        ("BSD-3-Clause", "BSD 3-Clause License"),
        ("Unknown", "Custom License Agreement"),
    ]

    for expected_type, license_text in test_cases:
        role_path = tmp_path / f"role_{expected_type}"
        role_path.mkdir()

        # Create minimal role
        (role_path / "meta").mkdir()
        (role_path / "meta" / "main.yml").write_text(
            """---
galaxy_info:
  author: Test
  description: License test
  license: MIT
"""
        )

        # Create LICENSE with specific text
        (role_path / "LICENSE").write_text(license_text)

        yaml_loader = RuamelYAMLLoader()
        result = _parse_single_role(role_path, yaml_loader)

        assert result["existing_docs"]["license_type"] == expected_type
