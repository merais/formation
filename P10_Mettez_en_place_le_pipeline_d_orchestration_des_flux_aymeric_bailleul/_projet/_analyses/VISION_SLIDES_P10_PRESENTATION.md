# 🎯 Vision des Slides - Présentation P10 BottleNeck

**Durée totale** : 15-20 minutes  
**Format** : 15 slides + démonstration live (3 min)

---

## 📊 SLIDE 1 : Page de titre

**Contenu** :
```
PIPELINE D'ORCHESTRATION DES FLUX DE DONNÉES
Projet BottleNeck - Réconciliation multi-sources

Aymeric Bailleul
Data Engineer
OpenClassrooms - Janvier 2026
```

**Visuel** : Logo BottleNeck + Icônes Kestra, AWS S3, Python

**Note orale** : "Bonjour, je vais vous présenter mon pipeline d'orchestration pour BottleNeck, une entreprise viticole."

---

## 🎯 SLIDE 2 : Contexte de la mission BottleNeck

**Titre** : Le défi BottleNeck

**Contenu** :
- **Problème métier** :
  - 3 sources de données isolées (ERP, Web, fichier liaison)
  - Processus manuel mensuel (15 du mois)
  - Risques d'erreurs et temps perdu
  - Pas de traçabilité ni automatisation

- **Données sources** :
  - ERP : 825 produits (stock, prix)
  - Web : 1428 entrées (ventes, SKU)
  - Liaison : 825 correspondances (id_erp ↔ id_web)

**Visuel** : Schéma 3 silos de données déconnectés

**Note orale** : "BottleNeck doit réconcilier manuellement 3 sources chaque mois. Mon objectif : automatiser ce processus."

---

## 🎯 SLIDE 3 : Objectifs et enjeux métier

**Titre** : Objectifs du pipeline

**Contenu** :
✅ **Automatisation complète** du processus mensuel  
✅ **Réconciliation** des 3 sources de données  
✅ **Calcul du CA** par produit et total (70 568,60 €)  
✅ **Classification** des vins (premium vs ordinaires, z-score > 2)  
✅ **Exports automatisés** : Excel + 2 CSV  
✅ **Validation** : 9 tests automatiques  
✅ **Résilience** : Retry + gestion d'erreurs + alertes  

**KPI attendus** :
- 714 produits réconciliés
- 30 vins premium identifiés
- Temps d'exécution : ~2 minutes

**Visuel** : Checklist avec icônes vertes

---

## 🏗️ SLIDE 4 : Architecture globale (Data Lineage)

**Titre** : Architecture du pipeline

**Contenu** : **Insérer le diagramme Draw.io v3**

**Points clés à annoter** :
- 📥 Entrée : 3 fichiers Excel (S3/RAW)
- 🔄 Transformation : 12 tâches Kestra
- ⚡ Parallélisme : 2 groupes (nettoyage + exports)
- ✅ Validations : 9 points de contrôle
- 📤 Sortie : 3 fichiers (S3/EXPORTS)

**Note orale** : "Voici le flux complet : téléchargement S3, nettoyage parallèle des 3 sources, fusion, calculs, validation, exports parallèles, puis upload S3."

---

## 🛠️ SLIDE 5 : Présentation de Kestra (vulgarisation)

**Titre** : Pourquoi Kestra ?

**Contenu** :
**Qu'est-ce que Kestra ?**
- Orchestrateur de workflows open-source
- Alternative moderne à Airflow (plus simple)
- Configuration YAML déclarative
- Interface web intuitive

**Avantages pour BottleNeck** :
- ✅ Orchestration visuelle des tâches
- ✅ Parallélisation native (gain de temps)
- ✅ Gestion d'erreurs avancée (retry, alertes)
- ✅ Planification automatique (cron mensuel)
- ✅ Logs détaillés pour debugging

**Comparaison rapide** :
| Critère | Airflow | Kestra |
|---------|---------|--------|
| Configuration | Python (code) | YAML (déclaratif) |
| Courbe d'apprentissage | Complexe | Simple |
| Interface | Basique | Moderne |
| Retry natif | Limité | Avancé |

**Visuel** : Logo Kestra + screenshot interface

---

## 💻 SLIDE 6 : Installation et prise en main de Kestra

**Titre** : Déploiement Docker

**Contenu** :
**Stack technique** :
```yaml
Docker Compose :
  - Kestra (latest)
  - PostgreSQL (backend)
  - Volumes persistants
```

**Configuration** :
- Secrets AWS encodés BASE64 (.env)
- Variables d'environnement sécurisées
- Accès : http://localhost:8080

**Captures d'écran** :
1. Terminal : `docker-compose up -d`
2. Interface Kestra : Dashboard
3. Workflow déployé : bottleneck_pipeline_s3

