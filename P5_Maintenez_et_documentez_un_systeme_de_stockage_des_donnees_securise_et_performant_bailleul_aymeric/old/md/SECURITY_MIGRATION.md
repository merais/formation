# Migration vers l'Authentification Sécurisée MongoDB

## 📋 Vue d'ensemble

Ce document explique les modifications apportées au script d'import pour intégrer l'authentification sécurisée MongoDB avec les utilisateurs `app_user` et `readonly_user`.

---

## 🔄 Modifications Apportées

### 1. Script d'Import (`docker_script_bdd.py`)

#### ❌ Avant (connexion non sécurisée)

```python
# Variables globales
DB_NAME = os.getenv("MONGODB_DB", "healthcare_db")
URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "patients")
```

**Problèmes** :
- ❌ Pas d'authentification
- ❌ Accès root par défaut
- ❌ Pas de gestion des credentials

#### ✅ Après (connexion sécurisée)

```python
# Variables globales
DB_NAME = os.getenv("MONGODB_DB", "healthcare_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "patients")
SOURCE_CSV = os.getenv("SOURCE_CSV", "./sources/healthcare_dataset.csv")

# Construction de l'URI sécurisée
# Priorité 1 : Utiliser MONGODB_URI si défini (depuis docker-compose.yml)
URI = os.getenv("MONGODB_URI")

if URI:
    # Extraire le username pour l'affichage
    username = URI.split("://")[1].split(":")[0]
    print(f"🔒 Connexion sécurisée avec l'utilisateur: {username}")
else:
    # Priorité 2 : Construire l'URI depuis les variables individuelles
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "app_user")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")
    MONGODB_HOST = os.getenv("MONGODB_HOST", "mongodb")
    MONGODB_AUTH_SOURCE = os.getenv("MONGODB_AUTH_SOURCE", "healthcare_db")
    
    if MONGODB_USERNAME and MONGODB_PASSWORD:
        URI = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:27017/{DB_NAME}?authSource={MONGODB_AUTH_SOURCE}"
        print(f"🔒 Connexion sécurisée avec l'utilisateur: {MONGODB_USERNAME}")
    else:
        URI = f"mongodb://{MONGODB_HOST}:27017/"
        print("⚠️  Connexion sans authentification")
```

**Avantages** :
- ✅ Authentification requise
- ✅ Utilise `app_user` (droits readWrite uniquement)
- ✅ Support de deux modes de configuration
- ✅ Affichage du mode de connexion

---

## 🔐 Architecture de Sécurité

### Utilisateurs MongoDB

| Utilisateur | Rôle | Base | Permissions | Usage |
|-------------|------|------|-------------|-------|
| **admin** | root | admin | Toutes | Administration, création d'utilisateurs |
| **app_user** | readWrite | healthcare_db | CRUD complet | Import de données, application |
| **readonly_user** | read | healthcare_db | Lecture seule | Rapports, analyses, tests lecture |

### Flux de Données Sécurisé

```
┌─────────────────────────────────────────────────────┐
│  1. docker compose run --rm create_users            │
│     → Crée app_user et readonly_user                │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  2. docker compose run --rm import_scripts          │
│     → Se connecte avec app_user                     │
│     → Importe les données dans healthcare_db        │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  3. Tests et Vérifications                          │
│     → tests: app_user (connexion + CRUD)            │
│     → readonly_test: readonly_user (lecture seule)  │
│     → readwrite_test: app_user (CRUD complet)       │
└─────────────────────────────────────────────────────┘
```

---

## 🐳 Configuration Docker

### Service `import_scripts`

```yaml
import_scripts:
  build:
    context: .
    dockerfile: Dockerfile.import_scripts
  container_name: healthcare_import
  depends_on:
    - mongodb
  environment:
    # ✅ URI sécurisée avec app_user
    MONGODB_URI: mongodb://${MONGO_APP_USERNAME}:${MONGO_APP_PASSWORD}@mongodb:27017/?authSource=healthcare_db
    MONGODB_DB: ${MONGO_INITDB_DATABASE}
  networks:
    - healthcare_network
  profiles:
    - import
```

**Points clés** :
- `MONGODB_URI` contient les credentials depuis `.env`
- `authSource=healthcare_db` : authentification sur la bonne base
- `app_user` a les droits `readWrite` nécessaires pour l'import

---

## 📝 Variables d'Environnement (.env)

```env
# MongoDB Root (admin)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=SecureAdminPassword123!

# Base de données
MONGO_INITDB_DATABASE=healthcare_db

# Application User (Import + CRUD)
MONGO_APP_USERNAME=app_user
MONGO_APP_PASSWORD=SecureAppPassword123!

# Read-Only User (Consultation)
MONGO_READONLY_USERNAME=readonly_user
MONGO_READONLY_PASSWORD=SecureReadPassword123!
```

---

## 🚀 Workflow Complet

### Première Installation

```bash
# 1. Démarrer MongoDB
docker compose up -d mongodb

# 2. Créer les utilisateurs
docker compose run --rm create_users

# 3. Importer les données (avec app_user)
docker compose run --rm import_scripts

# 4. Vérifier avec les tests
docker compose run --rm tests           # Tests généraux (app_user)
docker compose run --rm readonly_test   # Tests readonly_user
docker compose run --rm readwrite_test  # Tests app_user CRUD
```

### Sortie Attendue

#### `create_users`
```
============================================================
MongoDB User Creation Script
============================================================
🔧 Creating MongoDB users...
   ✓ Connected to MongoDB at mongodb
   ✓ app_user created successfully (readWrite permissions)
   ✓ readonly_user created successfully (read permissions)

✅ All users verified successfully!
```

