# Guide de Création des Utilisateurs MongoDB

## 📋 Vue d'ensemble

Le script `create_users.py` crée automatiquement les utilisateurs MongoDB avec les permissions appropriées, en utilisant PyMongo et les credentials du fichier `.env`.

---

## 🎯 Utilisateurs créés

| Utilisateur | Rôle | Base de données | Permissions |
|-------------|------|-----------------|-------------|
| `app_user` | `readWrite` | `healthcare_db` | Lecture + Écriture complète |
| `readonly_user` | `read` | `healthcare_db` | Lecture seule |

---

## 🚀 Utilisation

### Méthode recommandée : Docker Compose

```bash
# Créer les utilisateurs
docker compose run --rm create_users
```

**Avantages** :
- ✅ Fonctionne sur tous les systèmes (Windows, Linux, Mac)
- ✅ Pas besoin d'installer Python localement
- ✅ Accès direct au réseau Docker
- ✅ Variables d'environnement automatiquement chargées

### Méthode alternative : Exécution locale

```bash
# Windows PowerShell
& "C:/Program Files/Python313/python.exe" create_users.py

# Linux/Mac
python3 create_users.py
```

**Prérequis** :
- Python 3.13+
- `pip install pymongo python-dotenv`
- MongoDB accessible sur localhost:27017
- Fichier `.env` présent

---

## 📝 Configuration requise

### Fichier `.env`

Le script lit automatiquement les credentials depuis `.env` :

```env
# Administrateur (créateur des utilisateurs)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=SecureAdminPassword123!

# Utilisateur application (lecture/écriture)
MONGO_APP_USERNAME=app_user
MONGO_APP_PASSWORD=SecureAppPassword123!

# Utilisateur lecture seule
MONGO_READONLY_USERNAME=readonly_user
MONGO_READONLY_PASSWORD=SecureReadPassword123!
```

---

## 🔧 Fonctionnement

### 1. Connexion multi-hôtes

Le script essaie de se connecter dans cet ordre :
1. `mongodb` (réseau Docker)
2. `localhost` (exécution locale)
3. `127.0.0.1` (alternative locale)

### 2. Création des utilisateurs

Pour chaque utilisateur :
```python
db.command(
    "createUser",
    username,
    pwd=password,
    roles=[{"role": role, "db": "healthcare_db"}]
)
```

### 3. Gestion des doublons

Si un utilisateur existe déjà :
- ⚠️ Affiche un avertissement
- ✅ Continue sans erreur
- Ne modifie pas l'utilisateur existant

### 4. Vérification

Le script vérifie que tous les utilisateurs ont été créés :
```python
db.command("usersInfo")
```

---

## 📊 Sortie du script

### Succès complet

```
============================================================
MongoDB User Creation Script
============================================================
🔧 Creating MongoDB users...
   Trying to connect to mongodb...
   ✓ Connected to MongoDB at mongodb
   ✓ app_user created successfully (readWrite permissions)
   ✓ readonly_user created successfully (read permissions)

🔍 Verifying users...
   Found 2 user(s) in healthcare_db:
   - app_user: readWrite
   - readonly_user: read

✅ All users verified successfully!

============================================================
✅ User creation completed!
============================================================
```

### Utilisateurs existants

```
🔧 Creating MongoDB users...
   Trying to connect to mongodb...
   ✓ Connected to MongoDB at mongodb
   ⚠ app_user already exists
   ⚠ readonly_user already exists

🔍 Verifying users...
   Found 2 user(s) in healthcare_db:
   - app_user: readWrite
   - readonly_user: read

✅ All users verified successfully!
```

### Erreur de connexion

```
🔧 Creating MongoDB users...
   Trying to connect to mongodb...
   ✗ Failed to connect to mongodb: ServerSelectionTimeoutError
   Trying to connect to localhost...
   ✗ Failed to connect to localhost: ServerSelectionTimeoutError
   Trying to connect to 127.0.0.1...
   ✗ Failed to connect to 127.0.0.1: ServerSelectionTimeoutError
   ❌ Could not connect to MongoDB on any host

❌ Failed to create users
```

---

## 🐳 Architecture Docker

### Dockerfile.create_users

```dockerfile
FROM python:3.13-slim
WORKDIR /app

# Installation des dépendances
RUN pip install --no-cache-dir pymongo python-dotenv

# Copie des fichiers
COPY create_users.py .
COPY .env .

CMD ["python", "create_users.py"]
```

