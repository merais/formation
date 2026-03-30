# P12 – Liste des tâches et journal de bord – Projet dbt

**Auteur :** Aymeric Bailleul
**Formation :** Data Engineer – OpenClassrooms
**Période :** 10/03/2026 → 11/04/2026

> Ce projet (`_projet_dbt`) reconstruit la couche de transformation du pipeline P12 en SQL pur avec **dbt**.
> Il s'appuie sur la même instance PostgreSQL que `_projet` (port 5433, DB `sport_data`) :
> les schémas `raw` et `staging` sont alimentés par `_projet`, dbt prend en charge la transformation vers `gold`.

---

## Choix d'architecture retenus

| Composant | Outil retenu | Justification |
|---|---|---|
| Base de données | PostgreSQL via Docker | Même instance que `_projet` (port 5433, DB `sport_data`) |
| Calcul des distances | `staging.cache_distances` (alimenté par `_projet`) | Distances déjà calculées par Google Maps / haversine, réutilisées en SQL |
| Transformation SQL | dbt-core 1.11.7 + dbt-postgres 1.10.0 | DAG automatique, tests intégrés, SQL lisible, reproductible |
| Tests de qualité | dbt test (37 tests) | Tests natifs dbt : unique, not_null, accepted_values sur modèles et sources |
| Orchestration | `main.py` Python (subprocess dbt) | Lance `dbt run` puis `dbt test` depuis un script unique |
| Visualisation | PowerBI | Connexion PostgreSQL → schéma `gold` (même que `_projet`) |

---

## Rappel des données sources

### Données RH (`data/RAW/Données+RH.xlsx`)

- 161 salariés
- Colonnes : `ID salarié`, `Nom`, `Prénom`, `Date de naissance`, `BU`, `Date d'embauche`, `Salaire brut`, `Type de contrat`, `Nombre de jours de CP`, `Adresse du domicile`, `Moyen de déplacement`

### Données sportives (`data/RAW/Données+Sportive.xlsx`)

- 1 000 lignes
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

### Choix RGPD : Option B – Privacy by Design (hérité de `_projet`)

Les données nominatives (Nom, Prénom, DDN) sont gérées dans `_projet` :
- Anonymisées à l'ingestion XLSX → `staging.employes` (8 colonnes sans données personnelles)
- Stockées dans `rh_prive.identites` (accès restreint au rôle `role_rh_admin`)

dbt ne touche pas à `rh_prive`. Il lit uniquement les schémas `raw`, `staging` (anonymisés) et écrit dans `gold`.

```
_projet (Python ETL – pipeline source)
├── Données+RH.xlsx          → anonymisé → staging.employes (8 col)
│                                        → rh_prive.identites (Nom/Prénom/DDN – accès restreint)
├── Données+Sportive.xlsx    → staging.pratiques_declarees
├── Simulation Strava        → raw.activites_strava
└── distances.py             → staging.cache_distances (Google Maps / haversine)

                ↓  (même instance PostgreSQL – port 5433)

_projet_dbt (dbt – transformation SQL)
├── SOURCE raw     : raw.activites_strava
├── SOURCE staging : employes, pratiques_declarees, cache_distances
│
├── MODEL staging/stg_activites_strava  →  staging.activites_strava (nettoyage 5 filtres)
├── MODEL gold/eligibilite_prime        →  gold.eligibilite_prime   (règle distance + 5%)
├── MODEL gold/eligibilite_bien_etre    →  gold.eligibilite_bien_etre (>= 15 activités)
└── MODEL gold/impact_financier         →  gold.impact_financier    (agrégat département)

                ↓

dbt test (37 tests : unique, not_null, accepted_values)

                ↓

PowerBI (connexion PostgreSQL → gold uniquement)
```

---

## Structure cible du projet

