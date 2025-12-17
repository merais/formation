# Justification des Choix Techniques

## Vue d'ensemble

Ce document présente et justifie les choix technologiques effectués pour le projet Forecast 2.0. Chaque décision a été prise en tenant compte des contraintes du projet, des besoins des Data Scientists et des exigences de GreenAndCoop.

---

## 1. Choix de la base de données : MongoDB

### Décision
**MongoDB 7.0** (base de données NoSQL orientée documents)

### Alternatives considérées
- PostgreSQL (SQL relationnel)
- DynamoDB (NoSQL AWS natif)
- InfluxDB (Time Series Database)

### Justification

#### ✅ Avantages MongoDB pour ce projet

1. **Flexibilité du schéma**
   - Les stations InfoClimat et Weather Underground fournissent des données avec des **formats différents**
   - Certains champs sont présents uniquement dans une source (ex: `solar`, `uv` pour WU)
   - MongoDB accepte nativement les champs **nullable** sans schéma rigide
   - Facilite l'ajout de **nouvelles sources** sans migration complexe

2. **Structure documentaire naturelle**
   - Une mesure météo = un document JSON
   - Pas de normalisation nécessaire (pas de tables multiples)
   - Requêtes simples pour les Data Scientists : `db.measurements.find({ "id_station": "07015" })`

3. **Performance**
   - **Index efficaces** : unique_key (0.27 ms/recherche)
   - **Agrégations puissantes** : framework d'agrégation (4.1 ms pour group by)
   - **Scaling horizontal** : Sharding natif si besoin (> 1M documents)

4. **Écosystème Python**
   - **PyMongo** : driver officiel très mature
   - **Pandas** : intégration native (DataFrame ↔ MongoDB)
   - **SageMaker** : Support MongoDB Atlas (si migration cloud complète)

#### ❌ Pourquoi pas PostgreSQL ?

- Schéma rigide nécessite des migrations complexes pour ajouter champs
- Normalisation (tables multiples) complique les requêtes pour Data Scientists
- Moins adapté pour données semi-structurées (JSON imbriqué)
- Performances d'agrégation inférieures à MongoDB pour ce type de workload

#### ❌ Pourquoi pas DynamoDB ?

- Coût élevé pour volumes modérés (facturé au read/write request)
- Moins de flexibilité pour agrégations complexes
- Courbe d'apprentissage pour Data Scientists (vs MongoDB = JSON familier)
- Dépendance forte à AWS (lock-in)

#### ❌ Pourquoi pas InfluxDB ?

- Optimisé pour time-series mais **overkill** pour ce projet (4,950 docs)
- Moins de support Python/Pandas que MongoDB
- Complexité de déploiement supérieure (clustering)
- Pas de gain significatif pour notre volumétrie

### Conclusion
MongoDB offre le **meilleur compromis** entre flexibilité, performance et simplicité d'usage pour les Data Scientists.

---

## 2. Choix de l'orchestration : Docker + AWS ECS Fargate

### Décision
**Docker Compose** (local) + **AWS ECS Fargate** (production)

### Alternatives considérées
- Kubernetes (EKS)
- AWS Lambda + Step Functions
- EC2 + Docker Compose

### Justification

#### ✅ Avantages Docker + ECS Fargate

