# Feature Numbering Guide

## Current Feature Numbering

| Feature ID | Folder | Branch | Status | Notes |
|------------|--------|--------|--------|-------|
| 001 | `001-ansible-role-parser` | `001-ansible-role-parser` | ✅ Complete | v0.2.0 |
| 002 | `002-doc-generator` | `002-doc-generator` | ✅ Complete | v0.3.0 |
| 003 | `003-role-parity` | `003-role-parity` | ✅ Complete | v0.4.0 |
| 004 | `004-collection-support` | `004-collection-support` | ✅ Complete | v0.5.0 |
| 005 | `005-i18n-support` | `005-i18n-support` | ✅ Complete | v0.6.0 |
| 006 | `006-project-docs` | `006-project-docs` | ✅ Complete | v0.7.0 |
| 007 | **See Note** | `007-hierarchical-context` | 🔶 Planned | v0.8.0 |
| 008 | `008-template-customization` | `008-template-customization` | 🔶 Planned | v0.8.0 |

## Known Numbering Issues

### Issue #1: Duplicate Feature 007 Folders

**Problem**: Two folders exist with feature number 007:
- `specs/007-hierarchical-context/` - Full specification for hierarchical context detection
- `specs/007-project-navigation/` - Abbreviated spec for project navigation/breadcrumbs

**Root Cause**: These specs describe overlapping functionality. Both address:
- Breadcrumb navigation
- Parent/child context detection
- Hierarchical component relationships

**Resolution** (Recommended):
1. **Primary Spec**: Use `007-hierarchical-context/` as the canonical specification
   - Contains detailed user stories (US19-US24)
   - Includes comprehensive technical requirements
   - Has full task breakdown in tasks.md
   
2. **Merge or Deprecate**: `007-project-navigation/` should be either:
   - Merged into `007-hierarchical-context/` (if any unique content exists)
   - Marked as deprecated with a redirect note

**Action Items for Maintainers**:
- [ ] Review both specs for any unique requirements
- [ ] Consolidate into single spec under `007-hierarchical-context/`
- [ ] Either delete or add deprecation notice to `007-project-navigation/`
- [ ] Update ROADMAP.md to reference canonical spec location

### Issue #2: Version/Feature Alignment

The roadmap uses version numbers (v0.x.0) while specs use feature numbers (00x).
This creates a natural mapping but can cause confusion when features span versions.

**Current Mapping**:
| Feature | Target Version |
|---------|----------------|
| 001-003 | v0.2.0 - v0.4.0 |
| 004 | v0.5.0 |
| 005 | v0.6.0 |
| 006 | v0.7.0 |
| 007-008 | v0.8.0 |

**Guidance**: Features 007 and 008 are both targeted for v0.8.0 as they can be developed in parallel.

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

**Last Updated**: 2025-12-01
**Document Status**: Living document - update as numbering issues are discovered/resolved
