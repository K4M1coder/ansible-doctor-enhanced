"""Documentation extractor for existing docs (Spec 001, User Story 5)."""

import re
from pathlib import Path
from typing import Optional

from ansibledoctor.models.existing_docs import ExistingDocs
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class DocsExtractor:
    """Extractor for existing documentation files.
    
    Extracts README, CHANGELOG, LICENSE, CONTRIBUTING files
    and lists template/file assets.
    """
    
    def __init__(self, base_path: str):
        """Initialize the docs extractor.
        
        Args:
            base_path: Path to the role/collection/project directory
        """
        self.base_path = Path(base_path)
    
    def extract(self) -> ExistingDocs:
        """Extract all existing documentation.
        
        Returns:
            ExistingDocs object with extracted content
        """
        readme_content, readme_format = self._extract_readme()
        changelog_content = self._extract_file("CHANGELOG.md")
        contributing_content = self._extract_file("CONTRIBUTING.md")
        license_content = self._extract_file("LICENSE")
        license_type = self._detect_license_type(license_content) if license_content else None
        templates_list = self._list_directory("templates")
        files_list = self._list_directory("files")
        
        logger.debug(
            f"Extracted docs from {self.base_path}: "
            f"readme={bool(readme_content)}, "
            f"changelog={bool(changelog_content)}, "
            f"license={license_type}, "
            f"templates={len(templates_list)}, "
            f"files={len(files_list)}"
        )
        
        return ExistingDocs(
            readme_content=readme_content,
            readme_format=readme_format,
            changelog_content=changelog_content,
            contributing_content=contributing_content,
            license_content=license_content,
            license_type=license_type,
            templates_list=templates_list,
            files_list=files_list
        )
    
    def _extract_readme(self) -> tuple[Optional[str], Optional[str]]:
        """Extract README file and detect format.
        
        Returns:
            Tuple of (content, format) where format is 'markdown' or 'rst'
        """
        # Try README.md first
        readme_md = self.base_path / "README.md"
        if readme_md.exists():
            content = readme_md.read_text(encoding="utf-8")
            return content, "markdown"
        
        # Try README.rst
        readme_rst = self.base_path / "README.rst"
        if readme_rst.exists():
            content = readme_rst.read_text(encoding="utf-8")
            return content, "rst"
        
        # Try README (no extension) and detect format
        readme = self.base_path / "README"
        if readme.exists():
            content = readme.read_text(encoding="utf-8")
            format_type = self._detect_readme_format(content)
            return content, format_type
        
        return None, None
    
    def _detect_readme_format(self, content: str) -> str:
        """Detect README format from content.
        
        Args:
            content: README file content
            
        Returns:
            'rst' if RST markers detected, otherwise 'markdown'
        """
        # RST markers: section underlines with =, -, ~, ^, etc.
        rst_patterns = [
            r'^[=\-~^"\'`:#*+_]{3,}\s*$',  # Underlines
            r'^\.\. \w+::',  # Directives (.. code::, .. note::)
        ]
        
        for pattern in rst_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return "rst"
        
        return "markdown"
    
    def _extract_file(self, filename: str) -> Optional[str]:
        """Extract content from a file if it exists.
        
        Args:
            filename: Name of the file to extract
            
        Returns:
            File content or None if not found
        """
        file_path = self.base_path / filename
        if file_path.exists():
            try:
                return file_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {e}")
                return None
        return None
    
    def _detect_license_type(self, license_content: str) -> str:
        """Detect license type from license content.
        
        Args:
            license_content: Content of the LICENSE file
            
        Returns:
            License type string: 'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', or 'Unknown'
        """
        content_lower = license_content.lower()
        
        # MIT License
        if "mit license" in content_lower:
            return "MIT"
        
        # Apache License
        if "apache license" in content_lower and "version 2.0" in content_lower:
            return "Apache-2.0"
        
        # GPL License
        if "gnu general public license" in content_lower:
            if "version 3" in content_lower:
                return "GPL-3.0"
            elif "version 2" in content_lower:
                return "GPL-2.0"
            return "GPL"
        
        # BSD License
        if "bsd" in content_lower and "clause" in content_lower:
            if "3-clause" in content_lower or "three clause" in content_lower:
                return "BSD-3-Clause"
            elif "2-clause" in content_lower or "two clause" in content_lower:
                return "BSD-2-Clause"
            return "BSD"
        
        return "Unknown"
    
    def _list_directory(self, dirname: str) -> list[str]:
        """List files in a directory (non-recursive).
        
        Args:
            dirname: Directory name relative to base_path
            
        Returns:
            List of filenames (not directories)
        """
        dir_path = self.base_path / dirname
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        try:
            return [
                item.name
                for item in dir_path.iterdir()
                if item.is_file()
            ]
        except Exception as e:
            logger.warning(f"Failed to list directory {dir_path}: {e}")
            return []
