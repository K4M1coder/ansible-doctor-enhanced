# Real-World Use Case: Nginx Role Documentation

## Scenario

You're maintaining an Nginx role for your team. You want to:
1. ✅ **Generate documentation automatically** (works today in v0.3.0)
2. 🔜 **Store settings in a config file** (Feature 003 - US1)
3. 🔜 **Auto-regenerate docs when files change** (Feature 003 - US2)

---

## What Works TODAY (v0.3.0)

### Current Workflow

```bash
# Generate HTML documentation (manual command)
poetry run python -m ansibledoctor generate test-role --format html --output test-role/docs/nginx-role.html
```

**Output**:
```
✓ Documentation generated: test-role\docs\nginx-role.html (13KB)
✓ Parsed: 10 variables, 3 TODOs, 8 task tags
✓ Format: HTML with embedded CSS
✓ Duration: ~100ms
```

**Generated Documentation Includes**:
- ✅ Role metadata (author, license, platforms, dependencies)
- ✅ 10 variables with descriptions from `@meta` annotations
- ✅ 3 TODO items with priorities
- ✅ 8 task tags (installation, configuration, ssl, loadbalancer, service, firewall, security)
- ✅ Dependency tree (geerlingguy.certbot, common-firewall)

**Problem**: You have to type the same command every time with all the flags.

---

## What Feature 003 Will Add

### Use Case 1: Configuration File (US1) 🔜

**Problem**: Typing `--format html --output test-role/docs/nginx-role.html` every time is tedious.

**Solution**: Create `.ansibledoctor.yml` in role root:

```yaml
# .ansibledoctor.yml (already created in test-role/)
output_format: html
output: docs/nginx-role.html
exclude_patterns:
  - "*.pyc"
  - "__pycache__"
  - ".git"
```

**New Workflow** (after Feature 003):

```bash
# Simple command - settings loaded from config file!
ansible-doctor generate test-role

# Config file automatically discovered and used
# No need for --format or --output flags
```

**Validation**:

```bash
# Check if config is valid
ansible-doctor config validate
✓ Config valid: test-role/.ansibledoctor.yml

# Show effective configuration
ansible-doctor config show
Config file: test-role/.ansibledoctor.yml
Effective configuration:
  output_format: html
  output: docs/nginx-role.html
  recursive: false
  exclude_patterns: [*.pyc, __pycache__, .git]
```

**Team Benefits**:
- ✅ Consistent documentation format across team
- ✅ Config committed to Git → everyone uses same settings
- ✅ CLI flags still work for overrides
- ✅ Works in CI/CD pipelines (just `ansible-doctor generate .`)

---

### Use Case 2: Watch Mode (US2) 🔜

**Problem**: You're writing documentation annotations in `defaults/main.yml`. You save, run command, check HTML, edit again, run command again... tedious!

**Solution**: Watch mode with auto-regeneration

**New Workflow** (after Feature 003):

```bash
# Start watch mode (reads config from .ansibledoctor.yml)
ansible-doctor watch test-role

# Output:
Watching test-role for changes... Press Ctrl+C to stop
Config: test-role/.ansibledoctor.yml (html → docs/nginx-role.html)

[04:45:23] ✓ Initial generation complete (142ms)
[04:45:45] File changed: defaults/main.yml
[04:45:45] ✓ Regenerated documentation (98ms)
[04:46:12] File changed: tasks/main.yml
[04:46:12] ✓ Regenerated documentation (103ms)
```

**What It Monitors**:
- `meta/main.yml` - metadata changes
- `defaults/main.yml` - variable changes
- `vars/main.yml` - variable changes
- `tasks/*.yml` - task tag changes
- `.ansibledoctor.yml` - config changes

**Developer Experience**:
- ✅ Edit file in VSCode
- ✅ Save (Ctrl+S)
- ✅ **Docs auto-regenerate in <2 seconds**
- ✅ Refresh browser to see changes
- ✅ No manual commands needed

**Resilient**:
- If generation fails (parse error), watch continues
- Error displayed in terminal
- Fix the error, save again → regenerates successfully

---

### Use Case 3: Monorepo with Parent Config (US3) 🔜

**Problem**: You have 20 roles in `roles/` directory. Each needs same doc settings.

**Solution**: Config discovery in parent directories

**Directory Structure**:

```
my-ansible-project/
├── .ansibledoctor.yml          ← Parent config (all roles use this)
├── roles/
│   ├── nginx/
│   │   ├── meta/
│   │   ├── defaults/
│   │   └── tasks/
│   ├── mysql/
│   │   ├── .ansibledoctor.yml  ← Override for this role only
│   │   ├── meta/
│   │   └── defaults/
│   └── redis/
│       ├── meta/
│       └── defaults/
```

**Parent Config** (`my-ansible-project/.ansibledoctor.yml`):

