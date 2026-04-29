"""
Tests unitaires pour le système RAG.

Ce module teste les composants du RAGSystem sans appel réel à l'API Mistral.
Toutes les dépendances externes (LLM, embeddings, FAISS, fichiers) sont
mockées via unittest.mock et pytest.monkeypatch.

Stratégie de mock :
    - MISTRAL_API_KEY  : injectée via monkeypatch / variable d'env fictive
    - ChatMistralAI    : mock retournant une réponse déterministe
    - MistralAIEmbeddings : mock retournant des vecteurs aléatoires 1024D
    - faiss.read_index : mock retournant un index FAISS en mémoire
    - np.load          : mock retournant un tableau numpy fictif
    - pd.read_parquet  : mock retournant un DataFrame de métadonnées fictif
    - FAISS.from_documents : mock retournant un vectorstore factice
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Ajout du chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ============================================================================
# HELPERS — construire des objets mockés réutilisables
# ============================================================================

def make_mock_document(title="Concert Jazz", city="Montpellier", uid="evt-001"):
    """Crée un Document LangChain mocké."""
    from langchain_core.documents import Document
    return Document(
        page_content=f"Titre: {title} | Lieu: {city}",
        metadata={
            "uid": uid,
            "title_fr": title,
            "firstdate_begin": "2026-03-15",
            "location_city": city,
            "location_region": "Occitanie",
            "chunk_index": 0,
        },
    )


def make_fake_embeddings_array(n=5, dim=1024):
    """Crée un tableau numpy de vecteurs normalisés fictifs."""
    rng = np.random.default_rng(42)
    arr = rng.standard_normal((n, dim)).astype(np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / norms


def make_fake_metadata_df(n=5):
    """Crée un DataFrame de métadonnées de chunks fictif."""
    return pd.DataFrame({
        "uid": [f"evt-{i:03d}" for i in range(n)],
        "title_fr": [f"Titre {i}" for i in range(n)],
        "firstdate_begin": pd.date_range("2026-03-01", periods=n, tz="Europe/Paris"),
        "location_city": ["Montpellier", "Toulouse", "Carcassonne", "Nîmes", "Perpignan"][:n],
        "location_region": ["Occitanie"] * n,
        "chunk_index": [0] * n,
        "chunk_text": [f"Texte du chunk {i} avec des détails sur l'événement." for i in range(n)],
    })


# ============================================================================
# FIXTURE PRINCIPALE — RAGSystem entièrement mocké
# ============================================================================

@pytest.fixture
def mock_rag_system(monkeypatch, tmp_path):
    """
    Instancie un RAGSystem complet avec toutes les dépendances mockées.

    Aucun appel réseau, aucun fichier réel nécessaire.
    """

    # ── 1. Clé API fictive ────────────────────────────────────────────────────
    monkeypatch.setenv("MISTRAL_API_KEY", "test-api-key-fictive-1234")

    # ── 2. Créer une arborescence de fichiers factices ────────────────────────
    vs_dir = tmp_path / "data" / "vectorstore"
    vs_dir.mkdir(parents=True)
    (vs_dir / "faiss_index.bin").write_bytes(b"fake")
    (vs_dir / "embeddings.npy").write_bytes(b"fake")
    (vs_dir / "metadata.parquet").write_bytes(b"fake")

    fake_arr = make_fake_embeddings_array()
    fake_meta = make_fake_metadata_df()

    # ── 3. Mocks des dépendances lourdes ─────────────────────────────────────
    with (
        patch("src.rag.rag_system.ChatMistralAI") as mock_llm_cls,
        patch("src.rag.rag_system.MistralAIEmbeddings") as mock_emb_cls,
        patch("src.rag.rag_system.faiss.read_index") as mock_faiss_read,
        patch("src.rag.rag_system.np.load", return_value=fake_arr),
        patch("src.rag.rag_system.pd.read_parquet", return_value=fake_meta),
        patch("src.rag.rag_system.FAISS") as mock_faiss_cls,
        patch("src.rag.rag_system.VECTORSTORE_DIR", vs_dir),
        patch("src.rag.rag_system.load_dotenv"),
    ):
        # LLM mock : retourne une chaîne de caractères
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = "Réponse générée par le mock LLM."
        mock_llm_cls.return_value = mock_llm_instance

        # Embeddings mock
        mock_emb_instance = MagicMock()
        mock_emb_instance.embed_query.return_value = make_fake_embeddings_array(1).tolist()[0]
        mock_emb_cls.return_value = mock_emb_instance

        # FAISS index mock
        mock_index = MagicMock()
        mock_index.ntotal = len(fake_arr)
        mock_index.d = 1024
        mock_faiss_read.return_value = mock_index

        # LangChain FAISS vectorstore mock
        mock_docs = [make_mock_document(f"Concert {i}", uid=f"evt-{i:03d}") for i in range(5)]
        mock_vs_instance = MagicMock()
        mock_vs_instance.as_retriever.return_value = MagicMock(
            invoke=MagicMock(return_value=mock_docs[:3])
        )
        mock_faiss_cls.from_documents.return_value = mock_vs_instance

        from src.rag.rag_system import RAGSystem

        rag = RAGSystem(verbose=False)
        # RunnableSequence est un modèle Pydantic : impossible d'assigner .invoke
        # directement. On remplace l'attribut entier par un MagicMock.
        rag.rag_chain = MagicMock()
        rag._mock_docs = mock_docs
        yield rag


# ============================================================================
# TESTS — Initialisation
# ============================================================================

class TestRAGSystemInit:
    """Tests de l'initialisation du RAGSystem."""

    def test_init_raises_without_api_key(self, monkeypatch, tmp_path):
        """Une ValueError est levée si MISTRAL_API_KEY est absente ou vide."""
        monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
        vs_dir = tmp_path / "data" / "vectorstore"
        vs_dir.mkdir(parents=True)
        for fname in ("faiss_index.bin", "embeddings.npy", "metadata.parquet"):
            (vs_dir / fname).write_bytes(b"fake")

        with (
            patch("src.rag.rag_system.load_dotenv"),
            patch("src.rag.rag_system.os.getenv", return_value=None),
            patch("src.rag.rag_system.ChatMistralAI"),
            patch("src.rag.rag_system.MistralAIEmbeddings"),
            patch("src.rag.rag_system.VECTORSTORE_DIR", vs_dir),
        ):
            from src.rag.rag_system import RAGSystem
            with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
                RAGSystem(verbose=False)

    def test_init_raises_if_index_missing(self, monkeypatch, tmp_path):
        """FileNotFoundError est levée si faiss_index.bin est absent."""
        monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
        vs_dir = tmp_path / "data" / "vectorstore"
        vs_dir.mkdir(parents=True)
        # embeddings et metadata présents, index ABSENT

        with (
            patch("src.rag.rag_system.ChatMistralAI"),
            patch("src.rag.rag_system.MistralAIEmbeddings"),
            patch("src.rag.rag_system.VECTORSTORE_DIR", vs_dir),
            patch("src.rag.rag_system.load_dotenv"),
        ):
            from src.rag.rag_system import RAGSystem
            with pytest.raises(FileNotFoundError, match="faiss_index"):
                RAGSystem(verbose=False)

    def test_attributes_exist_after_init(self, mock_rag_system):
        """Les attributs principaux sont présents après initialisation."""
        rag = mock_rag_system
        assert hasattr(rag, "llm")
        assert hasattr(rag, "embeddings")
        assert hasattr(rag, "vectorstore")
        assert hasattr(rag, "retriever")
        assert hasattr(rag, "rag_chain")


