# Phase 0: Research & Technology Decisions
## Spec 013: Links & Cross-References

This document captures the research findings and technology decisions made during Phase 0 of the implementation planning process.

---

## 1. Link Validation Libraries

### Decision: `requests` + `beautifulsoup4`

**Rationale**:
- **requests**: Industry-standard HTTP client with excellent error handling, timeout/retry support, and session management for connection pooling
- **beautifulsoup4**: Mature HTML parsing library with simple API for extracting anchors and links
- Combined: Covers both external link validation (HTTP) and anchor extraction (HTML parsing)

**Alternatives Considered**:
1. **urllib3**: Lower-level HTTP library
   - ❌ More complex API, requires manual connection pooling
   - ❌ Less intuitive error handling
   - ✅ Slightly better performance for simple requests
   - **Verdict**: Rejected - requests built on urllib3 provides better DX

2. **httpx**: Modern async HTTP client
   - ✅ Async/await support for high concurrency
   - ✅ HTTP/2 support
   - ❌ Overkill for our use case (batch validation sufficient)
   - ❌ Additional complexity in tests (async fixtures)
   - **Verdict**: Rejected - async not needed for link validation

3. **lxml**: Faster HTML/XML parser
   - ✅ 5-10x faster parsing than beautifulsoup4
   - ❌ C dependency (installation issues on some platforms)
   - ❌ Less forgiving with malformed HTML
   - **Verdict**: Rejected - beautifulsoup4 more robust for real-world HTML

**Implementation Notes**:
- Use `requests.Session()` for connection pooling across multiple external link checks
- Set reasonable timeouts (10s default, configurable via CLI)
- Implement exponential backoff for retry logic (3 retries with 1s, 2s, 4s delays)
- Use `beautifulsoup4` with `html.parser` (built-in, no C dependencies)

---

## 2. Link Graph Algorithms

### Decision: DFS-based Cycle Detection + Adjacency List

**Rationale**:
- **DFS (Depth-First Search)**: Simple, efficient cycle detection in O(V+E) time
- **Adjacency List**: Memory-efficient for sparse graphs (typical documentation link structure)
- **Bidirectional Index**: Maintain both forward and reverse links for fast reverse lookups

**Alternatives Considered**:
1. **Tarjan's Strongly Connected Components**:
   - ✅ Finds all cycles in single pass O(V+E)
   - ✅ Identifies cycle clusters
   - ❌ More complex implementation
   - ❌ Overkill for detecting simple cycles
   - **Verdict**: Rejected - DFS sufficient for our needs

2. **NetworkX Graph Library**:
   - ✅ Rich graph algorithms (shortest path, centrality, clustering)
   - ✅ Visualization support
   - ❌ Heavy dependency (~5MB)
   - ❌ Performance overhead for simple operations
   - **Verdict**: Rejected - custom graph structure more efficient

3. **Adjacency Matrix**:
   - ✅ O(1) edge lookup
   - ❌ O(V²) memory (wasteful for sparse graphs)
   - ❌ Slower iteration over neighbors
   - **Verdict**: Rejected - adjacency list better for sparse documentation graphs

**Implementation Notes**:
- Custom `LinkGraph` class with `dict[Path, set[Link]]` adjacency list
- Maintain reverse index `dict[Path, set[Link]]` for incoming links (bidirectional)
- DFS cycle detection: Mark nodes as VISITING/VISITED, cycle found if VISITING encountered
- Related files discovery: Breadth-First Search (BFS) with configurable max depth

**Performance Targets**:
- Build graph: <5s for 5000 files
- Cycle detection: <1s for complete graph
- Related files (depth=2): <100ms per query

---

## 3. Anchor Extraction Strategies

### Decision: Format-Specific Parsers with GitHub-Compatible Slugs

