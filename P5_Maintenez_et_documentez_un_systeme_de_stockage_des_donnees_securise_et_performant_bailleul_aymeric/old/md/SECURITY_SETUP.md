# 🔒 Guide de Configuration de la Sécurité MongoDB

## Résumé

Ce projet utilise **3 niveaux d'accès** pour sécuriser MongoDB :
- 👑 **admin** : Gestion complète
- 📝 **app_user** : Lecture/écriture sur healthcare_db
- 👁️ **readonly_user** : Lecture seule sur healthcare_db

---

## 🚀 Configuration Initiale (À faire une seule fois)

### Étape 1 : Démarrer MongoDB
```bash
docker compose up -d mongodb
```

### Étape 2 : Créer les utilisateurs

#### Sur Windows PowerShell :
```powershell
.\create-users.ps1
```

#### Sur Linux/Mac :
```bash
chmod +x create-users.sh
./create-users.sh
```

---

## 📋 Scripts disponibles

### `create-users.ps1` (Windows)
- ✅ **À UTILISER** : Script PowerShell pour créer les utilisateurs
- Crée automatiquement app_user et readonly_user
- Vérifie que les utilisateurs sont bien créés

### `create-users.sh` (Linux/Mac)
- ✅ **À UTILISER** : Équivalent bash pour Linux/Mac

### ~~`mongo-init/000-create-users.js`~~
- ❌ **SUPPRIMÉ** : Ne fonctionnait pas car les scripts mongo-init ne s'exécutent qu'à la première initialisation

---

## 🧪 Tester la Sécurité

### Test 1 : Importer des données (app_user)
```bash
docker compose run --rm import_scripts
```
✅ Devrait réussir (app_user a les droits d'écriture)

### Test 2 : Lecture seule (readonly_user)
```bash
docker compose run --rm readonly_test
```
✅ Devrait lire les données
❌ Devrait échouer pour les opérations d'écriture

---

## 📖 Fichiers de Sécurité

| Fichier | Description | Versionné Git |
|---------|-------------|---------------|
| `.env` | Mots de passe et identifiants | ❌ NON (dans .gitignore) |
| `create-users.ps1` | Script PowerShell de création | ✅ OUI |
| `create-users.sh` | Script bash de création | ✅ OUI |
| `SECURITY.md` | Documentation complète | ✅ OUI |
| `docker-compose.yml` | Configuration Docker | ✅ OUI |

---

## ⚠️ Important

1. **Ne jamais versionner le fichier `.env`** (déjà dans .gitignore)
2. **Changer les mots de passe par défaut** avant la production
3. **Exécuter create-users une seule fois** (après la première initialisation)

---

## 🔍 Vérification Manuelle

```bash
# Se connecter à MongoDB en tant qu'admin
docker exec -it healthcare_mongodb mongosh admin -u admin -p SecureAdminPassword123!

# Lister les utilisateurs de healthcare_db
use healthcare_db
db.getUsers()
```

---

## 🆘 Dépannage

### Les utilisateurs existent déjà
- Normal si vous avez déjà exécuté le script
- Ignorez les erreurs "already exists"

### Réinitialiser complètement
```bash
# ATTENTION : Supprime toutes les données !
docker compose down -v
docker compose up -d mongodb
# Attendre 10 secondes
.\create-users.ps1  # ou ./create-users.sh
```

### Authentication failed
- Vérifiez que les utilisateurs ont bien été créés
- Vérifiez le fichier `.env` (mots de passe corrects)
- Relancez `create-users.ps1`
