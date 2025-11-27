# Feature Specification: Project Documentation

**Feature Branch**: `006-project-docs`  
**Created**: 2025-11-17  
**Milestone**: v0.7.0  
**Prerequisites**: v0.6.0 (i18n Support) COMPLETE ✅  
**Status**: Planned (Blocked until v0.6.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Extend ansible-doctor-enhanced to document complete Ansible projects, which include roles, collections, playbooks, inventory, and group_vars/host_vars. This is the highest abstraction level, providing project-wide architecture documentation.

## Output Naming & Slugs

Project output directories MUST use the `ansibleproject_{projectname}` slug convention to ensure a consistent, collision-free layout across languages and components. Slug generation rules follow rules from Collection: ASCII lowercase, whitespace replaced with `-`, preserve dots for hierarchy, length capped, and deterministic conflict resolution.

Example:
```
docs/lang/en/ansibleproject_myproject/README.md
docs/lang/en/ansibleproject_myproject/collections/collection_my_namespace.my_collection/README.md
docs/lang/en/ansibleproject_myproject/collections/collection_my_namespace.my_collection/role_my_namespace.webserver/README.md
```

CLI & Migration: Provide `--legacy-output` to write to old layout as requested; ensure PRs add migration notes and commit CHANGELOG guidance.

## What is an Ansible Project?

An Ansible Project is a complete automation codebase that typically includes:

**Project Structure**:
```
ansible-project/
├── ansible.cfg              # Ansible configuration
├── inventory/               # this folder can be customised by Ansible configuration 
│   ├── production.yml        # Production inventory
│   └── staging.yml           # Staging inventory
├── group_vars/              # This folder can be customised by Ansible configuration 
│   ├── all.yml               # Variables for all hosts
│   └── webservers.yml        # Group-specific variables
├── host_vars/              # This folder can be customised by Ansible configuration
│   └── server1.yml          # Host-specific variables
├── roles/                   # Local roles This folder can be customised by Ansible configuration
│   ├── webserver/
│   └── database/
├── collections/             # Collections directory This folder can be customised by Ansible configuration
│   └── requirements.yml     # Collection dependencies
├── playbooks/               # Playbooks
│   ├── site.yml            # Main playbook
│   ├── deploy.yml
│   └── rollback.yml
├── files/                   # Static files
├── templates/               # Jinja2 templates
├── README.md               # Project overview
├── requirements.lock.yml   # Role dependencies with locked versions (legacy)
└── requirements.yml        # Role dependencies (legacy)
```

## User Scenarios

### US14 - Parse Ansible Project Structure (Priority: P1) 🎯 MVP

As a project maintainer, I want to parse my complete Ansible project so that I can generate comprehensive project documentation that includes architecture, inventory, playbooks, and all components.

**Independent Test**: Run `ansible-doctor parse-project ./` → JSON output with project metadata, playbooks, roles, collections, inventory structure

**Acceptance Scenarios**:
1. **Given** a project with ansible.cfg, **When** parsing, **Then** extract project configuration (roles_path, collections_path, inventory)
2. **Given** project with inventory files, **When** parsing, **Then** parse inventory structure (groups, hosts, hierarchies)
3. **Given** project with playbooks, **When** parsing, **Then** extract playbook metadata (name, hosts, roles, tasks)
4. **Given** group_vars and host_vars, **When** parsing, **Then** extract variable definitions by group/host
5. **Given** project with local roles and collections, **When** parsing, **Then** discover and parse all roles and collections

### Edge Cases & Project Root Detection (Monorepo)

- Projects can exist inside monorepos or as nested folders. The project parser MUST document how it determines the project root.
- Detect the following heuristics in order: presence of `ansible.cfg` at or above target path, a `README.md` with `ansible` references, or explicit `--project-root` provided by the user.
- Add tests to validate behavior when multiple `ansible.cfg` exist in parent folders or monorepo layout.

---

### US15 - Generate Project Documentation (Priority: P1)

As a project maintainer, I want to generate project-level documentation so that new team members can understand the project architecture, playbook purposes, and inventory structure.

**Independent Test**: Run `ansible-doctor generate-project ./` → PROJECT_README.md with architecture overview, playbook index, inventory summary

**Acceptance Scenarios**:
1. **Given** a parsed project, **When** generating docs, **Then** create project README with architecture diagram, component index
2. **Given** multiple playbooks, **When** generating docs, **Then** document each playbook's purpose, target hosts, roles used
3. **Given** inventory structure, **When** generating docs, **Then** visualize group hierarchy and host assignments
4. **Given** group_vars/host_vars, **When** generating docs, **Then** document variable precedence and overrides

### Variable Precedence & Sensitive Data Handling

- The generator MUST capture variable precedence: `ansible.cfg` defaults → `group_vars` → `host_vars` → role defaults; document the precedence in the generated docs.
- Sensitive data (passwords, tokens, secrets, keys) MUST NOT be printed by default in generated docs. Provide a `--redact-sensitive` CLI flag (default true) to hide values with pattern matching (e.g., keys containing `password`, `secret`, `token`, `key`) or by whitelist/blacklist in configuration.
- Tests must confirm redaction behavior and allow analysis-only output when `--redact-sensitive=false` is given (for offline review).

---

### US16 - Playbook Task Flow Documentation (Priority: P2)

As a project maintainer, I want to document playbook task flows so that I can understand execution order and dependencies.

**Independent Test**: Run `ansible-doctor analyze-project ./ --playbook site.yml` → Task flow diagram showing execution order

**Acceptance Scenarios**:
1. **Given** a playbook with multiple plays, **When** analyzing, **Then** document play order and target hosts
2. **Given** plays using roles, **When** analyzing, **Then** expand roles to show included tasks
3. **Given** conditional tasks, **When** analyzing, **Then** document conditions and branching logic
4. **Given** task flow, **When** generating docs, **Then** include visual diagram (Mermaid flowchart)

---

### US17 - Project Architecture Visualization (Priority: P2)

As a project maintainer, I want to visualize project architecture so that stakeholders can understand component relationships and deployment structure.

**Independent Test**: Run `ansible-doctor visualize-project ./` → Architecture diagram showing roles, collections, playbooks, inventory

**Acceptance Scenarios**:
1. **Given** project components, **When** visualizing, **Then** generate architecture diagram (roles → playbooks → hosts)
2. **Given** collection dependencies, **When** visualizing, **Then** show external dependencies
3. **Given** inventory hierarchy, **When** visualizing, **Then** show group/host tree structure

---

### US18 - i18n Integration (Priority: P1)

As a project maintainer working with international teams, I want to generate project documentation in multiple languages so that all team members can read documentation in their preferred language.

**Independent Test**: Run `ansible-doctor generate-project ./ --languages en,fr,de` → Creates `docs/lang/en/project/`, `docs/lang/fr/project/`, `docs/lang/de/project/`

**Acceptance Scenarios**:
1. **Given** multi-language config with enabled languages [en, fr, de], **When** generating project docs, **Then** create `docs/lang/{code}/project/` structure for each enabled language
2. **Given** project with playbooks and roles, **When** generating multi-language docs, **Then** translate section headers (Overview, Playbooks, Roles, Inventory) using translation keys
3. **Given** project documentation template with `{{ t('project.title') }}`, **When** rendering, **Then** use language-specific translations from Feature 005 i18n system
4. **Given** `--languages fr` CLI flag, **When** generating project docs, **Then** generate French documentation only in `docs/lang/fr/project/`
5. **Given** missing translation for project-specific key, **When** rendering, **Then** fall back to English translation with warning

### Templates & i18n

- The project-level generator SHOULD reuse role-and-collection templates when applicable; when rendering project-level pages or aggregated content, translation keys should be looked up using the same i18n resolution rules as role/collection rendering (Feature 005 integration).
- Add tests to verify a project-level template can include role-specific templates (for example a list of role READMEs embedded in the project's Role Index) and that translation keys resolve correctly in all contexts.

## Notes

- NOTE: There is a repository feature numbering (directory) `006-project-docs`. If existing project documents (constitution/roadmap) use a different numbering convention, reconcile them as part of release planning; this spec follows the directory and branch naming in this repository.

---

## Success Criteria

**SC-001**: Parse complete Ansible project structure (ansible.cfg, inventory, playbooks, roles, collections)  
**SC-002**: Generate project-level README with architecture overview  
**SC-003**: Document all playbooks with purpose, hosts, roles, task count  
**SC-004**: Visualize inventory structure (groups, hosts, hierarchies)  
**SC-005**: Document variable precedence (ansible.cfg, group_vars, host_vars, role defaults)  
**SC-006**: Generate architecture diagrams (Mermaid or ASCII art)  
**SC-007**: Project documentation generation completes in <10s for typical project (5 playbooks, 10 roles, 50 hosts)  
**SC-008**: Reuse template system from v0.3.0 (no new template engine)  
**SC-009**: CLI commands: `parse-project`, `generate-project`, `analyze-project`, `visualize-project`  
**SC-010**: Generate project documentation in all enabled languages with translated section headers and labels (integrates Feature 005 i18n)

## Technical Constraints

**TC-001**: Must parse ansible.cfg to discover roles_path, collections_path, inventory  
**TC-002**: Must parse inventory files (YAML, INI formats)  
**TC-003**: Must parse playbooks without executing them (static analysis only)  
**TC-004**: Must handle complex inventory structures (nested groups, host patterns)  
**TC-005**: Must reuse TemplateEngine and renderers from Feature 002  
**TC-006**: Must support both legacy (requirements.yml) and modern (collections) dependency formats

## Out of Scope

- Playbook execution or testing
- Inventory management or modification
- Dynamic inventory plugin execution
- Ansible vault decryption
- Variable interpolation/evaluation (document as-is)
- Ansible version compatibility checking

## Prerequisites Validation

Before starting this feature, MUST verify:

1. ✅ v0.5.0 (Collection Documentation) is COMPLETE and stable
2. ✅ v0.6.0 (i18n Support) is COMPLETE and stable
3. ✅ Collection parsing works for collections within projects
4. ✅ Template system handles multi-level documentation (role → collection → project)
5. ✅ i18n system (Feature 005) works for role and collection documentation
6. ✅ Translation files exist for project-specific keys (project.*, playbook.*, inventory.*)
7. ✅ Performance is acceptable for collection-level operations
8. ✅ No critical bugs in collection or i18n documentation

**Gate**: This feature CANNOT start until v0.6.0 (i18n) is tagged and stable.

## v1.0.0 Readiness

Completing this feature (v0.7.0) represents the final major capability before v1.0.0. After this:

- **v0.8.0**: Hierarchical Context Detection + Advanced Template Customization
- **v0.9.0**: Stabilization, polish, performance tuning, bug fixes
- **v1.0.0**: Production release with stable API, comprehensive documentation, migration guides

The project scope (Role → Collection → Project) will be COMPLETE at v0.7.0. Feature 006 integrates with Feature 005 (i18n) to provide multi-language project documentation. Subsequent versions focus on UX enhancements and quality improvements.
