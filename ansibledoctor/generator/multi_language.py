"""Multi-language generator utilities.

This module contains the MultiLanguageGenerator class which is responsible
for generating project documentation for multiple languages. It takes a
parsed Project and uses a TranslationLoader to render language-specific
output directories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ansibledoctor.generator.project_generator import ProjectDocumentationGenerator
from ansibledoctor.models.project import Project
from ansibledoctor.translation.loader import TranslationLoader
from ansibledoctor.utils.slug import project_slug


class MultiLanguageGenerator:
    """Generate project documentation in multiple languages.

    The generator takes an already-parsed `Project` and renders per-language
    outputs under `docs/lang/{code}/...` or a custom `output_dir`.
    """

    def __init__(self, loader: TranslationLoader | None = None):
        self.loader = loader or TranslationLoader()

    def generate(
        self,
        project: Project,
        languages: Iterable[str],
        output_dir: Path | None = None,
        format: str = "markdown",
        template_path: str | None = None,
        legacy_output: bool = False,
    ) -> None:
        for lang in languages:
            provider = self.loader.load(lang, Path(project.path))
            gen = ProjectDocumentationGenerator(project=project, translation_provider=provider)
            if output_dir is not None:
                target = (
                    Path(output_dir) / "lang" / lang / project_slug(project.name)
                    if not legacy_output
                    else Path(output_dir) / "lang" / lang
                )
            else:
                if not legacy_output:
                    target = (
                        Path(project.path) / "docs" / "lang" / lang / project_slug(project.name)
                    )
                else:
                    target = Path(project.path) / "docs" / "lang" / lang
            gen.generate(
                format=format,
                output_dir=target,
                template_path=template_path,
                legacy_output=legacy_output,
            )
