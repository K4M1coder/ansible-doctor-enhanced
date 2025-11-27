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
| i18n Support | v0.6.0 📋 | Spec Complete | - | - |
| Project Docs | v0.7.0 📋 | Spec Complete | - | - |
| Hierarchical Context | v0.8.0 📋 | Spec Complete | - | - |
| Template Customization | v0.8.0 📋 | Spec Complete | - | - |

**Dernière mise à jour**: 2025-11-26  
**Branche active**: `002-doc-generator`  
**Prochain milestone**: v0.3.0 - Phase 11 (HTML and RST renderers)  
**Nouvelles spécifications**: Features 005-008 (i18n, Project, Context, Theming)

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

### 📋 v0.6.0 - Internationalization (i18n) Support (SPEC COMPLETE) 🆕

**Branch**: `005-i18n-support` (à créer)  
**Prerequisites**: v0.5.0 COMPLETE ✅  
**Spec**: `specs/005-i18n-support/spec.md`  
**Date spec**: 2025-11-26

**Objectif**: **NOUVELLE FONCTIONNALITÉ** (au-delà d'ansible-doctor original) - Documentation multi-langue.

**Contexte**: Support de plusieurs langues (Anglais, Français, Allemand par défaut, extensible) avec système de traduction, marqueurs i18n dans les templates, et génération parallèle multi-langue.

**Fonctionnalités prévues**:
- Configuration des langues dans `.ansibledoctor.yml` (default, enabled, fallback)
- Fichiers de traduction YAML par langue (translations/en.yml, fr.yml, de.yml)
- Filtre Jinja2 `{{ t('key', var=value) }}` pour traductions
- Structure de sortie multi-langue: `docs/lang/{code}/roles/`, `docs/lang/{code}/collections/`
- Support ISO 639-1 language codes
- Chaîne de fallback pour traductions manquantes
- Génération de documentation dans toutes les langues activées
- CLI: `--languages en,fr,de` pour override config

**User Stories**:
- US11: Configuration des langues dans `.ansibledoctor.yml`
- US12: Marqueurs de traduction dans les templates (`{{ t('key') }}`)
- US13: Génération multi-langue parallèle

**Critères de succès**:
- Parse configuration langues (default, enabled, fallback)
- Chargement de fichiers de traduction YAML (embedded + custom)
- Filtre `t()` avec lookup clé, substitution variables, pluriels
- Génération multi-langue avec structure `docs/lang/{code}/`
- Performance: <100ms overhead par langue additionnelle
- Réutilisation TemplateEngine Feature 002

**GATE**: v0.5.0 DOIT être stable (collections documentées). i18n est fondamental pour Features 006-008.

---

### 📋 v0.7.0 - Project Documentation (SPEC COMPLETE) 🆕

**Branch**: `006-project-docs` (à créer)  
**Prerequisites**: v0.6.0 COMPLETE ✅  
**Spec**: `specs/006-project-docs/spec.md`  
**Date spec**: 2025-11-17 (Updated: 2025-11-26)

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
- **Intégration i18n**: Documentation projet multi-langue (Feature 005)
- CLI: `parse-project`, `generate-project`, `analyze-project`, `visualize-project`

**User Stories**:
- US14: Parse Ansible project structure
- US15: Generate project documentation
- US16: Playbook task flow documentation
- US17: Project architecture visualization
- US18: i18n integration (multi-language project docs)

**Critères de succès**:
- Parse structure projet complète (ansible.cfg, inventory, playbooks, roles, collections)
- Génération de README projet avec overview architecture
- Documentation de tous les playbooks (purpose, hosts, roles, tasks)
- Visualisation d'inventaire (hierarchie groupes/hosts)
- **Génération multi-langue** avec en-têtes et labels traduits (Feature 005)
- Performance: <10s pour projet typique (5 playbooks, 10 rôles, 50 hosts)
- Réutilisation du système de templates v0.3.0

**GATE**: v0.6.0 DOIT être stable (i18n testé et validé).

**Impact**: Ce milestone complète la capacité de documentation projet (niveau abstraction le plus élevé).

---

### 📋 v0.8.0 - Hierarchical Context Detection (SPEC COMPLETE) 🆕

**Branch**: `007-hierarchical-context` (à créer)  
**Prerequisites**: v0.7.0 COMPLETE ✅  
**Spec**: `specs/007-hierarchical-context/spec.md`  
**Date spec**: 2025-11-26

**Objectif**: **NOUVELLE FONCTIONNALITÉ** - Détection automatique du contexte parent et navigation hiérarchique.

**Contexte**: Détection automatique des relations parent (role → collection → project) en analysant la structure de répertoires. Génération de breadcrumbs et vue d'ensemble contextuelle montrant les composants liés.

**Fonctionnalités prévues**:
- Détection automatique du parent collection (galaxy.yml) ou projet (ansible.cfg)
- Génération de breadcrumb navigation (Projet > Collection > Rôle)
- Section overview contextuelle listant les composants siblings
- Liens relatifs entre composants (structure `docs/lang/{code}/`)
- Flag `--no-parent` pour désactiver la détection
- Configuration `context.detect_parent: false` dans `.ansibledoctor.yml`

**User Stories**:
- US19: Auto-détection du contexte parent
- US20: Génération de breadcrumb navigation
- US21: Section overview contextuelle (siblings)
- US22: Mode standalone (`--no-parent`)

**Critères de succès**:
- Détection collection parent (galaxy.yml, max 3 niveaux)
- Détection projet parent (ansible.cfg/playbooks/, max 3 niveaux)
- Breadcrumbs avec liens cliquables vers documentation parent
- Listing siblings avec liens relatifs
- Performance: <500ms overhead pour détection
- Cache des résultats de détection par session
- **Support multi-langue**: Breadcrumbs et labels traduits (Feature 005)

**GATE**: v0.7.0 DOIT être stable (project docs validés). Feature 005 requise pour i18n des breadcrumbs.

---

### 📋 v0.8.0 - Advanced Template Customization & Theming (SPEC COMPLETE) 🆕

**Branch**: `008-template-customization` (à créer)  
**Prerequisites**: v0.2.0 COMPLETE ✅  
**Spec**: `specs/008-template-customization/spec.md`  
**Date spec**: 2025-11-26  
**Note**: Peut être développée en parallèle avec Feature 007

**Objectif**: **NOUVELLE FONCTIONNALITÉ** - Système de thèmes avec CSS personnalisable et variantes de design.

**Contexte**: Système de thèmes avancé avec variantes de design (minimal, detailed, modern), templates cascading (role → collection → projet → embedded), CSS personnalisable, et switch dark/light mode.

**Fonctionnalités prévues**:
- Configuration thème dans `.ansibledoctor.yml` (name, variant, color_scheme)
- 3 variantes built-in: minimal (compact), detailed (verbose), modern (UI enrichie)
- Découverte templates 4 niveaux: role → collection → project → embedded
- CSS customization: `css_url` (externe) ou `css_inline` (embedded)
- Dark/light mode: `color_scheme: auto/light/dark` avec media queries CSS
- Toggle dark/light avec JavaScript + localStorage persistence
- Héritage de templates Jinja2 (`{% extends %}`)
- CSS variables pour couleurs (20+ variables)

**User Stories**:
- US23: Configuration thème dans `.ansibledoctor.yml`
- US24: Override templates cascading (4 niveaux)
- US25: Variantes design built-in (minimal, detailed, modern)
- US26: Customisation CSS (url/inline)
- US27: Switch dark/light mode (auto/manual)
- US28: Héritage de templates Jinja2

**Critères de succès**:
- Chargement config thème (name, variant, color_scheme)
- Template discovery 4 niveaux avec priorité
- 3 variantes par format (minimal, detailed, modern)
- Injection CSS dans HTML (url + inline)
- Dark mode CSS media query + toggle JavaScript
- Backward compatibility (templates existants fonctionnent)
- Performance: caching template discovery

**GATE**: v0.2.0 (Template System) COMPLET. Feature 005 (i18n) recommandée pour labels thème.

**Impact**: Avec Features 007-008, v0.8.0 complète l'UX avancée (navigation, personnalisation).

---

### 🎯 v1.0.0 - Production Release (TARGET)

**Prerequisites**: v0.8.0 COMPLETE ✅  
**Date cible**: TBD (estimation: ~60-80 jours développement)

**Objectif**: Release stable production-ready avec API/CLI garantie stable.

**Critères de succès**:
- **Solution complète** Role → Collection → Project
- **Multi-langue**: Documentation EN/FR/DE par défaut (Feature 005)
- **Navigation contextuelle**: Breadcrumbs et hiérarchie (Feature 007)
- **Thèmes personnalisables**: Variantes + dark/light mode (Feature 008)
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

**Versions intermédiaires (v0.9.0)**:
Cette version se concentre sur la stabilisation, polish, et corrections de bugs:
- Pas de nouvelles fonctionnalités majeures
- Optimisations de performance
- Amélioration de la qualité des templates
- Corrections de bugs remontés par les utilisateurs
- Polish de documentation
- Amélioration des messages d'erreur
- Tests de charge et validation production

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
|-----------|------|-----------|---|
| v0.3.0 → v0.4.0 | Documentation de rôle fonctionnelle | Template system doit être testé en production |
| v0.4.0 → v0.5.0 | Parité avec ansible-doctor | Stabilité avant nouveaux features |
| v0.5.0 → v0.6.0 | Collection docs stable | Collections validées avant i18n |
| v0.6.0 → v0.7.0 | i18n system stable | Multi-langue validé avant project docs |
| v0.7.0 → v0.8.0 | Project docs stable | Projects validés avant context/theming |
| v0.8.0 → v0.9.0 | Features complètes validées | Stabilisation et polish uniquement |
| v0.9.0 → v1.0.0 | Production-ready quality | API/CLI stable, docs complète |

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
| v0.4.0 Role Parity | 3-5 jours | 📋 Spec ready |
| v0.5.0 Collection Docs | 10-14 jours | 📋 Spec ready |
| v0.6.0 i18n Support | 7-10 jours | 📋 Spec ready |
| v0.7.0 Project Docs | 14-21 jours | 📋 Spec ready |
| v0.8.0 Context + Theming | 10-14 jours | 📋 Spec ready |
| v0.9.0 Stabilization | 7-10 jours | ⏳ Not planned |
| v1.0.0 Production Release | 3-5 jours | ⏳ Not planned |
| **TOTAL** | **60-80 jours** | - |

*Note*: Estimation basée sur développement TDD avec Feature 002 comme référence.

## Indicateurs de Succès

### Tests et Qualité

| Milestone | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| v0.2.0 | 262 | 84% | ✅ |
| v0.3.0 | 497 (+235) | 86% | Target |
| v0.4.0 | ~550 | 87% | Target |
| v0.5.0 | ~650 | 88% | Target |
| v0.6.0 | ~720 | 88% | Target |
| v0.7.0 | ~790 | 89% | Target |
| v0.8.0 | ~860 | 89% | Target |
| v0.9.0 | ~900 | 90% | Target |
| v1.0.0 | 950+ | 90%+ | Target |

### Performance

| Opération | v0.2.0 | v0.3.0 Target | v0.4.0 Target | v0.6.0 Target | v0.7.0 Target | v0.8.0 Target |
|-----------|--------|---------------|---------------|---------------|---------------|---------------|
| Parse rôle | ~150ms | ~150ms | <100ms | <100ms | <100ms | <100ms |
| Generate docs | - | <100ms | <50ms | <50ms | <50ms | <50ms |
| Generate multi-lang | - | - | - | +100ms/lang | +100ms/lang | +100ms/lang |
| Parse+Generate | - | <250ms | <500ms | <650ms (3 langs) | <650ms | <650ms |
| Parent detection | - | - | - | - | - | <500ms |
| Collection | - | - | <5s | <6s (3 langs) | <6s | <6s |
| Project | - | - | - | - | <10s | <12s (3 langs) |

## Références

- **Specs**: `specs/001-role-parser/` through `specs/008-template-customization/`
- **Constitution**: `.specify/memory/constitution.md` (Milestone Definitions)
- **README**: `README.md` (Feature overview et roadmap)
- **Changelog**: `CHANGELOG.md` (Version history)

**Nouvelles spécifications** (2025-11-26):
- `specs/005-i18n-support/spec.md` - Multi-language documentation
- `specs/006-project-docs/spec.md` - Project-level documentation (updated)
- `specs/007-hierarchical-context/spec.md` - Parent detection & breadcrumbs
- `specs/008-template-customization/spec.md` - Theming & CSS customization

---

**Dernière mise à jour**: 2025-11-26  
**Auteur**: Specify Agent  
**Méthodologie**: speckit  
**Version du document**: 2.0.0
