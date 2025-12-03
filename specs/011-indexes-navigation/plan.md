# Implementation Plan: Indexes & Navigation

**Branch**: `011-indexes-navigation` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-indexes-navigation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Generate comprehensive index pages and navigation structures for ansible-doctor documentation. Support standalone index pages (e.g., `roles/index.md`), embedded section indexes via template markers (`{{ index('roles') }}`), and multiple visualization styles (list, table, tree, nested-table, Mermaid diagrams). Enable hierarchical views showing project → collections → roles relationships, filtering by tag/namespace/type, cross-reference links, and pagination for large projects. Reuse existing TemplateEngine infrastructure with new IndexGenerator component and IndexItem models.

## Technical Context

**Language/Version**: Python 3.11+ (existing project baseline)  
**Primary Dependencies**: Jinja2 (existing, template engine), pydantic (existing, models), anytree (NEW, tree visualization)  
**Storage**: Generated index files (Markdown/HTML/RST), in-memory index structures during generation  
**Testing**: pytest with index generation fixtures, tree structure validation, link validation  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) with Markdown/HTML/RST output  
**Project Type**: Single project - CLI application extending existing template system  
**Performance Goals**: <200ms per 100 components for index generation, <500ms for large projects (500+ components)  
**Constraints**: ASCII-only tree output by default (no Unicode unless explicit), Mermaid diagrams compatible with GitHub/GitLab, pagination for 50+ items  
**Scale/Scope**: Support projects with 500+ roles, 5+ nesting levels, detect circular dependencies, handle missing descriptions gracefully

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Test-First Development**: PASS  
  - Rationale: Index generation is highly testable. Write tests for tree structures, link validation, filtering logic, then implement IndexGenerator and IndexItem models. Fixture-based testing with sample project structures enables TDD workflow.

- **Library-First Architecture**: PASS  
  - Rationale: New `generator/indexes.py` module with IndexGenerator protocol is pure Python. IndexItem models in `models/index.py` are independent. CLI integration only wraps library calls (`--include-index`, `--index-style`, `--filter`).

- **CLI Mandate**: PASS  
  - Rationale: New CLI flags `--include-index`, `--index-style {list,table,tree,nested-table,diagram}`, `--index-format {full,section}`, `--filter <criteria>`, `--index-depth N`. Extends existing CLI in `ansibledoctor/cli/__init__.py`.

- **Observability**: PASS  
  - Rationale: Index generation emits structured logs with timing metrics (index generation duration, component counts). Links validation warnings logged. Execution reports (Spec 009) include index generation metrics.

- **Backward Compatibility**: PASS  
  - Rationale: No breaking changes. Index generation is opt-in via `--include-index` flag. Existing documentation generation unchanged. Template markers (`{{ index() }}`) are additive and ignored if index module not loaded.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
ansibledoctor/
├── models/
│   ├── index.py              # NEW: IndexItem, IndexPage, SectionIndex models
│   └── cross_reference.py    # NEW: CrossReference model for links
├── generator/
│   ├── indexes.py            # NEW: IndexGenerator implementation
│   ├── index_filters.py      # NEW: IndexFilter for filtering logic
│   └── tree_visualizer.py    # NEW: ASCII tree rendering
├── utils/
│   ├── mermaid_builder.py    # NEW: Mermaid diagram generation
│   └── link_validator.py     # NEW: Cross-reference link validation
├── cli/
│   └── __init__.py           # EXTEND: Add index CLI flags
└── templates/
    └── index/                # NEW: Index templates directory
        ├── list.j2           # NEW: List style template
        ├── table.j2          # NEW: Table style template
        ├── tree.j2           # NEW: Tree style template
        ├── nested_table.j2   # NEW: Nested table template
        └── diagram.j2        # NEW: Mermaid diagram template

tests/
├── unit/
│   ├── test_index_models.py         # NEW: IndexItem, IndexPage tests
│   ├── test_index_generator.py      # NEW: IndexGenerator tests
│   ├── test_tree_visualizer.py      # NEW: ASCII tree tests
│   ├── test_index_filters.py        # NEW: Filtering logic tests
│   └── test_link_validator.py       # NEW: Link validation tests
├── integration/
│   ├── test_index_generation.py     # NEW: End-to-end index generation
│   └── test_embedded_indexes.py     # NEW: Template marker integration
└── fixtures/
    └── project_structures/          # NEW: Sample projects for testing
        ├── simple_project/          # 1 collection, 3 roles
        ├── hierarchical_project/    # 3 collections, 15 roles, plugins
        └── large_project/           # 500+ components for performance testing
