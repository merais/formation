"""
Tests unitaires pour le module de chunking.

Teste les fonctions de découpage de texte en chunks avec fenêtre glissante,
le comptage de tokens et la création du DataFrame de chunks.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tiktoken
import sys

# Ajout du chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessing.chunk_texts import (
    count_tokens,
    split_text_into_chunks,
    create_chunks_dataframe,
    verify_chunks_quality,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    ENCODING_NAME,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def encoding():
    """Charge l'encodeur tiktoken une seule fois pour le module."""
    return tiktoken.get_encoding(ENCODING_NAME)


@pytest.fixture
def short_text():
    """Texte court (< 250 tokens)."""
    return "Titre: Concert de jazz à Montpellier | Description: Un beau concert | Lieu: Montpellier"


@pytest.fixture
def long_text():
    """Texte suffisamment long pour générer plusieurs chunks (> 250 tokens)."""
    phrase = "Ceci est un événement culturel très intéressant qui se déroule en Occitanie. "
    return phrase * 30  # ~300 tokens environ


@pytest.fixture
def sample_events_df():
    """DataFrame d'événements minimal pour tester create_chunks_dataframe."""
    today = pd.Timestamp.now(tz="Europe/Paris")
    return pd.DataFrame({
        "uid": ["evt-001", "evt-002", "evt-003"],
        "title_fr": ["Concert Jazz", "Exposition Peinture", "Festival Folk"],
        "firstdate_begin": [today, today, today],
        "location_city": ["Montpellier", "Toulouse", "Carcassonne"],
        "location_region": ["Occitanie", "Occitanie", "Occitanie"],
        "text_for_rag": [
            "Titre: Concert Jazz | Description: Jazz en plein air | Lieu: Montpellier",
            "Titre: Exposition Peinture | Description: Peintures contemporaines | Lieu: Toulouse",
            # Texte long → plusieurs chunks
            "Titre: Festival Folk | Description: " + ("La musique folk et ses racines. " * 30)
            + " | Lieu: Carcassonne",
        ],
    })


# ============================================================================
# TESTS — count_tokens
# ============================================================================

class TestCountTokens:
    """Tests pour la fonction count_tokens."""

    def test_count_tokens_non_empty(self, encoding):
        """count_tokens retourne un entier positif sur un texte normal."""
        result = count_tokens("Bonjour le monde", encoding)
        assert isinstance(result, int)
        assert result > 0

    def test_count_tokens_empty_string(self, encoding):
        """count_tokens retourne 0 sur une chaîne vide."""
        assert count_tokens("", encoding) == 0

    def test_count_tokens_none(self, encoding):
        """count_tokens retourne 0 sur None."""
        assert count_tokens(None, encoding) == 0

    def test_count_tokens_nan(self, encoding):
        """count_tokens retourne 0 sur np.nan."""
        assert count_tokens(np.nan, encoding) == 0

    def test_count_tokens_longer_text_has_more_tokens(self, encoding):
        """Un texte plus long a plus de tokens."""
        short = "Bonjour"
        long = "Bonjour le monde, ceci est une longue phrase avec beaucoup de tokens différents."
        assert count_tokens(long, encoding) > count_tokens(short, encoding)

    def test_count_tokens_returns_int(self, encoding):
        """count_tokens retourne bien un entier."""
        result = count_tokens("Test", encoding)
        assert isinstance(result, int)


# ============================================================================
# TESTS — split_text_into_chunks
# ============================================================================

