# Ansible Doctor Enhanced - Roadmap to v1.0.0

## Vision

Ansible Doctor Enhanced sera la solution de documentation complète pour Ansible, couvrant trois niveaux d'abstraction:

1. **Roles** (v0.2.0-v0.4.0): Documentation de rôles individuels
2. **Collections** (v0.5.0): Documentation de collections Ansible
3. **Projects** (v0.6.0): Documentation de projets complets

## État Actuel

| Feature | Version | Status | Tests | Coverage |
|---------|---------|--------|-------|----------|
| Role Parser | v0.2.0 ✅ | Complete | 262 | 84% |
| Documentation Generator | v0.3.0 🚧 | Phase 9 ✅, Phase 10 ✅ (MVP) | 498 | 81% |
| Role Parity | v0.4.0 ⏳ | Planned | - | - |
| Collection Docs | v0.5.0 ⏳ | Planned | - | - |
| Project Docs | v0.6.0 ⏳ | Planned | - | - |

**Dernière mise à jour**: 2025-11-19  
**Branche active**: `002-doc-generator`  
**Prochain milestone**: v0.3.0 - Phase 11 (HTML and RST renderers)

## Milestones Détaillés

### ✅ v0.2.0 - Role Parser (COMPLETE)

**Commit**: f2e3d16 (Tag: v0.2.0)  
**Date**: 2025-11-17  
**Branch**: `001-ansible-role-parser`

**Fonctionnalités**:
- Parsing de `meta/main.yml` (métadonnées de rôles)
- Parsing de `defaults/main.yml` et `vars/main.yml` (variables)
- Support des annotations `@var`, `@todo`, `@example`
- Extraction des tags de tâches
- CLI `parse` avec sortie JSON
- Support YAML complexe (dictionnaires, listes, multilignes)

**Métriques**:
- 262 tests (100% passing)
- 84% code coverage
- Performance: ~150ms par rôle

**Documentation**:
- README avec guide d'utilisation
- ANNOTATION_GUIDE pour syntaxe annotations
- CHANGELOG à jour

---

### 📋 v0.3.0 - Role Documentation Generator (SPECIFICATION COMPLETE)

**Branch**: `002-doc-generator`  
**Date début**: 2025-11-17  
**État**: Phase 9 ✅ (Foundation), Phase 10 ✅ (Markdown MVP)

**Spécification**:
- ✅ `specs/002-doc-generator/spec.md`: 3 user stories, 18 requirements
- ✅ `specs/002-doc-generator/plan.md`: Contexte technique, 3 phases
- ✅ `specs/002-doc-generator/research.md`: Analyse Jinja2, formats
- ✅ `specs/002-doc-generator/data-model.md`: TemplateContext, OutputFormat
- ✅ `specs/002-doc-generator/contracts/`: DocumentRenderer, TemplateLoader
- ✅ `specs/002-doc-generator/tasks.md`: 55 tâches (T201-T255)

**Fonctionnalités implémentées** (Phase 10 MVP):
- ✅ Génération de documentation en Markdown (HTML, RST en Phase 11)
- ✅ Système de templates Jinja2 avec héritage
- ✅ Templates embarqués (zero-config experience)
- ✅ Support de templates personnalisés (4 niveaux de découverte)
- ✅ CLI `generate` avec options de format
- ✅ Filtres Jinja2 personnalisés (markdown_escape, code_fence, format_priority, etc.)

**Objectifs techniques atteints**:
- ✅ +236 tests (262 → 498 tests)
- ✅ 81% code coverage (MVP quality validated)
- ✅ Performance: ~25ms pour le rendu (target <100ms exceeded by 75%)
- ✅ Phase 9 (T201-T215): Foundation complete
- ✅ Phase 10 (T216-T230): Markdown MVP complete

**Prochaine étape**: Phase 11 - HTML and RST renderers (T231-T255)

---

### ⏳ v0.4.0 - Role Documentation Parity (PLANNED)

**Branch**: `003-role-parity` (à créer)  
**Prerequisites**: v0.3.0 COMPLETE ✅  
**Spec**: `specs/003-role-parity/spec.md`

**Objectif**: Atteindre la parité complète avec ansible-doctor original pour les rôles.

**Fonctionnalités prévues**:
- Support du fichier de configuration `.ansibledoctor.yml`
- Mode watch (regénération automatique)
- Optimisations de performance (<500ms par rôle)
- Tests cross-platform (Windows, macOS, Linux)
- Stabilisation du système de templates
- Validation de qualité (markdownlint, htmllint, rst-lint)

