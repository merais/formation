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
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
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

# Expressions temporelles déclenchant le filtrage par date
TEMPORAL_PATTERNS = re.compile(
    r"\b(en ce moment|actuellement|ce week-?end|cette semaine|ce mois|aujourd'?hui"
    r"|demain|prochainement|bient[ôo]t|ces jours|ce soir|la semaine prochaine"
    r"|mois prochain|en cours)\b",
    re.IGNORECASE,
)

# Mapping mois français → numéro
FR_MONTHS = {
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8, "aout": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12, "decembre": 12,
}
MONTH_PATTERN = re.compile(
    r"\b(" + "|".join(FR_MONTHS.keys()) + r")\b", re.IGNORECASE
)
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")


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
        # Injecter la date du jour pour que le LLM puisse interpréter
        # les requêtes temporelles ("en ce moment", "ce weekend", etc.)
        today = datetime.now().strftime("%d/%m/%Y")

        template = f"""Tu es un assistant spécialisé dans la recommandation d'événements culturels en Occitanie.
            La date du jour est le {today}.
            Utilise UNIQUEMENT les informations du CONTEXTE ci-dessous pour répondre.
            INTERDICTION ABSOLUE d'utiliser tes connaissances générales ou d'inventer des informations.

            CONTEXTE (Événements pertinents):
            {{context}}

            QUESTION:
            {{question}}

            INSTRUCTIONS STRICTES:
            - Base ta réponse EXCLUSIVEMENT sur les événements du CONTEXTE fourni
            - Utilise la date du jour ({today}) pour interpréter les expressions temporelles
              comme "en ce moment", "ce weekend", "prochainement", "cette semaine", etc.
            - Mentionne les événements spécifiques avec leurs dates et lieux exacts
            - Si plusieurs événements correspondent, liste-les tous
            - Si aucun événement du contexte ne correspond exactement à la question, réponds UNIQUEMENT :
              "Aucun événement trouvé pour cette recherche dans notre base Puls-Events."
            - N'invente JAMAIS de dates, lieux, prix ou détails absents du contexte
            - N'utilise PAS tes connaissances générales sur des villes, artistes ou événements
            - Ne suggère PAS d'alternatives hors du contexte fourni
            - Cite les informations telles qu'elles apparaissent dans le contexte

            RÉPONSE:"""
        
        self._prompt = ChatPromptTemplate.from_template(template)
        
        # Construire la chaîne RAG (parcours standard, sans filtrage temporel)
        self.rag_chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self._prompt
            | self.llm
            | StrOutputParser()
        )
        
        if self.verbose:
            print(f"   [OK] Chaîne RAG construite")

    # ────────────────────────────────────────────────────────────────────────
    # HELPERS : formatage des docs et filtrage temporel
    # ────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _format_docs(docs: List[Document]) -> str:
        """Formate les documents récupérés pour le contexte LLM."""
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

    def _is_temporal_query(self, question: str) -> bool:
        """Détecte si la question contient une expression temporelle."""
        return bool(TEMPORAL_PATTERNS.search(question))

    def _compute_temporal_window(self, question: str):
        """
        Calcule la fenêtre temporelle [start, end] à partir de la question.

        Heuristiques :
           - "mois prochain" → [1er du mois suivant, dernier jour du mois suivant]
           - "en ce moment" / "actuellement" / "cette semaine" → [today-7j, today+30j]
           - "ce weekend" → [samedi, dimanche de cette semaine]
           - mois + année explicites ("mars 2026") → [1er-dernier du mois]
           - année seule ("2026") → [1er janv – 31 déc]
        """
        now = datetime.now()
        q = question.lower()

        # Mois + année explicites ("mars 2026")
        m_month = MONTH_PATTERN.search(q)
        m_year = YEAR_PATTERN.search(q)
        if m_month and m_year:
            month_num = FR_MONTHS[m_month.group(1).lower()]
            year_num = int(m_year.group(1))
            start = datetime(year_num, month_num, 1)
            # Dernier jour du mois
            if month_num == 12:
                end = datetime(year_num + 1, 1, 1) - timedelta(days=1)
            else:
                end = datetime(year_num, month_num + 1, 1) - timedelta(days=1)
            return start, end

        # "mois prochain"
        if "mois prochain" in q:
            month = now.month + 1 if now.month < 12 else 1
            year = now.year if now.month < 12 else now.year + 1
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = datetime(year, month + 1, 1) - timedelta(days=1)
            return start, end

        # "ce weekend"
        if re.search(r"ce week-?end", q, re.IGNORECASE):
            days_until_sat = (5 - now.weekday()) % 7
            saturday = now + timedelta(days=days_until_sat)
            sunday = saturday + timedelta(days=1)
            return saturday.replace(hour=0, minute=0), sunday.replace(hour=23, minute=59)

        # "la semaine prochaine"
        if "semaine prochaine" in q:
            days_until_mon = (7 - now.weekday()) % 7 or 7
            monday = now + timedelta(days=days_until_mon)
            sunday = monday + timedelta(days=6)
            return monday.replace(hour=0, minute=0), sunday.replace(hour=23, minute=59)

        # "année seule" ("2026" sans mois)
        if m_year and not m_month:
            year_num = int(m_year.group(1))
            return datetime(year_num, 1, 1), datetime(year_num, 12, 31)

        # Défaut pour expressions vagues ("en ce moment", "actuellement", "prochainement", etc.)
        return now - timedelta(days=7), now + timedelta(days=30)

    def _get_temporal_docs(
        self, question: str, max_docs: int = 10
    ) -> List[Document]:
        """
        Récupère des documents filtrés par date.

        1. Cherche dans le vectorstore un grand nombre de candidats sémantiques
        2. Filtre par date metadata dans la fenêtre temporelle
        3. Retourne au max `max_docs` résultats
        """
        start, end = self._compute_temporal_window(question)

        # Récupérer un large pool sémantique
        all_docs = self.vectorstore.similarity_search(question, k=200)

        # Filtrer par date
        filtered = []
        for doc in all_docs:
            raw_date = doc.metadata.get("firstdate_begin")
            if raw_date is None:
                continue
            try:
                dt = pd.Timestamp(str(raw_date))
                if dt.tz is not None:
                    dt = dt.tz_localize(None)
                if start <= dt.to_pydatetime() <= end:
                    filtered.append(doc)
            except Exception:
                continue

        return filtered[:max_docs]

    def _generate_from_docs(
        self, question: str, docs: List[Document]
    ) -> str:
        """Génère une réponse à partir d'une liste de docs (sans passer par le retriever)."""
        context_str = self._format_docs(docs)
        chain = self._prompt | self.llm | StrOutputParser()
        return chain.invoke({"context": context_str, "question": question})

    # ────────────────────────────────────────────────────────────────────────
    # MÉTHODES PUBLIQUES
    # ────────────────────────────────────────────────────────────────────────

    def query(self, question: str) -> Dict[str, Any]:
        """
        Interroge le système RAG avec une question et retourne la réponse.
        
        Si la question contient une expression temporelle, le système
        récupère un large pool de candidats sémantiques puis filtre par date
        avant d'envoyer au LLM. Sinon, la chaîne RAG standard est utilisée.
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant:
                - answer: Réponse générée par le LLM
                - sources: Liste des documents sources utilisés
                - question: Question originale
        """
        is_temporal = self._is_temporal_query(question)

        if is_temporal:
            # Parcours temporel : récupérer un large pool puis filtrer par date
            docs = self._get_temporal_docs(question, max_docs=self.retriever_k)
            answer = self._generate_from_docs(question, docs)
        else:
            # Parcours standard : chaîne RAG classique
            docs = self.retriever.invoke(question)
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
        Version détaillée de query() avec logs de débogage.
        Utilisée par l'interface Streamlit (chat_interface.py).
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire contenant la réponse et des informations détaillées
        """
        print(f"\n{'='*80}")
        print(f"QUESTION: {question}")
        print(f"{'='*80}\n")
        
        is_temporal = self._is_temporal_query(question)

        if is_temporal:
            start, end = self._compute_temporal_window(question)
            print(f"[TEMPORAL] Requête temporelle détectée")
            print(f"   Fenêtre : {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}\n")
            docs = self._get_temporal_docs(question, max_docs=self.retriever_k)
        else:
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
        if is_temporal:
            answer = self._generate_from_docs(question, docs)
        else:
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
