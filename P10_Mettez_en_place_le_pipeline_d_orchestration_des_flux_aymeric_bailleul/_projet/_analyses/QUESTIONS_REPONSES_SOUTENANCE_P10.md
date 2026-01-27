# 🎯 Questions/Réponses - Soutenance P10 BottleNeck

**Date** : 27/01/2026 | **Projet** : Pipeline d'orchestration BottleNeck

---

## 📋 MÉTIER & CONTEXTE

### **Q1 : Pourquoi réconcilier 3 sources de données ?**
**R** : ERP (stock/prix) + Web (ventes) + Liaison (correspondances) ne communiquent pas. Processus manuel 4h/mois → automatisé en 2 min. Gain 99% + 0 erreur.

### **Q2 : Pourquoi z-score > 2 pour les vins premium ?**
**R** : Méthode statistique objective = top 2,5% des prix. Seuil adaptatif (évolue avec les données). Résultat : 30 vins premium (4,2%).

### **Q3 : Valeur ajoutée pour BottleNeck ?**
**R** : Temps (4h → 2min), Fiabilité (0 erreur), Traçabilité (S3 horodaté), Scalabilité (10x volume sans modif).

---

## 🏗️ ARCHITECTURE & TECHNIQUE

### **Q4 : Pourquoi Kestra plutôt qu'Airflow ?**
**R** : YAML déclaratif vs code Python. Retry exponential natif. UI moderne avec Gantt temps réel. Courbe d'apprentissage plus rapide.

### **Q5 : Architecture des 12 tâches ?**
**R** : 
- Task 1: Download S3
- Tasks 2-4: Clean parallèle (ERP/LIAISON/WEB → 825/825/714)
- Tasks 5-7: Merge + CA + Classify
- Task 8: Validate (10 tests, allowFailure=false)
- Tasks 9-11: Exports parallèles (xlsx + 2 csv)
- Task 12: Upload S3/EXPORTS/YYYYMMDD_HHMMSS/

### **Q6 : Pourquoi Parquet entre les tâches ?**
**R** : Format colonnaire 5-10x plus compact que CSV. Préserve les types. Natif Pandas/PySpark/DuckDB.

### **Q7 : Gestion des erreurs ?**
**R** : Retry exponential (10s→20s→40s max 60s, 3 tentatives). Timeout 10min. Validation bloquante (allowFailure=false). Email auto avec détails + lien Kestra.

---

## 🧪 TESTS & VALIDATION

### **Q8 : Les 10 tests automatiques ?**
**R** : 
**Intermédiaires (4)** : ERP 825L, LIAISON 825L, WEB 1428L, WEB final 714L  
**Globaux (6)** : 714L fusionnées, CA 70568.60€, 30 premium, 684 ordinaires, 0 NULL, cohérence totale

### **Q9 : Validation des 714 lignes finales ?**
**R** : 825 ERP+LIAISON → 734 avec id_web → 714 avec SKU existant. 20 produits ERP jamais vendus = normal. CA cohérent, tous tests passent.

### **Q10 : Fichier source corrompu ?**
**R** : Retry 3x si manquant. Exception Pandas si format invalide → arrêt + email. Validations cardinalité détectent incohérences.

---

## 🔄 DÉPLOIEMENT & PRODUCTION

### **Q11 : Déploiement en production ?**
**R** : Docker Compose (Kestra + PostgreSQL). Credentials AWS encodés BASE64 dans .env. Trigger cron "0 9 15 * *" (9h le 15/mois).

### **Q12 : Scalabilité à 10 000 produits ?**
**R** : Actuel 714 en 2min. Estimé 10k en 15-20min. Pandas in-memory OK jusqu'à 50k. Au-delà : PySpark + DuckDB + partitionnement.

### **Q13 : Pourquoi S3 plutôt que local ?**
**R** : Durabilité 99.999999999%, accessibilité équipe, versioning auto (YYYYMMDD_HHMMSS), backup multi-zones, coût < 1$/an.

---

## 📊 DONNÉES & ANALYSE

### **Q14 : Pourquoi 1428 lignes Web mais 714 uniques ?**
**R** : WooCommerce : product (714) + product_variation (714). Tri post_type descendant + dédoublonnage keep='first' → 714 products.

### **Q15 : 30 premium = 6884€ sur 70568€ total ?**
**R** : 4,2% du catalogue = 9,8% du CA. Premium 229€/produit vs ordinaires 93€/produit (2,5x). Normal pour vins d'exception (faible rotation).

### **Q16 : DuckDB vs Parquet ?**
**R** : DuckDB = dev local (SQL pour tester jointures). Parquet = prod Kestra (format fichier entre tâches). Workflow : explore SQL → code Pandas → échange Parquet.

---

## ⚙️ CHOIX TECHNIQUES

### **Q17 : Python/Pandas vs SQL pur ?**
**R** : Pandas : flexibilité nettoyage, z-score natif, intégration S3/Kestra. SQL adapté si données déjà en BDD. Compromis : dev DuckDB + prod Pandas.

### **Q18 : Sécurité credentials AWS ?**
**R** : Encodés BASE64, stockés .env (jamais Git), décodés dans YAML via `{{ secret() | b64decode }}`. IAM policy limitée au bucket.

### **Q19 : Trigger 9h00 vs nuit ?**
**R** : Sources dispo 8h00. Support équipe si échec. Rapports pour réunions 10h-11h. Nuit OK si ultra-stable (> 6 mois sans échec).

### **Q20 : Évolutions futures ?**
**R** : 
**Court terme** : Dashboard Grafana, tests pytest, ADR  
**Moyen terme** : Profiling perf, ML prédictions, CI/CD  
**Long terme** : Data Warehouse, streaming Kafka, API REST

---

## 📚 DIFFICULTÉS RENCONTRÉES

### **Q21 : Principales difficultés ?**
**R** : 
1. Doublons WooCommerce (product_variation) → tri + keep='first'
2. Credentials AWS mal encodés → décodage explicite BASE64
3. Arrondis CA (70568.599999 vs .60) → tolérance np.isclose()
4. Choix z-score → tests z=1.5/2/2.5, retenu z=2 (30 vins cohérent)

**Leçons** : Explorer données avant automatiser. Tester mini-datasets. Logger abondamment.

---

**Auteur** : Aymeric Bailleul | **Projet** : P10 BottleNeck | **Date** : 27/01/2026
