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

```
Sources
├── Données+RH.xlsx          → table : employes
├── Données+Sportive.xlsx    → table : pratiques_declarees
└── Simulation Strava        → table : activites_strava

                ↓

PostgreSQL (Docker)
├── schema raw       : chargement brut des sources
├── schema staging   : nettoyage et typage
└── schema gold      : tables métier calculées
    ├── eligibilite_prime
    ├── eligibilite_bien_etre
    └── impact_financier

                ↓

Tests qualité (pytest)

                ↓

Mock Slack (JSON log)

                ↓

PowerBI (connexion PostgreSQL)
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
  - [X] Export CSV nettoyés (`rh_clean.csv`, `sport_clean.csv`)

---

### Phase 1 – Infrastructure PostgreSQL

- [X] Lancer le conteneur PostgreSQL via Docker Compose (port 5433, postgres:16-alpine)
- [ ] Créer les schémas `raw`, `staging`, `gold`
- [ ] Créer les tables du schéma `raw` :
  - [ ] `raw.employes`
  - [ ] `raw.pratiques_declarees`
  - [ ] `raw.activites_strava`
- [ ] Créer les tables du schéma `staging` :
  - [ ] `staging.employes`
  - [ ] `staging.pratiques_declarees`
  - [ ] `staging.activites_strava`
- [ ] Créer les tables du schéma `gold` :
  - [ ] `gold.eligibilite_prime`
  - [ ] `gold.eligibilite_bien_etre`
  - [ ] `gold.impact_financier`
- [ ] Écrire `src/db/connexion.py` (connexion via `.env`)
- [ ] Écrire `src/db/init_db.py` (création automatique des schémas et tables)

---

### Phase 2 – Ingestion des données sources

- [ ] Écrire `src/ingestion/load_rh.py` (xlsx → `raw.employes`, `raw.pratiques_declarees`)
- [ ] Écrire `src/ingestion/load_sport.py` (xlsx → `raw.pratiques_declarees`)
- [ ] Vérifier le chargement (comptage, aperçu)

---

### Phase 3 – Simulation des données Strava

- [ ] Définir les types de sport disponibles (course, randonnée, vélo, natation, etc.)
- [ ] Écrire `src/simulation/generate_strava.py` :
  - [ ] Générer plusieurs milliers d'activités sur les 12 derniers mois
  - [ ] Basé sur les salariés RH et leur pratique déclarée
  - [ ] Colonnes : `ID`, `ID salarié`, `Date début`, `Type sport`, `Distance (m)`, `Durée (s)`, `Commentaire`
  - [ ] Respect des cohérences (distances positives, durées positives, dates valides)
- [ ] Charger les données générées dans `raw.activites_strava`

---

### Phase 4 – Pipeline ETL (Staging → Gold)

- [ ] Écrire `src/transformation/staging.py` :
  - [ ] Nettoyage des types (dates, entiers, chaînes)
  - [ ] Gestion des valeurs nulles
  - [ ] Standardisation des colonnes
- [ ] Écrire `src/transformation/distances.py` :
  - [ ] Appel Google Maps API pour calculer la distance domicile-bureau
  - [ ] Fallback haversine si la clé API est absente
  - [ ] Mise en cache des résultats en base (éviter les appels répétés)
  - [ ] Application des règles métier (15 km marche/running, 25 km vélo/trottinette)
  - [ ] Flaggage des anomalies de déclaration
- [ ] Écrire `src/transformation/gold.py` :
  - [ ] Calcul de l'éligibilité à la prime sportive
  - [ ] Calcul de l'éligibilité aux 5 journées bien-être (>= 15 activités/an)
  - [ ] Calcul de l'impact financier (prime = salaire brut * 5 %)
  - [ ] Alimentation des tables `gold.*`

---

### Phase 5 – Tests de qualité (pytest)

- [ ] Écrire `tests/conftest.py` (fixtures : connexion DB, jeux de données de test)
- [ ] Écrire `tests/test_distances.py` :
  - [ ] Distance négative → erreur
  - [ ] Distance incohérente avec le moyen de déplacement → flaggée
  - [ ] Adresse invalide → gestion propre de l'erreur
- [ ] Écrire `tests/test_simulation.py` :
  - [ ] Distances >= 0
  - [ ] Durées >= 0
  - [ ] Dates dans les 12 derniers mois
  - [ ] IDs salariés tous présents dans la table `employes`
  - [ ] Types de sport valides (liste fermée)
- [ ] Écrire `tests/test_staging.py` :
  - [ ] Pas de doublon sur `ID salarié`
  - [ ] Salaires positifs
  - [ ] Dates d'embauche antérieures à aujourd'hui
- [ ] Écrire `tests/test_gold.py` :
  - [ ] Le montant de la prime = salaire brut * 0.05
  - [ ] Aucun salarié non éligible ne reçoit la prime
  - [ ] Nombre de jours bien-être = 5 si >= 15 activités, sinon 0
- [ ] Vérifier que tous les tests passent (`uv run pytest`)

---

### Phase 6 – Notifications Slack (mock)

- [ ] Écrire `src/notifications/mock_slack.py` :
  - [ ] Générer un message pour chaque activité sportive (format Juliette)
  - [ ] Logger les messages dans `data/exports/slack_messages.json`
  - [ ] Exemples de messages :
    - "Bravo [Prénom] [Nom] ! Tu viens de courir [X] km en [Y] min !"
    - "Magnifique [Prénom] [Nom] ! Une randonnée de [X] km terminée !"
- [ ] Intégrer l'appel au mock dans le pipeline principal

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
  - [ ] Montant total des primes par BU
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

