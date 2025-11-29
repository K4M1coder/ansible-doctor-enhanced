"""Tests for translation pluralization behavior using Babel when available.

These tests exercise the TranslationProvider.t() plural selection for
English, French and German locales using provided translation keys.
"""
from __future__ import annotations

from ansibledoctor.translation.provider import TranslationProvider


def test_pluralization_basic_en():
    translations = {
        "items.one": "{count} item",
        "items.other": "{count} items",
    }
    provider = TranslationProvider(translations, lang="en")

    assert provider.t("items", count=1) == "1 item"
    assert provider.t("items", count=2) == "2 items"


def test_pluralization_basic_fr():
    translations = {
        "items.one": "{count} article",
        "items.other": "{count} articles",
    }
    provider = TranslationProvider(translations, lang="fr")

    assert provider.t("items", count=1) == "1 article"
    assert provider.t("items", count=2) == "2 articles"


def test_pluralization_basic_de():
    translations = {
        "items.one": "{count} Element",
        "items.other": "{count} Elemente",
    }
    provider = TranslationProvider(translations, lang="de")

    assert provider.t("items", count=1) == "1 Element"
    assert provider.t("items", count=7) == "7 Elemente"
