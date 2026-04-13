# Trame de présentation — MVP Chatbot RAG Puls-Events
## P13 — Réalisez votre portfolio de Data Engineer

> **Auteur :** Aymeric Bailleul
> **Date cible de soutenance :** 31/07/2026
> **Durée cible :** 20 minutes exposé + 10 minutes questions
> **Format recommandé :** Slides (10–12 slides)
> **Document de référence :** `ABAI_P13_01_rapport_gestion_de_projet.md`

---

## Structure globale

| # | Slide | Durée | Objectif |
|---|-------|-------|---------|
| 1 | Titre & introduction | 1 min | Accrocher, cadrer |
| 2 | Contexte & enjeux | 2 min | Poser le problème métier |
| 3 | Du POC au MVP : les 4 défis | 3 min | Justifier la transition |
| 4 | Architecture technique MVP | 4 min | Démontrer la maîtrise technique |
| 5 | Plan de projet & backlog | 2 min | Montrer la rigueur de gestion |
| 6 | Estimation des coûts | 2 min | Ancrer dans le réel économique |
| 7 | Bilan & choix techniques | 3 min | Prendre du recul, justifier |
| 8 | Conclusion & perspectives | 1 min | Ouvrir, laisser une impression forte |
| 9 | Bilan de formation | 2 min | Montrer la progression sur 13 projets |
| 10 | Q&A + Annexes | 10 min | Répondre aux questions |

---

## Slides détaillées

---

### SLIDE 1 — Titre & introduction

**Titre :** Passage du POC au MVP — Chatbot RAG pour Puls-Events

**Message clé :** En 13 semaines, concevoir une architecture IA conversationnelle scalable, déployable en production, à moins de 50 €/mois.

**Contenu :**
- Nom, rôle, contexte formation (Data Engineer — OpenClassrooms)
- Logo / nom projet : Puls-Events — MVP Chatbot RAG
- Date de soutenance

**Discours oral :**
> "Je vais vous présenter le projet de gestion du P13, qui porte sur la conception du plan de passage d'un POC fonctionnel à un MVP industrialisé pour Puls-Events, une plateforme d'événements culturels. Ce projet illustre une problématique centrale du Data Engineer : comment transformer une preuve de concept en un système réellement déployable, maintenable et économiquement viable ?"

---

### SLIDE 2 — Contexte & enjeux

**Titre :** Puls-Events : de la recherche par mots-clés au chatbot intelligent

**Message clé :** Le POC a prouvé la faisabilité — la question n'est plus "est-ce possible ?" mais "comment le faire passer en production ?"

**Contenu :**
- **La plateforme** : Agrégation d'événements culturels en temps réel (Open Agenda) · Personnalisation par lieu, période, thématiques
- **Le POC réalisé (P11)** :
  - 913 818 événements nationaux → 7 960 filtrés Occitanie → 10 363 chunks FAISS
  - Stack : LangChain / FAISS / `mistral-embed` / `mistral-small-latest` / Streamlit
  - Scores Ragas : faithfulness=**0.764** · answer_relevancy=**0.910** · context_precision=0.700 · context_recall=0.583
  - Validation par les équipes produit & marketing
- **L'objectif P13** : Transformer ce POC en MVP scalable, déployable, maintenable

**Enjeux stratégiques :**
- Positionnement IA concurrentiel dans l'événementiel
- Architecture cloud capable de monter en charge
- Observabilité dès le départ (monitoring qualité & performance)

**Discours oral :**
> "Le POC P11 a démontré qu'un chatbot RAG sur données culturelles fonctionne — les scores Ragas le confirment quantitativement. Mais un POC n'est pas un produit : pas d'historique conversationnel, zone géographique limitée à l'Occitanie, données statiques, et aucun monitoring en production. C'est exactement ce que le MVP doit résoudre."

---

### SLIDE 3 — Du POC au MVP : les 4 défis techniques

**Titre :** 4 limites structurelles à lever pour passer en production

**Message clé :** Chaque défi est documenté, priorisé, et matchée à une solution technique précise.

**Contenu (tableau synthèse) :**

