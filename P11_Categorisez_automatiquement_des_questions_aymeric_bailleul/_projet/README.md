# P11 - RAG Chatbot pour Puls-Events

**Projet:** Developpement d'un assistant pour la recommandation d'evenements culturels  
**Auteur:** Aymeric Bailleul  
**Date de début** : 16/02/2026  
**Date de fin maximum** : 10/03/2026

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
│   │   ├── raw/                   # Donnees brutes Open Agenda
│   │   ├── processed/             # Donnees nettoyees et structurees
│   │   └── vectorstore/           # Base de donnees vectorielle FAISS
│   ├── src/                       # Code source
│   │   ├── preprocessing/         # Scripts de collecte et nettoyage
│   │   ├── vectorization/         # Scripts de vectorisation et indexation
│   │   └── rag/                   # Systeme RAG et interface chat
│   ├── tests/                     # Tests unitaires
│   ├── _analyses/                 # Notebooks d'exploration
│   ├── _docs/                     # Documentation du projet
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
- **LangChain 1.2.8** : Framework pour orchestrer le systeme RAG
- **LangChain-Mistralai 1.1.1** : Integration Mistral avec LangChain
- **Mistral AI 1.12.0** : SDK pour modeles de langage et embeddings
- **Faiss 1.13.2** : Base de donnees vectorielle pour la recherche semantique
- **Pandas 3.0.0** : Manipulation et analyse de donnees
- **Pytest 9.0.2** : Tests unitaires
- **Jupyter Notebook 7.5.3** : Environnement de developpement interactif
- **Tiktoken 0.12.0** : Comptage de tokens pour les modeles LLM

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
poetry run python tests/tests_environnement.py
```

---

## Utilisation

### 1. Collecte et pre-processing des donnees

```bash
# Collecter les evenements depuis Open Agenda
python src/preprocessing/fetch_openagenda.py

# Nettoyer les donnees
python src/preprocessing/clean_data.py
```

### 2. Vectorisation et creation de l'index FAISS

```bash
# Decouper les textes en chunks
python src/vectorization/chunk_texts.py

# Vectoriser avec Mistral Embeddings
python src/vectorization/vectorize_data.py

# Creer l'index FAISS
python src/vectorization/create_faiss_index.py
```

### 3. Lancer le chatbot

```bash
python src/rag/chat_interface.py
```

### 4. Executer les tests

```bash
pytest tests/
```

---

## Reconstruction de la base vectorielle

Pour reconstruire completement la base de donnees vectorielle depuis les donnees Open Agenda :

```bash
python rebuild_vectorstore.py
```

Ce script orchestre automatiquement toutes les etapes : collecte, nettoyage, chunking, vectorisation et indexation.

---

## Perimetre du POC

- **Zone geographique** : [A definir]
- **Periode** : Evenements de moins d'un an (historique et a venir)
- **Source de donnees** : Open Agenda (https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda)

---

## Evaluation

Le systeme est evalue sur un jeu de donnees test annote contenant des questions/reponses representatives. Les metriques evaluees incluent :

- Pertinence des documents recuperes
- Qualite et coherence des reponses generees
- Temps de reponse

Les resultats detailles sont disponibles dans le rapport technique.

---

## Limitations connues

- Le POC ne conserve pas l'historique de conversation
- La recherche semantique est limitee au perimetre geographique defini
- Les performances dependent de la qualite des donnees Open Agenda
- La vectorisation peut etre couteuse pour un large volume de donnees

---

## Ameliorations futures

- Implementer un historique de conversation
- Ajouter une interface web (Streamlit, Gradio)
- Optimiser l'index FAISS pour des volumes plus importants
- Implementer du re-ranking pour ameliorer la pertinence
- Deployer le systeme en production (API REST)
- Ajouter des filtres dynamiques (date, type d'evenement, lieu)

---

## Livrables

1. README.md (ce fichier)
2. Gestion des dependances (pyproject.toml, requirements.txt)
3. Scripts de pre-processing avec docstrings
4. Scripts de vectorisation avec docstrings
5. Tests unitaires avec pytest
6. Code du systeme RAG complet
7. Rapport technique (5-10 pages)
8. Presentation PowerPoint (10-15 slides)

---