```

**Structure Decision**: Single project structure extending existing `ansibledoctor/` package. New `models/index.py` for index-specific models colocated with existing models. `generator/indexes.py` follows pattern of existing generators. Templates in `templates/index/` subdirectory for organization. Tests mirror source structure with comprehensive fixture library for different project sizes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all gates pass. No additional complexity justification required.

---

## Phase 0: Research & Planning

### Research Tasks

1. **Tree Visualization Libraries**: Evaluate Python libraries for ASCII tree rendering
   - `anytree` (recommended): Rich tree data structures, ASCII rendering, traversal utilities
   - `treelib`: Simpler API but less flexible
   - Custom implementation: Full control but reinventing wheel
   - Decision criteria: ASCII rendering quality, Unicode support toggle, performance on deep trees

2. **Mermaid Diagram Patterns**: Study Mermaid syntax for component hierarchies
   - Flowchart vs mindmap vs graph for project structures
   - Node styling and clickable links syntax
   - Clustering/subgraphs for large diagrams (50+ nodes)
   - GitHub/GitLab Mermaid rendering compatibility

3. **Link Validation Strategies**: Research approaches for validating cross-references
   - File existence checks during generation
   - URL validation for external links
   - Circular dependency detection algorithms (cycle detection in graphs)
   - Broken link reporting formats (inline warnings, summary report, exit code)

4. **Pagination Patterns**: Investigate pagination approaches for large indexes
   - Static pagination (generate index-1.md, index-2.md)
   - Virtual scrolling for HTML output (load on demand)
   - Configurable items per page (default 50)
   - Navigation links (previous, next, jump to page)

5. **Filtering Performance**: Study efficient filtering for large datasets
   - In-memory filtering vs pre-filtered indexes
   - Tag index structures (inverted index for O(1) tag lookup)
   - Multi-criteria filtering (AND/OR logic)
   - Filter caching for repeated queries

**Output**: `research.md` with findings, decisions, and rationale for each topic

---

## Phase 1: Design & Contracts

### Data Model Design

**IndexItem** (Base Component):
```python
class IndexItem(BaseModel):
    \"\"\"Single entry in an index with metadata and navigation.\"\"\"
    name: str  # Component name (role name, collection name)
    type: Literal["collection", "role", "plugin", "module", "playbook"]
    description: str | None
    path: Path  # Relative path to component
    doc_link: str | None  # Link to generated documentation
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)  # Custom metadata
    children: list["IndexItem"] = Field(default_factory=list)  # For hierarchical items
    dependencies: list[str] = Field(default_factory=list)  # Dependency names
    
    @property
    def depth(self) -> int:
        \"\"\"Calculate depth in hierarchy (root=0).\"\"\"
        ...
```

**IndexPage**:
```python
class IndexPage(BaseModel):
    \"\"\"Standalone index page for a component type.\"\"\"
    title: str  # \"Role Index\", \"Collection Index\"
    component_type: str  # \"roles\", \"collections\"
    items: list[IndexItem]
    format: Literal["list", "table", "tree", "nested-table", "diagram"]
    total_count: int
    filtered_count: int | None  # If filter applied
    page_number: int = 1
    total_pages: int = 1
    filters_applied: list[str] = Field(default_factory=list)
    
    def render(self, template_engine: TemplateEngine) -> str:
        \"\"\"Render index page using appropriate template.\"\"\"
        ...
```

**SectionIndex**:
```python
class SectionIndex(BaseModel):
    \"\"\"Embedded index section within parent documentation.\"\"\"
    component_type: str
    items: list[IndexItem]
    format: str
    limit: int | None  # Max items to show
    show_more_link: bool = True  # Link to full index page
    group_by: str | None  # Group items by field (\"type\", \"tag\")
    
    def render_inline(self, template_engine: TemplateEngine) -> str:
        \"\"\"Render as inline section for embedding.\"\"\"
        ...
```

**IndexFilter**:
```python
class IndexFilter(BaseModel):
    \"\"\"Criteria for filtering index content.\"\"\"
    field: str  # \"tag\", \"namespace\", \"type\", \"status\"
    operator: Literal["equals", "contains", "startswith", "in"]
    value: str | list[str]
    
    def matches(self, item: IndexItem) -> bool:
        \"\"\"Check if item matches filter criteria.\"\"\"
        ...
```

**CrossReference**:
```python
class CrossReference(BaseModel):
    \"\"\"Link between components with validation.\"\"\"
    source: IndexItem
    target_name: str
    target_type: str
    link_type: Literal["dependency", "used_by", "related"]
    resolved_path: Path | None  # Resolved during generation
    is_valid: bool = False  # Set by link validator
    
    @property
    def link_text(self) -> str:
        \"\"\"Generate Markdown link text.\"\"\"
        ...
