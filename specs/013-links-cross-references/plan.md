# Implementation Plan: Links & Cross-References

**Branch**: `013-links-cross-references` | **Date**: 2025-12-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-links-cross-references/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Provide comprehensive link management and cross-reference capabilities for ansible-doctor documentation. Enable automatic internal links between roles/collections/projects, section-to-section navigation with anchors, broken link detection (internal and external), integration with official Ansible documentation, and bidirectional cross-references. Extends Spec 002 (Document Generation) with intelligent linking and Spec 011 (Indexes) with enhanced navigation. Transforms isolated documentation files into a cohesive, interconnected knowledge network.

## Technical Context

**Language/Version**: Python 3.11+ (existing project baseline)  
**Primary Dependencies**: pydantic (existing, models), requests (NEW, HTTP link validation), beautifulsoup4 (NEW, HTML anchor parsing), markdown (existing, Markdown parsing)  
**Storage**: Link graph in memory during generation, link validation cache, broken link reports (JSON/text)  
**Testing**: pytest with link validation fixtures, mock HTTP responses for external link tests, graph cycle detection tests  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) with Markdown/HTML/RST output  
**Project Type**: Single project - documentation enhancement extending existing generator  
**Performance Goals**: <30s link validation for 1000 docs, <100ms link resolution per document, <50ms anchor extraction per file  
**Constraints**: Must support relative and absolute links, must handle circular references gracefully, must work offline (external link validation optional), must preserve existing link syntax  
**Scale/Scope**: Support documentation sets with 5000+ files, 50000+ links, 10+ nesting levels, detect cycles in dependency graphs, validate external links to 100+ domains

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Test-First Development**: PASS  
  - Rationale: Link validation is highly testable. Write tests for link parsing, validation (internal/external), cycle detection, anchor extraction, then implement LinkValidator, CrossReferenceGenerator. Mock HTTP responses for external link testing enables TDD workflow.

- **Library-First Architecture**: PASS  
  - Rationale: New `links/link_manager.py`, `links/link_validator.py`, `links/cross_reference_generator.py` modules are pure Python libraries. LinkManager protocol is independent. CLI integration in `cli/linkcheck.py` only wraps library calls.

- **CLI Mandate**: PASS  
  - Rationale: New CLI commands `ansible-doctor linkcheck`, `ansible-doctor linkfix`, `ansible-doctor linkreport`. Extends existing CLI structure with link validation subcommands.

- **Observability**: PASS  
  - Rationale: Link validation emits structured logs with broken links, validation timing, external link HTTP status codes. Link health monitoring logs link check results. Execution reports (Spec 009) include link validation metrics.

- **Backward Compatibility**: PASS  
  - Rationale: No breaking changes. Extends existing document generation with optional link validation. Existing documentation generation unchanged. Link validation is opt-in via `--validate-links` flag or config option.

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

```text
ansibledoctor/
├── models/
│   ├── link.py                      # NEW: Link, LinkType, LinkStatus models
│   └── cross_reference.py           # EXTEND: Add bidirectional references (from Spec 011)
├── links/
│   ├── __init__.py                  # NEW: Links module
│   ├── link_manager.py              # NEW: LinkManager implementation
│   ├── link_validator.py            # NEW: LinkValidator (internal/external)
│   ├── cross_reference_generator.py # NEW: CrossReferenceGenerator
│   ├── navigation_builder.py        # NEW: NavigationBuilder (TOC, section links)
│   ├── external_link_integrator.py  # NEW: ExternalLinkIntegrator (Ansible docs)
│   └── link_health_monitor.py       # NEW: LinkHealthMonitor (reporting)
├── utils/
│   ├── link_parser.py               # NEW: Parse links from Markdown/HTML/RST
│   ├── anchor_extractor.py          # NEW: Extract section anchors from files
│   └── link_graph.py                # NEW: Graph data structure for link relationships
├── cli/
│   ├── __init__.py                  # EXTEND: Add link commands
│   └── linkcheck.py                 # NEW: linkcheck, linkfix, linkreport commands
└── generator/
    └── __init__.py                  # EXTEND: Add link generation to doc generation

tests/
├── unit/
│   ├── test_link_models.py          # NEW: Link, CrossReference model tests
│   ├── test_link_validator.py       # NEW: Link validation tests (mocked HTTP)
│   ├── test_link_parser.py          # NEW: Link parsing tests
│   ├── test_anchor_extractor.py     # NEW: Anchor extraction tests
│   ├── test_navigation_builder.py   # NEW: TOC/section link tests
│   ├── test_link_graph.py           # NEW: Graph cycle detection tests
│   └── test_cross_reference_gen.py  # NEW: Cross-reference generation tests
├── integration/
│   ├── test_link_validation_e2e.py  # NEW: End-to-end link validation
│   ├── test_external_links.py       # NEW: External link integration (live HTTP)
│   └── test_link_generation.py      # NEW: Link generation in doc workflow
└── fixtures/
    ├── docs_with_links/             # NEW: Sample docs with various link types
    │   ├── valid_links.md
    │   ├── broken_links.md
    │   └── circular_refs.md
    └── external_responses/          # NEW: Mock HTTP responses for testing
        ├── ansible_docs_200.html
        └── broken_link_404.html
```

