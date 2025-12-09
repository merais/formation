# P8 - Projet ETL Données Météorologiques

Mon pipeline ETL dockerisé pour lire, nettoyer et intégrer automatiquement les données météorologiques depuis AWS S3 vers MongoDB.

## Description

J'extrais les données météorologiques au format JSONL depuis mon bucket S3, j'applique des transformations de nettoyage et de conversion d'unités, puis je les importe automatiquement dans MongoDB.

## 🏗️ Architecture

J'utilise une architecture microservices avec Docker Compose :

- **MongoDB 7.0** : Ma base de données NoSQL pour stocker les données météorologiques
- **Mongo Express** : Interface web d'administration MongoDB accessible sur http://localhost:8081
- **ETL Pipeline** : Nettoyage et transformation des données
- **MongoDB Importer** : Import automatique des données nettoyées (toutes les 5 minutes)
- **S3 Cleanup** : Service de nettoyage automatique de mon bucket S3 (toutes les heures)

### Fonctionnalités principales

- ✅ **Lecture S3** : Extraction de fichiers JSONL depuis AWS S3
- ✅ **Parsing Airbyte** : Décodage du format Airbyte avec support des structures imbriquées
- ✅ **Nettoyage des données** :
  - Conversion températures (°F → °C)
  - Conversion vitesses (mph → km/h)
  - Conversion pression (inHg → hPa)
  - Conversion précipitations (in → mm)
  - Conversion direction du vent (texte → degrés)
- ✅ **Préparation MongoDB** :
  - Dates au format ISO 8601
  - Types numériques corrects
  - Clé unique composite (id_station + timestamp)
  - Timestamp de traitement
- ✅ **Export S3** : Sauvegarde du résultat dans un dossier de destination
- ✅ **Import MongoDB automatique** : Surveillance du bucket S3 et import automatique des nouveaux fichiers
- ✅ **Docker Compose** : Orchestration complète avec MongoDB, Mongo Express et services ETL
- ✅ **Sécurité** : Aucun credential en clair dans les fichiers Docker

## Installation

### Prérequis

- Docker et Docker Compose
- Compte AWS avec accès S3

### Configuration avec Docker

1. Copier le fichier `.env.example` en `.env` :

```powershell
Copy-Item .env.example .env
```

2. Éditer `.env` avec mes identifiants et autres données en italique :

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

Avant chaque import, mon système exécute automatiquement une suite de tests pour vérifier :
- ✅ Disponibilité de MongoDB
- ✅ Existence de la base de données et de la collection
- ✅ Permissions CRUD (Create, Read, Update, Delete)
- ✅ Fonctionnement des index (unique_key)
- ✅ Opérations d'upsert
- ✅ Collection de métadonnées

Pour exécuter manuellement les tests :

```powershell
# En local avec Poetry
poetry run pytest ABAI_P8_script_03_test_mongodb.py -v

# Dans Docker
docker-compose run --rm mongodb-importer python ABAI_P8_script_03_test_mongodb.py
```

### Nettoyage et archivage S3

Mon service `s3-cleanup` nettoie automatiquement le bucket S3 toutes les heures :
1. Vérifie que mes données cleaned sont bien dans MongoDB
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

Mon script propose plusieurs options interactives :
1. Sauvegarder le premier fichier localement (CSV)
2. Lire et combiner tous les fichiers du bucket
3. Sauvegarder le résultat dans S3 (format MongoDB)

### Structure des données en sortie

Mon script génère un fichier JSON avec 19 colonnes par enregistrement :

```json
{
  "id_station": "07015",
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
  "processed_at": "2025-12-08T15:56:18.000Z",
  "unique_key": "07015_2024-10-05T00:00:00.000Z"
}
```

**Colonnes supprimées lors du nettoyage :**
- `time` : Redondante avec `dh_utc`
- `temps_omm` : Très peu de valeurs (< 1%)
- `nebulosite` : Très peu de valeurs (< 2%)

## Import dans MongoDB

### Automatique (Docker Compose)

Mon service `mongodb-importer` surveille automatiquement le dossier `02_cleaned/` de mon bucket S3 et importe les nouveaux fichiers toutes les 5 minutes (configurable via `WATCH_INTERVAL`).

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

## 📁 Architecture du projet

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

## 🛠️ Technologies

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

## Transformations appliquées

| Mesure | Unité source | Unité cible | Formule |
|--------|-------------|-------------|---------|
| Température | °F | °C | (°F - 32) × 5/9 |
| Vitesse du vent | mph | km/h | mph × 1.60934 |
| Pression | inHg | hPa | inHg × 33.8639 |
| Précipitations | in | mm | in × 25.4 |
| Direction du vent | Texte (N, NE, etc.) | Degrés (0-360°) | Mapping |
