# README - Livrables pour Soutenance

## Contenu du dossier

Ce dossier contient tous les livrables nécessaires pour la soutenance du projet **Forecast 2.0 - Pipeline de données météorologiques**.

### 📄 Documents disponibles

| # | Document | Description | Audience |
|---|----------|-------------|----------|
| 1 | [01_schema_mongodb.md](01_schema_mongodb.md) | Schéma de la base de données MongoDB avec index et validation | Data Scientists + Technique |
| 2 | [02_logigramme_processus.md](02_logigramme_processus.md) | Logigramme détaillé du processus ETL (collecte → transformation → stockage → tests) | Équipe projet + Technique |
| 3 | [03_architecture_infrastructure.md](03_architecture_infrastructure.md) | Architecture complète de l'infrastructure AWS (ECS, S3, MongoDB, réseau) | DSI + Technique |
| 4 | [04_rapport_qualite_donnees.md](04_rapport_qualite_donnees.md) | Rapport de qualité : taux d'erreur, complétude, conversions, anomalies | Data Scientists + Management |
| 5 | [05_rapport_temps_accessibilite.md](05_rapport_temps_accessibilite.md) | Benchmark de performance : temps de lecture, écriture, agrégation | Data Scientists + Management |
| 6 | [06_justification_choix_techniques.md](06_justification_choix_techniques.md) | Justification détaillée de tous les choix techniques (MongoDB, ECS, Python, etc.) | Évaluateurs + DSI |
| 7 | [07_guide_demonstration.md](07_guide_demonstration.md) | Guide pas-à-pas pour la démonstration de 3 minutes en soutenance | Présentateur |
| 8 | [README.md](README.md) | Ce fichier - Index des livrables | Tous |

---

## 🎯 Objectifs de la mission

**Entreprise** : GreenAndCoop (fournisseur électricité renouvelable Hauts-de-France)

**Projet** : Forecast 2.0 - Amélioration des prévisions de demande électrique

**Mission** : Intégrer de nouvelles sources de données météorologiques (stations InfoClimat + Weather Underground) dans une base de données MongoDB hébergée sur AWS pour enrichir les modèles de prévision.

---

## 📊 Résultats du projet

### Données intégrées

| Source | Stations | Nombre de mesures | Période |
|--------|----------|------------------|---------|
| **InfoClimat API** | Bergues, Hazebrouck, Armentières, Lille-Lesquin | 1,143 | Oct 2024 |
| **Weather Underground Excel** | Ichtegem (BE), La Madeleine (FR) | 3,807 | Oct-Déc 2024 |
| **TOTAL** | **6 stations** | **4,950** | **Oct-Déc 2024** |

### Qualité des données

- ✅ **Taux d'erreur** : 0%
- ✅ **Doublons** : 0 (grâce à unique_key avec séquence)
- ✅ **Complétude** : 100% pour champs obligatoires
- ✅ **Conversions** : 100% conformes (°F→°C, mph→km/h, inHg→hPa, in→mm)

### Performance

| Opération | Résultat | Évaluation |
|-----------|----------|------------|
| **Lecture indexée** | 0.54 ms/recherche | ⭐⭐⭐⭐⭐ Excellent |
| **Écriture batch (1000)** | 26,515 docs/s | ⭐⭐⭐⭐ Très bon |
| **Agrégation** | 12.5 ms (6 groupes) | ⭐⭐⭐⭐⭐ Excellent |
| **Lecture séquentielle (1000)** | 16.9 ms | ⭐⭐⭐⭐ Très bon |

### Infrastructure

- **Cloud** : AWS (eu-west-1)
- **Orchestration** : ECS Fargate (5 services)
- **Base de données** : MongoDB 7.0 sur ECS + EFS
- **Stockage** : S3 (3 dossiers : raw, cleaned, archived)
- **Monitoring** : CloudWatch Dashboard + Mongo Express
- **Coût** : ~30-35$/mois (services manuels arrêtables)

---

## 🏗️ Architecture du pipeline

```
[InfoClimat API] ──┐
                   ├──> [Airbyte] ──> [S3:01_raw/] ──> [ETL Python]
[WU Excel Files] ──┘
                                                            │
                                                            ▼
                                                       [S3:02_cleaned/]
                                                            │
                                                            ▼
                                                    [Import MongoDB]
                                                            │
                                                            ▼
                                                    [MongoDB ECS/EFS]
                                                            │
                                                            ▼
                                                [Data Scientists/SageMaker]
```

### Services ECS Fargate

1. **mongodb** (actif) : Base de données MongoDB 7.0
2. **mongo-express** (actif) : Interface web MongoDB
3. **weather-etl** (manuel) : Transformation des données (S3 → S3)
4. **mongodb-importer** (manuel) : Import automatique (S3 → MongoDB)
5. **s3-cleanup** (manuel) : Nettoyage et archivage S3

---

## 📚 Utilisation des livrables

### Pour la préparation de la présentation

