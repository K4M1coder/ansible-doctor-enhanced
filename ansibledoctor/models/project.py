from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class Playbook(BaseModel):
    name: str
    path: str
    hosts: List[str] = []
    roles: List[str] = []


class RoleInfo(BaseModel):
    name: str
    path: str


class CollectionInfo(BaseModel):
    name: str
    path: str


class InventoryItem(BaseModel):
    name: str
    groups: List[str] = []
    hosts: List[str] = []


class Project(BaseModel):
    name: Optional[str] = None
    path: str
    playbooks: List[Playbook] = []
    roles: List[RoleInfo] = []
    collections: List[CollectionInfo] = []
    inventory: List[InventoryItem] = []