```yaml
# Default settings for all roles
output_format: html
output: docs/role.html
exclude_patterns: ["test_*", "*.pyc"]
```

**Role-Specific Override** (`roles/mysql/.ansibledoctor.yml`):

```yaml
# MySQL role needs RST for Sphinx docs
output_format: rst
output: docs/mysql.rst
```

**Behavior**:

```bash
# Nginx role: uses parent config (html → docs/role.html)
cd roles/nginx
ansible-doctor generate .
# Config discovered: ../../.ansibledoctor.yml

# MySQL role: uses role-specific config (rst → docs/mysql.rst)
cd roles/mysql
ansible-doctor generate .
# Config discovered: .ansibledoctor.yml (overrides parent)

# Redis role: uses parent config (html → docs/role.html)
cd roles/redis
ansible-doctor generate .
# Config discovered: ../../.ansibledoctor.yml
```

**Batch Generation** (already works in v0.3.0!):

```bash
# Generate docs for all roles with parent config
cd my-ansible-project
ansible-doctor generate roles --recursive --output-dir docs/roles
# Each role inherits .ansibledoctor.yml from parent
```

---

## Real-World Timeline

### Today (v0.3.0) ✅

```bash
# Works now!
poetry run python -m ansibledoctor generate test-role --format html --output test-role/docs/nginx-role.html
```

**What you get**:
- ✅ HTML/Markdown/RST documentation
- ✅ Batch generation with `--recursive`
- ✅ Template management (`templates list/show/validate`)
- ✅ 593 tests, 82% coverage

**What's missing**:
- ❌ Config file support (need to type flags every time)
- ❌ Watch mode (manual regeneration)
- ❌ Config validation CLI

### After Feature 003 (v0.4.0) 🔜

**Estimated**: 4 days (~30 hours)

```bash
# Simplest workflow
ansible-doctor generate .              # Config from .ansibledoctor.yml
ansible-doctor watch .                 # Auto-regenerate on changes
ansible-doctor config validate         # Check config syntax
ansible-doctor config show             # Show effective settings
```

**Complete ansible-doctor parity**:
- ✅ All original features
- ✅ Config file support
- ✅ Watch mode
- ✅ Enhanced with HTML/RST formats
- ✅ Better error messages
- ✅ 100% type-safe with Pydantic

---

## Try It Now

The test role is ready at `test-role/`:

```bash
# 1. Generate docs with current v0.3.0
poetry run python -m ansibledoctor generate test-role --format html --output test-role/docs/nginx-role.html

# 2. Open in browser
start test-role/docs/nginx-role.html  # Windows
# or: open test-role/docs/nginx-role.html  # macOS
# or: xdg-open test-role/docs/nginx-role.html  # Linux

# 3. Try Markdown format
poetry run python -m ansibledoctor generate test-role --format markdown --output test-role/README.md

# 4. Try RST format for Sphinx
poetry run python -m ansibledoctor generate test-role --format rst --output test-role/docs/role.rst

# 5. Validate template
poetry run python -m ansibledoctor templates show html > custom.j2
poetry run python -m ansibledoctor templates validate custom.j2
```

---

## Feature 005: Internationalization (i18n) Support ✅

**Status**: Complete (v0.5.1)

### Use Case: Multi-Language Documentation

**Problem**: Your team spans multiple countries. You need documentation in English, French, and German.

**Solution**: Generate multi-language documentation with translations:

```bash
# Generate docs in multiple languages
poetry run ansible-doctor-enhanced project generate ./demo/project_demo_namespace.demo_project --languages en,fr,de

# Output structure:
# docs/lang/
# ├── en/README.md
# ├── fr/README.md
# └── de/README.md
```

### Custom Translations

Create translation overrides in your project:

```
.ansibledoctor/
└── translations/
    ├── en.yml
    ├── fr.yml
    └── de.yml
```

Example translation file (`fr.yml`):

```yaml
overview:
  title: "Aperçu du Projet"
  description: "Description du projet"
roles:
  title: "Rôles"
collections:
  title: "Collections"
```

### Demo

Try the included demo project with i18n:

```bash
# Navigate to demo project
cd demo/project_demo_namespace.demo_project

# Generate multi-language docs
poetry run ansible-doctor-enhanced project generate ./ --languages en,fr,de --output-dir docs/lang

# Check generated files
ls docs/lang/*/
```

**Supported Languages**: English (en), French (fr), German (de)

---

## Feature 003 Implementation Ready

**Spec**: `specs/003-role-parity/spec.md` ✅  
**Plan**: `specs/003-role-parity/plan.md` ✅  
**Tasks**: `specs/003-role-parity/tasks.md` ✅ (37 tasks)

Ready to start implementing? Just say "pret" and I'll begin Phase 1 (Setup)! 🚀