1. **Lire en priorité** :
   - [07_guide_demonstration.md](07_guide_demonstration.md) : Plan de la démo de 3 minutes
   - [03_architecture_infrastructure.md](03_architecture_infrastructure.md) : Schémas visuels pour slides
   - [02_logigramme_processus.md](02_logigramme_processus.md) : Logigramme pour présenter le flux

2. **Préparer les réponses aux questions** :
   - [06_justification_choix_techniques.md](06_justification_choix_techniques.md) : Argumentaire pour défendre les choix
   - [04_rapport_qualite_donnees.md](04_rapport_qualite_donnees.md) : Chiffres de qualité
   - [05_rapport_temps_accessibilite.md](05_rapport_temps_accessibilite.md) : Chiffres de performance

3. **Créer les slides** :
   - Extraire schémas ASCII des documents .md
   - Ajouter captures d'écran (Mongo Express, CloudWatch Dashboard, AWS ECS Console)
   - Intégrer tableaux de statistiques

### Pour les Data Scientists (Ouly et équipe)

1. **Schéma de requêtage** : [01_schema_mongodb.md](01_schema_mongodb.md)
   - Exemples de requêtes MongoDB
   - Structure des documents
   - Index disponibles

2. **Qualité des données** : [04_rapport_qualite_donnees.md](04_rapport_qualite_donnees.md)
   - Taux de complétude par champ
   - Stations disponibles
   - Période couverte

3. **Performance d'accès** : [05_rapport_temps_accessibilite.md](05_rapport_temps_accessibilite.md)
   - Temps de réponse pour requêtes typiques
   - Recommandations de requêtage optimisé
   - Code Python d'exemple

### Pour la DSI

1. **Architecture technique** : [03_architecture_infrastructure.md](03_architecture_infrastructure.md)
   - Schéma réseau VPC
   - Services AWS utilisés
   - Dimensionnement et coût

2. **Justification des choix** : [06_justification_choix_techniques.md](06_justification_choix_techniques.md)
   - Comparaison des alternatives
   - Trade-offs assumés
   - Évolutivité et réversibilité

3. **Processus ETL** : [02_logigramme_processus.md](02_logigramme_processus.md)
   - Flux de données
   - Points de contrôle qualité
   - Gestion des erreurs

---

## 🎤 Checklist pour la soutenance

### Avant la présentation (J-1)

- [ ] Lire tous les livrables (2-3 heures)
- [ ] Créer le support de présentation (PowerPoint/Keynote)
- [ ] Préparer captures d'écran (Airbyte, Mongo Express, CloudWatch, AWS ECS)
- [ ] Répéter la démonstration de 3 minutes
- [ ] Tester les services AWS (mongodb + mongo-express actifs)
- [ ] Préparer les commandes PowerShell dans le terminal

### Le jour J (1 heure avant)

- [ ] Vérifier services AWS actifs (desiredCount = 1 pour mongodb + mongo-express)
- [ ] Tester URL Mongo Express : http://34.244.220.245:8081
- [ ] Ouvrir CloudWatch Dashboard dans un onglet
- [ ] Ouvrir AWS ECS Console dans un onglet
- [ ] Préparer terminal PowerShell avec commandes prêtes
- [ ] Charger le support de présentation
- [ ] Chronométrer une dernière fois (< 3 min)

### Pendant la soutenance

- [ ] **Présentation** (10-15 min) : Contexte, démarche, architecture, résultats
- [ ] **Démonstration** (3 min) : Pipeline fonctionnel de bout en bout
- [ ] **Questions/Réponses** (10-15 min) : S'appuyer sur les livrables

### Après la soutenance

- [ ] Arrêter les services AWS si nécessaire (économie de coût)
- [ ] Archiver captures d'écran et logs pour portfolio
- [ ] Mettre à jour README.md du projet principal

---

## 📂 Structure du projet complet

```
_projet/
├── livrables/                                  # 👈 VOUS ÊTES ICI
│   ├── 01_schema_mongodb.md
│   ├── 02_logigramme_processus.md
│   ├── 03_architecture_infrastructure.md
│   ├── 04_rapport_qualite_donnees.md
│   ├── 05_rapport_temps_accessibilite.md
│   ├── 06_justification_choix_techniques.md
│   ├── 07_guide_demonstration.md
│   └── README.md (ce fichier)
│
├── ABAI_P8_script_01_clean_data.py           # Script ETL principal
├── ABAI_P8_script_02_import_to_mongodb.py    # Service d'import automatique
├── ABAI_P8_script_03_test_mongodb.py         # Tests qualité MongoDB
├── ABAI_P8_script_04_cleanup_s3.py           # Nettoyage et archivage S3
├── ABAI_P8_script_05_benchmark_mongodb.py    # Benchmark performance
│
├── conf_ecs/                                  # Configuration AWS ECS
│   ├── cloudwatch-dashboard.json              # Dashboard de monitoring
│   └── task-definition-*.json                 # Définitions des tâches ECS
│
├── docker-compose.yml                         # Orchestration locale
├── Dockerfile                                 # Image Docker pour ETL
├── pyproject.toml                             # Dépendances Python (Poetry)
├── README.md                                  # Documentation principale
└── .env                                       # Configuration (non versionné)
```

