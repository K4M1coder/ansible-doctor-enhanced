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
    def __init__(
        self,
        translations: Dict[str, str],
        lang: str = "en",
        requested_lang: Optional[str] = None,
        orig_translations: Optional[Dict[str, str]] = None,
        fallback_lang: Optional[str] = None,
    ) -> None:
        self._translations = translations or {}
        self.lang = lang
        # original translations present in the requested language (before fallback merge)
        self._orig_translations = orig_translations or {}
        # The language originally requested by the caller (before fallback)
        self._requested_lang = requested_lang or lang
        # fallback language (e.g., 'en') that was used to fill missing values
        self._fallback_lang = fallback_lang
        self._logged_missing_keys: set[str] = set()
        # Try to cache a parsed Babel locale when Babel is available
        self._babel_locale = None
        if BabelLocale is not None:
            try:
                self._babel_locale = BabelLocale.parse(lang)
            except Exception:
                # fallback silently to None; pluralization will use simple rules
                self._babel_locale = None

    def _lookup(self, key: str):
        """Look up a key in nested translation mapping.

        Supports dotted key lookups and returns either a string, a dict (for plural forms),
        or None if missing.
        """
        # If translations are flat dict (keys are dotted), fallback to direct lookup
        if key in self._translations:
            return self._translations.get(key)

        # Otherwise attempt nested lookup via '.' splitting
        parts = key.split(".")
        node = self._translations
        try:
            for part in parts:
                if not isinstance(node, dict):
                    return None
                node = node.get(part)
            return node
        except Exception:
            return None

    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        value = self._lookup(key)
        # If a dict was returned (e.g., plural forms), it's not a direct string
        if value is None:
            return default if default is not None else key
        if isinstance(value, dict):
            # No count was provided; return the 'other' form when present, or default
            if "other" in value:
                value = value["other"]
            elif "one" in value:
                value = value["one"]
            else:
                # Can't present dict directly; fall back to default.
                return default if default is not None else key
            try:
                if kwargs:
                    return str(value).format(**kwargs)
                return str(value)
            except Exception:
                logger.debug("translation_format_failed", key=key, value=value)
            return str(value)

        # If key exists in translations (post-fallback merge) but did not exist in
        # the original requested language translations, we likely fell back to a
        # different language for this key; warn so the user can spot missing
        # translations for the desired language.
        try:
            if self._fallback_lang and value is not None:
                # If the key doesn't exist in original translations (pre-merge),
                # this key was pulled from fallback; log once per key.
                if not self._exists_in_orig(key) and key not in self._logged_missing_keys:
                    logger.warning(
                        "translation_missing_in_lang_fallback",
                        key=key,
                        lang=self._requested_lang,
                        fallback=self._fallback_lang,
                        message=f"Key '{key}' missing in '{self._requested_lang}', using fallback '{self._fallback_lang}'",
                    )
                    self._logged_missing_keys.add(key)
        except Exception:
            # Non-critical; do not disrupt translation retrieval on logging errors.
            pass
        # Finally, return the string representation of the found value
        try:
            if kwargs:
                return str(value).format(**kwargs)
            return str(value)
        except Exception:
            logger.debug("translation_format_failed", key=key, value=value)
            return str(value)

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
            # Try dotted plural key first (e.g., 'items.one')
            plural_key = f"{key}.{form}"
            plural_val = self._lookup(plural_key)
            if plural_val is not None and isinstance(plural_val, str):
                return self.get(plural_key, default=default, **kwargs)
            # Or key maps to a dict with plural forms: {one: '', other: ''}
            main_val = self._lookup(key)
            if isinstance(main_val, dict) and form in main_val:
                return self.get(f"{key}.{form}", default=default, **kwargs)
            # fallback to other form
            other_form = "other" if form == "one" else "one"
            other_key = f"{key}.{other_form}"
            other_val = self._lookup(other_key)
            if other_val is not None and isinstance(other_val, str):
                return self.get(other_key, default=default, **kwargs)
            if isinstance(main_val, dict) and other_form in main_val:
                return self.get(f"{key}.{other_form}", default=default, **kwargs)
        return self.get(key, default=default, **kwargs)

    def _exists_in_orig(self, key: str) -> bool:
        """Return True if the dotted key exists in the original translations dict.

        This checks the pre-merged set of translations for the requested language,
        so callers can detect whether results came from a fallback merge or
        originally existed for the requested language.
        """
        if not self._orig_translations:
            return False
        if key in self._orig_translations:
            return True
        parts = key.split(".")
        node = self._orig_translations
        try:
            for p in parts:
                if not isinstance(node, dict):
                    return False
                if p not in node:
                    return False
                node = node.get(p)
            return node is not None
        except Exception:
            return False
