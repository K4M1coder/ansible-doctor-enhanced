# Feature Specification: Documentation Generator with Templates

**Feature Branch**: `002-doc-generator`  
**Created**: 2025-11-16  
**Updated**: 2025-11-17
**Status**: In Progress  
**Input**: Generate professional documentation from parsed Ansible role data (from Feature 001) using customizable Jinja2 templates with multiple output formats

## User Scenarios & Testing *(mandatory)*

### User Story 5 - Generate Markdown Documentation from Parsed Role (Priority: P1) 🎯 MVP

As a DevOps engineer, I want to generate clean Markdown documentation from my Ansible role so that I can commit README.md files to my role repositories automatically.

**Why this priority**: Most critical feature - provides immediate value by automating README generation. Markdown is the most common format for role documentation on GitHub/GitLab.

**Independent Test**: Run `ansible-doctor generate my-role/ --format markdown` → produces README.md with sections for metadata, variables, tags, examples, structured from parsed JSON data.

**Acceptance Scenarios**:

1. **Given** a parsed role JSON file, **When** I run `generate --format markdown`, **Then** a README.md is created with properly formatted sections (Title, Description, Requirements, Role Variables, Tags, Examples, TODOs)
2. **Given** a role with no variables, **When** generating documentation, **Then** the "Role Variables" section is omitted gracefully
3. **Given** a role with @example blocks, **When** generating Markdown, **Then** code blocks are properly fenced with language hints
4. **Given** a custom template path, **When** I run `generate --template custom.md.j2`, **Then** my custom template is used instead of default
5. **Given** output path specified, **When** I run `generate --output docs/README.md`, **Then** documentation is written to that location

---

### User Story 6 - Generate HTML Documentation with Styling (Priority: P2)

As a documentation lead, I want to generate HTML documentation with CSS styling so that I can publish role documentation to internal wikis or static sites with a professional appearance.

**Why this priority**: Adds value for teams needing web-based documentation. HTML enables better styling, navigation, and integration with doc sites.

**Independent Test**: Run `ansible-doctor generate my-role/ --format html` → produces index.html with embedded CSS, navigation menu, and proper semantic HTML structure.

**Acceptance Scenarios**:

1. **Given** a parsed role, **When** generating HTML with default template, **Then** output includes embedded CSS for typography, code blocks, and responsive layout
2. **Given** HTML output, **When** viewing in browser, **Then** I see a table of contents, syntax-highlighted code blocks, and mobile-responsive layout
3. **Given** multiple roles, **When** generating HTML for each, **Then** I can link them together with relative paths in a navigation structure
4. **Given** a custom CSS file, **When** I run `generate --format html --css custom.css`, **Then** my stylesheet is embedded/linked in the output

---

### User Story 7 - Generate reStructuredText for Sphinx Integration (Priority: P3)

As a technical writer, I want to generate reStructuredText (.rst) documentation so that I can integrate role documentation into our Sphinx-based documentation system.

**Why this priority**: Lower priority but important for organizations using Sphinx. Enables integration with existing Python/Ansible documentation pipelines.

**Independent Test**: Run `ansible-doctor generate my-role/ --format rst` → produces index.rst with proper reST directives, cross-references, and Sphinx-compatible structure.

**Acceptance Scenarios**:

1. **Given** a parsed role, **When** generating RST format, **Then** output uses proper directives (.. code-block::, .. note::, .. warning::)
2. **Given** TODO items with priorities, **When** generating RST, **Then** critical/high priority items are formatted as .. warning:: directives
3. **Given** role dependencies, **When** generating RST, **Then** cross-references use :doc: or :ref: directives for Sphinx linking

---

### Edge Cases

