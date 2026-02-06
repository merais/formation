# Cheatsheet RAG pour LLM - Ultra Condensé

## 📌 Concepts Fondamentaux

### LLM (Large Language Model)
- **Définition** : Modèles entraînés sur d'immenses corpus textuels pour comprendre et générer du langage naturel
- **Fonctionnement** : Transformers + mécanisme d'attention pour prédire le prochain mot (token)
- **Tokens** : Unités de traitement (mots ou fragments) - limités par la fenêtre de contexte
- **Limites** : Hallucinations, connaissances figées à la date d'entraînement, biais

### RAG (Retrieval-Augmented Generation)
- **Principe** : Combiner récupération d'information + génération LLM
- **Workflow** : Question → Recherche sémantique → Contexte + Prompt → LLM → Réponse enrichie
- **Avantages** : Réponses factuelles, pas de fine-tuning coûteux, mise à jour facile de la base de connaissances

## 🔧 Pipeline RAG Complet

### 1. Préparation des Données

**Extraction de contenu**
```python
# PDFs : PyPDF2, pymupdf4llm, markitdown
# Images scannées : EasyOCR, GOT OCR
# Audio/Vidéo : Whisper (transcription)
```

**Cycle de vie des données**
1. **Acquisition** : Collecte de données pertinentes
2. **Stockage** : BD relationnelle, NoSQL ou vectorielle
3. **Traitement** : Nettoyage, conversion, enrichissement
4. **Gouvernance** : RGPD, sécurité, conformité

### 2. Vectorisation & Embeddings

**Modèles d'embedding**
- **Word2Vec/GloVe** : Embeddings statiques (mots isolés)
- **BERT/SBERT** : Embeddings contextuels (phrases/paragraphes)
- **Mistral Embed** : Via API Mistral

**Sélection du modèle**
- Utiliser **MTEB Leaderboard** pour comparer les performances
- Critères : Langue, tâches (retrieval, clustering), domaine, vitesse

```python
# Exemple avec Sentence Transformers
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["texte 1", "texte 2"])
```

### 3. Chunking (Découpage des Documents)

**Stratégies**
- **Récursif avec chevauchement** : Taille fixe (1000 car) + overlap (200 car)
- **Basé sur balises** : HTML/Markdown (préserve structure)
- **Sémantique** : NLP (spaCy) pour segments cohérents

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_text(document)
```

### 4. Base de Données Vectorielle

**Options populaires**
- **FAISS** : Rapide, local, simple (Facebook)
- **Pinecone** : Managé, cloud
- **Weaviate** : Graphes de connaissances
- **Milvus** : Grande échelle

**Création index FAISS**
```python
import faiss
import numpy as np

# Créer index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Recherche
distances, indices = index.search(query_embedding, k=5)
```

### 5. Recherche Sémantique

**Processus**
1. Vectoriser la question utilisateur
2. Rechercher les k chunks les plus similaires (cosine similarity)
3. Récupérer les textes correspondants

```python
def search_similar(question, k=3):
    q_embedding = embed(question)
    distances, indices = index.search(np.array([q_embedding]), k)
    return [chunks[i] for i in indices[0]]
```

## 🎯 Spécialisation du LLM

### 1. Choix du Modèle

**Critères**
- **Sécurité** : RGPD, confidentialité
- **Performance** : Latence, capacité d'analyse
- **Coût** : Token-based vs machine dédiée

**Modèles populaires**
- **Propriétaires** : GPT-4, Gemini, Claude
- **Open Source** : LLaMA, Mistral, Qwen
- **Leaderboards** : Open LLM Leaderboard, Chatbot Arena

**SLM vs LLM**
- **SLM** : Spécialisés, légers, moins de ressources
- **LLM** : Polyvalents, lourds, coûteux

### 2. Prompt Engineering

**Structure du prompt système**
```
Vous êtes l'assistant de [CONTEXTE].

SOURCES AUTORISÉES :
- Documents officiels uniquement
- [Liste des sources]

COMPORTEMENTS OBLIGATOIRES :
- Ton formel et courtois
- Demander précisions si ambigu
- Indiquer si information manquante

COMPORTEMENTS INTERDITS :
- Ne pas inventer d'informations
- Ne pas traiter données personnelles
```

**Paramètres clés**
- **Temperature** : 0.2 (réponses factuelles)
- **Top-p** : 0.9 (filtrage tokens improbables)
- **Max_tokens** : 300 (concision)

**Techniques**
- **Zero-shot** : Sans exemples
- **Few-shot** : Avec exemples
- **Chain of Thought** : Raisonnement étape par étape

### 3. Application avec Streamlit

**Gestion mémoire conversation**
```python
import streamlit as st

# Initialisation historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input utilisateur
if prompt := st.chat_input("Question ?"):
    # Ajouter à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
```

**Construction prompt RAG**
```python
def build_rag_prompt(question, history, max_history=5):
    # Rechercher contextes pertinents
    contexts = search_similar(question, k=3)
    
    # Prompt système avec contextes
    system_prompt = f"""Assistant virtuel.
    Contexte pertinent :
    {chr(10).join(contexts)}
    
    Répondre uniquement basé sur ce contexte."""
    
    # Messages récents
    recent = history[-max_history:]
    
    return [ChatMessage(role="system", content=system_prompt)] + recent
