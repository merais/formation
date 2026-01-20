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
- [Tests et validation](#-tests-et-validation)
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

### Vue d'ensemble simplifiée

```
┌────────────────────────────────────────────────────────┐
│           Fichiers sources locaux                      │
│  ─────────────────────────────────────────────────────  │
│  sources/                                              │
│  ├─ fichier_erp.xlsx      (825 lignes brutes)         │
│  ├─ fichier_liaison.xlsx  (825 lignes brutes)         │
│  └─ fichier_web.xlsx      (1513 lignes brutes)        │
└────────────┬───────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│  Script 1: 01_clean_and_merge.py                       │
│  ─────────────────────────────────────────────────────  │
│  [Lecture locale] → Nettoyage → Fusion → [DuckDB]     │
│  Etapes: Verification → Nettoyage → Fusion (3 etapes) │
└────────────┬───────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│             DuckDB (bottleneck.db)                     │
│  ─────────────────────────────────────────────────────  │
│  Tables intermediaires:                                │
│  - erp_clean_final       (825 lignes)                 │
│  - liaison_clean_final   (825 lignes)                 │
│  - web_clean_final       (714 lignes)                 │
│  Table finale:                                         │
│  - merged_data_final     (714 lignes)                 │
└────────────┬───────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│  Script 2: 02_process_and_export.py                    │
│  ─────────────────────────────────────────────────────  │
│  [DuckDB] → Calcul CA → Classification → Export local │
│  Etapes: CA → Classification → Export (3 etapes)      │
└────────────┬───────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│           Fichiers exports locaux                      │
│  ─────────────────────────────────────────────────────  │
│  _exports/                                             │
│  ├─ YYYYMMDD_rapport_ca.xlsx      (2 feuilles)        │
│  ├─ YYYYMMDD_vins_premium.csv     (30 vins)           │
│  └─ YYYYMMDD_vins_ordinaires.csv  (684 vins)          │
└────────────────────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│  Script 3: 03_validate_all.py                          │
│  ─────────────────────────────────────────────────────  │
│  10 tests automatises (100%)                           │
│  Exit code 0 si OK, 1 si KO                            │
└────────────────────────────────────────────────────────┘
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

### 4. Vérifier les fichiers sources

```bash
# Les fichiers doivent être présents dans sources/
ls sources/
# fichier_erp.xlsx
# fichier_liaison.xlsx
# fichier_web.xlsx
```

### 5. Vérifier l'installation

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

## Utilisation

### Exécution manuelle du pipeline complet

```bash
# 1. Script 1 : Nettoyage et fusion
.venv\Scripts\python.exe _scripts\01_clean_and_merge.py

# 2. Script 2 : Traitement et export
.venv\Scripts\python.exe _scripts\02_process_and_export.py

# 3. Script 3 : Validation
.venv\Scripts\python.exe _scripts\03_validate_all.py
```

### Description des scripts

#### Script 1 : 01_clean_and_merge.py
- **Input** : 3 fichiers depuis sources/ (lecture locale)
- **Traitement** : 
  - Verification des fichiers sources (3 fichiers requis)
  - Nettoyage ERP (825 lignes)
  - Nettoyage LIAISON (825 lignes, conservation des NULL sur id_web)
  - Nettoyage WEB (714 lignes, filtrage products + suppression NULL)
  - Fusion complete (714 lignes finales)
- **Output** : Table `merged_data_final` dans DuckDB
- **Etapes** : 3 (Verification → Nettoyage → Fusion)

#### Script 2 : 02_process_and_export.py
- **Input** : Table `merged_data_final` depuis DuckDB
- **Traitement** :
  - Calcul CA par produit et CA total (70 568,60 €)
  - Classification z-score (30 premium, 684 ordinaires)
  - Export local dans _exports/
- **Output** :
  - `YYYYMMDD_rapport_ca.xlsx` (2 feuilles)
  - `YYYYMMDD_vins_premium.csv` (30 vins)
  - `YYYYMMDD_vins_ordinaires.csv` (684 vins)
- **Etapes** : 3 (Calcul CA → Classification → Export)

#### Script 3 : 03_validate_all.py
- **Tests** : 10 tests automatises (100%)
- **Exit code** : 0 si OK, 1 si erreur
- **Validations** :
  - Nettoyage (4 tests)
  - Jointures (2 tests)
  - Calculs CA (2 tests)
  - Classification (2 tests)

---

### Tests et validation

**Dernier test complet : 20/01/2026 16:44**

```bash
# Execution complete
.venv\Scripts\python.exe _scripts\01_clean_and_merge.py
# [OK] PHASE 1 TERMINEE AVEC SUCCES

.venv\Scripts\python.exe _scripts\02_process_and_export.py
# [OK] PHASE 2 TERMINEE AVEC SUCCES

.venv\Scripts\python.exe _scripts\03_validate_all.py
# [OK] VALIDATION GLOBALE REUSSIE
# Total de tests : 10
# Tests reussis  : 10
# Tests echoues  : 0
# Taux de reussite : 100.0%
```

---

## Orchestration Kestra

### Workflow Kestra

Le workflow Kestra orchestrera les 3 scripts Python (traitement 100% local) avec :

1. **Planification** : Cron `0 9 15 * *` (15 du mois a 9h00)
2. **Dependances** : Graphe acyclique dirige (DAG)
3. **Retry** : 3 tentatives par tache
4. **Timeout** : 1 heure maximum
5. **Notifications** : Email en cas d'echec
6. **Logs** : Capture des outputs de validation

---

## Resultats attendus

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