# Exécution du Pipeline Weather en Local

Ce guide explique comment exécuter l'infrastructure complète en local avec Docker Compose.

## Architecture Locale

L'infrastructure comprend 5 services Docker :

1. **mongodb** : Base de données MongoDB 7.0
2. **mongo-express** : Interface web MongoDB (port 8081)
3. **etl-pipeline** : Service ETL pour nettoyer les données S3
4. **mongodb-importer** : Service d'import automatique vers MongoDB
5. **s3-cleanup** : Service de nettoyage/archivage S3

## Prérequis

- Docker Desktop installé et démarré
- Fichier `.env` configuré avec les credentials AWS et MongoDB
- Accès au bucket S3 `p8-weather-data`

## Lancement

### 1. Démarrer l'infrastructure complète

```powershell
# Depuis le répertoire du projet
docker-compose up -d
```

Cette commande démarre tous les services en arrière-plan.

### 2. Vérifier l'état des services

```powershell
docker-compose ps
```

Vous devriez voir 5 services `running`.

### 3. Suivre les logs

```powershell
# Tous les services
docker-compose logs -f

# Service ETL uniquement
docker-compose logs -f etl-pipeline

# Service d'import uniquement
docker-compose logs -f mongodb-importer
```

## Accès aux services

- **Mongo Express** : http://localhost:8081
  - Login : `admin`
  - Password : `pass`

- **MongoDB** : `mongodb://admin:admin123@localhost:27017/`

## Fonctionnement

### Service ETL (etl-pipeline)

- Traite les fichiers depuis `s3://p8-weather-data/01_raw/`
- Fusionne tous les fichiers en un seul JSON nettoyé
- Supporte les données API (Météo France) et Excel (Ichtegem, LaMadeleine)
- Crée les `dh_utc` pour les données Excel à partir de la colonne `time`
- Génère des `unique_key` avec séquence pour éviter les doublons
- Dépose le fichier dans `02_cleaned/`
- **Mode continu** : S'exécute toutes les heures (WATCH_INTERVAL=3600s)

### Service Import (mongodb-importer)

- Surveille `s3://p8-weather-data/02_cleaned/`
- Importe automatiquement les nouveaux fichiers JSON
- Utilise `upsert` sur `unique_key` pour éviter les doublons
- Enregistre les métadonnées d'import dans `import_metadata`
- **Mode continu** : Vérifie toutes les 5 minutes (WATCH_INTERVAL=300s)

### Service Cleanup (s3-cleanup)

- Archive les fichiers importés de `02_cleaned/` vers `03_archived/`
- Vérifie que l'import est terminé avant d'archiver
- **Mode continu** : S'exécute toutes les heures (CLEANUP_INTERVAL=3600s)

## Corrections Appliquées

### Problème des doublons unique_key

**Symptôme** : Seulement 1,722 documents importés au lieu de 4,950.

**Cause** : Les données Excel avaient plusieurs jours de mesures avec la même heure (ex: `time="00:04:00"` répété 6-7 fois). La fonction `create_dh_utc_from_time()` utilisait `date.today()` pour tous les records, créant des `unique_key` identiques.

**Solution** : Ajout d'un numéro de séquence aux `unique_key` pour différencier les doublons :
```python
# Avant
unique_key = "EXCEL_ICHTEGEM_2025-12-10T00:04:00.000Z"

# Après (pour doublons)
unique_key = "EXCEL_ICHTEGEM_2025-12-10T00:04:00.000Z_seq1"
unique_key = "EXCEL_ICHTEGEM_2025-12-10T00:04:00.000Z_seq2"
```

### Problème des données Excel sans dh_utc

**Symptôme** : 3,807 records Excel avec `dh_utc=""` et `unique_key=""`.

**Cause** : Les données Excel avaient une colonne `dh_utc` pré-créée mais vide (chaînes vides `""`). La vérification `.isna().all()` ne détectait pas les chaînes vides.

**Solution** : Traitement ligne par ligne avec masque pour identifier et remplir uniquement les lignes avec `dh_utc` vide :
```python
mask_empty = df['dh_utc'].isna() | (df['dh_utc'].astype(str).str.strip() == '')
df.loc[mask_empty, 'dh_utc'] = ...  # Créer dh_utc uniquement pour ces lignes
```

## Commandes Utiles

### Redémarrer un service

```powershell
# Redémarrer le service ETL
docker-compose restart etl-pipeline

# Redémarrer le service d'import
docker-compose restart mongodb-importer
```

### Forcer un nouveau traitement ETL

```powershell
# Arrêter et redémarrer pour forcer l'exécution immédiate
docker-compose restart etl-pipeline
```

### Nettoyer et reconstruire

```powershell
# Arrêter et supprimer tous les conteneurs
docker-compose down

# Reconstruire les images
docker-compose build

# Redémarrer
docker-compose up -d
```

### Réinitialiser MongoDB

```powershell
# Arrêter les services
docker-compose down

# Supprimer le volume MongoDB (ATTENTION: perte de données)
docker volume rm weather-mongodb-data

# Redémarrer
docker-compose up -d
```

## Monitoring

### Vérifier le nombre de documents

Via Mongo Express : http://localhost:8081
- Database : `weather_data`
- Collection : `measurements`
- Nombre attendu : **4,950 documents**

### Distribution par station

```javascript
// Dans Mongo Express > Execute
db.measurements.aggregate([
  { $group: { _id: "$id_station", count: { $count: {} } } },
  { $sort: { count: -1 } }
])
```

Résultat attendu :
- EXCEL_LAMADELEINE : 1,908
- EXCEL_ICHTEGEM : 1,899
- 00052 (Armentières) : 361
- 000R5 (Bergues) : 361
- STATIC0010 (Hazebrouck) : 361
- 07015 (Lille-Lesquin) : 60

## Dépannage

### Le service ETL ne démarre pas

```powershell
# Vérifier les logs
docker-compose logs etl-pipeline

# Vérifier les credentials AWS dans .env
cat .env | Select-String "AWS_ACCESS_KEY_ID"
```

### MongoDB ne démarre pas

```powershell
# Vérifier le healthcheck
docker-compose ps mongodb

# Si "unhealthy", vérifier les logs
docker-compose logs mongodb
```

### Import bloqué

```powershell
# Vérifier les métadonnées d'import
# Via Mongo Express : collection import_metadata

# Redémarrer le service
docker-compose restart mongodb-importer
```

## Arrêt

```powershell
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (ATTENTION: perte de données)
docker-compose down -v
```
