# Logbook - P10 Mettez en place le pipeline d'orchestration des flux

**Auteur** : Aymeric Bailleul  
**Date de début** : 15/01/2026  
**Date de fin prévue** : 16/02/2026
**Date de soutenance souhaitable** : Entre le 09/02/2026 et le 13/02/2026

---

## QUESTIONS POUR JEREMY

- Quel comportement les scripts de nettoyage/insertion dans DuckDB doivent avoir : remplacement des données en fonction des fichiers sources donnés ou prendre en compte la possibilité d'une insertion incrémentielle dans la base de données ?

---

## Liste complète des tâches à effectuer

### PHASE 1 : PREPARATION ET ANALYSE

#### 1.1 Analyse des données sources
- [X] Explorer les fichiers erp.xlsx, web.xlsx, liaison.xlsx dans _projet/sources/
- [X] Analyser la structure de chaque fichier (colonnes, types de données)
- [X] Identifier les clés primaires et les relations entre les tables
- [X] Repérer les valeurs manquantes et doublons potentiels
- [X] Documenter les caractéristiques de chaque source : **ABAI_P10_02_analyse_donnees_sources.md**

#### 1.2 Compréhension du processus métier
- [X] Comprendre le processus de réconciliation via le fichier liaison
- [X] Identifier les règles métier pour le calcul du chiffre d'affaires
- [X] Comprendre la méthode de classification des vins (z-score > 2)
- [X] Définir les critères de qualité des données : **ABAI_P10_03_processus_metier.md**

#### 1.3 Configuration de l'environnement de développement
- [X] Installer Docker Desktop
    --> Déjà installé
- [X] Installer Kestra via Docker
    --> `cd tools/kestra && docker-compose up -d`
    --> Conteneurs: kestra-kestra-1 + kestra-postgres-1
- [X] Vérifier le bon fonctionnement de Kestra (accès interface web)
    --> Accessible sur `http://localhost:8080`
- [X] Prendre des captures d'écran de l'installation de Kestra
- [X] Configurer l'environnement Python Poetry avec les dépendances nécessaires
    --> Poetry 2.2.1 - Python 3.14.0 - pandas, openpyxl, black, ruff, pytest installés
- [X] Installer DuckDB et tester son fonctionnement
    --> Ajout de `duckdb = "^1.1.0"` dans le **pyproject.toml** puis `poetry install`
    --> `poetry run duckdb`
    --> DuckDB 1.4.3 installé et testé avec succès
- [X] Prendre des captures d'écran de l'installation de DuckDB

---

### PHASE 2 : CONCEPTION DE L'ARCHITECTURE

#### 2.1 Conception du diagramme de flux (Data lineage)
- [X] Identifier toutes les tâches de transformation nécessaires
    --> 21 tâches identifiées et lister dans **ABAI_P10_04_conception_data_lineage.md**
- [X] Lister les tâches de nettoyage (suppression valeurs manquantes, dédoublonnage)
    --> 9 tâches de nettoyage (3 par fichier source)
- [X] Lister les tâches de fusion (jointures via fichier liaison)
    --> 2 jointures : ERP-LIAISON puis avec WEB
- [X] Lister les tâches d'agrégation (calcul CA par produit et total)
    --> 2 tâches d'agrégation identifiées
- [X] Lister les tâches d'extraction (rapports Excel, CSV premium/ordinaires)
    --> 5 tâches d'extraction (3 branches)
- [X] Identifier les points de test après chaque étape de transformation
    --> 10 tests définis avec valeurs attendues

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

### PHASE 3 : DEVELOPPEMENT DES SCRIPTS

#### 3.1 Scripts Python de nettoyage (TERMINES)
- [X] **01_clean_erp.py** : Chargement + suppression NULL + dédoublonnage ERP
    - Commande : `poetry run python 01_clean_erp.py`
    - Chargement du fichier erp.xlsx avec pandas
    - Suppression des valeurs manquantes (si présentes)
    - Dédoublonnage complet (drop_duplicates)
    - Résultat obtenu : 825 lignes (OK)
    - Stockage : Table erp_clean_final dans bottleneck.db