```
_projet_dbt/
├── _docs/
│   ├── ABAI_X0_tasks_list_logbook.md   # Ce fichier
│   ├── ABAI_X1_note_cadrage.md
│   └── ABAI_X2_contexte.md
├── data/
│   └── RAW/                             # Fichiers sources (identiques à _projet)
├── sport_data/                          # Projet dbt (dbt init sport_data)
│   ├── dbt_project.yml                  # Config : profil, chemins, schémas cibles
│   ├── macros/
│   │   └── generate_schema_name.sql     # Surcharge pour schémas exacts (sans préfixe)
│   ├── models/
│   │   ├── sources.yml                  # Déclaration raw.* et staging.* comme sources
│   │   ├── staging/
│   │   │   ├── stg_activites_strava.sql # Nettoyage raw → staging (5 filtres)
│   │   │   └── schema.yml               # Tests dbt du modèle staging
│   │   └── gold/
│   │       ├── eligibilite_prime.sql    # Règle distance (cache) + prime 5%
│   │       ├── eligibilite_bien_etre.sql# Seuil >= 15 activités → 5 jours
│   │       ├── impact_financier.sql     # Agrégat FULL OUTER JOIN par département
│   │       └── schema.yml               # Tests dbt des modèles gold
│   ├── analyses/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
├── profiles.yml                         # Connexion PostgreSQL (port 5433) – non versionné
├── main.py                              # Wrapper : dbt run + dbt test
├── pyproject.toml                       # Python 3.12, dbt-postgres, python-dotenv
├── .env                                 # Variables d'environnement – non versionné
├── .python-version                      # 3.12
└── README.md
```

> **Venv** : créé hors Google Drive (`C:\Users\aymer\.venvs\projet_dbt`) pour contourner
> le blocage Windows sur les exécutables `.exe` dans les dossiers synchronisés.

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
- [X] Créer les schémas `raw`, `staging`, `gold`
- [X] Créer la table du schéma `raw` (uniquement données simulées, aucune donnée personnelle) :
  - [X] `raw.activites_strava` — 7 colonnes : `id_activite`, `id_salarie`, `date_debut`, `type_sport`, `distance_m`, `duree_s`, `commentaire`
- [X] Créer les tables du schéma `staging` (premier niveau en base, anonymisé RGPD + nettoyé) :
  - [X] `staging.employes` — 8 colonnes : `id_salarie`, `departement`, `date_embauche`, `salaire_brut`, `type_contrat`, `nb_jours_cp`, `adresse_domicile`, `moyen_deplacement` (XLSX lu + anonymisé à la volée)
  - [X] `staging.pratiques_declarees` — 2 colonnes : `id_salarie`, `pratique_sport` (XLSX lu + NaN → "Non déclaré")
  - [X] `staging.activites_strava` — 7 colonnes : idem raw (données simulées nettoyées)
- [X] Créer les tables du schéma `gold` :
  - [X] `gold.eligibilite_prime` — `id_salarie`, `departement`, `moyen_deplacement`, `adresse_domicile`, `distance_km`, `seuil_km`, `est_eligible`, `montant_prime`
  - [X] `gold.eligibilite_bien_etre` — `id_salarie`, `departement`, `nb_activites_annee`, `est_eligible`, `nb_jours_bien_etre`
  - [X] `gold.impact_financier` — `departement`, `nb_primes`, `total_primes`, `nb_bien_etre`, `total_jours_bien_etre`
- [X] Écrire `src/db/connexion.py` (connexion via `.env`, psycopg2-binary + python-dotenv)
- [X] Écrire `src/db/init_db.py` (création automatique des schémas et tables, option `--reset`)

---

### Phase 2 – Ingestion des données sources

- [X] Écrire `src/ingestion/load_rh.py` (XLSX → lecture + anonymisation + insertion dans `staging.employes`, 8 colonnes)
- [X] Écrire `src/ingestion/load_sport.py` (XLSX → lecture + nettoyage NaN + correction typo "Runing" + insertion dans `staging.pratiques_declarees`, 2 colonnes)
- [X] Vérifier le chargement (161 employes, 161 pratiques, jointure 161/161, RGPD OK)

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

- [X] Écrire `tests/conftest.py` (fixtures : connexion DB, jeux de données de test)
- [X] Écrire `tests/test_distances.py` :
  - [X] Distance négative → erreur
  - [X] Distance incohérente avec le moyen de déplacement → flaggée
  - [X] Adresse invalide → gestion propre de l'erreur
