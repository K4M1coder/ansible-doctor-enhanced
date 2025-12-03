# Feature Specification: Indexes & Navigation

**Feature Branch**: `011-indexes-navigation`  
**Created**: 2025-12-02  
**Milestone**: v0.10.0  
**Prerequisites**: v0.8.0 (Template Customization) PLANNED  
**Status**: Draft

**Cross-Spec Dependencies**:
- **Consumes Spec 013**: CrossReference model and LinkValidator for cross-references (US7 moved to Spec 013)
- **Consumes Spec 012**: MermaidBuilder can use SchemaService for diagram validation
- **Integrates Spec 009**: Index generation metrics feed into ExecutionReport

## Objective

**NEW CAPABILITY** (extends existing documentation generation)

Generate comprehensive index pages and navigation structures for ansible-doctor-enhanced documentation. Support multiple display formats (full pages, embedded sections), various visualization styles (lists, trees, nested tables, schemas), and indexing of all Ansible component types (collections, roles, plugins, modules, playbooks).

## What is Indexes & Navigation?

Indexes & Navigation provides structured navigation and discovery for documentation:

- **Index Pages**: Dedicated pages listing all components of a type (all roles, all collections, etc.)
- **Section Indexes**: Embedded index sections within parent documentation (e.g., role list in collection doc)
- **Hierarchical Views**: Tree structures showing parent-child relationships (project → collections → roles)
- **Multiple Formats**: Lists, trees, nested tables, diagrams/schemas for different visualization needs
- **Cross-References**: Links between related components (role dependencies, plugin usage)
- **Filtering**: Filter indexes by criteria (namespace, tags, type, status)

**Indexed Component Types**:
- **Collections**: Ansible Galaxy collections with namespace.name
- **Roles**: Individual Ansible roles with metadata
- **Plugins**: Filter, lookup, callback, inventory plugins
- **Modules**: Custom Ansible modules
- **Playbooks**: Project playbooks with descriptions

**Display Formats**:

1. **Full Page Index**: Dedicated `index.md` or `roles/index.md` page
2. **Section Index**: Embedded `## Roles` section within collection README
3. **Filtered Index**: Subset of items matching criteria (e.g., "roles with tag 'database'")

**Visualization Styles**:

```markdown
# List Style (simple)
- webserver - Configure web servers
- database - Install and configure databases
- monitoring - Setup monitoring stack

# Tree Style (hierarchical)
my_namespace.my_collection/
├── roles/
│   ├── webserver/
│   ├── database/
│   └── monitoring/
└── plugins/
    ├── modules/
    │   └── my_module.py
    └── filters/
        └── my_filter.py

# Table Style (detailed)
| Name | Description | Tags | Dependencies |
|------|-------------|------|--------------|
| webserver | Configure web servers | web, nginx | common |
| database | Install databases | db, postgres | common |

# Nested Table Style (children with their children)
| Collection | Roles | Plugins |
|------------|-------|---------|
| my_namespace.infrastructure | webserver, database | 2 modules, 1 filter |
| my_namespace.monitoring | prometheus, grafana | 3 modules |

# Schema/Diagram Style (Mermaid)
graph TD
    Project --> Collection1
    Project --> Collection2
    Collection1 --> Role1
    Collection1 --> Role2
```

## User Scenarios & Testing

### User Story 1 - Generate Role Index Page (Priority: P1) 🎯 MVP

As a collection maintainer, I want to generate a dedicated role index page so that users can discover all roles in my collection with descriptions and links.

**Why this priority**: Role discovery is fundamental. Users need to see what roles exist before they can use them.

**Independent Test**: Run `ansible-doctor generate collection/ --include-index` → Creates `roles/index.md` with all roles listed.

**Acceptance Scenarios**:

1. **Given** a collection with 5 roles, **When** generating docs with index enabled, **Then** `roles/index.md` is created listing all 5 roles with descriptions
2. **Given** roles have tags defined, **When** index is generated, **Then** tags are displayed and can be used to filter
3. **Given** `--index-format list|table|tree` flag, **When** index is generated, **Then** output uses specified visualization style
4. **Given** roles have dependencies, **When** index is generated, **Then** dependencies are shown with links to dependent role docs
5. **Given** collection has no roles, **When** generating index, **Then** index page shows "No roles in this collection" message

---

### User Story 2 - Generate Hierarchical Project Index (Priority: P1) 🎯 MVP

As a project maintainer, I want to generate a hierarchical index showing collections, their roles, and plugins so that new team members can understand the project structure at a glance.

