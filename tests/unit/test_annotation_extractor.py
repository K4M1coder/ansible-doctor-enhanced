"""
Unit tests for annotation extractor.

Following Constitution Article III (TDD): Tests written BEFORE implementation.
This test suite drives the design of AnnotationExtractor through Red-Green-Refactor cycle.
"""

from pathlib import Path

import pytest

from ansibledoctor.models.annotation import Annotation, AnnotationType
from ansibledoctor.parser.annotation_extractor import AnnotationExtractor


@pytest.fixture
def annotation_extractor():
    """Fixture providing annotation extractor instance."""
    return AnnotationExtractor()


class TestAnnotationExtraction:
    """Test suite for annotation extraction from YAML comments."""

    def test_extract_var_annotation_single_line(self, annotation_extractor):
        """
        RED: Test extracting single-line @var annotation.
        
        Format: # @var variable_name: description here
        """
        yaml_content = """
# @var web_port: HTTP port for web server
web_port: 80
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        assert len(annotations) == 1
        assert annotations[0].type == AnnotationType.VAR
        assert annotations[0].key == "web_port"
        assert "HTTP port" in annotations[0].content
        assert annotations[0].file_path == "defaults/main.yml"

    def test_extract_var_annotation_multiline(self, annotation_extractor):
        """
        RED: Test extracting multiline @var annotation.
        
        Format:
        # @var variable_name:
        #   description: Long description
        #   required: true
        """
        yaml_content = """
# @var database_config:
#   description: Database connection configuration
#   required: true
#   example: {host: localhost, port: 5432}
database_config:
  host: localhost
  port: 5432
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        assert len(annotations) == 1
        var_annotation = annotations[0]
        assert var_annotation.type == AnnotationType.VAR
        assert var_annotation.key == "database_config"
        assert "Database connection" in var_annotation.content
        assert var_annotation.has_attribute("description")
        assert var_annotation.has_attribute("required")
        assert var_annotation.has_attribute("example")

    def test_extract_var_annotation_json(self, annotation_extractor):
        """
        RED: Test extracting @var annotation with JSON attributes.
        
        Format: # @var variable_name: {"description": "...", "type": "string"}
        """
        yaml_content = """
# @var app_name: {"description": "Application name", "type": "string", "required": true}
app_name: myapp
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        assert len(annotations) == 1
        var_annotation = annotations[0]
        assert var_annotation.type == AnnotationType.VAR
        assert var_annotation.key == "app_name"
        
        # JSON should be parsed into attributes
        assert var_annotation.get_attribute("description") == "Application name"
        assert var_annotation.get_attribute("type") == "string"
        assert var_annotation.get_attribute("required") is True

    def test_extract_tag_annotation(self, annotation_extractor):
        """
        RED: Test extracting @tag annotation from task files.
        
        Format: # @tag tag_name: description of what this tag does
        """
        yaml_content = """
# @tag install: Install and configure web server packages
- name: Install nginx
  apt:
    name: nginx
    state: present
  tags:
    - install
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "tasks/main.yml")
        
        assert len(annotations) == 1
        tag_annotation = annotations[0]
        assert tag_annotation.type == AnnotationType.TAG
        assert tag_annotation.key == "install"
        assert "Install and configure" in tag_annotation.content

    def test_extract_todo_annotation(self, annotation_extractor):
        """
        RED: Test extracting @todo annotation.
        
        Format: # @todo: description of what needs to be done
        """
        yaml_content = """
# @todo: Add input validation for port numbers
web_port: 80

# @todo: Implement TLS certificate auto-renewal
ssl_enabled: false
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        todos = [a for a in annotations if a.type == AnnotationType.TODO]
        assert len(todos) == 2
        assert "input validation" in todos[0].content
        assert "TLS certificate" in todos[1].content

    def test_extract_example_annotation(self, annotation_extractor):
        """
        RED: Test extracting @example annotation.
        
        Format:
        # @example: Example title
        # code line 1
        # code line 2
        """
        yaml_content = """
# @example: Basic web server configuration
# web_port: 8080
# web_host: 0.0.0.0
# ssl_enabled: true

