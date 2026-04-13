# Portfolio Data Engineer — Aymeric Bailleul

> Formation Data Engineer — OpenClassrooms (2025–2026)
> 13 projets couvrant l'ensemble du cycle de vie de la donnée : ingestion, modélisation, cloud, orchestration, NLP et IA générative.

---

## Compétences démontrées

| Domaine | Compétences | Projets |
|---------|-------------|---------|
| **Analyse de données** | Exploration, visualisation, statistiques descriptives | P2, P6 |
| **Bases de données relationnelles** | SQL, PostgreSQL, modélisation UML, audit, normalisation | P3, P4, P12 |
| **Bases de données NoSQL** | MongoDB (ReplicaSet, Sharding, sécurité, rôles) | P5, P7 |
| **Machine Learning** | Régression, RandomForest, évaluation de modèles, API ML (BentoML) | P6 |
| **ETL & pipelines de données** | Ingestion multi-sources, transformation, chargement, Docker | P8, P10, P12 |
| **Cloud & infrastructure** | Architecture cloud, streaming temps réel (Kafka/Redpanda, PySpark) | P9 |
| **Orchestration** | Kestra, workflows séquentiels et parallèles, AWS S3 | P10 |
| **NLP & IA générative** | RAG (LangChain, FAISS, Qdrant), LLM (Mistral AI), évaluation Ragas | P11, P13 |
| **DevOps & qualité** | Docker, Docker Compose, CI/CD, pytest, Privacy by Design (RGPD) | P5, P8, P12 |
| **DataViz & reporting** | PowerBI, matplotlib, seaborn, dashboards interactifs | P2, P6, P7, P12 |

---

## Projets

### P2 — Analyse des données de systèmes éducatifs
**Objectif :** Exploration et analyse de données éducatives internationales (UNESCO/World Bank) pour identifier des marchés cibles d'une EdTech.

**Stack :** Python · pandas · numpy · matplotlib · seaborn · Jupyter Notebook · Poetry

**Livrables :** Notebook EDA complet avec visualisations statistiques, identification des pays à fort potentiel, présentation des résultats.

---

### P3 — Création d'une base de données immobilière (SQL)
**Objectif :** Concevoir et implémenter une base de données relationnelle normalisée pour gérer des transactions immobilières DVF (Demandes de Valeurs Foncières).

**Stack :** SQL · SQLite · DrawIO (UML) · Excel

**Livrables :** Base de données SQLite finale, diagramme UML (3NF), dictionnaire de données, requêtes d'analyse.

---

### P4 — Audit d'un environnement de données (SuperSmartMarket)
**Objectif :** Auditer la base PostgreSQL d'un supermarché, identifier les anomalies de modélisation et corriger la structure via scripts SQL.

**Stack :** PostgreSQL · SQL (contraintes, triggers, procédures stockées) · DrawIO

**Livrables :** Rapport d'audit complet, diagramme UML avant/après correction, scripts SQL de correction (ALTER TABLE, contraintes, triggers, logs d'audit).

---

### P5 — Maintenance d'un système de stockage MongoDB sécurisé
**Objectif :** Créer, sécuriser et tester une base de données MongoDB healthcare avec gestion fine des rôles et tests automatisés de sécurité.

**Stack :** Python · pymongo · pytest · python-dotenv · Docker · MongoDB

**Livrables :** Scripts de création et import CSV, gestion des rôles (lecture seule / lecture-écriture), suite de tests de sécurité pytest avec couverture complète.

---

### P6 — Prédiction de la consommation énergétique de bâtiments (Seattle)
**Objectif :** Prédire la consommation énergétique de bâtiments à Seattle via Machine Learning, exposer le modèle via une API REST déployée avec BentoML.

**Stack :** Python · scikit-learn (RandomForestRegressor) · BentoML · pydantic · pandas · matplotlib · seaborn · Poetry

**Livrables :** Modèle Random Forest entraîné et sauvegardé, service API BentoML opérationnel, notebooks d'analyse et de sélection de modèle.

