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

### Vue d'ensemble - Architecture AWS S3

```
┌────────────────────────────────────────────────────────┐
│           AWS S3 - bottleneck-pipeline-p10             │
│           Région: eu-west-3 (Paris)                    │
│  ─────────────────────────────────────────────────────  │
│  s3://bottleneck-pipeline-p10/                         │
│  ├─ RAW/                                               │
│  │  ├─ fichier_erp.xlsx      (825 lignes brutes)      │
│  │  ├─ fichier_liaison.xlsx  (825 lignes brutes)      │
│  │  └─ fichier_web.xlsx      (1513 lignes brutes)     │
│  │                                                      │
│  └─ EXPORTS/                                           │
│     └─ YYYYMMDD_HHMMSS/                                │
│        ├─ rapport_ca.xlsx                              │
│        ├─ vins_premium.csv                             │
│        └─ vins_ordinaires.csv                          │
└────────────┬───────────────────────────────────────────┘
             ▼
┌────────────────────────────────────────────────────────┐
│  Kestra - Workflow bottleneck_pipeline_s3              │
│  ─────────────────────────────────────────────────────  │
│  Tâche 1: Download depuis S3/RAW/                     │
│           ↓                                            │
│  Tâches 2-4: Nettoyage parallèle (ERP, LIAISON, WEB)  │
│           ↓                                            │
│  Tâche 5: Fusion des données (714 lignes)             │
│           ↓                                            │
│  Tâche 6: Calcul CA (70 568,60 €)                     │
│           ↓                                            │
│  Tâche 7: Classification z-score (30 premium)         │
│           ↓                                            │
│  Tâches 8-11: Exports + Validation en parallèle       │
│           ↓                                            │
│  Tâche 12: Upload vers S3/EXPORTS/                    │
│                                                         │
│  Parallélisme: 2 groupes (nettoyage + exports)        │
│  Performance: ~2 minutes (40% plus rapide)            │
└────────────────────────────────────────────────────────┘
```

### Architecture détaillée Kestra

**12 tâches orchestrées avec 2 groupes parallèles:**

1. **task_01_download_sources** - Téléchargement S3 (3 fichiers)
2. **parallel_cleaning** - Groupe parallèle de nettoyage:
   - **task_02_clean_erp** - 825 lignes
   - **task_03_clean_liaison** - 825 lignes
   - **task_04_clean_web** - 714 lignes
3. **task_05_merge_data** - Fusion (714 lignes)
4. **task_06_calculate_ca** - Calcul CA (70 568,60 €)
5. **task_07_classify_wines** - Classification (30 premium, 684 ordinaires)
6. **task_08_validation** - 5 tests automatisés (bloque si échec)
7. **parallel_exports** - Groupe parallèle d'exports:
   - **task_09_export_rapport_ca** - Excel 2 feuilles
   - **task_10_export_vins_premium** - CSV 30 vins
   - **task_11_export_vins_ordinaires** - CSV 684 vins
8. **task_12_upload_exports_to_s3** - Upload vers S3

---

## Technologies utilisées

| Technologie | Version | Usage |
|------------|---------|-------|
| **Python** | 3.14.0 | Langage de développement |
| **Poetry** | 2.2.1 | Gestionnaire de dépendances |
| **pandas** | 2.3.3 | Manipulation de données |
| **pyarrow** | 23.0.0 | Format Parquet (performance) |
| **openpyxl** | 3.1.5 | Lecture/écriture Excel |
| **numpy** | 2.4.1 | Calculs statistiques (z-score) |
| **Kestra** | Latest | Orchestration de workflows |
| **Docker** | Latest | Conteneurisation Kestra + PostgreSQL |
| **AWS S3** | - | Stockage cloud (eu-west-3) |
| **boto3** | Latest | SDK AWS pour Python |

---

## Installation

### Prérequis

- Python 3.14+
- Poetry 2.2.1+
- Docker Desktop (pour Kestra)
- Git

### 1. Cloner le projet

```bash
git clone https://github.com/merais/formation.git # /!\ il s'agit de mon repo complet pour la formation
cd "P10_Mettez_en_place_le_pipeline_d_orchestration_des_flux_aymeric_bailleul/_projet"
```

### 2. Installer les dépendances Python

```bash
# Installation avec Poetry
poetry install

# Activation de l'environnement virtuel
poetry shell
```

### 3. Configuration AWS S3

```bash
# Créer le bucket S3 dans la région eu-west-3 (Paris)
aws s3 mb s3://bottleneck-pipeline-p10 --region eu-west-3

# Créer les dossiers RAW/ et EXPORTS/
aws s3api put-object --bucket bottleneck-pipeline-p10 --key RAW/
aws s3api put-object --bucket bottleneck-pipeline-p10 --key EXPORTS/

# Uploader les fichiers sources dans S3/RAW/
aws s3 cp sources/fichier_erp.xlsx s3://bottleneck-pipeline-p10/RAW/
aws s3 cp sources/fichier_liaison.xlsx s3://bottleneck-pipeline-p10/RAW/
aws s3 cp sources/fichier_web.xlsx s3://bottleneck-pipeline-p10/RAW/

# Vérifier l'upload
aws s3 ls s3://bottleneck-pipeline-p10/RAW/
```