web_port: 80
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        examples = [a for a in annotations if a.type == AnnotationType.EXAMPLE]
        assert len(examples) == 1
        assert "Basic web server" in examples[0].content

    def test_extract_multiple_annotations(self, annotation_extractor):
        """
        RED: Test extracting multiple different annotations from same file.
        """
        yaml_content = """
# @var web_port: HTTP port
web_port: 80

# @var ssl_port: HTTPS port
ssl_port: 443

# @todo: Add certificate validation
# @example: SSL configuration
# ssl_enabled: true
# ssl_cert: /etc/ssl/cert.pem
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        vars_annotations = [a for a in annotations if a.type == AnnotationType.VAR]
        todos = [a for a in annotations if a.type == AnnotationType.TODO]
        examples = [a for a in annotations if a.type == AnnotationType.EXAMPLE]
        
        assert len(vars_annotations) == 2
        assert len(todos) == 1
        assert len(examples) == 1

    def test_extract_no_annotations(self, annotation_extractor):
        """
        RED: Test extracting from file with no annotations.
        """
        yaml_content = """
# Regular comment
web_port: 80

# Another regular comment
web_host: localhost
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        assert len(annotations) == 0

    def test_extract_malformed_annotation(self, annotation_extractor):
        """
        RED: Test handling malformed annotations gracefully.
        """
        yaml_content = """
# @var
# @var:
# @var variable_name
web_port: 80
"""
        # Should not crash, just skip malformed annotations
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        # Malformed annotations should be skipped or logged
        assert isinstance(annotations, list)

    def test_line_number_tracking(self, annotation_extractor):
        """
        RED: Test that annotations include correct line numbers.
        """
        yaml_content = """line 1
# @var web_port: HTTP port
web_port: 80

# @var ssl_port: HTTPS port
ssl_port: 443
"""
        annotations = annotation_extractor.extract_annotations(yaml_content, "defaults/main.yml")
        
        assert len(annotations) == 2
        # Line numbers should be tracked (1-indexed)
        assert annotations[0].line_number > 0
        assert annotations[1].line_number > annotations[0].line_number


class TestAnnotationParsing:
    """Test suite for annotation attribute parsing."""

    def test_parse_json_attributes(self, annotation_extractor):
        """
        RED: Test parsing JSON attributes from annotation.
        """
        annotation_text = '{"description": "Test", "type": "string", "required": true}'
        
        attributes = annotation_extractor.parse_annotation_attributes(annotation_text)
        
        assert attributes["description"] == "Test"
        assert attributes["type"] == "string"
        assert attributes["required"] is True

    def test_parse_yaml_attributes(self, annotation_extractor):
        """
        RED: Test parsing YAML-style attributes from multiline annotation.
        """
        annotation_text = """
description: Database configuration
required: true
type: dict
example:
  host: localhost
  port: 5432
"""
        attributes = annotation_extractor.parse_annotation_attributes(annotation_text)
        
        assert attributes["description"] == "Database configuration"
        assert attributes["required"] is True
        assert attributes["type"] == "dict"
        assert isinstance(attributes["example"], dict)

    def test_parse_simple_text(self, annotation_extractor):
        """
        RED: Test parsing simple text (no JSON/YAML structure).
        """
        annotation_text = "Simple description text here"
        
        attributes = annotation_extractor.parse_annotation_attributes(annotation_text)
        
        # Simple text should be accessible via description key or raw content
        assert isinstance(attributes, dict)
        assert len(attributes) == 0 or "description" in attributes

    def test_parse_invalid_json(self, annotation_extractor):
        """
        RED: Test handling invalid JSON gracefully.
        """
        annotation_text = '{"invalid": json syntax here}'
        
        # Should not crash, return empty dict or raw text
        attributes = annotation_extractor.parse_annotation_attributes(annotation_text)
        
        assert isinstance(attributes, dict)


class TestCommentExtraction:
    """Test suite for extracting comments from YAML content."""

    def test_extract_comments_from_yaml(self, annotation_extractor):
        """
        RED: Test extracting all comment lines from YAML.
        """
        yaml_content = """
# First comment
key1: value1

# Second comment
# Third comment
key2: value2

key3: value3  # Inline comment
"""
        comments = annotation_extractor.extract_comment_lines(yaml_content)
        
        assert "# First comment" in comments
        assert "# Second comment" in comments
        assert "# Third comment" in comments
        assert "# Inline comment" in comments

    def test_preserve_line_numbers(self, annotation_extractor):
        """
        RED: Test that line numbers are preserved for comments.
        """
        yaml_content = """line 1
# Comment on line 2
line 3
# Comment on line 4
"""
        comments_with_lines = annotation_extractor.extract_comment_lines_with_numbers(
            yaml_content
        )
        
        assert len(comments_with_lines) == 2
        assert comments_with_lines[0][0] == 2  # Line number
        assert "Comment on line 2" in comments_with_lines[0][1]  # Comment text
        assert comments_with_lines[1][0] == 4
