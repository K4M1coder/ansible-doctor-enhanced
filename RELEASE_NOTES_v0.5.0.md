# Release Notes - ansible-doctor-enhanced v0.5.0

**Release Date**: November 21, 2025  
**Release Tag**: v0.5.0  
**Release Type**: MINOR (New Features, Backward Compatible)

---

## 🎉 What's New in v0.5.0

### Feature 004: Ansible Collection Documentation Support

This release introduces comprehensive support for documenting Ansible collections, expanding ansible-doctor-enhanced beyond single roles to full collection analysis and documentation generation.

---

## 🚀 New Features

### 1. Parse Collection Metadata (US8)

Extract and validate collection metadata from `galaxy.yml`:

```bash
python -m ansibledoctor collection parse my_namespace.my_collection --pretty
```

**Output**: JSON with collection FQCN, version, authors, roles, plugins, and dependencies

**Features**:
- ✅ Parse galaxy.yml with comprehensive validation
- ✅ Namespace format validation (lowercase alphanumeric)
- ✅ Semantic versioning validation
- ✅ Automatic role discovery in `roles/` directory
- ✅ Plugin discovery across all plugin types (modules, filters, lookups, tests, inventory, callbacks)
- ✅ Dependency extraction with version constraints

### 2. Generate Collection Documentation (US9)

Generate professional documentation in multiple formats:

```bash
python -m ansibledoctor collection generate my_namespace.my_collection \
  --output-dir docs/ \
  --format [markdown|html|rst]
```

**Output Formats**:
- **Markdown**: Clean, GitHub-compatible documentation
- **HTML**: Styled, responsive single-page documentation
- **RST**: Sphinx-compatible reStructuredText

**Documentation Includes**:
- ✅ Collection overview and metadata
- ✅ Installation instructions with ansible-galaxy commands
- ✅ Role catalog with FQCN references
- ✅ Plugin catalog grouped by type
- ✅ Dependency matrix with version constraints
- ✅ License and attribution
- ✅ Generator version and timestamp

### 3. Analyze Role Dependencies (US10)

Visualize and analyze role dependencies within collections:

```bash
python -m ansibledoctor collection analyze my_namespace.my_collection \
  --show-dependencies \
  --output-format [text|json|mermaid] \
  --check-circular
```

**Visualization Formats**:
- **ASCII Tree**: Hierarchical text representation
- **Mermaid**: Graph diagram syntax for documentation
- **JSON**: Machine-readable dependency graph

**Analysis Features**:
- ✅ Build dependency graphs from `meta/main.yml`
- ✅ Detect circular dependencies with warnings
- ✅ Topological sorting for dependency order
- ✅ Export to multiple formats
- ✅ Non-zero exit code for circular dependencies (CI/CD integration)

---

## 🏗️ New Architecture Components

### Models (Domain-Driven Design)

- **`GalaxyMetadata`**: Pydantic model for galaxy.yml schema
  - Immutable, validated metadata
  - FQCN property (namespace.name)
  - Version constraint parsing

- **`AnsibleCollection`**: Aggregate root for collections
  - Composition of metadata, roles, and plugins
  - Helper methods for listing and filtering
  - Self-dependency validation

- **`Plugin`**: Value object for plugin information
  - Type-safe plugin types (enum)
  - Immutable plugin data

- **`PluginCatalog`**: Repository pattern for plugin management
  - Group plugins by type
  - Count and list operations

- **`CollectionRole`**: Extended role model
  - Collection context (FQCN)
  - Full role name computation

### Parsers

- **`GalaxyMetadataParser`**: Parse and validate galaxy.yml
- **`CollectionStructureWalker`**: Discover roles and plugins
- **`PluginDiscovery`**: Recursive plugin discovery
- **`CollectionParser`**: Main orchestrator
- **`DependencyGraph`**: Build and analyze dependencies

### Generators

- **`CollectionDocumentationGenerator`**: Multi-format documentation
- **`CollectionTemplateContext`**: Template context builder
- **Templates**: Jinja2 templates for Markdown, HTML, RST

---

## 📊 Quality Metrics

### Test Coverage
- **Total Tests**: 847 passing (8 skipped)
- **Overall Coverage**: 83% (exceeds 80% target)
- **Critical Path Coverage**: 100% (collection_parser, collection_walker)
- **Integration Tests**: 32 end-to-end scenarios
- **Property Tests**: 18 hypothesis-based tests

### Code Quality
- **mypy --strict**: 0 errors (full type safety)
- **ruff linter**: 0 errors (all 242 issues fixed)
- **Docstrings**: 100% coverage on public APIs
- **Type hints**: 100% coverage on public APIs

