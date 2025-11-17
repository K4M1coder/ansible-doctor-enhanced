# Feature Specification: Project Documentation

**Feature Branch**: `005-project-docs`  
**Created**: 2025-11-17  
**Milestone**: v0.6.0  
**Prerequisites**: v0.5.0 (Collection Documentation) COMPLETE ✅  
**Status**: Planned (Blocked until v0.5.0)

## Objective

**NEW CAPABILITY** (not in original ansible-doctor)

Extend ansible-doctor-enhanced to document complete Ansible projects, which include roles, collections, playbooks, inventory, and group_vars/host_vars. This is the highest abstraction level, providing project-wide architecture documentation.

## What is an Ansible Project?

An Ansible Project is a complete automation codebase that typically includes:

**Project Structure**:
```
ansible-project/
├── ansible.cfg               # Ansible configuration
├── inventory/
│   ├── production.yml        # Production inventory
│   └── staging.yml           # Staging inventory
├── group_vars/
│   ├── all.yml              # Variables for all hosts
│   └── webservers.yml       # Group-specific variables
├── host_vars/
│   └── server1.yml          # Host-specific variables
├── roles/                   # Local roles
│   ├── webserver/
│   └── database/
├── collections/             # Collections directory
│   └── requirements.yml     # Collection dependencies
├── playbooks/               # Playbooks
│   ├── site.yml            # Main playbook
│   ├── deploy.yml
│   └── rollback.yml
├── files/                   # Static files
├── templates/               # Jinja2 templates
├── README.md               # Project overview
└── requirements.yml        # Role dependencies (legacy)
```

## User Scenarios

### US11 - Parse Ansible Project Structure (Priority: P1) 🎯 MVP

As a project maintainer, I want to parse my complete Ansible project so that I can generate comprehensive project documentation that includes architecture, inventory, playbooks, and all components.

**Independent Test**: Run `ansible-doctor parse-project ./` → JSON output with project metadata, playbooks, roles, collections, inventory structure

**Acceptance Scenarios**:
1. **Given** a project with ansible.cfg, **When** parsing, **Then** extract project configuration (roles_path, collections_path, inventory)
2. **Given** project with inventory files, **When** parsing, **Then** parse inventory structure (groups, hosts, hierarchies)
3. **Given** project with playbooks, **When** parsing, **Then** extract playbook metadata (name, hosts, roles, tasks)
4. **Given** group_vars and host_vars, **When** parsing, **Then** extract variable definitions by group/host
5. **Given** project with local roles and collections, **When** parsing, **Then** discover and parse all roles and collections

---

### US12 - Generate Project Documentation (Priority: P1)

As a project maintainer, I want to generate project-level documentation so that new team members can understand the project architecture, playbook purposes, and inventory structure.

**Independent Test**: Run `ansible-doctor generate-project ./` → PROJECT_README.md with architecture overview, playbook index, inventory summary

**Acceptance Scenarios**:
1. **Given** a parsed project, **When** generating docs, **Then** create project README with architecture diagram, component index
2. **Given** multiple playbooks, **When** generating docs, **Then** document each playbook's purpose, target hosts, roles used
3. **Given** inventory structure, **When** generating docs, **Then** visualize group hierarchy and host assignments
4. **Given** group_vars/host_vars, **When** generating docs, **Then** document variable precedence and overrides

---

### US13 - Playbook Task Flow Documentation (Priority: P2)

As a project maintainer, I want to document playbook task flows so that I can understand execution order and dependencies.

**Independent Test**: Run `ansible-doctor analyze-project ./ --playbook site.yml` → Task flow diagram showing execution order

**Acceptance Scenarios**:
1. **Given** a playbook with multiple plays, **When** analyzing, **Then** document play order and target hosts
2. **Given** plays using roles, **When** analyzing, **Then** expand roles to show included tasks
3. **Given** conditional tasks, **When** analyzing, **Then** document conditions and branching logic
4. **Given** task flow, **When** generating docs, **Then** include visual diagram (Mermaid flowchart)

---

### US14 - Project Architecture Visualization (Priority: P2)

As a project maintainer, I want to visualize project architecture so that stakeholders can understand component relationships and deployment structure.

**Independent Test**: Run `ansible-doctor visualize-project ./` → Architecture diagram showing roles, collections, playbooks, inventory

**Acceptance Scenarios**:
1. **Given** project components, **When** visualizing, **Then** generate architecture diagram (roles → playbooks → hosts)
2. **Given** collection dependencies, **When** visualizing, **Then** show external dependencies
3. **Given** inventory hierarchy, **When** visualizing, **Then** show group/host tree structure

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
2. ✅ Collection parsing works for collections within projects
3. ✅ Template system handles multi-level documentation (role → collection → project)
4. ✅ Performance is acceptable for collection-level operations
5. ✅ No critical bugs in collection documentation

**Gate**: This feature CANNOT start until v0.5.0 is tagged and stable.

## v1.0.0 Readiness

Completing this feature (v0.6.0) represents the final major capability before v1.0.0. After this:

- **v0.7.0-v0.9.0**: Stabilization, polish, performance tuning, bug fixes
- **v1.0.0**: Production release with stable API, comprehensive documentation, migration guides

The project scope (Role → Collection → Project) will be COMPLETE at v0.6.0. Subsequent versions before v1.0.0 focus on quality, not new features.