**Note orale** : "Déploiement simple avec Docker Compose. Les credentials AWS sont sécurisés via variables d'environnement."

---

## 🔀 SLIDE 7 : Topologie du workflow Kestra

**Titre** : Architecture des 12 tâches

**Contenu** :
```
TASK 1: Download S3 (3 fichiers Excel)
         ↓
┌────────┴────────┐
│ PARALLEL GROUP  │ (Nettoyage simultané)
├─────────────────┤
│ TASK 2: Clean ERP      (825 → 825)  ✅ Validation
│ TASK 3: Clean LIAISON  (825 → 825)  ✅ Validation
│ TASK 4: Clean WEB      (1428 → 714) ✅ Validation
└─────────────────┘
         ↓
TASK 5: Merge (714 lignes fusionnées)
         ↓
TASK 6: Calculate CA (70 568,60 €)
         ↓
TASK 7: Classify (30 premium, 684 ordinaires)
         ↓
TASK 8: Validate ✅ (5 tests globaux)
         ↓
┌────────┴────────┐
│ PARALLEL GROUP  │ (Exports simultanés)
├─────────────────┤
│ TASK 9:  rapport_ca.xlsx
│ TASK 10: vins_premium.csv
│ TASK 11: vins_ordinaires.csv
└─────────────────┘
         ↓
TASK 12: Upload S3/EXPORTS/YYYYMMDD_HHMMSS/
```

**Métriques** :
- Temps total : ~2 minutes
- Parallélisme : 2 groupes (gain 40%)
- Validations : 9 points de contrôle

---

## 🧹 SLIDE 8 : Détail des tâches de nettoyage et tests

**Titre** : Nettoyage parallèle (Tasks 2-4)

**Contenu** :

**Task 2 - Clean ERP** :
- Suppression valeurs manquantes
- Dédoublonnage sur product_id
- ✅ Validation : 825 lignes exactement
- Output : erp_clean.parquet

**Task 3 - Clean LIAISON** :
- Conservation NULL sur id_web (filtre après jointure)
- Dédoublonnage uniquement
- ✅ Validation : 825 lignes exactement
- Output : liaison_clean.parquet

**Task 4 - Clean WEB** :
- Suppression NULL sur sku (85 NULL)
- Résultat intermédiaire : 1428 lignes
- ✅ Validation intermédiaire : 1428 lignes
- Tri descendant sur post_type (priorise 'product')
- Dédoublonnage sur sku (keep='first')
- ✅ Validation finale : 714 lignes (que des products)
- Output : web_clean.parquet

**Points clés** :
- ⚡ Exécution parallèle (3 tâches simultanées)
- ✅ 4 validations intermédiaires avec sys.exit(1)
- 📦 Format Parquet (performance)

**Visuel** : Diagramme des 3 flux parallèles avec validations

---

## 🔗 SLIDE 9 : Détail des tâches de fusion et agrégation

**Titre** : Fusion et calculs (Tasks 5-6)

**Contenu** :

**Task 5 - Merge (Assemblage des données)** :
Fusion des 3 fichiers nettoyés en 3 étapes :
1. **ERP + LIAISON** → 825 produits reliés par leur code interne
2. **Filtrage** → 734 produits (retrait de ceux jamais vendus en ligne)
3. **+ WEB** → **714 produits finaux** avec toutes les infos (stock, prix, ventes)

✅ **Output** : merged_data.parquet (714 lignes)

**Analogie** : Assembler un puzzle en connectant les pièces par leurs encoches communes

---

