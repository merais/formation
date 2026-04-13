# P13 — Réalisez votre portfolio de Data Engineer
## Task List & Logbook

> Projet : Puls-Events — Passage du POC au MVP (chatbot RAG sémantique)
> Auteur  : Aymeric Bailleul
> Début   : 2026-04-02

---

## Livrables attendus

| # | Livrable | Fichier cible | Statut |
|---|----------|---------------|--------|
| L1 | Rapport de gestion de projet (template complété) | `ABAI_P13_01_rapport_gestion_de_projet.md` | ✅ Fait |
| L2 | Support de présentation | `ABAI_P13_02_presentation.pptx` | ✅ Fait |
| L3 | Portfolio GitHub (README + liens projets) | GitHub + `ABAI_P13_02_portfolio.md` | ✅ Fait |

---

## Étapes du projet

### PHASE 1 — Cadrage & analyse des besoins

- [x] **1.1** Lire et analyser le contexte complet du projet (mail Jérémy + mission)
- [x] **1.2** Rédiger la section **Introduction** du rapport (contexte, objectif, enjeux)
- [x] **1.3** Rédiger la section **Analyse & synthèse des besoins**
  - [x] 1.3.1 Synthèse du contexte métier et contraintes techniques
  - [x] 1.3.2 Identification des utilisateurs cibles et cas d'usage
  - [x] 1.3.3 Formalisation des 4 défis techniques (mémoire conv., géo, recherche web, monitoring)

---

### PHASE 2 — Architecture technique

- [x] **2.1** Réaliser une **veille cloud providers** (AWS vs GCP vs Azure vs autre) adaptée au cas RAG/NLP
- [x] **2.2** Choisir et justifier le cloud provider retenu → **GCP** (Vertex AI Mistral, Cloud Run serverless, BigQuery)
- [x] **2.3** Concevoir le **schéma d'architecture technique détaillée** du MVP
  - [x] 2.3.1 Infrastructure (VM, conteneurs, orchestration) → Cloud Run serverless
  - [x] 2.3.2 Base de données vectorielle → Qdrant (remplace FAISS POC, filtre métadonnées GPS)
  - [x] 2.3.3 LLM / NLP pipeline (embeddings, RAG, smolagents HF) → mistral-embed + mistral-small + smolagents
  - [x] 2.3.4 API / Backend → FastAPI + Redis sessions
  - [x] 2.3.5 Monitoring & observabilité → Langfuse + Cloud Monitoring + BigQuery
- [x] **2.4** Définir la **stratégie de déploiement** (CI/CD, conteneurisation, modularité)
- [x] **2.5** Rédiger la section **Architecture technique** dans le rapport

---

### PHASE 3 — Plan de projet & backlog

- [x] **3.1** Définir les **jalons** du projet → 5 jalons J1–J5 (07/04 → 10/06/2026)
- [x] **3.2** Construire l'**échéancier** → tableau 10 semaines S1–S10
- [x] **3.3** Lister les **livrables** par jalon → 7 livrables associés J1–J5
- [x] **3.4** Rédiger le **macro backlog** des fonctionnalités
  - [x] 3.4.1 Catégoriser Must-Have / Nice-to-Have → 12 MH + 7 NH
  - [x] 3.4.2 Estimer la complexité (S/M/L/XL) → ~35 j MH, ~25 j NH
  - [x] 3.4.3 Identifier les risques et solutions de mitigation → colonne risque/mitigation
- [x] **3.5** Intégrer plan de projet + backlog dans le rapport

---

### PHASE 4 — Estimation des coûts

- [x] **4.1** Estimer les **coûts build** (développement initial)
  - [x] 4.1.1 Coûts humains → 37 j (~13 450 € valeur-marché)
  - [x] 4.1.2 Coûts infrastructure setup → ~50 € (couverts par crédits GCP $300)
- [x] **4.2** Estimer les **coûts OPEX** (exploitation)
  - [x] 4.2.1 Scénario 1 — MVP 100 users/j → ~50 €/mois
  - [x] 4.2.2 Scénario 2 — Croissance 1 000 users/j → ~350 €/mois
  - [x] 4.2.3 Scénario 3 — Scale 10 000 users/j → ~2 265 €/mois
- [x] **4.3** Proposer des **optimisations budgétaires** → 5 leviers (cache, modèle léger, incrémental, auto-hébergé)
- [x] **4.4** Rédiger la section **Estimation des coûts** dans le rapport

---

### PHASE 5 — Bilan & conclusion