```

## 📊 Évaluation avec RAGAS

### Métriques Clés

**Génération (G)**
- **Faithfulness** : Fidélité au contexte (pas d'hallucination)
- **Answer Relevancy** : Pertinence de la réponse vs question

**Récupération (R)**
- **Context Precision** : Peu de bruit dans les contextes
- **Context Recall** : Tous les éléments nécessaires récupérés
- **Context Relevancy** : Pertinence globale des contextes

### Préparation des données

```python
from datasets import Dataset

evaluation_data = {
    "question": ["Q1", "Q2", ...],
    "answer": ["A1", "A2", ...],          # Générées par RAG
    "contexts": [[ctx1, ctx2], ...],       # Récupérés par RAG
    "ground_truth": ["Réf1", "Réf2", ...]  # Réponses idéales
}

dataset = Dataset.from_dict(evaluation_data)
```

### Exécution

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings

results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=ChatMistralAI(api_key="...", model="mistral-large-latest"),
    embeddings=MistralAIEmbeddings(api_key="...")
)

# Afficher résultats
results_df = results.to_pandas()
print(results_df.mean(numeric_only=True))
```

### Interprétation & Amélioration

| Score Faible | Cause Probable | Amélioration |
|--------------|----------------|--------------|
| **Faithfulness** | Hallucinations LLM | Meilleur prompt, contexte plus propre, T° plus basse |
| **Answer Relevancy** | Réponse hors-sujet | Prompt plus clair, meilleur LLM |
| **Context Precision** | Trop de bruit | Affiner embedding, ajuster chunking, filtrer par seuil |
| **Context Recall** | Info manquantes | Améliorer embedding, augmenter k, chunks plus grands |

## 🔄 Feedback Utilisateur & Amélioration Continue

### Collecte de feedback

```python
# Boutons feedback
col1, col2 = st.columns(2)
with col1:
    if st.button("👍"):
        log_feedback(interaction_id, score=1)
with col2:
    if st.button("👎"):
        log_feedback(interaction_id, score=-1)
```

### Stockage (SQLAlchemy)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    user_query = Column(Text)
    contexts = Column(JSON)
    llm_response = Column(Text)
    feedback_score = Column(Integer, nullable=True)
```

### Tableau de bord

```python
# pages/1_Feedback_Viewer.py
df = pd.read_sql("SELECT * FROM interactions", engine)

# Filtres
filter_option = st.selectbox("Feedback", ["Tous", "Positif", "Négatif"])

# Affichage
st.dataframe(df)
st.metric("Satisfaction", df['feedback_score'].mean())
```

## 🛠️ Stack Technique Recommandée

### Frameworks & Bibliothèques
- **LangChain** / **LlamaIndex** : Orchestration RAG
- **Streamlit** : Interface utilisateur
- **FAISS** : Index vectoriel
- **Sentence Transformers** : Embeddings
- **SQLAlchemy** : Base de données
- **RAGAS** : Évaluation

### APIs & Modèles
- **Mistral AI** : LLM + Embeddings via API
- **Hugging Face** : Modèles open source
- **OpenAI** : Alternative propriétaire

### Déploiement
- **Streamlit Cloud** : Gratuit, simple
- **Docker** : Conteneurisation
- **VM Cloud** : AWS, GCP, Azure

## 📝 Checklist Projet RAG

- [ ] **Données** : Extraction, nettoyage, chunking optimisé
- [ ] **Vectorisation** : Modèle embedding performant sélectionné
- [ ] **Index** : Base vectorielle créée et testée
- [ ] **LLM** : Modèle choisi selon critères (coût, perf, sécurité)
- [ ] **Prompt** : Prompt système robuste avec garde-fous
- [ ] **Interface** : Application Streamlit avec historique
- [ ] **RAG Pipeline** : Recherche + réinjection contexte fonctionnelle
- [ ] **Classification** : Intention (RAG vs CHAT) détectée
- [ ] **Évaluation** : Métriques RAGAS calculées et analysées
- [ ] **Feedback** : Système de collecte implémenté
- [ ] **Monitoring** : Tableau de bord des interactions
- [ ] **Tests** : Tests unitaires des fonctions critiques
- [ ] **Déploiement** : Application déployée et accessible

## 🚀 Optimisations Avancées

### Reranking
- Ajouter un modèle de reranking après recherche initiale
- Réordonne les k résultats par pertinence réelle à la question

### Recherche Hybride
- Combiner recherche vectorielle + recherche par mots-clés (BM25)
- Meilleure couverture des requêtes

### Filtrage par Métadonnées
- Ajouter filtres (date, catégorie, source) avant recherche vectorielle
- Réduit l'espace de recherche

### Seuil de Similarité
```python
def search_with_threshold(query, k=5, max_distance=0.8):
    distances, indices = index.search(query_emb, k)
    # Filtrer par seuil
    valid = [(d, i) for d, i in zip(distances[0], indices[0]) if d <= max_distance]
    return [chunks[i] for d, i in valid]
```

### Agents Multi-outils
- RAG + recherche web + appels API
- Planification et exécution autonome

## 📚 Ressources Clés

- **MTEB Leaderboard** : https://huggingface.co/spaces/mteb/leaderboard
- **RAGAS** : https://docs.ragas.io/
- **LangChain** : https://python.langchain.com/
- **Mistral AI** : https://docs.mistral.ai/
- **FAISS** : https://github.com/facebookresearch/faiss

---

*Cheatsheet créé à partir du cours OpenClassrooms "Mettez en place un RAG pour un LLM"*
