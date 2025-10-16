# 🔒 Sécurité MongoDB - Guide de Configuration

## Vue d'ensemble

Ce projet implémente plusieurs niveaux de sécurité pour la base de données MongoDB :

## 1. Authentification avec Trois Niveaux d'Accès

### 👑 Administrateur (admin)
- **Username**: `admin` (défini dans `.env`)
- **Rôles**: `userAdminAnyDatabase`, `readWriteAnyDatabase`
- **Permissions**: 
  - Créer/supprimer des bases de données
  - Gérer tous les utilisateurs
  - Accès en lecture/écriture sur toutes les bases
- **Usage**: Administration et maintenance du système

### 📝 Utilisateur Application (app_user)
- **Username**: `app_user` (défini dans `.env`)
- **Rôle**: `readWrite` sur `healthcare_db`
- **Permissions**:
  - Lire et écrire dans `healthcare_db`
  - Créer/modifier/supprimer des documents
  - Créer des index
- **Usage**: Utilisé par les scripts d'import et les tests

### 👁️ Utilisateur Lecture Seule (readonly_user)
- **Username**: `readonly_user` (défini dans `.env`)
- **Rôle**: `read` sur `healthcare_db`
- **Permissions**:
  - Lire uniquement les données de `healthcare_db`
  - Aucune modification possible
- **Usage**: Rapports, analyses, dashboards, audits

## 2. Configuration des Fichiers

### Fichier `.env` (Non versionné - dans .gitignore)
```env
# Identifiants MongoDB - À MODIFIER avant utilisation
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=SecureAdminPassword123!
MONGO_INITDB_DATABASE=healthcare_db
MONGO_APP_USERNAME=app_user
MONGO_APP_PASSWORD=SecureAppPassword123!
MONGO_READONLY_USERNAME=readonly_user
MONGO_READONLY_PASSWORD=SecureReadPassword123!
```

⚠️ **Important**: Changez tous les mots de passe par défaut avant de déployer en production !

### Script d'Initialisation MongoDB
- **Fichier**: `mongo-init/000-create-users.js`
- **Exécuté**: Au premier démarrage de MongoDB
- **Fonction**: Crée les trois utilisateurs avec leurs permissions respectives

## 3. Services Docker Sécurisés

### Service MongoDB
- Authentification activée avec les identifiants du fichier `.env`
- Les utilisateurs sont créés automatiquement au démarrage

### Service import_scripts
- Utilise `app_user` (lecture/écriture)
- Peut importer et modifier des données

### Service tests
- Utilise `app_user` (lecture/écriture)
- Peut tester les opérations CRUD

### Service readonly_test
- Utilise `readonly_user` (lecture seule)
- Teste que les modifications sont bien refusées

## 4. Utilisation

### Démarrer MongoDB avec sécurité
```bash
docker compose up -d mongodb
```

### Créer les utilisateurs (première fois seulement)

**Sur Windows PowerShell :**
```powershell
.\create-users.ps1
```

**Sur Linux/Mac :**
```bash
./create-users.sh
```

**Ou manuellement :**
```bash
docker exec healthcare_mongodb mongosh admin -u admin -p SecureAdminPassword123! --eval "db=db.getSiblingDB('healthcare_db'); db.createUser({user:'app_user',pwd:'SecureAppPassword123!',roles:[{role:'readWrite',db:'healthcare_db'}]}); db.createUser({user:'readonly_user',pwd:'SecureReadPassword123!',roles:[{role:'read',db:'healthcare_db'}]})"
```

### Tester l'utilisateur en lecture seule
```bash
docker compose run --rm readonly_test
```

### Exécuter les tests avec l'utilisateur app
```bash
docker compose run --rm tests
```

### Importer des données
```bash
docker compose run --rm import_scripts
```

## 5. Connexion Manuelle à MongoDB

### Avec l'admin
```bash
docker exec -it healthcare_mongodb mongosh -u admin -p SecureAdminPassword123! --authenticationDatabase admin
```

