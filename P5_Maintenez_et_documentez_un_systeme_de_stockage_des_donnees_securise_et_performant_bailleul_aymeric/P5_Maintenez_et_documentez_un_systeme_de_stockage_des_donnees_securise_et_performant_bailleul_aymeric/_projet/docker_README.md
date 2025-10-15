# MongoDB Healthcare Database - Docker Setup

Ce projet configure une base de données MongoDB avec Docker Compose pour gérer les données de santé.

## Architecture

- **Service MongoDB** : Base de données persistante
- **Service Import** : Script Python d'importation des données CSV (exécution à la demande)
- **2 Volumes** :
  - `mongodb_data` : Persistance des données MongoDB
  - `./sources` : Accès au fichier CSV en lecture seule

## Prérequis

- Docker et Docker Compose installés
- Le fichier `healthcare_dataset.csv` doit être dans `./sources/`

## Utilisation

### 1. Démarrer MongoDB seul

```powershell
docker-compose up -d mongodb
```

Cela démarre uniquement le conteneur MongoDB sans exécuter l'import.

### 2. Construire l'image d'import (première fois seulement)

```powershell
docker-compose build import_scripts
```

### 3. Exécuter les scripts

Pour exécuter le script d'import des données :

```powershell
docker-compose run --rm -e SCRIPT_TO_RUN=docker_script_bdd.py import_scripts
```

Pour exécuter le script de test de la base de données :

```powershell
docker-compose run --rm -e SCRIPT_TO_RUN=docker_tests_bdd.py import_scripts
```

Pour exécuter le script de test avec pytest :

```powershell
docker-compose run --rm -e SCRIPT_TO_RUN=test_docker_bdd.py import_scripts
```

Options :
- `--rm` : Supprime le conteneur après exécution
- Le script détecte automatiquement si les données existent déjà
- Ré-exécuter la commande affiche le nombre de documents existants sans réimporter

---

### 4. Arrêter tous les services

```powershell
docker-compose down
```

### 5. Supprimer les données persistantes

**Attention : cela supprime toutes les données de la base** :

```powershell
docker-compose down -v
```

## Variables d'environnement

Le script `docker_script_bdd.py` utilise les variables d'environnement suivantes (définies dans `docker-compose.yml`) :

- `MONGODB_URI` : URI de connexion MongoDB (par défaut : `mongodb://mongodb:27017/`)
- `MONGODB_DB` : Nom de la base de données (par défaut : `healthcare_db`)
- `COLLECTION_NAME` : Nom de la collection (par défaut : `patients`)
- `SOURCE_CSV` : Chemin vers le fichier CSV (par défaut : `./sources/healthcare_dataset.csv`)

## Accéder à MongoDB depuis un conteneur

```powershell
# Shell interactif dans le conteneur MongoDB
docker-compose exec mongodb mongosh healthcare_db
```

## Vérifier les données

```javascript
// Dans mongosh
use healthcare_db
db.patients.countDocuments()
db.patients.findOne()
```

```powershell
# On lance le script de test de la bdd
docker-compose run --rm -e SCRIPT_TO_RUN=docker_tests_bdd.py import_scripts
```
## Dépannage

### MongoDB ne démarre pas

```powershell
# Vérifier les logs
docker-compose logs mongodb
```

### Script d'import échoue

```powershell
# Vérifier que le CSV existe
ls ./sources/healthcare_dataset.csv

# Vérifier les logs du conteneur d'import
docker-compose logs import_scripts
```

### Réinitialiser complètement

```powershell
docker-compose down -v
docker-compose up -d mongodb
docker-compose run --rm import_scripts
```

## Sécurité

**Note** : Cette configuration est pour le développement. En production, ajoutez :
- Authentification MongoDB (MONGO_INITDB_ROOT_USERNAME/PASSWORD)
- Réseau isolé
- Secrets Docker pour les credentials
- Limite de ressources (CPU/RAM)

## Raccourcis

```powershell
# Relance mongodb, la création du conteneur de scripts et lance le script de création, test et import 
docker-compose down -v; docker-compose up -d mongodb; docker-compose build import_scripts; docker-compose run --rm -e SCRIPT_TO_RUN=docker_script_bdd.py import_scripts

# Lance le script de test de la bdd
docker-compose run --rm -e SCRIPT_TO_RUN=docker_tests_bdd.py import_scripts
```