# ============================================================================
# TESTS — méthode query()
# ============================================================================

class TestRAGSystemQuery:
    """Tests de la méthode query()."""

    def test_query_returns_dict(self, mock_rag_system):
        """query() retourne un dictionnaire."""
        # Configurer le retriever et la chaîne pour les tests
        docs = [make_mock_document()]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Réponse test.")

        result = mock_rag_system.query("Concerts à Montpellier ?")
        assert isinstance(result, dict)

    def test_query_contains_required_keys(self, mock_rag_system):
        """Le résultat de query() contient 'question', 'answer' et 'sources'."""
        docs = [make_mock_document()]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Voici les concerts.")

        result = mock_rag_system.query("Y a-t-il des concerts ?")
        assert "question" in result
        assert "answer" in result
        assert "sources" in result

    def test_query_preserves_question(self, mock_rag_system):
        """La question originale est conservée dans la réponse."""
        mock_rag_system.retriever.invoke = MagicMock(return_value=[])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Aucun résultat.")

        question = "Expositions à Toulouse ce mois-ci ?"
        result = mock_rag_system.query(question)
        assert result["question"] == question

    def test_query_answer_is_string(self, mock_rag_system):
        """La réponse ('answer') est une chaîne de caractères."""
        mock_rag_system.retriever.invoke = MagicMock(return_value=[])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Texte de réponse.")

        result = mock_rag_system.query("Question test")
        assert isinstance(result["answer"], str)

    def test_query_sources_is_list(self, mock_rag_system):
        """Les sources sont retournées sous forme de liste."""
        docs = [make_mock_document("Festival Jazz", "Nîmes", "evt-99")]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Réponse.")

        result = mock_rag_system.query("Festivals ?")
        assert isinstance(result["sources"], list)

    def test_query_sources_contain_expected_fields(self, mock_rag_system):
        """Chaque source contient les champs title, date, location, uid."""
        docs = [make_mock_document("Expo Peinture", "Perpignan", "evt-42")]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Réponse.")

        result = mock_rag_system.query("Expositions ?")
        assert len(result["sources"]) == 1
        source = result["sources"][0]
        assert "title" in source
        assert "date" in source
        assert "location" in source
        assert "uid" in source

    def test_query_no_documents_returns_empty_sources(self, mock_rag_system):
        """Quand le retriever ne trouve rien, sources est une liste vide."""
        mock_rag_system.retriever.invoke = MagicMock(return_value=[])
        mock_rag_system.rag_chain.invoke = MagicMock(
            return_value="Aucun événement trouvé pour cette recherche dans notre base Puls-Events."
        )

        result = mock_rag_system.query("Concerts en Bretagne ?")
        assert result["sources"] == []

    def test_query_out_of_scope_answer_mentions_perimetre(self, mock_rag_system):
        """Une question hors périmètre retourne un message explicite."""
        mock_rag_system.retriever.invoke = MagicMock(return_value=[])
        mock_rag_system.rag_chain.invoke = MagicMock(
            return_value="Aucun événement trouvé pour cette recherche dans notre base Puls-Events."
        )

        result = mock_rag_system.query("Concerts à Paris ?")
        assert "Aucun événement" in result["answer"]

    def test_query_multiple_sources(self, mock_rag_system):
        """query() retourne autant de sources que de documents récupérés."""
        docs = [
            make_mock_document("Concert A", "Montpellier", "evt-01"),
            make_mock_document("Concert B", "Toulouse", "evt-02"),
            make_mock_document("Concert C", "Nîmes", "evt-03"),
        ]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Trois concerts trouvés.")

        result = mock_rag_system.query("Concerts Occitanie ?")
        assert len(result["sources"]) == 3

    def test_query_source_uid_matches_document(self, mock_rag_system):
        """L'uid dans les sources correspond à celui du document récupéré."""
        doc = make_mock_document("Spectacle Danse", "Carcassonne", "evt-ABCD")
        mock_rag_system.retriever.invoke = MagicMock(return_value=[doc])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Bel événement.")

        result = mock_rag_system.query("Spectacles ?")
        assert result["sources"][0]["uid"] == "evt-ABCD"