---

## 🔗 Liens utiles

### AWS

- **Mongo Express** : http://34.244.220.245:8081 (admin/pass)
- **CloudWatch Dashboard** : [Console AWS](https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1#dashboards/dashboard/weather-pipeline-monitoring)
- **ECS Console** : [Services](https://eu-west-1.console.aws.amazon.com/ecs/v2/clusters/weather-pipeline-cluster/services)
- **S3 Bucket** : s3://p8-weather-data

### Documentation projet

- **README principal** : [../README.md](../README.md)
- **Repository GitHub** : formation (merais/main)

---

## 💡 Conseils pour la soutenance

### Communication

1. **Commencer par le contexte** : Rappeler le besoin métier (prévision demande électrique)
2. **Montrer les résultats** : 4,950 mesures, 0% erreur, < 1 ms de latence
3. **Démontrer la valeur** : "Les Data Scientists peuvent requêter en temps réel"
4. **Anticiper les questions** : Lire [06_justification_choix_techniques.md](06_justification_choix_techniques.md)

### Démonstration

1. **Répéter 3-4 fois** : Fluidité = professionnalisme
2. **Chronométrer** : Ne jamais dépasser 3 minutes
3. **Commenter en continu** : Dire ce qu'on fait, pourquoi, résultat attendu
4. **Plan B prêt** : Si problème réseau, montrer l'environnement local

### Gestion des questions

1. **Écouter attentivement** : Reformuler la question si besoin
2. **Répondre factuellement** : S'appuyer sur les chiffres des livrables
3. **Admettre les limites** : "Single-node MongoDB, pas de réplication pour optimiser coût"
4. **Ouvrir sur l'évolution** : "Si volumétrie x10, on passerait à Replica Set"

---

## 📞 Contact

**Auteur** : Aymeric Bailleul  
**Projet** : P8 - Construisez et testez une infrastructure de données  
**Formation** : Data Engineer - OpenClassrooms  
**Date** : Décembre 2025

---

## ✅ Critères d'évaluation couverts

| Critère | Livrable | Statut |
|---------|----------|--------|
| **Schéma de la base de données** | 01_schema_mongodb.md | ✅ |
| **Logigramme du processus** | 02_logigramme_processus.md | ✅ |
| **Architecture de la base de données** | 03_architecture_infrastructure.md | ✅ |
| **Stack technique** | 03_architecture_infrastructure.md | ✅ |
| **Installation Airbyte** | Capture d'écran à ajouter au support | ⚠️ |
| **Qualité des données (taux d'erreur)** | 04_rapport_qualite_donnees.md | ✅ |
| **Temps d'accessibilité aux données** | 05_rapport_temps_accessibilite.md | ✅ |
| **Installation AWS** | Capture d'écran à ajouter au support | ⚠️ |
| **Justification des choix** | 06_justification_choix_techniques.md | ✅ |
| **Démonstration fonctionnelle** | 07_guide_demonstration.md | ✅ |

**Note** : Les captures d'écran Airbyte et AWS ECS sont à faire et intégrer au support de présentation.

---

## 🚀 Prochaines étapes recommandées

1. **Créer support de présentation** (PowerPoint/Google Slides)
   - Slide 1 : Contexte et objectifs
   - Slide 2 : Architecture globale (schéma du 03_architecture)
   - Slide 3 : Logigramme du processus (schéma du 02_logigramme)
   - Slide 4 : Schéma MongoDB (extrait du 01_schema)
   - Slide 5 : Qualité et performance (chiffres clés des 04 et 05)
   - Slide 6 : Stack technique (tableau du 03_architecture)
   - Slide 7 : Captures d'écran (Airbyte, Mongo Express, CloudWatch, AWS ECS)
   - Slide 8 : Conclusion et évolutions

2. **Prendre captures d'écran**
   - Airbyte : Dashboard avec sources/destinations configurées
   - Mongo Express : Collection measurements avec documents
   - CloudWatch Dashboard : Métriques temps réel
   - AWS ECS Console : Services actifs

3. **Répéter la démonstration**
   - Timing strict : 3 minutes
   - Fluidité des transitions
   - Commentaires clairs
   - Plan B si problème technique

4. **Préparer les réponses aux questions types**
   - "Pourquoi MongoDB et pas PostgreSQL ?"
   - "Comment gérez-vous les pannes ?"
   - "Quel est le coût mensuel ?"
   - "Quelle est la capacité maximale ?"
   - → Toutes les réponses dans [06_justification_choix_techniques.md](06_justification_choix_techniques.md)

---

**Bonne chance pour la soutenance ! 🎓**
