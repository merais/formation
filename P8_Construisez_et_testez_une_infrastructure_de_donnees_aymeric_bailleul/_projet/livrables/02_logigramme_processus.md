# Logigramme du Pipeline de Données

## Vue d'ensemble du processus ETL

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE DONNÉES MÉTÉOROLOGIQUES                  │
│                         GreenAndCoop - Forecast 2.0                     │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   SOURCES DE DONNÉES │
└──────────┬───────────┘
           │
           ├─── InfoClimat API (Bergues, Hazebrouck, Armentières, Lille-Lesquin)
           │
           └─── Weather Underground Excel (Ichtegem, La Madeleine)
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         ÉTAPE 1 : COLLECTE (Airbyte)                     │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── Airbyte Source: HTTP API (InfoClimat)
           │    └─── Format: JSON avec structure imbriquée Airbyte
           │
           ├─── Airbyte Source: File (Excel → CSV)
           │    └─── Format: CSV avec métadonnées stations
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  ÉTAPE 2 : STOCKAGE TEMPORAIRE (S3)                      │
│                         Bucket: p8-weather-data                          │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── Dossier: 01_raw/
           │    └─── Fichiers JSONL bruts depuis Airbyte
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              ÉTAPE 3 : TRANSFORMATION (Script ETL Python)                │
│                   ABAI_P8_script_01_clean_data.py                        │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── [Début] Lecture fichiers JSONL depuis S3
           │
           ├─── [Parsing] Décodage format Airbyte (_airbyte_data)
           │
           ├─── [Détection] Identification du type de source
           │    ├─── JSON API: Extraction stations multiples
           │    └─── Excel: Extraction nom station depuis chemin S3
           │
           ├─── [Fusion] Consolidation de tous les fichiers en DataFrame unique
           │
           ├─── [Nettoyage] Standardisation des données
           │    ├─── Conversion températures (°F → °C)
           │    ├─── Conversion vitesse vent (mph → km/h)
           │    ├─── Conversion pression (inHg → hPa)
           │    ├─── Conversion précipitations (in → mm)
           │    ├─── Conversion direction vent (texte → degrés)
           │    └─── Normalisation noms colonnes
           │
           ├─── [Enrichissement] Ajout métadonnées
           │    ├─── unique_key: id_station + dh_utc + sequence
           │    ├─── processed_at: timestamp traitement
           │    ├─── source_file: nom fichier source
           │    └─── nom_station: nom géographique
           │
           ├─── [Validation] Contrôle qualité
           │    ├─── Vérification doublons (unique_key)
           │    ├─── Validation types numériques
           │    ├─── Détection valeurs manquantes
           │    └─── Tests cohérence (température, humidité)
           │
           ├─── [Export] Sauvegarde JSON vers S3
           │    └─── Dossier: 02_cleaned/
           │
           └─── [Logs] Rapport de traitement
                ├─── Nombre fichiers traités
                ├─── Nombre enregistrements
                ├─── Stations détectées
                └─── Temps d'exécution
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│       ÉTAPE 4 : IMPORTATION MONGODB (Script Import + Watch)              │
│                  ABAI_P8_script_02_import_to_mongodb.py                  │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── [Watch] Surveillance dossier 02_cleaned/ (toutes les 5 min)
           │
           ├─── <Nouveau fichier détecté ?> ──[Non]──┐
           │    └─── [Oui]                           │
           │         │                                │
           │         ▼                                │
           ├─── [Tests] Suite tests MongoDB          │
           │    ├─── Connexion MongoDB                │
           │    ├─── Existence collection             │
           │    ├─── Permissions CRUD                 │
           │    ├─── Index unique_key                 │
           │    └─── Opérations upsert               │
           │    │                                     │
           │    └─── <Tests OK ?> ──[Non]─→ [Erreur] │
           │         └─── [Oui]                       │
           │              │                           │
           │              ▼                           │
           ├─── [Import] Insertion MongoDB           │
           │    ├─── Chargement JSON depuis S3       │
           │    ├─── Conversion types (str → Date)   │
           │    ├─── Upsert avec unique_key          │
           │    └─── Gestion doublons                │
           │    │                                     │
           │    └─── <Import réussi ?> ──[Non]──┐    │
           │         └─── [Oui]                  │    │
           │              │                      │    │
           │              ▼                      │    │
           ├─── [Métadonnées] Enregistrement    │    │
           │    ├─── Collection: import_metadata │    │
           │    ├─── Date import                 │    │
           │    ├─── Nombre documents            │    │
           │    └─── Durée traitement            │    │
           │                                      │    │
           └─── [Attente] 5 minutes ─────────────┴────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│          ÉTAPE 5 : STOCKAGE FINAL (MongoDB sur AWS ECS)                  │
