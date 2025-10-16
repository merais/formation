# 🏥 Healthcare MongoDB - Projet Sécurisé avec Tests Pytest

## 📋 Vue d'ensemble

Projet de gestion de données de santé avec MongoDB sécurisé, incluant :
- 🔒 **Authentification multi-niveaux** (admin, app_user, readonly_user)
- 🧪 **Suite de tests complète avec Pytest** (29 tests)
- 🐳 **Déploiement Docker** avec docker-compose
- 📊 **Import de données** depuis CSV
- 📚 **Documentation complète**

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Docker et Docker Compose
- PowerShell (Windows) ou Bash (Linux/Mac)

### 2. Installation

```bash
# 1. Démarrer MongoDB
docker compose up -d mongodb

# 2. Créer les utilisateurs (première fois seulement)
.\create-users.ps1  # Windows
# ou
./create-users.sh   # Linux/Mac

# 3. Importer les données
docker compose run --rm import_scripts
```

---

## 📁 Structure du Projet

```
_projet/
├── 📄 .env                              # Identifiants (NON versionné)
├── 🐳 docker-compose.yml                # Configuration Docker
├── 🐳 Dockerfile.tests                  # Image pour pytest
├── 🐳 Dockerfile.import_scripts         # Image pour import
├── 🐳 Dockerfile.create_users           # Image pour création utilisateurs
│
├── 🧪 Tests Pytest
│   ├── docker_tests_bdd_pytest.py       # Tests connexion (4 tests)
│   ├── test_readonly_security.py        # Tests lecture seule (12 tests)
│   └── test_readwrite_security.py       # Tests lecture/écriture (13 tests)
│
├── 📝 Scripts Python
│   ├── create_users.py                  # Création utilisateurs MongoDB
│   ├── docker_script_bdd.py             # Import CSV → MongoDB
│   └── docker_script_readonly.py        # Script lecture seule (ancien)
│
├── 🔧 Scripts Utilitaires
│   ├── create-users.sh                  # Création utilisateurs (Bash - alternatif)
│   └── run-all-tests.ps1                # Exécution tous tests
│
└── 📚 Documentation
    ├── README.md                         # Ce fichier
    ├── SECURITY.md                       # Guide sécurité complet
    ├── SECURITY_SETUP.md                 # Guide configuration rapide
    ├── PYTEST_GUIDE.md                   # Guide utilisation pytest
    ├── TESTS_RECAP.md                    # Récapitulatif tests
    ├── docker_README.md                  # Guide Docker
    └── local_README.md                   # Guide exécution locale
```

---

## 🔒 Sécurité MongoDB

### Trois Niveaux d'Accès

| Utilisateur | Rôle | Permissions | Usage |
|-------------|------|-------------|-------|
| **admin** | Administrateur | Tous droits | Administration système |
| **app_user** | Lecture/Écriture | CRUD complet sur `healthcare_db` | Application principale |
| **readonly_user** | Lecture seule | Lecture uniquement sur `healthcare_db` | Rapports, analyses |

### Configuration
Voir [SECURITY_SETUP.md](SECURITY_SETUP.md) pour le guide rapide ou [SECURITY.md](SECURITY.md) pour la documentation complète.

---

## 🧪 Tests avec Pytest

### Exécution des Tests

```bash
# Tests individuels
docker compose run --rm tests           # Tests de connexion
docker compose run --rm readonly_test   # Tests lecture seule
docker compose run --rm readwrite_test  # Tests lecture/écriture
```

### Résumé des Tests

| Type | Fichier | Tests | Description |
|------|---------|-------|-------------|
| Connexion | `docker_tests_bdd_pytest.py` | 4 | Tests de base |
| Lecture seule | `test_readonly_security.py` | 12 | Vérif permissions readonly |
| Lecture/Écriture | `test_readwrite_security.py` | 13 | Vérif permissions app_user |
| **TOTAL** | | **29** | |

Voir [PYTEST_GUIDE.md](PYTEST_GUIDE.md) pour le guide complet et [TESTS_RECAP.md](TESTS_RECAP.md) pour le récapitulatif.

---

## 🐳 Services Docker

### Services Disponibles

```yaml
# Base de données
mongodb              # MongoDB avec authentification

# Configuration
create_users         # Création des utilisateurs (admin → app_user, readonly_user)

# Import de données
import_scripts       # Import CSV → MongoDB (app_user)

# Tests
tests                # Tests de connexion de base (app_user)
readwrite_test       # Tests sécurité lecture/écriture (app_user)
readonly_test        # Tests sécurité lecture seule (readonly_user)
```

### Commandes Utiles

```bash
# Démarrer MongoDB
docker compose up -d mongodb

# Voir les logs
docker compose logs -f mongodb

# Arrêter tout
docker compose down

# Supprimer volumes (⚠️ DONNÉES PERDUES)
docker compose down -v

# État des services
docker compose ps
```

---

## 📊 Import de Données

### Dataset
- **Source**: `sources/healthcare_dataset_cleaned.csv`
- **Documents**: ~55 000 patients
- **Champs**: Nom, âge, sexe, condition médicale, dates, etc.

