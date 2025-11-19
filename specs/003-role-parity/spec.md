# Feature Specification: ansible-doctor Parity - Config & Watch Mode

**Feature Branch**: `003-role-parity`  
**Created**: 2025-11-19  
**Status**: In Progress  
**Milestone**: v0.4.0  
**Prerequisites**: v0.3.0 (Documentation Generator) COMPLETE  
**Input**: Complete ansible-doctor parity: config file support and watch mode

## Objective

Complete feature parity with original ansible-doctor for role documentation by implementing the two missing critical features: **configuration file support** and **watch mode**. This achieves 100% role-level parity before moving to collections (v0.5.0) or projects (v0.6.0).

**Note**: Performance optimization and cross-platform validation have been deferred to dedicated features per project roadmap reorganization.

## Scope

**In Scope**:
- Configuration file support (`.ansibledoctor.yml` or `.ansibledoctor.yaml`)
- Watch mode with auto-regeneration on file changes
- Backward compatibility with original ansible-doctor config format
- Migration guide from original ansible-doctor

**Out of Scope** (Deferred):
- Performance optimization (<500ms target) → Future feature
- Cross-platform CI/CD (macOS, Linux) → Future feature  
- Collection documentation → v0.5.0
- Project documentation → v0.6.0

## User Scenarios & Testing

### User Story 1 - Configuration File Support (Priority: P1)

As a role maintainer, I want to store documentation settings in a `.ansibledoctor.yml` file so I don't have to pass the same CLI flags repeatedly.

**Why this priority**: Essential for team workflows and CI/CD pipelines. Original ansible-doctor users expect this feature. Blocking adoption.

**Independent Test**: Create `.ansibledoctor.yml` in role root, run `ansible-doctor generate .` without flags, verify settings applied from config file.

**Acceptance Scenarios**:

1. **Given** a `.ansibledoctor.yml` with `output_format: html` exists in role root, **When** I run `ansible-doctor generate .`, **Then** HTML documentation is generated without specifying `--format html`

2. **Given** a `.ansibledoctor.yml` with `output: docs/README.md` exists, **When** I run `ansible-doctor generate .`, **Then** documentation is written to `docs/README.md` without specifying `--output`

3. **Given** both `.ansibledoctor.yml` config and CLI flags are provided, **When** I run `ansible-doctor generate . --format rst`, **Then** CLI flags override config file (RST generated, not HTML from config)

4. **Given** an invalid `.ansibledoctor.yml` with syntax errors, **When** I run `ansible-doctor generate .`, **Then** a clear error message is shown with file location and line number

---

### User Story 2 - Watch Mode Auto-Regeneration (Priority: P2)

As a role developer, I want documentation to auto-regenerate when I modify role files so I can preview changes in real-time without manual commands.

**Why this priority**: Improves developer experience during documentation authoring. Common workflow in modern tools (webpack watch, sphinx-autobuild). Not blocking for CI/CD but valuable for local development.

**Independent Test**: Run `ansible-doctor watch /role`, modify `defaults/main.yml`, verify docs regenerate automatically within 2 seconds.

**Acceptance Scenarios**:

1. **Given** watch mode is running on a role directory, **When** I modify `defaults/main.yml` and save, **Then** documentation regenerates automatically within 2 seconds

2. **Given** watch mode is running, **When** I modify `meta/main.yml`, **Then** documentation regenerates and metadata section updates

3. **Given** watch mode is running, **When** I create a new file `tasks/database.yml`, **Then** documentation regenerates and includes new task tags

4. **Given** watch mode is running with errors in role files, **When** regeneration fails, **Then** error is displayed in terminal but watch continues (doesn't crash)

5. **Given** watch mode is running, **When** I press `Ctrl+C`, **Then** watch mode exits gracefully with cleanup message

---

### User Story 3 - Config File Discovery & Validation (Priority: P3)

As a role maintainer, I want ansible-doctor to discover config files in parent directories (like Git does) and validate my config syntax so I catch errors early.

**Why this priority**: Nice-to-have for monorepo setups. Improves UX but not essential for basic functionality.

**Independent Test**: Place `.ansibledoctor.yml` in parent directory, run command in role subdirectory, verify config is discovered.

**Acceptance Scenarios**:

1. **Given** `.ansibledoctor.yml` exists in parent directory, **When** I run `ansible-doctor generate ./roles/web-server`, **Then** config from parent directory is used

2. **Given** `.ansibledoctor.yml` exists in both parent and role directory, **When** I run `ansible-doctor generate .`, **Then** role-specific config takes precedence (nearest file wins)

3. **Given** I run `ansible-doctor config validate`, **When** config file has schema errors, **Then** validation errors are displayed with field names and expected types

4. **Given** I run `ansible-doctor config show`, **When** config file exists, **Then** effective configuration is displayed (merged defaults + file + CLI)

---

## Edge Cases

- What happens when `.ansibledoctor.yml` contains unsupported keys? → Warning logged, unsupported keys ignored
- What happens when watch mode detects 100+ file changes in 1 second? → Debounce to single regeneration after 500ms quiet period
- What happens when config file has recursive template includes? → Validation error with cycle detection
- What happens when watch mode runs out of file handles (OS limit)? → Graceful error with recovery steps
- What happens when config specifies non-existent template file? → Clear error before watch starts, not on first regeneration

## Requirements

### Functional Requirements

**Configuration File Support (US1):**

- **FR-001**: System MUST support `.ansibledoctor.yml` and `.ansibledoctor.yaml` file formats (YAML 1.2)
- **FR-002**: System MUST discover config files in current directory, then parent directories up to filesystem root
- **FR-003**: System MUST apply config priority: CLI flags > nearest config file > default values
- **FR-004**: System MUST validate config schema on load with Pydantic models
- **FR-005**: System MUST support these config keys matching original ansible-doctor:
  - `output` (str): Output file path
  - `output_format` (str): markdown | html | rst
  - `template` (str): Custom template path
  - `template_dir` (str): Custom template directory
  - `recursive` (bool): Enable recursive role discovery
  - `output_dir` (str): Output directory for recursive mode
  - `exclude_patterns` (list[str]): Glob patterns to exclude from parsing

**Watch Mode (US2):**

- **FR-006**: System MUST provide `ansible-doctor watch <role-path>` command
- **FR-007**: System MUST watch these paths for changes: `meta/`, `defaults/`, `vars/`, `tasks/`, `handlers/`, `.ansibledoctor.yml`
- **FR-008**: System MUST debounce file changes (500ms quiet period before regeneration)
- **FR-009**: System MUST display generation status (timestamp, duration, success/failure)
- **FR-010**: System MUST continue watching after generation errors (resilient)
- **FR-011**: System MUST support graceful shutdown on SIGINT/SIGTERM
- **FR-012**: System MUST use platform-specific file watching (watchdog library)  
- **FR-003**: Users MUST be able to [key interaction, e.g., "reset their password"]
- **FR-004**: System MUST [data requirement, e.g., "persist user preferences"]
- **FR-005**: System MUST [behavior, e.g., "log all security events"]

*Example of marking unclear requirements:*

- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*

- **[Entity 1]**: [What it represents, key attributes without implementation]
- **[Entity 2]**: [What it represents, relationships to other entities]

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: [Measurable metric, e.g., "Users can complete account creation in under 2 minutes"]
- **SC-002**: [Measurable metric, e.g., "System handles 1000 concurrent users without degradation"]
- **SC-003**: [User satisfaction metric, e.g., "90% of users successfully complete primary task on first attempt"]
- **SC-004**: [Business metric, e.g., "Reduce support tickets related to [X] by 50%"]