**Why this priority**: Project overview is essential for onboarding. Hierarchical view shows relationships between components.

**Independent Test**: Run `ansible-doctor generate project/ --index-style tree` → Creates index with tree visualization showing full hierarchy.

**Acceptance Scenarios**:

1. **Given** project with 2 collections containing 3 roles each, **When** generating tree index, **Then** tree shows Project → Collections → Roles hierarchy
2. **Given** project with plugins, **When** generating index, **Then** plugins are shown under their collection with type labels (module, filter, etc.)
3. **Given** `--index-depth 2` flag, **When** generating index, **Then** tree shows only 2 levels deep (collections and their direct children)
4. **Given** playbooks in project, **When** generating index, **Then** playbooks section lists all playbooks with descriptions
5. **Given** ASCII tree requested, **When** generating, **Then** output uses ASCII characters (├── └──) for tree structure

---

### User Story 3 - Embed Section Index in Documentation (Priority: P1) 🎯 MVP

As a documentation reader, I want to see a role list section embedded in the collection README so that I don't need to navigate to a separate page.

**Why this priority**: Inline discovery improves user experience. Most users start with README, not index pages.

**Independent Test**: Generate collection docs → README includes "## Roles" section with role list automatically.

**Acceptance Scenarios**:

1. **Given** collection template has `{{ index('roles') }}` marker, **When** generating, **Then** role list is embedded at that location
2. **Given** `index('roles', format='table')` call, **When** generating, **Then** table format is used for embedded section
3. **Given** `index('plugins', group_by='type')` call, **When** generating, **Then** plugins are grouped by type (modules, filters, etc.)
4. **Given** `index('roles', limit=5)` call, **When** generating, **Then** only first 5 roles are shown with "and X more..." link
5. **Given** `index('roles', filter='tag:database')` call, **When** generating, **Then** only roles with 'database' tag are included

---

### User Story 4 - Generate Nested Tables (Priority: P2)

As a documentation reader viewing a large project, I want to see nested tables showing collections with their children so that I can compare collections side by side.

**Why this priority**: Nested tables provide compact overview for large projects. Useful for comparing collections.

**Independent Test**: Generate project index with `--index-style nested-table` → Table shows collections with inline role/plugin summaries.

**Acceptance Scenarios**:

1. **Given** 3 collections with varying numbers of roles, **When** generating nested table, **Then** each row shows collection name, role count, plugin count
2. **Given** nested table with expandable detail, **When** clicking collection row, **Then** children (roles, plugins) are revealed
3. **Given** `--nested-depth 2` flag, **When** generating, **Then** table shows collection → roles but not role details
4. **Given** HTML output, **When** generating nested table, **Then** table is interactive (sortable columns, expandable rows)
5. **Given** Markdown output, **When** generating nested table, **Then** static table with children listed inline (comma-separated)

---

### User Story 5 - Generate Mermaid Diagrams (Priority: P2)

As a documentation reader, I want to see visual schema/diagrams showing project structure so that I can understand component relationships visually.

**Why this priority**: Visual diagrams aid comprehension for complex projects. Mermaid is widely supported.

**Independent Test**: Generate project docs with `--index-style diagram` → Mermaid graph showing component hierarchy.

**Acceptance Scenarios**:

1. **Given** project with collections and roles, **When** generating diagram, **Then** Mermaid graph shows hierarchy with clickable nodes
2. **Given** role dependencies, **When** generating diagram, **Then** dependency arrows connect dependent roles
3. **Given** `diagram('flowchart')` type, **When** generating, **Then** top-down flowchart is produced
4. **Given** `diagram('mindmap')` type, **When** generating, **Then** mind map style diagram is produced
5. **Given** very large project (100+ components), **When** generating diagram, **Then** diagram is clustered by collection to avoid clutter

---

### User Story 6 - Filter and Search Indexes (Priority: P2)

As a documentation reader, I want to filter indexes by criteria so that I can find specific components quickly.

**Why this priority**: Large projects need filtering. Finding specific roles among 50+ is impractical without filters.

**Independent Test**: Generate index with `--filter 'tag:web'` → Only components matching filter are included.

**Acceptance Scenarios**:

1. **Given** `--filter 'tag:database'` flag, **When** generating index, **Then** only roles/collections with database tag are included
2. **Given** `--filter 'namespace:my_namespace'` flag, **When** generating, **Then** only components in that namespace are included
3. **Given** HTML output with filter enabled, **When** viewing in browser, **Then** client-side filter/search box is available
4. **Given** multiple filters `--filter 'tag:web' --filter 'status:stable'`, **When** generating, **Then** components matching ALL filters are included (AND logic)
5. **Given** filter matches no components, **When** generating, **Then** message "No components match filter criteria" is shown

