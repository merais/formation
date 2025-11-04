# 10 — Cheatsheet NoSQL

Ce mémo résume l'essentiel pour choisir et utiliser une base NoSQL, d'après le cours « Immergez vos données dans le NoSQL ».

## Qu'est-ce que le NoSQL ?

- NoSQL = Not Only SQL: alternatives au modèle relationnel, pensées pour la distribution (scalabilité, disponibilité) et l'agilité du schéma.
- Idée clé: relâcher certaines contraintes (ACID global, schéma rigide) pour optimiser le débit, la latence et l'élasticité.
- Le choix dépend du modèle de données, des requêtes dominantes et des exigences CAP (cohérence/disponibilité/partition).

## Les 4 familles NoSQL

1) Clé–valeur (ex: Redis)
- Modèle: paires clé → valeur; structures simples (string, hash, liste, set…)
- + Ultra rapide, simple, idéal pour cache, sessions, rate limiting, files légères
- − Requêtes complexes difficiles, pas de jointure
- Usages: cache applicatif, compteur, tokens, verrous, leaderboard

2) Orienté colonnes (ex: Cassandra, HBase)
- Modèle: familles de colonnes, stockage par colonne, partitionnement par clé
- + Très bon pour séries temporelles, logs, énormes volumétries, écritures massives
- − Schéma d'accès à concevoir en amont; agrégations ad hoc moins naturelles
- Usages: timeseries, événements IoT, métriques, data à haute cardinalité

3) Orienté documents (ex: MongoDB, Couchbase)
- Modèle: documents JSON/BSON hiérarchiques (sous-documents)
- + Schéma flexible, requêtes riches, index variés, bon compromis dev/ops
- − Transactions multi-documents limitées selon moteurs; coût des docs trop imbriqués
- Usages: contenus semi-structurés, profils, catalogues, applications web

4) Graphe (ex: Neo4j)
- Modèle: nœuds + arêtes + propriétés; relation au centre
- + Traversées de graphes rapides; requêtes relationnelles profondes
- − Modèle spécialisé; volumétrie extrême à concevoir finement
- Usages: réseaux sociaux, recommandations, détection de fraude, IAM

## Théorème CAP

- C = Cohérence, A = Disponibilité, P = Tolérance au partitionnement.
- Sous partition réseau, on ne peut pas garantir C et A parfaites en même temps.
- Tendances: Cassandra ≈ AP (cohérence éventuelle configurable), HBase ≈ CP, MongoDB = cohérence configurable (readConcern/writeConcern, replica sets).

## ACID vs BASE

- ACID (relationnel): transactions fortes, cohérence stricte.
- BASE (souvent NoSQL): Basically Available, Soft state, Eventual consistency.
- En pratique: transactions souvent limitées à une partition/clé/document; cohérence paramétrable selon le moteur et le besoin métier.

## Comment choisir ? (checklist)

- Modèle de données: clés simples, documents hiérarchiques, colonnes à grande échelle, relations denses ?
- Patterns d'accès: lookup par clé, agrégations, time-range scans, traversées de graphes ?
- Exigences non-fonctionnelles: latence, débits, disponibilité, RPO/RTO, multi‑AZ/région
- Cohérence: stricte, quorum, éventuelle ? tolérance aux partitions ?
- Écosystème: outils d'admin/backup/monitoring, offres managées, expertise équipe

## Décision rapide (si → alors)

- Si cache/session/compteur/TTL très rapide → Clé–valeur (Redis)
- Si time series/logs à très gros volume → Colonnes (Cassandra/HBase)
- Si données semi-structurées, agiles → Documents (MongoDB/Couchbase)
- Si relations et parcours profonds → Graphe (Neo4j)

## Bonnes pratiques & pièges

- Modéliser d'après les requêtes dominantes (query-driven design)
- Définir clé de partition adaptée (skew hotkeys → sharding/hashed)
- Indexer ce qui est lu, pas tout; mesurer le coût RAM/disque
- Contrôler la cohérence: niveau de lecture/écriture (quorum, majority, etc.)
- Gérer TTL, compactions, backups, tests de restauration
- Observer: métriques latence, throughput, p95/p99, erreurs; capacity planning

## Vocabulaire utile

- Cohérence éventuelle, quorum, réplication, sharding, compaction, TTL, replica set
- Read/Write Concern (MongoDB), consistency levels (Cassandra)

## 5 points à retenir

1. NoSQL = familles de bases optimisées pour la distribution et des besoins précis.
2. Le modèle (clé-valeur/colonnes/documents/graphe) suit tes requêtes et ton schéma.
3. CAP impose des compromis sous partition; choisis et paramètre en connaissance de cause.
4. ACID global n'est pas gratuit: utilise BASE + patterns (sagas, outbox, idempotence) si besoin.
5. Exemples: Redis (cache), Cassandra/HBase (timeseries), MongoDB (documents), Neo4j (relations).
