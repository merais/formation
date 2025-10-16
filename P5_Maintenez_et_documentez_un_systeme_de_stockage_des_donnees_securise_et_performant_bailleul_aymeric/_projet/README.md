# MongoDB Healthcare Database - Projet P5

Système de gestion de base de données MongoDB sécurisé avec Docker pour les données de santé.

## Liens Github et Google Drive
**Github :**  
- https://github.com/merais/formation/tree/a7ae03b6bbac2170ce3dd3c1e6685061bf484db9/P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric/_projet

**Google Drive :**
- https://drive.google.com/drive/folders/10Qf2RcjWwrMhN26JyQrY_CDQ1LS3bxVw?usp=drive_link

## Livrables :
- Les livrables demandés sont dans `docs/`

## Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Sécurité](#sécurité)
- [Tests](#tests)
- [Structure du Projet](#structure-du-projet)
- [Dépannage](#dépannage)

---

## Vue d'ensemble

Ce projet implémente une base de données MongoDB conteneurisée avec Docker pour gérer des données de santé (patients). Il intègre :

- **Authentification MongoDB** à 3 niveaux (admin, lecture/écriture, lecture seule)
- **Import automatisé** de données CSV (54 966 documents)
- **Tests automatisés** avec pytest (27 tests de sécurité)
- **Architecture Docker** complète avec 6 services
- **Scripts Python** pour création d'utilisateurs et import de données

---

## Architecture

### Services Docker

Le projet utilise **6 services Docker** orchestrés par `docker-compose.yml` :

| Service | Description | Port | Profil |
|---------|-------------|------|--------|
| **mongodb** | Base de données MongoDB 8.0 | 27017 | - |
| **create_users** | Création des utilisateurs MongoDB | - | à la demande |
| **import_scripts** | Import des données CSV | - | à la demande |
| **tests** | Tests généraux de connexion | - | à la demande |
| **readwrite_test** | Tests utilisateur R/W | - | à la demande |
| **readonly_test** | Tests utilisateur lecture seule | - | à la demande |

### Architecture de Sécurité

```
┌─────────────────────────────────────────────┐
│           MONGODB (Port 27017)              │
├─────────────────────────────────────────────┤
│  admin (Root)                               │
│     └─ userAdminAnyDatabase                 │
│                                             │
│  app_user (Application)                     │
│     └─ readWrite sur healthcare_db          │
│                                             │
│  readonly_user (Lecture seule)              │
│     └─ read sur healthcare_db               │
└─────────────────────────────────────────────┘
```

### Volumes

- **mongodb_data** : Persistance des données MongoDB
- **./sources** : Fichiers CSV (lecture seule)

### Réseau

- **healthcare_network** : Réseau bridge isolé pour tous les services

---

## Prérequis

### Logiciels Requis

- **Docker Desktop** (Windows/Mac) ou Docker Engine (Linux)
- **Docker Compose** v2.0+
- **PowerShell** (Windows) ou Bash (Linux/Mac)

### Vérification

```powershell
# Vérifier Docker
docker --version
# Docker version 24.0.0 ou supérieur

# Vérifier Docker Compose
docker compose version
# Docker Compose version v2.0.0 ou supérieur
```

### Fichiers Requis

- `sources/healthcare_dataset.csv` (dataset de 54 966 patients)
- `.env` (credentials MongoDB)

---

## Installation

### 1. Cloner le Projet

```powershell
git clone <repository-url>
cd P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric/_projet
```

### 2. Configurer les Credentials

Créer un fichier `.env` à la racine du projet :

```env
# MongoDB Root Credentials
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=MOT DE PASSE PERSONNALISÉ À MODIFIER IMPÉRATIVEMENT

# MongoDB Database
MONGO_INITDB_DATABASE=healthcare_db

# Application User (Read/Write)
MONGO_APP_USERNAME=app_user
MONGO_APP_PASSWORD=MOT DE PASSE PERSONNALISÉ À MODIFIER IMPÉRATIVEMENT

# Read-Only User
MONGO_READONLY_USERNAME=readonly_user
MONGO_READONLY_PASSWORD=MOT DE PASSE PERSONNALISÉ À MODIFIER IMPÉRATIVEMENT
```

**IMPORTANT** : Modifier les mots de passe par défaut impérativement !

### 3. Vérifier le Dataset

```powershell
# Vérifier la présence du fichier CSV
Test-Path ./sources/healthcare_dataset.csv
# Doit retourner: True
```

---

## Utilisation

### Démarrage Initial

#### Étape 1 : Démarrer MongoDB

```powershell
docker compose up -d mongodb
```

Attendez que MongoDB soit prêt (healthcheck) :
```powershell
docker compose ps
# mongodb doit être "healthy"
```

#### Étape 2 : Créer les Utilisateurs

```powershell
docker compose run --rm create_users
```

**Sortie attendue** :
```
============================================================
Script de Création des Utilisateurs MongoDB
============================================================
	Création des utilisateurs MongoDB...
	Connecté à MongoDB sur mongodb
	app_user créé avec succès (permissions readWrite)
	readonly_user créé avec succès (permissions read)

	Vérification des utilisateurs...
	Trouvé 2 utilisateur(s) dans healthcare_db:
	- app_user: readWrite
	- readonly_user: read

	Tous les utilisateurs vérifiés avec succès!
============================================================
```

#### Étape 3 : Importer les Données

```powershell
docker compose run --rm import_scripts
```

**Sortie attendue** :
```
Connexion sécurisée avec l'utilisateur: app_user
Connexion à MongoDB réussie
Vérification des données...
Le fichier contient 54966 lignes...
Import : 54966 documents insérés dans la collection 'patients'
```

#### Étape 4 : Valider avec les Tests

```powershell
# Tests généraux
docker compose run --rm tests

# Tests sécurité R/W
docker compose run --rm readwrite_test

# Tests sécurité lecture seule
docker compose run --rm readonly_test
```

---

### Commandes Courantes

#### Rebuild et Exécution

Forcer la reconstruction de l'image avant exécution :

```powershell
# Rebuild + création utilisateurs
docker compose run --build --rm create_users

# Rebuild + import données
docker compose run --build --rm import_scripts

# Rebuild + tests
docker compose run --build --rm tests

# Rebuild + tests sécurité R/W
docker compose run --build --rm readwrite_test

# Rebuild + tests sécurité lecture seule
docker compose run --build --rm readonly_test
```

#### Gestion des Services

```powershell
# Arrêter tous les services
docker compose down

# Arrêter et supprimer les volumes (ATTENTION : SUPPRIME LES DONNÉES)
docker compose down -v

# Voir les logs
docker compose logs mongodb
docker compose logs -f mongodb  # Mode suivi
```

#### Accès MongoDB

```powershell
# Shell MongoDB (mongosh)
docker compose exec mongodb mongosh healthcare_db

# Avec authentification
docker compose exec mongodb mongosh -u app_user -p "MOT DE PASSE CONFIGURER DANS LE .env" --authenticationDatabase healthcare_db healthcare_db
```

---

## Sécurité

### Système d'Authentification

Le projet implémente un **système d'authentification à 3 niveaux** :

#### 1. Administrateur (admin)

```yaml
Rôle: userAdminAnyDatabase
Permissions: Gestion complète des utilisateurs
Utilisation: Configuration initiale uniquement
```

#### 2. Utilisateur Application (app_user)

```yaml
Rôle: readWrite sur healthcare_db
Permissions: 
  - Lecture (find, count, aggregate)
  - Écriture (insert, update, delete)
  - Création d'index
Utilisation: Import de données et opérations CRUD
```

#### 3. Utilisateur Lecture Seule (readonly_user)

```yaml
Rôle: read sur healthcare_db
Permissions: 
  - Lecture uniquement (find, count, aggregate)
  - Aucune écriture autorisée
Utilisation: Consultations et reporting
```

### Variables d'Environnement

Les credentials sont stockés dans `.env` et injectés via Docker Compose :

```yaml
environment:
  MONGODB_URI: mongodb://${MONGO_APP_USERNAME}:${MONGO_APP_PASSWORD}@mongodb:27017/?authSource=healthcare_db
```

### Bonnes Pratiques

- `.env` **JAMAIS versionné** (dans `.gitignore`)
- Mots de passe complexes (min. 16 caractères)
- Utilisateur dédié par service (app_user pour import)
- Principe du moindre privilège (readonly_user pour lectures)
- Network bridge isolé

---

## Tests

### Suite de Tests Complète

Le projet inclut **27 tests automatisés** avec pytest :

| Fichier | Tests | Description |
|---------|-------|-------------|
| `test_bdd.py` | 4 | Connexion, collection, comptage |
| `test_readonly_security.py` | 11 | Validation lecture seule |
| `test_readwrite_security.py` | 12 | Validation R/W complet |

### Exécution des Tests

#### Tests Généraux

```powershell
docker compose run --rm tests
```

**Tests exécutés** :
- Connexion à MongoDB
- Accès à la collection patients
- Comptage des documents
- Lecture d'un document

#### Tests Sécurité Lecture/Écriture

```powershell
docker compose run --rm readwrite_test
```

**Tests exécutés** :
- Opérations de lecture (find, count)
- Insertion de documents
- Mise à jour de documents
- Suppression de documents
- Création d'index
- Opérations bulk
- Agrégations

#### Tests Sécurité Lecture Seule

```powershell
docker compose run --rm readonly_test
```

**Tests exécutés** :
- Connexion autorisée
- Lecture autorisée (find, count)
- Insertion refusée (OperationFailure)
- Mise à jour refusée
- Suppression refusée
- Suppression collection refusée
---

## Structure du Projet

```
_projet/
├── README.md                         # Ce fichier
├── docker_README.md                  # Documentation Docker (legacy)
├── docker-compose.yml                # Orchestration des services
├── .env                              # Credentials (NON versionné)
├── .dockerignore                     # Exclusions Docker
├── requirements.txt                  # Dépendances Python
│
├── Dockerfile.create_users           # Image création utilisateurs
├── Dockerfile.import_scripts         # Image import données
├── Dockerfile.tests                  # Image tests pytest
│
├── script_create_users.py            # Script création utilisateurs (227 lignes)
├── script_bdd.py                     # Script import données (157 lignes)
│
├── test_bdd.py                       # Tests généraux (4 tests)
├── test_readonly_security.py         # Tests lecture seule (11 tests)
├── test_readwrite_security.py        # Tests R/W (12 tests)
│
└── sources/                          # Données
    └── healthcare_dataset.csv        # Dataset 54 966 patients
```

---

## Scripts Python

### script_create_users.py

**Rôle** : Créer les utilisateurs MongoDB depuis le fichier `.env`

**Fonctionnalités** :
- Lecture des credentials depuis `.env`
- Connexion multi-host (mongodb, localhost, 127.0.0.1)
- Création de 2 utilisateurs (app_user, readonly_user)
- Vérification des permissions
- Gestion des erreurs (utilisateur existant)

**Exécution** :
```powershell
docker compose run --rm create_users
```

### script_bdd.py

**Rôle** : Importer les données CSV dans MongoDB

**Fonctionnalités** :
- Connexion sécurisée avec app_user
- Lecture du CSV (pandas)
- Nettoyage des données :
  - Conversion des dates (datetime)
  - Normalisation des noms (Title Case)
  - Vérification des valeurs manquantes
  - Détection des doublons
- Insertion (54 966 documents)
- Vérification post-import

**Exécution** :
```powershell
docker compose run --rm import_scripts
```

---

## Dépannage

### MongoDB ne démarre pas

**Symptôme** : `docker compose ps` affiche `unhealthy`

**Solutions** :
```powershell
# Vérifier les logs
docker compose logs mongodb

# Vérifier les ports
netstat -an | findstr 27017

# Redémarrer MongoDB
docker compose restart mongodb

# Réinitialisation complète
docker compose down -v
docker compose up -d mongodb
```

### Échec de création d'utilisateurs

**Symptôme** : `Échec de connexion à mongodb`

**Solutions** :
```powershell
# Vérifier que MongoDB est healthy
docker compose ps mongodb

# Vérifier le fichier .env
Get-Content .env

# Vérifier les logs
docker compose logs create_users

# Forcer rebuild
docker compose build create_users
docker compose run --rm create_users
```

### Échec d'import de données

**Symptôme** : `Erreur lors de la lecture du fichier`

**Solutions** :
```powershell
# Vérifier le fichier CSV
Test-Path ./sources/healthcare_dataset.csv

# Vérifier que les utilisateurs sont créés
docker compose run --rm create_users

# Vérifier les logs
docker compose logs import_scripts

# Import manuel
docker compose run --rm import_scripts
```

### Tests en échec

**Symptôme** : `OperationFailure: not authorized`

**Solutions** :
```powershell
# Vérifier les utilisateurs
docker compose exec mongodb mongosh -u admin -p SecureAdminPassword123! --authenticationDatabase admin

# Dans mongosh :
use healthcare_db
db.getUsers()

# Recréer les utilisateurs si nécessaire
docker compose run --rm create_users

# Réimporter les données si collection vide
docker compose run --rm import_scripts
```

### Réinitialisation Complète

```powershell
# 1. Arrêter et supprimer tout
docker compose down -v

# 2. Nettoyer les images
docker compose build --no-cache

# 3. Redémarrer MongoDB
docker compose up -d mongodb

# 4. Attendre le healthcheck (10-30 secondes)
Start-Sleep -Seconds 30

# 5. Créer les utilisateurs
docker compose run --rm create_users

# 6. Importer les données
docker compose run --rm import_scripts

# 7. Valider avec les tests
docker compose run --rm tests
docker compose run --rm readwrite_test
docker compose run --rm readonly_test
```

---

## Données

### Dataset Healthcare

**Fichier** : `sources/healthcare_dataset.csv`

**Caractéristiques** :
- **54 966 documents** (patients)
- **15 colonnes** :
  - `Name` : Nom du patient
  - `Age` : Âge
  - `Gender` : Genre
  - `Blood Type` : Groupe sanguin
  - `Medical Condition` : Condition médicale
  - `Date of Admission` : Date d'admission
  - `Doctor` : Médecin traitant
  - `Hospital` : Hôpital
  - `Insurance Provider` : Assureur
  - `Billing Amount` : Montant facturé
  - `Room Number` : Numéro de chambre
  - `Admission Type` : Type d'admission
  - `Discharge Date` : Date de sortie
  - `Medication` : Médicaments
  - `Test Results` : Résultats tests

### Vérification des Données

```javascript
// Dans mongosh
use healthcare_db

// Compter les documents
db.patients.countDocuments()
// Résultat: 54966

// Voir un document
db.patients.findOne()

// Statistiques
db.patients.aggregate([
  {
    $group: {
      _id: "$Medical Condition",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
])
```

---

## Variables d'Environnement

### Fichier docker-compose.yml

#### Service create_users
```yaml
MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
MONGO_APP_USERNAME: ${MONGO_APP_USERNAME}
MONGO_APP_PASSWORD: ${MONGO_APP_PASSWORD}
MONGO_READONLY_USERNAME: ${MONGO_READONLY_USERNAME}
MONGO_READONLY_PASSWORD: ${MONGO_READONLY_PASSWORD}
```

#### Service import_scripts
```yaml
MONGODB_URI: mongodb://${MONGO_APP_USERNAME}:${MONGO_APP_PASSWORD}@mongodb:27017/?authSource=healthcare_db
MONGODB_DB: ${MONGO_INITDB_DATABASE}
```

#### Service tests
```yaml
MONGODB_URI: mongodb://${MONGO_APP_USERNAME}:${MONGO_APP_PASSWORD}@mongodb:27017/?authSource=healthcare_db
MONGODB_DB: ${MONGO_INITDB_DATABASE}
COLLECTION_NAME: patients
```

---

## Documentation Complémentaire

### Ressources Externes

- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [pytest Documentation](https://docs.pytest.org/)

---

## Notes Importantes

### Sécurité en Production

**AVERTISSEMENT : Cette configuration est optimisée pour le développement.**

Pour une utilisation en production, ajoutez :

- **TLS/SSL** : Chiffrement des connexions
- **Secrets Docker** : Gestion sécurisée des credentials
- **Limites de ressources** : CPU/RAM dans docker-compose.yml
- **Backup automatisé** : Sauvegarde régulière
- **Monitoring** : Logs centralisés et alertes
- **Réseau privé** : Pas d'exposition du port 27017

### Performance

Pour améliorer les performances :

```javascript
// Créer des index
db.patients.createIndex({ "Name": 1 })
db.patients.createIndex({ "Medical Condition": 1 })
db.patients.createIndex({ "Date of Admission": -1 })
```

### Maintenance

```powershell
# Vérifier l'espace disque
docker system df

# Nettoyer les images inutilisées
docker system prune -a

# Backup des données
docker compose exec mongodb mongodump --out /backup

# Restore des données
docker compose exec mongodb mongorestore /backup
```

---

**Version** : 1.0  
**Dernière mise à jour** : Octobre 2025