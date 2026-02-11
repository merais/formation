"""
Tests pour la base vectorielle FAISS.

Ce module teste l'intégrité et les performances de la base vectorielle créée
avec les embeddings Mistral et l'index FAISS.

Usage:
    pytest tests/test_02_vectorstore.py -v
"""

import pytest
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
import time


# ============================================================================
# CHEMINS DES FICHIERS
# ============================================================================

VECTORSTORE_DIR = Path("data/vectorstore")
EMBEDDINGS_FILE = VECTORSTORE_DIR / "embeddings.npy"
METADATA_FILE = VECTORSTORE_DIR / "metadata.parquet"
INDEX_FILE = VECTORSTORE_DIR / "faiss_index.bin"
PROCESSED_DIR = Path("data/processed")
CLEAN_DATA_FILE = PROCESSED_DIR / "evenements_occitanie_clean.parquet"

EMBEDDING_DIM = 1024


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def embeddings():
    """Charge les embeddings pour les tests."""
    if not EMBEDDINGS_FILE.exists():
        pytest.skip(f"Fichier embeddings introuvable: {EMBEDDINGS_FILE}")
    return np.load(EMBEDDINGS_FILE)


@pytest.fixture(scope="module")
def metadata():
    """Charge les métadonnées pour les tests."""
    if not METADATA_FILE.exists():
        pytest.skip(f"Fichier métadonnées introuvable: {METADATA_FILE}")
    return pd.read_parquet(METADATA_FILE)


@pytest.fixture(scope="module")
def faiss_index():
    """Charge l'index FAISS pour les tests."""
    if not INDEX_FILE.exists():
        pytest.skip(f"Fichier index FAISS introuvable: {INDEX_FILE}")
    return faiss.read_index(str(INDEX_FILE))


@pytest.fixture(scope="module")
def clean_data():
    """Charge les données nettoyées pour les tests."""
    if not CLEAN_DATA_FILE.exists():
        pytest.skip(f"Fichier données nettoyées introuvable: {CLEAN_DATA_FILE}")
    return pd.read_parquet(CLEAN_DATA_FILE)


# ============================================================================
# TESTS DE STRUCTURE ET INTÉGRITÉ
# ============================================================================

def test_embeddings_file_exists():
    """Test: Le fichier embeddings.npy existe."""
    assert EMBEDDINGS_FILE.exists(), f"Fichier embeddings introuvable: {EMBEDDINGS_FILE}"


def test_metadata_file_exists():
    """Test: Le fichier metadata.parquet existe."""
    assert METADATA_FILE.exists(), f"Fichier métadonnées introuvable: {METADATA_FILE}"


def test_index_file_exists():
    """Test: Le fichier faiss_index.bin existe."""
    assert INDEX_FILE.exists(), f"Fichier index FAISS introuvable: {INDEX_FILE}"


def test_embeddings_shape(embeddings):
    """Test: Les embeddings ont la bonne forme (n_chunks, 1024)."""
    assert embeddings.ndim == 2, f"Embeddings doivent être 2D, obtenu {embeddings.ndim}D"
    assert embeddings.shape[1] == EMBEDDING_DIM, \
        f"Dimension attendue: {EMBEDDING_DIM}, obtenue: {embeddings.shape[1]}"


def test_embeddings_quality(embeddings):
    """Test: Les embeddings ne contiennent pas de NaN ou Inf."""
    assert not np.isnan(embeddings).any(), "Les embeddings contiennent des NaN"
    assert not np.isinf(embeddings).any(), "Les embeddings contiennent des Inf"


def test_embeddings_normalized(embeddings):
    """Test: Les embeddings sont normalisés (norme ≈ 1.0)."""
    norms = np.linalg.norm(embeddings, axis=1)
    avg_norm = norms.mean()
    assert 0.99 < avg_norm < 1.01, \
        f"Embeddings pas normalisés: norme moyenne = {avg_norm:.6f}"


def test_metadata_shape(metadata, embeddings):
    """Test: Le nombre de métadonnées correspond au nombre d'embeddings."""
    assert len(metadata) == len(embeddings), \
        f"Incohérence: {len(metadata)} métadonnées vs {len(embeddings)} embeddings"


def test_metadata_columns(metadata):
    """Test: Les métadonnées contiennent les colonnes essentielles."""
    required_columns = ['uid', 'title_fr', 'chunk_text', 'chunk_index']
    for col in required_columns:
        assert col in metadata.columns, f"Colonne manquante dans metadata: {col}"


