# P8 - Projet ETL Données Météorologiques

Pipeline ETL dockerisé pour lire, nettoyer et intégrer automatiquement les données météorologiques depuis AWS S3 vers MongoDB.

## Description

Ce projet extrait des données météorologiques au format JSONL depuis un bucket S3, applique des transformations de nettoyage et de conversion d'unités, puis les importe automatiquement dans MongoDB.

## ️ Architecture

J'utilise une architecture microservices avec Docker Compose :

- **MongoDB 7.0** : Base de données NoSQL pour stocker les données météorologiques
- **Mongo Express** : Interface web d'administration MongoDB accessible sur http://localhost:8081
- **ETL Pipeline** : Nettoyage et transformation des données
- **MongoDB Importer** : Import automatique des données nettoyées (toutes les 5 minutes)
- **S3 Cleanup** : Service de nettoyage automatique du bucket S3 (toutes les heures)

### Fonctionnalités principales

-  **Lecture S3** : Extraction de fichiers JSONL depuis AWS S3
-  **Parsing Airbyte** : Décodage du format Airbyte avec support des structures imbriquées
-  **Support multi-sources** :
  - Fichiers JSON API avec stations multiples
  - Fichiers Excel convertis (une station par dossier)
  - Extraction automatique du nom de station depuis le chemin S3
-  **Fusion de données** : Tous les fichiers sont fusionnés en un seul DataFrame unifié
-  **Nettoyage des données** :
  - Conversion températures (°F → °C)
  - Conversion vitesses (mph → km/h)
  - Conversion pression (inHg → hPa)
  - Conversion précipitations (in → mm)
  - Conversion direction du vent (texte → degrés)
-  **Préparation MongoDB** :
  - Dates au format ISO 8601
  - Types numériques corrects
  - Clé unique : id_station + timestamp + **random 10 digits**
  - Timestamp de traitement
  - **Traçabilité complète** : nom_station et source_file
-  **Export S3** : Sauvegarde du résultat fusionné dans un dossier de destination
-  **Import MongoDB automatique** : Surveillance du bucket S3 et import automatique des nouveaux fichiers
-  **Docker Compose** : Orchestration complète avec MongoDB, Mongo Express et services ETL
-  **Sécurité** : Aucun credential en clair dans les fichiers Docker

## Installation

### Prérequis

- Docker et Docker Compose
- Compte AWS avec accès S3

### Configuration avec Docker

1. Copier le fichier `.env.example` en `.env` :

```powershell
Copy-Item .env.example .env
```

2. Éditer `.env` avec vos identifiants et autre donnée en italique:

```dotenv
# AWS S3
AWS_ACCESS_KEY_ID=*votre_access_key*
AWS_SECRET_ACCESS_KEY=*votre_secret_key*
AWS_REGION=*eu-west-1*
S3_BUCKET_NAME=*votre-bucket*
S3_PREFIX_SOURCE=01_raw/
S3_PREFIX_DESTINATION=02_cleaned/
S3_PREFIX_ARCHIVE=03_archived/

# MongoDB
MONGODB_ROOT_USER=admin
MONGODB_ROOT_PASSWORD=admin123
MONGODB_DATABASE=weather_data
MONGODB_COLLECTION=measurements

# Mongo Express (Interface Web)
MONGO_EXPRESS_USER=*admin*
MONGO_EXPRESS_PASSWORD=*pass*

# Services
WATCH_INTERVAL=300          # Import automatique (5 minutes)
CLEANUP_INTERVAL=3600       # Nettoyage S3 (1 heure)
```

3. Lancer l'environnement complet :

```powershell
docker-compose up -d
```

4. Accéder à Mongo Express :
   - URL : http://localhost:8081
   - Username : `admin`
   - Password : `pass` (ou celui défini dans `.env`)

### Configuration locale (Développement)

1. Installer les dépendances :

```powershell
poetry install
```

2. Configurer le fichier `.env` comme ci-dessus

## Utilisation

### Démarrage avec Docker Compose

```powershell
# Lancer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f

# Vérifier l'état des services
docker-compose ps

# Arrêter les services
docker-compose down
```

**Services disponibles :**

1. **mongodb** : Base de données MongoDB (port 27017)
2. **mongo-express** : Interface web MongoDB (port 8081)
3. **etl-pipeline** : Script de nettoyage des données (exécution unique)
4. **mongodb-importer** : Service d'import automatique (surveille S3 toutes les 5 minutes)
5. **s3-cleanup** : Service de nettoyage S3 (archive et supprime toutes les heures)

### Tests de connexion MongoDB

