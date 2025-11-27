# Checklist: Collection Documentation Requirements Quality

Purpose: Validate the Collection Documentation spec (`specs/004-collection-support/spec.md`) for completeness, clarity, consistency, measurability, and coverage.

- [ ] CHK001 - Is the required `galaxy.yml` schema and required field set clearly specified (namespace, name, version, authors, dependencies)? [Completeness, Spec §US8, SC-001]
- [ ] CHK002 - Are optional fields (tags, license, repository) demarcated and expected behavior for them spelled out (e.g., included or deferred)? [Clarity, Spec §Clarifications]
- [ ] CHK003 - Is the collection naming convention and output path explicitly defined (e.g., `collection_{namespace}.{collection}/`) including how slugs are generated? [Completeness, Spec §Objective, Gap]
- [ ] CHK004 - Is role discovery within a collection defined with precise scanning rules (paths to scan, file patterns, and exclusion rules)? [Clarity, TC-002]
- [ ] CHK005 - Are plugin discovery rules and expected output sections defined for all plugin types (module, filters, inventory, lookup)? [Completeness, Spec §US9]
- [ ] CHK006 - Are dependency resolution rules for collection dependencies specified, including how version constraints are handled for display and warnings? [Clarity, SC-004]
- [ ] CHK007 - Is the cross-role dependency analysis algorithm and expected visual output defined (Mermaid diagram or alternative) and measurable? [Measurability, SC-005]
- [ ] CHK008 - Does the spec define performance expectations with measurable tests (e.g., <5s for a typical collection)? [Measurability, SC-006]
- [ ] CHK009 - Are CLI commands and flags specified and consistent for `collection parse`, `collection generate`, and `collection analyze`? [Completeness, SC-008]
- [ ] CHK010 - Does the spec define integration with the template engine and where collection-specific templates are loaded (site-local, collection-level directories)? [Consistency, TC-003]
- [ ] CHK011 - Are multi-language docs behavior and expected output per language described or explicitly marked as integration with Feature 005? [Coverage, Spec §Dependencies, Gap]
- [ ] CHK012 - Are error and warning semantics defined for missing galaxy.yml or malformed fields (should parse fail or continue with best-effort)? [Edge Case Coverage, SC-001]
- [ ] CHK013 - Are sample output examples documenting `docs/lang/{code}/collections/` paths included for the UI and CLI? [Clarity, Spec §Objective]
- [ ] CHK014 - Do tests include cases for local file collections, git-sourced collections, and ansible-galaxy installed collections? [Coverage, TC-004]
- [ ] CHK015 - Is the expected behavior when a collection includes modules or plugins with syntax errors defined (skip, warn, fail)? [Edge Case & Observability, TC-002]
- [ ] CHK016 - Are integration test scenarios defined for collection + role generation (role docs nested under collection docs) and their layout? [Coverage, SC-003]
- [ ] CHK017 - Is a migration or compatibility plan described if output naming is changed (collection slug format)? [Consistency / SemVer, Gap]
- [ ] CHK018 - Are security implications (parsing untrusted code in `plugins/` or running code) addressed in the spec or marked as Out-of-Scope? [Security, Gap]
- [ ] CHK019 - Is expected behavior for embedded `docs/` vs generated docs specified (do embedded READMEs remain untouched)? [Clarity, Gap]
- [ ] CHK020 - Are observability requirements (structured logging, warnings for circular dependencies) defined and testable? [Non-Functional Requirements, Spec §Success Criteria]

If any item above is marked [Gap], please clarify or add to the spec: examples (output path naming), multi-language integration, error semantics for parsing, and security considerations.