def test_metadata_no_missing_values(metadata):
    """Test: Les métadonnées ne contiennent pas de valeurs manquantes critiques."""
    # UID et chunk_text doivent être présents à 100%
    assert metadata['uid'].isna().sum() == 0, "UID ne doit pas avoir de valeurs manquantes"
    assert metadata['chunk_text'].isna().sum() == 0, "chunk_text ne doit pas avoir de valeurs manquantes"
    
    # title_fr peut avoir quelques valeurs manquantes (cas observés dans les données)
    missing_titles = metadata['title_fr'].isna().sum()
    missing_pct = missing_titles / len(metadata) * 100
    assert missing_pct < 1.0, f"Trop de titres manquants: {missing_pct:.2f}%"


# ============================================================================
# TESTS DE L'INDEX FAISS
# ============================================================================

def test_faiss_index_loaded(faiss_index):
    """Test: L'index FAISS se charge correctement."""
    assert faiss_index is not None, "Index FAISS non chargé"


def test_faiss_index_size(faiss_index, embeddings):
    """Test: L'index FAISS contient tous les vecteurs."""
    assert faiss_index.ntotal == len(embeddings), \
        f"Index contient {faiss_index.ntotal} vecteurs, attendu {len(embeddings)}"


def test_faiss_index_dimension(faiss_index):
    """Test: L'index FAISS a la bonne dimension."""
    assert faiss_index.d == EMBEDDING_DIM, \
        f"Dimension index: {faiss_index.d}, attendue: {EMBEDDING_DIM}"


# ============================================================================
# TESTS DE RECHERCHE DE SIMILARITÉ
# ============================================================================

def test_similarity_search_self(faiss_index, embeddings, metadata):
    """Test: La recherche trouve le vecteur lui-même avec score parfait."""
    # Prendre le premier vecteur comme requête
    query_idx = 0
    query_vector = embeddings[query_idx:query_idx+1]
    
    # Rechercher les 1 plus proches voisins
    distances, indices = faiss_index.search(query_vector, k=1)
    
    # Le premier résultat doit être le vecteur lui-même
    assert indices[0][0] == query_idx, \
        f"Le vecteur devrait se trouver lui-même, trouvé index {indices[0][0]}"
    
    # Le score doit être proche de 1.0 (cosine similarity pour vecteurs normalisés)
    assert distances[0][0] > 0.99, \
        f"Score de similarité pour lui-même devrait être ~1.0, obtenu {distances[0][0]:.4f}"


def test_similarity_search_top5(faiss_index, embeddings, metadata):
    """Test: La recherche retourne 5 résultats pertinents."""
    query_idx = 0
    query_vector = embeddings[query_idx:query_idx+1]
    
    k = 5
    distances, indices = faiss_index.search(query_vector, k=k)
    
    # Vérifier qu'on a bien k résultats
    assert len(indices[0]) == k, f"Attendu {k} résultats, obtenu {len(indices[0])}"
    assert len(distances[0]) == k, f"Attendu {k} scores, obtenu {len(distances[0])}"
    
    # Vérifier que les scores sont décroissants
    assert all(distances[0][i] >= distances[0][i+1] for i in range(k-1)), \
        "Les scores doivent être triés par ordre décroissant"
    
    # Vérifier que tous les scores sont positifs (pour Inner Product)
    assert all(distances[0] > 0), "Tous les scores doivent être positifs"


def test_similarity_search_different_queries(faiss_index, embeddings, metadata):
    """Test: Différentes requêtes donnent des résultats différents."""
    query_idx_1 = 0
    query_idx_2 = 100
    
    query_1 = embeddings[query_idx_1:query_idx_1+1]
    query_2 = embeddings[query_idx_2:query_idx_2+1]
    
    distances_1, indices_1 = faiss_index.search(query_1, k=5)
    distances_2, indices_2 = faiss_index.search(query_2, k=5)
    
    # Les résultats doivent être différents
    assert not np.array_equal(indices_1, indices_2), \
        "Deux requêtes différentes ne doivent pas donner les mêmes résultats"


def test_similarity_search_batch(faiss_index, embeddings):
    """Test: La recherche par batch fonctionne correctement."""
    # Prendre 10 vecteurs comme requêtes
    n_queries = 10
    query_vectors = embeddings[:n_queries]
    
    k = 5
    distances, indices = faiss_index.search(query_vectors, k=k)
    
    # Vérifier la forme des résultats
    assert distances.shape == (n_queries, k), \
        f"Forme attendue: ({n_queries}, {k}), obtenue: {distances.shape}"
    assert indices.shape == (n_queries, k), \
        f"Forme attendue: ({n_queries}, {k}), obtenue: {indices.shape}"
    
    # Vérifier que chaque vecteur se trouve lui-même en premier
    for i in range(n_queries):
        assert indices[i][0] == i, \
            f"Le vecteur {i} devrait se trouver lui-même en premier"


