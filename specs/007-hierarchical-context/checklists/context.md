# Checklist: Hierarchical Context Detection Requirements Quality

Purpose: Validate `specs/007-hierarchical-context/spec.md` for clarity, completeness, consistency, measurability, and edge-case coverage for parent detection and breadcrumb generation.

- [ ] CHK001 - Are all parent detection markers specified (galaxy.yml for collection; ansible.cfg or playbooks/ for project) and search algorithm details (max levels = 3)? [Completeness, TC-001]
- [ ] CHK002 - Is the search depth and early-stop behavior defined and measurable (stop after 3 levels or earlier)? [Measurability, TC-001]
- [ ] CHK003 - Are the fallback behaviors specified when parent markers are not found (standalone marking, logging) and `--no-parent` justifications? [Clarity, SC-005]
- [ ] CHK004 - Does the spec mention the naming conventions/slugs used in breadcrumbs and links (e.g., `collection_{ns}.{collection}`) or mark as integration with naming conventions (Gap)? [Consistency, Gap]
- [ ] CHK005 - Are breadcrumb generation rules specified (order, clickable links when docs exist, plain text otherwise) and template examples included? [Clarity, SC-003]
- [ ] CHK006 - Is sibling discovery behavior defined (what components are considered siblings, limit = 50, sort/ordering rules)? [Completeness, TC-008]
- [ ] CHK007 - Are relative link generation rules explicit (relative links assuming `docs/lang/{code}/` output structure) and examples provided? [Consistency, TC-003]
- [ ] CHK008 - Is caching/persistence of detection results during a generation session defined and measurable? [Measurability, SC-007, TC-002]
- [ ] CHK009 - Are edge cases defined: multiple candidates found for parent markers, inconsistent galaxy.yml formats, nested collections? [Edge Case Coverage]
- [ ] CHK010 - Is CLI integration described (`--no-parent`, `--no-breadcrumbs`, `--no-siblings`) and precedence rules documented (CLI vs config)? [Completeness, US22]
- [ ] CHK011 - Is the behavior for generating breadcrumbs in multi-language outputs defined (translated labels, language-specific links)? [Coverage, SC-008]
- [ ] CHK012 - Are tests defined to validate breadcrumb link resolution when parent documentation exists vs when it does not (link vs plain text)? [Traceability, SC-003]
- [ ] CHK013 - Are performance tests described and measurable for parent detection overhead (<500ms) including caching scenarios? [Measurability, SC-006]
- [ ] CHK014 - Are observability/logging rules defined for detection (info-level, warnings when parent found/no docs)? [Observability, Spec §Notes]
- [ ] CHK015 - Are security considerations covered if parent detection traverses symlinks or network-mounted directories? [Security/Edge Cases]
- [ ] CHK016 - Does the spec define how the breadcrumb generator handles missing parent docs (breadcrumb text without link) in the UI templates? [Clarity, SC-009]
- [ ] CHK017 - Is the integration with Hierarchical Context (Feature 007) and templates (Feature 002) explicitly described and tested in integration tests? [Traceability, Integration]
- [ ] CHK018 - Are sibling listing limits (50) and handling very large collections/projects defined and tested for pagination/overflow? [Non-Functional, TC-008]

If any item above is marked [Gap], clarify or update the spec to include naming conventions for link and slug generation, multi-language breadcrumb behavior, symlink/security handling, and edge-case behavior for nested collections.