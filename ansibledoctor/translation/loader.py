"""Translation loader and provider utilities.

Provides a TranslationLoader which loads translations from project-level
`.ansibledoctor/translations/{lang}.yml` and embedded package translations
under `ansibledoctor/translations/`.
"""

from pathlib import Path
from typing import Dict, Optional

from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader
from ansibledoctor.translation.provider import TranslationProvider
from ansibledoctor.utils.logging import get_logger

logger = get_logger(__name__)


class TranslationLoader:
    def __init__(self, package: Optional[str] = None):
        self.yaml_loader = RuamelYAMLLoader()
        self.package = package
        self._cache: dict[tuple[str, str | None], TranslationProvider] = {}

    def load_from_path(self, path: Path) -> Dict[str, str]:
        if not path.exists():
            return {}
        if not path.is_file():
            return {}
        data = self.yaml_loader.load_file(path)
        if isinstance(data, dict):
            return data
        return {}

    def load(self, lang: str, project_root: Optional[Path] = None) -> TranslationProvider:
        """Load translations for given language.

        Search order:
        - project_root/.ansibledoctor/translations/{lang}.yml if project_root provided
        - embedded package translations in ansibledoctor/translations/{lang}.yml
        """
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
        translations: Dict[str, str] = {}
        translations.update(self.load_from_path(pkg_path))
        # Overlay project-level translations to override package defaults
        if project_root:
            # Collection-level translations (lower precedence than project-level)
            for col_path in Path(project_root).glob("collections/**/translations/*.yml"):
                translations.update(self.load_from_path(col_path))
            # Project-level overrides
            pr = Path(project_root) / ".ansibledoctor" / "translations" / f"{lang}.yml"
            translations.update(self.load_from_path(pr))
            # Role-level overrides (highest precedence): overlay role-specific translations
            for role_path in Path(project_root).glob("roles/**/translations/*.yml"):
                translations.update(self.load_from_path(role_path))
        # If no translations found for requested lang, fallback to 'en'
        fallback_lang = "en"
        if not translations and fallback_lang != lang:
            logger.warning(
                "unsupported_language_code",
                lang=lang,
                message=f"No translations found for '{lang}', falling back to '{fallback_lang}'",
            )
            lang = fallback_lang
            translations.update(
                self.load_from_path(
                    Path(__file__).resolve().parents[1] / "translations" / f"{lang}.yml"
                )
            )
            # When falling back to `lang` (e.g., en), ensure we also apply any
            # project-level overrides for the fallback language so project
            # translations override package defaults as expected.
            if project_root:
                # overlay collection-level translations (lower precedence)
                for col_path in Path(project_root).glob("collections/**/translations/*.yml"):
                    translations.update(self.load_from_path(col_path))
                # project-level overrides for the fallback language
                pr = Path(project_root) / ".ansibledoctor" / "translations" / f"{lang}.yml"
                translations.update(self.load_from_path(pr))
                # role-level overrides
                for role_path in Path(project_root).glob("roles/**/translations/*.yml"):
                    translations.update(self.load_from_path(role_path))
        # Attempt to load fallback (e.g., 'en') translations and merge missing keys
        fallback_lang = "en"
        if fallback_lang != lang:
            fb_trans: Dict[str, str] = {}
            # Load package fallback first then project fallback so project-level
            # values override package values for the fallback language.
            pkg_fb_path = (
                Path(__file__).resolve().parents[1] / "translations" / f"{fallback_lang}.yml"
            )
            fb_trans.update(self.load_from_path(pkg_fb_path))
            if project_root:
                pr_fb = (
                    Path(project_root) / ".ansibledoctor" / "translations" / f"{fallback_lang}.yml"
                )
                fb_trans.update(self.load_from_path(pr_fb))
            # Merge fallback keys for any missing entries
            for k, v in fb_trans.items():
                translations.setdefault(k, v)

        provider = TranslationProvider(translations=translations, lang=lang)
        self._cache[cache_key] = provider
        return provider
