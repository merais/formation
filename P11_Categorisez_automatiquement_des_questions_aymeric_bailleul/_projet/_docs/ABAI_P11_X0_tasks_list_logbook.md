# P11 - RAG Chatbot pour Puls-Events - Liste des taches et Logfile

**Projet:** Developpement d'un assistant pour la recommandation d'evenements culturels
**Date de demarrage:** 03/02/2026
**Statut global:** EN COURS

---

## PHASE 0 - INITIALISATION DU PROJET

### 0.1 - Configuration initiale du projet
- [X] Creer la structure de dossiers du projet
  - `/data/` (donnees brutes et traitees)
  - `/data/raw/` (donnees brutes Open Agenda)
  - `/data/processed/` (donnees nettoyees)
  - `/data/vectorstore/` (base FAISS)
  - `/src/` (code source)
  - `/src/preprocessing/` (scripts de pre-traitement)
  - `/src/vectorization/` (scripts de vectorisation)
  - `/src/rag/` (systeme RAG)
  - `/tests/` (tests unitaires)
  - `/analyses/` (exploration et analyses)
  - `/_docs/` (documentation)
- [X] Ajouter au `.gitignore` du dossier parent (_FORMATION_OVER_GIT) les exclusion : .env, data/, vectorstore/, etc
- [X] Creer le fichier `README.md` avec structure de base

**Date de realisation:** 06/02/2026  
**Notes:** 
- Structure complete de dossiers creee
- Ajout au .gitignore parent : vectorstore/, data/, *.faiss, *.pkl, *.pickle
- README.md cree avec architecture complete, instructions d'installation et utilisation

---

## PHASE 1 - ENVIRONNEMENT DE TRAVAIL

### 1.1 - Configuration de l'environnement virtuel
- [X] Creer un environnement virtuel Python (venv avec Poetry)
- [X] Nommer l'environnement (ex: `p11_rag_env`)
- [X] Activer l'environnement virtuel


### 1.2 - Installation des dependances principales dans l'environnement Poetry
**LangChain et ses composants**
  - [X] `poetry run pip install langchain`
  - [X] `poetry run pip install langchain-community`
  - [X] `poetry run pip install langchain-mistralai`
**Faiss (CPU version)**
  - [X] `poetry run pip install faiss-cpu`
**Mistral AI**
  - [X] `poetry run pip install mistralai`
**Manipulation de données**
  - [X] `poetry run pip install pandas`
**Requêtes HTTP**
  - [X] `poetry run pip install requests` (deja installe)
**Gestion des variables d'environnement**
  - [X] `poetry run pip install python-dotenv` (deja installe)
**Tests (en tant que dépendance de développement)**
  - [X] `poetry run pip install pytest`
**Jupyter notebook (en tant que dépendance de développement)**
  - [X] `poetry run pip install notebook` (inclut ipykernel)
**Autres dépendances utiles**
  - [X] `poetry run pip install numpy` (deja installe)
  - [X] `poetry run pip install tiktoken`

**Date de realisation:** 06/02/2026  
**Notes:**
- Toutes les dependances installees avec succes
- faiss-cpu v1.13.2, mistralai v1.12.0, pandas v3.0.0
- pytest v9.0.2, notebook v7.5.3 (inclut jupyterlab v4.5.3)
- tiktoken v0.12.0 pour le comptage de tokens
- Certaines dependances etaient deja presentes (requests, python-dotenv, numpy)


### 1.3 - Gestion des dependances
- [X] Generer `requirements.txt`: `poetry run pip freeze > requirements.txt`
- [X] Mettre a jour `pyproject.toml` avec les dependances
- [X] Tester l'installation sur un environnement propre

**Date de realisation:** 06/02/2026  
**Notes:**
- requirements.txt genere avec toutes les dependances (incluant sous-dependances)
- pyproject.toml mis a jour avec les dependances principales
- Separation des dependances de dev (pytest, notebook) dans optional-dependencies