- [X] **02_clean_liaison.py** : Chargement + suppression NULL + dédoublonnage LIAISON
    - Commande : `poetry run python 02_clean_liaison.py`
    - Chargement du fichier liaison.xlsx avec pandas
    - /!\ NULL conservés sur id_web (91 lignes) - *Produits sans référence web, conservés pour cohérence, filtrés après jointure*
    - Dédoublonnage uniquement
    - Résultat obtenu : 825 lignes (OK)
    - Stockage : Table liaison_clean_final dans bottleneck.db
- [X] **03_clean_web.py** : Chargement + filtrage + suppression NULL + dédoublonnage WEB
    - Commande : `poetry run python 03_clean_web.py`
    - Chargement du fichier web.xlsx avec pandas
    - Filtrage sur post_type = 'product'
    - Suppression des valeurs NULL sur sku
    - Dédoublonnage sur sku (priorité ventes élevées)
    - Résultat obtenu : 714 lignes (OK)
    - Stockage : Table web_clean_final dans _bdd/bottleneck.db

#### 3.2 Scripts Python/SQL de transformation (2 scripts)
- [X] **04_merge_all.py** : Jointures complètes ERP + LIAISON + WEB
    - Commande : `poetry run python 04_merge_all.py`
    - Lecture des tables depuis _bdd/bottleneck.db
    - Jointure ERP + LIAISON sur product_id (825 lignes)
    - Suppression des NULL sur id_web (734 lignes)
    - Jointure avec WEB sur id_web = sku (714 lignes)
    - Résultat obtenu : 714 lignes avec erp_price et total_sales
    - Stockage : Table merged_data_final dans _bdd/bottleneck.db
- [X] **05_calculate_ca.py** : Agrégations CA (par produit + total)
    - Commande : `poetry run python 05_calculate_ca.py`
    - Calcul CA par produit : erp_price × total_sales
    - Calcul CA total : SUM(CA par produit)
    - Valeur obtenue CA total : 70 568,60 € (OK)
    - Stockage : Tables ca_par_produit et ca_total dans _bdd/bottleneck.db

#### 3.3 Scripts Python de classification et extraction (2 scripts)
- [x] **06_classify_wines.py** : Classification complète des vins
    - Commande : `cd _projet && poetry run python _scripts/06_classify_wines.py`
    - Calcul de la moyenne des prix (mu = 32.49€)
    - Calcul de l'écart-type des prix (sigma = 27.81€)
    - Calcul du z-score : (price - mu) / sigma
    - Classification : premium si z-score > 2, sinon ordinaire
    - Valeur attendue : 30 vins premium
    - Table créée : wines_classified (714 lignes, 8 colonnes dont z_score et categorie)
- [x] **07_export_results.py** : Extractions des 3 fichiers de sortie
    - Commande : `cd _projet && poetry run python _scripts/07_export_results.py`
    - Export rapport_ca.xlsx (2 feuilles : CA par produit 714 lignes + CA total 70,568.60€) 
    - Export vins_premium.csv (30 vins premium, CA 6,884.40€) 
    - Export vins_ordinaires.csv (684 vins ordinaires, CA 63,684.20€) 
    - Fichiers créés dans _exports/

#### 3.4 Script de validation globale (1 script)
- [x] **08_validate_all.py** : Validation complète de toute la chaîne
    - Commande : `cd _projet && poetry run python _scripts/08_validate_all.py`
    - **BLOC 1 - Nettoyage** : 4 tests (ERP 825, LIAISON 825, WEB 714, doublons)
    - **BLOC 2 - Jointures** : 2 tests (coherence ERP-LIAISON, coherence finale 714)
    - **BLOC 3 - CA** : 2 tests (CA positifs, CA total 70,568.60 euros)
    - **BLOC 4 - Classification** : 2 tests (z-score valides, 30 vins premium)
    - **Resultat** : 10/10 tests OK (100%)
    - Exit code 0 si OK, 1 si erreur (utilisable dans Kestra)

---

### PHASE 4 : IMPLEMENTATION KESTRA

#### 4.1 Création du workflow Kestra de base
- [ ] Créer le fichier .yaml du workflow
- [ ] Configurer les métadonnées du flow (id, namespace, description)
- [ ] Définir les inputs pour les fichiers sources
- [ ] Créer la tâche de chargement des fichiers Excel

#### 4.2 Implémentation des tâches de nettoyage
- [ ] Implémenter la tâche de nettoyage erp avec DuckDB
- [ ] Implémenter le test après nettoyage erp
- [ ] Implémenter la tâche de nettoyage liaison avec DuckDB
- [ ] Implémenter le test après nettoyage liaison
- [ ] Implémenter la tâche de nettoyage web avec DuckDB
- [ ] Implémenter le test après nettoyage web

