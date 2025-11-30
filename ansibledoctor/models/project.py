"""Models for representing Ansible project structure used by the parser.

This module contains Pydantic models for Project, Playbook, RoleInfo,
CollectionInfo and InventoryItem. These models are intentionally minimal and
will be expanded as project parsing features grow.
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Playbook(BaseModel):
    name: str
    path: str
    hosts: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)


class RoleInfo(BaseModel):
    name: str
    path: str


class CollectionInfo(BaseModel):
    name: str
    path: str


class InventoryItem(BaseModel):
    name: str
    groups: List[str] = Field(default_factory=list)
    hosts: List[str] = Field(default_factory=list)


class Project(BaseModel):
    name: Optional[str] = None
    path: str
    playbooks: List[Playbook] = Field(default_factory=list)
    roles: List[RoleInfo] = Field(default_factory=list)
    collections: List[CollectionInfo] = Field(default_factory=list)
    inventory: List[InventoryItem] = Field(default_factory=list)
    # Inventory variables mapping (group_vars and host_vars)
    group_vars: dict[str, dict[str, Any]] = Field(default_factory=dict)
    host_vars: dict[str, dict[str, Any]] = Field(default_factory=dict)
    # computed effective variables per host (applies precedence)
    effective_vars: dict[str, dict[str, Any]] = Field(default_factory=dict)
