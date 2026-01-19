# BottleNeck - Pipeline d'orchestration des flux de données

**Auteur** : Aymeric BAILLEUL  
**Projet** : P10 - Mettez en place le pipeline d'orchestration des flux  
**Formation** : Data Engineer - OpenClassrooms  
**Date** : Janvier 2026

---

## Sommaire

- [Description du projet](#-description-du-projet)
- [Architecture](#-architecture)
- [Technologies utilisées](#-technologies-utilisées)
- [Installation](#-installation)
- [Structure du projet](#-structure-du-projet)
- [Pipeline de traitement](#-pipeline-de-traitement)
- [Utilisation](#-utilisation)
- [Validation](#-validation)
- [Orchestration Kestra](#-orchestration-kestra)
- [Résultats attendus](#-résultats-attendus)

---

## Description du projet

**BottleNeck** est une entreprise de vente de vin en ligne qui souhaite automatiser son pipeline de données pour analyser ses performances commerciales et classifier ses produits.

### Objectifs métier

1. **Réconciliation des données** : Fusionner les données provenant de 3 sources (ERP, fichier de liaison, CMS web)
2. **Calcul du chiffre d'affaires** : Calculer le CA par produit et le CA total
3. **Classification des vins** : Identifier les vins premium via z-score (prix standardisé)
4. **Automatisation** : Orchestrer le pipeline avec Kestra pour exécution mensuelle

### Résultats finaux

- **CA total** : 70 568,60 €
- **Vins premium** : 30 produits (z-score > 2)
- **Vins ordinaires** : 684 produits
- **Exports** : rapport_ca.xlsx, vins_premium.csv, vins_ordinaires.csv

---

## Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  ERP.xlsx   │  │ LIAISON.xlsx│  │  WEB.xlsx   │
│  (825 rows) │  │  (825 rows) │  │ (1513 rows) │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│          Scripts de nettoyage                │
│  01_clean_erp.py │ 02_clean_liaison.py │    │
│               03_clean_web.py               │
└──────┬───────────────┬───────────────┬──────┘
       │               │               │
       ▼               ▼               ▼
┌──────────────────────────────────────────────┐
│            DuckDB (bottleneck.db)            │
│  erp_clean_final │ liaison_clean_final │    │
│            web_clean_final                   │
└──────────────────┬───────────────────────────┘
                   ▼
       ┌───────────────────────┐
       │  04_merge_all.py      │
       │  merged_data_final    │
       └───────────┬───────────┘
                   ▼
       ┌───────────────────────┐
       │  05_calculate_ca.py   │
       │  ca_par_produit       │
       │  ca_total             │
       └───────────┬───────────┘
                   ▼
       ┌───────────────────────┐
       │  06_classify_wines.py │
       │  wines_classified     │
       └───────────┬───────────┘
                   ▼
       ┌───────────────────────┐
       │  07_export_results.py │
       │  Excel + CSV          │
       └───────────┬───────────┘
                   ▼
       ┌───────────────────────┐
       │  08_validate_all.py   │
       │  10 tests (100%)      │
       └───────────────────────┘
```

---

## Technologies utilisées

| Technologie | Version | Usage |
|------------|---------|-------|
| **Python** | 3.14.0 | Langage de développement |
| **Poetry** | 2.2.1 | Gestionnaire de dépendances |
| **DuckDB** | 1.4.3 | Base de données analytique |
| **pandas** | Latest | Manipulation de données |
| **openpyxl** | Latest | Lecture/écriture Excel |
| **Kestra** | Latest | Orchestration de workflows |
| **Docker** | Latest | Conteneurisation Kestra |

---

## Installation

### Prérequis

- Python 3.14+
- Poetry 2.2.1+
- Docker Desktop (pour Kestra)
- Git

### 1. Cloner le projet

```bash
git clone https://github.com/merais/formation.git
cd "P10_Mettez_en_place_le_pipeline_d_orchestration_des_flux_aymeric_bailleul/_projet"
```

### 2. Installer les dépendances Python

```bash
# Installation avec Poetry
poetry install

# Activation de l'environnement virtuel
poetry shell
```

### 3. Installer Kestra (via Docker)

```bash
cd ../../tools/kestra
docker-compose up -d

# Vérifier que Kestra est accessible
# Interface web : http://localhost:8080
```

### 4. Vérifier l'installation

```bash
# Vérifier Python
python --version  # Python 3.14.0

# Vérifier Poetry
poetry --version  # Poetry 2.2.1

# Vérifier DuckDB
poetry run duckdb  # DuckDB 1.4.3

# Vérifier Docker
docker ps  # kestra-kestra-1, kestra-postgres-1
```

---

## Pipeline de traitement

### Étape 1 : Nettoyage des données (Scripts 01-03)

#### Script 01 : Nettoyage ERP
```bash
poetry run python _scripts/01_clean_erp.py
```
- **Input** : fichier_erp.xlsx (825 lignes)
- **Traitement** : Suppression NULL + dédoublonnage
- **Output** : Table `erp_clean_final` (825 lignes)
- **Clé primaire** : `product_id`

#### Script 02 : Nettoyage LIAISON
```bash
poetry run python _scripts/02_clean_liaison.py
```
- **Input** : fichier_liaison.xlsx (825 lignes)
- **Traitement** : Conservation NULL sur `id_web` (91 produits sans référence web)
- **Output** : Table `liaison_clean_final` (825 lignes)
- **Clé primaire** : `product_id`

#### Script 03 : Nettoyage WEB
```bash
poetry run python _scripts/03_clean_web.py
```
- **Input** : fichier_web.xlsx (1513 lignes)
- **Traitement** : Filtrage `post_type='product'` + suppression NULL + dédoublonnage intelligent
- **Output** : Table `web_clean_final` (714 lignes)
- **Clé primaire** : `sku`

### Étape 2 : Fusion des données (Script 04)

```bash
poetry run python _scripts/04_merge_all.py
```
- **Jointure 1** : ERP ⟕ LIAISON sur `product_id` → 825 lignes
- **Filtrage** : Suppression des `id_web` NULL → 734 lignes
- **Jointure 2** : (ERP+LIAISON) ⟕ WEB sur `id_web = sku` → 714 lignes
- **Output** : Table `merged_data_final` (714 lignes)

### Étape 3 : Calcul du chiffre d'affaires (Script 05)

```bash
poetry run python _scripts/05_calculate_ca.py
```
- **Formule** : `CA = erp_price × total_sales`
- **Output 1** : Table `ca_par_produit` (714 lignes)
- **Output 2** : Table `ca_total` (CA total = 70 568,60 €)

### Étape 4 : Classification des vins (Script 06)

```bash
poetry run python _scripts/06_classify_wines.py
```
- **Statistiques** : μ = 32,49 € | σ = 27,81 €
- **Formule z-score** : `z = (prix - μ) / σ`
- **Classification** : 
  - `premium` si z-score > 2
  - `ordinaire` sinon
- **Output** : Table `wines_classified` (714 lignes)
  - 30 vins premium
  - 684 vins ordinaires

### Étape 5 : Export des résultats (Script 07)

```bash
poetry run python _scripts/07_export_results.py
```
- **Fichier 1** : `rapport_ca.xlsx` (2 feuilles)
  - Feuille 1 : CA par produit (714 lignes)
  - Feuille 2 : CA total (1 ligne)
- **Fichier 2** : `vins_premium.csv` (30 vins)
- **Fichier 3** : `vins_ordinaires.csv` (684 vins)

### Étape 6 : Validation globale (Script 08)

```bash
poetry run python _scripts/08_validate_all.py
```
- **10 tests automatisés** :
  1. ERP nettoyé (825 lignes, 0 doublons)
  2. LIAISON nettoyé (825 lignes, 0 doublons)
  3. WEB nettoyé (714 lignes, 0 NULL, 0 doublons)
  4. WEB dédoublonné (714 SKU uniques)
  5. Cohérence jointure ERP-LIAISON (0 orphelins)
  6. Cohérence jointure finale (714 lignes)
  7. CA positifs (0 CA négatifs, 0 NULL)
  8. CA total (70 568,60 € ± 0,01 €)
  9. Z-scores valides (0 NULL/NaN/Inf)
  10. Vins premium (30 vins attendus)

- **Exit code** :
  - `0` : Tous les tests passent → Pipeline prêt pour Kestra
  - `1` : Erreurs détectées → Correction nécessaire

---

## Utilisation

### Exécution manuelle du pipeline complet

```bash
# 1. Supprimer la BDD pour repartir de zéro (optionnel)
rm _bdd/bottleneck.db

# 2. Exécuter les 8 scripts séquentiellement
poetry run python _scripts/01_clean_erp.py
poetry run python _scripts/02_clean_liaison.py
poetry run python _scripts/03_clean_web.py
poetry run python _scripts/04_merge_all.py
poetry run python _scripts/05_calculate_ca.py
poetry run python _scripts/06_classify_wines.py
poetry run python _scripts/07_export_results.py
poetry run python _scripts/08_validate_all.py

# 3. Vérifier les résultats
ls _exports/  # rapport_ca.xlsx, vins_premium.csv, vins_ordinaires.csv
```

### Exécution avec script unique (à créer)

```bash
# Créer un script run_pipeline.sh
poetry run python _scripts/01_clean_erp.py && \
poetry run python _scripts/02_clean_liaison.py && \
poetry run python _scripts/03_clean_web.py && \
poetry run python _scripts/04_merge_all.py && \
poetry run python _scripts/05_calculate_ca.py && \
poetry run python _scripts/06_classify_wines.py && \
poetry run python _scripts/07_export_results.py && \
poetry run python _scripts/08_validate_all.py
```

---

## Validation

Le script de validation globale (`08_validate_all.py`) effectue **10 tests** couvrant :

### BLOC 1 : Nettoyage (4 tests)
- ✓ Table ERP : 825 lignes, 0 doublons
- ✓ Table LIAISON : 825 lignes, 0 doublons
- ✓ Table WEB : 0 NULL sur SKU, 0 non-products
- ✓ Table WEB : 714 lignes, 0 doublons SKU

### BLOC 2 : Jointures (2 tests)
- ✓ Cohérence ERP-LIAISON : 0 orphelins
- ✓ Cohérence finale : 714 lignes, 0 orphelins WEB

### BLOC 3 : CA (2 tests)
- ✓ CA positifs : 0 négatifs, 0 NULL
- ✓ CA total : 70 568,60 € (écart = 0,00 €)

### BLOC 4 : Classification (2 tests)
- ✓ Z-scores valides : 0 NULL/NaN/Inf
- ✓ Vins premium : 30 (attendu = 30)

**Résultat** : 10/10 tests passent (100%) ✓

---

## Orchestration Kestra

### Workflow Kestra (à implémenter)

Le workflow Kestra orchestrera les 8 scripts Python avec :

1. **Planification** : Cron `0 9 15 * *` (15 du mois à 9h00)
2. **Dépendances** : Graphe acyclique dirigé (DAG)
3. **Retry** : 3 tentatives par tâche
4. **Timeout** : 1 heure maximum
5. **Notifications** : Email en cas d'échec
6. **Logs** : Capture des outputs de validation

---

## Résultats attendus

### Métriques clés

| Métrique | Valeur attendue | Statut |
|----------|----------------|--------|
| Lignes ERP nettoyées | 825 | OK |
| Lignes LIAISON nettoyées | 825 | OK |
| Lignes WEB nettoyées | 714 | OK |
| Lignes fusionnées | 714 | OK |
| **CA total** | **70 568,60 €** | OK |
| **Vins premium** | **30** | OK |
| **Vins ordinaires** | **684** | OK |
| Tests de validation | 10/10 (100%) | OK |

### TOP 5 vins premium

1. Champagne Egly-Ouriet Grand Cru Millésimé 2008 - 225,00 € (z=6.92)
2. David Duband Charmes-Chambertin Grand Cru 2014 - 217,50 € (z=6.65)
3. Coteaux Champenois Egly-Ouriet Ambonnay Rouge 2016 - 191,30 € (z=5.71)
4. Cognac Frapin VIP XO - 176,00 € (z=5.16)
5. Camille Giroud Clos de Vougeot 2016 - 175,00 € (z=5.12)

### TOP 5 produits par CA

1. Champagne Gosset Grand Blanc de Blancs - 4 704,00 €
2. Champagne Gosset Grand Rosé - 4 263,00 €
3. Cognac Frapin VIP XO - 2 288,00 €
4. Champagne Gosset Grand Millésime 2006 - 1 590,00 €
5. Champagne Gosset Grande Réserve - 1 560,00 €

---