Avant chaque import, le système exécute automatiquement une suite de tests pour vérifier :
-  Disponibilité de MongoDB
-  Existence de la base de données et de la collection
-  Permissions CRUD (Create, Read, Update, Delete)
-  Fonctionnement des index (unique_key)
-  Opérations d'upsert
-  Collection de métadonnées

Pour exécuter manuellement les tests :

```powershell
# En local avec Poetry
poetry run pytest ABAI_P8_script_03_test_mongodb.py -v

# Dans Docker
docker-compose run --rm mongodb-importer python ABAI_P8_script_03_test_mongodb.py
```

### Nettoyage et archivage S3

Le service `s3-cleanup` nettoie automatiquement le bucket S3 toutes les heures :
1. Vérifie que les données cleaned sont bien dans MongoDB
2. Déplace les fichiers cleaned vers `03_archived/`
3. Supprime les fichiers raw de `01_raw/`

**Exécution manuelle :**

```powershell
# Mode test (affiche les actions sans les exécuter)
poetry run python ABAI_P8_script_04_cleanup_s3.py --dry-run

# Nettoyage unique en production
poetry run python ABAI_P8_script_04_cleanup_s3.py

# Dans Docker (mode test)
docker-compose run --rm s3-cleanup python ABAI_P8_script_04_cleanup_s3.py --dry-run

# Aide
poetry run python ABAI_P8_script_04_cleanup_s3.py --help
```

### Exécution manuelle du script ETL

```powershell
# En local avec Poetry
poetry run python ABAI_P8_script_01_clean_data.py

# Dans Docker
docker-compose run --rm etl-pipeline
```

Le script exécute automatiquement les étapes suivantes :
1. **Lecture** de tous les fichiers JSONL du bucket S3 (01_raw/)
2. **Extraction** des données selon leur structure :
   - Format API avec stations multiples (Bergues, Lille-Lesquin, etc.)
   - Format Excel converti avec station unique par dossier (Ichtegem, LaMadeleine)
3. **Fusion** de tous les fichiers en un seul DataFrame unifié
4. **Nettoyage** : conversions d'unités et standardisation des colonnes
5. **Sauvegarde** du fichier fusionné dans S3 (02_cleaned/)

**Exemple de sortie** : `20251210_095134_df_weather_allFiles.json` (4 950 enregistrements, 6 stations)

### Structure des données en sortie

Le script génère un **fichier JSON unique fusionné** avec **24 colonnes** par enregistrement :

#### Exemple d'exécution

```
 Résultat de traitement
- Fichiers sources : 3 fichiers JSONL
- Stations détectées : 6 (Bergues, Lille-Lesquin, Hazebrouck, Armentières, Ichtegem, LaMadeleine)
- Enregistrements fusionnés : 4 950
- Fichier de sortie : 20251210_095134_df_weather_allFiles.json
```

#### Format des documents

```json
{
  "id_station": "07015",
  "nom_station": "Lille-Lesquin",
  "dh_utc": "2024-10-05T00:00:00.000Z",
  "temperature": 7.6,
  "pression": 1020.7,
  "humidite": 89.0,
  "point_de_rosee": 5.9,
  "visibilite": 6000.0,
  "vent_moyen": 3.6,
  "vent_rafales": 7.2,
  "vent_direction": 90.0,
  "pluie_3h": 0.0,
  "pluie_1h": 0.0,
  "neige_au_sol": null,
  "precip_accum": null,
  "solar": null,
  "precip_rate": null,
  "uv": null,
  "source_file": "2025_12_10_1765356670402_0.jsonl",
  "processed_at": "2025-12-10T09:51:34.000Z",
  "unique_key": "07015_2024-10-05T00:00:00.000Z_6686150138"
}
```

## Import dans MongoDB

### Automatique (Docker Compose)

Le service `mongodb-importer` surveille automatiquement le dossier `02_cleaned/` du bucket S3 et importe les nouveaux fichiers toutes les 5 minutes (configurable via `WATCH_INTERVAL`).

### Manuel

Si besoin, vous pouvez importer manuellement un fichier :

```bash
# Télécharger le fichier depuis S3
aws s3 cp s3://votre-bucket/02_cleaned/YYYYMMDD_HHMMSS_weather_data.json .

# Importer dans MongoDB
mongoimport --uri 'mongodb://admin:admin123@localhost:27017/weather_data?authSource=admin' \
            --collection measurements \
            --file YYYYMMDD_HHMMSS_weather_data.json \
            --jsonArray
```

### Accès à MongoDB

```powershell
# Se connecter au conteneur MongoDB
docker exec -it weather-mongodb mongosh

# Se connecter à la base de données
use weather_data

# Vérifier les données importées
db.measurements.countDocuments()
db.measurements.findOne()

# Requêtes exemples
db.measurements.find({ id_station: "07015" }).limit(5)
db.measurements.find({ dh_utc: { $gte: ISODate("2024-10-01") } }).count()
```

