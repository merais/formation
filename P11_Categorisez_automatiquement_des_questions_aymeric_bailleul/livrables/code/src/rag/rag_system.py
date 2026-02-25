"""
Système RAG (Retrieval-Augmented Generation) pour la recommandation d'événements.

Ce module implémente un système RAG complet intégrant :
- Recherche vectorielle avec FAISS
- Génération de réponses avec Mistral LLM
- LangChain pour l'orchestration

Le système récupère les événements les plus pertinents depuis la base vectorielle
et génère des recommandations personnalisées basées sur les questions des utilisateurs.

Usage:
    from src.rag.rag_system import RAGSystem
    
    rag = RAGSystem()
    response = rag.query("Quels sont les concerts ce weekend à Toulouse?")
    print(response)

Architecture:
    1. Question utilisateur
    2. Vectorisation de la question (Mistral Embeddings)
    3. Recherche de similarité (FAISS)
    4. Récupération des documents pertinents
    5. Génération de la réponse (Mistral LLM + contexte)
    6. Retour de la réponse avec sources

Auteur: Aymeric Bailleul
Date: 12/02/2026
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
import faiss
from dotenv import load_dotenv

# LangChain imports
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document


# ============================================================================
# CONSTANTES
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Configuration du modèle LLM Mistral
LLM_MODEL = "mistral-small-latest"  # Modèle équilibré performance/coût
LLM_TEMPERATURE = 0.0  # Déterministe pour maximiser la faithfulness (0.3 → 0.1 → 0.0)
LLM_MAX_TOKENS = 1024  # Longueur maximale de la réponse
LLM_TOP_P = 1.0  # top_p=1.0 obligatoire avec temperature=0.0 (greedy sampling)

# Configuration du retriever
RETRIEVER_K = 10  # Nombre de documents à récupérer (5→7→10 : meilleur recall)

# Configuration des embeddings
EMBEDDING_MODEL = "mistral-embed"
EMBEDDING_DIMENSION = 1024


# ============================================================================
# CLASSE PRINCIPALE RAG SYSTEM
# ============================================================================

class RAGSystem:
    """
    Système RAG complet pour la recommandation d'événements culturels.
    
    Ce système combine recherche vectorielle (FAISS) et génération de texte (Mistral LLM)
    pour fournir des recommandations personnalisées basées sur une base d'événements.
    
    Attributes:
        llm: Instance du modèle de langage Mistral
        embeddings: Instance du modèle d'embeddings Mistral
        vectorstore: Base vectorielle FAISS avec les événements
        retriever: Retriever LangChain configuré
        rag_chain: Chaîne RAG complète (retriever + LLM + prompt)
        
    Example:
        >>> rag = RAGSystem()
        >>> response = rag.query("Concerts de jazz à Montpellier")
        >>> print(response["answer"])
        >>> print(response["sources"])
    """
    
    def __init__(
        self,
        llm_model: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
        retriever_k: int = RETRIEVER_K,
        verbose: bool = True
    ):
        """
        Initialise le système RAG avec la configuration spécifiée.
        
        Args:
            llm_model: Nom du modèle LLM Mistral à utiliser
            temperature: Contrôle la créativité (0.0 = déterministe, 1.0 = créatif)
            max_tokens: Nombre maximum de tokens dans la réponse
            retriever_k: Nombre de documents à récupérer
            verbose: Afficher les logs de progression
            
        Raises:
            ValueError: Si la clé API Mistral n'est pas configurée
            FileNotFoundError: Si les fichiers de la base vectorielle sont introuvables
        """
        self.verbose = verbose
        self.retriever_k = retriever_k
        
        if self.verbose:
            print("\n" + "="*80)
            print("INITIALISATION DU SYSTEME RAG".center(80))
            print("="*80 + "\n")
        
        # 1. Charger les variables d'environnement
        self._load_environment()
        
        # 2. Initialiser le modèle LLM Mistral
        self._initialize_llm(llm_model, temperature, max_tokens)
        
        # 3. Initialiser le modèle d'embeddings
        self._initialize_embeddings()
        
        # 4. Charger la base vectorielle FAISS
        self._load_vectorstore()
        
        # 5. Créer le retriever
        self._create_retriever()
        
        # 6. Construire la chaîne RAG
        self._build_rag_chain()
        
        if self.verbose:
            print("\n[SUCCES] Système RAG initialisé avec succès")
            print("="*80 + "\n")
    
    def _load_environment(self) -> None:
        """
        Charge les variables d'environnement depuis le fichier .env.
        
        Raises:
            ValueError: Si MISTRAL_API_KEY n'est pas définie
        """
        if self.verbose:
            print("1. Chargement des variables d'environnement...")
        
        load_dotenv(PROJECT_ROOT / ".env")
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY non trouvée dans .env. "
                "Veuillez configurer votre clé API Mistral."
            )
        
        if self.verbose:
            print(f"   [OK] MISTRAL_API_KEY chargée (longueur: {len(api_key)} caractères)")
    
    def _initialize_llm(
        self,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> None:
        """
        Initialise le modèle de langage Mistral via LangChain.
        
        Args:
            model: Nom du modèle Mistral
            temperature: Paramètre de température
            max_tokens: Nombre maximum de tokens
        """
        if self.verbose:
            print(f"\n2. Initialisation du modèle LLM...")
            print(f"   - Modèle: {model}")
            print(f"   - Temperature: {temperature}")
            print(f"   - Max tokens: {max_tokens}")
        
        # Mistral exige top_p=1.0 en mode greedy (temperature=0.0)
        effective_top_p = 1.0 if temperature == 0.0 else LLM_TOP_P
        self.llm = ChatMistralAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=effective_top_p
        )
        
        if self.verbose:
            print(f"   [OK] LLM Mistral initialisé")
    
    def _initialize_embeddings(self) -> None:
        """
        Initialise le modèle d'embeddings Mistral via LangChain.
        """
        if self.verbose:
            print(f"\n3. Initialisation du modèle d'embeddings...")
            print(f"   - Modèle: {EMBEDDING_MODEL}")
            print(f"   - Dimensions: {EMBEDDING_DIMENSION}")
        
        self.embeddings = MistralAIEmbeddings(
            model=EMBEDDING_MODEL
        )
        
        if self.verbose:
            print(f"   [OK] Embeddings Mistral initialisés")
    
    def _load_vectorstore(self) -> None:
        """
        Charge la base vectorielle FAISS existante avec les métadonnées.
        
        Raises:
            FileNotFoundError: Si les fichiers nécessaires sont introuvables
        """
        if self.verbose:
            print(f"\n4. Chargement de la base vectorielle FAISS...")
        
        # Vérifier l'existence des fichiers
        index_path = VECTORSTORE_DIR / "faiss_index.bin"
        embeddings_path = VECTORSTORE_DIR / "embeddings.npy"
        metadata_path = VECTORSTORE_DIR / "metadata.parquet"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index FAISS introuvable: {index_path}")
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings introuvables: {embeddings_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Métadonnées introuvables: {metadata_path}")
        
        # Charger l'index FAISS
        index = faiss.read_index(str(index_path))
        
        # Charger les métadonnées
        metadata_df = pd.read_parquet(metadata_path)
        
        if self.verbose:
            print(f"   - Index FAISS: {index.ntotal} vecteurs")
            print(f"   - Dimensions: {index.d}D")
            print(f"   - Métadonnées: {len(metadata_df)} entrées")
        
        # Créer des Documents LangChain à partir des métadonnées
        documents = []
        for idx, row in metadata_df.iterrows():
            # Construire le texte pour la recherche (colonne chunk_text dans le parquet)
            text = row.get('chunk_text', '')
            
            # Métadonnées associées
            metadata = {
                'uid': row.get('uid', ''),
                'title_fr': row.get('title_fr', ''),
                'firstdate_begin': row.get('firstdate_begin', ''),
                'location_city': row.get('location_city', ''),
                'location_region': row.get('location_region', ''),
                'chunk_index': row.get('chunk_index', 0)
            }
            
            doc = Document(page_content=text, metadata=metadata)
            documents.append(doc)
        
        # Créer le vectorstore LangChain à partir de l'index existant
        # Note: FAISS.from_documents nécessite des embeddings, on va utiliser une approche différente
        # On va créer un vectorstore vide puis ajouter notre index
        self.vectorstore = FAISS.from_documents(
            documents=documents[:1],  # Initialiser avec 1 doc
            embedding=self.embeddings
        )
        
        # Remplacer l'index par notre index pré-calculé
        self.vectorstore.index = index
        self.vectorstore.docstore._dict = {str(i): doc for i, doc in enumerate(documents)}
        self.vectorstore.index_to_docstore_id = {i: str(i) for i in range(len(documents))}
        
        if self.verbose:
            print(f"   [OK] Base vectorielle chargée: {index.ntotal} documents")
    
    def _create_retriever(self) -> None:
        """
        Crée le retriever LangChain à partir du vectorstore.
        """
        if self.verbose:
            print(f"\n5. Configuration du retriever...")
            print(f"   - Top K documents: {self.retriever_k}")
        
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": self.retriever_k,   # chunks finaux retournés
                "fetch_k": 20,           # candidats pré-sélectionnés avant diversification MMR
                "lambda_mult": 0.7       # 1.0 = full similarity, 0.0 = full diversity
            }
        )
        
        if self.verbose:
            print(f"   [OK] Retriever configuré")
    
    def _build_rag_chain(self) -> None:
        """
        Construit la chaîne RAG complète (Retriever + Prompt + LLM).
        """
        if self.verbose:
            print(f"\n6. Construction de la chaîne RAG...")
        
        # Template du prompt
        # IMPORTANT : "suggère des alternatives proches" a été retiré — il poussait le LLM
        # à sortir du contexte (hallucinations + answer_relevancy = 0 sur questions hors-zone).
        template = """Tu es un assistant spécialisé dans la recommandation d'événements culturels en Occitanie.
            Utilise UNIQUEMENT les informations du CONTEXTE ci-dessous pour répondre.
            INTERDICTION ABSOLUE d'utiliser tes connaissances générales ou d'inventer des informations.

            CONTEXTE (Événements pertinents):
            {context}

            QUESTION:
            {question}

            INSTRUCTIONS STRICTES:
            - Base ta réponse EXCLUSIVEMENT sur les événements du CONTEXTE fourni
            - Mentionne les événements spécifiques avec leurs dates et lieux exacts
            - Si plusieurs événements correspondent, liste-les tous
            - Si aucun événement du contexte ne correspond exactement à la question, réponds UNIQUEMENT :
              "Aucun événement trouvé pour cette recherche dans notre base Puls-Events."
            - N'invente JAMAIS de dates, lieux, prix ou détails absents du contexte
            - N'utilise PAS tes connaissances générales sur des villes, artistes ou événements
            - Ne suggère PAS d'alternatives hors du contexte fourni
            - Cite les informations telles qu'elles apparaissent dans le contexte

            RÉPONSE:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Fonction pour formater les documents
        def format_docs(docs: List[Document]) -> str:
            """Formate les documents récupérés pour le contexte."""
            formatted = []
            for i, doc in enumerate(docs, 1):
                meta = doc.metadata
                formatted.append(
                    f"\nÉvénement {i}:\n"
                    f"Titre: {meta.get('title_fr', 'N/A')}\n"
                    f"Date: {meta.get('firstdate_begin', 'N/A')}\n"
                    f"Lieu: {meta.get('location_city', 'N/A')}, {meta.get('location_region', 'N/A')}\n"
                    f"Description: {doc.page_content[:300]}..."
                )
            return "\n".join(formatted)
        
        # Construire la chaîne RAG
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        if self.verbose:
            print(f"   [OK] Chaîne RAG construite")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Interroge le système RAG avec une question et retourne la réponse.
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant:
                - answer: Réponse générée par le LLM
                - sources: Liste des documents sources utilisés
                - question: Question originale
                
        Example:
            >>> response = rag.query("Concerts à Toulouse ce weekend")
            >>> print(response["answer"])
            >>> for source in response["sources"]:
            >>>     print(f"- {source['title']} ({source['date']})")
        """
        # Récupérer les documents pertinents
        docs = self.retriever.invoke(question)
        
        # Générer la réponse
        answer = self.rag_chain.invoke(question)
        
        # Formater les sources
        sources = []
        for doc in docs:
            sources.append({
                'title': doc.metadata.get('title_fr', 'N/A'),
                'date': doc.metadata.get('firstdate_begin', 'N/A'),
                'location': f"{doc.metadata.get('location_city', '')}, {doc.metadata.get('location_region', '')}",
                'uid': doc.metadata.get('uid', ''),
                'chunk_index': doc.metadata.get('chunk_index', 0)
            })
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources
        }
    
    def query_with_details(self, question: str) -> Dict[str, Any]:
        """
        Version détaillée de query() avec plus d'informations de débogage.
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant la réponse et des informations détaillées
        """
        print(f"\n{'='*80}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}\n")
        
        # Récupérer les documents avec scores
        docs = self.retriever.invoke(question)
        
        print(f"Documents récupérés: {len(docs)}\n")
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            print(f"{i}. {meta.get('title_fr', 'N/A')}")
            print(f"   Date: {meta.get('firstdate_begin', 'N/A')}")
            print(f"   Lieu: {meta.get('location_city', 'N/A')}")
            print(f"   Extrait: {doc.page_content[:150]}...\n")
        
        # Générer la réponse
        print("Génération de la réponse...\n")
        answer = self.rag_chain.invoke(question)
        
        print(f"{'='*80}")
        print("RÉPONSE:")
        print(f"{'='*80}")
        print(answer)
        print(f"{'='*80}\n")
        
        # Sources
        sources = []
        for i, doc in enumerate(docs, 1):
            sources.append({
                'rank': i,
                'content': doc.page_content,
                'metadata': doc.metadata
            })
        
        return {
            'question': question,
            'answer': answer,
            'sources': sources,
            'num_sources': len(sources)
        }


# ============================================================================
# FONCTION PRINCIPALE (POUR TESTS)
# ============================================================================

def main():
    """
    Fonction principale pour tester le système RAG.
    """
    print("\n" + "="*80)
    print("TEST DU SYSTÈME RAG - PULS-EVENTS".center(80))
    print("="*80 + "\n")
    
    # Initialiser le système RAG
    rag = RAGSystem(verbose=True)
    
    # Questions de test
    test_questions = [
        "Quels sont les concerts ce weekend à Toulouse?"
    ]
    
    print("\n" + "="*80)
    print("TESTS DE QUESTIONS".center(80))
    print("="*80 + "\n")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}/{len(test_questions)}")
        print(f"{'─'*80}\n")
        
        response = rag.query_with_details(question)
        
        print(f"\nSources utilisées: {response['num_sources']}")
        for j, source in enumerate(response['sources'], 1):
            print(f"  {j}. {source['title']} - {source['date']} ({source['location']})")
    
    print("\n" + "="*80)
    print("TESTS TERMINÉS".center(80))
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