---

### P7 — Conception et analyse d'une base de données NoSQL MongoDB
**Objectif :** Concevoir une architecture MongoDB haute disponibilité avec réplication et sharding, intégrer des données CSV, analyser les performances.

**Stack :** Python · pymongo · polars · MongoDB (ReplicaSet + Sharding) · Docker · PowerBI · DrawIO

**Livrables :** Scripts de réplication et sharding avec tests de bascule, dashboard PowerBI d'analyse, diagramme d'architecture distribué.

---

### P8 — Pipeline ETL données météorologiques (Docker + MongoDB)
**Objectif :** Construire un pipeline ETL dockerisé pour extraire des données météo depuis AWS S3 (format Airbyte/JSONL), les transformer et les charger dans MongoDB.

**Stack :** Python · Docker · Docker Compose · MongoDB 7.0 · AWS S3 · pandas

**Livrables :** Pipeline ETL multi-sources (JSON API + Excel), conversion automatique d'unités (°F→°C, mph→km/h), import toutes les 5 min, orchestration Docker Compose.

---

### P9 — Modélisation d'infrastructure cloud + POC streaming temps réel
**Objectif :** (1) Proposer une architecture cloud documentée pour un projet data ; (2) implémenter un POC de traitement de tickets clients en temps réel.

**Stack :** DrawIO · Redpanda (Kafka-compatible) · PySpark · MySQL · Docker Compose · Python

**Livrables :** Document d'architecture cloud avec schéma, POC pipeline Redpanda → PySpark → MySQL avec agrégations fenêtrées en temps réel.

---

### P10 — Pipeline d'orchestration des flux — BottleNeck
**Objectif :** Automatiser le pipeline de données de BottleNeck (e-commerce vin) : réconciliation de 3 sources hétérogènes, calcul du CA et identification des vins premium, orchestration mensuelle sur Kestra.

**Stack :** Python · pandas · numpy · pyarrow · openpyxl · Kestra · Docker · AWS S3 · Poetry

**Résultats :** CA total **70 568,60 €** calculé, **30 vins premium** identifiés (z-score > 2), 12 tâches Kestra orchestrées avec groupes parallèles, exports sur S3.

---

### P11 — RAG Chatbot Puls-Events (POC)
**Objectif :** Développer un POC de chatbot RAG (Retrieval-Augmented Generation) pour recommander des événements culturels Open Agenda en région Occitanie.

**Stack :** Python · LangChain · Mistral AI (mistral-embed 1024D + mistral-small-latest) · FAISS · Streamlit · Ragas · pandas

**Résultats :** 913 818 événements → 7 960 filtrés Occitanie → 10 480 chunks vectorisés. Scores Ragas : faithfulness=0.764, answer_relevancy=0.910, context_precision=0.700, context_recall=0.583.

---

### P12 — Pipeline ETL Avantages Sportifs (RGPD + PowerBI)
**Objectif :** Concevoir et déployer un pipeline ETL multi-schémas pour calculer l'éligibilité aux primes sportives et journées bien-être, avec conformité RGPD et tableau de bord PowerBI.

**Stack :** Python · PostgreSQL 16 · Docker Compose · pytest · Slack (notifications) · PowerBI · uv

**Livrables :** Pipeline ETL 4 schémas (raw/staging/gold/rh_prive), Privacy by Design RGPD (chiffrement colonnes nominatives), tests pytest, notifications Slack nominatives, dashboard PowerBI.

---

### P13 — MVP Chatbot RAG Puls-Events (gestion de projet)
**Objectif :** Concevoir le passage du POC (P11) au MVP production : architecture cloud GCP scalable, backlog priorisé, estimation des coûts, stratégie de déploiement.

**Stack :** GCP (Cloud Run · Qdrant · Redis · BigQuery · Langfuse · Cloud Build) · LangChain · Mistral AI · FastAPI · smolagents

