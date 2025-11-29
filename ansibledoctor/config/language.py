"""Language configuration schema for i18n settings.

Defines `LanguageConfig` Pydantic model used to validate `.ansibledoctor.yml`
language settings (default language, enabled languages, fallback language and
detect_system behavior).
"""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, validator


def _validate_lang_code(code: str) -> str:
    if not isinstance(code, str):
        raise ValueError("Language code must be a string")
    code = code.strip().lower()
    if len(code) != 2 or not code.isalpha():
        raise ValueError("Language code must be an ISO 639-1 two-letter code (e.g., 'en')")
    return code


class LanguageConfig(BaseModel):
    default: str = Field("en", description="Default language code (ISO 639-1)")
    enabled: Optional[List[str]] = Field(None, description="List of enabled languages")
    fallback: Optional[str] = Field("en", description="Fallback language if translation missing")
    detect_system: bool = Field(False, description="Detect system locale and enable it if supported")

    _validate_default = validator("default", allow_reuse=True)(_validate_lang_code)
    _validate_fallback = validator("fallback", allow_reuse=True)(_validate_lang_code)

    @validator("enabled", each_item=True)
    def _validate_enabled(cls, v):
        return _validate_lang_code(v)
"""Language configuration models and validation.

This module defines the `LanguageConfig` Pydantic model used to configure
which language translations are available and provide a default/fallback
language code. It includes validation to ensure language codes follow the
ISO 639-1 lower-case two-letter convention.
"""

from pydantic import BaseModel, Field, validator
from typing import List
import re


class LanguageConfig(BaseModel):
    default: str = Field(default="en")
    enabled: List[str] = Field(default_factory=lambda: ["en"])
    fallback: str = Field(default="en")
    detect_system: bool = Field(default=False)

    @validator("default", "fallback")
    def check_code(cls, v):
        if not re.match(r"^[a-z]{2}$", v):
            raise ValueError("Language codes must be two lower-case letters (ISO 639-1)")
        return v

    @validator("enabled")
    def check_enabled_list(cls, v):
        if not isinstance(v, list):
            raise ValueError("enabled must be a list of language codes")
        for code in v:
            if not re.match(r"^[a-z]{2}$", code):
                raise ValueError(f"Invalid language code in enabled: {code}")
        return v
