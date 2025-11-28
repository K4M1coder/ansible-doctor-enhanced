from pathlib import Path
from typing import Dict, Optional

from ansibledoctor.parser.yaml_loader import RuamelYAMLLoader


class TranslationProvider:
    def __init__(self, translations: Dict[str, str], lang: str = "en") -> None:
        self._translations = translations or {}
        self.lang = lang

    def get(self, key: str, default: Optional[str] = None) -> str:
        return self._translations.get(key, default if default is not None else key)

    def t(self, key: str) -> str:
        return self.get(key)


class TranslationLoader:
    def __init__(self, package: Optional[str] = None):
        self.yaml_loader = RuamelYAMLLoader()
        self.package = package

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
        translations = {}
        if project_root:
            pr = Path(project_root) / ".ansibledoctor" / "translations" / f"{lang}.yml"
            translations.update(self.load_from_path(pr))
        # Default embedded path in package: ansibledoctor/translations/{lang}.yml
        # We'll attempt to find it relative to this file
        pkg_path = Path(__file__).resolve().parents[1] / "translations" / f"{lang}.yml"
        translations.update(self.load_from_path(pkg_path))
        # Attempt to load fallback (e.g., 'en') translations and merge missing keys
        fallback_lang = "en"
        if fallback_lang != lang:
            fb_trans = {}
            if project_root:
                pr_fb = Path(project_root) / ".ansibledoctor" / "translations" / f"{fallback_lang}.yml"
                fb_trans.update(self.load_from_path(pr_fb))
            pkg_fb_path = Path(__file__).resolve().parents[1] / "translations" / f"{fallback_lang}.yml"
            fb_trans.update(self.load_from_path(pkg_fb_path))
            # Merge fallback keys for any missing entries
            for k, v in fb_trans.items():
                translations.setdefault(k, v)
        return TranslationProvider(translations=translations, lang=lang)
