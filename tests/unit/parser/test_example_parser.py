"""
Tests for ExampleParser - Extract @example...@end blocks from documentation comments.

TDD RED Phase: Write tests first before implementation.
Tests cover:
- Basic @example...@end block extraction
- Language detection from @example annotation
- Multiline code preservation
- Multiple examples in one file
- Examples across multiple files
- Error handling for malformed blocks
"""

from pathlib import Path
from typing import Protocol

import pytest

from ansibledoctor.models.example import Example


class ExampleParserProtocol(Protocol):
    """Protocol defining the interface for ExampleParser."""

    def parse_file(self, file_path: Path) -> list[Example]:
        """Extract examples from a single file."""
        ...

    def parse_directory(self, directory: Path) -> list[Example]:
        """Extract examples from all files in a directory recursively."""
        ...

    def parse_role(self, role_path: Path) -> list[Example]:
        """Extract examples from entire role directory."""
        ...


# RED Phase: Tests will fail until ExampleParser is implemented
class TestExampleParserBasicExtraction:
    """Test basic @example block extraction."""

    def test_extract_simple_example_block(self, tmp_path: Path):
        """Should extract basic @example...@end block with title and code."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "tasks" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""---
# @example Basic usage
# ```yaml
# - name: Example task
#   debug:
#     msg: "Hello"
# ```
# @end

- name: Real task
  debug:
    msg: "World"
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 1
        assert examples[0].title == "Basic usage"
        assert "- name: Example task" in examples[0].code
        assert examples[0].language == "yaml"

    def test_extract_example_with_description(self, tmp_path: Path):
        """Should extract example with title and description."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "README.md"
        file_path.write_text("""# Role Documentation

<!-- @example Deploy application
This example shows how to deploy the application with custom configuration.
-->
```yaml
- name: Deploy with config
  include_role:
    name: myapp
  vars:
    app_config: /etc/myapp.conf
```
<!-- @end -->
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 1
        assert examples[0].title == "Deploy application"
        assert "This example shows how to deploy" in examples[0].description
        assert "include_role" in examples[0].code

    def test_preserve_code_indentation(self, tmp_path: Path):
        """Should preserve exact code indentation and formatting."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "vars" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""---
# @example Complex nested structure
# myapp_config:
#   database:
#     host: localhost
#     port: 5432
#   cache:
#     enabled: true
# @end
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 1
        # Verify indentation is preserved exactly
        assert "  database:" in examples[0].code
        assert "    host: localhost" in examples[0].code
        assert "    port: 5432" in examples[0].code


class TestExampleParserLanguageDetection:
    """Test language detection and specification."""

    def test_detect_yaml_language(self, tmp_path: Path):
        """Should detect yaml language from file extension."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "defaults" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""---
# @example Default variables
# myapp_version: "1.0.0"
# @end
""")

        examples = parser.parse_file(file_path)

        assert examples[0].language == "yaml"

    def test_detect_python_language(self, tmp_path: Path):
        """Should detect python language from file extension."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "library" / "custom_module.py"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""#!/usr/bin/python

# @example Using custom module
# - name: Run custom module
#   custom_module:
#     param: value
# @end

def main():
    pass
""")

        examples = parser.parse_file(file_path)

        assert examples[0].language == "python"

    def test_detect_jinja2_language(self, tmp_path: Path):
        """Should detect jinja2 language from file extension."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "templates" / "config.j2"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""# @example Template usage
# server_name: {{ ansible_hostname }}
# server_port: {{ app_port | default(8080) }}
# @end

server {
    listen {{ app_port | default(8080) }};
}
""")

        examples = parser.parse_file(file_path)

        assert examples[0].language == "jinja2"

    def test_explicit_language_specification(self, tmp_path: Path):
        """Should allow explicit language specification in annotation."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "README.md"
        file_path.write_text("""# Documentation

<!-- @example:bash Shell script example -->
```bash
#!/bin/bash
ansible-playbook site.yml
```
<!-- @end -->
""")

        examples = parser.parse_file(file_path)

        assert examples[0].language == "bash"


class TestExampleParserMultipleExamples:
    """Test handling multiple examples in same file."""

    def test_extract_multiple_examples_from_file(self, tmp_path: Path):
        """Should extract all examples from file in order."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "tasks" / "main.yml"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("""---
# @example First example
# - name: Task 1
#   debug: msg="one"
# @end

- name: Real task

# @example Second example
# - name: Task 2
#   debug: msg="two"
# @end
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 2
        assert examples[0].title == "First example"
        assert examples[1].title == "Second example"
        assert "Task 1" in examples[0].code
        assert "Task 2" in examples[1].code


