"""TranslationProvider implementation.

This module provides `TranslationProvider`, the class responsible for looking
up translation keys, formatting values, and handling minimal pluralization.
"""

from __future__ import annotations

from typing import Dict, Optional

from ansibledoctor.utils.logging import get_logger

try:
    # Babel is optional; if present, use it for plural rules
    from babel.core import Locale as BabelLocale
except Exception:  # pragma: no cover - optional
    BabelLocale = None

logger = get_logger(__name__)


class TranslationProvider:
    def __init__(self, translations: Dict[str, str], lang: str = "en") -> None:
        self._translations = translations or {}
        self.lang = lang
        # Try to cache a parsed Babel locale when Babel is available
        self._babel_locale = None
        if BabelLocale is not None:
            try:
                self._babel_locale = BabelLocale.parse(lang)
            except Exception:
                # fallback silently to None; pluralization will use simple rules
                self._babel_locale = None

    def _lookup(self, key: str):
        return self._translations.get(key)

    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        value = self._lookup(key)
        if value is None:
            return default if default is not None else key
        try:
            if kwargs:
                return value.format(**kwargs)
            return value
        except Exception:
            logger.debug("translation_format_failed", key=key, value=value)
            return value

    def t(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        count = kwargs.get("count")
        if count is not None:
            # Try using Babel to determine the plural category, falling back
            # to a simple `one` vs `other` rule if Babel isn't available.
            form = None
            if self._babel_locale is not None:
                try:
                    # Babel Locale objects expose `plural_form` which may return
                    # a category (e.g. "one", "other") or an index; handle both
                    value = self._babel_locale.plural_form(count)  # type: ignore[attr-defined]
                    if isinstance(value, str):
                        form = value
                    else:
                        # If it's an integer, fall back to `one` vs `other`
                        form = "one" if value == 1 else "other"
                except Exception:
                    form = None
            if not form:
                form = "one" if count == 1 else "other"
            plural_key = f"{key}.{form}"
            plural_val = self._lookup(plural_key)
            if plural_val is not None:
                return self.get(plural_key, default=default, **kwargs)
            # fallback to other form
            other_form = "other" if form == "one" else "one"
            other_key = f"{key}.{other_form}"
            other_val = self._lookup(other_key)
            if other_val is not None:
                return self.get(other_key, default=default, **kwargs)
        return self.get(key, default=default, **kwargs)