### Service docker-compose

```yaml
create_users:
  build:
    context: .
    dockerfile: Dockerfile.create_users
  container_name: healthcare_create_users
  environment:
    MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
    MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
    MONGO_APP_USERNAME: ${MONGO_APP_USERNAME}
    MONGO_APP_PASSWORD: ${MONGO_APP_PASSWORD}
    MONGO_READONLY_USERNAME: ${MONGO_READONLY_USERNAME}
    MONGO_READONLY_PASSWORD: ${MONGO_READONLY_PASSWORD}
  depends_on:
    mongodb:
      condition: service_healthy
  networks:
    - healthcare_network
```

---

## 🛠️ Dépannage

### Erreur : `.env file not found`

**Solution** :
```bash
# Vérifier la présence du .env
ls -la .env  # Linux/Mac
dir .env     # Windows

# Créer le .env s'il manque
cp .env.example .env  # Si vous avez un template
```

### Erreur : `Authentication failed`

**Causes possibles** :
1. MongoDB pas démarré
2. Mauvais credentials dans `.env`
3. Utilisateur admin pas créé

**Solutions** :
```bash
# Vérifier que MongoDB est démarré
docker ps | grep healthcare_mongodb

# Redémarrer MongoDB
docker compose restart mongodb

# Réinitialiser complètement
docker compose down -v
docker compose up -d mongodb
```

### Erreur : `Missing environment variables`

**Solution** :
Vérifier que toutes les variables sont dans `.env` :
- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`
- `MONGO_APP_USERNAME`
- `MONGO_APP_PASSWORD`
- `MONGO_READONLY_USERNAME`
- `MONGO_READONLY_PASSWORD`

### Erreur : `Could not connect to MongoDB on any host`

**Solutions** :
```bash
# 1. Vérifier que MongoDB est healthy
docker compose ps

# 2. Vérifier les logs MongoDB
docker compose logs mongodb

# 3. Attendre que MongoDB soit prêt
docker compose run --rm create_users
```

---

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne jamais versionner le `.env`**
   ```bash
   # Ajouté dans .gitignore
   .env
   ```

2. **Utiliser des mots de passe forts**
   ```bash
   # Minimum recommandé
   - 12 caractères
   - Majuscules + minuscules
   - Chiffres
   - Caractères spéciaux
   ```

3. **Changer les mots de passe par défaut**
   ```bash
   # En production, modifier TOUS les mots de passe dans .env
   ```

4. **Limiter les permissions**
   ```bash
   # app_user : seulement readWrite sur healthcare_db
   # readonly_user : seulement read sur healthcare_db
   ```

---

## 🔄 Workflow typique

### Première installation

```bash
# 1. Démarrer MongoDB
docker compose up -d mongodb

# 2. Créer les utilisateurs
docker compose run --rm create_users

# 3. Vérifier
docker exec healthcare_mongodb mongosh admin -u admin -p SecureAdminPassword123! \
  --eval "db.getSiblingDB('healthcare_db').getUsers()"
```

### Réinitialisation

```bash
# Supprimer tous les utilisateurs et recréer
docker compose down -v
docker compose up -d mongodb
docker compose run --rm create_users
```

### Ajout d'un nouvel utilisateur

Modifier `create_users.py` :
```python
# Ajouter dans create_users()
success_new = create_user(
    db,
    'new_user',
    'password',
    'read'  # ou 'readWrite'
)
```

---

## 📚 Ressources

- [Documentation MongoDB - User Management](https://docs.mongodb.com/manual/tutorial/manage-users-and-roles/)
- [Documentation PyMongo](https://pymongo.readthedocs.io/)
- [Documentation python-dotenv](https://github.com/theskumar/python-dotenv)

---

## ✅ Checklist

Avant d'utiliser le script :

- [ ] MongoDB est démarré (`docker compose up -d mongodb`)
- [ ] Fichier `.env` existe et contient toutes les variables
- [ ] Les mots de passe sont sécurisés (production)
- [ ] Image Docker construite (`docker compose build create_users`)

Après exécution :

- [ ] Message "✅ User creation completed!" affiché
- [ ] 2 utilisateurs listés dans la vérification
- [ ] Tests passent (`docker compose run --rm tests`)

---

**🎉 Les utilisateurs sont prêts à être utilisés !**