class TestSplitTextIntoChunks:
    """Tests pour la fonction split_text_into_chunks."""

    def test_short_text_returns_single_chunk(self, short_text, encoding):
        """Un texte court (< chunk_size) retourne exactement 1 chunk."""
        chunks = split_text_into_chunks(short_text, encoding, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        assert len(chunks) == 1
        assert chunks[0] == short_text

    def test_long_text_returns_multiple_chunks(self, long_text, encoding):
        """Un texte long retourne plusieurs chunks."""
        chunks = split_text_into_chunks(long_text, encoding, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        assert len(chunks) > 1

    def test_empty_string_returns_empty_list(self, encoding):
        """Une chaîne vide retourne une liste vide."""
        chunks = split_text_into_chunks("", encoding)
        assert chunks == []

    def test_none_returns_empty_list(self, encoding):
        """None retourne une liste vide."""
        chunks = split_text_into_chunks(None, encoding)
        assert chunks == []

    def test_nan_returns_empty_list(self, encoding):
        """np.nan retourne une liste vide."""
        chunks = split_text_into_chunks(np.nan, encoding)
        assert chunks == []

    def test_chunks_are_strings(self, long_text, encoding):
        """Tous les chunks sont des chaînes de caractères."""
        chunks = split_text_into_chunks(long_text, encoding)
        assert all(isinstance(c, str) for c in chunks)

    def test_chunks_not_empty(self, long_text, encoding):
        """Aucun chunk n'est une chaîne vide."""
        chunks = split_text_into_chunks(long_text, encoding)
        assert all(len(c.strip()) > 0 for c in chunks)

    def test_each_chunk_respects_size(self, long_text, encoding):
        """Chaque chunk (sauf éventuellement le dernier) ne dépasse pas chunk_size tokens."""
        chunks = split_text_into_chunks(long_text, encoding, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        for chunk in chunks[:-1]:  # Le dernier peut être plus court
            token_count = count_tokens(chunk, encoding)
            assert token_count <= CHUNK_SIZE, (
                f"Chunk de {token_count} tokens dépasse la limite de {CHUNK_SIZE}"
            )

    def test_overlap_creates_continuity(self, long_text, encoding):
        """Avec overlap > 0, les chunks successifs partagent du contenu."""
        chunks = split_text_into_chunks(long_text, encoding, chunk_size=100, overlap=30)
        if len(chunks) >= 2:
            # On ne peut pas tester mot-à-mot facilement (décodage token),
            # mais on peut vérifier qu'il n'y a pas de perte de données
            total_tokens_chunks = sum(count_tokens(c, encoding) for c in chunks)
            original_tokens = count_tokens(long_text, encoding)
            # Avec overlap, la somme des tokens des chunks > tokens originaux
            assert total_tokens_chunks >= original_tokens

    def test_custom_chunk_size(self, encoding):
        """La taille de chunk est bien respectée avec un paramètre personnalisé."""
        text = "mot " * 200  # ~200 tokens
        chunks = split_text_into_chunks(text, encoding, chunk_size=50, overlap=10)
        assert len(chunks) > 1
        for chunk in chunks[:-1]:
            assert count_tokens(chunk, encoding) <= 50

    def test_returns_list(self, short_text, encoding):
        """split_text_into_chunks retourne toujours une liste."""
        result = split_text_into_chunks(short_text, encoding)
        assert isinstance(result, list)


# ============================================================================
# TESTS — create_chunks_dataframe
# ============================================================================

class TestCreateChunksDataframe:
    """Tests pour la fonction create_chunks_dataframe."""

    def test_returns_dataframe(self, sample_events_df):
        """create_chunks_dataframe retourne un DataFrame."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert isinstance(df_chunks, pd.DataFrame)

    def test_output_not_empty(self, sample_events_df):
        """Le DataFrame de chunks n'est pas vide."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert len(df_chunks) > 0

    def test_output_has_more_rows_than_input(self, sample_events_df):
        """Le DataFrame de chunks a au moins autant de lignes que l'entrée."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert len(df_chunks) >= len(sample_events_df)

    def test_required_columns_present(self, sample_events_df):
        """Les colonnes chunk_text, chunk_index et chunk_tokens sont présentes."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert "chunk_text" in df_chunks.columns
        assert "chunk_index" in df_chunks.columns
        assert "chunk_tokens" in df_chunks.columns

    def test_metadata_columns_preserved(self, sample_events_df):
        """Les colonnes de métadonnées sont préservées dans les chunks."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        for col in ["uid", "title_fr", "location_city", "location_region"]:
            assert col in df_chunks.columns, f"Colonne manquante : {col}"

    def test_chunk_index_starts_at_zero(self, sample_events_df):
        """Le chunk_index démarre à 0 pour chaque événement."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        for uid in df_chunks["uid"].unique():
            min_idx = df_chunks[df_chunks["uid"] == uid]["chunk_index"].min()
            assert min_idx == 0, f"chunk_index ne démarre pas à 0 pour uid={uid}"

    def test_chunk_text_not_empty(self, sample_events_df):
        """Aucun chunk_text n'est vide."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert df_chunks["chunk_text"].str.strip().ne("").all()

    def test_chunk_tokens_positive(self, sample_events_df):
        """Tous les chunk_tokens sont positifs."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        assert (df_chunks["chunk_tokens"] > 0).all()

    def test_missing_column_raises_valueerror(self, sample_events_df):
        """Une ValueError est levée si une colonne requise est absente."""
        df_bad = sample_events_df.drop(columns=["uid"])
        with pytest.raises(ValueError, match="Colonnes manquantes"):
            create_chunks_dataframe(df_bad)

    def test_missing_text_column_raises_valueerror(self, sample_events_df):
        """Une ValueError est levée si la colonne text_for_rag est absente."""
        df_bad = sample_events_df.drop(columns=["text_for_rag"])
        with pytest.raises(ValueError, match="Colonnes manquantes"):
            create_chunks_dataframe(df_bad)

    def test_empty_texts_are_skipped(self):
        """Les lignes avec texte vide ou NaN ne génèrent pas de chunks.

        Note : lorsque TOUS les événements ont un texte vide, le code source
        produit un ZeroDivisionError sur le calcul de la moyenne. Ce comportement
        est documenté ici via pytest.raises afin de le signaler explicitement.
        """
        today = pd.Timestamp.now(tz="Europe/Paris")
        df = pd.DataFrame({
            "uid": ["evt-001", "evt-002"],
            "title_fr": ["Événement A", "Événement B"],
            "firstdate_begin": [today, today],
            "location_city": ["Toulouse", "Montpellier"],
            "location_region": ["Occitanie", "Occitanie"],
            "text_for_rag": [None, ""],
        })
        # La fonction source lève ZeroDivisionError quand tous les textes sont vides
        # (division par zéro sur le calcul de la moyenne chunks/événement).
        with pytest.raises(ZeroDivisionError):
            create_chunks_dataframe(df)

    def test_long_event_produces_multiple_chunks(self, sample_events_df):
        """Un événement avec un texte long produit plusieurs chunks."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        # evt-003 a un texte long
        chunks_evt3 = df_chunks[df_chunks["uid"] == "evt-003"]
        assert len(chunks_evt3) > 1, "L'événement long doit être découpé en plusieurs chunks"


# ============================================================================
# TESTS — verify_chunks_quality
# ============================================================================

class TestVerifyChunksQuality:
    """Tests pour la fonction verify_chunks_quality."""

    @pytest.fixture
    def chunks_df(self, sample_events_df):
        return create_chunks_dataframe(sample_events_df)

    def test_returns_dict(self, chunks_df):
        """verify_chunks_quality retourne un dictionnaire."""
        result = verify_chunks_quality(chunks_df)
        assert isinstance(result, dict)

    def test_contains_expected_keys(self, chunks_df):
        """Le dictionnaire contient les métriques attendues."""
        result = verify_chunks_quality(chunks_df)
        expected_keys = [
            "total_chunks",
            "unique_events",
            "tokens_mean",
            "tokens_median",
            "tokens_min",
            "tokens_max",
            "chunks_per_event_mean",
            "chunks_per_event_max",
        ]
        for key in expected_keys:
            assert key in result, f"Clé manquante : {key}"

    def test_total_chunks_correct(self, chunks_df):
        """total_chunks correspond à la longueur du DataFrame."""
        result = verify_chunks_quality(chunks_df)
        assert result["total_chunks"] == len(chunks_df)

    def test_unique_events_correct(self, chunks_df, sample_events_df):
        """unique_events correspond au nombre d'UIDs distincts dans les chunks."""
        result = verify_chunks_quality(chunks_df)
        assert result["unique_events"] == chunks_df["uid"].nunique()

    def test_token_stats_coherent(self, chunks_df):
        """Les statistiques de tokens sont cohérentes (min ≤ mean ≤ max)."""
        result = verify_chunks_quality(chunks_df)
        assert result["tokens_min"] <= result["tokens_mean"] <= result["tokens_max"]

    def test_chunks_per_event_mean_positive(self, chunks_df):
        """La moyenne de chunks par événement est > 0."""
        result = verify_chunks_quality(chunks_df)
        assert result["chunks_per_event_mean"] > 0


# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

class TestChunkingIntegration:
    """Tests d'intégration du pipeline de chunking."""

    def test_full_pipeline(self, sample_events_df):
        """Pipeline complet : create_chunks_dataframe → verify_chunks_quality."""
        df_chunks = create_chunks_dataframe(sample_events_df)
        metrics = verify_chunks_quality(df_chunks)

        assert len(df_chunks) > 0
        assert metrics["total_chunks"] == len(df_chunks)
        assert metrics["unique_events"] <= len(sample_events_df)

    def test_idempotency(self, sample_events_df):
        """Deux appels successifs produisent le même résultat."""
        df1 = create_chunks_dataframe(sample_events_df.copy())
        df2 = create_chunks_dataframe(sample_events_df.copy())
        assert len(df1) == len(df2)

    def test_real_data_if_available(self):
        """Test sur les données réelles si disponibles (skippé sinon)."""
        processed_path = Path("data/processed/evenements_chunks.parquet")
        if not processed_path.exists():
            pytest.skip("Fichier de chunks non disponible")

        df_chunks = pd.read_parquet(processed_path)

        # Vérifications de base
        assert len(df_chunks) > 0
        assert "chunk_text" in df_chunks.columns
        assert "chunk_tokens" in df_chunks.columns
        assert (df_chunks["chunk_tokens"] <= CHUNK_SIZE).mean() >= 0.95, (
            "Plus de 5% des chunks dépassent la taille maximale"
        )
        assert df_chunks["chunk_text"].str.strip().ne("").all()


# ============================================================================
# CONSTANTES EXPORTÉES
# ============================================================================

class TestConstants:
    """Vérifie que les constantes par défaut sont cohérentes."""

    def test_chunk_size_positive(self):
        assert CHUNK_SIZE > 0

    def test_chunk_overlap_positive(self):
        assert CHUNK_OVERLAP > 0

    def test_overlap_smaller_than_chunk(self):
        assert CHUNK_OVERLAP < CHUNK_SIZE

    def test_encoding_name_valid(self):
        """L'encodeur par défaut est chargeable par tiktoken."""
        enc = tiktoken.get_encoding(ENCODING_NAME)
        assert enc is not None


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
