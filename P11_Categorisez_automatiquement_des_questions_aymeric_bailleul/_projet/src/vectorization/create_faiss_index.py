"""
Script pour créer l'index FAISS à partir des embeddings.

Ce script charge les embeddings Mistral générés précédemment et crée un index
FAISS optimisé pour la recherche de similarité.

Usage:
    python src/vectorization/create_faiss_index.py

Entrées:
    - data/vectorstore/embeddings.npy: Embeddings (10676, 1024)
    - data/vectorstore/metadata.parquet: Métadonnées des chunks

Sorties:
    - data/vectorstore/faiss_index.bin: Index FAISS
    - data/vectorstore/index_config.txt: Configuration de l'index
"""

import numpy as np
import pandas as pd
import faiss
from pathlib import Path
from datetime import datetime


# ============================================================================
# CONSTANTES
# ============================================================================

VECTORSTORE_DIR = Path("data/vectorstore")
EMBEDDINGS_FILE = VECTORSTORE_DIR / "embeddings.npy"
METADATA_FILE = VECTORSTORE_DIR / "metadata.parquet"
INDEX_FILE = VECTORSTORE_DIR / "faiss_index.bin"
CONFIG_FILE = VECTORSTORE_DIR / "index_config.txt"

EMBEDDING_DIM = 1024  # Dimension des embeddings Mistral


# ============================================================================
# FONCTIONS PRINCIPALES
# ============================================================================

def load_embeddings() -> np.ndarray:
    """
    Charge les embeddings depuis le fichier NumPy.
    
    Returns:
        np.ndarray: Matrice des embeddings (n_chunks, embedding_dim)
    
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        ValueError: Si les dimensions sont incorrectes
    """
    print(f"\n{'='*70}")
    print("CHARGEMENT DES EMBEDDINGS")
    print(f"{'='*70}\n")
    
    if not EMBEDDINGS_FILE.exists():
        raise FileNotFoundError(
            f"Fichier embeddings introuvable: {EMBEDDINGS_FILE}\n"
            f"Exécutez d'abord: python src/vectorization/vectorize_data.py"
        )
    
    print(f"Chargement depuis: {EMBEDDINGS_FILE}")
    embeddings = np.load(EMBEDDINGS_FILE)
    
    print(f"[OK] Embeddings chargés: {embeddings.shape}")
    print(f"  - Nombre de vecteurs: {embeddings.shape[0]:,}")
    print(f"  - Dimension: {embeddings.shape[1]}")
    print(f"  - Type: {embeddings.dtype}")
    print(f"  - Taille: {embeddings.nbytes / 1024 / 1024:.2f} MB")
    
    # Vérification des dimensions
    if embeddings.shape[1] != EMBEDDING_DIM:
        raise ValueError(
            f"Dimension incorrecte: attendu {EMBEDDING_DIM}, "
            f"obtenu {embeddings.shape[1]}"
        )
    
    return embeddings


def load_metadata() -> pd.DataFrame:
    """
    Charge les métadonnées des chunks.
    
    Returns:
        pd.DataFrame: Métadonnées avec uid, title_fr, etc.
    """
    print(f"\n{'='*70}")
    print("CHARGEMENT DES MÉTADONNÉES")
    print(f"{'='*70}\n")
    
    if not METADATA_FILE.exists():
        raise FileNotFoundError(f"Fichier métadonnées introuvable: {METADATA_FILE}")
    
    print(f"Chargement depuis: {METADATA_FILE}")
    metadata = pd.read_parquet(METADATA_FILE)
    
    print(f"[OK] Métadonnées chargées: {len(metadata):,} entrées")
    print(f"  - Colonnes: {', '.join(metadata.columns.tolist()[:5])}...")
    
    return metadata