1. **Containerisation (Docker)**
   - **Reproductibilité** : Environnement identique local ↔ production
   - **Isolation** : Chaque service (ETL, MongoDB, Importer) dans son conteneur
   - **Portabilité** : Peut migrer vers GCP, Azure sans refonte
   - **Versioning** : ECR permet de rollback facilement (tags d'image)

2. **ECS Fargate (serverless)**
   - **Pas de gestion de serveurs** : AWS gère l'infrastructure
   - **Scaling automatique** : ECS peut augmenter/diminuer les tâches selon charge
   - **Coût optimisé** : Paiement à l'usage (0.5 vCPU = $0.028/h)
   - **Intégration AWS** : CloudWatch, Secrets Manager, VPC natifs

3. **Simplicité vs Kubernetes**
   - **Courbe d'apprentissage** : ECS plus simple que Kubernetes
   - **Maintenance réduite** : Pas de cluster control plane à gérer
   - **Suffisant pour notre échelle** : 5 services, pas besoin de K8s pour ça

#### ❌ Pourquoi pas Kubernetes (EKS) ?

- **Complexité excessive** : Overhead de gestion du cluster K8s
- **Coût élevé** : Control plane EKS = $73/mois + worker nodes
- **Over-engineering** : 5 services ne nécessitent pas K8s
- **Compétences** : Équipe plus familière avec Docker qu'avec K8s

#### ❌ Pourquoi pas Lambda ?

- **Timeout** : Lambda = 15 min max, ETL peut prendre plus longtemps si volume élevé
- **Cold start** : Latence initiale (0.5-3s) pas idéale pour watch S3 fréquent
- **State** : Lambda stateless, MongoDB nécessite état persistant
- **Complexité** : Step Functions complexifie l'orchestration vs ECS simple

#### ❌ Pourquoi pas EC2 + Docker Compose ?

- **Gestion serveurs** : Patchs OS, monitoring, scaling manuel
- **Coût** : Instance EC2 toujours allumée ($30-50/mois) vs Fargate à l'usage
- **Disponibilité** : Pas de haute disponibilité automatique (single point of failure)

---

### Tableau Comparatif : ECS Fargate vs EC2 + Docker Compose

| Critère | **✅ ECS Fargate** | ❌ EC2 + Docker Compose |
|---------|-------------------|-------------------------|
| **Haute disponibilité** | ✅ Multi-AZ automatique<br>Pas de single point of failure | ❌ Single-AZ<br>Si EC2 tombe, tout s'arrête |
| **Maintenance** | ✅ Zéro maintenance<br>AWS gère OS + patchs | ❌ ~16h/mois<br>Patchs OS + Docker manuels |
| **Scaling** | ✅ Automatique<br>Selon charge CPU/RAM | ❌ Manuel<br>Provisionner instance plus grosse |
| **Coût avec HA** | ✅ $100-120/mois<br>HA incluse | ❌ $120-160/mois<br>2 instances + Load Balancer |
| **Déploiement** | ✅ 1 clic<br>Rollback instantané | ❌ SSH manuel<br>`git pull + docker-compose up` |
| **Monitoring** | ✅ CloudWatch intégré<br>Métriques + Logs centralisés | ❌ Logs locaux<br>Scripts custom requis |

#### 🎯 Verdict

| | ECS Fargate | EC2 + Docker Compose |
|---|-------------|----------------------|
| **Usage** | ⭐ Production | 🛠️ Dev local uniquement |
| **Disponibilité** | 99.9% | 95% |
| **Maintenance/mois** | 2h | 16h |
| **Coût réel avec HA** | $110 | $140 |

**💡 Conclusion** : ECS Fargate = **moins cher + zéro maintenance + HA native**

---

### Conclusion
ECS Fargate offre la **simplicité de Docker** avec le **scaling et la résilience du cloud**, sans la complexité de Kubernetes.

---

## 3. Choix du stockage : AWS S3 + Amazon EFS

### Décision
- **S3** : Stockage des fichiers JSONL bruts et transformés
- **EFS** : Volume persistant pour MongoDB (/data/db)

### Alternatives considérées
- EBS (Elastic Block Store)
- S3 uniquement (MongoDB Atlas ou DocumentDB)

### Justification

#### ✅ AWS S3 pour fichiers intermédiaires

1. **Durabilité** : 99.999999999% (11 nines)
2. **Coût** : $0.023/GB/mois (3 MB = $0.0007/mois = quasi gratuit)
3. **Lifecycle policies** : Archivage automatique vers Glacier après 90 jours
4. **Versioning** : Peut récupérer fichiers supprimés accidentellement
5. **Intégration** : Boto3 (SDK Python) très mature

#### ✅ Amazon EFS pour MongoDB

1. **Multi-AZ** : Haute disponibilité automatique (données répliquées)
2. **Élasticité** : Taille s'ajuste automatiquement (pay-per-use)
3. **Compatibilité** : Montage NFS standard (pas de refonte MongoDB)
4. **Snapshots** : Sauvegardes automatiques quotidiennes

#### ❌ Pourquoi pas EBS ?

- **Single-AZ** : Attaché à une seule zone de disponibilité (risque de perte)
- **Taille fixe** : Nécessite provisioning manuel
- **Migration complexe** : Si changement de taille ou AZ

#### ❌ Pourquoi pas MongoDB Atlas ou DocumentDB ?

- **Coût élevé** : Atlas = $57/mois minimum, DocumentDB = $70/mois
- **Lock-in** : DocumentDB = propriétaire AWS (pas 100% compatible MongoDB)
- **Over-engineering** : Managed service pas nécessaire pour 5k documents
- **Apprentissage** : Self-hosted MongoDB plus pédagogique

### Conclusion
**S3 + EFS** offrent le **meilleur compromis coût/résilience** pour ce projet, avec possibilité de migrer vers Atlas/DocumentDB si volumétrie explose.

---

## 4. Choix de l'ETL : Python + Pandas

### Décision
Scripts Python avec **Pandas** pour transformations

### Alternatives considérées
- Apache Spark
- AWS Glue (PySpark serverless)
- dbt (data build tool)

### Justification

#### ✅ Avantages Python + Pandas

1. **Simplicité**
   - Code lisible et maintenable
   - Pas de cluster Spark à gérer
   - Debugging facile (print, logs)

2. **Performance suffisante**
   - 4,950 documents en **3-5 secondes**
   - Pandas optimisé en C (numpy backend)
   - Pas besoin de distribué pour cette volumétrie

3. **Écosystème**
   - Boto3 pour S3, PyMongo pour MongoDB
   - Intégration native Jupyter Notebooks (Data Scientists)
   - Tests avec pytest

4. **Flexibilité**
   - Conversions d'unités (°F→°C) très simples
   - Fusion multi-sources avec `pd.concat()`
   - Validation avec masques Pandas

#### ❌ Pourquoi pas Spark ?

- **Over-engineering** : Spark pour 5k docs = tuer mouche avec bazooka
- **Complexité** : Cluster à gérer, configuration lourde
- **Coût** : EMR cluster = $100-200/mois minimum
- **Latency** : Spark a un overhead de démarrage (JVM, shuffle)

#### ❌ Pourquoi pas AWS Glue ?

- **Coût** : $0.44/DPU/heure, minimum 2 DPUs = $0.88/h
- **Cold start** : 1-2 minutes pour démarrer job Glue
- **Debugging difficile** : Logs CloudWatch moins accessibles

#### ❌ Pourquoi pas dbt ?

- **SQL-centric** : dbt optimisé pour transformations SQL dans warehouse
- **Pas adapté** : Nos données viennent de fichiers JSON/CSV, pas d'une BDD
- **Courbe d'apprentissage** : Nécessite apprentissage de Jinja + YAML

### Conclusion
**Python + Pandas** est le choix **pragmatique et efficient** pour ce volume de données, avec possibilité de migrer vers Spark si volumétrie > 1M documents.

---

## 5. Choix de la collecte : Airbyte

### Décision
**Airbyte** (self-hosted) pour ingestion des sources

### Alternatives considérées
- Scripts Python maison (requests + pandas)
- AWS Glue Crawlers
- Fivetran (SaaS)

### Justification

#### ✅ Avantages Airbyte

1. **Connecteurs prêts à l'emploi**
   - HTTP API (InfoClimat)
   - Local Files (Excel WU)
   - S3 destination native

2. **Standardisation**
   - Format JSONL Airbyte unifié
   - Gestion erreurs/retries automatique
   - Logging et monitoring intégré

3. **Évolutivité**
   - +300 connecteurs disponibles
   - Ajout nouvelles sources = quelques clics
   - Pas de code Python custom à maintenir

4. **Open-source**
   - Gratuit, self-hosted
   - Communauté active
   - Pas de lock-in

#### ❌ Pourquoi pas scripts Python maison ?

- **Maintenance** : Code custom à maintenir pour chaque source
- **Gestion erreurs** : Retries, exponential backoff à coder manuellement
- **Pas de monitoring** : Logs manuels, pas de dashboard
- **Évolutivité** : Ajouter source = coder nouveau script

#### ❌ Pourquoi pas Fivetran ?

- **Coût** : $1,000-2,000/mois (pricing entreprise)
- **Lock-in** : SaaS propriétaire
- **Overkill** : Pour 2-3 sources, trop cher

#### ❌ Pourquoi pas AWS Glue Crawlers ?

- **Limité** : Optimisé pour S3/RDS, pas pour API HTTP
- **Coût** : $0.44/h par crawler
- **Moins flexible** : Airbyte plus de connecteurs

### Conclusion
**Airbyte** offre le **meilleur rapport simplicité/coût/flexibilité** pour l'ingestion de données hétérogènes.

---

## 6. Choix du monitoring : CloudWatch + Mongo Express

### Décision
- **CloudWatch** : Métriques + Logs + Dashboard
- **Mongo Express** : Interface web MongoDB

### Alternatives considérées
- Grafana + Prometheus
- Datadog (SaaS)
- MongoDB Compass (desktop)

### Justification

#### ✅ Avantages CloudWatch

1. **Intégration native AWS**
   - Métriques ECS automatiques (CPU, RAM)
   - Logs centralisés (/ecs/*)
   - Dashboard créé en 1 commande

2. **Coût**
   - Gratuit pour 3 dashboards + 10 métriques
   - Logs : $0.50/GB (< $1/mois pour nous)

3. **Simplicité**
   - Pas d'installation requise
   - API/CLI pour automation

#### ✅ Avantages Mongo Express

1. **Simplicité**
   - Interface web accessible via navigateur
   - Pas d'installation desktop requise
   - Authentification intégrée

2. **Fonctionnalités**
   - CRUD documents
   - Exécution requêtes
   - Visualisation index

#### ❌ Pourquoi pas Grafana + Prometheus ?

- **Complexité** : Nécessite installer Prometheus + Grafana + Exporters
- **Maintenance** : Deux services supplémentaires à gérer
- **Coût** : 2 conteneurs ECS = $0.04/h = $30/mois

#### ❌ Pourquoi pas Datadog ?

- **Coût** : $15/host/mois minimum = $75/mois pour 5 services
- **Overkill** : Pour monitoring basique, trop cher

### Conclusion
**CloudWatch + Mongo Express** offrent un **monitoring complet à coût quasi nul**, avec intégration AWS native.

---

## 7. Choix de l'architecture réseau : VPC privé

### Décision
- **VPC privé** avec subnets multi-AZ
- **Service Discovery** (Cloud Map) pour résolution DNS interne
- **Pas de Load Balancer** (accès direct via IP publique Mongo Express)

### Justification

#### ✅ Sécurité

1. **MongoDB isolé** : Pas d'exposition Internet (port 27017 fermé)
2. **Service Discovery** : mongodb.weather-pipeline.local résolu en interne
3. **Security Groups** : Firewall contrôlant trafic entrant/sortant

#### ✅ Performance

1. **Latence réduite** : Communication interne VPC < 1 ms
2. **Pas de NAT** : Trafic direct entre services ECS

#### ✅ Coût

1. **Pas de Load Balancer** : $20/mois économisés
2. **NAT Gateway désactivé** : $45/mois économisés
3. **Total économie** : $65/mois

### Conclusion
**VPC privé avec Service Discovery** offre **sécurité et performance** à coût minimal.

---

## Synthèse des choix

| Composant | Choix | Justification principale |
|-----------|-------|-------------------------|
| **Base de données** | MongoDB 7.0 | Flexibilité schéma + Performance |
| **Orchestration** | ECS Fargate | Simplicité + Coût optimisé |
| **Stockage fichiers** | S3 | Durabilité + Coût minimal |
| **Stockage MongoDB** | EFS | Multi-AZ + Élasticité |
| **ETL** | Python + Pandas | Simplicité + Performance suffisante |
| **Ingestion** | Airbyte | Connecteurs prêts + Open-source |
| **Monitoring** | CloudWatch | Intégration AWS + Gratuit |
| **Interface MongoDB** | Mongo Express | Simplicité + Web-based |
| **Réseau** | VPC privé | Sécurité + Performance |

## Trade-offs assumés

### Choix pragmatiques

1. **MongoDB single-node vs Replica Set**
   - **Trade-off** : Disponibilité (99.9% vs 99.99%)
   - **Justification** : Coût (0.5 vCPU vs 1.5 vCPU) + Volumétrie faible (5k docs)
   - **Évolution** : Migrer vers Replica Set si criticité augmente

2. **EFS vs EBS**
   - **Trade-off** : Performance I/O (EBS io2 = 2-3x plus rapide)
   - **Justification** : Coût ($0.30/GB vs $0.125/GB) + Haute dispo Multi-AZ
   - **Évolution** : Migrer vers EBS io2 si latence I/O devient critique

3. **Fargate vs EC2**
   - **Trade-off** : Coût unitaire (Fargate 20% plus cher que EC2)
   - **Justification** : Pas de gestion infra + Scaling automatique
   - **Évolution** : Migrer vers EC2 si usage > 80% du temps (break-even)

### Décisions réversibles

✅ **Facilement migrables** :
- MongoDB → DocumentDB (compatible API)
- ECS Fargate → EKS (mêmes images Docker)
- S3 → Blob Storage Azure (API similaire)
- CloudWatch → Grafana (export métriques)

❌ **Difficilement migrables** :
- MongoDB → PostgreSQL (schéma à créer)
- AWS → On-premise (refonte réseau/sécurité)

## Conclusion

Les choix techniques ont été guidés par :
1. **Pragmatisme** : Solutions simples et éprouvées
2. **Coût** : $1-2/jour pour infra de production
3. **Maintenabilité** : Code Python lisible, Docker standard
4. **Évolutivité** : Architecture peut scale 100x sans refonte
5. **Réversibilité** : Pas de lock-in majeur (open-source + standards)

Ces choix permettent à GreenAndCoop de **démarrer rapidement** avec Forecast 2.0, tout en gardant la **flexibilité d'évoluer** selon les besoins futurs.
