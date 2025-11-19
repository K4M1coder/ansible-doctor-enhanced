"""
Annotation extractor for Ansible roles.

Extracts @var, @tag, @todo, @example annotations from YAML comments.
Implements AnnotationExtractor protocol following Constitution Article III (TDD) and Article X (DDD).

This module implements US2: "Parse role variables with annotations" from specification 001.
"""

import json
import re
from typing import Any

from ruamel.yaml import YAML

from ansibledoctor.models.annotation import Annotation, AnnotationType
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class AnnotationExtractor:
    """
    Extractor for Ansible Doctor annotations from YAML comments.
    
    Responsibilities (DDD Domain Service):
    - Extract comment lines from YAML content
    - Parse annotation markers (@var, @tag, @todo, @example)
    - Parse annotation attributes (JSON, YAML, plain text)
    - Transform raw comments into Annotation value objects
    
    Following DDD principles:
    - Returns Annotation value objects (immutable)
    - Anti-Corruption Layer for comment parsing logic
    - Ubiquitous Language: uses Ansible terminology
    """

    # Annotation patterns
    VAR_PATTERN = re.compile(r"#\s*@var\s+(\w+):\s*(.*)", re.IGNORECASE)
    TAG_PATTERN = re.compile(r"#\s*@tag\s+(\w+):\s*(.*)", re.IGNORECASE)
    TODO_PATTERN = re.compile(r"#\s*@todo:\s*(.*)", re.IGNORECASE)
    EXAMPLE_PATTERN = re.compile(r"#\s*@example:\s*(.*)", re.IGNORECASE)
    META_PATTERN = re.compile(r"#\s*@meta\s+(\w+):\s*(.*)", re.IGNORECASE)

    def __init__(self):
        """Initialize annotation extractor."""
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        logger.debug("AnnotationExtractor initialized")

    def extract_annotations(
        self, yaml_content: str, file_path: str
    ) -> list[Annotation]:
        """
        Extract all annotations from YAML content.
        
        Parses comment lines looking for annotation markers:
        - @var variable_name: description or JSON/YAML attributes
        - @tag tag_name: description
        - @todo: description
        - @example: title
        - @meta key: value
        
        Args:
            yaml_content: YAML file content as string
            file_path: Path to source file for tracking
            
        Returns:
            list[Annotation]: Parsed annotation value objects
        """
        logger.debug("extracting_annotations", file_path=file_path)

        annotations = []
        comment_lines = self.extract_comment_lines_with_numbers(yaml_content)

        i = 0
        while i < len(comment_lines):
            line_num, comment = comment_lines[i]
            
            # Try to match each annotation pattern
            if match := self.VAR_PATTERN.match(comment):
                var_name = match.group(1)
                content = match.group(2).strip()
                
                # Check if multiline annotation (next lines are continuations)
                multiline_content = []
                j = i + 1
                while j < len(comment_lines):
                    next_line_num, next_comment = comment_lines[j]
                    # Continue if next line is indented comment (multiline continuation)
                    if next_comment.startswith("#") and not any(
                        pattern.match(next_comment)
                        for pattern in [
                            self.VAR_PATTERN,
                            self.TAG_PATTERN,
                            self.TODO_PATTERN,
                            self.EXAMPLE_PATTERN,
                            self.META_PATTERN,
                        ]
                    ):
                        # Remove leading # and whitespace
                        clean_line = next_comment.lstrip("#").strip()
                        if clean_line:
                            multiline_content.append(clean_line)
                        j += 1
                    else:
                        break
                
                # Combine content if multiline
                if multiline_content:
                    content = content + "\n" + "\n".join(multiline_content)
                    i = j - 1  # Skip processed lines
                
                # Parse attributes
                parsed_attrs = self.parse_annotation_attributes(content)
                
                annotation = Annotation(
                    type=AnnotationType.VAR,
                    key=var_name,
                    content=content,
                    file_path=file_path,
                    line_number=line_num,
                    parsed_attributes=parsed_attrs,
                )
                annotations.append(annotation)
                
            elif match := self.TAG_PATTERN.match(comment):
                tag_name = match.group(1)
                content = match.group(2).strip()
                
                annotation = Annotation(
                    type=AnnotationType.TAG,
                    key=tag_name,
                    content=content,
                    file_path=file_path,
                    line_number=line_num,
                    parsed_attributes={},
                )
                annotations.append(annotation)
                
            elif match := self.TODO_PATTERN.match(comment):
                content = match.group(1).strip()
                
                annotation = Annotation(
                    type=AnnotationType.TODO,
                    key=None,
                    content=content,
                    file_path=file_path,
                    line_number=line_num,
                    parsed_attributes={},
                )
                annotations.append(annotation)
                
            elif match := self.EXAMPLE_PATTERN.match(comment):
                title = match.group(1).strip()
                
                # Collect example code from following comment lines
                example_lines = []
                j = i + 1
                while j < len(comment_lines):
                    next_line_num, next_comment = comment_lines[j]
                    # Continue collecting until non-comment or new annotation
                    if next_comment.startswith("#") and not any(
                        pattern.match(next_comment)
                        for pattern in [
                            self.VAR_PATTERN,
                            self.TAG_PATTERN,
                            self.TODO_PATTERN,
                            self.EXAMPLE_PATTERN,
                            self.META_PATTERN,
                        ]
                    ):
                        clean_line = next_comment.lstrip("#").strip()
                        if clean_line:
                            example_lines.append(clean_line)
                        j += 1
                    else:
                        break
                
                content = title
                if example_lines:
                    content = title + "\n" + "\n".join(example_lines)
                    i = j - 1
                
                annotation = Annotation(
                    type=AnnotationType.EXAMPLE,
                    key=None,
                    content=content,
                    file_path=file_path,
                    line_number=line_num,
                    parsed_attributes={"title": title, "code": "\n".join(example_lines)},
                )
                annotations.append(annotation)
                
            elif match := self.META_PATTERN.match(comment):
                meta_key = match.group(1)
                content = match.group(2).strip()
                
                annotation = Annotation(
                    type=AnnotationType.META,
                    key=meta_key,
                    content=content,
                    file_path=file_path,
                    line_number=line_num,
                    parsed_attributes={},
                )
                annotations.append(annotation)
            
            i += 1

        logger.info(
            "annotations_extracted",
            file_path=file_path,
            count=len(annotations),
            types={
                "var": sum(1 for a in annotations if a.type == AnnotationType.VAR),
                "tag": sum(1 for a in annotations if a.type == AnnotationType.TAG),
                "todo": sum(1 for a in annotations if a.type == AnnotationType.TODO),
                "example": sum(1 for a in annotations if a.type == AnnotationType.EXAMPLE),
            },
        )

        return annotations

    def parse_annotation_attributes(self, content: str) -> dict[str, Any]:
        """
        Parse annotation content into structured attributes.
        
        Supports three formats:
        1. JSON: {"description": "...", "required": true}
        2. YAML: description: ...\nrequired: true
        3. Plain text: Simple description
        
        Args:
            content: Annotation content to parse
            
        Returns:
            dict[str, Any]: Parsed attributes
        """
        content = content.strip()
        
        if not content:
            return {}
        
        # Strip dollar sign prefix if present (JSON format marker)
        if content.startswith("$"):
            content = content[1:].strip()
        
        # Try JSON format first
        if content.startswith("{"):
            try:
                attrs = json.loads(content)
                if isinstance(attrs, dict):
                    return attrs
            except json.JSONDecodeError:
                logger.debug("json_parse_failed", content_preview=content[:50])
        
        # Try YAML format (multiline with key: value pairs)
        if "\n" in content or ":" in content:
            try:
                attrs = self._yaml.load(content)
                # Only accept dict results, reject None or other types
                if isinstance(attrs, dict):
                    # Filter out None keys (edge case: content is just ":")
                    attrs = {k: v for k, v in attrs.items() if k is not None}
                    return attrs
            except Exception:
                logger.debug("yaml_parse_failed", content_preview=content[:50])
        
        # Plain text - return empty dict (content is in Annotation.content)
        return {}

    def extract_comment_lines(self, yaml_content: str) -> list[str]:
        """
        Extract all comment lines from YAML content.
        
        Args:
            yaml_content: YAML file content
            
        Returns:
            list[str]: Comment lines with leading # preserved
        """
        comments = []
        for line in yaml_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.append(stripped)
            elif "#" in line:
                # Inline comment
                parts = line.split("#", 1)
                if len(parts) == 2:
                    comments.append("#" + parts[1])
        return comments

    def extract_comment_lines_with_numbers(
        self, yaml_content: str
    ) -> list[tuple[int, str]]:
        """
        Extract comment lines with line numbers.
        
        Args:
            yaml_content: YAML file content
            
        Returns:
            list[tuple[int, str]]: List of (line_number, comment_text) tuples
        """
        comments = []
        for line_num, line in enumerate(yaml_content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                comments.append((line_num, stripped))
            elif "#" in line:
                # Inline comment
                parts = line.split("#", 1)
                if len(parts) == 2:
                    comments.append((line_num, "#" + parts[1]))
        return comments
