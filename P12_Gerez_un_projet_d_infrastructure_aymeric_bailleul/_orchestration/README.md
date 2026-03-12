# Sport Data – Orchestration

Pipeline de données complet pour le projet **Sport Data Solution**.  
Ce répertoire est le projet final autonome : il contient sa propre stack Python, son projet dbt et son orchestrateur Kestra.

---

## Architecture

```
_orchestration/
├── docker-compose.yml          # PostgreSQL + Kestra
├── kestra.Dockerfile           # Image Kestra enrichie (Python 3 + dbt-postgres)
├── init-db.sql                 # Crée la base 'kestra' au premier démarrage
├── init.ps1                    # Script d'initialisation locale (hors Docker)
├── main.py                     # Pipeline Python complet (6 étapes)
├── pyproject.toml              # Dépendances du package Python
├── .python-version             # Python 3.12
├── .env                        # Configuration locale (non commité)
├── .env.example                # Template de configuration
│
├── src/                        # Package Python (utilisé par main.py en local)
│   ├── db/
│   │   ├── connexion.py        # Connexion PostgreSQL multi-rôle
│   │   └── init_db.py          # Schémas, tables, rôles, migration
│   ├── ingestion/
│   │   ├── load_rh.py          # UPSERT employes + soft-delete + hash
│   │   └── load_sport.py       # UPSERT pratiques + delete-absent + hash
│   ├── transformation/
│   │   ├── staging.py          # Staging Python (activites_strava)
│   │   ├── distances.py        # Calcul distances géographiques
│   │   └── gold.py             # Couche gold Python (eligibilite_bien_etre)
│   └── simulation/
│       └── generate_strava.py  # Génération initiale d'activités Strava simulées
│
├── scripts/                    # Scripts standalone exécutés par Kestra
│   ├── check_changes.py        # Détection changements XLSX + watermark Strava
│   ├── reload_rh.py            # Re-ingestion RH (UPSERT + soft-delete)
│   ├── reload_sport.py         # Re-ingestion sport (UPSERT + delete-absent)
│   └── simulate_new_activities.py  # Ajout incrémental d'activités Strava
│
├── dbt/                        # Projet dbt autonome (copie de _projet_dbt)
│   ├── profiles.yml            # Connexion dbt (via env_var())
│   └── sport_data/
│       ├── dbt_project.yml
│       ├── macros/
│       └── models/
│           ├── sources.yml
│           ├── staging/        # stg_activites_strava (filtre actif = true)
│           └── gold/           # eligibilite_prime, eligibilite_bien_etre, impact_financier
│
└── flows/
    └── sport_data_pipeline.yml # Flow Kestra (déclenchement quotidien 06h00)
```

---

## Différences avec `_projet` / `_projet_dbt`

| Fonctionnalité | `_projet` | `_orchestration` |
|---|---|---|
| Ingestion | TRUNCATE + INSERT | UPSERT + hash SHA-256 |
| Salariés inactifs | Non géré | `actif = FALSE` (soft-delete) |
| Détection changements | Non | `meta.pipeline_state` (hash + watermark) |
| Historique exécutions | Non | `meta.pipeline_runs` |
| Colonne `inserted_at` | Non | `raw.activites_strava.inserted_at` |
| Filtres dbt | Tous salariés | `WHERE actif = true` |
| Orchestration | Manuelle | Kestra (cron quotidien) |

---

## Prérequis

- **Docker Desktop** (PostgreSQL + Kestra)
- **Python 3.12** — venv à `C:\Users\aymer\.venvs\orchestration`
- Fichiers XLSX sources dans le dossier indiqué par `XLSX_DIR` dans `.env`

> **Images locales** : les images `sport_data_kestra:local` et `sport_data_postgres:local` ne sont pas sur Docker Hub. Elles doivent être construites localement via `docker compose build` avant tout `docker compose up -d` (premier démarrage ou après suppression des images).

---

## Démarrage

### 1. Configuration

```powershell
Copy-Item .env.example .env
# Editer .env : adapter XLSX_DIR si nécessaire
```

### 2. Construction des images (premier démarrage ou après reset complet)

```powershell
docker compose build
```

Construit les deux images locales (`sport_data_kestra:local`, `sport_data_postgres:local`).  
Cette étape est **obligatoire** si les images n'existent pas (premier démarrage, ou après `docker system prune` / suppression des images). Si les images existent déjà, cette étape peut être sautée.