# ============================================================================
# TESTS DE COHÉRENCE DES MÉTADONNÉES
# ============================================================================

def test_metadata_uid_coherence(metadata, clean_data):
    """Test: Les UIDs dans metadata correspondent à ceux dans les données nettoyées."""
    metadata_uids = set(metadata['uid'].unique())
    clean_uids = set(clean_data['uid'].unique())
    
    # Tous les UIDs de metadata doivent exister dans clean_data
    assert metadata_uids.issubset(clean_uids), \
        "Tous les UIDs de metadata doivent exister dans les données nettoyées"


def test_metadata_chunk_indices(metadata):
    """Test: Les indices de chunks sont cohérents pour chaque événement."""
    # Grouper par UID
    for uid, group in metadata.groupby('uid'):
        chunk_indices = sorted(group['chunk_index'].tolist())
        expected_indices = list(range(len(chunk_indices)))
        
        # Les indices doivent être 0, 1, 2, ... pour chaque événement
        assert chunk_indices == expected_indices, \
            f"Événement {uid}: indices incohérents {chunk_indices}, attendu {expected_indices}"


def test_metadata_titles_exist(metadata):
    """Test: La plupart des titres sont non vides."""
    empty_titles = metadata['title_fr'].isna().sum()
    total = len(metadata)
    completeness = (total - empty_titles) / total * 100
    
    # Au moins 99% des titres doivent être présents
    assert completeness >= 99.0, f"Complétude des titres insuffisante: {completeness:.2f}%"
    
    # Pour les titres présents, vérifier qu'ils ont une longueur minimale
    non_empty_titles = metadata['title_fr'].dropna()
    if len(non_empty_titles) > 0:
        min_length = non_empty_titles.str.len().min()
        assert min_length > 0, "Les titres présents doivent avoir une longueur > 0"


def test_metadata_chunk_text_exists(metadata):
    """Test: Tous les textes de chunks sont non vides."""
    empty_chunks = metadata['chunk_text'].isna().sum()
    assert empty_chunks == 0, f"{empty_chunks} chunks vides trouvés"
    
    # Vérifier que les chunks ont une longueur minimale
    min_length = metadata['chunk_text'].str.len().min()
    assert min_length > 10, "Tous les chunks doivent avoir une longueur > 10 caractères"


# ============================================================================
# TESTS DE COUVERTURE
# ============================================================================

def test_all_events_indexed(metadata, clean_data):
    """Test: Tous les événements nettoyés sont présents dans la base vectorielle."""
    n_clean_events = len(clean_data)
    n_indexed_events = metadata['uid'].nunique()
    
    assert n_indexed_events == n_clean_events, \
        f"Événements indexés: {n_indexed_events}, attendus: {n_clean_events}"


def test_chunks_distribution(metadata):
    """Test: La distribution des chunks est cohérente."""
    chunks_per_event = metadata.groupby('uid').size()
    
    # Statistiques de base
    mean_chunks = chunks_per_event.mean()
    median_chunks = chunks_per_event.median()
    max_chunks = chunks_per_event.max()
    
    # Vérifications de cohérence
    assert mean_chunks > 0, "Moyenne de chunks doit être > 0"
    assert median_chunks >= 1, "Médiane de chunks doit être >= 1"
    assert max_chunks >= median_chunks, "Maximum doit être >= médiane"
    
    # Au moins 50% des événements doivent avoir 1 chunk
    single_chunk_pct = (chunks_per_event == 1).sum() / len(chunks_per_event)
    assert single_chunk_pct > 0.5, \
        f"Au moins 50% des événements devraient avoir 1 chunk, obtenu {single_chunk_pct:.1%}"


# ============================================================================
# TESTS DE PERFORMANCE
# ============================================================================

def test_search_performance_single(faiss_index, embeddings):
    """Test: Mesurer le temps de recherche pour une requête."""
    query_vector = embeddings[0:1]
    k = 5
    
    # Mesurer le temps
    start_time = time.time()
    distances, indices = faiss_index.search(query_vector, k=k)
    elapsed = time.time() - start_time
    
    # La recherche doit être rapide (< 100ms pour IndexFlatIP)
    assert elapsed < 0.1, \
        f"Recherche trop lente: {elapsed*1000:.2f}ms (limite: 100ms)"
    
    print(f"\nTemps de recherche (1 requête, top-{k}): {elapsed*1000:.2f}ms")