| Défi | Limite du POC | Solution MVP |
|------|--------------|-------------|
| **Mémoire conversationnelle** | Chaque question traitée indépendamment | Redis session store + fenêtre de contexte glissante |
| **Géographie dynamique** | Filtre Occitanie statique au preprocessing | Index Qdrant national + filtre géospatial à la requête |
| **Données temps réel** | Base vectorielle statique (snapshot) | Mistral Agents API `web_search` natif en fallback |
| **Monitoring production** | Évaluation Ragas offline ponctuelle | Langfuse (traces LLM continus) + Cloud Monitoring |

**Exemples de cas d'usage :**
- UC1 : *"Qu'est-ce qu'il y a à faire ce week-end à Lyon ?"* → recherche sémantique + géo
- UC2 : *"Et plutôt pour des enfants ?"* → mémoire conversationnelle
- UC3 : Événement très récent non indexé → `web_search` automatique

**Discours oral :**
> "Ces quatre défis ne sont pas des améliorations cosmétiques — ce sont des prérequis fonctionnels. Sans mémoire, le chatbot est inutilisable dans un contexte conversationnel réel. Sans géolocalisation dynamique, on ne peut pas servir l'ensemble du territoire national. Le diagnostic du POC a permis d'identifier ces blocages avec précision avant de concevoir l'architecture."

---

### SLIDE 4a — Architecture technique MVP : vue globale

**Titre :** Une architecture cloud en 4 couches, serverless et modulaire

**Message clé :** Chaque composant répond à un besoin précis et peut être mis à jour indépendamment.

**Contenu :**
- Schéma d'architecture en 4 couches (insérer image `ABAI_P13_annexe_schema_archi_cloud.png`)
  - Couche **Données** : Open Agenda API + Mistral `web_search`
  - Couche **Traitement IA** : Pipeline ingestion → Qdrant → RAG LangChain + Redis + Filtrage géo
  - Couche **API** : FastAPI + Streamlit
  - Couche **Monitoring** : Langfuse + BigQuery + Cloud Monitoring

- Cloud provider retenu : **GCP** (vs AWS / Azure)

**Points forts de l'architecture :**
- Scale-to-zero sur Cloud Run → coût à l'usage uniquement
- Zéro dépendance externe pour la recherche web (Mistral natif)
- Modularité : LLM, vectorstore, frontend interchangeables sans refonte

**Discours oral :**
> "L'architecture est pensée pour évoluer sans refonte. Chaque service est un conteneur Cloud Run indépendant. Si demain le client veut remplacer Streamlit par React, ou migrer vers un autre LLM — il n'y a pas de couplage fort entre les couches. C'est précisément ce que permet une architecture micro-services correctement découpée."

---

### SLIDE 4b — Architecture technique MVP : choix GCP & composants clés

**Titre :** Pourquoi GCP ? Les choix techniques justifiés

**Message clé :** Le choix du cloud n'est pas arbitraire — il découle directement des contraintes de la stack existante.

**Contenu :**

| Composant | Technologie | Pourquoi ce choix |
|-----------|------------|------------------|
| Cloud provider | **GCP** | Mistral AI sur Vertex AI (continuité POC) · $300 crédits · BigQuery natif |
| Vectorstore | **Qdrant** | Filtre métadonnées GPS/date/ville — impossible avec FAISS |
| LLM | **mistral-small-latest** (Vertex AI) | Continuité POC · coût/performance optimal (temperature=0.0) |
| Mémoire | **Redis** (Cloud Memorystore) | TTL configurable par session · ultra-rapide |
| Recherche web | **Mistral Agents API** `web_search` | Natif, zéro dépendance, citations sources incluses |
| API | **FastAPI** | Asynchrone · documentation OpenAPI auto · légèreté |
| CI/CD | **Cloud Build** + Artifact Registry | Pipeline automatique sur merge `main` |
| Monitoring LLM | **Langfuse** | Self-hostable · traces complètes · scores Ragas continus |

**Discours oral :**
> "Le passage de FAISS à Qdrant est le choix technique le plus structurant. FAISS est une bibliothèque de recherche vectorielle en mémoire — elle ne supporte pas le filtrage par métadonnées. Or, pour filtrer les événements par localisation géographique à la requête, il nous faut un vectorstore qui stocke les coordonnées GPS comme métadonnées interrogeables. Qdrant le fait nativement. Ce n'est pas un choix par mode — c'est une nécessité fonctionnelle."

