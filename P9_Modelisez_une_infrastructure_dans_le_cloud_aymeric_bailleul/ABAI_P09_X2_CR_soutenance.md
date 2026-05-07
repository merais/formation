# Projet 9 — Modélisez une infrastructure dans le cloud

**Évaluation :** mercredi 14 janvier 2026
**Statut :** Projet validé

---

## Remarques sur l'évaluation

**Compétences évaluées**

---

**1. Représenter visuellement une infrastructure de gestion des données**

Validé

Commentaires : Schéma clair, lisible et bien structuré (on-prem / réseau sécurisé / cloud). Les composants cloud (Redpanda, S3, Redshift, DMS, CloudWatch), les flux critiques (IoT/logs), les points de synchronisation (SQL Server, AD) et les protocoles (TLS/LDAPS/CDC) sont bien identifiés.

---

**2. Transformer des données afin de les adapter à leur utilisation finale**

Validé

Commentaires : La logique est cohérente avec l'objectif "temps réel".

---

**3. Charger des données afin de les stocker dans un emplacement adapté**

Validé

Commentaires : Les résultats sont persistés dans un stockage exploitable (MySQL) pour requêtes et analyses. L'architecture prévoit aussi S3/Redshift côté cloud pour stockage/warehouse.

---

**4. Évaluer la compatibilité des composants avec l'environnement SI de l'organisation**

Validé

Commentaires : Les aspects sécurité/identité (TLS, AD trust, IAM), interopérabilité (SQL Server <-> cloud via CDC/JDBC/DMS) et scalabilité sont bien pris en compte. Les éléments de monitoring/cost control (CloudWatch, budgets) sont mentionnés.

---

**5. Extraire des données issues de toutes sources confondues pour les traiter ou les déplacer**

Validé

Commentaires : Les tickets sont produits et publiés dans le topic client_tickets, consommés par PySpark, puis déplacés vers la couche de stockage/consultation. L'enchaînement extraction → traitement → chargement est fonctionnel et démontré.

---

**6. Documenter son travail**

Validé

Commentaires : Diagrammes Mermaid/pipeline clairs + vidéo de démonstration de bonne qualité (POC exécuté, Docker/Redpanda/Spark OK).

---

**7. Identifier et sélectionner les composants nécessaires à une infrastructure de données**

Validé

Commentaires : Les choix sont pertinents et alignés avec les critères. Les liens avec scalabilité/sécurité/interopérabilité sont globalement justifiés.

---

**Livrable**

Points forts :
- Architecture hybride cohérente et lisible, avec sécurité/identité et synchro on-prem <-> cloud bien adressées.
- POC technique opérationnel : Docker, Redpanda, consumer PySpark, persistance et requêtage.
- Documentation visuelle utile (schémas + séquence/pipeline) et démonstration convaincante.

Axes d'amélioration : RAS

---

**Soutenance**

Remarques : La démonstration vidéo et la session live permettent de valider le fonctionnement et la compréhension. Bravo Aymeric !