def verify_embeddings(embeddings: np.ndarray) -> dict:
    """
    Vérifie la qualité des embeddings avant l'indexation.
    
    Args:
        embeddings: Matrice des embeddings
    
    Returns:
        dict: Statistiques de vérification
    """
    print(f"\n{'='*70}")
    print("VÉRIFICATION DES EMBEDDINGS")
    print(f"{'='*70}\n")
    
    stats = {}
    
    # Vérifier les valeurs manquantes
    has_nan = np.isnan(embeddings).any()
    has_inf = np.isinf(embeddings).any()
    
    print(f"  - NaN présents: {'[ERREUR] OUI' if has_nan else '[OK] NON'}")
    print(f"  - Inf présents: {'[ERREUR] OUI' if has_inf else '[OK] NON'}")
    
    stats['has_nan'] = bool(has_nan)
    stats['has_inf'] = bool(has_inf)
    
    if has_nan or has_inf:
        raise ValueError("Les embeddings contiennent des valeurs NaN ou Inf")
    
    # Vérifier la normalisation (Mistral normalise automatiquement)
    norms = np.linalg.norm(embeddings, axis=1)
    avg_norm = norms.mean()
    min_norm = norms.min()
    max_norm = norms.max()
    
    print(f"  - Norme moyenne: {avg_norm:.6f}")
    print(f"  - Norme min: {min_norm:.6f}")
    print(f"  - Norme max: {max_norm:.6f}")
    
    stats['avg_norm'] = float(avg_norm)
    stats['min_norm'] = float(min_norm)
    stats['max_norm'] = float(max_norm)
    stats['is_normalized'] = (0.99 < avg_norm < 1.01)
    
    if stats['is_normalized']:
        print(f"  [OK] Embeddings normalisés (cosine similarity optimale)")
    
    return stats


def create_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """
    Crée un index FAISS optimisé pour la recherche de similarité.
    
    Pour des embeddings normalisés, on utilise IndexFlatIP (Inner Product)
    qui est équivalent à la similarité cosinus pour des vecteurs normalisés.
    
    Args:
        embeddings: Matrice des embeddings (n_chunks, embedding_dim)
    
    Returns:
        faiss.Index: Index FAISS créé et populé
    """
    print(f"\n{'='*70}")
    print("CRÉATION DE L'INDEX FAISS")
    print(f"{'='*70}\n")
    
    n_vectors, dim = embeddings.shape
    
    print(f"Configuration:")
    print(f"  - Nombre de vecteurs: {n_vectors:,}")
    print(f"  - Dimension: {dim}")
    
    # Choisir le type d'index selon la taille du dataset
    # Pour ~10K vecteurs, IndexFlatIP est optimal (recherche exacte, rapide)
    if n_vectors < 50000:
        print(f"  - Type d'index: IndexFlatIP (recherche exacte)")
        print(f"  - Raison: Dataset de taille moyenne (< 50K vecteurs)")
        index = faiss.IndexFlatIP(dim)
        index_type = "IndexFlatIP"
    else:
        # Pour de plus gros datasets, utiliser IVF (Inverted File)
        print(f"  - Type d'index: IndexIVFFlat (recherche approximative)")
        n_clusters = int(np.sqrt(n_vectors))  # Heuristique standard
        quantizer = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quantizer, dim, n_clusters, faiss.METRIC_INNER_PRODUCT)
        index_type = "IndexIVFFlat"
        
        print(f"  - Entraînement de l'index avec {n_clusters} clusters...")
        index.train(embeddings)
    
    print(f"\nAjout des vecteurs à l'index...")
    index.add(embeddings)
    
    print(f"[OK] Index créé avec succès")
    print(f"  - Vecteurs indexés: {index.ntotal:,}")
    print(f"  - Type: {index_type}")
    
    return index


