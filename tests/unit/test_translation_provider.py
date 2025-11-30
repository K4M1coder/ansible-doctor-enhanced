from ansibledoctor.translation.provider import TranslationProvider


class TestTranslationProvider:
    def test_get_simple_key(self):
        provider = TranslationProvider({"project.title": "Project"}, lang="en")
        assert provider.get("project.title") == "Project"

    def test_get_missing_key(self):
        provider = TranslationProvider({}, lang="en")
        assert provider.get("missing.key") == "missing.key"
        assert provider.get("missing.key", default="Fallback") == "Fallback"

    def test_get_with_formatting(self):
        provider = TranslationProvider({"welcome": "Hello {name}"}, lang="en")
        assert provider.get("welcome", name="Alice") == "Hello Alice"

    def test_t_simple_string(self):
        provider = TranslationProvider({"hello": "Hi"}, lang="en")
        assert provider.t("hello") == "Hi"

    def test_t_missing_key_returns_key(self):
        provider = TranslationProvider({}, lang="en")
        assert provider.t("missing") == "missing"

    def test_t_with_variable_substitution(self):
        provider = TranslationProvider({"greet": "Hello {name}"}, lang="en")
        assert provider.t("greet", name="Bob") == "Hello Bob"

    def test_t_plural_one(self):
        provider = TranslationProvider(
            {"items.one": "1 item", "items.other": "{count} items"}, lang="en"
        )
        assert provider.t("items", count=1) == "1 item"
        assert provider.t("items", count=3) == "3 items"

    def test_t_plural_missing_form(self):
        provider = TranslationProvider({"items.other": "{count} items"}, lang="en")
        # when 'one' missing, fallback to other
        assert (
            provider.t("items", count=1) == "1 items"
            or provider.t("items", count=1) == "{count} items"
        )