### 3. Démarrage des conteneurs

```powershell
docker compose up -d
```

Lance 3 services :
- **postgres** (port 5433) — base `sport_data` + base interne `kestra`
- **kestra** (port 9000) — orchestrateur, attend que postgres soit healthy  
  Authentification via `basicAuth` : identifiants déclarés dans `KESTRA_EMAIL` / `KESTRA_PASSWORD` du `.env`, copiés dans la config YAML de Kestra au démarrage — **aucun état en base requis**, fonctionne dès les volumes vides.
- **kestra-setup** — service éphémère qui, au démarrage :
  1. Attend que l'endpoint `/health` de Kestra réponde `UP`
  2. Boucle jusqu'à ce que l'authentification soit opérationnelle
  3. Importe automatiquement `sport_data_pipeline.yml` via `POST /api/v1/flows` avec les credentials
  4. Supprime les flows tutoriaux par défaut

Le flow est donc **prêt à l'emploi sans action manuelle** dans l'UI.

### 4. Reset complet (containers + images + volumes)

Procédure pour repartir de zéro :

```powershell
# 1. Tout supprimer
docker compose down -v --rmi local

# 2. Reconstruire les images
docker compose build

# 3. Redémarrer (flow importé automatiquement par kestra-setup)
docker compose up -d

# 4. Vérifier l'import du flow (doit afficher "importe avec succes")
docker logs sport_data_kestra_setup

# 5. Créer les schémas, tables et charger les données initiales
.\init.ps1

# Ou en une seul ligne : 
docker compose down -v --rmi local; docker compose build; docker compose up -d; Start-Sleep -Seconds 45; docker logs sport_data_kestra_setup; .\init.ps1
```

### 5. Initialisation locale

```powershell
.\init.ps1
```

Ce script :
1. Charge `.env` dans les variables d'environnement
2. Exécute `main.py --reset` (crée schémas, tables, rôles, charge les données, lance dbt)
3. Valide la connexion dbt avec `dbt debug`

### 6. Interface Kestra

