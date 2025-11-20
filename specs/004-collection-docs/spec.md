# Feature Specification: Collection Documentation

**Feature Branch**: `004-collection-docs`  
**Created**: 2025-11-17  
**Milestone**: v0.5.0  
**Prerequisites**: v0.4.0 (Role Parity) COMPLETE ✅  
**Status**: Planned (Blocked until v0.4.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Extend ansible-doctor-enhanced to document Ansible collections, which are bundles of roles, plugins, modules, and playbooks. Collections are the modern Ansible distribution format (Ansible 2.9+). This feature enables documentation at a higher abstraction level than individual roles.

## What is an Ansible Collection?

An Ansible Collection is a package format introduced in Ansible 2.9+ that bundles:
- **Roles**: Multiple roles under `roles/`
- **Plugins**: Custom plugins under `plugins/`
- **Modules**: Custom modules under `plugins/modules/`
- **Playbooks**: Sample playbooks under `playbooks/`
- **Documentation**: READMEs, changelogs, licenses
- **Metadata**: `galaxy.yml` with collection info, dependencies

**Collection Structure**:
```
my_namespace.my_collection/
├── galaxy.yml                 # Collection metadata
├── README.md                  # Collection overview
├── CHANGELOG.md              # Version history
├── roles/
│   ├── role1/                # Individual role
│   └── role2/
├── plugins/
│   ├── modules/              # Custom modules
│   ├── inventory/            # Inventory plugins
│   └── filter/               # Filter plugins
├── playbooks/                # Example playbooks
├── tests/                    # Integration tests
└── docs/                     # Additional documentation
```

## User Scenarios

### US8 - Parse Collection Metadata (Priority: P1) 🎯 MVP

As a collection maintainer, I want to parse my collection's `galaxy.yml` so that I can generate documentation that includes collection name, namespace, version, dependencies, and author information.

**Independent Test**: Run `ansible-doctor parse-collection my_namespace.my_collection/` → JSON output with collection metadata

**Acceptance Scenarios**:
1. **Given** a collection with galaxy.yml, **When** parsing, **Then** extract required fields (namespace, name, version, authors, dependencies); optional fields (tags, license, repository) deferred to v0.6.0
2. **Given** collection dependencies in galaxy.yml, **When** parsing, **Then** resolve and list dependent collections with version constraints
3. **Given** collection with multiple roles, **When** parsing, **Then** discover and list all roles with their paths

---

### US9 - Generate Collection Documentation (Priority: P1)

As a collection maintainer, I want to generate comprehensive collection documentation (see SC-003 for concrete definition) so that users understand the collection's purpose, roles, plugins, and usage.

**Independent Test**: Run `ansible-doctor generate-collection my_namespace.my_collection/` → README.md with collection overview, role index, plugin list

**Acceptance Scenarios**:
1. **Given** a parsed collection, **When** generating docs, **Then** create collection README with overview, installation, role index
2. **Given** collection with plugins, **When** generating docs, **Then** list plugins by type (modules, filters, inventory)
3. **Given** collection with example playbooks, **When** generating docs, **Then** include playbook examples with descriptions

---

### US10 - Cross-Role Dependency Analysis (Priority: P2)

As a collection maintainer, I want to visualize role dependencies within my collection so that I can document the relationship between roles and identify circular dependencies.

**Independent Test**: Run `ansible-doctor analyze-collection my_namespace.my_collection/ --show-dependencies` → Dependency graph showing role relationships

**Acceptance Scenarios**:
1. **Given** roles with dependencies in meta/main.yml, **When** analyzing, **Then** build dependency graph (role → dependent roles)
2. **Given** circular dependencies, **When** analyzing, **Then** detect and warn about circular references
3. **Given** dependency graph, **When** generating docs, **Then** include visual representation (Mermaid diagram, ASCII tree)

---

## Success Criteria

**SC-001**: Parse galaxy.yml and extract all required collection metadata fields (namespace, name, version, authors, dependencies); optional fields deferred to v0.6.0  
**SC-002**: Discover all roles within collection automatically  
**SC-003**: Generate collection-level README with role index and plugin list  
**SC-004**: Document collection dependencies with version constraints  
**SC-005**: Cross-role dependency analysis detects circular references  
**SC-006**: Collection documentation generation completes in <5s for typical collection (5 roles, 10 plugins, ~50 files total)  
**SC-007**: Reuse template system from v0.3.0 (no new template engine)  
**SC-008**: CLI commands: `collection parse`, `collection generate`, `collection analyze`

## Technical Constraints

**TC-001**: Must parse Ansible Galaxy collection format (galaxy.yml specification, schema version 1.0.0 for Ansible 2.9+)  
**TC-002**: Must discover roles, plugins, modules automatically from collection structure (no file exclusions; parse all Python files, let validation filter)  
**TC-003**: Must reuse TemplateEngine and renderers from Feature 002  
**TC-004**: Must support collections from ansible-galaxy, local filesystem, git repos  
**TC-005**: Must handle namespace/name format (e.g., community.general)

## Out of Scope

- Plugin source code parsing (only list plugins, no detailed parsing)
- Module documentation parsing (Ansible auto-generates this)
- Playbook execution or testing
- Collection publishing/uploading to Galaxy

## Clarifications

### Session 2025-11-20

- Q: Which optional galaxy.yml fields (tags, license, repository, etc.) should be documented? → A: Defer optional fields to v0.6.0 (only required fields in v0.5.0)
- Q: Which galaxy.yml schema version(s) to support? → A: 1.0.0 (Ansible 2.9+ standard), support latest versions in future releases
- Q: Which files to exclude from plugin discovery? → A: No exclusions (parse all Python files, let validation filter)
- Q: Role index layout format (table vs list)? → A: Let template decide (configurable via template)

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.4.0 (Role Parity) is COMPLETE and stable
2. ✅ Template system (Feature 002) has no pending breaking changes
3. ✅ Role documentation generation is production-ready
4. ✅ Performance targets met for role-level operations
5. ✅ No critical bugs in role parsing or generation

**Gate**: This feature CANNOT start until v0.4.0 is tagged and stable.