**Rationale**:
- Each format has unique anchor generation rules
- GitHub-compatible slugs most widely used standard
- Markdown: Headers (#), HTML: id attributes, RST: Sphinx-style anchors

**GitHub Anchor Generation Algorithm**:
```python
def generate_anchor(header_text: str) -> str:
    """Generate GitHub-compatible anchor from header text."""
    slug = header_text.lower()  # Lowercase
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except hyphen/underscore
    slug = re.sub(r'[\s_]+', '-', slug)  # Replace spaces/underscores with hyphens
    slug = slug.strip('-')  # Remove leading/trailing hyphens
    return slug

# Examples:
# "Installation Guide" → "installation-guide"
# "API Reference (v2.0)" → "api-reference-v20"
# "What's New?" → "whats-new"
```

**Format-Specific Parsers**:

1. **Markdown** (`ansibledoctor/utils/anchor_extractor.py`):
   - Parse headers: `# Header`, `## Header`, etc.
   - Extract level (1-6) from `#` count
   - Generate anchor using GitHub algorithm
   - Handle ATX headers (# Header) and Setext headers (underlined)

2. **HTML** (`beautifulsoup4`):
   - Find `<h1>-<h6>` tags
   - Extract `id` attribute if present
   - Generate anchor from text content if no id
   - Handle nested HTML (strip tags, preserve text)

3. **RST** (Markdown conversion fallback):
   - RST headers have no standard anchor format
   - Sphinx generates anchors during build (not in source)
   - Strategy: Convert RST → Markdown → extract anchors
   - Or: Use Sphinx anchor generation rules if Sphinx detected

**Alternatives Considered**:
1. **Pandoc for Unified Parsing**:
   - ✅ Single parser for all formats
   - ❌ External binary dependency
   - ❌ Slower than native Python parsers
   - **Verdict**: Rejected - format-specific parsers more reliable

2. **Regex-Only Parsing**:
   - ✅ Fast, no dependencies
   - ❌ Fragile with edge cases (code blocks, inline code)
   - ❌ Fails on nested structures
   - **Verdict**: Rejected - AST parsing more robust

**Implementation Notes**:
- Cache extracted anchors per file to avoid re-parsing
- Handle duplicate anchors (GitHub appends `-1`, `-2`, etc.)
- Detect anchor changes across doc regenerations (warn if links break)

---

## 4. External Link Validation

### Decision: HTTP HEAD + Caching + Rate Limiting

**Rationale**:
- **HTTP HEAD**: Faster than GET (only checks existence, no body download)
- **Caching**: Avoid re-checking same URLs (TTL: 24 hours)
- **Rate Limiting**: Respect external servers (max 10 req/sec per domain)

**Best Practices Implemented**:

1. **HTTP HEAD Requests**:
   - Send HEAD first to check existence
   - Fallback to GET if HEAD returns 405 (Method Not Allowed)
   - Follow redirects (max 5 hops)
   - Treat 3xx redirects as warnings, not errors

2. **Timeout Strategy**:
   - Connection timeout: 5s
   - Read timeout: 10s
   - Total timeout: 30s (for very slow servers)
   - Configurable via CLI: `--timeout <seconds>`

3. **Retry Logic**:
   - Retry on connection errors, timeouts, 5xx server errors
   - Exponential backoff: 1s, 2s, 4s delays
   - Max 3 retries per link
   - Don't retry on 4xx client errors (permanent failures)

4. **Caching**:
   - In-memory LRU cache (1000 URLs max)
   - Optional disk cache (`~/.cache/ansible-doctor/links/`) for CI/CD
   - Cache key: `(url, timestamp // 86400)` (24-hour TTL)
   - Cache format: JSON `{url: {status, http_status, timestamp}}`

5. **Rate Limiting**:
   - Per-domain rate limiter (max 10 req/sec)
   - Use `requests.Session()` with pooling for same domain
   - Respect `Retry-After` header if present
   - Skip validation if `robots.txt` disallows

6. **User-Agent Header**:
   - Identify as `ansible-doctor/{version} (+https://github.com/thegeeklab/ansible-doctor)`
   - Some servers block requests without User-Agent

**Alternatives Considered**:
1. **Always Use GET Requests**:
   - ❌ Slower (downloads full page)
   - ❌ Wastes bandwidth
   - ✅ More reliable (some servers block HEAD)
   - **Verdict**: Rejected - use HEAD with GET fallback

2. **No Caching**:
   - ❌ Slow for repeated validations (CI/CD pipelines)
   - ❌ Wastes external server resources
   - ✅ Always fresh results
   - **Verdict**: Rejected - caching essential for performance

3. **Ignore robots.txt**:
   - ❌ Unethical, may get IP banned
   - ❌ Violates web standards
   - ✅ Simpler implementation
   - **Verdict**: Rejected - respect robots.txt

**Implementation Notes**:
- Parallel validation using `ThreadPoolExecutor` (max 10 workers)
- Separate workers for internal vs external links (internal faster)
- Progress bar for long validations (`click` with `tqdm`)
- Skip external validation by default (opt-in with `--external`)

**Performance Targets**:
- External link validation: ~500ms per link (with retries)
- Parallel validation: 10-20 links/sec (depending on server latency)
- Cached results: <1ms per link

---

## 5. Link Format Conversion

### Decision: Template-Based Conversion with Format-Specific Renderers

**Rationale**:
- Each output format has unique link syntax
- Template-based approach integrates with existing Jinja2 rendering (Spec 002)
- Relative path resolution handled by `pathlib.Path.relative_to()`

**Link Syntax by Format**:

| Format   | Syntax                                | Example                                           |
|----------|---------------------------------------|---------------------------------------------------|
| Markdown | `[text](url)`                         | `[Role Guide](../roles/demo_role.md)`             |
| HTML     | `<a href="url">text</a>`              | `<a href="../roles/demo_role.html">Role Guide</a>`|
| RST      | `` `text <url>`_ `` or `:ref:`label`` | `` `Role Guide <../roles/demo_role.html>`_ ``     |

**Relative Path Resolution**:
- All links stored as absolute paths internally
- Resolved to relative paths during rendering based on current file location
- Use `pathlib.Path.relative_to()` for cross-platform compatibility

**URL Escaping**:
- Markdown: Escape `()` in URLs as `%28` and `%29`
- HTML: Escape `&`, `<`, `>`, `"` as HTML entities
- RST: Escape backticks as `` `` (double backtick)

**Cross-Reference Templates** (Jinja2):

```jinja2
{# Markdown template #}
{% for ref in cross_references %}
- [{{ ref.target.name }}]({{ ref.target.path | relative_to(current_file) }}) - {{ ref.target.description }}
{% endfor %}

{# HTML template #}
<ul class="cross-references">
{% for ref in cross_references %}
  <li><a href="{{ ref.target.path | relative_to(current_file) }}">{{ ref.target.name }}</a> - {{ ref.target.description }}</li>
{% endfor %}
</ul>

{# RST template #}
{% for ref in cross_references %}
- `{{ ref.target.name }} <{{ ref.target.path | relative_to(current_file) }}>`_ - {{ ref.target.description }}
{% endfor %}
```

**Alternatives Considered**:
1. **Pandoc for Link Conversion**:
   - ✅ Handles all format conversions
   - ❌ External dependency (binary)
   - ❌ Slower than template-based approach
   - ❌ Limited control over link generation
   - **Verdict**: Rejected - template approach more flexible

2. **Separate Link Renderers per Format**:
   - ✅ Clear separation of concerns
   - ✅ Easy to extend for new formats
   - ❌ Duplicates logic (relative path resolution)
   - **Verdict**: Accepted - use template-based renderers with shared utilities

**Implementation Notes**:
- Extend existing `ansibledoctor/generator/renderers.py` with link rendering
- Add `relative_to` Jinja2 filter for path resolution
- Add `escape_link` filter for format-specific escaping
- Integrate with existing template system (no new dependencies)

**Integration with Spec 002 (Doc Generation)**:
- Hook into document generation pipeline after content rendering
- Generate cross-references automatically based on metadata
- Build navigation sections (TOC) during rendering
- Validate generated links before writing output files

---

## Summary of Technology Stack

| Component              | Technology               | Rationale                                      |
|------------------------|--------------------------|------------------------------------------------|
| HTTP Link Validation   | `requests`               | Industry standard, excellent error handling    |
| HTML Parsing           | `beautifulsoup4`         | Mature, robust with malformed HTML             |
| Graph Structure        | Custom Adjacency List    | Memory-efficient, fast for sparse graphs       |
| Cycle Detection        | DFS Algorithm            | Simple, O(V+E) time complexity                 |
| Anchor Generation      | GitHub-Compatible Slugs  | Widely adopted standard                        |
| Link Format Conversion | Jinja2 Templates         | Integrates with existing rendering pipeline    |
| Caching                | In-Memory LRU + Disk     | Fast, persistent across CI/CD runs             |
| Rate Limiting          | Per-Domain Throttling    | Respect external servers                       |
| Parallel Validation    | `ThreadPoolExecutor`     | Simple, built-in, suitable for I/O-bound tasks |

**No New Major Dependencies**: All libraries align with Python standard library + existing project dependencies (pydantic, Jinja2 already in use).

**Performance Profile**:
- Link extraction: <50ms per file (1000 files in ~50s)
- Internal link validation: <100ms per link
- External link validation: ~500ms per link (with retries, cached <1ms)
- Graph cycle detection: <1s for 5000 files
- Related files query: <100ms per file

**Testing Strategy**:
- Mock HTTP responses using `responses` library (already in project)
- Fixture-based tests with sample docs containing various link types
- Property-based testing for anchor generation (ensure idempotency, uniqueness)
- Integration tests with live external links (run nightly, not in CI)

---

## Next Steps

1. **Phase 1: Design** → Create detailed data models, API contracts, CLI extensions
2. **Implementation** → Build link management module based on these decisions
3. **Testing** → Comprehensive unit/integration tests with mock HTTP responses
4. **Documentation** → Update user guides with link validation workflows
5. **CI/CD Integration** → Add link validation to GitHub Actions workflow

---

**Document Metadata**:
- Created: {{ now }}
- Spec: 013-links-cross-references
- Phase: 0 (Research)
- Status: Complete
- Reviewers: [To be assigned]