Ouvrir [http://localhost:9000](http://localhost:9000).

Connexion : email et mot de passe définis dans `KESTRA_EMAIL` / `KESTRA_PASSWORD` du `.env`.

Le flow `sport_data / sport_data_pipeline` est déjà importé et actif. Deux modes de déclenchement :
- **Manuel** : bouton "Execute" dans l'UI
- **Automatique** : cron quotidien à 06h00

---

## Pipeline Kestra — Logique

```
check_changes.py
    ├── rh_changed = True      →  reload_rh.py
    ├── sport_changed = True   →  reload_sport.py
    └── should_run = True      →  dbt run  (PASS=4)
                               →  dbt test (PASS=36)
                               →  meta.pipeline_runs (INSERT résultat)
```

Le flow ne relance dbt que si au moins un changement est détecté (`rh_changed OR sport_changed OR new_activities_count > 0`), évitant des exécutions inutiles.

---

## Configuration Kestra

### Authentification (`basicAuth`)

Kestra est configuré en mode `basicAuth` avec les credentials du `.env` :

```yaml
# Dans KESTRA_CONFIGURATION (docker-compose.yml)
kestra:
  server:
    basicAuth:
      enabled: true
      username: ${KESTRA_EMAIL}
      password: ${KESTRA_PASSWORD}
```

Ces credentials sont résolus au démarrage du conteneur à partir du `.env`. Ils ne sont **pas stockés dans la base de données** — la configuration fonctionne donc sur des volumes vierges sans étape d'initialisation manuelle.

### Variables de flow (`{{ vars.* }}`)

Les paramètres de connexion et de chemin sont déclarés dans le bloc `variables:` du flow YAML et accessibles via `{{ vars.xxx }}` :

```yaml
variables:
  postgres_host: postgres
  postgres_port: "5432"
  postgres_db: sport_data
  postgres_user: postgres
  data_dir: /opt/data/RAW
  dbt_project_dir: /opt/dbt/sport_data
  dbt_profiles_dir: /opt/dbt
```

### Secrets (`{{ secret('...') }}`)

Le mot de passe PostgreSQL est injecté via le mécanisme secret de Kestra (toute variable d'environnement préfixée `SECRET_` dans le conteneur kestra devient un secret) :

```yaml
# docker-compose.yml — variable d'environnement du container kestra
SECRET_POSTGRES_PASSWORD: cG9zdGdyZXM=   # base64('postgres')

# Utilisation dans le flow
password: "{{ secret('POSTGRES_PASSWORD') }}"
```

### Connexion PostgreSQL mutualisée (`pluginDefaults`)

L'URL, le nom d'utilisateur et le mot de passe ne sont déclarés **qu'une seule fois** pour toutes les tâches `io.kestra.plugin.jdbc.postgresql.*` :

```yaml
pluginDefaults:
  - type: io.kestra.plugin.jdbc.postgresql
    values:
      url: "jdbc:postgresql://{{ vars.postgres_host }}:{{ vars.postgres_port }}/{{ vars.postgres_db }}"
      username: "{{ vars.postgres_user }}"
      password: "{{ secret('POSTGRES_PASSWORD') }}"
```

---

## Pipeline local — Options

```powershell
# Initialisation complète (supprime et recrée tout)
python main.py --reset

# Sans appel API Strava (simulation locale)
python main.py --reset --skip-api

# Chargement seul, sans reset
python main.py

# Avec regénération des données simulées
python main.py --seed
```

---

## Schéma de base de données

```
raw
└── activites_strava        (id_salarie, date_activite, type_activite, duree_minutes, distance_km, inserted_at)

staging
├── employes                (id_salarie, nom, prenom, poste, departement, salaire, date_embauche, actif)
├── pratiques_declarees     (id_salarie, activite_preferee, frequence_semaine, annee_depart)
└── activites_strava        (vue dbt)

gold
├── eligibilite_prime       (dbt — filtre actif = true)
├── eligibilite_bien_etre   (dbt — filtre actif = true)
└── impact_financier        (dbt)

rh_prive
└── identites               (id_salarie, email, telephone, adresse)
└── vue_primes_nominatives  (vue — filtre actif = true)

meta
├── pipeline_state          (file_name, file_hash, watermark, updated_at)
└── pipeline_runs           (run_id, run_at, status, rh_changed, sport_changed, new_activities_count)
```

---

## Simulation d'un cycle incrémental

### 1. Vérifier l'état avant

```powershell
# Nombre d'activités brutes + watermark actuel
docker exec sport_data_postgres psql -U postgres -d sport_data -c "
SELECT
  (SELECT COUNT(*) FROM raw.activites_strava)          AS nb_activites_raw,
  (SELECT COUNT(*) FROM staging.activites_strava)      AS nb_activites_staging,
  (SELECT MAX(nb_activites_annee) FROM gold.eligibilite_bien_etre) AS max_activites_gold,
  (SELECT watermark FROM meta.pipeline_state WHERE file_name = '_strava_watermark') AS watermark;
"
```

### 2. Simuler de nouvelles entrées Strava

```powershell
# Activer le venv de l'orchestration (psycopg2 requis)
& "C:\Users\aymer\.venvs\orchestration\Scripts\Activate.ps1"

# Insère entre 1 et 10 activités Strava aléatoires dans raw.activites_strava
$env:POSTGRES_HOST="localhost"; $env:POSTGRES_PORT="5433"
$env:POSTGRES_DB="sport_data"; $env:POSTGRES_USER="postgres"; $env:POSTGRES_PASSWORD="postgres"
python scripts/simulate_new_activities.py
```

### 3. Exécuter le flow dans Kestra

Ouvrir [http://localhost:9000](http://localhost:9000) → flow `sport_data / sport_data_pipeline` → bouton **Execute**.

### 4. Vérifier l'état après

```powershell
# Même requête — staging et gold doivent refléter les nouvelles activités, watermark mis à jour
docker exec sport_data_postgres psql -U postgres -d sport_data -c "
SELECT
  (SELECT COUNT(*) FROM raw.activites_strava)          AS nb_activites_raw,
  (SELECT COUNT(*) FROM staging.activites_strava)      AS nb_activites_staging,
  (SELECT MAX(nb_activites_annee) FROM gold.eligibilite_bien_etre) AS max_activites_gold,
  (SELECT watermark FROM meta.pipeline_state WHERE file_name = '_strava_watermark') AS watermark;
"

# Historique des runs Kestra
docker exec sport_data_postgres psql -U postgres -d sport_data -c "
SELECT run_at, status, new_activities_count FROM meta.pipeline_runs ORDER BY run_at DESC LIMIT 5;
"
```
