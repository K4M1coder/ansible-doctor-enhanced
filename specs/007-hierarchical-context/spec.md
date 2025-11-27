# Feature Specification: Hierarchical Context Detection

**Feature Branch**: `007-hierarchical-context`  
**Created**: 2025-11-26  
**Milestone**: v0.8.0  
**Prerequisites**: v0.7.0 (Project Documentation) COMPLETE ✅  
**Status**: Planned (Blocked until v0.7.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Automatically detect parent context when documenting Ansible components (roles, collections, projects). Generate breadcrumb navigation and contextual overviews showing component relationships and hierarchy. Enable users to understand component placement within larger project structures without manual configuration.

## What is Hierarchical Context Detection?

Hierarchical Context Detection analyzes directory structure to determine relationships between Ansible components:

- **Parent Detection**: Automatically find parent collection or project for a role
- **Breadcrumb Navigation**: Generate clickable breadcrumbs showing hierarchy (Project > Collection > Role)
- **Sibling Discovery**: List related components at the same level (other roles in collection, other collections in project)
- **Relative Linking**: Generate documentation cross-references with relative paths
- **Standalone Mode**: Optional flag to disable context detection for isolated documentation

**Hierarchy Levels**:
1. **Project Level**: Root directory containing ansible.cfg, playbooks/, or inventory/
2. **Collection Level**: Directory containing galaxy.yml with namespace.name format
3. **Role Level**: Directory containing tasks/main.yml or meta/main.yml

**Detection Strategy**:
- Search up to 3 directory levels above current component
- Cache detection results per generation session (session-scoped in-memory cache)
- Generate relative links assuming `docs/lang/{code}/` structure from Feature 005

**Symlink handling & security**:
- By default, the generator does not follow filesystem symlinks for parent detection to avoid traversal outside the repo or across mounted devices, improving security.
- A `--follow-symlinks` CLI flag is available for advanced users to follow symlinks. When enabled, symlink traversal is limited and validated to remain in the same device/volume.

**Relative Link Generation**:
- Relative links must be canonicalized using `pathlib.Path` utilities to ensure cross-platform compatibility. All generated links should be normalized (no trailing slashes unless it is a directory) and validated for existence.
- When a target doc doesn't exist for a language or path, the breadcrumb will render as plain text and the generator logs a warning with `context` where the doc was expected.

**Output Examples**:

*Role in Collection in Project*:
```
Breadcrumb: My Project > my_namespace.my_collection > webserver
Sibling Roles: database, cache, monitoring
Parent Collection: my_namespace.my_collection
```

*Standalone Role*:
```
No parent context detected (use --no-parent to suppress this search)
```

## User Scenarios

### US19 - Auto-Detect Parent Context (Priority: P1) 🎯 MVP

As a role developer working within a collection or project, I want ansible-doctor to automatically detect the parent context so that generated documentation reflects the role's position in the larger structure.

**Independent Test**: Document role in collection → Breadcrumb shows "Collection > Role"

**Acceptance Scenarios**:
1. **Given** role in directory `collections/my_namespace/my_collection/roles/webserver/`, **When** documenting role, **Then** detect parent collection from `../../galaxy.yml`
2. **Given** role in project with `ansible.cfg` two levels up, **When** documenting role, **Then** detect project parent and extract project name from config or directory name
3. **Given** collection in project with `ansible.cfg` in parent directory, **When** documenting collection, **Then** detect project parent
4. **Given** standalone role with no parent markers in 3 directory levels, **When** documenting, **Then** mark as standalone component
5. **Given** role 4+ directory levels deep with parent markers only at level 4+, **When** searching, **Then** stop at 3 levels and treat as standalone

## Slug & Link Integration

The generated breadcrumbs and relative links MUST use the output slug naming defined by the collection/project specs (e.g., `collection_{namespace}.{collection}`, `role_{namespace}.{rolename}`, `ansibleproject_{projectname}`). When generating breadcrumbs and links, the generator MUST ensure links are language-specific and point to `docs/lang/{code}/...` locations. If the target translation file does not exist for a given language, the link MUST render as plain text and a warning log entry must be emitted. 

Example:
```
Breadcrumb: My Project > my_namespace.my_collection > webserver
Links:  /docs/lang/en/ansibleproject_myproject/collections/collection_my_namespace.my_collection/role_my_namespace.webserver/README.md
```

---

### US20 - Generate Breadcrumb Navigation (Priority: P1) 🎯 MVP

As a documentation reader, I want to see breadcrumb navigation at the top of component documentation so that I understand the hierarchy and can navigate to parent documentation.

**Independent Test**: Open role documentation → See "Project > Collection > Role" breadcrumb with links

**Acceptance Scenarios**:
1. **Given** role with detected collection parent, **When** rendering documentation, **Then** show breadcrumb "Collection Name > Role Name" in header
2. **Given** role with detected project + collection parents, **When** rendering, **Then** show breadcrumb "Project Name > Collection Name > Role Name"
3. **Given** collection with detected project parent, **When** rendering, **Then** show breadcrumb "Project Name > Collection Name"
4. **Given** parent documentation exists at expected path, **When** rendering breadcrumb, **Then** make parent names clickable links to `../../project/README.md` or `../collection/README.md`
5. **Given** parent documentation doesn't exist, **When** rendering breadcrumb, **Then** show parent names as plain text (no broken links)
6. **Given** `--no-parent` flag, **When** generating docs, **Then** omit breadcrumb navigation entirely

---

### US21 - Add Contextual Overview Section (Priority: P2)

As a documentation reader exploring a collection or project, I want to see a list of sibling components (other roles, other collections) so that I can discover related documentation easily.

**Independent Test**: Open collection docs → See "Roles in this Collection: webserver, database, cache"

**Acceptance Scenarios**:
1. **Given** role in collection with 5 other roles, **When** rendering role docs, **Then** show "Sibling Roles in {collection_name}" section with links to other role documentation
2. **Given** collection in project with 3 other collections, **When** rendering collection docs, **Then** show "Collections in {project_name}" section with links
3. **Given** sibling component documentation exists, **When** generating overview, **Then** create relative links (e.g., `../other_role/README.md`)
4. **Given** sibling component has no documentation yet, **When** generating overview, **Then** list component name without link
5. **Given** `--no-parent` flag, **When** generating docs, **Then** omit sibling overview section

---

### US22 - Support Standalone Mode (Priority: P2)

As a developer documenting a single role for distribution, I want to use `--no-parent` flag so that documentation doesn't attempt context detection or show breadcrumbs for components intended as standalone.

**Independent Test**: Run `ansible-doctor --no-parent` → No breadcrumbs, no parent detection warnings

**Acceptance Scenarios**:
1. **Given** `--no-parent` CLI flag, **When** generating documentation, **Then** skip all parent context detection logic
2. **Given** `--no-parent` flag, **When** rendering documentation, **Then** omit breadcrumb navigation section
3. **Given** `--no-parent` flag, **When** rendering documentation, **Then** omit sibling overview section
4. **Given** `.ansibledoctor.yml` with `context.detect_parent: false`, **When** generating, **Then** behave as if `--no-parent` flag was passed
5. **Given** no `--no-parent` flag on standalone role, **When** generating, **Then** show informational message "No parent context detected" but don't treat as error

---

## Success Criteria

**SC-001**: Detect collection parent by finding `galaxy.yml` in parent directory (up to 3 levels)  
**SC-002**: Detect project parent by finding `ansible.cfg` or `playbooks/` directory (up to 3 levels)  
**SC-003**: Generate breadcrumbs with clickable links to parent documentation when files exist  
**SC-004**: List sibling roles/collections in contextual overview section with working relative links  
**SC-005**: `--no-parent` flag completely disables parent detection, breadcrumbs, and sibling overviews  
**SC-006**: Parent detection adds <500ms to generation time for typical projects  
**SC-007**: Cache parent detection results for reuse when generating multiple components in same session  
**SC-008**: Multi-language support: Breadcrumbs and sibling sections use i18n keys (e.g., `{{ t('context.breadcrumb') }}`)  
**SC-009**: Handle missing parent documentation gracefully (breadcrumb text without links, no broken links)  
**SC-010**: Configuration option `context.detect_parent: false` in `.ansibledoctor.yml` disables detection by default

---

## Technical Constraints

**TC-001**: Search maximum 3 directory levels up for parent context markers (`galaxy.yml`, `ansible.cfg`, `playbooks/`)  
**TC-002**: Cache parent detection results in-memory per generation session (avoid re-scanning filesystem)  
**TC-003**: Generate relative links between components assuming `docs/lang/{code}/` structure from Feature 005  
**TC-004**: Gracefully handle missing parent documentation by omitting links (show breadcrumb text only)  
**TC-005**: Use `pathlib.Path` for cross-platform directory traversal (Windows/Linux compatible)  
**TC-006**: Breadcrumb and sibling sections must use i18n translation keys from Feature 005  
**TC-007**: Parent detection must work independently for each language output directory  
**TC-008**: Limit sibling listing to 50 components maximum (prevent overwhelming documentation with large collections/projects)

---

## Key Entities

### ContextDetector
**Purpose**: Detect parent collection or project by scanning parent directories  
**Attributes**:
- `component_path: Path` - Current component directory
- `max_levels: int = 3` - Maximum directory levels to search upward
- `cache: Dict[Path, Optional[ParentContext]]` - Cached detection results

**Operations**:
- `detect_parent() -> Optional[ParentContext]` - Search for parent markers up directory tree
- `find_collection_parent() -> Optional[Path]` - Look for galaxy.yml in parent directories
- `find_project_parent() -> Optional[Path]` - Look for ansible.cfg or playbooks/ directory
- `_search_upward(markers: List[str], levels: int) -> Optional[Path]` - Generic upward search

### ParentContext
**Purpose**: Store detected parent information  
**Attributes**:
- `type: Literal['project', 'collection']` - Type of parent
- `path: Path` - Absolute path to parent directory
- `name: str` - Display name (from galaxy.yml namespace.name or directory name)
- `doc_path: Optional[Path]` - Expected path to parent documentation

**Operations**:
- `has_documentation() -> bool` - Check if parent documentation exists at expected path
- `relative_link_from(child_path: Path) -> str` - Calculate relative link from child to parent docs

### BreadcrumbGenerator
**Purpose**: Generate breadcrumb navigation HTML/Markdown  
**Attributes**:
- `context_chain: List[ParentContext]` - Ordered list from root to current component
- `current_name: str` - Name of current component being documented
- `i18n_provider: TranslationProvider` - For translating breadcrumb labels

**Operations**:
- `generate_breadcrumb() -> str` - Create breadcrumb navigation markup
- `_create_link(context: ParentContext) -> str` - Generate link if documentation exists, else plain text
- `_format_separator() -> str` - Return translated separator (e.g., " > ")

### SiblingDiscovery
**Purpose**: Find and list sibling components at same hierarchy level  
**Attributes**:
- `parent_context: ParentContext` - Detected parent (collection or project)
- `current_component: str` - Current component name (to exclude from sibling list)
- `component_type: Literal['role', 'collection']` - Type of components to find

**Operations**:
- `discover_siblings() -> List[SiblingComponent]` - Find all sibling roles or collections
- `_scan_roles_directory() -> List[Path]` - Scan collection roles/ directory
- `_scan_collections_directory() -> List[Path]` - Scan project collections/ directory
- `_check_documentation_exists(sibling: Path) -> bool` - Verify if sibling has generated docs

### SiblingComponent
**Purpose**: Represent a discovered sibling component  
**Attributes**:
- `name: str` - Component name
- `path: Path` - Absolute path to component directory
- `has_docs: bool` - Whether documentation exists
- `relative_link: Optional[str]` - Relative link to documentation (if exists)

---

## Architecture

### Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                     Documentation Generator                      │
│                     (from Feature 002/006)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  ContextDetector   │
                    │  - detect_parent() │
                    └─────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌────────────────┐        ┌────────────────┐
        │ find_collection│        │ find_project   │
        │    _parent()   │        │   _parent()    │
        └────────┬───────┘        └────────┬───────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                     ┌─────────────────┐
                     │ ParentContext   │
                     │ (cached result) │
                     └────────┬────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌────────────────┐        ┌────────────────┐
        │ Breadcrumb     │        │ Sibling        │
        │   Generator    │        │  Discovery     │
        └────────┬───────┘        └────────┬───────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │  Template Renderer   │
                    │  (Feature 002)       │
                    │  + i18n (Feature 005)│
                    └──────────────────────┘
```

### Data Flow

1. **Generator Initialization**: DocumentGenerator creates ContextDetector with component path
2. **Parent Detection**: ContextDetector searches up directory tree (max 3 levels) for markers
3. **Cache Check**: If parent already detected in session, return cached ParentContext
4. **Context Creation**: Create ParentContext with type, path, name, and expected doc path
5. **Breadcrumb Generation**: BreadcrumbGenerator builds navigation from context chain
6. **Sibling Discovery**: SiblingDiscovery scans parent directory for related components
7. **Template Rendering**: Pass breadcrumb and sibling data to Jinja2 templates with i18n
8. **Multi-Language**: Repeat breadcrumb/sibling generation for each enabled language

---

## Configuration Schema

```yaml
# .ansibledoctor.yml
context:
  detect_parent: true              # Enable/disable parent detection
  max_search_levels: 3             # Maximum directory levels to search upward
  show_breadcrumbs: true           # Include breadcrumb navigation in docs
  show_siblings: true              # Include sibling component listings
  sibling_limit: 50                # Maximum siblings to list
  
output:
  structure: hierarchical          # From Feature 005, required for relative links
  per_language: true               # Generate per-language output directories
```

### CLI Flags

```bash
# Disable parent detection completely
ansible-doctor generate --no-parent ./roles/webserver

# Disable only breadcrumbs (still detect for sibling discovery)
ansible-doctor generate --no-breadcrumbs ./roles/webserver

# Disable only sibling listings
ansible-doctor generate --no-siblings ./roles/webserver
```

---

## Template Integration

### Breadcrumb Template Section

```jinja2
{# templates/role.md.j2 #}
{% if context.parent %}
<nav class="breadcrumb">
  <ol>
    {% if context.project %}
    <li>
      {% if context.project.has_docs %}
      <a href="{{ context.project.relative_link }}">{{ context.project.name }}</a>
      {% else %}
      {{ context.project.name }}
      {% endif %}
    </li>
    <li class="separator">{{ t('context.separator') }}</li>
    {% endif %}
    
    {% if context.collection %}
    <li>
      {% if context.collection.has_docs %}
      <a href="{{ context.collection.relative_link }}">{{ context.collection.name }}</a>
      {% else %}
      {{ context.collection.name }}
      {% endif %}
    </li>
    <li class="separator">{{ t('context.separator') }}</li>
    {% endif %}
    
    <li class="current">{{ role.name }}</li>
  </ol>
</nav>
{% endif %}

# {{ t('role.title', name=role.name) }}

{{ t('role.description') }}
```

### Sibling Overview Template Section

```jinja2
{# Sibling roles in same collection #}
{% if context.siblings %}
## {{ t('context.sibling_roles', collection=context.collection.name) }}

{% for sibling in context.siblings %}
- {% if sibling.has_docs %}[{{ sibling.name }}]({{ sibling.relative_link }}){% else %}{{ sibling.name }}{% endif %}
{% endfor %}
{% endif %}
```

---

## Translation Keys

```yaml
# translations/en.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Other Roles in {collection}"
  sibling_collections: "Collections in {project}"
  no_parent: "Standalone Component"
  parent_project: "Project"
  parent_collection: "Collection"

# translations/fr.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Autres Rôles dans {collection}"
  sibling_collections: "Collections dans {project}"
  no_parent: "Composant Autonome"
  parent_project: "Projet"
  parent_collection: "Collection"

# translations/de.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Andere Rollen in {collection}"
  sibling_collections: "Sammlungen in {project}"
  no_parent: "Eigenständige Komponente"
  parent_project: "Projekt"
  parent_collection: "Sammlung"
```

---

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.5.0 (Collection Documentation) is COMPLETE and stable
2. ✅ v0.6.0 (i18n Support) is COMPLETE and stable
3. ✅ v0.7.0 (Project Documentation) is COMPLETE and stable
4. ✅ Collection parsing works and generates documentation
5. ✅ Project parsing works and generates documentation
6. ✅ i18n system generates multi-language output in `docs/lang/{code}/` structure
7. ✅ Template system can accept context variables for breadcrumbs and siblings
8. ✅ No critical bugs in collection, project, or i18n features

**Gate**: This feature CANNOT start until v0.7.0 (Project Documentation) is tagged and stable.

---

## Dependencies

### Upstream (Must Complete First)
- ✅ Feature 002 (Template System) - For rendering breadcrumbs and sibling sections
- ✅ Feature 004 (Collection Support) - For collection parent detection
- ✅ Feature 005 (i18n Support) - For multi-language breadcrumbs and labels
- ✅ Feature 006 (Project Documentation) - For project parent detection

### Downstream (Can Start After This)
- Feature 008 (Template Customization) - Can add custom breadcrumb styling
- Future features needing component relationships

---

## Out of Scope

**Explicitly NOT included in v0.8.0**:
- ❌ Dependency graph visualization (e.g., role dependencies between collections)
- ❌ Auto-linking to role dependencies defined in `meta/main.yml`
- ❌ Full-text search across hierarchical documentation
- ❌ Automatic table of contents generation for project-level docs
- ❌ Git-based breadcrumbs (using repository structure instead of filesystem)

These may be considered for future versions (v0.9.0+) based on user feedback.

---

## Testing Strategy

### Unit Tests
- `test_context_detector_finds_collection_parent()` - Verify galaxy.yml detection
- `test_context_detector_finds_project_parent()` - Verify ansible.cfg detection
- `test_context_detector_respects_max_levels()` - Stop at 3 levels
- `test_context_detector_caches_results()` - Verify caching works
- `test_breadcrumb_generator_creates_links()` - Test link generation
- `test_breadcrumb_generator_omits_links_when_no_docs()` - Graceful handling
- `test_sibling_discovery_lists_roles()` - Find sibling roles in collection
- `test_sibling_discovery_limits_results()` - Respect sibling_limit config

### Integration Tests
- `test_role_in_collection_shows_breadcrumb()` - End-to-end breadcrumb in docs
- `test_collection_in_project_shows_breadcrumb()` - Multi-level hierarchy
- `test_no_parent_flag_disables_detection()` - CLI flag works
- `test_multi_language_breadcrumbs()` - i18n integration
- `test_sibling_links_work_across_languages()` - Relative links correct for each language

### Performance Tests
- `test_parent_detection_under_500ms()` - Meets SC-006 performance requirement
- `test_large_collection_sibling_discovery()` - 100+ roles doesn't timeout

---

## v1.0.0 Readiness

Completing this feature (v0.8.0) provides advanced UX for navigating complex Ansible project structures. After this:

- **v0.9.0**: Stabilization, polish, performance tuning, bug fixes, documentation improvements
- **v1.0.0**: Production release with stable API, comprehensive documentation, migration guides

Features 005-007 complete the core capability set (Multi-language, Project docs, Context detection). Feature 008 (Template Customization) can be developed in parallel with v0.8.0 as it has minimal dependencies. v0.9.0 focuses exclusively on quality, not new features.

---

## Notes

- **Feature 005 Integration**: Breadcrumbs and sibling sections MUST use i18n translation keys
- **Feature 006 Integration**: Project detection relies on parsing logic from Project Documentation feature
- **Relative Links**: Assume `docs/lang/{code}/roles/`, `docs/lang/{code}/collections/`, `docs/lang/{code}/project/` structure
- **Performance**: Parent detection is one-time cost per component; caching is critical for multi-language generation
- **Graceful Degradation**: Missing parent docs should not break generation; show text instead of links
# Feature Specification: Hierarchical Context Detection

**Feature Branch**: `007-hierarchical-context`  
**Created**: 2025-11-26  
**Milestone**: v0.8.0  
**Prerequisites**: v0.7.0 (Project Documentation) COMPLETE ✅  
**Status**: Planned (Blocked until v0.7.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Automatically detect parent context when documenting Ansible components (roles, collections, projects). Generate breadcrumb navigation and contextual overviews showing component relationships and hierarchy. Enable users to understand component placement within larger project structures without manual configuration.

## What is Hierarchical Context Detection?

Hierarchical Context Detection analyzes directory structure to determine relationships between Ansible components:

- **Parent Detection**: Automatically find parent collection or project for a role
- **Breadcrumb Navigation**: Generate clickable breadcrumbs showing hierarchy (Project > Collection > Role)
- **Sibling Discovery**: List related components at the same level (other roles in collection, other collections in project)
- **Relative Linking**: Generate documentation cross-references with relative paths
- **Standalone Mode**: Optional flag to disable context detection for isolated documentation

**Hierarchy Levels**:
1. **Project Level**: Root directory containing ansible.cfg, playbooks/, or inventory/
2. **Collection Level**: Directory containing galaxy.yml with namespace.name format
3. **Role Level**: Directory containing tasks/main.yml or meta/main.yml

**Detection Strategy**:
- Search up to 3 directory levels above current component
- Cache detection results per generation session
- Generate relative links assuming `docs/lang/{code}/` structure from Feature 005

**Output Examples**:

*Role in Collection in Project*:
```
Breadcrumb: My Project > my_namespace.my_collection > webserver
Sibling Roles: database, cache, monitoring
Parent Collection: my_namespace.my_collection
```

*Standalone Role*:
```
No parent context detected (use --no-parent to suppress this search)
```

## User Scenarios

### US19 - Auto-Detect Parent Context (Priority: P1) 🎯 MVP

As a role developer working within a collection or project, I want ansible-doctor to automatically detect the parent context so that generated documentation reflects the role's position in the larger structure.

**Independent Test**: Document role in collection → Breadcrumb shows "Collection > Role"

**Acceptance Scenarios**:
1. **Given** role in directory `collections/my_namespace/my_collection/roles/webserver/`, **When** documenting role, **Then** detect parent collection from `../../galaxy.yml`
2. **Given** role in project with `ansible.cfg` two levels up, **When** documenting role, **Then** detect project parent and extract project name from config or directory name
3. **Given** collection in project with `ansible.cfg` in parent directory, **When** documenting collection, **Then** detect project parent
4. **Given** standalone role with no parent markers in 3 directory levels, **When** documenting, **Then** mark as standalone component
5. **Given** role 4+ directory levels deep with parent markers only at level 4+, **When** searching, **Then** stop at 3 levels and treat as standalone

---

### US20 - Generate Breadcrumb Navigation (Priority: P1) 🎯 MVP

As a documentation reader, I want to see breadcrumb navigation at the top of component documentation so that I understand the hierarchy and can navigate to parent documentation.

**Independent Test**: Open role documentation → See "Project > Collection > Role" breadcrumb with links

**Acceptance Scenarios**:
1. **Given** role with detected collection parent, **When** rendering documentation, **Then** show breadcrumb "Collection Name > Role Name" in header
2. **Given** role with detected project + collection parents, **When** rendering, **Then** show breadcrumb "Project Name > Collection Name > Role Name"
3. **Given** collection with detected project parent, **When** rendering, **Then** show breadcrumb "Project Name > Collection Name"
4. **Given** parent documentation exists at expected path, **When** rendering breadcrumb, **Then** make parent names clickable links to `../../project/README.md` or `../collection/README.md`
5. **Given** parent documentation doesn't exist, **When** rendering breadcrumb, **Then** show parent names as plain text (no broken links)
6. **Given** `--no-parent` flag, **When** generating docs, **Then** omit breadcrumb navigation entirely

---

### US21 - Add Contextual Overview Section (Priority: P2)

As a documentation reader exploring a collection or project, I want to see a list of sibling components (other roles, other collections) so that I can discover related documentation easily.

**Independent Test**: Open collection docs → See "Roles in this Collection: webserver, database, cache"

**Acceptance Scenarios**:
1. **Given** role in collection with 5 other roles, **When** rendering role docs, **Then** show "Sibling Roles in {collection_name}" section with links to other role documentation
2. **Given** collection in project with 3 other collections, **When** rendering collection docs, **Then** show "Collections in {project_name}" section with links
3. **Given** sibling component documentation exists, **When** generating overview, **Then** create relative links (e.g., `../other_role/README.md`)
4. **Given** sibling component has no documentation yet, **When** generating overview, **Then** list component name without link
5. **Given** `--no-parent` flag, **When** generating docs, **Then** omit sibling overview section

---

### US22 - Support Standalone Mode (Priority: P2)

As a developer documenting a single role for distribution, I want to use `--no-parent` flag so that documentation doesn't attempt context detection or show breadcrumbs for components intended as standalone.

**Independent Test**: Run `ansible-doctor --no-parent` → No breadcrumbs, no parent detection warnings

**Acceptance Scenarios**:
1. **Given** `--no-parent` CLI flag, **When** generating documentation, **Then** skip all parent context detection logic
2. **Given** `--no-parent` flag, **When** rendering documentation, **Then** omit breadcrumb navigation section
3. **Given** `--no-parent` flag, **When** rendering documentation, **Then** omit sibling overview section
4. **Given** `.ansibledoctor.yml` with `context.detect_parent: false`, **When** generating, **Then** behave as if `--no-parent` flag was passed
5. **Given** no `--no-parent` flag on standalone role, **When** generating, **Then** show informational message "No parent context detected" but don't treat as error

---

## Success Criteria

**SC-001**: Detect collection parent by finding `galaxy.yml` in parent directory (up to 3 levels)  
**SC-002**: Detect project parent by finding `ansible.cfg` or `playbooks/` directory (up to 3 levels)  
**SC-003**: Generate breadcrumbs with clickable links to parent documentation when files exist  
**SC-004**: List sibling roles/collections in contextual overview section with working relative links  
**SC-005**: `--no-parent` flag completely disables parent detection, breadcrumbs, and sibling overviews  
**SC-006**: Parent detection adds <500ms to generation time for typical projects  
**SC-007**: Cache parent detection results for reuse when generating multiple components in same session  
**SC-008**: Multi-language support: Breadcrumbs and sibling sections use i18n keys (e.g., `{{ t('context.breadcrumb') }}`)  
**SC-009**: Handle missing parent documentation gracefully (breadcrumb text without links, no broken links)  
**SC-010**: Configuration option `context.detect_parent: false` in `.ansibledoctor.yml` disables detection by default

---

## Technical Constraints

**TC-001**: Search maximum 3 directory levels up for parent context markers (`galaxy.yml`, `ansible.cfg`, `playbooks/`)  
**TC-002**: Cache parent detection results in-memory per generation session (avoid re-scanning filesystem)  
**TC-003**: Generate relative links between components assuming `docs/lang/{code}/` structure from Feature 005  
**TC-004**: Gracefully handle missing parent documentation by omitting links (show breadcrumb text only)  
**TC-005**: Use `pathlib.Path` for cross-platform directory traversal (Windows/Linux compatible)  
**TC-006**: Breadcrumb and sibling sections must use i18n translation keys from Feature 005  
**TC-007**: Parent detection must work independently for each language output directory  
**TC-008**: Limit sibling listing to 50 components maximum (prevent overwhelming documentation with large collections/projects)

---

## Key Entities

### ContextDetector
**Purpose**: Detect parent collection or project by scanning parent directories  
**Attributes**:
- `component_path: Path` - Current component directory
- `max_levels: int = 3` - Maximum directory levels to search upward
- `cache: Dict[Path, Optional[ParentContext]]` - Cached detection results

**Operations**:
- `detect_parent() -> Optional[ParentContext]` - Search for parent markers up directory tree
- `find_collection_parent() -> Optional[Path]` - Look for galaxy.yml in parent directories
- `find_project_parent() -> Optional[Path]` - Look for ansible.cfg or playbooks/ directory
- `_search_upward(markers: List[str], levels: int) -> Optional[Path]` - Generic upward search

### ParentContext
**Purpose**: Store detected parent information  
**Attributes**:
- `type: Literal['project', 'collection']` - Type of parent
- `path: Path` - Absolute path to parent directory
- `name: str` - Display name (from galaxy.yml namespace.name or directory name)
- `doc_path: Optional[Path]` - Expected path to parent documentation

**Operations**:
- `has_documentation() -> bool` - Check if parent documentation exists at expected path
- `relative_link_from(child_path: Path) -> str` - Calculate relative link from child to parent docs

### BreadcrumbGenerator
**Purpose**: Generate breadcrumb navigation HTML/Markdown  
**Attributes**:
- `context_chain: List[ParentContext]` - Ordered list from root to current component
- `current_name: str` - Name of current component being documented
- `i18n_provider: TranslationProvider` - For translating breadcrumb labels

**Operations**:
- `generate_breadcrumb() -> str` - Create breadcrumb navigation markup
- `_create_link(context: ParentContext) -> str` - Generate link if documentation exists, else plain text
- `_format_separator() -> str` - Return translated separator (e.g., " > ")

### SiblingDiscovery
**Purpose**: Find and list sibling components at same hierarchy level  
**Attributes**:
- `parent_context: ParentContext` - Detected parent (collection or project)
- `current_component: str` - Current component name (to exclude from sibling list)
- `component_type: Literal['role', 'collection']` - Type of components to find

**Operations**:
- `discover_siblings() -> List[SiblingComponent]` - Find all sibling roles or collections
- `_scan_roles_directory() -> List[Path]` - Scan collection roles/ directory
- `_scan_collections_directory() -> List[Path]` - Scan project collections/ directory
- `_check_documentation_exists(sibling: Path) -> bool` - Verify if sibling has generated docs

### SiblingComponent
**Purpose**: Represent a discovered sibling component  
**Attributes**:
- `name: str` - Component name
- `path: Path` - Absolute path to component directory
- `has_docs: bool` - Whether documentation exists
- `relative_link: Optional[str]` - Relative link to documentation (if exists)

---

## Architecture

### Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                     Documentation Generator                      │
│                     (from Feature 002/006)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  ContextDetector   │
                    │  - detect_parent() │
                    └─────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌────────────────┐        ┌────────────────┐
        │ find_collection│        │ find_project   │
        │    _parent()   │        │   _parent()    │
        └────────┬───────┘        └────────┬───────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                     ┌─────────────────┐
                     │ ParentContext   │
                     │ (cached result) │
                     └────────┬────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌────────────────┐        ┌────────────────┐
        │ Breadcrumb     │        │ Sibling        │
        │   Generator    │        │  Discovery     │
        └────────┬───────┘        └────────┬───────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌──────────────────────┐
                    │  Template Renderer   │
                    │  (Feature 002)       │
                    │  + i18n (Feature 005)│
                    └──────────────────────┘
```

### Data Flow

1. **Generator Initialization**: DocumentGenerator creates ContextDetector with component path
2. **Parent Detection**: ContextDetector searches up directory tree (max 3 levels) for markers
3. **Cache Check**: If parent already detected in session, return cached ParentContext
4. **Context Creation**: Create ParentContext with type, path, name, and expected doc path
5. **Breadcrumb Generation**: BreadcrumbGenerator builds navigation from context chain
6. **Sibling Discovery**: SiblingDiscovery scans parent directory for related components
7. **Template Rendering**: Pass breadcrumb and sibling data to Jinja2 templates with i18n
8. **Multi-Language**: Repeat breadcrumb/sibling generation for each enabled language

---

## Configuration Schema

```yaml
# .ansibledoctor.yml
context:
  detect_parent: true              # Enable/disable parent detection
  max_search_levels: 3             # Maximum directory levels to search upward
  show_breadcrumbs: true           # Include breadcrumb navigation in docs
  show_siblings: true              # Include sibling component listings
  sibling_limit: 50                # Maximum siblings to list
  
output:
  structure: hierarchical          # From Feature 005, required for relative links
  per_language: true               # Generate per-language output directories
```

### CLI Flags

```bash
# Disable parent detection completely
ansible-doctor generate --no-parent ./roles/webserver

# Disable only breadcrumbs (still detect for sibling discovery)
ansible-doctor generate --no-breadcrumbs ./roles/webserver

# Disable only sibling listings
ansible-doctor generate --no-siblings ./roles/webserver
```

---

## Template Integration

### Breadcrumb Template Section

```jinja2
{# templates/role.md.j2 #}
{% if context.parent %}
<nav class="breadcrumb">
  <ol>
    {% if context.project %}
    <li>
      {% if context.project.has_docs %}
      <a href="{{ context.project.relative_link }}">{{ context.project.name }}</a>
      {% else %}
      {{ context.project.name }}
      {% endif %}
    </li>
    <li class="separator">{{ t('context.separator') }}</li>
    {% endif %}
    
    {% if context.collection %}
    <li>
      {% if context.collection.has_docs %}
      <a href="{{ context.collection.relative_link }}">{{ context.collection.name }}</a>
      {% else %}
      {{ context.collection.name }}
      {% endif %}
    </li>
    <li class="separator">{{ t('context.separator') }}</li>
    {% endif %}
    
    <li class="current">{{ role.name }}</li>
  </ol>
</nav>
{% endif %}

# {{ t('role.title', name=role.name) }}

{{ t('role.description') }}
```

### Sibling Overview Template Section

```jinja2
{# Sibling roles in same collection #}
{% if context.siblings %}
## {{ t('context.sibling_roles', collection=context.collection.name) }}

{% for sibling in context.siblings %}
- {% if sibling.has_docs %}[{{ sibling.name }}]({{ sibling.relative_link }}){% else %}{{ sibling.name }}{% endif %}
{% endfor %}
{% endif %}
```

---

## Translation Keys

```yaml
# translations/en.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Other Roles in {collection}"
  sibling_collections: "Collections in {project}"
  no_parent: "Standalone Component"
  parent_project: "Project"
  parent_collection: "Collection"

# translations/fr.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Autres Rôles dans {collection}"
  sibling_collections: "Collections dans {project}"
  no_parent: "Composant Autonome"
  parent_project: "Projet"
  parent_collection: "Collection"

# translations/de.yml
context:
  separator: " > "
  breadcrumb: "Navigation"
  sibling_roles: "Andere Rollen in {collection}"
  sibling_collections: "Sammlungen in {project}"
  no_parent: "Eigenständige Komponente"
  parent_project: "Projekt"
  parent_collection: "Sammlung"
```

---

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.5.0 (Collection Documentation) is COMPLETE and stable
2. ✅ v0.6.0 (i18n Support) is COMPLETE and stable
3. ✅ v0.7.0 (Project Documentation) is COMPLETE and stable
4. ✅ Collection parsing works and generates documentation
5. ✅ Project parsing works and generates documentation
6. ✅ i18n system generates multi-language output in `docs/lang/{code}/` structure
7. ✅ Template system can accept context variables for breadcrumbs and siblings
8. ✅ No critical bugs in collection, project, or i18n features

**Gate**: This feature CANNOT start until v0.7.0 (Project Documentation) is tagged and stable.

---

## Dependencies

### Upstream (Must Complete First)
- ✅ Feature 002 (Template System) - For rendering breadcrumbs and sibling sections
- ✅ Feature 004 (Collection Support) - For collection parent detection
- ✅ Feature 005 (i18n Support) - For multi-language breadcrumbs and labels
- ✅ Feature 006 (Project Documentation) - For project parent detection

### Downstream (Can Start After This)
- Feature 008 (Template Customization) - Can add custom breadcrumb styling
- Future features needing component relationships

---

## Out of Scope

**Explicitly NOT included in v0.8.0**:
- ❌ Dependency graph visualization (e.g., role dependencies between collections)
- ❌ Auto-linking to role dependencies defined in `meta/main.yml`
- ❌ Full-text search across hierarchical documentation
- ❌ Automatic table of contents generation for project-level docs
- ❌ Git-based breadcrumbs (using repository structure instead of filesystem)

These may be considered for future versions (v0.9.0+) based on user feedback.

---

## Testing Strategy

### Unit Tests
- `test_context_detector_finds_collection_parent()` - Verify galaxy.yml detection
- `test_context_detector_finds_project_parent()` - Verify ansible.cfg detection
- `test_context_detector_respects_max_levels()` - Stop at 3 levels
- `test_context_detector_caches_results()` - Verify caching works
- `test_breadcrumb_generator_creates_links()` - Test link generation
- `test_breadcrumb_generator_omits_links_when_no_docs()` - Graceful handling
- `test_sibling_discovery_lists_roles()` - Find sibling roles in collection
- `test_sibling_discovery_limits_results()` - Respect sibling_limit config

### Integration Tests
- `test_role_in_collection_shows_breadcrumb()` - End-to-end breadcrumb in docs
- `test_collection_in_project_shows_breadcrumb()` - Multi-level hierarchy
- `test_no_parent_flag_disables_detection()` - CLI flag works
- `test_multi_language_breadcrumbs()` - i18n integration
- `test_sibling_links_work_across_languages()` - Relative links correct for each language

### Performance Tests
- `test_parent_detection_under_500ms()` - Meets SC-006 performance requirement
- `test_large_collection_sibling_discovery()` - 100+ roles doesn't timeout

---

## v1.0.0 Readiness

Completing this feature (v0.8.0) provides advanced UX for navigating complex Ansible project structures. After this:

- **v0.9.0**: Stabilization, polish, performance tuning, bug fixes, documentation improvements
- **v1.0.0**: Production release with stable API, comprehensive documentation, migration guides

Features 005-007 complete the core capability set (Multi-language, Project docs, Context detection). Feature 008 (Template Customization) can be developed in parallel with v0.8.0 as it has minimal dependencies. v0.9.0 focuses exclusively on quality, not new features.

---

## Notes

- **Feature 005 Integration**: Breadcrumbs and sibling sections MUST use i18n translation keys
- **Feature 006 Integration**: Project detection relies on parsing logic from Project Documentation feature
- **Relative Links**: Assume `docs/lang/{code}/roles/`, `docs/lang/{code}/collections/`, `docs/lang/{code}/project/` structure
- **Performance**: Parent detection is one-time cost per component; caching is critical for multi-language generation
- **Graceful Degradation**: Missing parent docs should not break generation; show text instead of links