- [x] **5.1** Rédiger la section **Bilan**
  - [x] 5.1.1 Rappel des étapes clés POC → MVP (tableau 4 défis + solutions, jalons, charge)
  - [x] 5.1.2 Justification des choix techniques et méthodologiques (GCP, Qdrant, LangChain, Langfuse)
  - [x] 5.1.3 Défis rencontrés et solutions apportées (tableau 6 lignes)
- [x] **5.2** Rédiger la **conclusion**

---

### PHASE 6 — Portfolio GitHub

- [x] **6.1** Créer / mettre à jour le README du portfolio GitHub → README.md racine enrichi
- [x] **6.2** Documenter les projets P2 à P12 (description, outils, résultats, liens) → 12 fiches projet
- [x] **6.3** Ajouter les compétences démontrées et valeur ajoutée → tableau 10 domaines
- [x] **6.4** Intégrer le lien portfolio dans les annexes du rapport

---

### PHASE 7 — Support de présentation

- [X] **7.1** Définir le plan de la présentation (rappel contexte, points clés, architecture, coûts, bilan)
- [X] **7.2** Créer le support de présentation
- [X] **7.3** Préparer les éléments de discours oral

---

### PHASE 8 — Relecture & finalisation

- [ ] **8.1** Relire et corriger le rapport complet
- [ ] **8.2** Vérifier que tous les points du template sont couverts
- [ ] **8.3** Exporter le rapport en `.docx` / `.pdf` si nécessaire
- [ ] **8.4** Déposer les livrables finaux

---

## Logbook

| Date | Étape | Action réalisée | Notes |
|------|-------|-----------------|-------|
| 2026-04-02 | Init | Création du logbook et de la task list |
| 2026-04-02 | Phase 1 | Rédaction Introduction du rapport (contexte, objectifs, enjeux) |
| 2026-04-02 | Phase 1 | Rédaction Analyse & synthèse des besoins (objectifs métiers, contraintes, utilisateurs, cas d'usage, 4 défis techniques) |
| 2026-04-02 | Phase 1 | Plan de projet — structure posée, jalons & échéanciers à compléter en Phase 3 |
| 2026-04-02 | Phase 2 | Veille cloud providers — comparatif AWS/GCP/Azure, choix GCP justifié (Vertex AI + Cloud Run + BigQuery) |
| 2026-04-02 | Phase 2 | Schéma d'architecture MVP (Mermaid) — 6 couches : Sources → Ingestion → Qdrant → RAG → API → Monitoring |
| 2026-04-02 | Phase 2 | Stratégie déploiement (Cloud Run + CI/CD Cloud Build), modularité (découplage composants), monitoring 3 niveaux (Langfuse + Cloud Monitoring + BigQuery) |
| 2026-04-03 | Phase 3 | Plan de projet — 5 jalons J1–J5 (07/04→10/06/2026), échéancier 10 semaines, 7 livrables |
| 2026-04-03 | Phase 3 | Macro backlog — 12 Must-Have (~35 j) + 7 Nice-to-Have (~25 j), complexité S/M/L/XL, risques & mitigation |
| 2026-04-03 | Phase 4 | Coûts build — 37 j humains (~13 450 € valeur-marché), infra ~50 € (crédits GCP) |
| 2026-04-03 | Phase 4 | OPEX 3 scénarios : MVP ~50 €/mois, croissance ~350 €/mois, scale ~2 265 €/mois. 5 leviers optimisation |
| 2026-04-03 | Phase 5 | Bilan — tableau POC→MVP (4 défis/solutions), justification choix techniques, tableau 6 défis rencontrés |
| 2026-04-03 | Phase 5 | Conclusion — synthèse cadrage, choix, OPEX, positionnement compétences Data Engineer |
| 2026-04-07 | Phase 6 | README portfolio enrichi — tableau compétences (10 domaines) + 12 fiches projet (P2–P13) |
| 2026-04-07 | Phase 6 | Annexes rapport mises à jour avec lien GitHub et tableau récapitulatif projets |
| 2026-04-07 | Phase 6 | Création ABAI_P13_02_portfolio.md — profil, compétences, 12 fiches projet détaillées, matrice compétences |
| 2026-04-08 | Phase 7 | Plan présentation (trame 10 slides) — ABAI_P13_X3_presentation_trame.md |
| 2026-04-08 | Phase 7 | Support PPTX généré (10 slides) — ABAI_P13_02_presentation.pptx |
| 2026-04-08 | Phase 7 | Discours oral préparé — notes par slide + slide 9 bilan de formation ajoutée |

---