### 4. Configuration des secrets Kestra

Créer le fichier `_projet/_kestra/.env` avec les credentials AWS en BASE64:

```bash
# Créer le fichier .env
cd _projet/_kestra

# Éditer .env avec les valeurs suivantes :
# AWS Credentials (BASE64 encoded)
SECRET_AWS_ACCESS_KEY_ID=<VOTRE_ACCESS_KEY_BASE64>
SECRET_AWS_SECRET_ACCESS_KEY=<VOTRE_SECRET_KEY_BASE64>

# PostgreSQL Credentials (plain text)
POSTGRES_DB=kestra
POSTGRES_USER=kestra
POSTGRES_PASSWORD=k3str4
```

**Encodage BASE64** (si nécessaire):
```powershell
# PowerShell
[Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("VOTRE_ACCESS_KEY"))
```

### 5. Déployer le workflow Kestra

```bash
cd _projet/_kestra
docker-compose up -d

# Vérifier que Kestra est accessible
# Interface web : http://localhost:8080

```

### 6. Vérifier l'installation

```bash
# Vérifier Python
python --version  # Python 3.14.0

# Vérifier Poetry
poetry --version  # Poetry 2.2.1

# Vérifier Docker
docker ps  # kestra-kestra-1, kestra-postgres-1

# Vérifier AWS CLI
aws --version
aws s3 ls s3://bottleneck-pipeline-p10/

# Vérifier Kestra
# Accéder à http://localhost:8080
# Onglet Flows → company.bottleneck → bottleneck_pipeline_s3
```

---

## Utilisation

### Exécution via Kestra

1. **Accéder à l'interface Kestra**: http://localhost:8080
2. **Naviguer vers le workflow**: Flows → company.bottleneck → bottleneck_pipeline_s3
3. **Lancer l'exécution**: Bouton "Execute"
4. **Suivre l'exécution**: Onglet "Gantt" pour visualiser le parallélisme
5. **Consulter les logs**: Cliquer sur chaque tâche pour voir les détails
6. **Vérifier les résultats**: S3 bucket → EXPORTS/YYYYMMDD_HHMMSS/

**Temps d'exécution moyen**: ~2 minutes (avec parallélisation)

### Structure du workflow

#### Tâche 1: Download depuis S3
- **Input**: s3://bottleneck-pipeline-p10/RAW/
- **Output**: 3 fichiers Excel téléchargés
- **Durée**: ~5 secondes

#### Groupe parallèle: Nettoyage (tasks 2-4)
- **task_02_clean_erp**: 825 lignes (validées) → erp_clean.parquet
- **task_03_clean_liaison**: 825 lignes (validées) → liaison_clean.parquet
- **task_04_clean_web**: 1428 → 714 lignes (validées) → web_clean.parquet
- **Durée**: ~14 secondes (simultané)

#### Tâche 5: Fusion
- **Input**: 3 fichiers Parquet
- **Output**: merged_data.parquet (714 lignes)
- **Durée**: ~13 secondes

#### Tâche 6: Calcul CA
- **Input**: merged_data.parquet
- **Output**: data_with_ca.parquet (CA: 70 568,60 €)
- **Durée**: ~11 secondes

#### Tâche 7: Classification
- **Input**: data_with_ca.parquet
- **Output**: data_classified.parquet (30 premium, 684 ordinaires)
- **Durée**: ~13 secondes

#### Tâche 8: Validation
- **Input**: data_classified.parquet
- **Tests**: 5 tests automatisés (714 lignes, CA, premium, ordinaires)
- **Blocage**: allowFailure: false → arrête le workflow si échec
- **Durée**: ~13 secondes

#### Groupe parallèle: Exports (tasks 9-11)
- **task_09_export_rapport_ca**: Excel 2 feuilles
- **task_10_export_vins_premium**: CSV 30 vins
- **task_11_export_vins_ordinaires**: CSV 684 vins
- **Durée**: ~13 secondes (simultané)

#### Tâche 12: Upload vers S3
- **Input**: 3 fichiers (xlsx, 2x csv)
- **Output**: s3://bottleneck-pipeline-p10/EXPORTS/YYYYMMDD_HHMMSS/
- **Durée**: ~10 secondes

### Planification automatique

Le workflow s'exécute automatiquement:
- **Fréquence**: Mensuelle
- **Jour**: 15 de chaque mois
- **Heure**: 09h00 (Europe/Paris)
- **Cron**: `0 9 15 * *`

### Exécution manuelle locale (développement)

Pour les tests locaux avec les scripts Python:

```bash
# 1. Script 1 : Nettoyage et fusion
poetry run python _scripts/01_clean_and_merge.py

# 2. Script 2 : Traitement et export
poetry run python _scripts/02_process_and_export.py

# 3. Script 3 : Validation
poetry run python _scripts/03_validate_all.py
```

