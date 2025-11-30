"""Language configuration models and validation.

This module defines the `LanguageConfig` Pydantic model used to configure
which language translations are available and provide a default/fallback
language code. It includes validation to ensure language codes follow the
ISO 639-1 lower-case two-letter convention.
"""

from __future__ import annotations

import re
from typing import List

from pydantic import BaseModel, Field, field_validator


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


def detect_system_language() -> str | None:
    """Return the system's default language code as an ISO 639-1 two-letter code.

    Uses the locale module to derive the language code. Returns None if the
    language cannot be determined or if it does not match the expected 2-letter code.
    """
    import locale

    try:
        loc = locale.getdefaultlocale()[0]
        if not loc:
            return None
        # Extract 'en' from 'en_US' formats
        code = loc.split(".")[0].split("_")[0]
        code = code.lower()
        if re.match(r"^[a-z]{2}$", code):
            return code
    except Exception:
        return None
    return None


"""(Pydantic v2) Language configuration models and validation.

This module defines the `LanguageConfig` Pydantic model used to configure
which language translations are available and provide a default/fallback
language code. It includes validation to ensure language codes follow the
ISO 639-1 lower-case two-letter convention.
"""