---

### SLIDE 5 — Plan de projet & backlog

**Titre :** 13 semaines · 6 jalons · 19 fonctionnalités priorisées

**Message clé :** Un plan de projet structuré, ancré dans des jalons mesurables et un backlog priorisé par valeur métier.

**Contenu :**

**Jalons clés :**
| Jalon | Description | Date |
|-------|-------------|------|
| **J1** | Rapport de gestion validé | 07/05/2026 |
| **J2** | Architecture GCP approuvée | 15/05/2026 |
| **J3** | MVP développé & testé | 12/06/2026 |
| **J4** | MVP déployé (staging) | 26/06/2026 |
| **J5** | Recette UAT signée | 17/07/2026 |
| **J6** | Soutenance | 31/07/2026 |

**Backlog :**
- **12 fonctionnalités Must-Have** (~35 jours) — essentielles au MVP fonctionnel
  - Pipeline ingestion national, Qdrant, RAG+mémoire, FiltrGéo, FastAPI, CI/CD, Monitoring…
- **7 fonctionnalités Nice-to-Have** (~25 jours) — valeur ajoutée non bloquante
  - `web_search`, GeoIP, React, BigQuery analytics, Ragas en prod…
- **Total backlog : 19 fonctionnalités · ~60 jours estimés**

*Schéma de modularité (insérer `ABAI_P13_annexe_schema_archi_modules.png`)*

**Discours oral :**
> "La priorisation Must-Have / Nice-to-Have est essentielle dans ce type de projet. Les 12 fonctionnalités must-have forment le MVP strict — sans elles, le produit n'est pas livrable. Les 7 nice-to-have apportent de la valeur, mais ne bloquent pas la livraison. Cette distinction protège le planning des glissements classiques en projet IA, où la tentation d'ajouter des features est permanente."

---

### SLIDE 6 — Estimation des coûts

**Titre :** Coûts maîtrisés : ~50 € de build infra + OPEX scalable

**Message clé :** Un MVP IA conversationnel est financièrement accessible — à condition de choisir une architecture serverless et d'optimiser les appels LLM.

**Contenu :**

**Coûts build :**
| Type | Montant |
|------|---------|
| Coûts humains (valeur-marché indicative) | ~13 450 € |
| Infrastructure GCP (11 semaines dev/staging) | ~50 € |
| Couverts par crédits GCP ($300) | ✅ Intégralement |

**OPEX mensuel — 3 scénarios :**

| Scénario | Utilisateurs/j | OPEX/mois | Coût/utilisateur/mois |
|----------|---------------|-----------|----------------------|
| MVP lancement | 100 | **~50 €** | ~0,017 € |
| Croissance | 1 000 | **~350 €** | ~0,012 € |
| Scale production | 10 000 | **~2 265 €** | ~0,008 € |

> Le coût par utilisateur **décroît** avec la montée en charge (scale-to-zero + mutualisation des coûts fixes)

**5 leviers d'optimisation identifiés :**
- Cache Redis sur questions répétées → -20 à 30 % Mistral API
- Modèle plus léger (`open-mistral-7b`) → -60 % génération
- Ingestion incrémentale → -50 % coûts embedding build
- Qdrant auto-hébergé → -40 % vectorstore
- Langfuse self-hosted (> 50K traces) → -25 €/mois

**Discours oral :**
> "50 euros par mois pour 100 utilisateurs actifs par jour, c'est le coût d'un MVP IA conversationnel bien dimensionné sur GCP. La clé est le scale-to-zero de Cloud Run : si personne n'interroge l'API à 3h du matin, on ne paie pas. C'est fondamentalement différent d'une VM toujours allumée. Et quand on monte à 10 000 utilisateurs, le coût par utilisateur a été divisé par deux — c'est l'effet de mutualisation des coûts fixes."

---

### SLIDE 7 — Bilan & justification des choix

**Titre :** Ce que ce projet démontre au-delà du code

**Message clé :** La valeur du Data Engineer n'est pas seulement technique — c'est la capacité à articuler besoins métier, contraintes techniques et réalité économique.

