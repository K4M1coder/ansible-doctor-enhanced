"""Language configuration models and validation.

This module defines the `LanguageConfig` Pydantic model used to configure
which language translations are available and provide a default/fallback
language code. It includes validation to ensure language codes follow the
ISO 639-1 lower-case two-letter convention.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import List
import re


class LanguageConfig(BaseModel):
    default: str = Field(default="en")
    enabled: List[str] = Field(default_factory=lambda: ["en"])
    fallback: str = Field(default="en")
    detect_system: bool = Field(default=False)

    @field_validator("default", "fallback")
    def check_code(cls, v: str) -> str:
        if not isinstance(v, str) or not re.match(r"^[a-z]{2}$", v):
            raise ValueError("Language codes must be two lower-case letters (ISO 639-1)")
        return v

    @field_validator("enabled")
    def check_enabled_list(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list):
            raise ValueError("enabled must be a list of language codes")
        for code in v:
            if not re.match(r"^[a-z]{2}$", code):
                raise ValueError(f"Invalid language code in enabled: {code}")
        return v
"""(Pydantic v2) Language configuration models and validation.

This module defines the `LanguageConfig` Pydantic model used to configure
which language translations are available and provide a default/fallback
language code. It includes validation to ensure language codes follow the
ISO 639-1 lower-case two-letter convention.
"""
