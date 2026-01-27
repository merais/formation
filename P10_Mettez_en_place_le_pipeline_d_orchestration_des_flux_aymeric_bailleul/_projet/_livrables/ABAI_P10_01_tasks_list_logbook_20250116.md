# Logbook - P10 Mettez en place le pipeline d'orchestration des flux

**Auteur** : Aymeric Bailleul  
**Date de début** : 15/01/2026  
**Date de fin prévue** : 16/02/2026
**Date de soutenance souhaitable** : Entre le 09/02/2026 et le 13/02/2026 (ou avant si possible)

---

## Liste complète des tâches à effectuer

### PHASE 1 : PREPARATION ET ANALYSE

#### 1.1 Analyse des données sources
- [X] Explorer les fichiers erp.xlsx, web.xlsx, liaison.xlsx dans _projet/sources/
- [X] Analyser la structure de chaque fichier *(colonnes, types de données)*
- [X] Identifier les clés primaires et les relations entre les tables
- [X] Repérer les valeurs manquantes et doublons potentiels
- [X] Documenter les caractéristiques de chaque source : **ABAI_P10_02_analyse_donnees_sources.md**

#### 1.2 Compréhension du processus métier
- [X] Comprendre le processus de réconciliation via le fichier liaison
- [X] Identifier les règles métier pour le calcul du chiffre d'affaires
- [X] Comprendre la méthode de classification des vins *(z-score > 2)*
- [X] Définir et documenter les critères de qualité des données : **ABAI_P10_03_processus_metier.md**

#### 1.3 Configuration de l'environnement de développement
- [X] Installer Docker Desktop
    --> Déjà installé
- [X] Installer Kestra via Docker
    --> `cd _projet/_kestra && docker-compose up -d`
    --> Conteneurs: kestra-kestra-1 + kestra-postgres-1
- [X] Vérifier le bon fonctionnement de Kestra (accès interface web)
    --> Accessible sur `http://localhost:8080`
- [X] Prendre des captures d'écran de l'installation de Kestra
- [X] Configurer l'environnement Python Poetry avec les dépendances nécessaires
    --> Poetry 2.2.1 - Python 3.14.0 - pandas, openpyxl, boto3, duckdb, python-dotenv installés

---

### PHASE 2 : CONCEPTION DE L'ARCHITECTURE

#### 2.1 Conception du diagramme de flux (Data lineage)
- [X] Identifier toutes les tâches de transformation nécessaires
    --> 21 tâches détaillées dans **ABAI_P10_03_conception_data_lineage.md**
    --> **12 tâches Kestra final** a implémenter dans bottleneck_pipeline_s3.yaml
- [X] Lister les tâches de nettoyage (suppression valeurs manquantes, dédoublonnage)
    --> **3 tâches parallèles** : clean_erp, clean_liaison, clean_web (tasks 2-4)
- [X] Lister les tâches de fusion (jointures via fichier liaison)
    --> **2 jointures** dans task_05 : ERP-LIAISON puis avec WEB
- [X] Lister les tâches d'agrégation (calcul CA par produit et total)
    --> **1 tâche** : task_06_calculate_ca
- [X] Lister les tâches d'extraction (rapports Excel, CSV premium/ordinaires)
    --> **3 tâches parallèles** : rapport_ca, premium, ordinaires (tasks 9-11)
- [X] Identifier les points de test après chaque étape de transformation
    --> **9 validations automatisées** : 4 intermédiaires (825, 825, 1428, 714) + 5 globales

#### 2.2 Création du logigramme sur Draw.io
- [X] Créer le diagramme avec les 3 fichiers sources en entrée
- [X] Représenter les tâches de nettoyage pour chaque source
- [X] Représenter les jointures entre les fichiers
- [X] Représenter les calculs d'agrégation
- [X] Représenter la classification des vins (z-score)
- [X] Représenter les extractions finales (3 fichiers)
- [X] Ajouter les tâches de tests après chaque transformation
- [X] Ajouter les liaisons et flux de données entre les tâches
- [X] Exporter le diagramme au format PNG et .drawio dans `/_livrables`

---

### PHASE 3 : DEVELOPPEMENT DES SCRIPTS LOCAL