**Contenu :**

**Ce que le projet a livré :**
- Rapport de gestion complet (analyse, architecture, backlog, coûts, bilan)
- Architecture cloud scalable GCP documentée (schémas + justifications)
- Backlog priorisé : 12 Must-Have + 7 Nice-to-Have, estimés, avec risques et mitigations
- Plan de projet 13 semaines avec jalons mesurables
- Estimation OPEX sur 3 scénarios avec leviers d'optimisation

**Principaux défis rencontrés :**
| Défi | Nature | Solution |
|------|--------|---------|
| Index géographique du POC trop restreint | Technique | FAISS → Qdrant national + filtre runtime |
| Absence de mémoire | Fonctionnel | Redis session store + fenêtre glissante |
| Données obsolètes | Données | Ingestion incrémentale + Mistral `web_search` |
| Monitoring insuffisant | Qualité | Langfuse + Cloud Monitoring |
| Coûts LLM à l'échelle | Économique | Cache Redis + sampling Ragas 10 % |
| Déploiement multi-services | Opérationnel | CI/CD Cloud Build + Secret Manager |

**Discours oral :**
> "Ce projet ne se limite pas à choisir une stack technique. Il illustre une compétence qui distingue le Data Engineer du développeur : savoir prendre en compte simultanément les contraintes métier, les exigences de performance, la gouvernance des données et la réalité économique. Concevoir une architecture à 50 €/mois qui répond à un SLA de 99,5 % avec des métriques de qualité RAG continues — c'est ça, le travail d'ingénierie."

---


### SLIDE 8 — Conclusion & perspectives

**Titre :** Un MVP production-ready pour Puls-Events — et une compétence démontrée

**Message clé :** Le P13 clôt un parcours de 13 projets qui prouve une montée en compétences cohérente et industrielle.

**Contenu :**

**Synthèse du MVP :**
- Architecture GCP Cloud Run · Qdrant · Redis · LangChain · Mistral AI · Langfuse
- Plan de réalisation : 13 semaines · 37 jours · 6 jalons
- OPEX démarrage : ~50 €/mois pour 100 utilisateurs/jour
- Déploiement cible : **31 juillet 2026**

**Perspectives post-MVP (Nice-to-Have en v1) :**
- Interface React (remplacement Streamlit)
- Ragas en production (sampling 10 %)
- BigQuery analytics sur les interactions utilisateurs
- Multi-sources événements (Ticketmaster, Billetréduc…)

**Lien portfolio GitHub :** `github.com/merais/formation`

**Compétences démontrées sur 13 projets :**
Python · SQL · PostgreSQL · MongoDB · Docker · GCP · LangChain · Mistral AI · Kestra · PowerBI

**Discours oral :**
> "Ce projet de gestion est le point de synthèse de 13 mois de formation. Il ne produit pas encore de code — c'est intentionnel. Il produit quelque chose de plus rare : une décision architecturale argumentée, un plan de projet réaliste, et une estimation de coûts honnête. La prochaine étape, c'est l'implémentation — et l'architecture est prête."

---

### SLIDE 9 — Bilan de formation

**Titre :** 13 projets · 13 mois · un parcours Data Engineer complet

**Message clé :** Chaque projet a construit une compétence — ce dernier les synthétise toutes.

**Contenu :**

| Domaine | Projets clés | Compétences acquises |
|---------|-------------|---------------------|
| **Analyse & stats** | P2, P6 | Python · Pandas · Matplotlib · Seaborn |
| **SQL & bases de données** | P3, P5 | PostgreSQL · modélisation · optimisation |
| **NoSQL** | P7 | MongoDB · conception schéma document |
| **Infrastructure & cloud** | P8, P9 | Docker · GCP · architecture cloud |
| **Orchestration** | P10, P12 | Kestra · dbt · pipelines de données |
| **IA & LLM** | P11, P13 | LangChain · RAG · Mistral AI · Langfuse |
| **Visualisation & BI** | P4, P13 | PowerBI · storytelling données |

**Ce que ce parcours démontre :**
- Progression cohérente du SQL au LLM en production
- Capacité à travailler sur toute la chaîne data (collecte → traitement → exposition → monitoring)
- Projets réels sur des problématiques métier concrètes

