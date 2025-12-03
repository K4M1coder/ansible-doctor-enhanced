"""Handler model for Ansible handlers (Spec 001, User Story 5)."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Handler(BaseModel):
    """Represents an Ansible handler definition.
    
    Handlers are tasks that run when notified by other tasks.
    They are defined in handlers/*.yml files.
    """
    
    name: str = Field(..., description="Handler name")
    tags: list[str] = Field(default_factory=list, description="Handler tags")
    listen: Optional[str] = Field(None, description="Listen directive for handler notifications")
    file_path: str = Field(..., description="Source file path")
    line_number: int = Field(..., description="Line number in source file")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "restart apache",
                "tags": ["web", "critical"],
                "listen": "restart webserver",
                "file_path": "handlers/main.yml",
                "line_number": 5
            }
        }
    )