### Performance
- **Parse Collection**: <2s (target: <5s) ✅ Exceeds target
- **Generate Docs**: <1s (target: <3s) ✅ Exceeds target
- **Memory Usage**: <50MB (target: <200MB) ✅ Efficient

---

## 📦 Demo Collection

A complete demo collection is included to showcase all features:

**Location**: `demo/demo_namespace.demo_collection/`

**Contents**:
- 3 roles with dependency chain (database → application → webserver)
- 5 modules (app_deploy, database_backup, health_check, nginx_config_test, ssl_cert_info)
- 3 filter plugins (formatting, text, validation)
- 3 example playbooks
- Dependencies on ansible.posix and community.general

**Generated Documentation**:
- `README.md` - Markdown format
- `README.html` - Styled HTML format
- `README.rst` - reStructuredText format

---

## 🔄 Migration Guide

### From v0.4.0 to v0.5.0

**No Breaking Changes** - This is a backward-compatible release.

**New CLI Commands** (additive):
```bash
# New collection commands (additive, no impact on existing role commands)
python -m ansibledoctor collection parse <path>
python -m ansibledoctor collection generate <path>
python -m ansibledoctor collection analyze <path>

# Existing role commands unchanged
python -m ansibledoctor role parse <path>
python -m ansibledoctor role generate <path>
```

**Configuration** (optional):
No configuration changes required. Collection commands work with default settings.

---

## 📚 Documentation Updates

### New Documentation
- `IMPLEMENTATION_COMPLETE.md` - Full implementation report
- `demo/DEMO-COLLECTION-RESULTS.md` - Demo outputs and examples
- Collection command documentation in README.md

### Updated Documentation
- `CHANGELOG.md` - Complete v0.5.0 changelog
- `README.md` - Collection examples and usage
- CLI help text for collection commands

---

## 🐛 Bug Fixes

No bug fixes in this release (new feature only).

---

## 🔧 Maintenance

### Dependencies
- No new dependencies added
- All existing dependencies compatible
- Python 3.11+ required (unchanged)

### Deprecated Features
- None

### Removed Features
- None

---

## 🎯 Known Limitations

### Deferred to v0.5.1+
- **CollectionRoleParser** (T132-T134): Full role parsing within collections uses simplified RoleInfo approach. Deep role documentation integration planned for v0.6.0.
- **Performance Optimization** (T205-T210): Current performance exceeds targets; advanced optimizations deferred.
- **Cross-Platform CI** (T231-T240): Local testing complete; comprehensive CI/CD enhancement planned.

### Future Enhancements
- **v0.6.0**: Project-level documentation (multiple collections)
- **v0.7.0**: Advanced template customization
- **v0.8.0**: API documentation generation

---

## 🙏 Acknowledgments

This release implements Feature 004 following the constitutional principles:
- **TDD**: 223 tests written before implementation
- **DDD**: Ubiquitous language (Collection, Plugin, Role, Catalog)
- **SemVer**: Proper MINOR version increment
- **Keep a Changelog**: Comprehensive changelog maintained
- **KISS**: Simple, maintainable architecture

---

## 📦 Installation

### PyPI (when published)
```bash
pip install ansibledoctor==0.5.0
```

### From Source
```bash
git clone https://github.com/yourusername/ansible-doctor-enhanced.git
cd ansible-doctor-enhanced
git checkout v0.5.0
poetry install
```

### Using Poetry
```bash
poetry add ansibledoctor@^0.5.0
```

---

## 🔗 Links

- **Repository**: https://github.com/yourusername/ansible-doctor-enhanced
- **Documentation**: See README.md and docs/ folder
- **Issues**: https://github.com/yourusername/ansible-doctor-enhanced/issues
- **Changelog**: See CHANGELOG.md
- **Demo**: See demo/demo_namespace.demo_collection/

---

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md#050---2025-11-21) for complete details.

---

## 🎉 Try It Now!

```bash
# Parse a collection
python -m ansibledoctor collection parse demo/demo_namespace.demo_collection --pretty

# Generate documentation
python -m ansibledoctor collection generate demo/demo_namespace.demo_collection \
  --output-dir docs/ \
  --format markdown

# Analyze dependencies
python -m ansibledoctor collection analyze demo/demo_namespace.demo_collection \
  --show-dependencies \
  --output-format mermaid
```

Enjoy ansible-doctor-enhanced v0.5.0! 🎊

---

*Released with ❤️ by the ansible-doctor-enhanced team*
