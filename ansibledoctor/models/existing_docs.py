"""ExistingDocs model for existing documentation files (Spec 001, User Story 5)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExistingDocs(BaseModel):
    """Represents existing documentation files in a role/collection/project.

    This model captures README, CHANGELOG, LICENSE, CONTRIBUTING, and lists
    of template and file assets.
    """

    readme_content: Optional[str] = Field(default=None, description="README file content")
    readme_format: Optional[str] = Field(
        default=None, description="README format: 'markdown' or 'rst'"
    )
    changelog_content: Optional[str] = Field(default=None, description="CHANGELOG file content")
    contributing_content: Optional[str] = Field(
        default=None, description="CONTRIBUTING file content"
    )
    license_content: Optional[str] = Field(default=None, description="LICENSE file content")
    license_type: Optional[str] = Field(
        default=None,
        description="Detected license type: 'MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', or 'Unknown'",
    )
    templates_list: list[str] = Field(
        default_factory=list, description="List of template files (*.j2)"
    )
    files_list: list[str] = Field(default_factory=list, description="List of static files")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "readme_content": "# My Role\n\nDescription here.",
                "readme_format": "markdown",
                "changelog_content": "# Changelog\n\n## v1.0.0\n- Initial release",
                "contributing_content": "# Contributing\n\nPlease follow guidelines.",
                "license_content": "MIT License\n\nCopyright (c) 2025...",
                "license_type": "MIT",
                "templates_list": ["config.j2", "service.j2"],
                "files_list": ["script.sh", "config.txt"],
            }
        }
    )