- [X] Écrire `tests/test_simulation.py` :
  - [X] Distances >= 0
  - [X] Durées >= 0
  - [X] Dates dans les 12 derniers mois
  - [X] IDs salariés tous présents dans la table `employes`
  - [X] Types de sport valides (liste fermée)
- [X] Écrire `tests/test_staging.py` :
  - [X] Pas de doublon sur `ID salarié`
  - [X] Salaires positifs
  - [X] Dates d'embauche antérieures à aujourd'hui
- [X] Écrire `tests/test_gold.py` :
  - [X] Le montant de la prime = salaire brut * 0.05
  - [X] Aucun salarié non éligible ne reçoit la prime
  - [X] Nombre de jours bien-être = 5 si >= 15 activités, sinon 0
- [X] Vérifier que tous les tests passent (`uv run pytest`)

---

### Phase 6 – Notifications Slack (mock)

- [X] Écrire `src/notifications/mock_slack.py` :
  - [X] Générer un message pour chaque activité sportive (format Juliette)
  - [X] Utiliser uniquement l'ID salarié (pas de Nom/Prénom – conformité RGPD)
  - [X] Logger les messages dans `data/exports/slack_messages.json`
  - [X] Exemples de messages :
    - "Bravo salarié ID [X] ! Tu viens de courir [X] km en [Y] min !"
    - "Magnifique salarié ID [X] ! Une randonnée de [X] km terminée !"
- [X] Intégrer l’appel au mock dans le pipeline principal (Phase 7)

---

### Phase 7 – Pipeline principal (Manuel)

- [X] Écrire `src/config.py` (constantes : adresse entreprise, seuils distances, taux prime, chemins, RGPD, sports valides)
- [X] Écrire `src/main.py` :
  - [X] Orchestrer les 7 étapes dans l’ordre : init_db → ingestion RH → ingestion sport → simulation Strava → staging → gold → mock Slack
  - [X] Logging clair de chaque étape (module `logging`)
  - [X] Gestion des erreurs (try/except avec messages explicites, arrêt en cas d’erreur)
  - [X] Options CLI : `--reset`, `--seed`, `--step N`, `--dry-run`, `--skip-api`
- [X] Tester le pipeline de bout en bout (7/7 étapes OK, 59.8s, 42 tests pytest OK)

---

### Phase 8 – Orchestration pipeline



---

### Phase 9 – Dashboard PowerBI

- [ ] Connecter PowerBI à PostgreSQL (connecteur natif, mode DirectQuery pour le temps réel)
- [ ] Créer les visuels :
  - [ ] Nombre de salariés éligibles à la prime / au bien-être
  - [ ] Montant total des primes par département
  - [ ] Impact financier global
  - [ ] Répartition des types de sport pratiqués
  - [ ] Nombre d'activités par mois (historique 12 mois)
  - [ ] Liste des salariés avec anomalie de déclaration de distance