**Task 6 - Calculate CA (Calcul du Chiffre d'Affaires)** :
Calcul simple pour chaque vin : **Prix × Quantité vendue = CA produit**

*Exemple : Bordeaux 45€ × 12 ventes = 540€*

**CA total automatisé : 70 568,60 €** ✅

✅ **Output** : merged_with_ca.parquet (714 lignes + colonne ca_produit)

---

**Métriques clés** :
- 825 → 734 → 714 lignes (pertes tracées et justifiées)
- CA total validé : 70 568,60 € (tolérance ±0,01€)

**Visuel** : Schéma jointures avec cardinalités

---

## 📈 SLIDE 10 : Classification des vins (z-score)

**Titre** : Classification statistique (Task 7)

**Contenu** :

**Méthode du z-score** : Identification automatique des vins haut de gamme

**Comment ça marche ?**

1️⃣ **Calcul du prix moyen** : 32,49 €  
2️⃣ **Calcul de la dispersion** (écart-type) : ±27,81 €  
3️⃣ **Mesure de l'écart** pour chaque vin :
   - Vin à 40€ → écart normal (proche de la moyenne)
   - Vin à 90€ → **écart exceptionnel** (très au-dessus)

**Règle de classification** :
- **Z-score > 2** → Vin dans le **top 2,5%** des prix → **Premium** ✨
- **Z-score ≤ 2** → Vin dans la gamme normale → **Ordinaire**

**Interprétation** :
- Z-score > 2 : Prix > moyenne + 2 écarts-types
- Correspond aux vins haut de gamme (2,5% théorique)
- Résultat obtenu : 30 vins premium (4,2%)

**Résultats** :
- ✅ 30 vins premium (CA : 6 884,40 €)
- ✅ 684 vins ordinaires (CA : 63 684,20 €)
- ✅ Total : 70 568,60 € (cohérence validée)

**Visuel** : Courbe normale avec seuil z=2 annoté + histogramme des prix

---

## 📤 SLIDE 11 : Extractions et livrables

**Titre** : Exports parallèles (Tasks 9-11)

**Contenu** :

**Task 9 - Rapport CA (Excel)** :
- 2 feuilles : "CA par produit" + "CA total"
- 714 produits détaillés
- Format Excel pour analyse business

**Task 10 - Vins Premium (CSV)** :
- 30 vins avec z-score > 2
- Colonnes : product_id, price, total_sales, ca_produit, z_score
- CA total premium : 6 884,40 €

**Task 11 - Vins Ordinaires (CSV)** :
- 684 vins avec z-score ≤ 2
- Mêmes colonnes que premium
- CA total ordinaires : 63 684,20 €

**Task 12 - Upload S3** :
- Destination : S3/EXPORTS/YYYYMMDD_HHMMSS/
- Horodatage automatique
- Traçabilité complète

**Gain parallélisme** : 3 exports simultanés (gain 66%)

**Visuel** : Screenshots des 3 fichiers finaux + structure S3

---

## ⏰ SLIDE 12 : Planification et automatisation

**Titre** : Exécution automatique mensuelle

**Contenu** :

**Trigger Cron** :
```yaml
triggers:
  - id: monthly_execution
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 15 * *"
    timezone: "Europe/Paris"
```

**Signification** :
- Tous les **15 du mois** à **9h00** (heure Paris)
- Exécution automatique sans intervention
- Parfaitement aligné avec le besoin métier

**Calendrier 2026** :
| Mois | Date d'exécution | Statut |
|------|------------------|--------|
| Janvier | 15/01 à 9h | ✅ Réalisé |
| Février | 15/02 à 9h | ⏳ Planifié |
| Mars | 15/03 à 9h | ⏳ Planifié |

**Avantages** :
- ✅ Zéro intervention manuelle
- ✅ Exécution prévisible
- ✅ Traçabilité dans logs Kestra

---

## 🛡️ SLIDE 13 : Gestion des erreurs et résilience

**Titre** : Robustesse et fiabilité

**Contenu** :

**1. Mécanisme de nouvelle tentative** :
```yaml
retry:
  type: exponential
  maxAttempt: 3
  interval: PT10S
  maxInterval: PT60S
```
- 3 tentatives automatiques
- Délais croissants : 10s → 20s → 40s (max 60s)
- Évite la surcharge des services défaillants

**2. Délai d'expiration** :
- 10 minutes par tâche
- Protection contre blocages infinis

**3. Validation bloquante (Task 8)** :
```yaml
allowFailure: false  # Bloque les exports si échec
```
- 5 tests obligatoires : vérification du nombre de lignes fusionnées (714), du CA total (70568,60€), du nombre de vins premium (30) et ordinaires (684), et absence de valeurs NULL dans les CA
- Si un seul test échoue → sys.exit(1) → arrêt immédiat du workflow → aucun export généré

**4. Notification email avec détails de l'erreur** :
```yaml
errors:
  - type: io.kestra.plugin.notifications.mail.MailSend
    to: ["data-team@company.com", "aymeric.bailleul@company.com"]
    subject: "[ERREUR] Pipeline BottleNeck - Echec"
    htmlTextContent: |
      - Workflow ID, Execution ID, dates
      - Tâche en échec : {{ taskrun.task.id }}
      - Message d'erreur détaillé
      - Lien direct vers l'exécution Kestra
```
- **Contenu du mail** :
  - 📋 Infos d'exécution (ID, dates, statut)
  - ❌ **Erreur détaillée** (tâche + message complet)
  - 🔗 Lien direct vers logs Kestra
  - 🔧 Actions recommandées pour correction
- Configuration SMTP dans .env (Gmail/AWS SES/MailHog)
- Envoi **automatique** dès échec détecté

**Scénarios de test validés** :
- ✅ Erreur de validation → workflow arrêté + mail envoyé
- ✅ Retry sur erreur temporaire → récupération sans mail
- ✅ Mail contient l'erreur exacte (sys.exit(1) message)
- ✅ Logs détaillés pour debugging

---

## 📋 SLIDE 14 : Les 10 tests automatiques

**Titre** : Stratégie de validation complète

**Contenu** :

**Tests intermédiaires (Tasks 2-4)** :
1. ✅ **Test ERP** : Validation de 825 lignes après nettoyage
2. ✅ **Test LIAISON** : Validation de 825 lignes après dédoublonnage
3. ✅ **Test WEB étape 1** : Validation de 1428 lignes après suppression des NULL
4. ✅ **Test WEB étape 2** : Validation de 714 lignes après dédoublonnage final

**Tests globaux (Task 8 - Validation finale)** :
5. ✅ **Test de cardinalité** : Vérification de 714 lignes fusionnées exactement
6. ✅ **Test de cohérence CA** : Validation du CA total à 70 568,60 € (tolérance ±0,01€)
7. ✅ **Test classification premium** : Vérification de 30 vins avec z-score > 2
8. ✅ **Test classification ordinaire** : Vérification de 684 vins avec z-score ≤ 2
9. ✅ **Test d'intégrité NULL** : Absence de valeurs NULL dans les colonnes CA
10. ✅ **Test de cohérence totale** : CA premium (6 884,40 €) + CA ordinaires (63 684,20 €) = CA total (70 568,60 €)

**Comportement en cas d'échec** :
- Tout échec → `sys.exit(1)` → arrêt immédiat du workflow
- `allowFailure: false` empêche la génération d'exports invalides
- Notification email automatique avec détails de l'erreur

**Résultat** : **10/10 tests réussis** ✅

---


## 🎤 SLIDE 16 : Conclusion et questions

**Titre** : Récapitulatif

**Contenu** :

**Objectifs atteints** :
✅ Pipeline entièrement automatisé  
✅ Réconciliation des 3 sources réussie  
✅ 714 produits traités, CA validé (70 568,60 €)  
✅ Classification statistique opérationnelle  
✅ 10/10 tests automatiques réussis  
✅ Déploiement production-ready  

**Technologies maîtrisées** :
- Kestra (orchestration)
- AWS S3 (stockage cloud)
- Python/Pandas (transformation)
- DuckDB (développement local)
- Docker (conteneurisation)
- Git (versioning)

**Valeur ajoutée BottleNeck** :
- Gain temps : 4h → 2 min (99% de réduction)
- Fiabilité : 0 erreur manuelle
- Traçabilité : logs complets
- Scalabilité : prêt pour croissance

---

**Questions ?**

**Contact** : aymeric.bailleul@example.com  
**GitHub** : github.com/merais/formation  
**Documentation complète** : README.md

---

## 🎬 DÉMONSTRATION LIVE (3 minutes)

**Script de démo** :

1. **Montrer l'interface Kestra** (30s)
   - Dashboard workflows
   - Historique exécutions
   - Gantt Chart du dernier run

2. **Déclencher une exécution manuelle** (15s)
   - Clic "Execute"
   - Montrer démarrage du workflow

3. **Suivre l'exécution en temps réel** (90s)
   - Parallélisme du nettoyage (tasks 2-4)
   - Validations intermédiaires
   - Logs d'une tâche spécifique
   - Progression vers exports

4. **Montrer les résultats** (45s)
   - Fichiers dans S3/EXPORTS/YYYYMMDD_HHMMSS/
   - Ouvrir rapport_ca.xlsx (2 feuilles)
   - Aperçu vins_premium.csv (30 lignes)

**Backup si problème technique** :
- Screenshots préparés pour chaque étape
- Vidéo screencast de l'exécution complète

---

## 📝 NOTES POUR LA PRÉSENTATION

**Timing recommandé** :
- Slides 1-3 : 3 minutes (contexte)
- Slides 4-7 : 5 minutes (architecture/tech)
- Slides 8-11 : 5 minutes (détail technique)
- Slides 12-14 : 3 minutes (résultats)
- Slides 15-16 : 2 minutes (conclusion)
- Démo live : 3 minutes
- Questions : 5-10 minutes

**Total** : 18-20 minutes + Q&A

**Conseils** :
- Adapter le niveau technique selon l'audience
- Privilégier les visuels aux blocs de texte
- Préparer 3-4 questions anticipées
- Tester la démo 2 fois avant présentation
- Avoir un backup sans démo si problème réseau

---

**Créé le** : 23/01/2026  
**Auteur** : Aymeric Bailleul  
**Projet** : P10 - BottleNeck Pipeline