**Livrables :** Rapport de gestion de projet complet (architecture, backlog 19 fonctionnalités, coûts 3 scénarios), support de présentation.

---

## Tableau des projets

|Numéro | Nom | Date de début | Date de fin |
| :-----------------------------: | :-------------------------------------- | :----------------: | :----------------: |
|P1  | Découvrez votre formation de Data Engineer 											|   05/08/2025    |    10/08/2025   |
|P2  | Analysez les données de systèmes éducatifs 											|   10/08/2025    |    24/08/2025   |
|P3  | Entraînez-vous avec SQL et créez votre BDD 											|   24/08/2025    |    06/09/2025   |
|P4  | Auditez un environnement de données													|   06/09/2025    |    24/09/2025   |
|P5  | Maintenez et documentez un système de stockage des données sécurisé et performant 	|   24/09/2025    |    13/10/2025   |
|P6  | Anticipez les besoins en consommation de bâtiments 									|   13/10/2025    |    04/11/2025   |
|P7  | Concevez et analysez une base de données NoSQL 										|   04/11/2025    |    27/11/2025   |
|P8  | Construisez et testez une infrastructure de données 								    |   27/11/2025    |    19/12/2025   |
|P9  | Modélisez une infrastructure dans le cloud 											|   19/12/2025    |    15/01/2026   |
|P10 | Mettez en place le pipeline d'orchestration des flux 								|   15/01/2026    |    16/02/2026   |
|P11 | Catégorisez automatiquement des questions 											|   16/02/2026    |    10/03/2026   |
|P12 | Gérez un projet d'infrastructure 													|   10/03/2026    |    11/04/2026   |
|P13 | Réalisez votre portfolio de Data Engineer 											|   11/04/2026    |    04/05/2026   |
---

## Titre des dossiers par projet *(en gras celui en cours)*
- P1_Découverte_de_la_formation_bailleul_aymeric
- P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric
- P3_Entrainez_vous_avec_SQL_et_creez_votre_BDD_bailleul_aymeric
- P4_Auditez_un_environnement_de_donnees_bailleul_aymeric
- P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric
- P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric
- P7_Concevez_et_analysez_une_base_de_donnees_nosql_aymeric_bailleul
- P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul
- P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul
- P10_Mettez_en_place_le_pipeline_d_orchestration_des_flux_aymeric_bailleul
- P11_Categorisez_automatiquement_des_questions_aymeric_bailleul
- P12_Gerez_un_projet_d_infrastructure_aymeric_bailleul
- **P13_Realisez_votre_portfolio_de_data_engineer_aymeric_bailleul**

---

## Configuration des environnements Python par projet

Chaque projet dispose de son propre environnement virtuel Python. Voici comment sélectionner le bon interpréteur dans VS Code :

### Procédure de sélection de l'environnement

1. **Ouvrir la palette de commandes** : `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (Mac)
2. Tapez : **`Python: Select Interpreter`**
3. Choisissez l'environnement du projet actuel dans la liste
4. **OU** cliquez sur **"Enter interpreter path..."** et collez le chemin exact ci-dessous

### Chemins des interpréteurs Python par projet

| Projet | Version Python | Chemin de l'interpréteur |
|--------|----------------|--------------------------|
| **P2** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P5** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P6** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P7** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P7_Concevez_et_analysez_une_base_de_donnees_nosql_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P8** | Python 3.10 | `G:\Mon Drive\_formation_over_git\P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P9** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P10** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P10_Mettez_en_place_le_pipeline_d_orchestration_des_flux_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P11** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P11_Categorisez_automatiquement_des_questions_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P12** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P12_Gerez_un_projet_d_infrastructure_aymeric_bailleul\.venv\Scripts\python.exe` |

### Vérification

Après sélection, vous devriez voir en bas à droite de VS Code :
- **Python 3.14.0 ('.venv': venv)** pour P2, P5, P6, P7, P9, P10, P11, P12
- **Python 3.10.11 ('.venv': venv)** pour P8

---