### 1.4 - Configuration des cles API
- [X] Creer un compte Mistral AI (https://mistral.ai)
- [X] Obtenir la cle API Mistral
- [X] Creer le fichier `.env` avec la cle API

**Date de realisation:** 06/02/2026  
**Notes:**
- Compte Mistral AI cree et cle API obtenue
- Fichier .env configure avec MISTRAL_API_KEY


### 1.5 - Tests de l'environnement
- [X] Creer un script de test `tests/tests_environnement.py`
- [X] Tester l'import de LangChain
- [X] Tester l'import de Faiss
- [X] Tester l'import de Mistral
- [X] Tester l'import de Pandas
- [X] Verifier l'acces a l'API Mistral
- [X] Executer le script de test et verifier que tout fonctionne : `poetry run python tests\tests_environnement.py`

**Date de realisation:** 06/02/2026  
**Notes:**
- Script tests/tests_environnement.py cree avec tests complets
- Tous les imports testes : LangChain 1.2.8, LangChain-Mistralai, Faiss, Mistral SDK, Pandas 3.0.0, NumPy 2.4.2, Tiktoken, Pytest 9.0.2
- API Mistral testee et operationnelle
- Fonctionnalites Faiss testees (creation index, ajout vecteurs, recherche)
- Resultat : ENVIRONNEMENT OPERATIONNEL (8/8 tests reussis)

---

## PHASE 2 - COLLECTE ET PRE-PROCESSING DES DONNEES

### 2.1 - Exploration de l'API Open Agenda
- [ ] Explorer le dataset Open Agenda: https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda
- [ ] Comprendre la structure des donnees disponibles
- [ ] Identifier les champs pertinents (titre, description, date, lieu, etc.)
- [ ] Determiner le perimetre geographique (ville/region)
- [ ] Definir la periode de collecte (moins d'un an)


### 2.2 - Collecte des donnees via API
- [ ] Creer le script `src/preprocessing/fetch_openagenda.py`
- [ ] Implementer la connexion a l'API Open Agenda
- [ ] Implementer les filtres (geographique, temporel)
- [ ] Recuperer les evenements (format JSON)
- [ ] Sauvegarder les donnees brutes dans `data/raw/`
- [ ] Ajouter des docstrings au script


### 2.3 - Nettoyage des donnees
- [ ] Creer le script `src/preprocessing/clean_data.py`
- [ ] Gerer les valeurs manquantes
- [ ] Normaliser les formats de dates
- [ ] Nettoyer les descriptions (HTML, caracteres speciaux)
- [ ] Verifier la coherence des donnees
- [ ] Supprimer les doublons eventuels
- [ ] Ajouter des docstrings au script


### 2.4 - Structuration des donnees
- [ ] Creer un DataFrame Pandas avec les donnees nettoyees
- [ ] Definir le schema de donnees (colonnes necessaires)
- [ ] Sauvegarder les donnees structurees dans `data/processed/events_cleaned.csv`
- [ ] Generer un rapport de statistiques descriptives


### 2.5 - Tests unitaires du pre-processing
- [ ] Creer le fichier `tests/test_preprocessing.py`
- [ ] Test: verifier que tous les evenements sont dans la periode definie
- [ ] Test: verifier que tous les evenements sont dans la region geographique
- [ ] Test: verifier l'absence de valeurs manquantes critiques
- [ ] Test: verifier le format des dates
- [ ] Test: verifier la structure du DataFrame
- [ ] Executer les tests avec pytest


---

## PHASE 3 - VECTORISATION ET BASE DE DONNEES FAISS

### 3.1 - Chunking des textes
- [ ] Creer le script `src/vectorization/chunk_texts.py`
- [ ] Implementer la strategie de decoupage des descriptions
- [ ] Definir la taille des chunks (ex: 500 tokens)
- [ ] Definir le overlap entre chunks (ex: 50 tokens)
- [ ] Conserver les metadonnees (date, lieu, titre) avec chaque chunk
- [ ] Ajouter des docstrings au script


### 3.2 - Vectorisation avec Mistral
- [ ] Creer le script `src/vectorization/vectorize_data.py`
- [ ] Configurer l'acces a l'API Mistral Embeddings
- [ ] Choisir le modele d'embedding Mistral approprie
- [ ] Implementer la vectorisation des chunks
- [ ] Gerer la limitation de l'API (rate limiting)
- [ ] Sauvegarder les vecteurs et metadonnees
- [ ] Ajouter des docstrings au script


### 3.3 - Creation de l'index FAISS
- [ ] Creer le script `src/vectorization/create_faiss_index.py`
- [ ] Choisir le type d'index FAISS (ex: IndexFlatL2, IndexIVFFlat)
- [ ] Creer l'index FAISS
- [ ] Ajouter les vecteurs a l'index
- [ ] Associer les metadonnees aux vecteurs
- [ ] Sauvegarder l'index dans `data/vectorstore/`
- [ ] Ajouter des docstrings au script


### 3.4 - Tests de la base vectorielle
- [ ] Creer le fichier `tests/test_vectorstore.py`
- [ ] Test: verifier que tous les evenements sont indexes
- [ ] Test: tester une recherche de similarite simple
- [ ] Test: verifier la coherence des metadonnees
- [ ] Test: mesurer les temps de recherche
- [ ] Executer les tests avec pytest


### 3.5 - Script de reconstruction de la base
- [ ] Creer un script `rebuild_vectorstore.sh` ou `.py`
- [ ] Orchestrer toutes les etapes (fetch, clean, chunk, vectorize, index)
- [ ] Ajouter des logs pour suivre l'execution
- [ ] Tester la reconstruction complete de la base


---

## PHASE 4 - SYSTEME RAG AVEC LANGCHAIN

### 4.1 - Configuration de LangChain
- [ ] Creer le script `src/rag/rag_system.py`
- [ ] Configurer l'acces a Mistral LLM
- [ ] Choisir le modele LLM Mistral approprie
- [ ] Configurer les parametres du LLM (temperature, max_tokens, etc.)
- [ ] Ajouter des docstrings au script


### 4.2 - Integration de FAISS avec LangChain
- [ ] Creer un VectorStore LangChain a partir de l'index FAISS
- [ ] Implementer un retriever avec top-k documents
- [ ] Tester la recuperation de documents pertinents
- [ ] Ajuster les parametres de recherche (k, score_threshold)


### 4.3 - Creation de la chaine RAG
- [ ] Implementer une chaine de prompt pour le RAG
- [ ] Definir le template de prompt (contexte + question)
- [ ] Integrer le retriever dans la chaine
- [ ] Implementer la generation de reponse avec le LLM
- [ ] Gerer les erreurs et cas limites


### 4.4 - Optimisation du systeme
- [ ] Ajuster le nombre de documents recuperes (top-k)
- [ ] Optimiser le prompt template
- [ ] Implementer une strategie de re-ranking (optionnel)
- [ ] Tester avec differentes questions


### 4.5 - Interface de chat simple
- [ ] Creer un script `src/rag/chat_interface.py`
- [ ] Implementer une boucle de conversation en ligne de commande
- [ ] Afficher les sources (evenements utilises)
- [ ] Ajouter des commandes (exit, help, etc.)
- [ ] Tester l'interface avec plusieurs scenarios


---

## PHASE 5 - EVALUATION DU SYSTEME

### 5.1 - Creation du jeu de donnees test
- [ ] Creer le fichier `data/evaluation/test_questions.json`
- [ ] Rediger 10-20 questions representatives
- [ ] Annoter les reponses attendues pour chaque question
- [ ] Identifier les evenements pertinents pour chaque question
- [ ] Valider la qualite des annotations


### 5.2 - Script d'evaluation
- [ ] Creer le script `src/evaluation/evaluate_rag.py`
- [ ] Implementer l'evaluation automatique sur le jeu test
- [ ] Calculer des metriques (pertinence, coherence)
- [ ] Generer un rapport d'evaluation
- [ ] Identifier les points d'amelioration


### 5.3 - Tests du systeme RAG complet
- [ ] Creer le fichier `tests/test_rag_system.py`
- [ ] Test: verifier la generation de reponses
- [ ] Test: verifier la recuperation de documents pertinents
- [ ] Test: tester des cas limites (questions hors sujet)
- [ ] Test: verifier les temps de reponse
- [ ] Executer les tests avec pytest


---

## PHASE 6 - DOCUMENTATION

### 6.1 - README.md complet
- [ ] Rediger la presentation du projet
- [ ] Decrire les objectifs du POC
- [ ] Documenter l'architecture du systeme
- [ ] Expliquer la structure des dossiers et fichiers
- [ ] Fournir les instructions d'installation
- [ ] Expliquer comment reproduire le projet
- [ ] Ajouter des exemples d'utilisation
- [ ] Documenter les limitations connues


### 6.2 - Documentation technique (Rapport PDF/Word)
- [ ] Creer le document `docs/rapport_technique_P11.pdf`
- [ ] Introduction et contexte du projet
- [ ] Architecture du systeme RAG (schemas)
- [ ] Choix techniques justifies:
  - Pourquoi Faiss?
  - Pourquoi Mistral?
  - Pourquoi LangChain?
- [ ] Description des modeles selectionnes
- [ ] Methodologie de pre-processing
- [ ] Strategie de vectorisation et indexation
- [ ] Resultats du POC (metriques, exemples)
- [ ] Limitations et ameliorations futures
- [ ] Recommandations pour la version finale
- [ ] Conclusion
- [ ] Verifier que le document fait entre 5 et 10 pages


### 6.3 - Documentation du code
- [ ] Verifier que tous les scripts ont des docstrings
- [ ] Ajouter des commentaires pour les parties complexes
- [ ] Documenter les fonctions et classes
- [ ] Generer une documentation API (optionnel: Sphinx)


---

## PHASE 7 - PREPARATION DE LA SOUTENANCE

### 7.1 - Presentation PowerPoint
- [ ] Creer le fichier `docs/presentation_P11.pptx`
- [ ] Slide 1: Page de titre
- [ ] Slide 2-3: Contexte et problematique
- [ ] Slide 4-5: Architecture du systeme RAG
- [ ] Slide 6-7: Choix techniques (Faiss, Mistral, LangChain)
- [ ] Slide 8-9: Methodologie (collecte, pre-processing, vectorisation)
- [ ] Slide 10-11: Resultats du POC (metriques, exemples)
- [ ] Slide 12-13: Demo live et cas d'usage
- [ ] Slide 14: Limitations et ameliorations
- [ ] Slide 15: Conclusion et recommandations
- [ ] Verifier que la presentation fait entre 10 et 15 slides
- [ ] Chronometrer la presentation (15 minutes +/- 5)


### 7.2 - Preparation de la demo live
- [ ] Preparer un script de demo
- [ ] Selectionner 3-5 questions representatives
- [ ] Tester la demo en conditions reelles
- [ ] Preparer un plan B en cas de probleme technique
- [ ] Verifier que l'environnement est pret

### 7.3 - Preparation aux questions de la discussion
- [ ] Preparer la reponse: Comment Faiss optimise les recherches?
- [ ] Preparer la reponse: Limitations de Faiss pour grandes quantites?
- [ ] Preparer la reponse: Pourquoi choisir LangChain?
- [ ] Preparer la reponse: Methodes de garantie de qualite des donnees?
- [ ] Preparer la reponse: Comment detecter les derives de performance?
- [ ] Preparer la reponse: Indicateurs de performance en production?


### 7.4 - Repetition de la soutenance
- [ ] Faire une repetition complete (30 minutes)
- [ ] Chronometrer chaque partie
- [ ] Ajuster si necessaire
- [ ] Solliciter un feedback externe


---

## PHASE 8 - FINALISATION ET DEPOT

### 8.1 - Pipeline de tests complet
- [ ] Executer tous les tests unitaires
- [ ] Corriger les eventuels bugs
- [ ] Verifier que tous les tests passent


### 8.2 - Revue du code
- [ ] Verifier la qualite du code (PEP8 pour Python)
- [ ] Supprimer le code mort
- [ ] Verifier les imports inutilises
- [ ] Optimiser les performances si necessaire


### 8.3 - Verification des livrables
- [ ] Livrable 1: README.md complet
- [ ] Livrable 2: Gestion des dependances (requirements.txt ou pyproject.toml)
- [ ] Livrable 3: Scripts de pre-processing avec docstrings
- [ ] Livrable 4: Scripts de vectorisation avec docstrings
- [ ] Livrable 5: Tests unitaires avec pytest
- [ ] Livrable 6: Code du systeme RAG
- [ ] Livrable 7: Rapport technique (5-10 pages)
- [ ] Livrable 8: Presentation PowerPoint (10-15 slides)


### 8.4 - Preparation du depot
- [ ] Creer le dossier de depot: `Categorisez_automatiquement_des_questions_bailleul_aymeric`
- [ ] Organiser les livrables selon la nomenclature:
  - `bailleul_aymeric_1_readme_022026`
  - `bailleul_aymeric_2_gestion_022026`
  - `bailleul_aymeric_3_scripts_022026`
  - `bailleul_aymeric_4_rapport_technique_022026`
  - `bailleul_aymeric_5_presentation_022026`
- [ ] Creer le fichier ZIP final
- [ ] Verifier la taille du ZIP
- [ ] Tester l'extraction du ZIP


### 8.5 - Depot sur la plateforme
- [ ] Se connecter a la plateforme OpenClassrooms
- [ ] Deposer le fichier ZIP
- [ ] Verifier que le depot est complet
- [ ] Prendre une capture d'ecran de confirmation

---

## ANNEXE - NOTES TECHNIQUES

### Perimetre geographique selectionne:
- Region/Ville:
- Justification:

### Periode de collecte:
- Date debut:
- Date fin:
- Nombre d'evenements collectes:

### Configuration technique:
- Version Python: 3.11.9
- Version LangChain: 1.2.8
- Version LangChain-Mistralai: 1.1.1
- Version Faiss: 1.13.2 (CPU)
- Version Mistral SDK: 1.12.0
- Version Pandas: 3.0.0
- Version NumPy: 2.4.2
- Version Tiktoken: 0.12.0
- Version Pytest: 9.0.2
- Modele Mistral Embeddings: (a definir Phase 3)
- Modele Mistral LLM: mistral-small-latest (teste)
- Type d'index Faiss: (a definir Phase 3)
- Taille des chunks: (a definir Phase 3)
- Overlap entre chunks: (a definir Phase 3)
- Nombre de documents recuperes (k): (a definir Phase 4)