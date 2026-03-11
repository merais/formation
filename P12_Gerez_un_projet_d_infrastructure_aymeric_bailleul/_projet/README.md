# P12 – Avantages Sportifs (Sport Data Solution)

**Auteur :** Aymeric Bailleul
**Formation :** Data Engineer – OpenClassrooms
**Periode :** 10/03/2026 - 11/04/2026

---

## Objectif du projet

Concevoir et deployer un POC (Proof of Concept) pour le programme "Avantages Sportifs" de Sport Data Solution : pipeline ETL complet, base de donnees PostgreSQL, calcul d'eligibilite aux primes sportives et journees bien-etre, dashboard PowerBI.

---

## Architecture

```
Sources (couche raw = disque)
  Donnees+RH.xlsx          -> identites (rh_prive) + anonymise en memoire -> staging.employes
  Donnees+Sportive.xlsx    -> nettoye en memoire   -> staging.pratiques_declarees
  Simulation Strava        -> raw.activites_strava  -> staging.activites_strava

PostgreSQL (Docker, port 5433)
  schema raw       : activites_strava (donnees simulees uniquement)
  schema staging   : employes, pratiques_declarees, activites_strava
  schema gold      : eligibilite_prime, eligibilite_bien_etre, impact_financier
  schema rh_prive  : identites (Nom, Prenom, DDN) — acces restreint RGPD

Droits PostgreSQL
  role_pipeline  : lecture/ecriture raw + staging, lecture gold
  role_analytics : lecture seule gold (PowerBI)
  role_rh_admin  : herite pipeline + acces exclusif rh_prive

Tests qualite (pytest) -> Notifications Slack nominatives (JSON) -> PowerBI
```

**RGPD – Privacy by Design :** les colonnes nominatives (Nom, Prenom, Date de naissance)
sont isolees dans le schema `rh_prive`, accessible uniquement via `role_rh_admin`.
`staging.employes` ne contient que les 8 colonnes anonymisees. Les notifications Slack
utilisent les prenoms/noms via une jointure `rh_prive.identites` avec connexion dediee.

---

## Structure du projet

```
_projet/
├── _docs/                  # Documentation (logbook, note de cadrage, contexte)
├── analyses/               # Notebook exploratoire, CSV nettoyes
├── data/
│   ├── RAW/                # Fichiers sources XLSX (ne pas modifier)
│   └── exports/            # Exports (slack_messages.json, rapports)
├── docker/
│   └── docker-compose.yml  # PostgreSQL 16-alpine
├── src/
│   ├── db/
│   │   ├── connexion.py    # Connexion PostgreSQL via .env (support multi-roles)
│   │   └── init_db.py      # Creation des schemas, tables et roles PostgreSQL
│   ├── ingestion/
│   │   ├── load_rh.py      # XLSX RH -> rh_prive.identites + staging.employes (anonymise)
│   │   └── load_sport.py   # XLSX Sport -> staging.pratiques_declarees
│   ├── simulation/         # Generation des donnees Strava simulees
│   ├── transformation/     # ETL staging -> gold (distances, eligibilites)
│   ├── notifications/      # Notifications Slack nominatives (JSON)
│   └── main.py             # Pipeline complet
├── tests/                  # Tests pytest
│   ├── conftest.py
│   ├── test_distances.py
│   ├── test_simulation.py
│   ├── test_staging.py
│   ├── test_gold.py
│   └── test_rh_prive.py    # Tests schema rh_prive, droits et vue nominative
├── .env.example            # Modele de variables d'environnement
├── .gitignore
├── pyproject.toml          # Configuration uv (Python >= 3.13)
├── uv.lock                 # Verrouillage des dependances
└── README.md               # Ce fichier
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (pour PostgreSQL)
- [uv](https://docs.astral.sh/uv/) (gestionnaire Python)
- Python >= 3.13

---

## Installation

```powershell
# 1. Installer uv (si absent)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Creer l'environnement virtuel
uv venv .venv --python 3.13

# 3. Activer l'environnement
.venv\Scripts\Activate.ps1

# 4. Installer les dependances
uv sync --group dev

# 5. Configurer les variables d'environnement
Copy-Item .env.example .env
# Editer .env avec vos parametres (PostgreSQL, Google Maps API, etc.)
```

---

## Lancer le projet

```powershell
# Demarrer PostgreSQL
docker compose -f docker/docker-compose.yml up -d

# Pipeline complet (reset + ingestion + simulation + ETL + notifications)
uv run python -m src.main --reset

# Pipeline complet sans reset (reutilise la base existante)
uv run python -m src.main
```

### Options du pipeline

```powershell
# Afficher les etapes sans les executer
uv run python -m src.main --dry-run

# Executer une seule etape (1-7)
uv run python -m src.main --step 6      # recalcul gold uniquement

# Seed personnalise pour la simulation Strava
uv run python -m src.main --seed 123

# Reinitialiser la base (DROP + CREATE)
uv run python -m src.main --reset

# Ne pas appeler l'API Google Maps (reutilise le cache existant, ~11s au lieu de ~60s)
uv run python -m src.main --skip-api
```

### Commandes individuelles

```powershell
# Initialiser la base (schemas + tables)
uv run python -m src.db.init_db

# Charger les donnees sources
uv run python -m src.ingestion.load_rh
uv run python -m src.ingestion.load_sport

# Generer les donnees Strava simulees (seed 42 pour reproductibilite)
uv run python -m src.simulation.generate_strava --seed 42

# Pipeline ETL : raw -> staging -> gold
uv run python -m src.transformation.staging
uv run python -m src.transformation.gold

# Notifications Slack (mock -> JSON)
uv run python -m src.notifications.mock_slack
```

### Options utiles

```powershell
# Reinitialiser la base (supprime et recree tout)
uv run python -m src.db.init_db --reset

# Tester la connexion PostgreSQL
uv run python -m src.db.connexion

# Lancer les 51 tests
uv run pytest

# Notifications Slack limitees aux 10 dernieres activites
uv run python -m src.notifications.mock_slack --limit 10
```

---

## Avancement

| Phase | Description | Statut |
|-------|-------------|--------|
| 0 | Initialisation (uv, Docker, notebook exploratoire) | Termine |
| 1 | Infrastructure PostgreSQL (4 schemas, 8 tables, 3 roles) | Termine |
| 2 | Ingestion des donnees sources (RH + Sport + identites rh_prive) | Termine |
| 3 | Simulation Strava (2 256 activites, 95 sportifs, 15 sports) | Termine |
| 4 | Pipeline ETL staging->gold (distances API, eligibilites, impact) | Termine |
| 5 | Tests qualite (51 tests pytest, 0 echec) | Termine |
| 6 | Notifications Slack nominatives (2 256 messages JSON, Prenom + Nom) | Termine |
| 7 | Pipeline principal (main.py orchestrateur, config.py, CLI) | Termine |
| 8 | Streaming temps reel (Redpanda + insertion Strava a la demande) | A faire |
| 9 | Dashboard PowerBI | A faire |
| 10 | Documentation et soutenance | A faire |
