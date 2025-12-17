# Architecture de l'Infrastructure

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARCHITECTURE GLOBALE                               │
│                    GreenAndCoop - Pipeline Météorologique                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                          SOURCES DE DONNÉES                               │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── InfoClimat API (HTTP REST)
         │    ├─── Stations: Bergues, Hazebrouck, Armentières, Lille-Lesquin
         │    ├─── Format: JSON
         │    └─── Fréquence: 10-30 minutes
         │
         └─── Weather Underground (Fichiers Excel)
              ├─── Stations: Ichtegem (BE), La Madeleine (FR)
              ├─── Format: CSV
              └─── Fréquence: Variable

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                         COUCHE D'INGESTION                                │
│                            AIRBYTE (Self-Hosted)                          │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Source Connector: HTTP API
         │    └─── Authentification, pagination, rate limiting
         │
         ├─── Source Connector: Local Files
         │    └─── Parsing CSV, détection encodage
         │
         ├─── Destination Connector: AWS S3
         │    └─── Format: JSONL (Airbyte format)
         │
         └─── Scheduler: Manuel ou planifié

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                        COUCHE DE STOCKAGE BRUT                            │
│                          AWS S3 (p8-weather-data)                         │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── 01_raw/ ──────────► Fichiers JSONL bruts depuis Airbyte
         ├─── 02_cleaned/ ──────► Fichiers JSON transformés (prêts MongoDB)
         └─── 03_archived/ ─────► Fichiers traités et importés (historique)
         │
         │    [Configuration S3]
         │    ├─── Region: eu-west-1
         │    ├─── Storage Class: Standard
         │    ├─── Versioning: Disabled
         │    ├─── Encryption: AES-256
         │    └─── Lifecycle: 90 jours → Glacier

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                     COUCHE DE TRANSFORMATION (ETL)                        │
│                        AWS ECS Fargate + Docker                           │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Service: weather-etl (desiredCount: 0 - Manuel)
         │    ├─── Image: weather-etl:latest (ECR)
         │    ├─── CPU: 0.5 vCPU | RAM: 1 GB
         │    ├─── Script: ABAI_P8_script_01_clean_data.py
         │    ├─── Mode: Watch S3 (WATCH_INTERVAL=3600s)
         │    └─── Logs: CloudWatch (/ecs/weather-etl)
         │
         └─── Transformations:
              ├─── Parsing Airbyte format
              ├─── Fusion multi-sources
              ├─── Conversions d'unités (°F→°C, mph→km/h, inHg→hPa, in→mm)
              ├─── Génération unique_key
              └─── Validation qualité

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                    COUCHE D'IMPORT ET VALIDATION                          │
│                        AWS ECS Fargate + Docker                           │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Service: mongodb-importer (desiredCount: 0 - Manuel)
         │    ├─── Image: weather-etl:latest (ECR)
         │    ├─── CPU: 0.25 vCPU | RAM: 0.5 GB
         │    ├─── Script: ABAI_P8_script_02_import_to_mongodb.py
         │    ├─── Mode: Watch S3 (WATCH_INTERVAL=300s)
         │    └─── Logs: CloudWatch (/ecs/mongodb-importer)
         │
         ├─── Tests qualité (script_03):
         │    ├─── Connexion MongoDB
         │    ├─── CRUD permissions
         │    ├─── Index unique_key
         │    └─── Upsert operations
         │
         └─── Service: s3-cleanup (desiredCount: 0 - Manuel)
              ├─── Image: weather-etl:latest (ECR)
              ├─── CPU: 0.25 vCPU | RAM: 0.5 GB
              ├─── Script: ABAI_P8_script_04_cleanup_s3.py
              ├─── Mode: Watch (CLEANUP_INTERVAL=3600s)
              └─── Actions: 02_cleaned/ → 03_archived/ | 01_raw/ → Suppression

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                       COUCHE DE STOCKAGE FINAL                            │
│                    MongoDB 7.0 sur AWS ECS Fargate                        │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Service: mongodb (desiredCount: 1 - ACTIF)
         │    ├─── Image: mongo:7.0 (ECR privé)
         │    ├─── CPU: 0.5 vCPU | RAM: 1 GB
         │    ├─── Port: 27017 (interne VPC)
         │    ├─── Volume: EFS (persistant)
         │    │    └─── Montage: /data/db
         │    ├─── Service Discovery: mongodb.weather-pipeline.local
         │    └─── Secrets Manager: credentials
         │
         ├─── Base de données: weather_data
         │    ├─── Collection: measurements (4,950 documents)
         │    │    ├─── Index: unique_key (unique)
         │    │    ├─── Index: id_station + dh_utc
         │    │    └─── Index: dh_utc (desc)
         │    │
         │    └─── Collection: import_metadata
         │         └─── Audit des imports
         │
         └─── Sauvegarde: EFS snapshots automatiques

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                      COUCHE DE MONITORING                                 │
│                   AWS CloudWatch + Mongo Express                          │
└───────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Service: mongo-express (desiredCount: 1 - ACTIF)
         │    ├─── Image: mongo-express:latest
         │    ├─── CPU: 0.25 vCPU | RAM: 0.5 GB
         │    ├─── Port: 8081 (public via ALB ou IP)
         │    ├─── URL: http://34.244.220.245:8081
         │    └─── Auth: Basic (admin/pass)
         │
         ├─── CloudWatch Dashboard: weather-pipeline-monitoring
         │    ├─── Métriques CPU/RAM (MongoDB, services)
         │    ├─── Running tasks count
         │    ├─── S3 bucket size & object count
         │    └─── Logs MongoDB (50 dernières entrées)
         │
         ├─── CloudWatch Logs:
         │    ├─── /ecs/weather-mongodb
         │    ├─── /ecs/weather-etl
         │    ├─── /ecs/mongodb-importer
         │    └─── /ecs/s3-cleanup
         │
         └─── Benchmark: ABAI_P8_script_05_benchmark_mongodb.py
              ├─── Write: 87,840 docs/s (1,000 docs)
              ├─── Read sequential: 230,325 docs/s
              ├─── Read indexed: 3,717 searches/s (0.27ms/search)
              ├─── Update: 3,503 updates/s
              └─── Aggregate: 4.1ms (6 groups)

              ▼ ▼ ▼

