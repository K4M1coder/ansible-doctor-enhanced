"""
ExampleParser - Extract @example...@end code blocks from documentation.

Extracts code example blocks from comments in role files. Examples can be
embedded in YAML comments, Python docstrings, Jinja2 templates, or Markdown files.

Syntax patterns supported:
- YAML/Python: # @example Title ... # @end
- Markdown: <!-- @example Title --> ... <!-- @end -->
- Optional language: @example:bash Title

The parser preserves exact code formatting and detects language from file
extension or explicit annotation.
"""

import re
from pathlib import Path

import structlog

from ansibledoctor.models.example import Example

logger = structlog.get_logger(__name__)


class ExampleParser:
    """
    Parser for extracting @example...@end code blocks from role files.

    Supports multiple file formats and preserves exact code formatting.
    Language detection is automatic based on file extension or can be
    explicitly specified in the annotation.
    """

    # Regex patterns for different comment styles
    YAML_PYTHON_START = re.compile(r"^\s*#\s*@example(?::(\w+))?\s+(.+)$")
    YAML_PYTHON_CODE = re.compile(r"^\s*#\s(.*)$")  # Capture everything after "# " including indentation
    YAML_PYTHON_END = re.compile(r"^\s*#\s*@end\s*$")

    MARKDOWN_START = re.compile(r"<!--\s*@example(?::(\w+))?\s+(.+)\s*-->")
    MARKDOWN_DESC = re.compile(r"<!--\s*(.+)\s*-->")
    MARKDOWN_END = re.compile(r"<!--\s*@end\s*-->")

    # File extensions to scan
    SCANNABLE_EXTENSIONS = {".yml", ".yaml", ".py", ".j2", ".jinja", ".jinja2", ".md"}

    # Directories to exclude from scanning
    EXCLUDED_DIRS = {".git", "__pycache__", ".hypothesis", ".pytest_cache", "node_modules", "venv", ".venv"}

    # Language mapping by file extension
    LANGUAGE_MAP = {
        ".yml": "yaml",
        ".yaml": "yaml",
        ".py": "python",
        ".j2": "jinja2",
        ".jinja": "jinja2",
        ".jinja2": "jinja2",
        ".md": "markdown",
    }

    def parse_file(self, file_path: Path) -> list[Example]:
        """
        Extract all @example blocks from a single file.

        Args:
            file_path: Path to file to parse

        Returns:
            List of Example objects extracted from file
        """
        if not file_path.exists():
            logger.warning("file_not_found", file_path=str(file_path))
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError) as e:
            logger.debug("file_read_error", file_path=str(file_path), error=str(e))
            return []

        # Detect file type and use appropriate parser
        if file_path.suffix == ".md":
            return self._parse_markdown(content, file_path)
        else:
            return self._parse_comment_based(content, file_path)

    def _parse_comment_based(self, content: str, file_path: Path) -> list[Example]:
        """Parse examples from comment-based files (YAML, Python, Jinja2)."""
        examples = []
        lines = content.splitlines()
        i = 0

        while i < len(lines):
            start_match = self.YAML_PYTHON_START.match(lines[i])
            if start_match:
                explicit_lang = start_match.group(1)
                title = start_match.group(2).strip()
                i += 1

                # Collect all content lines until @end
                code_lines = []
                while i < len(lines):
                    end_match = self.YAML_PYTHON_END.match(lines[i])
                    if end_match:
                        i += 1
                        break

                    code_match = self.YAML_PYTHON_CODE.match(lines[i])
                    if code_match:
                        # Preserve indentation by not stripping
                        code_lines.append(code_match.group(1))
                    i += 1

                # Create example if we have code
                if code_lines or not lines:  # Allow empty for edge case tests
                    code = "\n".join(code_lines)
                    language = explicit_lang or self._detect_language(file_path)

                    example = Example(title=title, code=code, description=None, language=language)
                    examples.append(example)
                    logger.debug("example_extracted", title=title, language=language, code_lines=len(code_lines))
            else:
                i += 1

        return examples

    def _parse_markdown(self, content: str, file_path: Path) -> list[Example]:
        """Parse examples from Markdown files."""
        examples = []
        lines = content.splitlines()
        i = 0

        while i < len(lines):
            # Check for multiline HTML comment with @example
            if "<!-- @example" in lines[i]:
                # Extract title from opening comment
                start_match = re.search(r"<!--\s*@example(?::(\w+))?\s+(.+?)(?:\s*-->)?$", lines[i])
                if start_match:
                    explicit_lang = start_match.group(1)
                    title = start_match.group(2).strip()

                    # Check if this is a multiline comment or single-line
                    if "-->" not in lines[i]:
                        # Multiline comment - collect description until -->
                        i += 1
                        description_lines = []
                        while i < len(lines) and "-->" not in lines[i]:
                            if lines[i].strip():
                                description_lines.append(lines[i].strip())
                            i += 1
                        if i < len(lines):  # Skip closing -->
                            i += 1
                        description = " ".join(description_lines) if description_lines else None
                    else:
                        # Single-line comment
                        i += 1
                        description = None

                    # Look for code block
                    code_lines = []
                    fence_lang = None
                    while i < len(lines) and "<!-- @end -->" not in lines[i]:
                        if lines[i].strip().startswith("```"):
                            # Extract language from code fence
                            fence_match = re.match(r"```(\w+)?", lines[i].strip())
                            fence_lang = fence_match.group(1) if fence_match and fence_match.group(1) else None
                            i += 1

                            # Collect code until closing ```
                            while i < len(lines) and not lines[i].strip().startswith("```"):
                                code_lines.append(lines[i])
                                i += 1

                            if i < len(lines):  # Skip closing ```
                                i += 1
                            break
                        i += 1

                    # Find @end marker
                    while i < len(lines) and "<!-- @end -->" not in lines[i]:
                        i += 1
                    if i < len(lines):
                        i += 1

                    # Create example
                    if code_lines:
                        code = "\n".join(code_lines)
                        language = explicit_lang or fence_lang or "markdown"

                        example = Example(
                            title=title, code=code, description=description if description else None, language=language
                        )
                        examples.append(example)
                        logger.debug("markdown_example_extracted", title=title, language=language)
            else:
                i += 1

        return examples

    def _detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        return self.LANGUAGE_MAP.get(file_path.suffix, "yaml")

    def parse_directory(self, directory: Path) -> list[Example]:
        """
        Extract examples from all relevant files in directory recursively.

        Args:
            directory: Root directory to scan

        Returns:
            List of all Example objects found in directory tree
        """
        if not directory.exists():
            logger.warning("directory_not_found", directory=str(directory))
            return []

        examples = []
        for file_path in directory.rglob("*"):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in self.EXCLUDED_DIRS):
                continue

            # Only scan relevant file types
            if file_path.is_file() and file_path.suffix in self.SCANNABLE_EXTENSIONS:
                file_examples = self.parse_file(file_path)
                examples.extend(file_examples)

        logger.info(
            "directory_scan_complete",
            directory=str(directory),
            files_scanned=len(list(directory.rglob("*"))),
            examples_found=len(examples),
        )
        return examples

    def parse_role(self, role_path: Path) -> list[Example]:
        """
        Extract examples from entire Ansible role directory.

        Args:
            role_path: Path to role root directory

        Returns:
            List of all Example objects found in role
        """
        logger.info("parsing_role_examples", role_path=str(role_path))
        examples = self.parse_directory(role_path)
        logger.info("role_examples_extracted", role_path=str(role_path), example_count=len(examples))
        return examples
