# P11 - RAG Chatbot pour Puls-Events

**Projet:** Developpement d'un assistant pour la recommandation d'evenements culturels  
**Auteur:** Aymeric Bailleul  
**Date de début** : 03/02/2026  
**Date de derniere mise a jour** : 19/02/2026  
**Date de fin maximum** : 10/03/2026  
**Statut:** Phase 5.2 completee - Evaluation Ragas avec MMR (faith=0.764, prec=0.700)  

---

## Presentation du projet

Ce projet consiste en la realisation d'un Proof of Concept (POC) pour un chatbot intelligent base sur un systeme RAG (Retrieval-Augmented Generation). Le chatbot est concu pour recommander des evenements culturels issus de la plateforme Open Agenda, en fonction des preferences des utilisateurs.

### Contexte

L'entreprise Puls-Events souhaite integrer un assistant conversationnel capable de fournir des recommandations personnalisees et augmentees par des reponses precises issues de donnees d'evenements culturels. Ce POC vise a demontrer la faisabilite technique d'une telle solution avant son deploiement a plus grande echelle.

---

## Objectifs

- Implementer un systeme RAG fonctionnel avec LangChain, Mistral AI et Faiss
- Collecter et traiter des donnees d'evenements depuis Open Agenda
- Creer une base de donnees vectorielle pour une recherche semantique efficace
- Fournir des reponses contextuelles et pertinentes aux questions utilisateurs
- Evaluer la qualite et la pertinence des reponses generees

---

## Architecture du systeme

```
┌─────────────────┐
│  Open Agenda    │
│  API (Source)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Pre-processing  │
│ (Nettoyage)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Chunking      │
│  (Decoupage)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Vectorisation  │
│  (Mistral API)  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Index FAISS    │
│ (VectorStore)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  RAG System     │
│  (LangChain)    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Chatbot       │
│  (Interface)    │
└─────────────────┘
```

---

## Structure du projet

```
P11_Categorisez_automatiquement_des_questions_aymeric_bailleul/
├── _projet/
│   ├── data/                      # Donnees du projet
│   │   ├── RAW/                   # Donnees brutes Open Agenda (905 MB, 913K evenements)
│   │   ├── processed/             # Donnees nettoyees (7,960 evenements Occitanie)
│   │   │   ├── evenements_occitanie_clean.parquet (9.32 MB)
│   │   │   └── evenements_chunks.parquet (3.28 MB, 10,646 chunks)
│   │   ├── evaluation/            # Donnees et resultats d'evaluation
│   │   │   └── test_dataset_ragas.json (5 questions annotees, plain text)
│   │   └── vectorstore/           # Base vectorielle FAISS (140.64 MB)
│   │       ├── embeddings.npy      (83.17 MB, 10,646 vecteurs 1024D)
│   │       ├── metadata.parquet    (3.28 MB)
│   │       ├── faiss_index.bin     (41.59 MB, IndexFlatIP)
│   │       ├── config.txt
│   │       └── index_config.txt
│   ├── src/                       # Code source
│   │   ├── preprocessing/         # Scripts de collecte et nettoyage
│   │   │   ├── clean_data.py      
│   │   │   └── chunk_texts.py     
│   │   ├── vectorization/         # Scripts de vectorisation et indexation
│   │   │   ├── vectorize_data.py  (305 lignes)
│   │   │   └── create_faiss_index.py 
│   │   ├── rag/                   # Systeme RAG et interface chat
│   │   │   ├── rag_system.py      # Systeme RAG complet (494 lignes)
│   │   │   └── chat_interface.py  # Interface web Streamlit (309 lignes)
│   │   ├── evaluation/            # Evaluation du systeme RAG
│   │   │   └── evaluate_rag.py    # Script Ragas (4 metriques)
│   │   └── build_vectorstore.py   # Orchestrateur pipeline complet
│   ├── tests/                     # Tests unitaires
│   │   ├── test_00_environnement.py # Tests de configuration (8/8)
│   │   ├── test_01_preprocessing.py  # Tests du preprocessing (22/22)
│   │   └── test_02_vectorstore.py    # Tests base vectorielle (27/27)
│   ├── analyses/                  # Notebooks d'exploration
│   │   └── analyse_dataset.ipynb  # Analyse complete du dataset
│   ├── _docs/                     # Documentation du projet
│   │   └── ABAI_P11_X0_tasks_list_logbook.md
│   ├── README.md                  # Ce fichier
│   ├── pyproject.toml             # Configuration Poetry
│   └── requirements.txt           # Dependances Python
├── _cours/                        # Materiel de cours
└── desktop.ini
```

---

## Technologies utilisees