#### 3.1 Script de nettoyage et fusion des donnees
- [X] **01_clean_and_merge.py** : Nettoyage complet et fusion des 3 sources (100% local)
    - Commande : `cd _projet && poetry run python _scripts/01_clean_and_merge.py`
    - **Etape 1 - Verification** : Verification presence des 3 fichiers dans sources/
        - fichier_erp.xlsx
        - fichier_liaison.xlsx
        - fichier_web.xlsx
    - **Etape 2 - Nettoyage ERP** : 
        - Chargement fichier_erp.xlsx
        - Suppression valeurs manquantes + dedoublonnage
        - Resultat : 825 lignes
        - Stockage : Table DuckDB erp_clean_final
    - **Etape 3 - Nettoyage LIAISON** :
        - Chargement fichier_liaison.xlsx
        - /!\ NULL conserves sur id_web (91 lignes) - Filtres apres jointure
        - Dedoublonnage uniquement
        - Resultat : 825 lignes
        - Stockage : Table DuckDB liaison_clean_final
    - **Etape 4 - Nettoyage WEB** :
        - Chargement fichier_web.xlsx (1513 lignes)
        - Suppression NULL sur sku (85 NULL)
        - Resultat intermediaire : 1428 lignes (products + attachments)
        - Tri descendant sur post_type pour prioriser 'product'
        - Dedoublonnage sur sku (garde first = product en priorite)
        - Resultat final : 714 lignes (que des products)
        - Stockage : Table DuckDB web_clean_final
    - **Etape 5 - Jointure ERP + LIAISON** :
        - Jointure sur product_id (825 lignes)
        - Suppression NULL sur id_web (734 lignes)
    - **Etape 6 - Jointure finale avec WEB** :
        - Jointure INNER sur id_web = sku
        - Resultat : 714 lignes avec erp_price et total_sales
        - Stockage : Table DuckDB merged_data_final
    - **Resultat global** : Table merged_data_final (714 lignes) dans DuckDB, pret pour traitement
    - **Architecture** : 3 etapes (Verification -> Nettoyage -> Fusion)

#### 3.2 Script de traitement, classification et export
- [X] **02_process_and_export.py** : Calcul CA, classification et exports (100% local)
    - Commande : `cd _projet && poetry run python _scripts/02_process_and_export.py`
    - **Etape 1 - Calcul CA** :
        - Lecture depuis Table DuckDB merged_data_final
        - Calcul CA par produit : erp_price x total_sales
        - Calcul CA total : SUM(CA par produit)
        - Valeur obtenue : 70 568,60 € (OK)
        - Stockage : Table DuckDB data_with_ca
    - **Etape 2 - Classification des vins** :
        - Calcul moyenne (mu = 32.49€) et ecart-type (sigma = 27.81€)
        - Calcul z-score : (price - mu) / sigma
        - Classification : premium si z-score > 2, sinon ordinaire
        - Resultat : 30 vins premium, 684 vins ordinaires
        - Stockage : Table DuckDB data_classified
    - **Etape 3 - Export local** :
        - Creation rapport_ca.xlsx (2 feuilles)
        - Creation vins_premium.csv (30 vins, CA 6 884,40€)
        - Creation vins_ordinaires.csv (684 vins, CA 63 684,20€)
        - **Note** : CA total = 70 568,60€ (6 884,40 + 63 684,20)
        - Destination : _exports/ (local)
    - **Resultat global** : 3 fichiers exportes localement dans _exports/
    - **Architecture** : 3 etapes (CA -> Classification -> Export)

#### 3.3 Script de validation globale
- [X] **03_validate_all.py** : Validation complete de toute la chaine
    - Commande : `cd _projet && poetry run python _scripts/03_validate_all.py`
    - **BLOC 1 - Nettoyage (4 tests)** :
        - Test 1 : ERP nettoye (825 lignes, 0 doublons)
        - Test 2 : LIAISON nettoye (825 lignes, 0 doublons)
        - Test 3 : WEB nettoye (714 lignes, 0 NULL, 0 non-products)
        - Test 4 : WEB dedoublonne (714 SKU uniques)
    - **BLOC 2 - Jointures (2 tests)** :
        - Test 5 : Coherence ERP-LIAISON (0 orphelins)
        - Test 6 : Coherence finale (714 lignes)
    - **BLOC 3 - CA (2 tests)** :
        - Test 7 : CA positifs (0 CA negatifs, 0 NULL)
        - Test 8 : CA total (70 568,60 € +- 0,01 €)
    - **BLOC 4 - Classification (2 tests)** :
        - Test 9 : Z-scores valides (0 NULL/NaN/Inf)
        - Test 10 : Vins premium (30 vins attendus)
    - **Resultat** : 10/10 tests OK (100%)
    - Exit code 0 si OK, 1 si erreur (utilisable dans Kestra)