**Critères de succès**:
- 100% parité avec ansible-doctor original
- Performance: <500ms (rôle typique), <2s (grand rôle)
- Tests passent sur Windows, macOS (x64/ARM), Linux (Ubuntu, RHEL)
- Guide de migration publié et validé
- 90%+ code coverage maintenu

**GATE**: Ce milestone DOIT être complet avant v0.5.0 (collections).

---

### ⏳ v0.5.0 - Collection Documentation (PLANNED) 🆕

**Branch**: `004-collection-support` (à créer)  
**Prerequisites**: v0.4.0 COMPLETE ✅  
**Spec**: `specs/004-collection-support/spec.md`

**Objectif**: **NOUVELLE FONCTIONNALITÉ** (au-delà d'ansible-doctor original) - Documenter les collections Ansible.

**Contexte**: Les collections Ansible (format introduit dans Ansible 2.9+) sont des bundles contenant rôles, plugins, modules, et playbooks. Ce milestone étend ansible-doctor-enhanced à un niveau d'abstraction supérieur.

**Fonctionnalités prévues**:
- Parsing de `galaxy.yml` (métadonnées de collection)
- Découverte automatique de tous les rôles dans la collection
- Génération de README collection avec index des rôles
- Documentation des plugins (modules, filters, inventory)
- Analyse de dépendances cross-rôle (détection de cycles)
- Support namespace/name format (ex: community.general)
- CLI: `parse-collection`, `generate-collection`, `analyze-collection`

**Critères de succès**:
- Parse galaxy.yml complet
- Génération de README collection avec index
- Visualisation de dépendances (Mermaid diagrams)
- Performance: <5s pour collection typique (5 rôles, 10 plugins)
- Réutilisation du système de templates v0.3.0

**GATE**: v0.4.0 DOIT être stable (template system sans breaking changes).

---

### ⏳ v0.6.0 - Project Documentation (PLANNED) 🆕

**Branch**: `005-project-docs` (à créer)  
**Prerequisites**: v0.5.0 COMPLETE ✅  
**Spec**: `specs/005-project-docs/spec.md`

**Objectif**: **NOUVELLE FONCTIONNALITÉ** (au-delà d'ansible-doctor original) - Documenter des projets Ansible complets.

**Contexte**: Un projet Ansible complet inclut rôles, collections, playbooks, inventory, group_vars/host_vars. C'est le niveau d'abstraction le plus élevé, fournissant une documentation d'architecture projet.

**Fonctionnalités prévues**:
- Parsing de `ansible.cfg` (configuration projet)
- Parsing d'inventory (YAML, INI) avec hiérarchie groupes/hosts
- Parsing de playbooks (métadonnées, flux de tâches)
- Documentation de group_vars/host_vars (précédence variables)
- Découverte de rôles et collections locaux
- Visualisation d'architecture projet
- Diagrammes de flux de tâches (Mermaid flowcharts)
- CLI: `parse-project`, `generate-project`, `analyze-project`, `visualize-project`

**Critères de succès**:
- Parse structure projet complète (ansible.cfg, inventory, playbooks, roles, collections)
- Génération de README projet avec overview architecture
- Documentation de tous les playbooks (purpose, hosts, roles, tasks)
- Visualisation d'inventaire (hierarchie groupes/hosts)
- Performance: <10s pour projet typique (5 playbooks, 10 rôles, 50 hosts)
- Réutilisation du système de templates v0.3.0

**GATE**: v0.5.0 DOIT être stable (collections documentées et testées).

**Impact**: Ce milestone complète la vision Role → Collection → Project. Après v0.6.0, le scope fonctionnel est COMPLET.

---

### 🎯 v1.0.0 - Production Release (TARGET)

**Prerequisites**: v0.6.0 COMPLETE ✅  
**Date cible**: TBD (estimation: ~40-55 jours développement)

**Objectif**: Release stable production-ready avec API/CLI garantie stable.

**Critères de succès**:
- Solution complète Role → Collection → Project
- API et CLI stables (SemVer garantis à partir de v1.0.0)
- 90%+ test coverage maintenu sur toute la codebase
- Templates production-ready (testés, linters passing)
- Documentation complète:
  - README avec exemples complets
  - Guide de migration depuis ansible-doctor original
  - Documentation d'architecture
  - Guide de contribution
- Performance validée en production
- Validation cross-platform complète

**Versions intermédiaires (v0.7.0-v0.9.0)**:
Ces versions se concentrent sur la stabilisation, polish, et corrections de bugs:
- Pas de nouvelles fonctionnalités majeures
- Optimisations de performance
- Amélioration de la qualité des templates
- Corrections de bugs remontés par les utilisateurs
- Polish de documentation
- Amélioration des messages d'erreur

**Post v1.0.0** (déférées):
- Interface web UI
- Intégration CI/CD (GitHub Actions, GitLab CI)
- Support de formats additionnels (AsciiDoc, DocBook)
- Plugin ecosystem

---

## Règles de Développement

### Priorité de Développement

1. **Pas de nouveau scope avant fondation** ⛔
   - Les fonctionnalités Collection/Project DOIVENT attendre que la documentation de rôle soit complète et stable

2. **Parité avant innovation** 🎯
   - Atteindre la parité avec ansible-doctor original AVANT d'ajouter Collection/Project

3. **Milestones incrémentaux** 📦
   - Chaque version mineure doit être indépendamment valuable et déployable

4. **Template system first** 🏗️
   - L'infrastructure de templates (Feature 002) est un prérequis pour toutes les fonctionnalités de documentation

### Gates de Développement

| Milestone | Gate | Rationale |
|-----------|------|-----------|
| v0.3.0 → v0.4.0 | Documentation de rôle fonctionnelle | Template system doit être testé en production |
| v0.4.0 → v0.5.0 | Parité avec ansible-doctor | Stabilité avant nouveaux features |
| v0.5.0 → v0.6.0 | Collection docs stable | Collections validées avant projets |
| v0.6.0 → v1.0.0 | Scope complet validé | Stabilisation et polish uniquement |

### Méthodologie

**speckit** est OBLIGATOIRE pour toute spécification:

1. **Créer le spec de feature** (`spec.md`)
   - User stories avec acceptance scenarios
   - Success criteria
   - Technical constraints

2. **Planification détaillée** (`plan.md`)
   - Technical context
   - Phases d'implémentation
   - Constitution compliance

3. **Recherche** (`research.md`)
   - Analyse des technologies
   - Design decisions
   - Performance benchmarks

4. **Modèle de données** (`data-model.md`)
   - Domain objects
   - Protocols/interfaces
   - Validation schemas

5. **Contrats** (`contracts/`)
   - Interface definitions
   - Testing contracts
   - Error handling

6. **Tâches** (`tasks.md`)
   - Granular tasks (T001-T999)
   - TDD approach (tests FIRST)
   - Test count targets

## Timeline Estimé

| Milestone | Estimation | État |
|-----------|-----------|------|
| v0.2.0 Role Parser | ✅ COMPLETE | - |
| v0.3.0 Doc Generator | 7-10 jours | 📋 Spec ready |
| v0.4.0 Role Parity | 3-5 jours | ⏳ Spec ready |
| v0.5.0 Collection Docs | 10-14 jours | ⏳ Spec ready |
| v0.6.0 Project Docs | 14-21 jours | ⏳ Spec ready |
| v0.7.0-v0.9.0 Stabilization | 5-10 jours | ⏳ Not planned |
| v1.0.0 Production Release | 3-5 jours | ⏳ Not planned |
| **TOTAL** | **40-55 jours** | - |

*Note*: Estimation basée sur développement TDD avec Feature 002 comme référence.

## Indicateurs de Succès

### Tests et Qualité

| Milestone | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| v0.2.0 | 262 | 84% | ✅ |
| v0.3.0 | 497 (+235) | 86% | Target |
| v0.4.0 | ~550 | 87% | Target |
| v0.5.0 | ~650 | 88% | Target |
| v0.6.0 | ~750 | 89% | Target |
| v1.0.0 | 800+ | 90%+ | Target |

### Performance

| Opération | v0.2.0 | v0.3.0 Target | v0.4.0 Target |
|-----------|--------|---------------|---------------|
| Parse rôle | ~150ms | ~150ms | <100ms |
| Generate docs | - | <100ms | <50ms |
| Parse+Generate | - | <250ms | <500ms (total) |
| Collection | - | - | <5s |
| Project | - | - | <10s |

## Références

- **Specs**: `specs/001-role-parser/` through `specs/005-project-docs/`
- **Constitution**: `.specify/memory/constitution.md` (Milestone Definitions)
- **README**: `README.md` (Feature overview et roadmap)
- **Changelog**: `CHANGELOG.md` (Version history)

---

**Dernière mise à jour**: 2025-11-17  
**Auteur**: Specify Agent  
**Méthodologie**: speckit  
**Version du document**: 1.0.0
