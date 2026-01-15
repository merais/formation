# Logbook - P10 Mettez en place le pipeline d'orchestration des flux

**Auteur** : Aymeric Bailleul  
**Date de début** : 15/01/2026  
**Date de fin prévue** : 16/02/2026
**Date de soutenance souhaitable** : Entre le 09/02/2026 et le 13/02/2026

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

#### 3.1 Scripts SQL DuckDB
- [ ] Script de chargement des fichiers Excel dans DuckDB
- [ ] Script de suppression des valeurs manquantes pour erp.xlsx
- [ ] Script de dédoublonnage pour erp.xlsx
- [ ] Script de suppression des valeurs manquantes pour liaison.xlsx
- [ ] Script de dédoublonnage pour liaison.xlsx
- [ ] Script de suppression des valeurs manquantes pour web.xlsx
- [ ] Script de dédoublonnage pour web.xlsx
- [ ] Script de jointure entre erp et liaison
- [ ] Script de jointure entre le résultat et web
- [ ] Script de calcul du chiffre d'affaires par produit
- [ ] Script de calcul du chiffre d'affaires total

#### 3.2 Scripts Python
- [ ] Script de calcul du z-score sur les prix des vins
- [ ] Script de classification des vins (premium si z-score > 2, ordinaire sinon)
- [ ] Script d'extraction des vins premium en CSV
- [ ] Script d'extraction des vins ordinaires en CSV
- [ ] Script d'extraction du rapport CA en Excel

#### 3.3 Scripts de tests SQL/Python
- [ ] Test d'absence de doublons après nettoyage erp (attendu: 825 lignes)
- [ ] Test d'absence de doublons après nettoyage liaison (attendu: 825 lignes)
- [ ] Test d'absence de valeurs manquantes après nettoyage web
- [ ] Test d'absence de doublons après nettoyage web (attendu: 714 lignes)
- [ ] Test de cohérence de la jointure erp-liaison
- [ ] Test de cohérence de la jointure finale (attendu: 714 lignes)
- [ ] Test du chiffre d'affaires total (attendu: 70 568,60 euros)
- [ ] Test du nombre de vins premium (attendu: 30 vins)
- [ ] Test de validité du z-score (formule correcte)

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