- **Empty role**: What if role has only meta/main.yml with minimal data? → Generate minimal doc with disclaimer
- **Missing templates**: What if specified template doesn't exist? → Error with clear message, suggest available templates
- **Invalid JSON input**: What if parser output is malformed? → Validate JSON schema before rendering, fail gracefully
- **Large roles**: What if role has 100+ variables? → Ensure template handles pagination/collapsible sections
- **Special characters**: What if variable names/descriptions contain Markdown/HTML syntax? → Proper escaping in templates
- **Binary files**: What if output path exists and is a directory? → Error with clear guidance
- **Template syntax errors**: What if custom template has Jinja2 errors? → Catch TemplateError, show line number and error
- **Circular dependencies**: What if role metadata references itself? → Detect and warn, don't crash

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept JSON input from `ansible-doctor parse` command (Feature 001 output format)
- **FR-002**: System MUST support three output formats: Markdown (.md), HTML (.html), reStructuredText (.rst)
- **FR-003**: System MUST use Jinja2 template engine for rendering documentation
- **FR-004**: System MUST provide default templates for each output format (markdown.j2, html.j2, rst.j2)
- **FR-005**: Users MUST be able to specify custom template files via `--template` flag
- **FR-006**: System MUST validate JSON input against expected schema before rendering
- **FR-007**: System MUST handle missing/optional fields gracefully (e.g., no variables, no examples)
- **FR-008**: System MUST escape special characters appropriately for each output format
- **FR-009**: System MUST support `--output` flag to specify destination file path
- **FR-010**: System MUST log template rendering operations with structured logging
- **FR-011**: System MUST fail with clear error messages for template syntax errors (line number, error description)
- **FR-012**: System MUST preserve code block formatting and language hints from @example annotations
- **FR-013**: HTML output MUST include embedded CSS for professional styling (typography, code blocks, responsive layout)
- **FR-014**: HTML output MUST generate table of contents from role sections
- **FR-015**: RST output MUST use proper Sphinx directives (.. code-block::, .. note::, .. warning::)
- **FR-016**: System MUST support template inheritance (base.j2 → format-specific templates)
- **FR-017**: System MUST provide Jinja2 filters for: markdown_escape, html_escape, rst_escape, format_priority
- **FR-018**: System MUST allow batch generation for multiple roles with `--recursive` flag

### Key Entities *(include if feature involves data)*

- **TemplateEngine**: Manages Jinja2 environment, loads templates, provides custom filters
- **DocumentRenderer**: Protocol defining render(role_data, template, output_format) interface
- **MarkdownRenderer**: Implements DocumentRenderer for Markdown output with proper escaping
- **HtmlRenderer**: Implements DocumentRenderer for HTML with CSS injection and TOC generation
- **RstRenderer**: Implements DocumentRenderer for reStructuredText with Sphinx directives
- **TemplateContext**: Data structure wrapping parsed role JSON with helper methods for templates
- **OutputFormat**: Enum (MARKDOWN, HTML, RST) defining supported formats

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Generate Markdown documentation for a typical role in <100ms (template rendering time only)
- **SC-002**: All three output formats (MD, HTML, RST) produce valid, parseable output (100% format compliance)
- **SC-003**: Users can generate documentation with zero configuration (default templates work out-of-box)
- **SC-004**: Custom templates can override 100% of default template behavior
- **SC-005**: Generated HTML documentation renders correctly on mobile devices (responsive layout verified)
- **SC-006**: 90% test coverage for template rendering logic (TemplateEngine, Renderers)
- **SC-007**: Template syntax errors provide actionable error messages with line numbers
- **SC-008**: Batch generation of 10 roles completes in <2 seconds total
- **SC-009**: Generated Markdown documentation passes markdownlint with no errors (using default template)
- **SC-010**: Generated RST documentation builds successfully in Sphinx with no warnings

## Technical Constraints

- **TC-001**: Must integrate with existing CLI (`ansible-doctor generate` subcommand)
- **TC-002**: Must accept JSON output from Feature 001 parser as input (no schema changes)
- **TC-003**: Must follow project constitution principles (KISS, TDD, DDD)
- **TC-004**: Default templates must be embedded in package (no external file dependencies)
- **TC-005**: Template discovery must support user templates in: `.ansible-doctor/templates/`, `~/.ansible-doctor/templates/`, custom paths
- **TC-006**: Must maintain 80%+ test coverage across all components
- **TC-007**: Python 3.11+ compatibility (leveraging Jinja2 3.1+)
