+
# P12 – Sport Data Solution · Projet dbt

**Auteur :** Aymeric Bailleul  
**Formation :** Data Engineer – OpenClassrooms  
**Période :** 10/03/2026 → 11/04/2026

Ce projet reconstruit la **couche de transformation** du pipeline P12 en SQL pur avec **dbt**.  
Il s'appuie sur la même instance PostgreSQL que `_projet` (port 5433, DB `sport_data`) :  
les schémas `raw` et `staging` sont alimentés par `_projet`, **dbt prend en charge la transformation vers `gold`**.

---

## Contexte métier

L'entreprise Lattes Sport souhaite valoriser la pratique sportive de ses 161 salariés via deux avantages :

| Avantage | Règle | Source |
|---|---|---|
| **Prime sportive** (5% du salaire brut) | Venir au bureau à pied / vélo / trottinette dans le rayon autorisé | Déclaratif RH + distance Google Maps |
| **5 journées bien-être** | ≥ 15 activités physiques dans l'année | Données Strava simulées |

Seuils de distance :
- Marche / Running : ≤ 15 km domicile-bureau
- Vélo / Trottinette / Autres : ≤ 25 km

---

## Architecture

```
_projet (Python ETL – pipeline source, port 5433)
├── raw.activites_strava       ← données Strava simulées
├── staging.employes           ← RH anonymisés (RGPD)
├── staging.pratiques_declarees
└── staging.cache_distances    ← distances Google Maps / haversine

        ↓  même instance PostgreSQL

_projet_dbt (dbt – transformation SQL)
├── MODEL staging/stg_activites_strava   → staging.activites_strava (nettoyage)
├── MODEL gold/eligibilite_prime         → gold.eligibilite_prime
├── MODEL gold/eligibilite_bien_etre     → gold.eligibilite_bien_etre
└── MODEL gold/impact_financier          → gold.impact_financier

        ↓

dbt test (37 tests : unique, not_null, accepted_values)
```

---

## Prérequis

- PostgreSQL 16 via Docker (port 5433, DB `sport_data`) — lancé par `_projet`
- `_projet` doit avoir été exécuté au moins une fois pour peupler `raw` et `staging`
- Python 3.12 (dbt-core 1.11.7 n'est pas compatible Python 3.13)

---

## Installation

Le venv est intentionnellement créé **hors Google Drive** (Windows bloque la création d'exécutables `.exe` dans les dossiers synchronisés) :

```bash
# Créer le venv Python 3.12 en local
python -m venv C:\Users\<USER>\.venvs\projet_dbt

# Installer les dépendances
C:\Users\<USER>\.venvs\projet_dbt\Scripts\pip install dbt-postgres python-dotenv
```

Vérification :

```bash
C:\Users\<USER>\.venvs\projet_dbt\Scripts\dbt --version
# Core: 1.11.7  |  Plugins: postgres: 1.10.0
```

---

## Connexion PostgreSQL

Le fichier `profiles.yml` est à la racine de `_projet_dbt/` (non versionné) :

```yaml
sport_data:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5433
      user: postgres
      password: postgres
      dbname: sport_data
      schema: public
      threads: 4
```

---

## Utilisation

### Via `main.py` (recommandé)

```bash
cd _projet_dbt
C:\Users\<USER>\.venvs\projet_dbt\Scripts\python main.py
```

Lance `dbt run` puis `dbt test`. Arrête en cas d'erreur.

### Via dbt directement

```bash
cd _projet_dbt/sport_data

# Compiler (vérification SQL + DAG)
dbt compile --profiles-dir ..

# Exécuter les modèles
dbt run --profiles-dir ..

# Lancer les tests
dbt test --profiles-dir ..

# Tout en une fois
dbt build --profiles-dir ..
```

---

## Modèles dbt

### Staging

| Modèle | Source | Destination | Description |
|---|---|---|---|
| `stg_activites_strava` | `raw.activites_strava` | `staging.activites_strava` | Nettoyage des activités brutes (5 filtres qualité) |

Filtres appliqués :
- `distance_m > 0`
- `duree_s > 0`
- `date_debut >= now() - interval '395 days'`
- `type_sport` dans la liste des 15 sports valides
- `id_salarie` présent dans `staging.employes`

### Gold

| Modèle | Dépendances | Destination | Description |
|---|---|---|---|
| `eligibilite_prime` | `staging.employes`, `staging.cache_distances` | `gold.eligibilite_prime` | Prime 5% selon mode + distance |
| `eligibilite_bien_etre` | `stg_activites_strava` | `gold.eligibilite_bien_etre` | ≥ 15 activités → 5 jours |
| `impact_financier` | `eligibilite_prime`, `eligibilite_bien_etre` | `gold.impact_financier` | Agrégat par département |

---

## Tests dbt

**37 tests** automatisés, répartis en :

| Scope | Type | Nb |
|---|---|---|
| Sources (`staging.*`) | `unique`, `not_null` | 10 |
| Modèle staging | `not_null`, `accepted_values` | 6 |
| Modèles gold | `unique`, `not_null` | 21 |

```bash
dbt test --profiles-dir ..
# Done. PASS=37 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=37
```

---

## Structure du projet

```
_projet_dbt/
├── _docs/
│   └── ABAI_X0_tasks_list_logbook.md
├── data/RAW/                        # Fichiers XLSX sources (mêmes que _projet)
├── sport_data/                      # Projet dbt
│   ├── dbt_project.yml
│   ├── macros/
│   │   └── generate_schema_name.sql # Schémas exacts (sans préfixe public_)
│   └── models/
│       ├── sources.yml
│       ├── staging/
│       │   ├── stg_activites_strava.sql
│       │   └── schema.yml
│       └── gold/
│           ├── eligibilite_prime.sql
│           ├── eligibilite_bien_etre.sql
│           ├── impact_financier.sql
│           └── schema.yml
├── profiles.yml                     # Non versionné
├── main.py                          # Wrapper dbt run + dbt test
├── pyproject.toml                   # Python >=3.12, dbt-postgres, python-dotenv
└── .env                             # Non versionné
```

---

## Résultats

```
dbt run  → 4/4 modèles OK  (0.53s)
  161 salariés · 2 256 activités nettoyées · 5 départements
  68 éligibles prime (172 482,50 EUR) · 67 éligibles bien-être (335 jours)

dbt test → 37/37 PASS  (1.00s)
```
