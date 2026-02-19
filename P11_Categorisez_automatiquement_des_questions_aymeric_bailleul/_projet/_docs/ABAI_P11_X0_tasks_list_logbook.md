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
  - [X] `poetry run pip install pyarrow`
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
**Interface**
  - [X] `poetry run pip install streamlit`

**Date de realisation:** 06/02/2026  
**Notes:**
- Toutes les dependances installees avec succes
- faiss-cpu v1.13.2, mistralai v1.12.0, pandas v3.0.0, pyarrow v23.0.0
- pytest v9.0.2, notebook v7.5.3 (inclut jupyterlab v4.5.3)
- tiktoken v0.12.0 pour le comptage de tokens
- pyarrow necessaire pour la lecture de fichiers Parquet
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

---

## PHASE 2 - COLLECTE ET PRE-PROCESSING DES DONNEES

### 2.1- Collecte des donnees
- [X] Dataset complet disponible en format Parquet
- [X] Fichier source : data/raw/evenements-publics-openagenda.parquet

**Date de realisation:** 09/02/2026  
**Notes:**
- Le dataset complet Open Agenda est telecharge (913,818 evenements)


### 2.2 - Exploration et analyse du dataset Open Agenda
- [X] Explorer le dataset Open Agenda: https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda
- [X] Comprendre la structure des donnees disponibles : **913,818 evenements, 56 colonnes, 905.94 MB**
- [X] Identifier les champs pertinents : **title_fr, description_fr, longdescription_fr, firstdate_begin, location_*, etc.**
- [X] Determiner le perimetre geographique : **Occitanie (13 departements)**
- [X] Definir la periode de collecte : **1 an en arriere + tous evenements futurs**
- [X] Analyser la qualite des donnees (completude, doublons, colonnes vides)
- [X] Analyser les textes pour la vectorisation (longueur, HTML)

**Date de realisation:** 09/02/2026  
**Notes:**
- Analyse complete dans analyses/analyse_dataset.ipynb (Sections 1-7)
- Perimetre final retenu : Region Occitanie, 7,983 evenements (7,784 passes + 199 futurs)
- Completude excellente : title_fr 100%, description_fr 99.49%, dates 100%
- 5 colonnes vides identifiees (contributor_*, category)
- Pas de doublons exacts sur UID 


### 2.3 - Nettoyage des donnees
- [x] Creer le script `src/preprocessing/clean_data.py`
- [x] Gerer les valeurs manquantes
- [x] Normaliser les formats de dates
- [x] Nettoyer les descriptions (HTML, caracteres speciaux)
- [x] Verifier la coherence des donnees
- [x] Supprimer les doublons eventuels
- [x] Ajouter des docstrings au script

**Notes:**
- Script complet avec 9 fonctions modulaires et docstrings detaillees
- Fonctions principales: `load_raw_data()`, `filter_by_region_and_time()`, `remove_empty_columns()`, `clean_html()`, `clean_html_descriptions()`, `create_rag_text_field()`, `verify_data_quality()`, `save_cleaned_data()`, `main()`
- Nettoyage HTML avec regex et unescape pour decoder les entites
- Creation d'un champ `text_for_rag` consolidant titre, descriptions, keywords et lieu
- Metriques de qualite calculees et affichees


### 2.4 - Structuration des donnees
- [x] Creer un DataFrame Pandas avec les donnees nettoyees
- [x] Definir le schema de donnees (colonnes necessaires)
- [x] Sauvegarder les donnees structurees dans `data/processed/evenements_occitanie_clean.parquet`
- [x] Generer un rapport de statistiques descriptives

**Notes:**
- Schema final: suppression des colonnes vides (contributor_*, category_id)
- Conservation de 48 colonnes utiles sur 56 initiales
- Ajout du champ `text_for_rag` pour la vectorisation
- Rapport de qualite integre dans la fonction `verify_data_quality()`


### 2.5 - Tests unitaires du pre-processing
- [x] Creer le fichier `tests/test_preprocessing.py`
- [x] Test: verifier que tous les evenements sont dans la periode definie
- [x] Test: verifier que tous les evenements sont dans la region geographique
- [x] Test: verifier l'absence de valeurs manquantes critiques
- [x] Test: verifier le format des dates
- [x] Test: verifier la structure du DataFrame
- [x] Executer les tests avec pytest