### Scripts utilitaires AWS S3

Pour gérer manuellement les uploads/downloads S3 :

```bash
# Upload des fichiers sources vers S3/RAW/
poetry run python _scripts/04_upload_sources_to_s3.py

# Download des exports depuis S3/EXPORTS/ (dossier le plus récent)
poetry run python _scripts/05_download_exports_from_s3.py
```

**Notes** :
- Les scripts utilisent les credentials AWS depuis les variables d'environnement (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) ou `~/.aws/credentials`
- Le script 04 uploade les 3 fichiers sources (erp, liaison, web) vers S3/RAW/
- Le script 05 détecte automatiquement le dossier d'export le plus récent et télécharge les résultats dans `_exports/` (mise à jour si exécuté plusieurs fois)


---

### Monitoring et logs

Kestra fournit:
- **Gantt Chart**: Visualisation du parallélisme et des dépendances
- **Logs détaillés**: Output de chaque tâche (stdout/stderr)
- **Métriques**: Durée d'exécution, retry, statuts
- **Historique**: Toutes les exécutions avec résultats

---

## Orchestration Kestra

### Fichier workflow: bottleneck_pipeline_s3.yaml

**Localisation**: `_kestra/bottleneck_pipeline_s3.yaml`

**Caractéristiques**:
- **Namespace**: company.bottleneck
- **ID**: bottleneck_pipeline_s3
- **Bucket S3**: bottleneck-pipeline-p10 (eu-west-3)
- **Secrets**: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY (BASE64)

### Architecture du workflow

**12 tâches organisées en pipeline séquentiel avec 2 groupes parallèles:**

```
task_01_download_sources (S3 Downloads)
    ↓
parallel_cleaning (Parallel)
    ├─ task_02_clean_erp
    ├─ task_03_clean_liaison
    └─ task_04_clean_web
    ↓
task_05_merge_data
    ↓
task_06_calculate_ca
    ↓
task_07_classify_wines
    ↓
task_08_validation (allowFailure: false)
    ↓
parallel_exports (Parallel)
    ├─ task_09_export_rapport_ca
    ├─ task_10_export_vins_premium
    └─ task_11_export_vins_ordinaires
    ↓
task_12_upload_exports_to_s3
```

### Fonctionnalités avancées

#### Parallélisation
- **Plugin**: `io.kestra.plugin.core.flow.Parallel`
- **Groupe 1**: Nettoyage des 3 sources (tasks 2-4)
- **Groupe 2**: Exports (tasks 9-11)

#### Gestion des erreurs
- **Retry**: 3 tentatives avec backoff exponentiel
- **Timeout**: 10 minutes par tâche
- **Validation bloquante**: allowFailure: false sur task_08
- **Notifications**: Email en cas d'échec

#### Sécurité
- **Secrets BASE64**: Credentials AWS stockés dans `.env`
- **Variables d'environnement**: `docker-compose.yml` utilise `${VARIABLE}` pour référencer `.env`
- **Utilisateur IAM**: Droits limités
- **Région**: eu-west-3 (Paris) pour conformité RGPD
- **PostgreSQL**: Credentials également dans `.env` pour configuration unifiée

### Trigger de planification

**Exécution automatique mensuelle:**

```yaml
triggers:
  - id: monthly_execution
    type: io.kestra.plugin.core.trigger.Schedule
    description: "Execution automatique le 15 de chaque mois a 9h (heure Paris)"
    cron: "0 9 15 * *"
    timezone: "Europe/Paris"
```

**Calendrier d'exécution 2026:**
- 15 janvier 2026 à 09h00
- 15 février 2026 à 09h00
- 15 mars 2026 à 09h00
- etc.

### Accès au workflow

1. **Interface Kestra**: http://localhost:8080
2. **Flows** → **company.bottleneck** → **bottleneck_pipeline_s3**
3. **Actions disponibles**:
   - Execute: Lancer manuellement
   - Edit: Modifier le workflow
   - Export: Télécharger le YAML
   - Delete: Supprimer le workflow
4. **Onglets**:
   - **Overview**: Vue d'ensemble et description
   - **Topology**: Graphe des dépendances
   - **Gantt**: Timeline avec parallélisme
   - **Logs**: Sortie détaillée de chaque tâche
   - **Outputs**: Fichiers générés

---

## Resultats attendus

### Métriques clés

| Métrique | Valeur attendue | Statut |
|----------|----------------|--------|
| Lignes ERP après dedoublonnage | 825 | OK |
| Lignes LIAISON après dedoublonnage | 825 | OK |
| Lignes WEB après nettoyage NULL | 1428 | OK |
| Lignes WEB après dedoublonnage | 714 | OK |
| Lignes fusionnées | 714 | OK |
| **CA total** | **70 568,60 €** | OK |
| **Vins premium** | **30** | OK |
| **Vins ordinaires** | **684** | OK |
| Tests de validation | 5/5 (100%) | OK |

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