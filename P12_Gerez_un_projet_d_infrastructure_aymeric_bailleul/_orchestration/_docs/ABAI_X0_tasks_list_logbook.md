# P12 – Liste des tâches et journal de bord

**Auteur :** Aymeric Bailleul
**Formation :** Data Engineer – OpenClassrooms
**Période :** 10/03/2026 → 11/04/2026

---

## Choix d'architecture retenus

| Composant | Outil retenu | Justification |
|---|---|---|
| Base de données | PostgreSQL via Docker | Simule un vrai environnement de production |
| Contrôle des accès | Rôles PostgreSQL (role_pipeline, role_analytics, role_rh_admin) | Principe du moindre privilège, conformité RGPD |
| Calcul des distances | Google Maps API (+ fallback haversine si clé absente) | Distances routières réelles, plus précis pour la règle métier |
| Notifications Slack | Webhooks HTTP réels (deux canaux : activités + compte-rendu pipeline) | Répond à l'exigence de Juliette (publication automatique dans le channel Slack) |
| Tests de qualité | pytest (51 tests) + tests génériques dbt | Couverture DB et transformations SQL, cohérent avec les projets précédents |
| Transformations SQL | dbt (staging + gold) | Transformations versionnées et documentées, tests intégrés |
| Orchestration & monitoring | Kestra (UI web, logs, historique d'exécutions) | Orchestre le pipeline de bout en bout, répond au §3.5 de la note de cadrage |
| Visualisation | PowerBI | Requis par Juliette, connexion PostgreSQL |

---

## Rappel des données sources

### Données RH (`data/RAW/Données+RH.xlsx`)

- 161 salariés
- Colonnes : `ID salarié`, `Nom`, `Prénom`, `Date de naissance`, `BU`, `Date d'embauche`, `Salaire brut`, `Type de contrat`, `Nombre de jours de CP`, `Adresse du domicile`, `Moyen de déplacement`

### Données sportives (`data/RAW/Données+Sportive.xlsx`)

- 161 lignes (un enregistrement par salarié)
- Colonnes : `ID salarié`, `Pratique d'un sport`

---

## Rappel des règles métier

### Prime sportive (5 % du salaire brut annuel)

- Condition : le salarié vient au bureau via une activité sportive (vélo, trottinette, course à pied, marche, etc.)
- Validation : la distance domicile-bureau doit être cohérente avec le mode de déplacement déclaré :
  - Marche / Running : maximum 15 km
  - Vélo / Trottinette / Autres : maximum 25 km
- Source : déclaratif RH (`Moyen de déplacement`)

### 5 journées bien-être

- Condition : minimum 15 activités physiques dans l'année (données simulées Strava)
- Source : données Strava simulées + déclaratif google doc (simulé)

### Adresse de l'entreprise

- 1362 Av. des Platanes, 34970 Lattes

---

## Architecture des données

### Choix RGPD : Option B – Privacy by Design

Les fichiers XLSX (données RH et sportives) contiennent des données personnelles (Nom, Prénom, Date de naissance).
Conformément au principe de **minimisation des données** (Art. 5.1.c RGPD) et de **privacy by design** (Art. 25 RGPD) :

- Les XLSX font office de **couche raw** (source de vérité, sur disque, jamais copiés en base)
- Le pipeline lit les XLSX, anonymise et nettoie en mémoire, puis insère directement dans **staging**
- Seules les données Strava (simulées, sans données personnelles) transitent par le schéma **raw** en base
- Les identités nominatives (Nom, Prénom, Date de naissance) sont stockées dans le schéma **rh_prive**,
  accessible uniquement via `role_rh_admin` (principe du moindre privilège)
- `staging.employes` ne contient que les 8 colonnes anonymisées
- Les notifications Slack utilisent les prénoms/noms via une jointure `rh_prive.identites` avec connexion dédiée

```
Sources (couche raw = disque)
├── Données+RH.xlsx          → identités (rh_prive.identites) + anonymisé → staging.employes
├── Données+Sportive.xlsx    → lu à la volée, nettoyé, inséré dans staging.pratiques_declarees
└── Simulation Strava        → raw.activites_strava (pas de données personnelles)

                ↓

PostgreSQL (Docker)
├── schema rh_prive  : identites (Nom, Prénom, DDN) — role_rh_admin uniquement
├── schema raw       : uniquement activites_strava (données simulées)
├── schema staging   : employes (8 col anonymisées) + pratiques_declarees + activites_strava
└── schema gold      : tables métier calculées
    ├── eligibilite_prime
    ├── eligibilite_bien_etre
    └── impact_financier

Droits PostgreSQL
├── role_pipeline  : lecture/écriture raw + staging, lecture gold
├── role_analytics : lecture seule gold (PowerBI, analyst)
└── role_rh_admin  : hérite pipeline + accès exclusif rh_prive

                ↓

Tests qualité (pytest)

                ↓

Notifications Slack nominatives (Prénom + Nom via role_rh_admin)

                ↓

PowerBI (connexion role_analytics → gold uniquement)
```

---

## Structure du projet

### `_projet/` — POC initial (pipeline Python)

```
_projet/
├── src/
│   ├── config.py
│   ├── db/{init_db.py, connexion.py}
│   ├── ingestion/{load_rh.py, load_sport.py}
│   ├── simulation/generate_strava.py
│   ├── transformation/{staging.py, distances.py, gold.py}
│   ├── notifications/mock_slack.py      # Export JSON local (Phases 1-7)
│   └── main.py
├── tests/{conftest.py, test_*.py}       # 51 tests pytest
├── .env.example
├── pyproject.toml
└── README.md
```

### `_orchestration/` — Couche orchestration Kestra + dbt (Phase 8)

```
_orchestration/
├── _docs/
│   ├── ABAI_X0_tasks_list_logbook.md   # Ce fichier
│   ├── ABAI_X1_contexte.md
│   └── ABAI_X2_note_cadrage.md
├── analyses/
│   └── ABAI_P12_analyse_exploratoire_data.ipynb
├── data/
│   └── RAW/                             # Données+RH.xlsx, Données+Sportive.xlsx (gitignorés)
├── dbt/
│   ├── profiles.yml                     # Profil de connexion dbt (pointe vers PostgreSQL)
│   └── sport_data/                      # Projet dbt
│       ├── dbt_project.yml
│       ├── macros/
│       │   └── generate_schema_name.sql # Override du schéma cible
│       └── models/
│           ├── sources.yml              # Déclaration des sources (raw + staging)
│           ├── staging/
│           │   ├── schema.yml           # Tests + documentation modèles staging
│           │   └── stg_activites_strava.sql
│           └── gold/
│               ├── schema.yml           # Tests + documentation modèles gold
│               ├── eligibilite_prime.sql
│               ├── eligibilite_bien_etre.sql
│               └── impact_financier.sql
├── flows/
│   └── sport_data_pipeline.yml          # Flow Kestra (révision 5, 8 tâches)
├── scripts/                             # Scripts Python exécutés par Kestra
│   ├── check_changes.py                 # Détection nouvelles activités (watermark)
│   ├── reload_rh.py                     # Réingestion conditionnelle XLSX RH
│   ├── reload_sport.py                  # Réingestion conditionnelle XLSX Sport
│   ├── recalculate_distances.py         # Mise à jour staging.cache_distances via Google Maps API
│   ├── notify_slack_activities.py       # Envoi HTTP Slack nominatif par activité
│   └── simulate_new_activities.py       # Injection manuelle d'activités Strava (dev)
├── src/
│   ├── db/{init_db.py, connexion.py}
│   ├── ingestion/{load_rh.py, load_sport.py}
│   ├── simulation/generate_strava.py
│   └── transformation/{staging.py, distances.py, gold.py}
├── tests/
├── docker-compose.yml                   # 5 services : postgres, kestra, kestra-setup, dbt-docs-perms, dbt-docs
├── kestra.Dockerfile                    # Image Kestra custom (Python 3.12 + dbt-postgres)
├── postgres.Dockerfile                  # Image PostgreSQL custom (init + extensions)
├── init-db.sql                          # Script SQL d'initialisation (schémas, rôles, tables)
├── main.py                              # Point d'entrée local (équivalent de _projet/src/main.py)
├── init.ps1                             # Réinitialisation complète en une commande
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Liste des tâches

---

### Phase 0 – Initialisation du projet

- [X] Créer l'environnement virtuel avec uv (Python 3.14)
- [X] Configurer `pyproject.toml` pour uv
- [X] Lire et comprendre le contexte et la note de cadrage
- [X] Explorer les données RAW
- [X] Définir l'architecture et les choix techniques
- [X] Créer ce fichier de suivi (`ABAI_X0_tasks_list_logbook.md`)
- [X] Créer le `docker-compose.yml` pour PostgreSQL
- [X] Créer le notebook d'analyse exploratoire (`analyses/ABAI_P12_analyse_exploratoire_data.ipynb`)
  - [X] Chargement et aperçu des données RH (161 salariés, 11 colonnes) et Sport (161 lignes, 2 colonnes)
  - [X] Structure, types, statistiques descriptives
  - [X] Analyse des valeurs manquantes : 66 NaN (41 %) dans « Pratique d'un sport »
  - [X] Détection des doublons : aucun
  - [X] Distributions numériques (salaire : 25 570 – 74 990, CP : 25 – 29)
  - [X] Distributions catégorielles (5 BU, 4 modes de déplacement, 15 sports)
  - [X] Analyse croisée RH x Sport
  - [X] Détection valeurs aberrantes (IQR) : aucune
  - [X] Nettoyage : types, NaN → « Non déclaré », standardisation chaînes
  - [X] Anonymisation RGPD : suppression Nom, Prénom, Date de naissance
  - [X] Sélection des 8 colonnes utiles au cas d'usage

---

### Phase 1 – Infrastructure PostgreSQL

- [X] Lancer le conteneur PostgreSQL via Docker Compose (port 5433, postgres:16-alpine)
- [X] Créer les schémas `raw`, `staging`, `gold`, `rh_prive`
- [X] Créer la table du schéma `raw` (uniquement données simulées, aucune donnée personnelle) :
  - [X] `raw.activites_strava` — 7 colonnes : `id_activite`, `id_salarie`, `date_debut`, `type_sport`, `distance_m`, `duree_s`, `commentaire`
- [X] Créer les tables du schéma `staging` (premier niveau en base, anonymisé RGPD + nettoyé) :
  - [X] `staging.employes` — 8 colonnes anonymisées (sans Nom, Prénom, DDN)
  - [X] `staging.pratiques_declarees` — 2 colonnes : `id_salarie`, `pratique_sport`
  - [X] `staging.activites_strava` — 7 colonnes : idem raw (données simulées nettoyées)
- [X] Créer les tables du schéma `gold` :
  - [X] `gold.eligibilite_prime`
  - [X] `gold.eligibilite_bien_etre`
  - [X] `gold.impact_financier`
- [X] Créer la table du schéma `rh_prive` (accès restreint RGPD) :
  - [X] `rh_prive.identites` — `id_salarie`, `nom`, `prenom`, `date_naissance` (FK vers staging.employes)
  - [X] Vue `rh_prive.vue_primes_nominatives` (jointure identités + employes + gold)
- [X] Configurer les rôles PostgreSQL (créés automatiquement par `init_db.py --reset`) :
  - [X] `role_pipeline` : lecture/écriture raw + staging, lecture gold
  - [X] `role_analytics` : lecture seule gold (PowerBI)
  - [X] `role_rh_admin` : hérite pipeline + accès exclusif rh_prive
- [X] Écrire `src/db/connexion.py` (connexion via `.env`, support multi-rôles : `role=None|"rh_admin"|"analytics"|"pipeline"`)
- [X] Écrire `src/db/init_db.py` (création automatique des schémas, tables et rôles, option `--reset`)

---

### Phase 2 – Ingestion des données sources

- [X] Écrire `src/ingestion/load_rh.py` :
  - [X] Lire le XLSX et extraire les identités (Nom, Prénom, DDN) avant anonymisation
  - [X] Insérer les identités dans `rh_prive.identites` (161 lignes)
  - [X] Supprimer les colonnes nominatives en mémoire et insérer les 8 colonnes anonymisées dans `staging.employes` (161 lignes)
  - [X] TRUNCATE multi-tables (rh_prive.identites + staging.employes) pour l'idempotence avec respect de la FK
- [X] Écrire `src/ingestion/load_sport.py` (XLSX → lecture + nettoyage NaN + correction typo "Runing" + insertion dans `staging.pratiques_declarees`, 2 colonnes)
- [X] Vérifier le chargement (161 employés, 161 pratiques, 161 identités, jointure 161/161, RGPD OK)

---

### Phase 3 – Simulation des données Strava

- [X] Définir les types de sport disponibles (15 sports avec paramètres réalistes : distance, vitesse, commentaires)
- [X] Écrire `src/simulation/generate_strava.py` :
  - [X] Générer 2 256 activités sur les 12 derniers mois (seed 42)
  - [X] Basé sur les 95 salariés ayant une pratique déclarée (hors "Non déclaré")
  - [X] Colonnes : `id_activite`, `id_salarie`, `date_debut`, `type_sport`, `distance_m`, `duree_s`, `commentaire`
  - [X] Respect des cohérences (0 activité invalide, dates valides, 5-40 activités/salarié)
  - [X] Option `--seed` pour reproductibilité
- [X] Charger les données générées dans `raw.activites_strava` (TRUNCATE + INSERT)

---

### Phase 4 – Pipeline ETL (Staging → Gold)

- [X] Écrire `src/transformation/staging.py` :
  - [X] Nettoyage des activités Strava : raw → staging (types, cohérence dates/distances)
- [X] Écrire `src/transformation/distances.py` :
  - [X] Appel Google Maps API pour calculer la distance domicile-bureau
  - [X] Fallback haversine si la clé API est absente
  - [X] Mise en cache des résultats en base (éviter les appels répétés)
  - [X] Application des règles métier (15 km marche/running, 25 km vélo/trottinette)
  - [X] Flaggage des anomalies de déclaration
- [X] Écrire `src/transformation/gold.py` :
  - [X] Calcul de l'éligibilité à la prime sportive
  - [X] Calcul de l'éligibilité aux 5 journées bien-être (>= 15 activités/an)
  - [X] Calcul de l'impact financier (prime = salaire brut * 5 %)
  - [X] Alimentation des tables `gold.*`

---

### Phase 5 – Tests de qualité (pytest)

- [X] Écrire `tests/conftest.py` (fixtures : connexion DB, jeux de données de test, fixture `identites`)
- [X] Écrire `tests/test_distances.py` (10 tests : haversine, seuils, éligibilité, adresse invalide)
- [X] Écrire `tests/test_simulation.py` (9 tests : distances, durées, dates, IDs, sports, volumes)
- [X] Écrire `tests/test_staging.py` (12 tests : doublons, salaires, dates, complétude, pratiques)
- [X] Écrire `tests/test_gold.py` (9 tests : primes 5%, bien-être, impact financier agrégé)
- [X] Écrire `tests/test_rh_prive.py` (9 tests : volume identités, nulls, unicité, cohérence FK, Privacy by Design, droits role_analytics, vue nominative)
- [X] Vérifier que tous les tests passent (`uv run pytest` : 51 tests, 0 échec)

---

### Phase 6 – Notifications Slack

- [X] Écrire `src/notifications/mock_slack.py` :
  - [X] Joindre `rh_prive.identites` via connexion `role_rh_admin` pour obtenir Prénom + Nom
  - [X] Générer un message de félicitation nominatif pour chaque activité (format Juliette)
  - [X] 15 sports x 2-3 templates (~35 messages distincts), placeholders `{prenom}` et `{nom}`
  - [X] Exporter les messages dans `data/exports/slack_messages.json` (champs `prenom`, `nom` inclus)
  - [X] CLI avec option `--limit`
- [X] Intégrer l’appel au mock dans le pipeline principal (Phase 7)

---

### Phase 7 – Pipeline principal

- [X] Écrire `src/config.py` (constantes : adresse entreprise, seuils distances, taux prime, chemins, RGPD, sports valides)
- [X] Écrire `src/main.py` :
  - [X] Orchestrer les 7 étapes dans l’ordre : init_db → ingestion RH → ingestion sport → simulation Strava → staging → gold → mock Slack
  - [X] Logging clair de chaque étape (module `logging`)
  - [X] Gestion des erreurs (try/except avec messages explicites, arrêt en cas d’erreur)
  - [X] Options CLI : `--reset`, `--seed`, `--step N`, `--dry-run`, `--skip-api`
- [X] Tester le pipeline de bout en bout (7/7 étapes OK, 59.8s, 42 tests pytest OK)

---

### Phase 8 – Orchestration (Kestra + dbt)

- [X] Restructurer le projet : dossier `_orchestration/` séparé de `_projet/`, chacun autosuffisant
- [X] Créer le projet dbt `dbt/sport_data/` (modèles staging + gold + macros + tests + docs)
  - [X] Sources déclarées : `raw.activites_strava`, `staging.employes`, `staging.pratiques_declarees`, `staging.cache_distances`
  - [X] Modèle staging : `stg_activites_strava` (filtre types invalides, salariés inactifs, dates hors période)
  - [X] Modèles gold : `eligibilite_prime`, `eligibilite_bien_etre`, `impact_financier`
  - [X] Tests génériques dbt (not_null, unique, accepted_values) + documentation YAML
- [X] Écrire `kestra.Dockerfile` (extend `kestra:latest`, ajout Python 3.12, dbt-postgres, dépendances pip)
- [X] Créer `docker-compose.yml` multi-services :
  - [X] `postgres` (port 5433, image custom `sport_data_postgres:local`)
  - [X] `kestra` (port 9000, image custom `sport_data_kestra:local`)
  - [X] `kestra-setup` (import automatique du flow + création des secrets Kestra via API)
  - [X] `dbt-docs-perms` (alpine, `chmod -R 777` sur volume `sport_data_dbt_docs` — service init)
  - [X] `dbt-docs` (nginx:alpine, port 4080, sert la documentation dbt générée)
- [X] Écrire le flow Kestra `flows/sport_data_pipeline.yml` (révision 5) :
  - [X] `check_changes` : détecte les nouvelles activités Strava via watermark
  - [X] `reload_rh` / `reload_sport` : réingestion conditionnelle si modifications détectées
  - [X] `dbt_run` : exécution des modèles dbt (staging + gold)
  - [X] `dbt_test` : tests dbt génériques
  - [X] `dbt_docs_generate` : génération de la doc dbt dans le volume partagé
  - [X] `recalculate_distances` : calcul/mise à jour de `staging.cache_distances` via Google Maps API (avant dbt)
  - [X] `notify_slack_activities` : messages nominatifs par activité (webhook 1)
  - [X] `update_strava_watermark` / `update_watermark` : mise à jour du watermark pipeline
  - [X] `notify_slack_success` / `notify_slack_failure` : compte-rendu pipeline (webhook 2)
- [X] Écrire `scripts/recalculate_distances.py` :
  - [X] Script standalone (sans import `src/`) exécuté par Kestra avant `dbt run`
  - [X] Connexion PostgreSQL via variables d'environnement (POSTGRES_HOST/PORT/DB/USER/PASSWORD)
  - [X] Crée `staging.cache_distances` si elle n'existe pas (`CREATE TABLE IF NOT EXISTS`)
  - [X] Ne calcule que les adresses absentes du cache (optimisation : évite les appels API redondants)
  - [X] Appel Google Maps Distance Matrix → fallback haversine si échec ou clé absente
  - [X] Sauvegarde en cache avec `ON CONFLICT DO UPDATE`
  - [X] Secret `GOOGLE_MAPS_API_KEY` injecté via mécanisme Kestra (`SECRET_GOOGLE_MAPS_API_KEY` base64 dans docker-compose)
- [X] Écrire `scripts/notify_slack_activities.py` :
  - [X] Lecture des nouvelles activités depuis `raw.activites_strava` (filtre sur `inserted_at > watermark`)
  - [X] JOIN `rh_prive.identites` pour nom/prénom nominatifs (connexion superuser)
  - [X] 15 sports × 2-3 templates (~35 messages distincts), envoi HTTP POST par activité
- [X] Écrire `scripts/simulate_new_activities.py` : injection manuelle d'activités Strava, chargement `.env` via python-dotenv
- [X] Écrire `init.ps1` : réinitialisation complète en une commande (reset DB, import flow, dbt seed)
- [X] Configurer deux webhooks Slack :
  - [X] `SLACK_WEBHOOK` → messages nominatifs par activité (`notify_slack_activities.py`)
  - [X] `SLACK_WEBHOOK_INFO` → compte-rendu pipeline (`notify_slack_success/failure` dans le flow)
- [X] Déplacer `data/RAW/` dans `_orchestration/` : projet autosuffisant, chemins `.env` / `.env.example` / `README.md` mis à jour

---

### Phase 9 – Dashboard PowerBI

- [X] Connecter PowerBI à PostgreSQL (connecteur natif Npgsql, port 5433, mode DirectQuery)
- [X] Créer les visuels :
  - [X] KPIs Interne publics :
    - [X] Camembert sportifs / non-sportifs (59 % / 41 %)
    - [X] Top 10 sports déclarés (histogramme horizontal)
    - [X] Top 5 sportifs (classement par nb activités)
    - [X] Taux de participation aux activités (3 derniers mois via données Strava)
    - [X] Carte des salariés (adresse domicile → ville/département, sport pratiqué, nb activités)
  - [X] KPIs RH :
      - [X] Type de mobilité (histogramme : nb salariés par mode de transport)
      - [X] Table salariés avec distance domicile-bureau + temps de trajet estimé
      - [X] Total jours bien-être gagnés (carte KPI)
      - [X] Nb salariés éligibles bien-être (carte KPI)
      - [X] Prime moyenne par salarié éligible (carte KPI)
      - [X] Total primes sport (carte KPI)
- [X] Exporter le rapport `.pbix`

---

### Phase 10 – Documentation et soutenance

- [ ] Mettre à jour le README avec les instructions complètes d'installation et d'exécution
- [ ] Créer le support de présentation (architecture, pipeline, choix techniques)
- [ ] Préparer la démonstration live (pipeline complet + PowerBI)
- [ ] Relecture finale du code (ruff, black)

---

## Journal de bord

| Date | Action |
|---|---|
| 26/02/2026 | Initialisation du projet : uv, pyproject.toml, README, exploration des données RAW, choix d'architecture |
| 26/02/2026 | Création du `docker-compose.yml`, lancement du conteneur PostgreSQL (port 5433) |
| 26/02/2026 | Configuration Google Maps API, création `.env` / `.env.example` / `.gitignore` |
| 27/02/2026 | Passage de Python 3.14 à 3.13 (incompatibilité pandas `gettz`) |
| 27/02/2026 | Création et exécution du notebook d'analyse exploratoire (16 sections, 20 cellules de code) |
| 27/02/2026 | Constats principaux : 161 salariés, 66 NaN sport (41 %), 0 doublon, 0 aberrant, typo « Runing » |
| 27/02/2026 | Nettoyage : types corrigés, NaN → « Non déclaré », standardisation chaînes |
| 27/02/2026 | Anonymisation RGPD : suppression Nom, Prénom, Date de naissance ; sélection des 8+2 colonnes utiles |
| 27/02/2026 | Export des CSV nettoyés : `rh_clean.csv` (161×8), `sport_clean.csv` (161×2) |
| 03/03/2026 | Choix architecture Option B (Privacy by Design) : XLSX = couche raw sur disque (jamais en base), staging = 1er niveau DB anonymisé, raw DB = Strava uniquement, Slack = lecture XLSX à la volée |
| 03/03/2026 | Phase 1 terminée : `src/db/connexion.py` (connexion PostgreSQL multi-rôles via .env), `src/db/init_db.py` (4 schémas, 8 tables, 3 rôles PostgreSQL). Ajout de psycopg2-binary et python-dotenv aux dépendances. Vérification OK (PostgreSQL 16.12) |
| 03/03/2026 | Phase 2 terminée : `src/ingestion/load_rh.py` (XLSX → identités dans rh_prive.identites + anonymisation + staging.employes, 161 lignes), `src/ingestion/load_sport.py` (XLSX → nettoyage NaN + typo → staging.pratiques_declarees, 161 lignes). Cohérence IDs vérifiée (jointure 161/161) |
| 03/03/2026 | Phase 3 terminée : `src/simulation/generate_strava.py` – 2 256 activités générées pour 95 sportifs, 15 sports, période 03/2025-03/2026, seed 42. 0 activité invalide. Insérées dans raw.activites_strava |
| 03/03/2026 | Phase 4 terminée : pipeline ETL complet (staging → gold). `staging.py` : 2 256 activités raw → staging (0 rejetée). `distances.py` : 159 adresses via Google Maps API, cache en base (`staging.cache_distances`), règles métier appliquées (15 km marche, 25 km vélo). `gold.py` : 68 éligibles prime (172 482,50 EUR), 67 éligibles bien-être (335 jours), 5 départements agrégés dans `gold.impact_financier` |
| 03/03/2026 | Phase 5 terminée : 42 tests pytest, 0 échec (0.97s). `conftest.py` (fixtures DB session-scoped), `test_distances.py` (10 tests : haversine, seuils, éligibilité, adresse invalide), `test_simulation.py` (9 tests : distances, durées, dates, IDs, sports, volumes), `test_staging.py` (12 tests : doublons, salaires, dates, complétude, pratiques), `test_gold.py` (9 tests : primes 5%, bien-être, impact financier agrégé). Configuration `pythonpath` ajoutée au `pyproject.toml` |
| 04/03/2026 | Phase 6 terminée : `src/notifications/mock_slack.py` – 2 256 messages Slack nominatifs générés depuis staging.activites_strava avec jointure rh_prive.identites (role_rh_admin). 15 sports × 2-3 templates (~35 messages distincts, placeholders {prenom}/{nom}). Export JSON dans `data/exports/slack_messages.json` (champs prenom + nom inclus). CLI avec option `--limit` |
| 04/03/2026 | Tests qualité : 51 tests pytest, 0 échec. `test_rh_prive.py` (9 tests : volume, nulls, unicité, cohérence FK, Privacy by Design, droits role_analytics refusés, vue nominative). `conftest.py` enrichi avec fixture `identites` |
| 04/03/2026 | Review code : corrections coquilles (3 commentaires trompeurs, 2 imports inutiles), ajout commentaires explicatifs sur 6 parties complexes (haversine, cascade distances, CTE gold, seuil 395j, génération dates/durées). 42 tests OK |
| 04/03/2026 | Phase 7 terminée : `src/config.py` (constantes centralisées : chemins, seuils, taux, RGPD, sports). `src/main.py` (orchestrateur 7 étapes, CLI : `--reset`, `--seed`, `--step N`, `--dry-run`, `--skip-api`). Pipeline complet exécuté : 7/7 OK, 51 tests pytest OK |
| 11/03/2026 | Implémentation schéma `rh_prive` + 3 rôles PostgreSQL (role_pipeline, role_analytics, role_rh_admin). `init_db.py` : création automatique des rôles et droits au `--reset`. `connexion.py` : support multi-rôles via paramètre `role=`. `load_rh.py` : insertion des identités dans rh_prive.identites avant anonymisation. `mock_slack.py` : messages nominatifs via jointure rh_prive (role_rh_admin). 51/51 tests OK |
| 12/03/2026 | Projet dbt `sport_data` créé : modèles staging (3) + gold (3), sources YAML, macros, tests génériques (not_null, unique, accepted_values), documentation |
| 12/03/2026 | Phase 8 – Orchestration terminée : `docker-compose.yml` (5 services : postgres, kestra, kestra-setup, dbt-docs-perms, dbt-docs), `kestra.Dockerfile` (Python 3.12 + dbt-postgres), flow `sport_data_pipeline.yml` (8 tâches). Pipeline orchestré de bout en bout dans Kestra |
| 12/03/2026 | Fixes pipeline : colonnes `raw.activites_strava` corrigées dans `simulate_new_activities.py`, watermark géré par le flow (pas par le script), types sports alignés avec whitelist dbt, `docker-compose.yml` sans valeurs par défaut (erreur explicite si `.env` manquant) |
| 12/03/2026 | `simulate_new_activities.py` : chargement automatique de `.env` via python-dotenv |
| 12/03/2026 | Notifications Slack réelles : double webhook — webhook 1 (`SLACK_WEBHOOK`) → `scripts/notify_slack_activities.py` (messages nominatifs par activité, 15 sports × 2-3 templates, ~35 messages distincts) ; webhook 2 (`SLACK_WEBHOOK_INFO`) → `notify_slack_success/failure` dans le flow (compte-rendu pipeline). Flow révision 4 |
| 12/03/2026 | Fix `notify_slack_activities` : JOIN corrigé (`staging.employes` → `rh_prive.identites`) pour récupérer nom/prénom réels |
| 12/03/2026 | Génération docs dbt dans le flow (`dbt_docs_generate` après `dbt_test`) + service nginx `dbt-docs` port 4080, volume partagé `sport_data_dbt_docs`. Flow révision 5 |
| 12/03/2026 | Fix permissions volume `dbt_docs` : service init `dbt-docs-perms` (alpine, `chmod -R 777`) ajouté au `docker-compose.yml`, kestra en dépend. Correction port 8082 → 4080 dans README |
| 13/03/2026 | `data/RAW/` déplacé de `_projet/data/RAW` vers `_orchestration/data/RAW` — `_orchestration` devient autosuffisant. `.env`, `.env.example`, `README.md` mis à jour |
| 13/03/2026 | Intégration Google Maps API dans le flow Kestra : `scripts/recalculate_distances.py` créé (script standalone, cache `staging.cache_distances`, fallback haversine). `kestra.Dockerfile` : ajout de `requests`. `docker-compose.yml` : ajout `SECRET_GOOGLE_MAPS_API_KEY` (base64) + logique POST→PUT pour import flow idempotent. Flow `sport_data_pipeline.yml` : nouvelle étape `recalculate_distances` avant `dbt_run`. Révision 2. |
| 13/03/2026 | Dashboard PowerBI : connexion PostgreSQL (Npgsql, port 5433, role_analytics), visuels créés (camembert sportifs/non-sportifs, top 10 sports, top 5 sportifs avec trophées, carte, KPIs RH, taux participation, impact financier). Requêtes SQL DirectQuery sur gold.* + staging.* |
| 13/03/2026 | KPIs RH enrichis : table salariés avec distance + temps de trajet estimé (vitesses par mode de transport), histogramme type de mobilité, cartes KPI bien-être (total jours, nb éligibles), cartes KPI primes (prime moy., total primes). Requêtes SQL sur `staging.cache_distances`, `gold.eligibilite_bien_etre`, `gold.eligibilite_prime` |