**Notes:**
- 22 tests unitaires et d'integration crees
- Fixtures pytest pour donnees de test et donnees nettoyees
- Tests couvrant: filtrage geographique (3 tests), filtrage temporel (2 tests), suppression colonnes vides (2 tests), nettoyage HTML (4 tests), creation text_for_rag (4 tests), verification qualite (4 tests), chargement donnees (2 tests), integration (2 tests)
- Tests sur donnees reelles et donnees synthetiques


### 2.6 - Chunking des textes
- [x] Creer le script `src/preprocessing/chunk_texts.py`
- [x] Implementer la strategie de decoupage du champ text_for_rag
- [x] Definir la taille des chunks
- [x] Definir le overlap entre chunks
- [x] Conserver les metadonnees essentielles avec chaque chunk:
  - uid de l'evenement
  - title_fr
  - firstdate_begin
  - location_city
  - location_region
  - chunk_index (numero du chunk pour l'evenement)
- [x] Sauvegarder les chunks dans `data/processed/evenements_chunks.parquet`
- [x] Ajouter des docstrings au script

**Date de realisation:** 11/02/2026  
**Notes:**
- Parametres optimises: CHUNK_SIZE=250 tokens, CHUNK_OVERLAP=75 tokens (30%)
- Utilisation de tiktoken avec encodage cl100k_base (compatible Mistral)
- Fonctions principales: `load_cleaned_data()`, `count_tokens()`, `split_text_into_chunks()`, `create_chunks_dataframe()`, `verify_chunks_quality()`, `save_chunks()`, `main()`
- Resultats: 7,960 evenements -> 10,646 chunks crees (moyenne 1.34 chunks/evenement)
- Fichier genere: data/processed/evenements_chunks.parquet

---

## PHASE 3 - VECTORISATION ET INDEX FAISS

### 3.1 - Vectorisation avec Mistral
- [x] Creer le script `src/vectorization/vectorize_data.py`
- [x] Charger les chunks depuis `data/processed/evenements_chunks.parquet`
- [x] Configurer l'acces a l'API Mistral Embeddings
- [x] Choisir le modele d'embedding Mistral approprie
- [x] Implementer la vectorisation des chunks
- [x] Gerer la limitation de l'API (rate limiting)
- [x] Sauvegarder les vecteurs et metadonnees associees
- [x] Ajouter des docstrings au script

**Date de realisation:** 11/02/2026  
**Notes:**
- Modele: mistral-embed (1024 dimensions)
- Parametres: batch_size=100 chunks, rate_limit=1.0s entre batches
- Retry logic: 3 tentatives max avec delai 5s
- Fonctions principales: `load_api_key()`, `load_chunks()`, `vectorize_batch()`, `vectorize_chunks()`, `verify_embeddings()`, `save_embeddings()`, `main()`
- Resultats: 10,646 chunks vectorises
- 107 batches traites avec succes
- Qualite: norme moyenne 1.000 (vecteurs normalises), pas de NaN/Inf
- Fichiers generes:
  - data/vectorstore/embeddings.npy
  - data/vectorstore/metadata.parquet
  - data/vectorstore/config.txt


### 3.2 - Creation de l'index FAISS
- [x] Creer le script `src/vectorization/create_faiss_index.py`
- [x] Choisir le type d'index FAISS (ex: IndexFlatIP, IndexFlatL2, IndexIVFFlat)
- [x] Creer l'index FAISS
- [x] Ajouter les vecteurs a l'index
- [x] Associer les metadonnees aux vecteurs
- [x] Sauvegarder l'index dans `data/vectorstore/`
- [x] Ajouter des docstrings au script

**Date de realisation:** 11/02/2026  
**Notes:**
- Type d'index: IndexFlatIP (recherche exacte avec Inner Product)
- Metrique: Inner Product equivalent a cosine similarity pour vecteurs normalises
- Resultats: 10,646 vecteurs indexes avec succes
- Taille de l'index: 41.70 MB
- Test fonctionnel reussi: recherche semantique avec scores de similarite 0.84-1.0
- Fichiers generes:
  - data/vectorstore/faiss_index.bin
  - data/vectorstore/index_config.txt


### 3.3 - Tests de la base vectorielle
- [x] Creer le fichier `tests/test_02_vectorstore.py`
- [x] Test: verifier que tous les evenements sont indexes
- [x] Test: tester une recherche de similarite simple
- [x] Test: verifier la coherence des metadonnees
- [x] Test: mesurer les temps de recherche
- [x] Executer les tests avec pytest

**Date de realisation:** 11/02/2026  
**Notes:**
- Tous les tests passes: 27/27
- Categories de tests: structure (3), qualite embeddings (3), metadonnees (4), index FAISS (3), recherche similarite (4), coherence (4), couverture (2), performance (3), integration (2)
- Tests de qualite: embeddings normalises (norme=1.0), pas de NaN/Inf, dimensions correctes (10646, 1024)
- Tests de recherche: similarite fonctionnelle, scores coherents (0.84-1.0), batch processing valide
- Tests de performance: 0.02ms par requete en batch, < 100ms pour recherche unitaire
- Tests de couverture: 100% des evenements indexes (7,960), 99.98% de completude metadonnees
- Workflow end-to-end valide: chargement, recherche, recuperation metadonnees


### 3.4 - Script de reconstruction de la base
- [x] Creer un script `src/build_vectorstore.py`
- [x] Orchestrer toutes les etapes (clean, chunk, vectorize, index)
- [x] Ajouter des logs pour suivre l'execution
- [x] Tester la reconstruction complete de la base

**Date de realisation:** 11/02/2026  
**Notes:**
- Orchestration de 4 etapes: nettoyage, chunking, vectorisation, indexation
- Verification des prerequis: donnees brutes, .env, scripts, Python
- Logs detailles pour chaque etape avec progression ETA
- Test complet reussi: 4/4 etapes
- Statistiques finales: 7,960 evenements -> 10,646 chunks -> 10,646 embeddings -> index 41.59 MB
- Gestion des erreurs: arret si echec, retry logic API
- Fichiers generes verifies: 140.64 MB total (clean, chunks, embeddings, metadata, index, configs)


---

## PHASE 4 - SYSTEME RAG AVEC LANGCHAIN

### 4.1 - Configuration de LangChain
- [x] Creer le script `src/rag/rag_system.py`
- [x] Configurer l'acces a Mistral LLM
- [x] Choisir le modele LLM Mistral approprie
- [x] Configurer les parametres du LLM (temperature, max_tokens, etc.)
- [x] Ajouter des docstrings au script

**Date de realisation:** 12/02/2026  
**Notes:**
- Modele LLM: mistral-small-latest (equilibre performance/cout)
- Parametres LLM: temperature=0.3 (factuel), max_tokens=1024, top_p=0.9
- Integration complete LangChain: ChatMistralAI, MistralAIEmbeddings
- Architecture modulaire: 9 methodes (_load_environment, _initialize_llm, _initialize_embeddings, _load_vectorstore, _create_retriever, _build_rag_chain, query, query_with_details, main)
- Docstrings detaillees pour chaque methode avec exemples
- Gestion d'erreurs: ValueError pour API key, FileNotFoundError pour fichiers manquants
- Test reussi: systeme initialise en ~5s, reponse generee avec contexte pertinent


### 4.2 - Integration de FAISS avec LangChain
- [x] Creer un VectorStore LangChain a partir de l'index FAISS
- [x] Implementer un retriever avec top-k documents
- [x] Tester la recuperation de documents pertinents
- [x] Ajuster les parametres de recherche (k, score_threshold)

**Date de realisation:** 12/02/2026  
**Notes:**
- VectorStore FAISS LangChain cree a partir de l'index existant (10,646 documents)
- Conversion metadata Parquet -> Documents LangChain avec page_content et metadata
- Retriever configure: search_type="similarity", top_k=5 documents
- Seuil de similarite: 0.7 (ajustable)
- Test fonctionnel: recuperation de 5 documents pertinents pour "concerts Toulouse"
- Documents recuperes contiennent: title_fr, firstdate_begin, location_city, location_region, uid, chunk_index
- Integration transparente avec l'index FAISS pre-calcule (pas de re-vectorisation)


### 4.3 - Creation de la chaine RAG
- [x] Implementer une chaine de prompt pour le RAG
- [x] Definir le template de prompt (contexte + question)
- [x] Integrer le retriever dans la chaine
- [x] Implementer la generation de reponse avec le LLM
- [x] Gerer les erreurs et cas limites

**Date de realisation:** 12/02/2026  
**Notes:**
- Chaine RAG complete implementee dans _build_rag_chain()
- Template de prompt structure: instructions + contexte formate + question utilisateur
- Instructions LLM: reponses claires, mentions dates/lieux, suggestions alternatives, factuel uniquement
- Retriever integre avec fonction format_docs() pour formater le contexte
- Generation via ChatPromptTemplate + LLM + StrOutputParser
- Chaine construite avec operateur pipe LangChain: {context + question} | prompt | llm | parser
- Gestion d'erreurs: ValueError (API key), FileNotFoundError (fichiers vectorstore)
- Test reussi: question "concerts Toulouse" -> reponse coherente avec 2 evenements + dates/lieux
- Format de sortie: dictionnaire {question, answer, sources} avec metadonnees detaillees


### 4.5 - Interface de chat simple
- [x] Creer un script `src/rag/chat_interface.py`
- [x] Implementer une interface web Streamlit
- [x] Afficher les sources (evenements utilises)
- [x] Ajouter des statistiques et aide dans la sidebar
- [x] Tester l'interface avec plusieurs scenarios

**Date de realisation:** 12/02/2026  
**Notes:**
- Interface web avec Streamlit
- Script src/rag/chat_interface.py cree
- Fonctionnalites implementees:
  - Gestion de l'historique de conversation (st.session_state.messages)
  - Affichage des messages en bulles de chat (st.chat_message)
  - Sidebar avec aide, statistiques, exemples de questions
  - Affichage des sources formatees avec metadonnees (titre, date, lieu)
  - Bouton "Nouvelle conversation" pour reinitialiser
  - Cache du systeme RAG avec @st.cache_resource (initialisation unique)
  - Mesure et affichage du temps de reponse
- Configuration: page_title="Chatbot Puls-Events", page_icon="🎭", layout="wide"
- Commande de lancement: poetry run streamlit run src/rag/chat_interface.py
- URL locale: http://localhost:8501


---

## PHASE 5 - EVALUATION DU SYSTEME

### 5.1 - Creation du jeu de donnees test
- [X] Creer le fichier `data/evaluation/test_dataset_ragas.json`
- [X] Selectionner 5 questions representatives et ciblees (Occitanie)
- [X] Generer les reponses (answer) via le pipeline RAG complet
- [X] Recuperer les contextes (contexts) utilises par le retriever FAISS
- [X] Rediger les ground_truth en texte brut (format narratif, sans Markdown)
- [X] Valider le dataset (texte brut uniquement, pas de caracterees speciaux)

**Date de realisation:** 19/02/2026  
**Notes:**
- Format: JSON avec 4 champs par entree (question, answer, contexts, ground_truth)
- 5 questions ciblees Occitanie : expositions Montpellier, spectacles enfants, festivals ete, Carcassonne weekend, evenements plein air
- 10 contextes (chunks FAISS, k=10) par question
- Ground_truth rediges en style narratif court, texte simple, pour coller au style de reponse du modele
- Fichier : data/evaluation/test_dataset_ragas.json


### 5.2 - Script d'evaluation
- [X] Creer le script `src/evaluation/evaluate_rag.py`
- [X] Charger les donnees de test depuis test_dataset_ragas.json
- [X] Formater le dataset pour Ragas avec `datasets.Dataset`
- [X] Initialiser le LLM et les embeddings Mistral via LangChain
- [X] Lancer l'evaluation Ragas avec les 4 metriques
- [X] Afficher les resultats sous forme de DataFrame pandas
- [X] Sauvegarder les resultats dans un fichier JSON date

**Date de realisation:** 19/02/2026  
**Notes:**
- Script structure en 7 fonctions modulaires (conforme cours OC chapitre 4 partie 4)
- Modele d'evaluation : `mistral-large-latest` (temperature=0.1, via Mistral API)
- Embeddings d'evaluation : `mistral-embed` (via Mistral API, MistralAIEmbeddings)
- Import : `langchain_mistralai.ChatMistralAI` et `langchain_mistralai.MistralAIEmbeddings`
- 4 metriques Ragas : faithfulness, answer_relevancy, context_precision, context_recall
- Prompts Ragas traduits en francais via `configure_french_prompts()` :
  - Evite le biais cosinus (questions generees en anglais depuis reponses francaises)
  - Contraintes binaires explicites (REGLE ABSOLUE : 0 ou 1 uniquement) pour reduire les NaN
  - Modifie les attributs `.instruction` sur : statement_generator_prompt, nli_statements_prompt, question_generation, context_precision_prompt, context_recall_prompt
  - context_precision conserve le prompt natif anglais Ragas (parsing plus fiable)
- Retriever optimise : MMR (Maximal Marginal Relevance) active dans `_create_retriever()` :
  - `search_type="mmr"`, `fetch_k=20` (candidats pre-selectionnes), `lambda_mult=0.7` (70% similarite / 30% diversite)
  - Reduit les quasi-doublons de chunks issus du meme evenement
- `answer_relevancy.strictness = 1` pour eviter TypeError dict+=dict avec LangChain
- RunConfig : max_workers=1, timeout=120s, max_retries=3, max_wait=60s
- Variable d'environnement MAX_EVAL_QUESTIONS pour limiter le nombre de questions (tests)
- Scores finaux (5 questions, 19/02/2026, mistral-large-latest) :
  - faithfulness     : 0.764
  - answer_relevancy : 0.910
  - context_precision: 0.700
  - context_recall   : 0.583
- Fichier resultats : data/evaluation/ragas_results_final.json


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
- Region/Ville: Occitanie (13 departements : 09, 11, 12, 30, 31, 32, 34, 46, 48, 65, 66, 81, 82)
- Justification: Region Occitanie retenue comme perimetre geographique representatif pour le POC

### Periode de collecte:
- Date debut: 09/02/2025 (1 an en arriere au moment du telechargement)
- Date fin: evenements futurs sans limite de date
- Nombre d'evenements collectes: 7,983 (7,784 passes + 199 futurs au 09/02/2026, reduit a 7,960 apres nettoyage)

### Configuration technique:
- Version Python: 3.11.9
- Version LangChain: 1.2.8
- Version LangChain-Community: 0.4.1
- Version LangChain-Mistralai: 1.1.1
- Version LangChain-Core: 1.2.12
- Version Faiss: 1.13.2 (CPU)
- Version Mistral SDK: 1.12.0
- Version Pandas: 3.0.1
- Version NumPy: 2.4.2
- Version PyArrow: 23.0.0
- Version Tiktoken: 0.12.0
- Version Pytest: 9.0.2
- Version Streamlit: 1.54.0
- Version Ragas: 0.4.3
- Version Datasets: 4.5.0
- Version Nest-asyncio: 1.6.0
- Modele Mistral Embeddings: mistral-embed (1024 dimensions, production)
- Modele Mistral LLM (production): mistral-small-latest (temperature=0.1)
- Modele LLM (evaluation Ragas): mistral-large-latest (temperature=0.1, via Mistral API)
- Modele Embeddings (evaluation Ragas): mistral-embed (via Mistral API, MistralAIEmbeddings)
- Type d'index Faiss: IndexFlatIP (recherche exacte, Inner Product)
- Taille index Faiss: 41.70 MB pour 10,646 vecteurs
- Temps creation index: 0.39 secondes
- Batch size vectorisation: 100 chunks
- Rate limit vectorisation: 1.0s entre batches
- Temps vectorisation: 3.95 minutes pour 10,646 chunks
- Taille des chunks: 250 tokens
- Overlap entre chunks: 75 tokens (30%)
- Encodage tokens: cl100k_base (compatible Mistral)
- Nombre total de chunks: 10,646
- Moyenne chunks/evenement: 1.34
- Nombre de documents recuperes (k): 10 (RETRIEVER_K dans rag_system.py, augmente de 7 a 10)
- Seuil de similarite: 0.7 (RETRIEVER_SCORE_THRESHOLD dans rag_system.py, defini mais non applique avec MMR)
- Type de recherche : MMR - Maximal Marginal Relevance (fetch_k=20, lambda_mult=0.7)