# P12 – Liste des tâches et journal de bord

**Auteur :** Aymeric Bailleul
**Formation :** Data Engineer – OpenClassrooms
**Période :** 10/03/2026 → 11/04/2026

---

## Choix d'architecture retenus

| Composant | Outil retenu | Justification |
|---|---|---|
| Base de données | PostgreSQL via Docker | Simule un vrai environnement de production |
| Calcul des distances | Google Maps API (+ fallback haversine si clé absente) | Distances routières réelles, plus précis pour la règle métier |
| Notifications | Mock Slack (log JSON local) | Pas de dépendance externe, suffisant pour le POC |
| Tests de qualité | pytest | Déjà maîtrisé, cohérent avec les projets précédents |
| Orchestration | Scripts Python séquentiels | Suffisant pour un POC, lisible en soutenance |
| Visualisation | PowerBI | Requis par Juliette, connexion PostgreSQL |

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

### Choix RGPD : Option B – Privacy by Design

Les fichiers XLSX (données RH et sportives) contiennent des données personnelles (Nom, Prénom, Date de naissance).
Conformément au principe de **minimisation des données** (Art. 5.1.c RGPD) et de **privacy by design** (Art. 25 RGPD) :

- Les XLSX font office de **couche raw** (source de vérité, sur disque, jamais copiés en base)
- Le pipeline lit les XLSX, anonymise et nettoie en mémoire, puis insère directement dans **staging**
- Seules les données Strava (simulées, sans données personnelles) transitent par le schéma **raw** en base
- Pour les notifications Slack, Nom/Prénom sont lus à la volée depuis le XLSX (jamais stockés en base)

```
Sources (couche raw = disque)
├── Données+RH.xlsx          → lu à la volée, anonymisé, inséré dans staging.employes
├── Données+Sportive.xlsx    → lu à la volée, nettoyé, inséré dans staging.pratiques_declarees
└── Simulation Strava        → raw.activites_strava (pas de données personnelles)

                ↓

PostgreSQL (Docker)
├── schema raw       : uniquement activites_strava (données simulées)
├── schema staging   : employes (8 col anonymisées) + pratiques_declarees + activites_strava
└── schema gold      : tables métier calculées
    ├── eligibilite_prime
    ├── eligibilite_bien_etre
    └── impact_financier

                ↓

Tests qualité (pytest)

                ↓

Mock Slack (JSON log – Nom/Prénom lus à la volée depuis XLSX)

                ↓

PowerBI (connexion PostgreSQL → staging + gold uniquement)
```

---

## Structure cible du projet

```
_projet/
├── _docs/
│   ├── ABAI_X0_tasks_list_logbook.md   # Ce fichier
│   ├── ABAI_X1_note_cadrage.md
│   └── ABAI_X2_contexte.md
├── analyses/                            # Analyses exploratoires
├── data/
│   ├── RAW/                             # Fichiers sources (ne pas modifier)
│   └── exports/                         # Exports PowerBI / rapports
├── src/
│   ├── config.py                        # Paramètres centraux (chemins, constantes métier)
│   ├── db/
│   │   ├── init_db.py                   # Création des schémas et tables PostgreSQL
│   │   └── connexion.py                 # Gestion de la connexion (psycopg2 + .env)
│   ├── ingestion/
│   │   ├── load_rh.py                   # Chargement Données+RH.xlsx → PostgreSQL raw
│   │   └── load_sport.py                # Chargement Données+Sportive.xlsx → PostgreSQL raw
│   ├── simulation/
│   │   └── generate_strava.py           # Génération des activités Strava simulées (12 mois)
│   ├── transformation/
│   │   ├── staging.py                   # Nettoyage et typage (raw → staging)
│   │   ├── distances.py                 # Calcul distances via Google Maps API + fallback haversine
│   │   └── gold.py                      # Calcul des éligibilités et de l'impact financier
│   ├── notifications/
│   │   └── mock_slack.py                # Génération des messages Slack (log JSON)
│   └── main.py                          # Point d'entrée : exécute le pipeline complet
├── tests/
│   ├── conftest.py                      # Fixtures pytest (connexion DB, données de test)
│   ├── test_distances.py                # Tests de la règle de distance domicile-bureau
│   ├── test_simulation.py               # Tests de cohérence des données Strava simulées
│   ├── test_staging.py                  # Tests de qualité des données staging
│   └── test_gold.py                     # Tests de cohérence des calculs métier
├── docker/
│   └── docker-compose.yml               # PostgreSQL + (optionnel) pgAdmin
├── .env.example                         # Modèle de variables d'environnement
├── .gitignore
├── pyproject.toml
├── uv.lock
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
- [ ] Intégrer l'appel au mock dans le pipeline principal (Phase 7)

---

### Phase 7 – Pipeline principal

- [ ] Écrire `src/config.py` (constantes : adresse entreprise, seuils distances, taux prime)
- [ ] Écrire `src/main.py` :
  - [ ] Orchestrer les étapes dans l'ordre : ingestion → staging → distances → gold → mock Slack
  - [ ] Logging clair de chaque étape (module `logging`)
  - [ ] Gestion des erreurs (try/except avec messages explicites)
- [ ] Tester le pipeline de bout en bout

---

### Phase 8 – Dashboard PowerBI

- [ ] Connecter PowerBI à PostgreSQL (connecteur natif)
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

### Phase 9 – Documentation et soutenance

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