┌───────────────────────────────────────────────────────────────────────────┐
│                        COUCHE CONSOMMATION                                │
│                    AWS SageMaker / Notebooks Python                       │
└───────────────────────────────────────────────────────────────────────────┘
         │
         └─── Connexion MongoDB via PyMongo
              ├─── URI: mongodb://mongodb.weather-pipeline.local:27017
              ├─── Requêtes SQL-like avec aggregation framework
              └─── Export vers Pandas DataFrame pour ML
```

## Architecture réseau AWS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            AWS VPC (eu-west-1)                          │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ├─── Subnet AZ-1 (eu-west-1a) - Private
         │    ├─── ECS Tasks: mongodb, mongo-express, etl, importer
         │    └─── CIDR: 10.0.1.0/24
         │
         ├─── Subnet AZ-2 (eu-west-1b) - Private
         │    └─── CIDR: 10.0.2.0/24 (Haute disponibilité)
         │
         ├─── Security Group: weather-pipeline-sg
         │    ├─── Inbound: 27017 (MongoDB) - Internal only
         │    ├─── Inbound: 8081 (Mongo Express) - Public IP
         │    └─── Outbound: All traffic (S3, ECR, CloudWatch)
         │
         ├─── Service Discovery (Cloud Map)
         │    └─── mongodb.weather-pipeline.local → Private IP MongoDB
         │
         └─── EFS File System
              ├─── ID: fs-xxxxx
              ├─── Mount Target: AZ-1 & AZ-2
              └─── Performance: General Purpose (Bursting)
```

## Stack technique

### Infrastructure as Code
- **AWS CLI** : Déploiement services ECS
- **Docker Compose** : Orchestration locale
- **Task Definitions JSON** : Configuration ECS Fargate

### Containers & Registry
- **Docker** : Conteneurisation (Python 3.12-slim)
- **Amazon ECR** : Registry privé (weather-etl:latest, weather-mongodb:latest)
- **Amazon ECS Fargate** : Orchestration serverless

### Data Processing
- **Python 3.12** : Langage ETL
- **Pandas** : Manipulation DataFrames
- **Boto3** : SDK AWS (S3, Secrets Manager)
- **PyMongo** : Driver MongoDB

### Storage
- **AWS S3** : Stockage objet (3 dossiers)
- **MongoDB 7.0** : Base NoSQL
- **Amazon EFS** : Stockage persistant MongoDB

### Monitoring & Logs
- **CloudWatch Logs** : Logs centralisés
- **CloudWatch Dashboard** : Métriques temps réel
- **Mongo Express** : Interface web MongoDB

### Security
- **AWS Secrets Manager** : Credentials MongoDB
- **IAM Roles** : Permissions ECS (Task Execution Role, Task Role)
- **VPC Security Groups** : Isolation réseau

### CI/CD & Tools
- **Poetry** : Gestion dépendances Python
- **pytest** : Tests qualité
- **Git/GitHub** : Versioning code

## Dimensionnement actuel

### Services actifs (coût ~$1/jour)
- **MongoDB** : 0.5 vCPU, 1 GB RAM, EFS volume
- **Mongo Express** : 0.25 vCPU, 0.5 GB RAM

### Services manuels (coût $0 si arrêtés)
- **weather-etl** : 0.5 vCPU, 1 GB RAM
- **mongodb-importer** : 0.25 vCPU, 0.5 GB RAM
- **s3-cleanup** : 0.25 vCPU, 0.5 GB RAM

### Storage
- **S3** : ~3 MB (fichiers JSON)
- **EFS** : ~100 MB (base MongoDB)
- **ECR** : ~500 MB (images Docker)

## Haute disponibilité & Résilience

- ✅ **Multi-AZ** : Subnets dans 2 zones de disponibilité
- ✅ **Persistent Storage** : EFS avec snapshots automatiques
- ✅ **Service Discovery** : DNS interne pour résolution MongoDB
- ✅ **Auto-restart** : ECS redémarre automatiquement les tâches échouées
- ✅ **Upsert MongoDB** : Pas de doublons avec unique_key
- ❌ **Réplication MongoDB** : Non activée (single node)
- ❌ **Load Balancer** : Non nécessaire (pas de trafic public intense)

## Évolution future

- **Réplication MongoDB** : Replica Set 3 nodes pour HA
- **Auto-scaling ECS** : Scale basé sur CPU/RAM
- **Lambda** : Alternative à ECS pour tâches ponctuelles
- **API Gateway** : Exposition API REST pour Data Scientists
- **DynamoDB** : Alternative MongoDB pour scaling horizontal