- **Python 3.11.9** : Langage de programmation principal
- **Poetry** : Gestion des dependances et environnement virtuel
- **LangChain >= 0.3.19** : Framework pour orchestrer le systeme RAG
- **LangChain-Community >= 0.3.19** : Extensions communautaires LangChain
- **LangChain-Mistralai >= 0.2.7** : Integration Mistral avec LangChain
- **LangChain-Ollama >= 1.0.1** : Integration Ollama local avec LangChain (evaluation RAG)
- **Mistral AI >= 1.12.0** : SDK pour modeles de langage et embeddings
- **Ollama** : Serveur d'inference local (mistral:latest) utilise pour l'evaluation Ragas
- **Faiss-cpu >= 1.13.2** : Base de donnees vectorielle pour la recherche semantique
- **Pandas >= 3.0.0** : Manipulation et analyse de donnees
- **NumPy >= 2.4.2** : Calculs numeriques et operations matricielles
- **PyArrow >= 23.0.0** : Lecture/ecriture de fichiers Parquet
- **Streamlit >= 1.54.0** : Framework pour interface web interactive
- **Ragas >= 0.4.3** : Framework d'evaluation des systemes RAG
- **Datasets >= 3.3.0** : Format de dataset Hugging Face (requis par Ragas)
- **Nest-asyncio >= 1.6.0** : Gestion des event loops asyncio imbriquees
- **Pytest >= 9.0.2** : Tests unitaires
- **Jupyter Notebook >= 7.5.3** : Environnement de developpement interactif
- **Tiktoken >= 0.12.0** : Comptage de tokens pour les modeles LLM
- **Python-dotenv >= 1.2.1** : Gestion des variables d'environnement
- **Requests >= 2.32.5** : Requetes HTTP

---

## Installation

### Prerequis

