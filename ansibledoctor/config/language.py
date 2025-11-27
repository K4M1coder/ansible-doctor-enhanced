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