#### 3.4 Scripts utilitaires AWS S3
- [X] **04_upload_sources_to_s3.py** : Upload des fichiers sources vers S3/RAW/
    - Commande : `cd _projet && poetry run python _scripts/04_upload_sources_to_s3.py`
    - Upload les 3 fichiers sources (erp, liaison, web) vers S3/RAW/
    - Gestion des credentials AWS (variables d'environnement ou ~/.aws/)
    - Verification de connexion au bucket avant upload
    - Exit code 0 si OK, 1 si erreur
    
- [X] **05_download_exports_from_s3.py** : Download des exports depuis S3/EXPORTS/
    - Commande : `cd _projet && poetry run python _scripts/05_download_exports_from_s3.py`
    - Detecte automatiquement le dossier d'export le plus recent
    - Telecharge les 3 fichiers (rapport_ca.xlsx, vins_premium.csv, vins_ordinaires.csv)
    - Mise a jour automatique si execute plusieurs fois (remplace les anciens fichiers)
    - Destination : _exports/ (local)
    - Exit code 0 si OK, 1 si erreur

---

### PHASE 4 : INTEGRATION KESTRA

#### 4.1 Structure de base du workflow
- [X] Creer le fichier bottleneck_pipeline_s3.yaml dans _projet/_kestra/
- [X] Configurer les metadonnees (id: bottleneck_pipeline_s3, namespace: company.bottleneck)
- [X] Definir les variables globales (bucket S3, region, prefixes)
- [X] Creer fichier .env avec secrets AWS (BASE64) et PostgreSQL
- [X] Configurer docker-compose.yml pour utiliser variables d'environnement ${VARIABLE}
- [X] Deployer Kestra avec PostgreSQL backend

#### 4.2 Integration AWS S3
- [X] Creer le bucket S3 bottleneck-pipeline-p10 dans eu-west-3
- [X] Creer la structure RAW/ et EXPORTS/
- [X] Configurer un utilisateur IAM avec droits limites
- [X] Encoder les credentials AWS en BASE64 et stocker dans .env
- [X] Configurer docker-compose.yml pour lire .env via ${SECRET_AWS_ACCESS_KEY_ID}
- [X] Tester la connexion S3 depuis Kestra
- [X] Uploader les fichiers sources dans S3/RAW/ *(gràce au script 04 dans notre cas)*

#### 4.3 Implementation des taches Kestra
- [X] **Tache 1 : Download S3** (io.kestra.plugin.aws.s3.Downloads)
    - Action: NONE (download sans suppression)
    - Output: 3 fichiers Excel
    
- [X] **Groupe parallele 1 : Nettoyage** (io.kestra.plugin.core.flow.Parallel)
    - [X] task_02_clean_erp: 825 lignes (validation OK) → erp_clean.parquet
    - [X] task_03_clean_liaison: 825 lignes (validation OK) → liaison_clean.parquet
    - [X] task_04_clean_web: 1428 → 714 lignes (validations OK) → web_clean.parquet
        - **Validations intermediaires** : 825, 825, 1428, 714 avec sys.exit(1) si echec
    - Execution simultanee des 3 taches
    
- [X] **Tache 5 : Fusion** (io.kestra.plugin.scripts.python.Commands)
    - Jointure ERP + LIAISON sur product_id
    - Jointure avec WEB sur id_web = sku
    - Output: merged_data.parquet (714 lignes)
    
- [X] **Tache 6 : Calcul CA** (io.kestra.plugin.scripts.python.Commands)
    - Calcul CA par produit: price x total_sales
    - CA total: 70 568,60 €
    - Output: data_with_ca.parquet
    
- [X] **Tache 7 : Classification** (io.kestra.plugin.scripts.python.Commands)
    - Calcul z-score: (price - mu) / sigma
    - Classification: premium si z-score > 2
    - Output: data_classified.parquet (30 premium, 684 ordinaires)
    
- [X] **Tache 8 : Validation** (io.kestra.plugin.scripts.python.Commands)
    - 5 tests automatises globaux (allowFailure: false)
    - Test 1 : 714 lignes fusionnees
    - Test 2 : CA total 70568.60€
    - Test 3 : 30 vins premium
    - Test 4 : 684 vins ordinaires
    - Test 5 : 0 valeurs NULL dans CA
    - Bloque les exports et upload si echec (sys.exit(1))
    - **IMPORTANT** : Validations intermediaires (825, 825, 1428, 714) dans tasks 2-4
    
- [X] **Groupe parallele 2 : Exports** (io.kestra.plugin.core.flow.Parallel)
    - [X] task_09_export_rapport_ca: Excel 2 feuilles
    - [X] task_10_export_vins_premium: CSV 30 vins
    - [X] task_11_export_vins_ordinaires: CSV 684 vins
    - Execution simultanee des 3 taches
    
- [X] **Tache 12 : Upload S3** (io.kestra.plugin.scripts.python.Commands + boto3)
    - Upload vers S3/EXPORTS/YYYYMMDD_HHMMSS/
    - 3 fichiers: rapport_ca.xlsx, vins_premium.csv, vins_ordinaires.csv
    - Ne s'execute que si validation OK (task_08)

#### 4.5 Configuration de la planification et triggers
- [X] Creer le trigger schedule avec cron: "0 9 15 * *" (15 du mois a 9h)
- [X] Configurer timezone: "Europe/Paris"
- [X] Tester la syntaxe cron
- [X] Documenter les conditions d'execution

#### 4.6 Gestion des erreurs et resilience
- [X] Configurer retry sur chaque tache (maxAttempt: 3, backoff exponentiel)
- [X] Configurer timeout 10 minutes par tache
- [X] Configurer allowFailure: false sur task_08 (validation bloquante)
- [ ] Ajouter une tache d'alerte email (SMTP non configure)
- [X] Tester les scenarios d'erreur (corrections multiples)

#### 4.8 Validation finale
- [X] Execution complete reussie
- [X] Verification parallelisme (Gantt Chart)
- [X] Verification temps execution (~2 minutes)
- [X] Verification uploads S3 (EXPORTS/YYYYMMDD_HHMMSS/)
- [X] Validation 5 tests automatises (100%)
- [X] Verification logs detailles de chaque tache

---

### PHASE 5 : TESTS ET VALIDATION

#### 5.1 Tests unitaires Kestra
- [X] Tester individuellement task_01 (download S3)
- [X] Tester individuellement task_02 (nettoyage ERP)
- [X] Tester individuellement task_03 (nettoyage LIAISON)
- [X] Tester individuellement task_04 (nettoyage WEB)
- [X] Tester individuellement task_05 (fusion)
- [X] Tester individuellement task_06 (calcul CA)
- [X] Tester individuellement task_07 (classification)
- [X] Tester individuellement task_08 (validation globale)
- [X] Tester individuellement task_09 (export rapport CA)
- [X] Tester individuellement task_10 (export premium)
- [X] Tester individuellement task_11 (export ordinaires)
- [X] Tester individuellement task_12 (upload S3)

#### 5.2 Tests d'integration
- [X] Exécuter le workflow complet de bout en bout
- [X] Vérifier que tous les fichiers de sortie sont générés
- [X] Valider le contenu du rapport CA Excel (2 feuilles, 714 produits)
- [X] Valider le contenu du fichier vins premium CSV (30 vins)
- [X] Valider le contenu du fichier vins ordinaires CSV (684 vins)
- [X] Verifier les valeurs de reference (825, 825, 1428, 714, 70568.60€, 30, 684)
- [X] Verifier la structure S3/EXPORTS/YYYYMMDD_HHMMSS/

#### 5.3 Tests de robustesse
- [X] Tester le workflow avec corrections iteratives (12 phases)
- [X] Tester le comportement en cas d'erreur de validation
- [X] Tester le mecanisme de retry (backoff exponentiel)
- [X] Valider le blocage upload si validation echoue (allowFailure: false)
- [X] Verifier les logs detailles de chaque tache

#### 5.4 Tests de planification
- [X] Verifier que le trigger cron est correctement configure (0 9 15 * *)
- [X] Verifier timezone Europe/Paris
- [X] Documenter le calendrier d'execution 2026

---

### PHASE 6 : DOCUMENTATION ET PRESENTATION

#### 6.1 Documentation technique
- [X] Documenter l'architecture du workflow
- [X] Documenter chaque tâche du workflow Kestra
- [X] Documenter les scripts Python
- [X] Documenter les tests implémentés (9 validations)
- [X] Documenter la procédure de déploiement (Docker + S3)
- [X] Rédiger le README avec les instructions d'installation et d'utilisation

#### 6.2 Création du support de présentation
- [X] Slide 2 : Contexte et enjeux métier
- [X] Slide 3 : Objectif et KPI 
- [X] Slide 4 : Présentation de Kestra (vulgarisation)
- [X] Slide 5 : Arichitecture du pipeline
- [X] Slide 6 : Détail des tâches de nettoyage et tests
- [X] Slide 7 : Détail des tâches de fusion et agrégation
- [X] Slide 8 : Résumé des jointures
- [X] Slide 9 : Classification des vins (z-score)
- [X] Slide 10 : Histogramme des prix
- [X] Slide 11 : Extractions et livrables
- [X] Slide 12 : Planification et automatisation
- [ ] Slide 13 : Gestion des erreurs et résilience
- [ ] Slide 14 : Conclusion et questions

#### 6.3 Préparation de la démonstration
- [ ] Préparer la démonstration du workflow Kestra (3 minutes max)
- [ ] Préparer la démonstration de l'interface Kestra
- [ ] Préparer la démonstration des résultats (fichiers générés)
- [ ] Préparer les réponses aux questions techniques anticipées
- [ ] S'entraîner à la présentation complète (15-20 minutes)

#### 6.4 Livrables finaux
- [ ] Vérifier la complétude de tous les livrables
- [ ] Finaliser le fichier .yaml Kestra
- [ ] Finaliser le diagramme Draw.io (PNG + .drawio)
- [ ] Finaliser le support de présentation
- [ ] Remplir la fiche d'autoévaluation
- [ ] Préparer le dernier mentorat de validation

---