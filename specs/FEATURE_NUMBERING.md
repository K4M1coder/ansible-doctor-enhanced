# Feature Numbering Guide

## Current Feature Numbering

| Feature ID | Folder | Branch | Status | Notes |
| --- | --- | --- | --- | --- |
| 001 | `001-ansible-role-parser` | `001-ansible-role-parser` | ✅ Complete | v0.2.0 |
| 002 | `002-doc-generator` | `002-doc-generator` | ✅ Complete | v0.3.0 |
| 003 | `003-role-parity` | `003-role-parity` | ✅ Complete | v0.4.0 |
| 004 | `004-collection-support` | `004-collection-support` | ✅ Complete | v0.5.0 |
| 005 | `005-i18n-support` | `005-i18n-support` | ✅ Complete | v0.6.0 |
| 006 | `006-project-docs` | `006-project-docs` | ✅ Complete | v0.7.0 |
| 007 | `007-hierarchical-context` | `007-hierarchical-context` | ✅ Complete | v0.8.0 |
| 008 | `008-template-customization` | `008-template-customization` | ✅ Complete | v0.8.0 |
| 009 | `009-execution-reports-and-logs` | `009-execution-reports-and-logs` | ✅ Complete | v0.9.0 |
| 010 | `010-error-reports-and-recovery` | `010-error-reports-and-recovery` | ✅ Complete | v0.10.0 |
| 011 | `011-indexes-navigation` | `011-indexes-navigation` | 🟡 In progress (MVP complete) | v0.10.0 |
| 012 | `012-schema-documentation` | `012-schema-documentation` | ✅ Complete | v0.10.0 |
| 013 | `013-links-cross-references` | `013-links-cross-references` | 🟡 In progress (MVP complete) | v0.11.0 |

> Note: **Branch** should match the folder name; **Status** reflects the spec/implementation state as of the last update.
> Note: **Branch** should match the folder name; **Status** reflects the spec/implementation state as of the last update.

## Known Numbering Issues

### Issue #2: Version/Feature Alignment

The roadmap uses version milestones (x.y.z) while specs use feature numbers (`00y`) and task use patch numbers (`00z`) release use manual number (`00x`). Maintaining a clear mapping reduces confusion when features span multiple versions.

**Current Mapping**:

| Feature(s) | Target Version |
| ------------ | ---------------- |
| 001-003 | v0.2.0 - v0.4.0 |
| 004 | v0.5.0 |
| 005 | v0.6.0 |
| 006 | v0.7.0 |
| 007 | v0.8.0 |
| 008-010 | v0.9.0 - v0.10.0 |
| 011-012 | v0.10.0 |
| 013 | v0.11.0 |

**Current release**: **v0.12.*** (repository is at v0.12.x as of this update). Please ensure `ROADMAP.md` is synchronized if versions listed above need adjustment to reflect patch/minor releases beyond v0.11.0.

**Guidance**: Keep feature milestones in ROADMAP.md up to date when specs move between "draft", "planned", and "complete". When multiple features target the same version, ensure dependencies and sequencing are documented in each spec's `plan.md`. If the repository release version changes (e.g., v0.12.x), consider annotating features that were included in the release and note any remaining deferred work.

## Outstanding / Deferred Tasks (per-spec) ⚠️

Below are the notable optional or deferred tasks discovered while reviewing each spec's `tasks.md`. These are *non-blocking* items that can be scheduled as follow-up work or tracked in the backlog.

- **001 — Ansible Role Parser**: T230 (Add integration tests for role slug output and legacy compatibility) remains open.
- **004 — Collection Support**: Refactor items T165 (parallel plugin discovery) and T166 (template caching) are deferred.
- **011 — Indexes & Navigation**: Regression checks T094-T096 (run existing test suites and verify generation without `--include-index`), and client-side filtering test T078 are outstanding.
- **012 — Schema Documentation**: Future enhancements T086 (schema versioning) and T087 (schema diff) are optional and deferred.
- **013 — Links & Cross-References**: Link health/monitoring and remediation tasks T084-T087 (LinkHealthMonitor, linkreport, linkfix) and large-scale performance test T089 are deferred post-MVP.

## Guidance for Maintainers

### Adding New Features

1. **Check existing numbers**: Verify the next feature number isn't already used
2. **Single folder per feature**: Create only one `specs/00X-feature-name/` folder
3. **Consistent naming**: Branch name should match folder pattern (`00X-feature-name`)
4. **Update ROADMAP.md**: Add entry with version target

### Resolving Conflicts

If you discover duplicate or conflicting feature specs:

1. Identify which spec is more complete
2. Document the conflict in this file
3. Create consolidation task in tasks.md
4. Mark deprecated spec with clear notice pointing to canonical location

---

**Current Release**: v0.12.*
**Last Updated**: 2026-01-10
**Document Status**: Living document - update as numbering issues are discovered/resolved