- [ ] Implémenter le rafraîchissement : permettre le recalcul si les taux changent
- [ ] Exporter le rapport `.pbix`

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
| 03/03/2026 | Phase 1 terminée : `src/db/connexion.py` (connexion PostgreSQL via .env), `src/db/init_db.py` (3 schémas, 7 tables). Ajout de psycopg2-binary et python-dotenv aux dépendances. Vérification OK (PostgreSQL 16.12) |
| 03/03/2026 | Phase 2 terminée : `src/ingestion/load_rh.py` (XLSX → anonymisation → staging.employes, 161 lignes), `src/ingestion/load_sport.py` (XLSX → nettoyage NaN + typo → staging.pratiques_declarees, 161 lignes). Cohérence IDs vérifiée (jointure 161/161) |
| 03/03/2026 | Phase 3 terminée : `src/simulation/generate_strava.py` – 2 256 activités générées pour 95 sportifs, 15 sports, période 03/2025-03/2026, seed 42. 0 activité invalide. Insérées dans raw.activites_strava |
| 03/03/2026 | Phase 4 terminée : pipeline ETL complet (staging → gold). `staging.py` : 2 256 activités raw → staging (0 rejetée). `distances.py` : 159 adresses via Google Maps API, cache en base (`staging.cache_distances`), règles métier appliquées (15 km marche, 25 km vélo). `gold.py` : 68 éligibles prime (172 482,50 EUR), 67 éligibles bien-être (335 jours), 5 départements agrégés dans `gold.impact_financier` |
| 03/03/2026 | Phase 5 terminée : 42 tests pytest, 0 échec (0.97s). `conftest.py` (fixtures DB session-scoped), `test_distances.py` (10 tests : haversine, seuils, éligibilité, adresse invalide), `test_simulation.py` (9 tests : distances, durées, dates, IDs, sports, volumes), `test_staging.py` (12 tests : doublons, salaires, dates, complétude, pratiques), `test_gold.py` (9 tests : primes 5%, bien-être, impact financier agrégé). Configuration `pythonpath` ajoutée au `pyproject.toml` |
| 04/03/2026 | Phase 6 terminée : `src/notifications/mock_slack.py` – 2 256 messages Slack générés depuis staging.activites_strava. 15 sports × 2-3 templates (~35 messages distincts). Export JSON dans `data/exports/slack_messages.json`. Conformité RGPD : uniquement ID salarié (pas de Nom/Prénom). CLI avec option `--limit` |
| 04/03/2026 | Review code : corrections coquilles (3 commentaires trompeurs, 2 imports inutiles), ajout commentaires explicatifs sur 6 parties complexes (haversine, cascade distances, CTE gold, seuil 395j, génération dates/durées). 42 tests OK |
| 04/03/2026 | Phase 7 terminée : `src/config.py` (constantes centralisées : chemins, seuils, taux, RGPD, sports). `src/main.py` (orchestrateur 7 étapes, CLI : `--reset`, `--seed`, `--step N`, `--dry-run`). Pipeline complet exécuté : 7/7 OK, 59.8s. 42 tests pytest OK |
| 09/03/2026 | Ajout option `--skip-api` au pipeline (`main.py`, `gold.py`, `distances.py`). Permet de réutiliser le cache des distances sans appeler l’API Google Maps. Pipeline en 11.4s au lieu de ~60s. README mis à jour |
| 10/03/2026 | Initialisation de `_projet_dbt` : `uv init --no-workspace --name projet-dbt`. Découverte incompatibilité dbt-core 1.11.7 / Python 3.13 (erreur `JSONDecodeError` dans `jsonschema_specifications`). Passage à Python 3.12 |
| 10/03/2026 | Venv créé hors Google Drive : `python -m venv C:\Users\aymer\.venvs\projet_dbt` (Google Drive bloque la création d'exécutables `.exe` dans les dossiers synchronisés). `pip install dbt-postgres python-dotenv` → 55 paquets, dbt-core 1.11.7, dbt-postgres 1.10.0 |
| 11/03/2026 | Phase 1 terminée : `dbt init sport_data --skip-profile-setup`. `profiles.yml` (port 5433, DB sport_data). `macros/generate_schema_name.sql` (schémas exacts sans préfixe). `dbt debug` → `All checks passed!` |
| 11/03/2026 | Phase 2 terminée : `models/sources.yml` – 2 sources déclarées (raw + staging), 4 tables, tests unique/not_null. `dbt compile` : 4 modèles, 0 erreur, 0 warning |
| 11/03/2026 | Phases 3-4 terminées : `stg_activites_strava.sql` (5 filtres qualité), `eligibilite_prime.sql` (seuils 15/25 km + prime 5%), `eligibilite_bien_etre.sql` (seuil >= 15 activités), `impact_financier.sql` (FULL OUTER JOIN). `dbt run` : 4/4 OK en 0.53s (161 salariés, 2 256 activités, 5 départements) |
| 11/03/2026 | Phase 5 terminée : `dbt test` → **37/37 PASS** en 1.00s. Phase 6 : `main.py` wrapper (`dbt run` + `dbt test`). Pipeline end-to-end OK |