class TestExampleParserDirectoryScanning:
    """Test recursive directory scanning for examples."""

    def test_scan_directory_recursively(self, tmp_path: Path):
        """Should find examples in all subdirectories."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        
        # Create examples in different directories
        (tmp_path / "tasks").mkdir()
        (tmp_path / "tasks" / "main.yml").write_text("""
# @example Task example
# - name: Example
# @end
""")
        
        (tmp_path / "handlers").mkdir()
        (tmp_path / "handlers" / "main.yml").write_text("""
# @example Handler example
# - name: Handler
# @end
""")

        examples = parser.parse_directory(tmp_path)

        assert len(examples) == 2
        titles = {ex.title for ex in examples}
        assert "Task example" in titles
        assert "Handler example" in titles

    def test_filter_relevant_file_types(self, tmp_path: Path):
        """Should only scan relevant file types (.yml, .py, .j2, .md)."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        
        # Create example in .txt file (should be ignored)
        (tmp_path / "notes.txt").write_text("""
# @example Should be ignored
# - name: Task
# @end
""")
        
        # Create example in .yml file (should be found)
        (tmp_path / "tasks.yml").write_text("""
# @example Should be found
# - name: Task
# @end
""")

        examples = parser.parse_directory(tmp_path)

        assert len(examples) == 1
        assert examples[0].title == "Should be found"


class TestExampleParserRoleScanning:
    """Test parsing entire role directory."""

    def test_parse_role_returns_all_examples(self, tmp_path: Path):
        """Should aggregate examples from entire role structure."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        role_path = tmp_path / "my_role"
        
        # Create realistic role structure with examples
        (role_path / "tasks").mkdir(parents=True)
        (role_path / "tasks" / "main.yml").write_text("""
# @example Task example
# - name: Example task
# @end
""")
        
        (role_path / "defaults").mkdir()
        (role_path / "defaults" / "main.yml").write_text("""
# @example Default vars
# myvar: value
# @end
""")
        
        (role_path / "README.md").write_text("""
<!-- @example README example -->
```
Usage example
```
<!-- @end -->
""")

        examples = parser.parse_role(role_path)

        assert len(examples) == 3
        titles = {ex.title for ex in examples}
        assert "Task example" in titles
        assert "Default vars" in titles
        assert "README example" in titles


class TestExampleParserErrorHandling:
    """Test error handling for malformed examples."""

    def test_handle_missing_end_marker(self, tmp_path: Path):
        """Should handle @example without @end gracefully."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @example Incomplete example
# - name: Task
# (missing @end marker)
""")

        # Should not raise exception
        examples = parser.parse_file(file_path)

        # Either extract what's available or skip incomplete block
        # Both behaviors are acceptable, test implementation choice
        assert isinstance(examples, list)

    def test_handle_empty_example_block(self, tmp_path: Path):
        """Should handle empty @example blocks."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @example Empty example
# @end
""")

        examples = parser.parse_file(file_path)

        # Should either skip empty or create with empty code
        if len(examples) == 1:
            assert examples[0].title == "Empty example"
            assert examples[0].code == ""

    def test_handle_nonexistent_file(self, tmp_path: Path):
        """Should return empty list for nonexistent file."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        nonexistent = tmp_path / "does_not_exist.yml"

        examples = parser.parse_file(nonexistent)

        assert examples == []

    def test_handle_binary_file(self, tmp_path: Path):
        """Should skip binary files gracefully."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        binary_file = tmp_path / "image.png"
        binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        examples = parser.parse_file(binary_file)

        assert examples == []


class TestExampleParserEdgeCases:
    """Test edge cases and special scenarios."""

    def test_example_with_special_characters(self, tmp_path: Path):
        """Should handle examples with special characters."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @example Example with $pecial ch@rs & symbols!
# - name: Task with {{ jinja }}
#   command: echo "quoted 'string'"
# @end
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 1
        assert "{{ jinja }}" in examples[0].code
        assert '"quoted \'string\'"' in examples[0].code

    def test_nested_comment_markers(self, tmp_path: Path):
        """Should handle nested comment markers in code."""
        from ansibledoctor.parser.example_parser import ExampleParser

        parser = ExampleParser()
        file_path = tmp_path / "test.yml"
        file_path.write_text("""
# @example Example with nested comments
# - name: Task
#   # This is a comment in the example code
#   debug: msg="test"
# @end
""")

        examples = parser.parse_file(file_path)

        assert len(examples) == 1
        # Comment in example should be preserved as part of code
        assert "# This is a comment" in examples[0].code