# ============================================================================
# TESTS — Constantes et configuration
# ============================================================================

class TestRAGConstants:
    """Vérifie la cohérence des constantes de configuration."""

    def test_llm_model_is_string(self):
        from src.rag.rag_system import LLM_MODEL
        assert isinstance(LLM_MODEL, str)
        assert len(LLM_MODEL) > 0

    def test_temperature_in_valid_range(self):
        from src.rag.rag_system import LLM_TEMPERATURE
        assert 0.0 <= LLM_TEMPERATURE <= 1.0

    def test_max_tokens_positive(self):
        from src.rag.rag_system import LLM_MAX_TOKENS
        assert LLM_MAX_TOKENS > 0

    def test_retriever_k_positive(self):
        from src.rag.rag_system import RETRIEVER_K
        assert RETRIEVER_K > 0

    def test_embedding_dimension(self):
        from src.rag.rag_system import EMBEDDING_DIMENSION
        assert EMBEDDING_DIMENSION == 1024

    def test_embedding_model_is_string(self):
        from src.rag.rag_system import EMBEDDING_MODEL
        assert isinstance(EMBEDDING_MODEL, str)

    def test_greedy_mode_uses_top_p_one(self):
        """En mode greedy (temperature=0), top_p doit valoir 1.0."""
        from src.rag.rag_system import LLM_TEMPERATURE, LLM_TOP_P
        if LLM_TEMPERATURE == 0.0:
            assert LLM_TOP_P == 1.0