**Structure Decision**: Single project structure extending existing `ansibledoctor/` package. New `links/` module for all link management logic colocated with existing generator modules. CLI extensions in `cli/linkcheck.py` follow pattern of existing CLI structure. Tests mirror source structure with comprehensive fixture library for link validation scenarios and mock HTTP responses.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all gates pass. No additional complexity justification required.

---

## Phase 0: Research & Planning

### Research Tasks

1. **Link Validation Libraries**: Evaluate Python libraries for HTTP link checking and HTML parsing
   - `requests` (recommended): HTTP client for external link validation with timeout/retry support
   - `urllib3`: Lower-level HTTP, more control but more complex
   - `beautifulsoup4`: HTML parsing for anchor extraction
   - `lxml`: Fast XML/HTML parsing alternative
   - Decision criteria: Performance, error handling, timeout support, proxy support

2. **Link Graph Algorithms**: Study graph algorithms for link relationship management
   - Cycle detection algorithms (DFS, Tarjan's strongly connected components)
   - Bidirectional link relationships (extends Spec 011 CrossReference)
   - Graph traversal for "related content" discovery
   - Shortest path algorithms for navigation optimization
   - Decision criteria: Performance on large graphs (5000+ nodes), memory usage

3. **Anchor Extraction Strategies**: Research approaches for extracting section anchors from documents
   - Markdown: Parse headers (#, ##, ###) and generate anchor slugs
   - HTML: Parse `<h1>-<h6>` tags and extract `id` attributes
   - RST: Parse section markers and Sphinx-generated anchors
   - GitHub anchor generation algorithm (lowercase, hyphenate, special char handling)
   - Decision criteria: Accuracy, cross-format consistency, performance

4. **External Link Validation**: Investigate best practices for validating external links
   - HTTP HEAD requests (faster than GET, only checks existence)
   - Timeout and retry strategies (avoid hanging on slow servers)
   - Caching validation results (avoid re-checking same URLs)
   - Respecting robots.txt and rate limiting
   - Decision criteria: Speed, reliability, respect for external servers

5. **Link Format Conversion**: Study link syntax differences across output formats
   - Markdown: `[text](url)` syntax
   - HTML: `<a href="url">text</a>` with proper escaping
   - RST: `` `text <url>`_ `` inline syntax or `.. _label:` references
   - Relative vs absolute path resolution
   - Decision criteria: Syntax correctness, cross-format compatibility

**Output**: `research.md` with findings, decisions, and rationale for each topic

---

## Phase 1: Design & Contracts

### Data Model Design

**Link** (Base Model):

```python
from enum import Enum
from pathlib import Path

class LinkType(str, Enum):
    \"\"\"Types of links in documentation.\"\"\"
    INTERNAL_FILE = "internal_file"      # Link to another doc file
    INTERNAL_SECTION = "internal_section"  # Anchor link within same file
    CROSS_REFERENCE = "cross_reference"  # Link to related content
    EXTERNAL_URL = "external_url"        # External HTTP/HTTPS link
    RELATIVE_PATH = "relative_path"      # Relative file path
    ABSOLUTE_PATH = "absolute_path"      # Absolute file path

class LinkStatus(str, Enum):
    \"\"\"Link validation status.\"\"\"
    VALID = "valid"
    BROKEN = "broken"
    REDIRECT = "redirect"
    TIMEOUT = "timeout"
    NOT_CHECKED = "not_checked"

class Link(BaseModel):
    \"\"\"Represents a link in documentation.\"\"\"
    source_file: Path  # File containing the link
    target: str  # Link target (URL, file path, or anchor)
    link_type: LinkType
    text: str | None  # Link text/title
    line_number: int | None  # Line number in source file
    status: LinkStatus = LinkStatus.NOT_CHECKED
    http_status: int | None  # HTTP status code for external links
    error_message: str | None  # Error message if broken
    last_checked: datetime | None  # Last validation timestamp
    
    @property
    def is_valid(self) -> bool:
        \"\"\"Check if link is valid.\"\"\"
        return self.status == LinkStatus.VALID
    
    @classmethod
    def from_markdown(cls, source: Path, match: re.Match) -> "Link":
        \"\"\"Parse link from Markdown regex match.\"\"\"
        ...
```

**CrossReference** (Extended from Spec 011):

```python
class CrossReference(BaseModel):
    \"\"\"Bidirectional cross-reference between documentation items.\"\"\"
    source: IndexItem  # From Spec 011
    target: IndexItem
    link_type: Literal["dependency", "used_by", "related", "parent", "child"]
    forward_link: Link | None  # Link from source to target
    backward_link: Link | None  # Link from target back to source (bidirectional)
    strength: float = 1.0  # Relationship strength (0.0-1.0)
    
    @property
    def is_bidirectional(self) -> bool:
        \"\"\"Check if cross-reference has both forward and backward links.\"\"\"
        return self.forward_link is not None and self.backward_link is not None
```

**NavigationSection**:

```python
class NavigationSection(BaseModel):
    \"\"\"Section navigation entry for table of contents.\"\"\"
    title: str
    anchor: str  # URL-safe anchor (e.g., "installation-guide")
    level: int  # Heading level (1-6)
    line_number: int
    children: list["NavigationSection"] = Field(default_factory=list)
    
    @property
    def depth(self) -> int:
        \"\"\"Calculate depth in navigation tree.\"\"\"
        ...
    
    def to_link(self, base_url: str) -> Link:
        \"\"\"Convert to Link object.\"\"\"
        ...
```

**LinkValidationResult**:

```python
class LinkValidationResult(BaseModel):
    \"\"\"Result of link validation operation.\"\"\"
    total_links: int
    valid_links: int
    broken_links: int
    external_links_checked: int
    links: list[Link]
    duration_ms: float
    validation_timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        \"\"\"Calculate link validation success rate.\"\"\"
        return self.valid_links / self.total_links if self.total_links > 0 else 1.0
    
    def format_report(self, show_valid: bool = False) -> str:
        \"\"\"Generate human-readable validation report.\"\"\"
        ...
```

**LinkGraph**:

```python
class LinkGraph:
    \"\"\"Graph data structure for link relationships.\"\"\"
    
    def __init__(self):
        self.nodes: dict[Path, set[Link]] = {}  # File -> outgoing links
        self.reverse_index: dict[Path, set[Link]] = {}  # File -> incoming links
    
    def add_link(self, link: Link) -> None:
        \"\"\"Add link to graph.\"\"\"
        ...
    
    def find_cycles(self) -> list[list[Link]]:
        \"\"\"Detect circular link dependencies using DFS.\"\"\"
        ...
    
    def get_related_files(
        self,
        file: Path,
        max_depth: int = 2,
    ) -> list[tuple[Path, int]]:
        \"\"\"Find files related to given file within max_depth hops.\"\"\"
        ...
```

### API Contracts

**LinkValidator Protocol**:

```python
class LinkValidator(Protocol):
    \"\"\"Protocol for validating links in documentation.\"\"\"
    
    def validate_link(
        self,
        link: Link,
        output_dir: Path,
        check_external: bool = False,
    ) -> Link:
        \"\"\"
        Validate single link.
        
        Args:
            link: Link to validate
            output_dir: Base directory for resolving relative paths
            check_external: Whether to check external HTTP links
        
        Returns:
            Updated Link with validation status
        \"\"\"
        ...
    
    def validate_file(
        self,
        file_path: Path,
        output_dir: Path,
        check_external: bool = False,
    ) -> LinkValidationResult:
        \"\"\"Validate all links in a file.\"\"\"
        ...
    
    def validate_all(
        self,
        docs_dir: Path,
        check_external: bool = False,
        parallel: bool = True,
    ) -> LinkValidationResult:
        \"\"\"
        Validate all links in documentation set.
        
        Args:
            docs_dir: Documentation directory
            check_external: Whether to check external links
            parallel: Use parallel validation for performance
        
        Returns:
            Aggregated validation results
        \"\"\"
        ...
```

**CrossReferenceGenerator**:

```python
class CrossReferenceGenerator:
    \"\"\"Generate automatic cross-references between documentation.\"\"\"
    
    def generate_cross_references(
        self,
        items: list[IndexItem],  # From Spec 011
    ) -> list[CrossReference]:
        \"\"\"
        Generate cross-references based on relationships.
        
        Creates bidirectional links for:
        - Dependencies (A depends on B → B used by A)
        - Parent-child (Collection contains Role → Role part of Collection)
        - Similar functionality (based on tags, descriptions)
        \"\"\"
        ...
    
    def generate_related_links(
        self,
        item: IndexItem,
        all_items: list[IndexItem],
        max_related: int = 5,
    ) -> list[CrossReference]:
        \"\"\"
        Find related items based on similarity.
        
        Uses tags, descriptions, dependencies for similarity scoring.
        \"\"\"
        ...
```

**NavigationBuilder**:

```python
class NavigationBuilder:
    \"\"\"Build navigation structures for documents.\"\"\"
    
    def build_toc(
        self,
        file_path: Path,
        max_depth: int = 3,
    ) -> list[NavigationSection]:
        \"\"\"
        Build table of contents from document headers.
        
        Args:
            file_path: Document file
            max_depth: Maximum heading depth to include
        
        Returns:
            Hierarchical list of navigation sections
        \"\"\"
        ...
    
    def generate_section_links(
        self,
        toc: list[NavigationSection],
        format: Literal["markdown", "html", "rst"] = "markdown",
    ) -> str:
        \"\"\"Generate formatted section links for TOC.\"\"\"
        ...
```

**ExternalLinkIntegrator**:

```python
class ExternalLinkIntegrator:
    \"\"\"Integrate links to external documentation resources.\"\"\"
    
    def __init__(self, ansible_version: str = "latest"):
        self.ansible_version = ansible_version
        self.base_urls = {
            "ansible_docs": f"https://docs.ansible.com/ansible/{ansible_version}/",
            "ansible_galaxy": "https://galaxy.ansible.com/",
            "ansible_github": "https://github.com/ansible/ansible",
        }
    
    def generate_module_link(self, module_name: str) -> str:
        \"\"\"Generate link to Ansible module documentation.\"\"\"
        ...
    
    def generate_collection_link(
        self,
        namespace: str,
        name: str,
    ) -> str:
        \"\"\"Generate link to Ansible Galaxy collection page.\"\"\"
        ...
    
    def generate_best_practices_link(self, topic: str) -> str | None:
        \"\"\"Generate link to relevant best practices guide.\"\"\"
        ...
```

### CLI Extensions

**New Commands in `ansibledoctor/cli/linkcheck.py`**:

```python
@click.group()
def linkcheck():
    \"\"\"Link validation and health monitoring commands.\"\"\"
    pass

@linkcheck.command(\"check\")
@click.argument(\"docs_dir\", type=click.Path(exists=True))
@click.option(\"--external\", is_flag=True, help=\"Check external HTTP links\")
@click.option(\"--parallel\", is_flag=True, default=True, help=\"Use parallel validation\")
@click.option(\"--timeout\", type=int, default=10, help=\"HTTP request timeout (seconds)\")
@click.option(\"--output\", \"-o\", type=click.Path(), help=\"Output report file\")
def check_command(docs_dir: str, external: bool, parallel: bool, timeout: int, output: str | None):
    \"\"\"Validate all links in documentation.\"\"\"
    ...

@linkcheck.command(\"fix\")
@click.argument(\"docs_dir\", type=click.Path(exists=True))
@click.option(\"--dry-run\", is_flag=True, help=\"Show fixes without applying\")
@click.option(\"--backup\", is_flag=True, default=True, help=\"Create backups before fixing\")
def fix_command(docs_dir: str, dry_run: bool, backup: bool):
    \"\"\"Automatically fix broken links where possible.\"\"\"
    ...

@linkcheck.command(\"report\")
@click.argument(\"docs_dir\", type=click.Path(exists=True))
@click.option(\"--format\", type=click.Choice([\"text\", \"json\", \"html\"]), default=\"text\")
@click.option(\"--output\", \"-o\", type=click.Path(), help=\"Output report file\")
def report_command(docs_dir: str, format: str, output: str | None):
    \"\"\"Generate link health report.\"\"\"
    ...
```

### Integration Points

1. **Spec 002 (Document Generation) Extension**:
   - Add link generation hooks during doc rendering
   - Generate cross-references automatically
   - Build navigation sections (TOC)

2. **Spec 011 (Indexes) Integration**:
   - Use CrossReference model for bidirectional links
   - Enhance index pages with smart linking
   - Build link graph from index structures

3. **Spec 012 (Schema) Integration**:
   - Use schema cross-references for intelligent linking
   - Validate link schemas

### Quickstart Example

**Validate Links**:

```bash
# Check all links in documentation
ansible-doctor linkcheck docs/

# Include external link validation
ansible-doctor linkcheck docs/ --external

# Generate JSON report
ansible-doctor linkcheck docs/ --output link-report.json
```

**Fix Broken Links**:

```bash
# Dry-run to preview fixes
ansible-doctor linkcheck fix docs/ --dry-run

# Apply fixes with backup
ansible-doctor linkcheck fix docs/ --backup
```

**Generate Link Report**:

```bash
# Text report
ansible-doctor linkcheck report docs/

# HTML report
ansible-doctor linkcheck report docs/ --format html --output link-health.html
```

**Output**: `quickstart.md`, `data-model.md`, `contracts/link-validator.yaml`, `contracts/link-graph-examples.md`

| Violation | Why Needed | Simpler Alternative Rejected Because |
| ----------- | ------------ | ------------------------------------- |
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