#### 4.3 Implémentation des tâches de fusion
- [ ] Implémenter la jointure erp-liaison avec DuckDB
- [ ] Implémenter le test de cohérence de la jointure
- [ ] Implémenter la jointure finale avec web
- [ ] Implémenter le test de cohérence de la jointure finale

#### 4.4 Implémentation des tâches d'agrégation
- [ ] Implémenter le calcul du CA par produit
- [ ] Implémenter le calcul du CA total
- [ ] Implémenter le test du CA total

#### 4.5 Implémentation de la classification des vins
- [ ] Implémenter la tâche Python de calcul du z-score
- [ ] Implémenter le test du z-score
- [ ] Implémenter la classification premium/ordinaire
- [ ] Implémenter le test du nombre de vins premium

#### 4.6 Implémentation des extractions (avec branches Kestra)
- [ ] Créer la branche pour l'extraction du rapport CA en Excel
- [ ] Créer la branche pour l'extraction des vins premium en CSV
- [ ] Créer la branche pour l'extraction des vins ordinaires en CSV

#### 4.7 Configuration de la planification
- [ ] Configurer le trigger avec cron pour exécution le 15 de chaque mois à 9h
- [ ] Tester la syntaxe cron sur Crontab.guru

#### 4.8 Gestion des erreurs
- [ ] Implémenter la gestion des erreurs pour l'indisponibilité de DuckDB
- [ ] Implémenter les mécanismes de retry
- [ ] Implémenter les notifications en cas d'échec

---

### PHASE 5 : TESTS ET VALIDATION

#### 5.1 Tests unitaires
- [ ] Tester individuellement chaque tâche de nettoyage
- [ ] Tester individuellement chaque tâche de jointure
- [ ] Tester individuellement chaque tâche d'agrégation
- [ ] Tester individuellement la classification des vins
- [ ] Vérifier que tous les tests passent avec les valeurs attendues

#### 5.2 Tests d'intégration
- [ ] Exécuter le workflow complet de bout en bout
- [ ] Vérifier que tous les fichiers de sortie sont générés
- [ ] Valider le contenu du rapport CA Excel
- [ ] Valider le contenu du fichier vins premium CSV
- [ ] Valider le contenu du fichier vins ordinaires CSV
- [ ] Vérifier les valeurs de référence (825, 714, 70568.60, 30)

#### 5.3 Tests de robustesse
- [ ] Tester le workflow avec des données incomplètes
- [ ] Tester le comportement en cas d'erreur de connexion DuckDB
- [ ] Tester le mécanisme de retry
- [ ] Valider les notifications d'erreur

#### 5.4 Tests de planification
- [ ] Vérifier que le trigger cron est correctement configuré
- [ ] Simuler une exécution planifiée

---

### PHASE 6 : DOCUMENTATION ET PRESENTATION

#### 6.1 Documentation technique
- [ ] Documenter l'architecture du workflow
- [ ] Documenter chaque tâche du workflow Kestra
- [ ] Documenter les scripts SQL et Python
- [ ] Documenter les tests implémentés
- [ ] Documenter la procédure de déploiement
- [ ] Rédiger le README avec les instructions d'installation et d'utilisation

#### 6.2 Création du support de présentation
- [ ] Slide 1 : Contexte de la mission BottleNeck
- [ ] Slide 2 : Objectifs et enjeux métier
- [ ] Slide 3 : Architecture globale (logigramme Draw.io)
- [ ] Slide 4 : Présentation de Kestra (vulgarisation)
- [ ] Slide 5 : Installation et prise en main de Kestra (captures)
- [ ] Slide 6 : Topologie du workflow Kestra
- [ ] Slide 7 : Détail des tâches de nettoyage et tests
- [ ] Slide 8 : Détail des tâches de fusion et agrégation
- [ ] Slide 9 : Classification des vins (z-score)
- [ ] Slide 10 : Extractions et livrables
- [ ] Slide 11 : Planification et automatisation
- [ ] Slide 12 : Gestion des erreurs et résilience
- [ ] Slide 13 : Résultats et validation des tests
- [ ] Slide 14 : Pistes d'amélioration
- [ ] Slide 15 : Conclusion et questions

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