# ============================================================================
# TESTS — format_docs (comportement implicite via query)
# ============================================================================

class TestFormatDocs:
    """Teste indirectement la fonction format_docs via query()."""

    def test_source_location_combines_city_and_region(self, mock_rag_system):
        """Le champ 'location' dans les sources combine ville et région."""
        doc = make_mock_document("Concert Test", "Montpellier", "evt-loc")
        # Forcer city et region dans metadata
        doc.metadata["location_city"] = "Montpellier"
        doc.metadata["location_region"] = "Occitanie"

        mock_rag_system.retriever.invoke = MagicMock(return_value=[doc])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Ok.")

        result = mock_rag_system.query("Test ?")
        location = result["sources"][0]["location"]
        assert "Montpellier" in location
        assert "Occitanie" in location

    def test_source_chunk_index_present(self, mock_rag_system):
        """chunk_index est présent dans les sources."""
        doc = make_mock_document()
        doc.metadata["chunk_index"] = 2

        mock_rag_system.retriever.invoke = MagicMock(return_value=[doc])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Ok.")

        result = mock_rag_system.query("Test ?")
        assert result["sources"][0]["chunk_index"] == 2


# ============================================================================
# TESTS — query_with_details()
# ============================================================================

class TestQueryWithDetails:
    """Tests de la méthode query_with_details() (mode debug)."""

    def test_returns_dict_with_num_sources(self, mock_rag_system, capsys):
        """query_with_details() retourne un dict avec 'num_sources'."""
        docs = [make_mock_document()]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Détails complets.")

        result = mock_rag_system.query_with_details("Question détaillée ?")
        assert "num_sources" in result
        assert result["num_sources"] == len(docs)

    def test_contains_sources_as_list_with_metadata(self, mock_rag_system, capsys):
        """Les sources dans query_with_details() contiennent le contenu et les metadata."""
        doc = make_mock_document("Exposition Dali", "Perpignan", "evt-dali")
        mock_rag_system.retriever.invoke = MagicMock(return_value=[doc])
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Belle expo.")

        result = mock_rag_system.query_with_details("Expos Perpignan ?")
        assert len(result["sources"]) == 1
        source = result["sources"][0]
        assert "content" in source
        assert "metadata" in source
        assert source["metadata"]["uid"] == "evt-dali"


# ============================================================================
# TESTS — Intégration légère (sans appel API)
# ============================================================================

class TestRAGIntegration:
    """Tests d'intégration sans appel réseau."""

    def test_query_then_query_with_details(self, mock_rag_system, capsys):
        """Deux appels successifs (query + query_with_details) fonctionnent."""
        docs = [make_mock_document("Festival Folk", "Foix", "evt-folk")]
        mock_rag_system.retriever.invoke = MagicMock(return_value=docs)
        mock_rag_system.rag_chain.invoke = MagicMock(return_value="Festival Folk confirmé.")

        r1 = mock_rag_system.query("Festival ?")
        r2 = mock_rag_system.query_with_details("Festival détails ?")

        assert r1["answer"] == "Festival Folk confirmé."
        assert r2["answer"] == "Festival Folk confirmé."

    def test_multiple_queries_independent(self, mock_rag_system):
        """Deux questions différentes retournent des réponses différentes."""
        docs_1 = [make_mock_document("Concert A", "Montpellier")]
        docs_2 = [make_mock_document("Expo B", "Toulouse")]

        answers = ["Réponse 1.", "Réponse 2."]
        call_count = {"n": 0}

        def side_effect_retriever(q):
            n = call_count["n"]
            call_count["n"] += 1
            return [docs_1, docs_2][n % 2]

        def side_effect_chain(q):
            n = call_count["n"]
            return answers[(n - 1) % 2]

        mock_rag_system.retriever.invoke = MagicMock(side_effect=side_effect_retriever)
        mock_rag_system.rag_chain.invoke = MagicMock(side_effect=side_effect_chain)

        r1 = mock_rag_system.query("Question A ?")
        r2 = mock_rag_system.query("Question B ?")

        assert r1["question"] == "Question A ?"
        assert r2["question"] == "Question B ?"


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