```

### API Contracts

**IndexGenerator Protocol**:
```python
class IndexGenerator(Protocol):
    \"\"\"Protocol for generating index pages and sections.\"\"\"
    
    def generate_index_page(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        filters: list[IndexFilter] | None = None,
        page_size: int = 50,
    ) -> IndexPage:
        \"\"\"
        Generate standalone index page.
        
        Args:
            component_type: Type of components (\"roles\", \"collections\")
            items: List of components to index
            format: Visualization style
            filters: Optional filtering criteria
            page_size: Items per page for pagination
        
        Returns:
            IndexPage with rendered content
        \"\"\"
        ...
    
    def generate_section_index(
        self,
        component_type: str,
        items: list[IndexItem],
        format: str = "list",
        limit: int | None = None,
        group_by: str | None = None,
    ) -> SectionIndex:
        \"\"\"Generate embedded index section for template marker.\"\"\"
        ...
    
    def build_hierarchy(
        self,
        items: list[IndexItem],
        max_depth: int = 5,
    ) -> list[IndexItem]:
        \"\"\"
        Build hierarchical tree structure from flat item list.
        
        Detects circular dependencies and limits depth.
        \"\"\"
        ...
```

**TreeVisualizer**:
```python
class TreeVisualizer:
    \"\"\"ASCII tree rendering with customizable characters.\"\"\"
    
    def __init__(self, use_unicode: bool = False):
        \"\"\"
        Args:
            use_unicode: Use Unicode box-drawing characters (│ ├ └)
        \"\"\"
        self.branch = \"├── \" if not use_unicode else \"├── \"
        self.last_branch = \"└── \" if not use_unicode else \"└── \"
        self.vertical = \"│   \" if not use_unicode else \"│   \"
        self.space = \"    \"
    
    def render_tree(
        self,
        root: IndexItem,
        max_depth: int = 5,
    ) -> str:
        \"\"\"Render item hierarchy as ASCII tree.\"\"\"
        ...
    
    def _render_node(
        self,
        item: IndexItem,
        prefix: str,
        is_last: bool,
        depth: int,
        max_depth: int,
    ) -> str:
        \"\"\"Recursively render tree node with prefix.\"\"\"
        ...
```

**MermaidBuilder**:
```python
class MermaidBuilder:
    \"\"\"Generate Mermaid diagrams for component hierarchies.\"\"\"
    
    def build_flowchart(
        self,
        items: list[IndexItem],
        diagram_type: Literal["TD", "LR"] = "TD",
    ) -> str:
        \"\"\"
        Generate Mermaid flowchart.
        
        Args:
            items: Components to include
            diagram_type: Top-down (TD) or left-right (LR)
        
        Returns:
            Mermaid diagram code
        \"\"\"
        ...
    
    def build_mindmap(self, root: IndexItem) -> str:
        \"\"\"Generate Mermaid mindmap diagram.\"\"\"
        ...
    
    def add_dependencies(
        self,
        diagram: str,
        items: list[IndexItem],
    ) -> str:
        \"\"\"Add dependency arrows to existing diagram.\"\"\"
        ...
```

**LinkValidator**:
```python
class LinkValidator:
    \"\"\"Validate cross-reference links between components.\"\"\"
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.validation_cache: dict[str, bool] = {}
    
    def validate_link(self, cross_ref: CrossReference) -> bool:
        \"\"\"
        Check if cross-reference target exists.
        
        Returns:
            True if target documentation exists
        \"\"\"
        ...
    
    def validate_all(
        self,
        items: list[IndexItem],
    ) -> tuple[list[CrossReference], list[CrossReference]]:
        \"\"\"
        Validate all cross-references in index.
        
        Returns:
            Tuple of (valid_links, broken_links)
        \"\"\"
        ...
```

### CLI Extensions

**New Flags in `ansibledoctor/cli/__init__.py`**:

```python
@click.option(
    \"--include-index\",
    is_flag=True,
    help=\"Generate index pages for components\",
)
@click.option(
    \"--index-style\",
    type=click.Choice([\"list\", \"table\", \"tree\", \"nested-table\", \"diagram\"]),
    default=\"list\",
    help=\"Index visualization style (default: list)\",
)
@click.option(
    \"--index-format\",
    type=click.Choice([\"full\", \"section\"]),
    default=\"full\",
    help=\"Generate full page or section index (default: full)\",
)
@click.option(
    \"--index-depth\",
    type=int,
    default=5,
    help=\"Maximum hierarchy depth for tree/nested views (default: 5)\",
)
@click.option(
    \"--filter\",
    multiple=True,
    help=\"Filter index by criteria (e.g., 'tag:database', 'namespace:my_namespace')\",
)
@click.option(
    \"--validate-links\",
    is_flag=True,
    help=\"Validate cross-reference links and report broken links\",
)
@click.option(
    \"--page-size\",
    type=int,
    default=50,
    help=\"Items per page for pagination (default: 50)\",
)
@click.option(
    \"--use-unicode\",
    is_flag=True,
    help=\"Use Unicode box-drawing characters in tree output\",
)
```

### Template Marker Syntax

**Jinja2 Template Extension**:
```jinja2
{# List all roles in collection #}
{{ index('roles') }}

{# Table format with tag filtering #}
{{ index('roles', format='table', filter='tag:database') }}

{# Tree view limited to 3 levels #}
{{ index('collections', format='tree', depth=3) }}

{# Limit items shown, link to full index #}
{{ index('plugins', format='list', limit=10) }}

{# Group plugins by type #}
{{ index('plugins', format='table', group_by='type') }}

{# Mermaid diagram of project structure #}
{{ index('collections', format='diagram', diagram_type='flowchart') }}
```

### Output Contracts

**List Format**:
```markdown
## Roles

- **webserver** - Configure web servers with nginx
  - Tags: web, nginx
  - Dependencies: common
  - [Documentation](./roles/webserver/README.md)

- **database** - Install and configure PostgreSQL
  - Tags: database, postgres
  - Dependencies: common
  - [Documentation](./roles/database/README.md)
```

**Table Format**:
```markdown
## Roles

| Name | Description | Tags | Dependencies |
|------|-------------|------|--------------|
| [webserver](./roles/webserver/README.md) | Configure web servers | web, nginx | [common](./roles/common/README.md) |
| [database](./roles/database/README.md) | Install PostgreSQL | database, postgres | [common](./roles/common/README.md) |
```

**Tree Format**:
```text
my_namespace.infrastructure/
├── roles/
│   ├── webserver/
│   │   └── Configure web servers with nginx
│   ├── database/
│   │   └── Install and configure PostgreSQL
│   └── monitoring/
│       └── Setup monitoring stack
└── plugins/
    ├── modules/
    │   └── my_module.py
    └── filters/
        └── my_filter.py
```

**Mermaid Diagram**:
```mermaid
graph TD
    Project[\"My Ansible Project\"]
    Collection1[\"my_namespace.infrastructure\"]
    Collection2[\"my_namespace.monitoring\"]
    Role1[\"webserver\"]
    Role2[\"database\"]
    Role3[\"prometheus\"]
    
    Project --> Collection1
    Project --> Collection2
    Collection1 --> Role1
    Collection1 --> Role2
    Collection2 --> Role3
    
    Role1 -.depends.-> Role2
    
    click Role1 \"./roles/webserver/README.md\"
    click Role2 \"./roles/database/README.md\"
    click Role3 \"./roles/prometheus/README.md\"
```

### Integration Points

1. **TemplateEngine Extension**:
   - Register `index()` function as Jinja2 global
   - Parse template marker arguments
   - Call IndexGenerator during rendering

2. **Parser Integration**:
   - Extract component metadata (name, description, tags)
   - Build IndexItem list from parsed components
   - Detect dependencies during role parsing

3. **Generator Integration**:
   - Generate index files after main documentation
   - Write to appropriate output directories (`docs/lang/{code}/index/`)
   - Update navigation links in parent documents

4. **Execution Report Integration** (Spec 009):
   - Include index generation metrics (components indexed, links validated)
   - Log index generation duration
   - Report broken links in execution warnings

### Quickstart Example

**Generate Role Index**:
```bash
# Simple role index (list format)
ansible-doctor generate collection/ --include-index

# Tree visualization
ansible-doctor generate collection/ --include-index --index-style tree

# Filter by tag
ansible-doctor generate collection/ --include-index --filter 'tag:database'

# Validate all cross-reference links
ansible-doctor generate collection/ --include-index --validate-links
```

**Embedded Section Index**:
```markdown
<!-- collection/README.md.j2 -->
# {{ collection.name }}

{{ collection.description }}

## Available Roles

{{ index('roles', format='table', limit=10) }}

[View all roles](./roles/index.md)
```

**Output**: `quickstart.md`, `data-model.md`, `contracts/index-generator.yaml`, `contracts/mermaid-examples.md`
