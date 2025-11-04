# 11 — Cheatsheet Audit qualité des données (OLAP / CA)

Synthèse du rapport d’audit « incohérence du chiffre d’affaires (CA) » sur l’entrepôt OLAP.

## Contexte et objectifs
- Entreprise: SuperSmartMarket (BI/Data Support). Objectif business: hyper‑personnalisation.
- Problème: instabilité du CA historique dans l’OLAP (chiffres changent rétroactivement).
- Objectifs audit: comprendre la source, restaurer la fiabilité, proposer remédiations et plan d’action.

## Constats clés (faits majeurs)
1) Instabilité du CA (symptôme)
- Le CA d’un jour passé varie (ex: 14 août: 275 186,59€ → 284 243,88€ en 2 jours).
- Impact stratégique: reporting et décisions faussés; perte de crédibilité.

2) Cause racine: gestion des dates défaillante
- Saisie/enregistrement de dates incorrectes dans les transactions; modifications rétroactives.
- Perte d’« intégrité temporelle » (impossibilité de figer l’historique).

3) Faiblesse structurelle et gouvernance
- Manque de contraintes (FK, CHECK), documentation absente (dictionnaire, schéma), contrôles a posteriori.
- POC nécessaire pour comprendre la base (symptôme d’absence de gouvernance).

## Risques évalués
- CA incohérent: Impact 5/5, Probabilité 4/5 → risque critique (erreurs stratégiques, budgets faux).
- Dates mal renseignées: Impact 4/5, Probabilité 4/5 → données analytiques non fiables.
- Gouvernance faible (docs/contraintes): Impact 4/5, Probabilité 5/5 → erreurs récurrentes et inertie.

## Écarts vs bonnes pratiques
- Historique non immuable (OLAP) alors qu’il doit l’être.
- Absence d’intégrité structurelle (FK, CHECK), contrôles qualité non automatisés.
- Documentation manquante; processus ETL/ELT laissent passer des dates incohérentes.

## Recommandations principales
1) Immuabilité du CA historique
- Interdire toute écriture sur périodes clôturées (périodes verrouillées et versionnées).
- Tables d’historisation (SCD) et mécanismes append‑only pour transactions.

2) Intégrité des données temporelles
- Contraintes CHECK sur domaines de dates; référentiels jours ouvrés/fermés.
- Procédure stockée / trigger bloquant si date incohérente (ex: jour fermé).
- Normaliser TZ/format; valider en amont (ETL) + à l’insert (DB).

3) Gouvernance et structure
- Ajouter clés primaires/étrangères; clés techniques auto‑incrémentées.
- Créer et maintenir: dictionnaire des données + schéma relationnel.
- Journaliser les mutations (audit logs) et tracer auteur/horodatage/opération.

## Plan d’action (proposé)
- Phase 1 (≤ 3 semaines) — Urgence & stabilité
  - Geler périodes sensibles; mettre CHECK/trigger minimum; journaliser les updates.
  - Corriger dates invalides existantes; activer contrôle ETL en entrée.
- Phase 2 (≤ 3 semaines) — Fondation & pérennité
  - Déployer FK/PK, procédures stockées, référentiels calendaires; SCD pour historiques.
  - Produire dictionnaire et schéma; aligner PowerBI avec vues maîtrisées.
- Phase 3 (≤ 3 semaines) — Gouvernance & maintenance
  - Mettre en place normes/REVIEWS de schéma, runbooks, sauvegardes/restaure tests.
  - Monitoring qualité (règles, seuils, alertes) et revue périodique des logs.

## Contrôles techniques (exemples)
- SQL: CHECK(date BETWEEN min AND max), FK vers calendrier, UNIQUE(period, business_key) sur périodes verrouillées.
- Triggers/procédures: bloquer insert/update si règle violée; remplir colonnes audit (created_at/by, updated_at/by).
- ETL/ELT: validations amont (type, bornes, référentiel), quarantaines, rejets chiffrés, rapport quotidien.
- Historisation: SCD type 2 (valid_from/valid_to, is_current), tables d’événements append‑only.

## Indicateurs de suivi (KPI/qualité)
- Nombre d’updates sur périodes clôturées (doit tendre vers 0).
- % d’enregistrements rejetés pour dates incohérentes (baisse après corrections sources).
- Délai de détection → correction (MTTD/MTTR) des anomalies de dates.
- Couverture documentaire (tables/colonnes décrites; schémas à jour).

## Messages clés
- Le CA historique doit être immuable en OLAP; toute modification rétroactive est une anomalie.
- La fiabilité repose sur des contraintes DB + validations ETL + gouvernance documentaire.
- Priorité: sécurité des dates et traçabilité avant toute optimisation.
