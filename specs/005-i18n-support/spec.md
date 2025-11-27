# Feature Specification: Internationalization (i18n) Support

**Feature Branch**: `005-i18n-support`  
**Created**: 2025-11-26  
**Milestone**: v0.6.0  
**Prerequisites**: v0.5.0 (Collection Documentation) COMPLETE ✅  
**Status**: Planned (Blocked until v0.5.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Enable multi-language documentation generation for ansible-doctor-enhanced. Support multiple languages (English, French, German by default, extensible to more) with translation files, i18n template markers, and configurable language settings. Generate documentation in parallel for all enabled languages with organized output structure.

## What is i18n Documentation?

Internationalization (i18n) allows documentation to be generated in multiple languages from a single codebase. This feature provides:

- **Translation System**: YAML-based translation files for each supported language
- **Template i18n Markers**: Jinja2 filter `{{ t('key') }}` for translatable strings
- **Language Configuration**: Configure default, enabled, and fallback languages in `.ansibledoctor.yml`
- **Multi-Language Output**: Generate docs for multiple languages with structure `docs/lang/{code}/`
- **CLI Override**: Command-line flags to generate specific languages on demand

**Supported Languages (Default)**:
- **English (en)**: Default language, always available
- **French (fr)**: Full translation support
- **German (de)**: Full translation support
- **Extensible**: Users can add custom languages via translation files

**Output Structure**:
```
docs/
└── lang/
    ├── en/                    # English documentation
    │   ├── roles/
    │   │   └── webserver/
    │   │       └── README.md
    │   └── collections/
    │       └── my_namespace.my_collection/
    │           └── README.md
    ├── fr/                    # French documentation
    │   ├── roles/
    │   └── collections/
    └── de/                    # German documentation
        ├── roles/
        └── collections/
```

## User Scenarios

### US11 - Configure Language Settings (Priority: P1) 🎯 MVP

As a documentation maintainer, I want to configure supported languages in `.ansibledoctor.yml` so that I can control which languages are generated and set default/fallback behavior.

**Independent Test**: Create `.ansibledoctor.yml` with language config → ansible-doctor respects settings

**Acceptance Scenarios**:
1. **Given** `.ansibledoctor.yml` with `languages.default: fr`, **When** generating docs without CLI flags, **Then** French is the primary language generated
2. **Given** `languages.enabled: [en, fr]`, **When** generating docs, **Then** only English and French documentation is created
3. **Given** `languages.fallback: en`, **When** translation key is missing in French, **Then** use English translation as fallback
4. **Given** no language config, **When** generating docs, **Then** default to English only
5. **Given** `languages.detect_system: true`, **When** generating docs, **Then** auto-enable system locale language if translation exists

**Configuration Schema**:
```yaml
# .ansibledoctor.yml
languages:
  default: en              # Default language (required)
  enabled:                 # Languages to generate (list)
    - en
    - fr
    - de
  fallback: en            # Fallback when translation missing
  detect_system: false    # Auto-detect system locale (optional)

output:
  structure: hierarchical  # Output structure type
  per_language: true      # Generate separate dirs per language
  base_dir: docs          # Base output directory
```

---

### US12 - i18n Template Markers (Priority: P1)

As a template author, I want to use `{{ t('key') }}` markers in templates so that strings are translated based on the current language context.

**Independent Test**: Template with `{{ t('overview.title') }}` → Renders "Overview" (en), "Aperçu" (fr), "Übersicht" (de)

**Acceptance Scenarios**:
1. **Given** template with `{{ t('section.title') }}`, **When** rendering in English, **Then** lookup `section.title` in `translations/en.yml`
2. **Given** translation key with placeholders `{{ t('install.version', version='1.0.0') }}`, **When** rendering, **Then** substitute variables in translated string
3. **Given** missing translation key, **When** rendering, **Then** fall back to fallback language, or return key name if all fail
4. **Given** nested key like `{{ t('meta.author.name') }}`, **When** rendering, **Then** resolve nested YAML structure
5. **Given** plural forms `{{ t('items.count', count=5) }}`, **When** rendering, **Then** select correct plural form based on count

**Translation File Format** (`translations/en.yml`):
```yaml
# translations/en.yml
overview:
  title: "Overview"
  description: "Role description and metadata"

installation:
  title: "Installation"
  instructions: "Install this role using ansible-galaxy:"
  version: "Version {version}"

meta:
  author:
    name: "Author"
    email: "Email"
  license: "License"
  
variables:
  title: "Variables"
  required: "Required"
  optional: "Optional"
  default_value: "Default: {value}"

tasks:
  title: "Tasks"
  count:
    one: "{count} task"
    other: "{count} tasks"
```

**Template Usage**:
```jinja2
{# role.j2 template with i18n #}
# {{ role.name }}

## {{ t('overview.title') }}

{{ role.description }}

## {{ t('installation.title') }}

{{ t('installation.instructions') }}

```bash
ansible-galaxy install {{ role.name }}
```

## {{ t('variables.title') }}

{% for var in role.variables %}
### `{{ var.name }}`

{% if var.required %}**{{ t('variables.required') }}**{% else %}{{ t('variables.optional') }}{% endif %}

{{ t('variables.default_value', value=var.default) }}
{% endfor %}
```

---

### US13 - Multi-Language Documentation Generation (Priority: P1)

As a documentation maintainer, I want to generate documentation in multiple languages simultaneously so that all language versions stay synchronized.

**Independent Test**: Run `ansible-doctor generate role/ --languages en,fr,de` → Creates `docs/lang/en/`, `docs/lang/fr/`, `docs/lang/de/`

**Acceptance Scenarios**:
1. **Given** enabled languages [en, fr, de], **When** generating role docs, **Then** create 3 README files in respective language directories
2. **Given** `--languages fr` CLI flag, **When** generating, **Then** override config and generate French only
3. **Given** collection with 5 roles, **When** generating multi-language, **Then** generate docs for all roles in all languages
4. **Given** output directory exists, **When** generating, **Then** overwrite existing language-specific files without affecting other languages
5. **Given** 3 enabled languages, **When** generating, **Then** complete generation in <5s (SC-006 performance target)

**CLI Examples**:
```bash
# Generate all enabled languages (from config)
ansible-doctor generate role/webserver

# Generate specific languages only
ansible-doctor generate role/webserver --languages en,fr

# Generate single language
ansible-doctor generate role/webserver --language de

# Generate with custom output structure
ansible-doctor generate role/webserver --output-dir custom_docs/

# Generate collection in multiple languages
ansible-doctor collection generate my_namespace.my_collection --languages en,fr,de
```

**Output Structure**:
```
docs/
└── lang/
    ├── en/
    │   └── roles/
    │       └── webserver/
    │           └── README.md    # English version
    ├── fr/
    │   └── roles/
    │       └── webserver/
    │           └── README.md    # French version
    └── de/
        └── roles/
            └── webserver/
                └── README.md    # German version
```

---

## Success Criteria

**SC-001**: Parse language configuration from `.ansibledoctor.yml` with schema validation (default, enabled, fallback, detect_system)  
**SC-002**: Load translation files for enabled languages from `ansibledoctor/translations/{lang}.yml` with fallback chain  
**SC-003**: Provide Jinja2 template filter `t(key, **kwargs)` for translating keys with variable substitution  
**SC-004**: Generate documentation for each enabled language in separate `docs/lang/{code}/` subdirectories  
**SC-005**: CLI flag `--languages` or `--language` overrides configuration file settings  
**SC-006**: Multi-language generation (3 languages) completes in <5s for typical role (10 variables, 5 tasks)  
**SC-007**: Missing translation keys fall back to fallback language, then display key name with warning  
**SC-008**: Support nested translation keys using dot notation (e.g., `section.subsection.key`)  
**SC-009**: Support variable substitution in translations using `{variable}` syntax  
**SC-010**: Support plural forms in translations with `one`/`other` keys based on count parameter  
**SC-011**: Embed default translations (en, fr, de) in package for zero-configuration experience  
**SC-012**: Allow custom translation files in project `.ansibledoctor/translations/` directory

## Technical Constraints

**TC-001**: Reuse existing TemplateEngine from Feature 002 (no new rendering system)  
**TC-002**: Support YAML translation files only (no JSON, no gettext .po files)  
**TC-003**: Support system locale detection via Python `locale` module (optional feature)  
**TC-004**: Translation keys must use dot notation for hierarchical structure (`section.key`)  
**TC-005**: Translation files must be UTF-8 encoded for international character support  
**TC-006**: Language codes follow ISO 639-1 (2-letter codes: en, fr, de, es, it, etc.)  
**TC-007**: Parallel language generation uses same parsed role data (no re-parsing per language)  
**TC-008**: Template filter `t()` must be thread-safe for potential future parallelization

## Out of Scope

- Right-to-left (RTL) language support (Arabic, Hebrew) - deferred to v0.7.0
- Translation management UI or editor
- Automatic translation via machine translation APIs
- Translation file format conversion (gettext, XLIFF, etc.)
- Language negotiation based on HTTP Accept-Language headers
- Date/number formatting localization (use default formats)
- Translation file validation/linting (manual YAML validation only)

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.5.0 (Collection Documentation) is COMPLETE and stable
2. ✅ TemplateEngine from Feature 002 supports custom filters
3. ✅ Template system can handle multiple render passes with different contexts
4. ✅ Output directory management supports hierarchical structures
5. ✅ No critical bugs in role or collection documentation generation

**Gate**: This feature CANNOT start until v0.5.0 is tagged and stable.

## Architecture Overview

### Components

1. **LanguageConfig**: Pydantic model for language configuration
   - Fields: default, enabled, fallback, detect_system
   - Validation: ISO 639-1 language codes

2. **TranslationLoader**: Service for loading translation files
   - Embedded translations (package resources)
   - Custom translations (`.ansibledoctor/translations/`)
   - Fallback chain resolution

3. **TranslationProvider**: Translation resolution service
   - Key lookup with dot notation
   - Variable substitution
   - Plural form selection
   - Fallback language handling

4. **i18n TemplateFilter**: Jinja2 filter `t(key, **kwargs)`
   - Registered in TemplateEngine
   - Context-aware (current language)
   - Thread-safe implementation

5. **MultiLanguageGenerator**: Orchestrator for multi-language generation
   - Iterate over enabled languages
   - Set language context per render
   - Create language-specific output directories

### Data Flow

```
.ansibledoctor.yml
    ↓
LanguageConfig (parse & validate)
    ↓
TranslationLoader (load .yml files)
    ↓
TranslationProvider (ready for lookups)
    ↓
TemplateEngine (with t() filter)
    ↓
For each language:
    - Set language context
    - Render template
    - Write to docs/lang/{code}/
```

## Dependencies

### Existing Features
- **Feature 001** (Role Parser): Parse role data (unchanged)
- **Feature 002** (Doc Generator): TemplateEngine, custom filters, output formats
- **Feature 004** (Collection Support): Collection documentation (i18n applied)

### New Dependencies
- `ruamel.yaml`: Already in project (for translation files)
- `pydantic`: Already in project (for LanguageConfig model)
- No new external dependencies required

## Acceptance Tests

### Integration Tests
1. Generate role docs with 3 languages → Verify 3 output files with translated content
2. Missing translation key → Verify fallback to English, warning logged
3. Custom translation file overrides embedded → Verify custom translation used
4. CLI `--languages fr,de` → Verify only French and German generated
5. Variable substitution in translation → Verify `{version}` replaced with actual value
6. Plural forms with different counts → Verify correct form selected

### Performance Tests
1. Generate role docs for 3 languages → Complete in <5s
2. Generate collection (10 roles) for 3 languages → Complete in <30s

## Roadmap Impact

**v0.6.0 (This Feature)**:
- i18n foundation established
- English, French, German support
- Multi-language role and collection documentation

**v0.7.0 (Feature 006 - Project Docs)**:
- Project documentation uses i18n system
- Unified translation keys across all levels

**v0.8.0+**:
- Additional languages (Spanish, Italian, Portuguese, etc.)
- RTL language support
- Advanced localization (dates, numbers)

---

*Feature specification created following Constitution Article X (DDD), Article III (TDD), and SpecKit methodology*