##  Architecture du projet

```
_projet/
├── .env                              # Configuration (non versionné)
├── .env.example                      # Exemple de configuration
├── .gitignore                        # Exclusions Git
├── docker-compose.yml                # Orchestration Docker (5 services)
├── Dockerfile                        # Image Docker pour ETL
├── init-mongo.js                     # Script d'initialisation MongoDB
├── pyproject.toml                    # Configuration Poetry
├── poetry.lock                       # Versions des dépendances
├── README.md                         # Documentation
├── ABAI_P8_script_01_clean_data.py         # Script principal ETL
├── ABAI_P8_script_02_import_to_mongodb.py  # Service d'import automatique
├── ABAI_P8_script_03_test_mongodb.py       # Tests CRUD MongoDB (pytest)
└── ABAI_P8_script_04_cleanup_s3.py         # Nettoyage et archivage S3
```

## ️ Technologies

- **Python 3.10+** : Langage principal
- **Docker & Docker Compose** : Conteneurisation et orchestration
- **MongoDB 7.0** : Base de données NoSQL
- **Mongo Express** : Interface web MongoDB
- **AWS S3** : Stockage cloud
- **Poetry** : Gestionnaire de dépendances
- **Boto3** : Client AWS
- **Pandas** : Manipulation de données
- **PyMongo** : Driver MongoDB

### Flux de données

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│  S3 Bucket  │──1──▶│  ETL Script  │──2──▶│  S3 Bucket  │──3──▶│ MongoDB  │
│  01_raw/    │      │   (Docker)   │      │ 02_cleaned/ │      │ Database │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘
                                                   │
                                                   │ 4. Watch
                                                   ▼
                                            ┌──────────────┐
                                            │   Importer   │
                                            │   Service    │
                                            └──────────────┘
```

1. Lecture des fichiers JSONL bruts
2. Nettoyage et transformation des données
3. Sauvegarde JSON compatible MongoDB
4. Import automatique dans MongoDB (toutes les 5 minutes)
5. Archivage et nettoyage S3 après import réussi (toutes les heures)

## Dépendances

- **boto3** ^1.35.0 : Client AWS S3
- **pandas** ^2.2.0 : Manipulation de données
- **python-dotenv** ^1.0.0 : Gestion des variables d'environnement
- **pymongo** ^4.10.0 : Driver MongoDB pour Python
- **pytest** ^8.0.0 : Framework de tests (dev)

##  Traçabilité des données

Chaque document MongoDB contient des métadonnées de traçabilité :

- **`nom_station`** : Nom de la ville/station météo
  - **Sources API** : Extrait du mapping Airbyte (ex: `"Lille-Lesquin"` pour ID `"07015"`)
  - **Sources Excel** : Extrait du nom du dossier S3 (ex: `"Ichtegem"` pour `weather_files_Ichtegem/`)
  - Permet d'identifier rapidement la localisation géographique

- **`source_file`** : Nom du fichier JSONL source individuel
  - Exemple : `"2025_12_10_1765356670402_0.jsonl"`
  - **Traçabilité individuelle** : chaque enregistrement garde le nom de SON fichier source
  - Permet de tracer l'origine exacte de chaque mesure
  - Utile pour le débogage, retraitement sélectif et audit des données

- **`processed_at`** : Timestamp du traitement ETL
  - Format ISO 8601 : `"2025-12-09T16:05:18.000Z"`
  - Permet de suivre le délai entre extraction et traitement

- **`unique_key`** : Clé composite unique avec random
  - Format : `"id_station_dh_utc_random10digits"`
  - Exemple : `"07015_2024-10-05T00:00:00.000Z_6686150138"`
  - Les 10 chiffres aléatoires garantissent l'unicité absolue
  - Facilite les upserts et évite les collisions

**Avantages :**
-  Audit complet : fichier → extraction → traitement → base de données
-  Retraitement sélectif : possibilité de supprimer et retraiter un fichier source spécifique
-  Analyse qualité : suivi de la qualité par lot d'extraction
-  Débogage facilité : identification rapide des problèmes par fichier source

## Transformations appliquées

| Mesure | Unité source | Unité cible | Formule |
|--------|-------------|-------------|---------|
| Température | °F | °C | (°F - 32) × 5/9 |
| Vitesse du vent | mph | km/h | mph × 1.60934 |
| Pression | inHg | hPa | inHg × 33.8639 |
| Précipitations | in | mm | in × 25.4 |
| Direction du vent | Texte (N, NE, etc.) | Degrés (0-360°) | Mapping |
