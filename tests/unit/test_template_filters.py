from ansibledoctor.generator.engine import TemplateEngine
from ansibledoctor.translation.loader import TranslationProvider


def test_t_translation_global_and_filter():
    translations = {
        "greet": "Hello {name}",
        "items.one": "1 item",
        "items.other": "{count} items",
    }
    provider = TranslationProvider(translations)
    engine = TemplateEngine.create(translation_provider=provider)
    out1 = engine.render_string("{{ t('greet', name='Alice') }}")
    assert out1.strip() == "Hello Alice"
    out2 = engine.render_string("{{ 'greet' | t(name='Bob') }}")
    assert out2.strip() == "Hello Bob"
    out3 = engine.render_string("{{ t('items', count=1) }}")
    assert out3.strip() == "1 item"
    out4 = engine.render_string("{{ 'items' | t(count=3) }}")
    assert out4.strip() == "3 items"