### Avec l'utilisateur app
```bash
docker exec -it healthcare_mongodb mongosh healthcare_db -u app_user -p SecureAppPassword123!
```

### Avec l'utilisateur readonly
```bash
docker exec -it healthcare_mongodb mongosh healthcare_db -u readonly_user -p SecureReadPassword123!
```

## 6. Bonnes Pratiques de Sécurité

### ✅ Ce qui est fait
- ✓ Authentification activée sur MongoDB
- ✓ Principe du moindre privilège (3 niveaux d'accès)
- ✓ Mots de passe stockés dans `.env` (non versionné)
- ✓ Variables d'environnement pour les connexions

### 🔄 Recommandations supplémentaires pour la production

1. **Mots de passe forts**
   - Minimum 16 caractères
   - Mélange de majuscules, minuscules, chiffres et symboles
   - Utiliser un gestionnaire de mots de passe

2. **Chiffrement TLS/SSL**
   - Activer TLS pour les connexions MongoDB
   - Utiliser des certificats SSL valides

3. **Réseau**
   - Ne pas exposer le port 27017 sur l'hôte (retirer `ports:` dans docker-compose.yml)
   - Utiliser un réseau Docker privé
   - Ajouter un pare-feu si exposé

4. **Sauvegardes**
   - Configurer des sauvegardes automatiques
   - Chiffrer les sauvegardes
   - Tester la restauration régulièrement

5. **Audit et Logs**
   - Activer les logs d'audit MongoDB
   - Surveiller les tentatives de connexion échouées
   - Mettre en place des alertes

6. **Rotation des mots de passe**
   - Changer les mots de passe régulièrement
   - Utiliser un coffre-fort de secrets (HashiCorp Vault, AWS Secrets Manager, etc.)

7. **Validation de schéma**
   - Définir des schémas JSON pour valider les données
   - Empêcher l'insertion de données malformées

## 7. Vérification de la Sécurité

### Test 1: Vérifier que l'authentification est requise
```bash
# Cette commande doit échouer (pas d'authentification)
docker exec -it healthcare_mongodb mongosh healthcare_db --eval "db.patients.find()"
```

### Test 2: Vérifier les permissions en lecture seule
```bash
# Doit réussir à lire
docker exec -it healthcare_mongodb mongosh healthcare_db -u readonly_user -p SecureReadPassword123! --eval "db.patients.countDocuments()"

# Doit échouer à écrire
docker exec -it healthcare_mongodb mongosh healthcare_db -u readonly_user -p SecureReadPassword123! --eval "db.patients.insertOne({test: 'fail'})"
```

## 8. Dépannage

### Erreur "Authentication failed"
- Vérifiez que le fichier `.env` est présent
- Vérifiez que les mots de passe sont corrects
- Assurez-vous que MongoDB a bien été initialisé (supprimez le volume si nécessaire)

### Réinitialiser MongoDB et les utilisateurs
```bash
# Arrêter et supprimer les conteneurs et volumes
docker compose down -v

# Redémarrer (les utilisateurs seront recréés)
docker compose up -d mongodb
```

## 9. Structure des Fichiers de Sécurité

```
.
├── .env                              # Identifiants (non versionné)
├── .gitignore                        # Contient .env
├── docker-compose.yml                # Configuration avec authentification
├── mongo-init/
│   └── 000-create-users.js          # Script de création des utilisateurs
└── SECURITY.md                       # Ce fichier
```

## 10. Checklist de Sécurité

Avant de déployer en production :

- [ ] Tous les mots de passe par défaut ont été changés
- [ ] Le fichier `.env` n'est pas versionné dans Git
- [ ] Le port MongoDB n'est pas exposé publiquement
- [ ] TLS/SSL est activé
- [ ] Les sauvegardes automatiques sont configurées
- [ ] Les logs d'audit sont activés
- [ ] Un plan de rotation des mots de passe est en place
- [ ] Les certificats SSL sont valides et à jour
- [ ] Un monitoring est en place
- [ ] Les alertes de sécurité sont configurées
