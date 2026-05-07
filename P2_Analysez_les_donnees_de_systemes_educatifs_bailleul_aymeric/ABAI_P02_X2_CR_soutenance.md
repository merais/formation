# Projet 2 — Analysez les données de systèmes éducatifs

**Évaluation :** mercredi 3 septembre 2025
**Statut :** Projet validé

---

## Remarques sur l'évaluation

**Compétences évaluées**

En vous basant sur les critères d'évaluation dans le guide mentor du projet, définissez le statut d'acquisition de chaque compétence listée ci-dessous :

Validé - Expliquez pourquoi en partageant des retours constructifs

Non validé - Expliquez de façon constructive pourquoi et comment l'étudiant peut s'améliorer, en vous appuyant sur les critères d'évaluations

---

**1. Appliquer des analyses statistiques descriptives et naviguer visuellement dans les données**

Validé

Commentaires :

Notebook **Jupyter** OK ; imports `pandas/matplotlib/seaborn` OK ; `.shape`, `.describe()`, `value_counts()` et distributions tracées ; matrices de corrélation **Pearson & Spearman** utilisées. À renforcer : ajouter `df.info()` (typage) et une phrase explicite "**une ligne = …**" ; veiller à **titres + axes** sur tous les graphiques.

---

**2. Configurer l'environnement de travail nécessaire à l'exploitation des données**

Validé

Commentaires :

Environnement **Poetry** fonctionnel, exécution du notebook OK.

---

**3. Corriger les anomalies manuellement et à l'aide d'outils adaptés**

Validé

Commentaires :

Doublons quantifiés/supprimés ; valeurs manquantes quantifiées ; filtres conditionnels (`==`, `.isin()`) ; corrélation utilisée pour réduire la redondance. Filtrer les faux pays via référentiel. Abaisser le **seuil** de redondance à **"|r| ≥ 0,70"**, et **qualifier** les corrélations (afficher le **n pairwise**, traiter les ±1 dus à faible n/duplication).

---

**Livrable**

Points forts :
- Cadrage métier clair
- EDA structurée
- corrélations Pearson/Spearman
- code factorisé (fonctions/boucles)
- shortlist finale lisible.

Axes d'amélioration :
- Mesurer la **couverture** indicateur×année (proportions).
- Expliciter la **règle de score** (normalisation + agrégation) et les **seuils** retenus.
- Corriger les **coquilles** des slides ; lister **indicateurs retirés/gardés** avec justification (couverture/pertinence).

---

**Soutenance**

Remarques :
- Justifier la **sélection** des indicateurs (couverture, pertinence, corrélation) et mentionner les **limites** (faible n, notes *FootNote*).
- Raconter le pipeline en 1 slide : **brut → nettoyage → couverture → corrélation → pivot → score → top-5**.
- 1 slide = 1 élément à raconter (lié au **business**)
- Expliquer quelques indicateurs **d'un point de vue métier**