def test_search_performance_batch(faiss_index, embeddings):
    """Test: Mesurer le temps de recherche pour un batch de requêtes."""
    n_queries = 100
    query_vectors = embeddings[:n_queries]
    k = 5
    
    # Mesurer le temps
    start_time = time.time()
    distances, indices = faiss_index.search(query_vectors, k=k)
    elapsed = time.time() - start_time
    
    # Calculer le temps moyen par requête
    avg_time_per_query = elapsed / n_queries
    
    # La recherche doit être rapide (< 10ms par requête en moyenne)
    assert avg_time_per_query < 0.01, \
        f"Recherche batch trop lente: {avg_time_per_query*1000:.2f}ms/requête (limite: 10ms)"
    
    print(f"\nTemps de recherche ({n_queries} requêtes, top-{k}):")
    print(f"   - Total: {elapsed*1000:.2f}ms")
    print(f"   - Moyenne: {avg_time_per_query*1000:.2f}ms/requête")


def test_index_memory_size():
    """Test: Vérifier la taille de l'index sur disque."""
    index_size_mb = INDEX_FILE.stat().st_size / 1024 / 1024
    embeddings_size_mb = EMBEDDINGS_FILE.stat().st_size / 1024 / 1024
    
    # L'index devrait être de taille comparable aux embeddings (IndexFlatIP)
    # Ratio attendu: ~0.5 (index optimisé) à ~1.0 (index non compressé)
    ratio = index_size_mb / embeddings_size_mb
    
    assert 0.3 < ratio < 1.2, \
        f"Ratio taille index/embeddings anormal: {ratio:.2f} (attendu: 0.5-1.0)"
    
    print(f"\nTailles des fichiers:")
    print(f"   - Index FAISS: {index_size_mb:.2f} MB")
    print(f"   - Embeddings: {embeddings_size_mb:.2f} MB")
    print(f"   - Ratio: {ratio:.2f}")


# ============================================================================
# TESTS D'INTÉGRATION
# ============================================================================

def test_end_to_end_search(faiss_index, embeddings, metadata):
    """Test d'intégration: Recherche end-to-end avec récupération des métadonnées."""
    # 1. Choisir une requête
    query_idx = 42
    query_vector = embeddings[query_idx:query_idx+1]
    query_title = metadata.iloc[query_idx]['title_fr']
    
    # 2. Effectuer la recherche
    k = 5
    distances, indices = faiss_index.search(query_vector, k=k)
    
    # 3. Récupérer les métadonnées
    results = metadata.iloc[indices[0]]
    
    # 4. Vérifications
    assert len(results) == k, f"Attendu {k} résultats, obtenu {len(results)}"
    
    # Le premier résultat doit être la requête elle-même
    assert results.iloc[0]['title_fr'] == query_title, \
        "Le premier résultat devrait être la requête elle-même"
    
    # Tous les résultats doivent avoir les colonnes requises
    required_cols = ['uid', 'title_fr', 'chunk_text']
    for col in required_cols:
        assert col in results.columns, f"Colonne manquante: {col}"
        assert not results[col].isna().any(), f"Valeurs manquantes dans {col}"
    
    print(f"\nRecherche end-to-end réussie:")
    print(f"   - Requête: {query_title[:60]}...")
    print(f"   - {k} résultats récupérés avec métadonnées complètes")


def test_vectorstore_complete_workflow():
    """Test: Workflow complet de la base vectorielle."""
    print("\n" + "="*70)
    print("TEST DU WORKFLOW COMPLET DE LA BASE VECTORIELLE")
    print("="*70)
    
    # 1. Charger tous les composants
    assert EMBEDDINGS_FILE.exists(), "Embeddings manquants"
    embeddings = np.load(EMBEDDINGS_FILE)
    print(f"[OK] Embeddings chargés: {embeddings.shape}")
    
    assert METADATA_FILE.exists(), "Métadonnées manquantes"
    metadata = pd.read_parquet(METADATA_FILE)
    print(f"[OK] Métadonnées chargées: {len(metadata)} entrées")
    
    assert INDEX_FILE.exists(), "Index FAISS manquant"
    index = faiss.read_index(str(INDEX_FILE))
    print(f"[OK] Index FAISS chargé: {index.ntotal} vecteurs")
    
    # 2. Vérifier la cohérence
    assert len(embeddings) == len(metadata) == index.ntotal, "Incohérence des tailles"
    print(f"[OK] Cohérence vérifiée: {len(embeddings)} éléments")
    
    # 3. Test de recherche
    query = embeddings[0:1]
    distances, indices = index.search(query, k=3)
    print(f"[OK] Recherche fonctionnelle: top-3 trouvés")
    
    # 4. Récupération des métadonnées
    results = metadata.iloc[indices[0]]
    print(f"[OK] Métadonnées récupérées: {len(results)} résultats")
    
    print("\n" + "="*70)
    print("[SUCCES] WORKFLOW COMPLET VALIDÉ")
    print("="*70)
