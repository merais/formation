# P8 - Construisez et testez une infrastructure de données

## Description
Projet de construction et test d'une infrastructure de données météorologiques avec pipeline ETL, stockage S3, et base de données MongoDB conteneurisée.

## 🏗️ Architecture

Le projet utilise une architecture microservices avec Docker Compose :

- **MongoDB** : Base de données NoSQL pour stocker les données météorologiques
- **Mongo Express** : Interface web d'administration MongoDB
- **ETL Pipeline** : Nettoyage et transformation des données
- **MongoDB Importer** : Import automatique des données nettoyées
- **S3 Cleanup** : Service de nettoyage automatique du bucket S3

## 🛠️ Technologies utilisées

### Backend & Data
- **Python 3.10+** : Langage principal
- **Poetry** : Gestionnaire de dépendances
- **PyAirbyte 0.33.6** : Bibliothèque pour les connecteurs Airbyte
- **Pandas** : Manipulation de données
- **SQLAlchemy** : ORM pour bases de données

### Infrastructure
- **Docker & Docker Compose** : Conteneurisation et orchestration
- **MongoDB 7.0** : Base de données NoSQL
- **Mongo Express** : Interface web MongoDB
- **AWS S3** : Stockage cloud des fichiers

### Développement
- **Pytest** : Tests unitaires
- **Black** : Formatage du code
- **Flake8** : Linting
- **Mypy** : Vérification de types

## 📁 Structure du projet

```
P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul/
├── _cours/                      # Matériel de cours
├── _projet/                     # Dossier principal du projet
│   ├── .env                     # Variables d'environnement (à ne pas commiter)
│   ├── .env.example             # Template des variables d'environnement
│   ├── docker-compose.yml       # Configuration Docker Compose
│   ├── Dockerfile               # Image Docker pour les services Python
│   ├── init-mongo.js            # Script d'initialisation MongoDB
│   ├── pyproject.toml           # Configuration Poetry du projet
│   ├── ABAI_P8_script_01_clean_data.py       # Script de nettoyage des données
│   ├── ABAI_P8_script_02_import_to_mongodb.py # Script d'import MongoDB
│   ├── ABAI_P8_script_03_test_mongodb.py     # Tests MongoDB
│   └── ABAI_P8_script_04_cleanup_s3.py       # Script de nettoyage S3
├── src/                         # Code source Python (environnement Poetry)
├── tests/                       # Tests unitaires
├── pyproject.toml               # Configuration Poetry racine
└── README.md                    # Ce fichier
```

## 🚀 Installation et démarrage

### Prérequis
- Python 3.10 ou supérieur
- Poetry installé (`pip install poetry`)
- Docker et Docker Compose installés
- Compte AWS avec accès S3

### 1. Configuration de l'environnement Python (optionnel)

```bash
# Installer les dépendances Poetry
poetry install

# Activer l'environnement virtuel
poetry shell
```

### 2. Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cd _projet
cp .env.example .env

# Éditer .env avec vos credentials AWS et MongoDB
```

Variables requises dans `.env` :
```env
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-1
S3_BUCKET_NAME=p8-weather-data

# MongoDB
MONGODB_ROOT_USER=admin
MONGODB_ROOT_PASSWORD=admin123
MONGODB_DATABASE=weather_data
MONGODB_COLLECTION=measurements

# Mongo Express
MONGO_EXPRESS_USER=admin
MONGO_EXPRESS_PASSWORD=pass
```

### 3. Démarrage des services Docker

```bash
cd _projet

# Lancer tous les services en arrière-plan
docker-compose up -d

# Vérifier l'état des conteneurs
docker-compose ps

# Voir les logs
docker-compose logs -f
```

## 🌐 Accès aux services

- **MongoDB** : `mongodb://localhost:27017`
- **Mongo Express** : http://localhost:8081
  - Username : `admin`
  - Password : `pass` (configurable dans `.env`)

## 📊 Utilisation

### Pipeline ETL complet

Les services Docker s'exécutent automatiquement :

1. **ETL Pipeline** : Nettoie les données brutes du S3
2. **MongoDB Importer** : Importe les données nettoyées dans MongoDB toutes les 5 minutes
3. **S3 Cleanup** : Archive les fichiers traités toutes les heures

### Exécution manuelle des scripts

```bash
# Nettoyage des données
docker-compose run etl-pipeline python ABAI_P8_script_01_clean_data.py

# Import vers MongoDB
docker-compose run mongodb-importer python ABAI_P8_script_02_import_to_mongodb.py

# Test de connexion MongoDB
docker-compose run etl-pipeline python ABAI_P8_script_03_test_mongodb.py

# Nettoyage S3
docker-compose run s3-cleanup python ABAI_P8_script_04_cleanup_s3.py
```

## 🧪 Tests

```bash
# Avec Poetry
poetry run pytest

# Avec Docker
docker-compose run etl-pipeline pytest
```

## 🛑 Arrêt des services

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

## 📝 Commandes utiles

### Docker Compose
```bash
docker-compose up -d              # Démarrer en arrière-plan
docker-compose down               # Arrêter les services
docker-compose logs -f [service]  # Voir les logs
docker-compose restart [service]  # Redémarrer un service
docker-compose ps                 # État des conteneurs
```

### Poetry
```bash
poetry install                    # Installer les dépendances
poetry add <package>              # Ajouter un package
poetry remove <package>           # Supprimer un package
poetry update                     # Mettre à jour les dépendances
poetry shell                      # Activer l'environnement virtuel
```

### Formatage & Linting
```bash
poetry run black .                # Formater le code
poetry run flake8 .               # Linter le code
poetry run mypy .                 # Vérifier les types
```

## 🔐 Sécurité

- ⚠️ Ne jamais commiter le fichier `.env`
- ✅ Utiliser `.env.example` comme template
- ✅ Le `docker-compose.yml` ne contient aucun credential en clair
- ✅ Les credentials AWS sont chargés depuis le `.env`

## 📚 Ressources

- [Documentation PyAirbyte](https://github.com/airbytehq/PyAirbyte)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