### Processus d'Import

```bash
docker compose run --rm import_scripts
```

**Étapes automatiques**:
1. Connexion à MongoDB (app_user)
2. Nettoyage des données
3. Transformation (dates, noms, ID unique)
4. Suppression des doublons
5. Insertion dans la collection `patients`

---

## 📚 Documentation

### Guides Disponibles

| Document | Description | Quand l'utiliser |
|----------|-------------|------------------|
| [README.md](README.md) | Vue d'ensemble | Commencer ici |
| [SECURITY_SETUP.md](SECURITY_SETUP.md) | Config sécurité rapide | Première installation |
| [SECURITY.md](SECURITY.md) | Sécurité complète | Approfondir la sécurité |
| [SECURITY_MIGRATION.md](SECURITY_MIGRATION.md) | Migration sécurité | Comprendre les changements |
| [CREATE_USERS_GUIDE.md](CREATE_USERS_GUIDE.md) | Création utilisateurs | Gérer les utilisateurs |
| [PYTEST_GUIDE.md](PYTEST_GUIDE.md) | Guide pytest | Développer des tests |
| [TESTS_RECAP.md](TESTS_RECAP.md) | Récap tests | Voir tous les tests |
| [docker_README.md](docker_README.md) | Guide Docker | Utilisation Docker |
| [local_README.md](local_README.md) | Exécution locale | Sans Docker |

---

## 🛠️ Workflow Typique

### Premier Démarrage
```bash
# 1. Démarrer MongoDB
docker compose up -d mongodb

# 2. Créer les utilisateurs
docker compose run --rm create_users

# 3. Importer les données
docker compose run --rm import_scripts

# 4. Vérifier avec les tests
.\run-all-tests.ps1
```

### Développement
```bash
# Modifier le code
# ...

# Tester
docker compose run --rm tests

# Si besoin, reconstruire l'image
docker compose build tests
```

### Production
- Changer tous les mots de passe dans `.env`
- Ne pas exposer le port MongoDB (retirer `ports:` dans docker-compose.yml)
- Activer TLS/SSL
- Configurer les sauvegardes
- Voir [SECURITY.md](SECURITY.md) pour plus de détails

---

## 🔍 Vérification de la Sécurité

### Test 1: Lecture Seule
```bash
docker compose run --rm readonly_test
```
**Attendu**:
- ✅ Lecture réussie
- ❌ Écriture refusée

### Test 2: Lecture/Écriture
```bash
docker compose run --rm readwrite_test
```
**Attendu**:
- ✅ Lecture réussie
- ✅ Écriture réussie

---

## 🆘 Dépannage

### MongoDB ne démarre pas
```bash
docker compose logs mongodb
docker compose down -v  # ⚠️ Supprime les données
docker compose up -d mongodb
```

### Authentication failed
```bash
docker compose run --rm create_users  # Recréer les utilisateurs
```

### Tests échouent
```bash
# Vérifier que MongoDB est démarré
docker compose ps

# Vérifier que les données sont importées
docker compose run --rm tests

# Réinitialiser si nécessaire
docker compose down -v
docker compose up -d mongodb
docker compose run --rm create_users
docker compose run --rm import_scripts
```

---

## 📈 Statistiques du Projet

- **Tests**: 29 tests pytest automatisés
- **Couverture**: Connexion, sécurité, CRUD, agrégations
- **Documents**: ~55 000 patients
- **Utilisateurs MongoDB**: 3 (admin, app_user, readonly_user)
- **Services Docker**: 6 (mongodb, create_users, import_scripts, tests, readwrite_test, readonly_test)

---

## 🎓 Technologies Utilisées

- **Base de données**: MongoDB 8.0
- **Langage**: Python 3.13
- **Framework de tests**: Pytest 8.4
- **Conteneurisation**: Docker & Docker Compose
- **Librairies Python**: PyMongo, Pandas, NumPy

---

## 📝 Licence

Ce projet est à des fins éducatives dans le cadre de la formation Data Engineer.

---

## 👤 Auteur

**Aymeric Bailleul**
- Formation: Data Engineer
- Projet: P5 - Maintenez et documentez un système de stockage des données sécurisé et performant
- Date: Octobre 2025

---

## 🔗 Liens Utiles

- [Documentation MongoDB](https://docs.mongodb.com/)
- [Documentation PyMongo](https://pymongo.readthedocs.io/)
- [Documentation Pytest](https://docs.pytest.org/)
- [Documentation Docker](https://docs.docker.com/)

---

## ✅ Checklist de Vérification

Avant de considérer le projet terminé :

- [x] MongoDB démarre avec authentification
- [x] Les 3 utilisateurs sont créés
- [x] Import de données fonctionne
- [x] Tests de connexion passent (4/4)
- [x] Tests readonly passent (12/12)
- [x] Tests readwrite passent (13/13)
- [x] Documentation complète
- [x] Scripts d'automatisation créés
- [x] Sécurité configurée
- [x] Code versionné dans Git

---

**🎉 Projet opérationnel et sécurisé !**