│               Base: weather_data | Collection: measurements              │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── Données disponibles pour requêtes
           │
           ├─── Réplication: EFS volume persistant
           │
           └─── Monitoring: CloudWatch + Mongo Express
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              ÉTAPE 6 : NETTOYAGE S3 (Script Cleanup)                     │
│                    ABAI_P8_script_04_cleanup_s3.py                       │
└──────────────────────────────────────────────────────────────────────────┘
           │
           ├─── [Watch] Surveillance (toutes les 1h)
           │
           ├─── [Vérification] Données importées dans MongoDB
           │
           ├─── <Données en MongoDB ?> ──[Non]──┐
           │    └─── [Oui]                       │
           │         │                            │
           │         ▼                            │
           ├─── [Archivage] Déplacement vers     │
           │    └─── 03_archived/                 │
           │                                      │
           ├─── [Suppression] Nettoyage          │
           │    └─── 01_raw/                      │
           │                                      │
           └─── [Attente] 1 heure ───────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    UTILISATION FINALE (Data Science)                     │
│                          SageMaker / Notebooks                           │
└──────────────────────────────────────────────────────────────────────────┘
           │
           └─── Requêtes MongoDB pour modèles de prévision
```

## Légende des symboles

- **┌─┐ │ └─┘** : Boîtes représentant les étapes/processus
- **▼** : Flux de données descendant
- **├─── └───** : Connexions et branches
- **<Question ?>** : Point de décision (losange)
- **[Action]** : Opération/traitement (rectangle)

## Fréquences d'exécution

| Service | Fréquence | Mode |
|---------|-----------|------|
| Airbyte | Manuelle ou planifiée | Pull |
| ETL (script_01) | Continue (Watch S3) | Push |
| Import MongoDB (script_02) | 5 minutes | Watch |
| Cleanup S3 (script_04) | 1 heure | Watch |

## Points de contrôle qualité

1. **Post-Airbyte** : Vérification présence fichiers JSONL dans S3
2. **Post-ETL** : Validation doublons, types, valeurs manquantes
3. **Pré-Import** : Suite complète de tests MongoDB
4. **Post-Import** : Vérification count documents, métadonnées
5. **Pre-Cleanup** : Confirmation présence données dans MongoDB

## Gestion des erreurs

- **Échec Airbyte** : Logs Airbyte + alerte
- **Échec ETL** : Logs Python + fichier non traité reste dans 01_raw/
- **Échec Tests MongoDB** : Import annulé + logs détaillés
- **Échec Import** : Rollback + retry + alert
- **Échec Cleanup** : Fichiers conservés pour investigation

## Temps d'exécution moyens

- **ETL (4,950 records)** : ~3-5 secondes
- **Import MongoDB** : ~2-3 secondes
- **Tests qualité** : <1 seconde
- **Cleanup S3** : ~1-2 secondes

## Traçabilité

Chaque document MongoDB contient :
- `source_file` : Nom du fichier JSONL source
- `processed_at` : Timestamp du traitement ETL
- `unique_key` : Identifiant unique pour upsert/déduplication