---

### User Story 7 - Cross-Reference Links (Priority: P3)

As a documentation reader, I want indexes to include cross-reference links so that I can navigate between related components.

**Why this priority**: Cross-references enable documentation navigation. Important but not blocking for basic indexes.

**Independent Test**: Generate role index → Each role links to its documentation page, dependencies link to their pages.

**Acceptance Scenarios**:

1. **Given** role in index, **When** viewing index, **Then** role name is clickable link to role documentation
2. **Given** role has dependencies, **When** viewing index, **Then** dependency names link to their documentation pages
3. **Given** role is used by playbooks, **When** viewing index, **Then** "Used by" column shows playbook links
4. **Given** broken link (target doc doesn't exist), **When** generating, **Then** link is rendered as plain text with warning logged
5. **Given** `--validate-links` flag, **When** generating, **Then** all cross-reference links are validated, errors reported

---

### Edge Cases

- What happens when project has 500+ roles?
  - MUST paginate index (50 per page default) or provide virtual scrolling in HTML
- What happens when role has circular dependencies?
  - MUST detect cycle, show warning icon, prevent infinite recursion in tree view
- How does system handle roles with no description?
  - MUST show role name with "[No description]" placeholder, log warning
- What happens when collection namespace contains special characters?
  - MUST escape for Markdown/HTML, use slug for file paths
- What happens when index template marker is malformed?
  - MUST show template error with line number, suggestion to check syntax
- How does system handle mixed language indexes (some docs in EN, some in FR)?
  - MUST generate language-specific indexes, link to same-language docs, fallback to default

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate standalone index pages for each component type (roles, collections, plugins, modules, playbooks)
- **FR-002**: System MUST support embedding index sections in parent documentation via template markers
- **FR-003**: System MUST support visualization styles: list, table, tree, nested-table, diagram (Mermaid)
- **FR-004**: System MUST index all Ansible component types: collections, roles, plugins, modules, playbooks
- **FR-005**: System MUST support hierarchical indexing showing parent-child relationships to configurable depth
- **FR-006**: System MUST support filtering indexes by: tag, namespace, type, status, custom metadata
- **FR-007**: System MUST generate cross-reference links from index items to their documentation pages
- **FR-008**: System MUST validate cross-reference links and warn on broken links
- **FR-009**: System MUST support pagination for large indexes (configurable items per page)
- **FR-010**: Template marker `{{ index('type', **options) }}` MUST support: format, limit, filter, group_by, depth
- **FR-011**: Tree visualization MUST use ASCII characters (├── └── │) for text output
- **FR-012**: Mermaid diagrams MUST include clickable nodes linking to documentation
- **FR-013**: HTML output MUST support interactive features (sortable tables, expandable rows, client-side filtering)
- **FR-014**: System MUST handle circular dependencies in tree views by detecting cycles and showing warning
- **FR-015**: System MUST respect language configuration and generate language-specific indexes

### Key Entities

- **IndexPage**: Standalone page listing components of a type with metadata and navigation
- **SectionIndex**: Embedded index rendered within parent documentation
- **IndexItem**: Single entry in index with name, description, tags, links, children
- **IndexFilter**: Criteria for filtering index content (tag, namespace, type, custom)
- **IndexFormat**: Visualization style (list, table, tree, nested-table, diagram)
- **CrossReference**: Link between index item and its documentation or related components

## Success Criteria

### Measurable Outcomes

- **SC-001**: Index pages are generated within 200ms per 100 components
- **SC-002**: All component types are discoverable via index navigation
- **SC-003**: Users can filter indexes to find specific components in under 5 seconds
- **SC-004**: Tree visualizations correctly show 5+ levels of hierarchy
- **SC-005**: 95% of cross-reference links resolve to valid documentation pages
- **SC-006**: Mermaid diagrams render correctly in GitHub/GitLab/standard Markdown viewers
- **SC-007**: HTML indexes support client-side filtering without page reload

## Technical Constraints

- **TC-001**: MUST reuse existing TemplateEngine for index generation
- **TC-002**: MUST follow existing output structure conventions (`docs/lang/{code}/`)
- **TC-003**: Mermaid diagrams MUST be compatible with GitHub-flavored Markdown
- **TC-004**: Index template markers MUST be valid Jinja2 syntax
- **TC-005**: Tree ASCII output MUST work on all terminals (no Unicode box-drawing unless explicitly requested)