def save_index(index: faiss.Index, embeddings_shape: tuple, stats: dict) -> None:
    """
    Sauvegarde l'index FAISS et sa configuration.
    
    Args:
        index: Index FAISS à sauvegarder
        embeddings_shape: Forme de la matrice d'embeddings
        stats: Statistiques de vérification
    """
    print(f"\n{'='*70}")
    print("SAUVEGARDE DE L'INDEX")
    print(f"{'='*70}\n")
    
    # Sauvegarder l'index
    print(f"Sauvegarde de l'index: {INDEX_FILE}")
    faiss.write_index(index, str(INDEX_FILE))
    
    index_size_mb = INDEX_FILE.stat().st_size / 1024 / 1024
    print(f"[OK] Index sauvegardé: {index_size_mb:.2f} MB")
    
    # Sauvegarder la configuration
    config = {
        "creation_date": datetime.now().isoformat(),
        "index_type": type(index).__name__,
        "n_vectors": int(index.ntotal),
        "embedding_dim": embeddings_shape[1],
        "metric": "INNER_PRODUCT (cosine similarity pour vecteurs normalisés)",
        "index_file": str(INDEX_FILE.name),
        "index_size_mb": round(index_size_mb, 2),
        "embeddings_stats": stats
    }
    
    print(f"\nSauvegarde de la configuration: {CONFIG_FILE}")
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write("CONFIGURATION DE L'INDEX FAISS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date de création: {config['creation_date']}\n\n")
        f.write(f"Type d'index: {config['index_type']}\n")
        f.write(f"Nombre de vecteurs: {config['n_vectors']:,}\n")
        f.write(f"Dimension des embeddings: {config['embedding_dim']}\n")
        f.write(f"Métrique de similarité: {config['metric']}\n\n")
        f.write(f"Fichier index: {config['index_file']}\n")
        f.write(f"Taille de l'index: {config['index_size_mb']} MB\n\n")
        f.write("Statistiques des embeddings:\n")
        f.write(f"  - Norme moyenne: {stats['avg_norm']:.6f}\n")
        f.write(f"  - Norme min: {stats['min_norm']:.6f}\n")
        f.write(f"  - Norme max: {stats['max_norm']:.6f}\n")
        f.write(f"  - Normalisés: {stats['is_normalized']}\n")
    
    print(f"[OK] Configuration sauvegardée")


def test_index(index: faiss.Index, embeddings: np.ndarray, metadata: pd.DataFrame) -> None:
    """
    Teste l'index FAISS avec une requête exemple.
    
    Args:
        index: Index FAISS à tester
        embeddings: Matrice des embeddings
        metadata: Métadonnées des chunks
    """
    print(f"\n{'='*70}")
    print("TEST DE L'INDEX")
    print(f"{'='*70}\n")
    
    # Utiliser le premier embedding comme requête test
    query_idx = 0
    query_vector = embeddings[query_idx:query_idx+1]  # Shape (1, 1024)
    
    print(f"Recherche des 5 chunks les plus similaires au chunk #{query_idx}")
    print(f"   Titre original: {metadata.iloc[query_idx]['title_fr'][:60]}...")
    
    # Recherche des k plus proches voisins
    k = 5
    distances, indices = index.search(query_vector, k)
    
    print(f"\nRésultats (similarité cosinus):\n")
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        title = metadata.iloc[idx]['title_fr'][:50]
        chunk_idx = metadata.iloc[idx]['chunk_index']
        print(f"  {i+1}. Score: {dist:.4f} | Chunk #{idx} (partie {chunk_idx}) | {title}...")
    
    print(f"\n[OK] Index fonctionnel - Prêt pour la recherche sémantique")


def main():
    """
    Fonction principale: crée l'index FAISS complet.
    """
    print("\n" + "="*70)
    print("CRÉATION DE L'INDEX FAISS POUR LA BASE VECTORIELLE")
    print("="*70)
    
    start_time = datetime.now()
    
    try:
        # 1. Charger les embeddings
        embeddings = load_embeddings()
        
        # 2. Charger les métadonnées
        metadata = load_metadata()
        
        # 3. Vérifier la cohérence
        if len(embeddings) != len(metadata):
            raise ValueError(
                f"Incohérence: {len(embeddings)} embeddings "
                f"vs {len(metadata)} métadonnées"
            )
        
        # 4. Vérifier la qualité des embeddings
        stats = verify_embeddings(embeddings)
        
        # 5. Créer l'index FAISS
        index = create_faiss_index(embeddings)
        
        # 6. Sauvegarder l'index et sa configuration
        save_index(index, embeddings.shape, stats)
        
        # 7. Tester l'index
        test_index(index, embeddings, metadata)
        
        # Résumé final
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*70}")
        print("[SUCCES] INDEXATION TERMINÉE AVEC SUCCÈS")
        print(f"{'='*70}\n")
        print(f"Temps d'exécution: {elapsed:.2f} secondes")
        print(f"Fichiers créés:")
        print(f"   - {INDEX_FILE}")
        print(f"   - {CONFIG_FILE}")
        print(f"\nProchaine étape: Tests de la base vectorielle (Phase 3.3)")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        raise


if __name__ == "__main__":
    main()