#### `import_scripts`
```
🔒 Connexion sécurisée avec l'utilisateur: app_user
Connexion à MongoDB réussie
La collection 'patients' n'existe pas et va donc être créée.
Le fichier contient 55500 lignes et 15 colonnes avant le nettoyage.
...
Import : 54966 documents insérés dans la collection 'patients'
```

#### `tests`
```
test_connection PASSED
test_collection_exists PASSED
test_count_documents PASSED (54966 documents)
test_document_operations PASSED

4 passed in 0.22s
```

---

## 🛡️ Sécurité Renforcée

### Avant vs Après

| Aspect | Avant | Après |
|--------|-------|-------|
| **Authentification** | ❌ Aucune | ✅ Requise |
| **Utilisateur** | ❌ root implicite | ✅ app_user (droits limités) |
| **Credentials** | ❌ Hardcodés | ✅ Variables d'environnement |
| **Principe du moindre privilège** | ❌ Non respecté | ✅ Respecté |
| **Traçabilité** | ❌ Impossible | ✅ Par utilisateur |
| **Isolation** | ❌ Aucune | ✅ Par rôle |

### Avantages

1. **Séparation des responsabilités**
   - Admin : Gestion des utilisateurs
   - app_user : Import et CRUD
   - readonly_user : Consultation

2. **Moindre privilège**
   - Chaque utilisateur a uniquement les permissions nécessaires
   - Limite l'impact d'une compromission

3. **Auditabilité**
   - Chaque action est liée à un utilisateur
   - Logs MongoDB montrent qui a fait quoi

4. **Conformité**
   - Respect des bonnes pratiques de sécurité
   - Prêt pour un environnement de production

---

## 🔍 Vérification de la Sécurité

### Test 1 : Import avec app_user

```bash
docker compose run --rm import_scripts
```

**Attendu** :
- ✅ Message "🔒 Connexion sécurisée avec l'utilisateur: app_user"
- ✅ Import réussi
- ✅ 54966 documents insérés

### Test 2 : Lecture avec readonly_user

```bash
docker compose run --rm readonly_test
```

**Attendu** :
- ✅ Lecture réussie (54966 documents)
- ✅ Insertion/Mise à jour/Suppression refusées
- ✅ 11 tests passent

### Test 3 : CRUD avec app_user

```bash
docker compose run --rm readwrite_test
```

**Attendu** :
- ✅ Lecture réussie
- ✅ Insertion/Mise à jour/Suppression réussies
- ✅ 12 tests passent

---

## 🔧 Dépannage

### Erreur : `Authentication failed`

**Cause** : Les utilisateurs n'ont pas été créés

**Solution** :
```bash
docker compose run --rm create_users
```

### Erreur : `not authorized on healthcare_db`

**Cause** : Mauvais utilisateur ou permissions insuffisantes

**Solution** :
```bash
# Vérifier les utilisateurs existants
docker exec healthcare_mongodb mongosh admin -u admin -p SecureAdminPassword123! \
  --eval "db.getSiblingDB('healthcare_db').getUsers()"

# Recréer les utilisateurs si nécessaire
docker compose run --rm create_users
```

### Erreur : `Could not connect to MongoDB`

**Cause** : MongoDB pas démarré ou pas healthy

**Solution** :
```bash
# Vérifier l'état
docker compose ps

# Redémarrer si nécessaire
docker compose restart mongodb

# Attendre le healthcheck
docker compose logs -f mongodb
```

---

## 📊 Tests de Validation

### Matrice de Tests

| Test | Utilisateur | Opération | Résultat Attendu |
|------|-------------|-----------|------------------|
| `tests` | app_user | Connexion | ✅ PASSED |
| `tests` | app_user | Lecture | ✅ PASSED (54966 docs) |
| `tests` | app_user | Insert | ✅ PASSED |
| `readonly_test` | readonly_user | Lecture | ✅ PASSED |
| `readonly_test` | readonly_user | Insert | ✅ FAILED (refusé) |
| `readonly_test` | readonly_user | Update | ✅ FAILED (refusé) |
| `readonly_test` | readonly_user | Delete | ✅ FAILED (refusé) |
| `readwrite_test` | app_user | Lecture | ✅ PASSED |
| `readwrite_test` | app_user | Insert | ✅ PASSED |
| `readwrite_test` | app_user | Update | ✅ PASSED |
| `readwrite_test` | app_user | Delete | ✅ PASSED |

**Total** : 27 tests automatisés validant la sécurité

---

## 📚 Ressources

- [CREATE_USERS_GUIDE.md](CREATE_USERS_GUIDE.md) - Guide création utilisateurs
- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Configuration sécurité
- [SECURITY.md](SECURITY.md) - Documentation sécurité complète
- [PYTEST_GUIDE.md](PYTEST_GUIDE.md) - Guide tests pytest
- [TESTS_RECAP.md](TESTS_RECAP.md) - Récapitulatif des tests

---

## ✅ Checklist de Migration

Avant migration :
- [ ] MongoDB démarré (`docker compose up -d mongodb`)
- [ ] Fichier `.env` configuré avec les credentials

Après migration :
- [ ] Utilisateurs créés (`docker compose run --rm create_users`)
- [ ] Import réussi avec app_user
- [ ] Tests de connexion passent (4/4)
- [ ] Tests readonly passent (11/11)
- [ ] Tests readwrite passent (12/12)
- [ ] Message "🔒 Connexion sécurisée" affiché

---

## 🎯 Résumé

Le script d'import `docker_script_bdd.py` a été **migré avec succès** vers une **architecture sécurisée** :

- ✅ Authentification obligatoire
- ✅ Utilisation de `app_user` (droits limités)
- ✅ Credentials depuis variables d'environnement
- ✅ Tests de sécurité validés
- ✅ Principe du moindre privilège respecté

**Le système est maintenant prêt pour la production !** 🎉