**Discours oral :**
> "Ces 13 projets ne sont pas des exercices académiques — ce sont 13 réponses à des problèmes réels : comment auditer une base de données, comment orchestrer un pipeline, comment déployer un chatbot IA en production. Ce parcours m'a appris à raisonner en Data Engineer : pas seulement coder une solution, mais choisir la bonne, la documenter, la faire tenir dans un budget et la livrer dans les délais."

---

## Annexes (disponibles pour les questions)

### A1 — Schéma d'architecture complet
`ABAI_P13_annexe_schema_archi_cloud.png`

### A2 — Schéma de modularité
`ABAI_P13_annexe_schema_archi_modules.png`

### A3 — Macro backlog complet (19 fonctionnalités)
→ Voir `ABAI_P13_01_rapport_gestion_de_projet.md` section "Macro backlog"

### A4 — Comparatif cloud providers (AWS / GCP / Azure)
→ Tableau 10 critères dans le rapport

### A5 — Scores Ragas POC (référence)
| Métrique | Score POC |
|----------|-----------|
| faithfulness | 0.764 |
| answer_relevancy | 0.910 |
| context_precision | 0.700 |
| context_recall | 0.583 |
> Évaluation réalisée sur 5 questions de test avec `mistral-large-latest` comme juge · périmètre Occitanie

### A6 — Détail OPEX Scénario 2 (1 000 users/j — ~350 €/mois)

| Service | Coût mensuel |
|---------|-------------|
| Cloud Run (API + RAG) | ~50 € |
| Qdrant | ~60 € |
| Redis (Cloud Memorystore) | ~120 € |
| Mistral AI génération | ~72 € |
| Mistral AI embeddings | ~2 € |
| Cloud Monitoring | ~10 € |
| Langfuse Cloud Pro | ~25 € |
| BigQuery + Scheduler | ~10 € |

---

## Notes de préparation orale

### Points à maîtriser absolument
- [ ] Différence FAISS vs Qdrant (filtrage métadonnées → géolocalisation)
- [ ] Pourquoi Langfuse plutôt que LangSmith ? (self-hostable, coût, maturité 2026)
- [ ] Qu'est-ce que le scale-to-zero et pourquoi c'est décisif pour le budget MVP ?
- [ ] Quel est le vrai coût d'un token Mistral ? (mistral-embed : 0,10 €/M tokens)
- [ ] Comment fonctionne le `web_search` natif de Mistral Agents API ?
- [ ] Quelle est la différence entre le monitoring infra (Cloud Monitoring) et le monitoring LLM (Langfuse) ?

### Questions probables du jury
- *"Pourquoi GCP plutôt qu'AWS, qui est plus répandu en entreprise ?"*
  → Continuité stack Mistral (Vertex AI) · crédits $300 · BigQuery natif ; AWS reste une option valide, ce choix est documenté et justifiable
- *"Comment gérez-vous les risques de coûts Mistral en production ?"*
  → Cache Redis sur prompts fréquents, sampling Ragas à 10 %, possibilité de fallback `open-mistral-7b`
- *"Qdrant self-hosted sur Cloud Run, c'est robuste ?"*
  → Disque persistant GCP, possible migration vers Vertex AI Vector Search si la charge l'exige — architecture prévue pour ça
- *"Le backlog de 60 jours pour 13 semaines, c'est réaliste ?"*
  → Must-Have = 35 j sur S3–S8 (6 semaines) · Must-Have uniquement = livraison J3 garantie · Nice-to-Have en parallèle si avance

### Timing conseillé
| Slide | Temps |
|-------|-------|
| 1 — Titre | 1 min |
| 2 — Contexte | 2 min |
| 3 — 4 défis | 3 min |
| 4a — Architecture vue globale | 2 min |
| 4b — Choix composants | 2 min |
| 5 — Plan & backlog | 2 min |
| 6 — Coûts | 2 min |
| 7 — Bilan | 3 min |
| 8 — Conclusion | 1 min |
| **Total exposé** | **18 min** |
| Q&A | 10 min |
| **Total** | **28 min** |
