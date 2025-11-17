# Implementation Plan: Documentation Generator with Templates

**Branch**: `002-doc-generator` | **Date**: 2025-11-17 | **Spec**: [spec.md](./spec.md)  
**Milestone**: v0.3.0 | **Prerequisites**: v0.2.0 (Role Parser) COMPLETE ✅

## Summary

Build a documentation generator that transforms parsed Ansible role data (JSON from Feature 001) into professional documentation using Jinja2 templates. Support three output formats (Markdown, HTML, reStructuredText) with default templates and custom template override capability.

**Primary requirement**: Generate README.md from parsed role with zero configuration  
**Technical approach**: Jinja2 template engine + format-specific renderers + embedded default templates

**Milestone Context**: This is Feature 002, targeting v0.3.0. It establishes the template infrastructure that will be reused for collection (v0.5.0) and project (v0.6.0) documentation. Must achieve stable template system before adding new scope.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:

- Jinja2 3.1+ (template engine)
- markupsafe 2.1+ (escaping)
- Existing: pydantic, click, structlog

**Storage**: File system (JSON input, documentation output)

**Testing**: pytest with 90%+ coverage target

**Target Platform**: Cross-platform (Windows, macOS, Linux)

**Performance Goals**:

- <100ms template rendering per role
- <2s batch generation for 10 roles
- Template caching

**Constraints**:

- Integrate with existing CLI
- Accept Feature 001 JSON format
- Embed default templates in package
- Maintain 80%+ coverage

## Constitution Check

- **Article III (SMART)**: ✅ Specific (3 formats), Measurable (90% coverage, <100ms)
- **Article IV (DDD)**: ✅ Template domain, Renderer services
- **Article V (Observability)**: ✅ Structured logging
- **Article VII (Simplicity)**: ✅ Leverage Jinja2 built-ins
- **Article IX (Documentation)**: ✅ Update README

## Project Structure

### Documentation

```text
specs/002-doc-generator/
├── plan.md              # This file
├── spec.md              # ✅ COMPLETE
├── research.md          # Phase 9
├── data-model.md        # Phase 9
├── quickstart.md        # Phase 9
├── contracts/           # Phase 9
└── tasks.md             # Phase 10
```

### Source Code

```text
ansibledoctor/
├── models/
│   └── output_format.py         # NEW: Enum
├── generator/                   # NEW
│   ├── __init__.py
│   ├── protocols.py             # DocumentRenderer protocol
│   ├── template_engine.py       # Jinja2 + filters
│   ├── renderers/
│   │   ├── markdown.py
│   │   ├── html.py
│   │   └── rst.py
│   └── templates/               # Embedded
│       ├── base.j2
│       ├── markdown.j2
│       ├── html.j2
│       ├── rst.j2
│       └── styles.css
├── cli/
│   └── __init__.py              # MODIFY: Add generate command
└── utils/
    └── template_loader.py       # NEW

tests/
├── unit/generator/              # NEW
│   ├── test_template_engine.py
│   ├── test_markdown_renderer.py
│   ├── test_html_renderer.py
│   └── test_rst_renderer.py
└── integration/
    └── test_generator_integration.py
```

## Implementation Phases

### Phase 9: Foundation & Research

**Goal**: Establish generator architecture and Jinja2 infrastructure

**Tasks**:

1. Research Jinja2 best practices (escaping, filters, inheritance)
2. Create OutputFormat enum (MARKDOWN, HTML, RST)
3. Define DocumentRenderer protocol
4. Create TemplateEngine class with custom filters
5. Setup template loader with discovery logic
6. Create base.j2 template structure
7. Unit tests for TemplateEngine and filters

**Deliverables**: generator/ module, protocols, template infrastructure

---

### Phase 10: US5 - Markdown Generator (MVP)

**Goal**: Generate clean Markdown documentation

**Tasks**:

1. Implement MarkdownRenderer with escaping
2. Create markdown.j2 template (metadata, variables, tags, examples)
3. Add markdown_escape filter
4. Integrate `generate` command in CLI
5. Add --format, --template, --output flags
6. Unit tests for MarkdownRenderer
7. Integration test: parse → generate → verify README.md

**Deliverables**: Working `ansible-doctor generate role/ --format markdown`

---

### Phase 11: US6 & US7 - HTML and RST

**Goal**: Add HTML and reStructuredText support

**Tasks**:

1. Implement HtmlRenderer with CSS injection
2. Create html.j2 template + styles.css
3. Add TOC generation for HTML
4. Implement RstRenderer with Sphinx directives
5. Create rst.j2 template
6. Add html_escape and rst_escape filters
7. Unit tests for both renderers
8. Integration tests for all formats
9. Add --recursive flag for batch generation
10. Update README and CHANGELOG

**Deliverables**: Complete documentation generator with 3 formats

## Success Metrics

- ✅ 90%+ test coverage for generator module
- ✅ <100ms rendering time per role
- ✅ All 3 formats produce valid output
- ✅ Zero-config works with defaults
- ✅ Custom templates fully override defaults

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Jinja2 template complexity | Medium | Use simple filters, clear examples in docs |
| Performance with large roles | Low | Implement template caching, lazy evaluation |
| Custom template errors | Medium | Detailed error messages with line numbers |
| Cross-platform paths | Low | Use pathlib throughout |

## Next Steps

1. Mark T118-T120 complete in todo list
2. Create research.md for Jinja2 analysis
3. Define data-model.md for template context
4. Build contracts/ with protocol definitions
5. Generate tasks.md with TDD breakdown