- Python 3.11 ou superieur (Python 3.11.9 recommande)
- Poetry installe sur votre systeme
- Cle API Mistral AI (inscription gratuite sur https://console.mistral.ai)
- Cle API Mistral AI

### Etapes d'installation

1. Cloner le repository (ou extraire l'archive)

```bash
cd P11_Categorisez_automatiquement_des_questions_aymeric_bailleul/_projet
```

2. Creer et activer l'environnement virtuel avec Poetry

```bash
# Installer les dependances depuis pyproject.toml
poetry install

# OU installer depuis requirements.txt
poetry run pip install -r requirements.txt

# Activer l'environnement virtuel (Poetry 2.0+)
# Sur Windows PowerShell:
poetry env activate

# Ou executer des commandes dans l'environnement sans activation:
poetry run python script.py
```

3. Configurer les variables d'environnement

Creer un fichier `.env` a la racine du projet :

```env
MISTRAL_API_KEY=votre_cle_api_mistral
```

4. Verifier l'installation

```bash
# Executer les tests d'environnement
pytest tests/test_00_environnement.py -v
```

---

## Utilisation

### 1. Collecte et pre-processing des donnees

```bash
# Nettoyer les donnees (fichier dans data/RAW deja present)
poetry run python src/preprocessing/clean_data.py

# Le script effectue :
# - Filtrage geographique (Occitanie) et temporel (1 an + futurs)
# - Suppression des colonnes vides
# - Nettoyage du HTML dans les descriptions
# - Creation du champ text_for_rag pour la vectorisation
# - Sauvegarde dans data/processed/evenements_occitanie_clean.parquet
```

### 2. Vectorisation et creation de l'index FAISS

```bash
# Option 1 : Pipeline complet automatique (recommande)
poetry run python src/build_vectorstore.py

# Le script build_vectorstore.py orchestre automatiquement :
# 1. Nettoyage des donnees (clean_data.py)
# 2. Decoupage en chunks (chunk_texts.py)
# 3. Vectorisation Mistral (vectorize_data.py)
# 4. Creation index FAISS (create_faiss_index.py)
# Duree totale : ~4-5 minutes pour 10,646 chunks

# Option 2 : Etapes manuelles
poetry run python src/vectorization/vectorize_data.py     # Vectorisation
poetry run python src/vectorization/create_faiss_index.py # Indexation
```

### 3. Lancer le chatbot Streamlit

```bash
# Lancer l'interface web interactive
poetry run streamlit run src/rag/chat_interface.py

# L'interface s'ouvre automatiquement dans votre navigateur
# URL par defaut: http://localhost:8501

# Fonctionnalites disponibles:
# - Chat interactif avec historique de conversation
# - Affichage des sources d'evenements consultes
# - Sidebar avec statistiques, aide et exemples de questions
# - Bouton "Nouvelle conversation" pour reinitialiser
# - Affichage du temps de reponse
```

### 4. Executer les tests

```bash
# IMPORTANT : Toujours executer depuis le repertoire _projet avec venv active
cd P11_Categorisez_automatiquement_des_questions_aymeric_bailleul/_projet

# Tous les tests
poetry run pytest tests/ -v --disable-warnings

# Tests de l'environnement
poetry run pytest tests/test_00_environnement.py -v

# Tests du preprocessing
poetry run pytest tests/test_01_preprocessing.py -v

# Tests de la base vectorielle
poetry run pytest tests/test_02_vectorstore.py -v
```

---

## Perimetre du POC

- **Zone geographique** : Occitanie (13 departements)
- **Periode** : 1 an en arriere (depuis le 09/02/2025) + tous evenements futurs
- **Volume de donnees** : 
  - Dataset brut : 913,818 evenements
  - Dataset nettoye : 7,960 evenements Occitanie
  - Dataset chunks : 10,646 chunks (250 tokens/chunk, overlap 75 tokens)
  - Base vectorielle : 10,646 embeddings 1024D + index FAISS 
  - Repartition : 7,784 evenements passes + 176 evenements futurs
- **Source de donnees** : Open Agenda (https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda)

---

## Evaluation

Le systeme est evalue avec le framework **Ragas** sur un jeu de 5 questions annotees manuellement (`data/evaluation/test_dataset_ragas.json`).

### Metriques Ragas — Scores finaux

Dataset : `data/evaluation/test_dataset_ragas.json` (5 questions, ground_truths plain text)  
Modele d'evaluation : `mistral-large-latest` (temperature=0.1)  
Embeddings d'evaluation : `mistral-embed`  
Configuration RAG : k=10, MMR (fetch_k=20, lambda=0.7), temperature=0.0, prompt strict  
Prompts Ragas : traduits en francais sauf context_precision (natif anglais)  
Date : 19/02/2026  
Fichier resultats : `data/evaluation/ragas_results_final.json`

| Metrique | Description | Score |
|---|---|---|
| `faithfulness` | La reponse est-elle fidele au contexte ? (anti-hallucination) | **0.764** |
| `answer_relevancy` | La reponse repond-elle a la question ? | **0.910** |
| `context_precision` | Le contexte recupere est-il exempt de bruit ? | **0.700** |
| `context_recall` | Toutes les infos necessaires ont-elles ete recuperees ? | **0.583** |

> Le retriever utilise MMR (Maximal Marginal Relevance) pour diversifier les chunks recuperes et reduire les quasi-doublons issus du meme evenement. Le dataset de test couvre 5 questions representatives de la zone Occitanie : expositions, spectacles enfants, festivals, evenements locaux et plein air.

### Lancer l'evaluation

```bash
# Evaluation complete (17 questions)
poetry run python src/evaluation/evaluate_rag.py

# Evaluation rapide (N questions)
$env:MAX_EVAL_QUESTIONS="3"; poetry run python src/evaluation/evaluate_rag.py

# Regenerer le dataset de test (apres modification du RAG)
poetry run python src/evaluation/generate_test_dataset.py
```

---

## Etat d'avancement

- [FAIT] **Phase 1** : Configuration environnement et API Mistral (8/8 tests PASSED)
- [FAIT] **Phase 2.1-2.2** : Collection et exploration des donnees (notebook complet)
- [FAIT] **Phase 2.3** : Script de nettoyage clean_data.py (9 fonctions documentees)
- [FAIT] **Phase 2.4** : Structuration des donnees (48 colonnes finales)
- [FAIT] **Phase 2.5** : Tests unitaires preprocessing (22/22 tests PASSED)
- [FAIT] **Phase 2.6** : Chunking des textes (10,646 chunks crees, 250 tokens/chunk)
- [FAIT] **Phase 3.1** : Vectorisation avec Mistral Embeddings (10,646 embeddings 1024D, 3.95 min)
- [FAIT] **Phase 3.2** : Creation de l'index FAISS (IndexFlatIP, 41.70 MB, 0.39 sec)
- [FAIT] **Phase 3.3** : Tests vectorisation et FAISS (27/27 tests PASSED)
- [FAIT] **Phase 3.4** : Script de reconstruction complete (build_vectorstore.py, 4m 37s)
- [FAIT] **Phase 4.1-4.3** : Systeme RAG avec LangChain
- [FAIT] **Phase 4.4** : Tests et optimisation du RAG
- [FAIT] **Phase 4.5** : Interface de chat Streamlit
- [FAIT] **Phase 5.1** : Jeu de donnees test Ragas (5 questions ciblees, ground_truths plain text)
- [FAIT] **Phase 5.2** : Script d'evaluation Ragas + optimisation RAG (4 metriques, mistral-large-latest, prompts FR, MMR, scores : faith=0.764, rel=0.910, prec=0.700, recall=0.583)
- [TODO] **Phase 6-8** : Documentation et livrables finaux

---

## Livrables

1. [FAIT] README.md (ce fichier, mise a jour 19/02/2026)
2. [FAIT] Gestion des dependances (pyproject.toml, requirements.txt)
3. [FAIT] Scripts de pre-processing avec docstrings
   - src/preprocessing/clean_data.py
   - src/preprocessing/chunk_texts.py
4. [FAIT] Scripts de vectorisation avec docstrings
   - src/vectorization/vectorize_data.py
   - src/vectorization/create_faiss_index.py
   - src/build_vectorstore.py
5. [FAIT] Tests unitaires avec pytest (57/57 tests PASSED : 8 environnement + 22 preprocessing + 27 vectorstore)
6. [FAIT] Code du systeme RAG complet
   - src/rag/rag_system.py (systeme RAG avec LangChain)
   - src/rag/chat_interface.py (interface web Streamlit)
7. [TODO] Rapport technique (5-10 pages)
8. [TODO] Presentation PowerPoint (10-15 slides)
9. [FAIT] Logbook detaille (ABAI_P11_X0_tasks_list_logbook.md)
10. [FAIT] Notebook d'exploration (analyse_dataset.ipynb - 8 sections)

---