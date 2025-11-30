"""Translation loader and provider utilities.

Provides a TranslationLoader which loads translations from project-level
`.ansibledoctor/translations/{lang}.yml` and embedded package translations
under `ansibledoctor/translations/`.
"""

import copy
from pathlib import Path
from typing import Optional

from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.translation.provider import TranslationProvider
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class TranslationLoader:
    def __init__(self, package: Optional[str] = None):
        self.yaml_loader = RuamelYAMLLoader()
        self.package = package
        self._cache: dict[tuple[str, str | None], TranslationProvider] = {}

    def load_from_path(self, path: Path) -> dict:
        if not path.exists():
            return {}
        if not path.is_file():
            return {}
        data = self.yaml_loader.load_file(path)
        if isinstance(data, dict):
            # Return nested dict (we will deep-merge these later)
            return data
        return {}

    def _deep_update(self, dest: dict, src: dict) -> None:
        """Recursively update `dest` with `src`, merging nested dicts.

        Values from `src` override those in `dest`. When both values are dicts
        we recurse; otherwise `src` value replaces `dest`.
        """
        for k, v in src.items():
            if isinstance(v, dict) and isinstance(dest.get(k), dict):
                self._deep_update(dest[k], v)
            else:
                dest[k] = v

    def load(self, lang: str, project_root: Optional[Path] = None) -> TranslationProvider:
        """Load translations for given language.

        Search order:
        - project_root/.ansibledoctor/translations/{lang}.yml if project_root provided
        - embedded package translations in ansibledoctor/translations/{lang}.yml
        """
        # Keep a copy of the requested language for logging/diagnostic purposes
        requested_lang = lang
        # Validate the provided language code: ISO 639-1 two-letter code expected.
        if not isinstance(lang, str) or len(lang.strip()) != 2 or not lang.strip().isalpha():
            logger.warning(
                "invalid_language_code",
                lang=lang,
                message="Invalid language code; falling back to 'en'",
            )
            lang = "en"
        cache_key = (lang, str(project_root) if project_root is not None else None)
        if cache_key in self._cache:
            return self._cache[cache_key]
        # Load packaged (default) translations first (base)
        pkg_path = Path(__file__).resolve().parents[1] / "translations" / f"{lang}.yml"
        translations: dict = {}
        pkg_trans = self.load_from_path(pkg_path)
        if pkg_trans:
            self._deep_update(translations, pkg_trans)
        # Overlay project-level translations to override package defaults
        if project_root:
            # Collection-level translations (lower precedence than project-level)
            for col_path in Path(project_root).glob("collections/**/translations/*.yml"):
                col_trans = self.load_from_path(col_path)
                if col_trans:
                    self._deep_update(translations, col_trans)
            # Project-level overrides
            pr = Path(project_root) / ".ansibledoctor" / "translations" / f"{lang}.yml"
            pr_trans = self.load_from_path(pr)
            if pr_trans:
                self._deep_update(translations, pr_trans)
            # Role-level overrides (highest precedence): overlay role-specific translations
            for role_path in Path(project_root).glob("roles/**/translations/*.yml"):
                role_trans = self.load_from_path(role_path)
                if role_trans:
                    self._deep_update(translations, role_trans)
        # Capture the original translations before fallback merge
        orig_translations = copy.deepcopy(translations)

        # If no translations found for requested lang, fallback to 'en'
        fallback_lang = "en"
        if not translations and fallback_lang != lang:
            logger.warning(
                "unsupported_language_code",
                lang=lang,
                message=f"No translations found for '{lang}', falling back to '{fallback_lang}'",
            )
            lang = fallback_lang
            pkg_fb_trans = self.load_from_path(
                Path(__file__).resolve().parents[1] / "translations" / f"{lang}.yml"
            )
            if pkg_fb_trans:
                self._deep_update(translations, pkg_fb_trans)
            # When falling back to `lang` (e.g., en), ensure we also apply any
            # project-level overrides for the fallback language so project
            # translations override package defaults as expected.
            if project_root:
                # overlay collection-level translations (lower precedence)
                for col_path in Path(project_root).glob("collections/**/translations/*.yml"):
                    col_trans = self.load_from_path(col_path)
                    if col_trans:
                        self._deep_update(translations, col_trans)
                # project-level overrides for the fallback language
                pr = Path(project_root) / ".ansibledoctor" / "translations" / f"{lang}.yml"
                pr_trans = self.load_from_path(pr)
                if pr_trans:
                    self._deep_update(translations, pr_trans)
                # role-level overrides
                for role_path in Path(project_root).glob("roles/**/translations/*.yml"):
                    role_trans = self.load_from_path(role_path)
                    if role_trans:
                        self._deep_update(translations, role_trans)
        # Attempt to load fallback (e.g., 'en') translations and merge missing keys
        fallback_lang = "en"
        if fallback_lang != lang:
            fb_trans: dict = {}
            # Load package fallback first then project fallback so project-level
            # values override package values for the fallback language.
            pkg_fb_path = (
                Path(__file__).resolve().parents[1] / "translations" / f"{fallback_lang}.yml"
            )
            pkg_fb_trans = self.load_from_path(pkg_fb_path)
            if pkg_fb_trans:
                self._deep_update(fb_trans, pkg_fb_trans)
            if project_root:
                pr_fb = (
                    Path(project_root) / ".ansibledoctor" / "translations" / f"{fallback_lang}.yml"
                )
                pr_fb_trans = self.load_from_path(pr_fb)
                if pr_fb_trans:
                    self._deep_update(fb_trans, pr_fb_trans)

            # Merge fallback keys for any missing entries
            # Fill in any missing keys from fallback; we only set missing values
            def set_missing(dest: dict, src: dict) -> None:
                for kk, vv in src.items():
                    if isinstance(vv, dict):
                        if kk not in dest or not isinstance(dest.get(kk), dict):
                            dest[kk] = {}
                        set_missing(dest[kk], vv)
                    else:
                        dest.setdefault(kk, vv)

            set_missing(translations, fb_trans)

        fallback_used = None
        if orig_translations != translations:
            fallback_used = "en"
        provider = TranslationProvider(
            translations=translations,
            lang=lang,
            requested_lang=requested_lang,
            orig_translations=orig_translations,
            fallback_lang=fallback_used,
        )
        self._cache[cache_key] = provider
        return provider
