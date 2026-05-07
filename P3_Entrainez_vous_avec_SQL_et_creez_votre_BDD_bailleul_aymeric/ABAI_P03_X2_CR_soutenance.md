# Projet 3 — Entraînez-vous avec SQL et créez votre BDD

**Évaluation :** vendredi 19 septembre 2025
**Statut :** Projet validé

---

## Remarques sur l'évaluation

**Compétences évaluées**

---

**1. Créer des bases de données relationnelles afin de contenir les données**

Validé

Commentaires :

Schéma créé, tables peuplées + contrôles de volumétrie, volet RGPD/sauvegarde présent. Ajouter un DDL complet (PK/FK, index, contraintes)

---

**2. Structurer les données et leurs relations en cohérence avec leurs caractéristiques**

Validé

Commentaires :

Modèle cohérent et jointures correctes ; requêtes couvrent les cas du corrigé. Harmoniser granularité (ex. `COUNT(DISTINCT id_bien)` quand on parle de ventes) et nomenclature colonnes/types.

---

**Livrable**

Points forts : schéma normalisé clair ; requêtes variées (agrégations, fenêtres, TOP N) ; volet RGPD.

Axes d'amélioration : fournir DDL versionné (PK/FK/index), expliciter règles de qualité (`>0`, dates ISO), et aligner les métriques avec le corrigé (`DISTINCT`)

---

**Soutenance**

Remarques : montrer rapidement MCD/MPD + choix de normalisation, conclure par RGPD & pistes d'industrialisation (index, vues matérialisées, tests)
