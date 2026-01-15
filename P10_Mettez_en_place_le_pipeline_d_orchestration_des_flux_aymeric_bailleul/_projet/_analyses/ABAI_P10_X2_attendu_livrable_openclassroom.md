# Livrables attendus - P10 Projet OpenClassrooms

---

## Vue d'ensemble

Voici un rappel des documents que vous devez déposer sur la plateforme.

---

## Tableau récapitulatif des livrables

| Compétences | Activités | Livrables |
|-------------|-----------|-----------|
| Mettre en place l'ordonnancement des flux des données pour programmer leur déclenchement | Conception de l'architecture d'automatisation | Diagramme de flux des tâches réalisé (au format .drawio) |
| | Orchestration des tâches nominales avec Kestra | Workflow d'automatisation des tâches de traitement des données |
| Créer des processus de test et les lancer afin de valider la mise en production des pipelines de données | Implémentation des tâches de tests avec Kestra | Enrichissement du workflow d'automatisations des tâches avec tests |
| | Conception de votre support de présentation et préparation votre soutenance | Une présentation au format type PowerPoint |

---

## COMPÉTENCE 1 : Mettre en place l'ordonnancement des flux des données

### Activité 1.1 : Conception de l'architecture d'automatisation

**Livrable attendu :**
- **Diagramme de flux des tâches** réalisé au format `.drawio`

---

### Activité 1.2 : Orchestration des tâches nominales avec Kestra

**Livrable attendu :**
- **Workflow d'orchestration sur Kestra** en `.yaml`

**Le workflow doit inclure les scripts SQL ou Python de :**

#### Scripts de nettoyage
- Dédoublonnage
- Suppressions des données manquantes

#### Scripts de transformation
- Fusion (jointures entre les fichiers)

#### Scripts de calcul
- Calcul du chiffre d'affaires par produit
- Calcul du chiffre d'affaires global

#### Scripts de classification
- Détection des vins millésimes et ordinaires en Python

**Fichiers de sortie à générer :**
- **Rapport du chiffre d'affaires par produit** en `.xlsx`
- **Extraction des vins millésimes** en `.csv`
- **Extraction des vins ordinaires** en `.csv`

---

## COMPÉTENCE 2 : Créer des processus de test

### Activité 2.1 : Implémentation des tâches de tests avec Kestra

**Livrable attendu :**
- **Enrichissement du workflow d'automatisations** avec tâches de tests

**Le workflow doit inclure les scripts SQL ou Python de vérification :**

#### Tests de qualité des données
- Vérification de **l'absence de doublons**
- Vérification de **l'absence de valeurs manquantes**

#### Tests de cohérence
- Vérification de **la cohérence de la volumétrie des données après les jointures**
  - ERP après nettoyage : 825 lignes
  - LIAISON après nettoyage : 825 lignes
  - WEB après nettoyage : 714 lignes
  - Données fusionnées : 714 lignes

#### Tests de calculs
- Vérification de **la cohérence du chiffre d'affaires calculé**
  - Valeur attendue : 70 568,60 €

#### Tests de classification
- Vérification de **la cohérence de la volumétrie des vins millésimes et ordinaires avec le z-score**
  - Vins millésimes (z-score > 2) : 30 vins attendus

---

## COMPÉTENCE 3 : Présentation et soutenance

### Activité 3.1 : Conception de votre support de présentation

**Livrable attendu :**
- **Présentation au format PowerPoint** (ou équivalent)

**La présentation doit rappeler :**
- Le contexte du projet BottleNeck
- La démarche technique justifiée

**La présentation doit inclure :**

#### 1. Diagramme des flux de tâches
Représentation visuelle pour :
- Ingérer les données (3 fichiers sources)
- Nettoyer les données (suppression NULL, dédoublonnage)
- Fusionner les données (jointures)
- Agréger les données (calcul CA)
- Extraire les données (3 fichiers de sortie)

#### 2. Workflow d'automatisation sur Kestra
- Topologie du workflow
- Démonstration de la prise en main de l'outil
- Captures d'écran de l'interface Kestra

#### 3. Tests mis en place
- Liste des tests implémentés
- Valeurs attendues vs obtenues
- Mécanismes de validation

---

## LISTE COMPLÈTE DES LIVRABLES À DÉPOSER

### 1. Fichiers techniques

#### a) Architecture
- [ ] `diagramme_flux_taches.drawio` - Diagramme de flux complet

#### b) Workflow Kestra
- [ ] `workflow_kestra.yaml` - Fichier YAML d'orchestration avec :
  - Scripts SQL de nettoyage (dédoublonnage, suppression NULL)
  - Scripts SQL de fusion (jointures)
  - Scripts SQL de calcul (CA par produit, CA total)
  - Scripts Python de classification (z-score, millésimes/ordinaires)
  - Scripts de tests (SQL et Python)

#### c) Fichiers de sortie générés par le workflow
- [ ] `rapport_ca.xlsx` - Rapport chiffre d'affaires
- [ ] `vins_millesimes.csv` - Liste des vins premium
- [ ] `vins_ordinaires.csv` - Liste des vins ordinaires

### 2. Présentation

- [ ] `presentation_soutenance.pptx` - Support de présentation avec :
  - Contexte et enjeux
  - Diagramme de flux
  - Workflow Kestra (topologie + démo)
  - Tests et validations
  - Résultats et conclusions

---

##  CRITÈRES DE VALIDATION

### Workflow Kestra
-  Fichier YAML valide et exécutable
-  Scripts SQL/Python intégrés et fonctionnels
-  Génération automatique des 3 fichiers de sortie
-  Tests intégrés avec valeurs de référence

### Tests
-  Absence de doublons vérifiée
-  Absence de valeurs manquantes vérifiée
-  Volumétrie cohérente (825, 714 lignes)
-  CA total = 70 568,60 €
-  30 vins millésimes identifiés

### Présentation
-  Contexte clair
-  Démarche technique justifiée
-  Diagramme de flux lisible
-  Démonstration Kestra préparée
-  Tests documentés

---

##  NOTES IMPORTANTES

### Terminologie
- **"Vins millésimes"** dans le sujet = **"Vins premium"** dans la documentation
- Critère : z-score > 2

### Format des fichiers
- Diagramme : `.drawio` (obligatoire)
- Workflow : `.yaml` (obligatoire)
- Rapport CA : `.xlsx` (obligatoire)
- Extractions vins : `.csv` (obligatoire)
- Présentation : PowerPoint ou équivalent

### Points de vigilance
- Inclure les scripts dans le fichier YAML (pas de fichiers séparés)
- Documenter les valeurs de référence dans les tests
- Préparer une démonstration de 3-5 minutes de Kestra
- Expliquer le z-score de manière vulgarisée

---

