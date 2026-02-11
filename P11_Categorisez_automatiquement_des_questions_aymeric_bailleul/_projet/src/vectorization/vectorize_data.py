"""
Script de vectorisation des chunks avec Mistral Embeddings.

Ce script transforme les chunks de texte en vecteurs numeriques (embeddings)
en utilisant l'API Mistral Embeddings. Il gere le rate limiting et sauvegarde
les vecteurs avec leurs metadonnees.

Auteur: Aymeric Bailleul
Date: 11/02/2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import time
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv
from mistralai import Mistral


# ============================================================================
# CONSTANTES
# ============================================================================

EMBEDDING_MODEL = "mistral-embed"  # Modele Mistral pour embeddings (1024 dimensions)
EMBEDDING_DIM = 1024  # Dimension des vecteurs
BATCH_SIZE = 100  # Nombre de chunks a vectoriser par batch
RATE_LIMIT_DELAY = 1.0  # Delai entre les batches (secondes)
MAX_RETRIES = 3  # Nombre de tentatives en cas d'erreur
RETRY_DELAY = 5.0  # Delai entre les tentatives (secondes)


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def load_api_key() -> str:
    """
    Charge la cle API Mistral depuis le fichier .env
    
    Returns:
        Cle API Mistral
        
    Raises:
        ValueError: Si la cle API n'est pas trouvee
    """
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY non trouvee. "
            "Verifiez que le fichier .env existe et contient MISTRAL_API_KEY=votre_cle"
        )
    
    print("[OK] Cle API Mistral chargee")
    return api_key


def load_chunks(chunks_path: str) -> pd.DataFrame:
    """
    Charge les chunks depuis un fichier Parquet.
    
    Args:
        chunks_path: Chemin vers le fichier Parquet des chunks
        
    Returns:
        DataFrame avec les chunks
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    path = Path(chunks_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Le fichier {chunks_path} n'existe pas.")
    
    print(f"\nChargement des chunks depuis {chunks_path}...")
    df = pd.read_parquet(chunks_path)
    print(f"[OK] {len(df):,} chunks charges")
    
    # Afficher les colonnes
    print(f"Colonnes: {list(df.columns)}")
    
    return df


def vectorize_batch(
    texts: List[str],
    client: Mistral,
    model: str = EMBEDDING_MODEL,
    retry_count: int = 0
) -> np.ndarray:
    """
    Vectorise un batch de textes avec l'API Mistral Embeddings.
    
    Args:
        texts: Liste de textes a vectoriser
        client: Client Mistral configure
        model: Nom du modele d'embedding
        retry_count: Compteur de tentatives (pour retry logic)
        
    Returns:
        Array numpy des embeddings (shape: [len(texts), 1024])
        
    Raises:
        Exception: Si l'API echoue apres toutes les tentatives
    """
    try:
        # Appel a l'API Mistral Embeddings
        response = client.embeddings.create(
            model=model,
            inputs=texts
        )
        
        # Extraire les embeddings
        embeddings = [item.embedding for item in response.data]
        
        return np.array(embeddings)
        
    except Exception as e:
        if retry_count < MAX_RETRIES:
            print(f"[ATTENTION] Erreur API (tentative {retry_count + 1}/{MAX_RETRIES}): {e}")
            print(f"  Nouvelle tentative dans {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            return vectorize_batch(texts, client, model, retry_count + 1)
        else:
            print(f"[ERREUR] Erreur API apres {MAX_RETRIES} tentatives: {e}")
            raise


def vectorize_chunks(
    df_chunks: pd.DataFrame,
    client: Mistral,
    text_column: str = 'chunk_text',
    batch_size: int = BATCH_SIZE
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Vectorise tous les chunks par batches.
    
    Args:
        df_chunks: DataFrame des chunks
        client: Client Mistral configure
        text_column: Nom de la colonne contenant le texte
        batch_size: Taille des batches
        
    Returns:
        Tuple (embeddings, metadonnees):
            - embeddings: Array numpy (shape: [n_chunks, 1024])
            - metadonnees: DataFrame avec uid, title, dates, etc.
    """
    print(f"\n=== Vectorisation de {len(df_chunks):,} chunks ===")
    print(f"Parametres:")
    print(f"  - Modele: {EMBEDDING_MODEL}")
    print(f"  - Dimension: {EMBEDDING_DIM}")
    print(f"  - Batch size: {batch_size}")
    print(f"  - Rate limit delay: {RATE_LIMIT_DELAY}s")
    
    # Preparer les textes
    texts = df_chunks[text_column].tolist()
    n_chunks = len(texts)
    n_batches = (n_chunks + batch_size - 1) // batch_size
    
    print(f"\nNombre de batches: {n_batches}")
    print("Debut de la vectorisation...\n")
    
    # Vectoriser par batches
    all_embeddings = []
    start_time = time.time()
    
    for i in range(0, n_chunks, batch_size):
        batch_num = i // batch_size + 1
        end_idx = min(i + batch_size, n_chunks)
        batch_texts = texts[i:end_idx]
        
        print(f"Batch {batch_num}/{n_batches} ({len(batch_texts)} chunks)...", end=" ")
        
        # Vectoriser le batch
        batch_embeddings = vectorize_batch(batch_texts, client)
        all_embeddings.append(batch_embeddings)
        
        # Calculer et afficher le temps
        elapsed = time.time() - start_time
        chunks_done = end_idx
        avg_time_per_chunk = elapsed / chunks_done
        remaining_chunks = n_chunks - chunks_done
        eta_seconds = remaining_chunks * avg_time_per_chunk
        
        print(f"[OK] (ETA: {eta_seconds/60:.1f}m)")
        
        # Rate limiting (sauf pour le dernier batch)
        if batch_num < n_batches:
            time.sleep(RATE_LIMIT_DELAY)
    
    # Concatener tous les embeddings
    embeddings = np.vstack(all_embeddings)
    
    # Statistiques finales
    total_time = time.time() - start_time
    print(f"\n[OK] Vectorisation terminee en {total_time/60:.2f} minutes")
    print(f"  - Chunks vectorises: {len(embeddings):,}")
    print(f"  - Shape des embeddings: {embeddings.shape}")
    print(f"  - Temps moyen par chunk: {total_time/len(embeddings):.3f}s")
    
    return embeddings, df_chunks


def verify_embeddings(embeddings: np.ndarray, df_chunks: pd.DataFrame) -> Dict:
    """
    Verifie la qualite des embeddings generes.
    
    Args:
        embeddings: Array numpy des embeddings
        df_chunks: DataFrame des chunks
        
    Returns:
        Dictionnaire de metriques
    """
    print("\n=== Verification de la qualite des embeddings ===")
    
    metrics = {}
    
    # Dimensions
    metrics['n_embeddings'] = embeddings.shape[0]
    metrics['embedding_dim'] = embeddings.shape[1]
    print(f"Nombre d'embeddings: {metrics['n_embeddings']:,}")
    print(f"Dimension: {metrics['embedding_dim']}")
    
    # Verifier la coherence avec les chunks
    assert len(embeddings) == len(df_chunks), \
        f"Mismatch: {len(embeddings)} embeddings vs {len(df_chunks)} chunks"
    print(f"[OK] Coherence chunks/embeddings verifiee")
    
    # Statistiques sur les vecteurs
    metrics['mean_norm'] = np.linalg.norm(embeddings, axis=1).mean()
    metrics['std_norm'] = np.linalg.norm(embeddings, axis=1).std()
    print(f"\nNorme des vecteurs:")
    print(f"  - Moyenne: {metrics['mean_norm']:.3f}")
    print(f"  - Ecart-type: {metrics['std_norm']:.3f}")
    
    # Verifier qu'il n'y a pas de NaN ou Inf
    has_nan = np.isnan(embeddings).any()
    has_inf = np.isinf(embeddings).any()
    metrics['has_nan'] = has_nan
    metrics['has_inf'] = has_inf
    
    if has_nan or has_inf:
        print(f"[ATTENTION] NaN={has_nan}, Inf={has_inf}")
    else:
        print(f"[OK] Pas de valeurs invalides (NaN/Inf)")
    
    return metrics


def save_embeddings(
    embeddings: np.ndarray,
    df_chunks: pd.DataFrame,
    output_dir: str = "data/vectorstore"
):
    """
    Sauvegarde les embeddings et metadonnees.
    
    Args:
        embeddings: Array numpy des embeddings
        df_chunks: DataFrame des chunks avec metadonnees
        output_dir: Repertoire de sortie
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== Sauvegarde des embeddings ===")
    
    # 1. Sauvegarder les embeddings (numpy)
    embeddings_file = output_path / "embeddings.npy"
    np.save(embeddings_file, embeddings)
    embeddings_size_mb = embeddings_file.stat().st_size / (1024 * 1024)
    print(f"[OK] Embeddings sauvegardes: {embeddings_file}")
    print(f"  Taille: {embeddings_size_mb:.2f} MB")
    
    # 2. Sauvegarder les metadonnees (Parquet)
    metadata_file = output_path / "metadata.parquet"
    df_chunks.to_parquet(metadata_file, index=False)
    metadata_size_mb = metadata_file.stat().st_size / (1024 * 1024)
    print(f"[OK] Metadonnees sauvegardees: {metadata_file}")
    print(f"  Taille: {metadata_size_mb:.2f} MB")
    
    # 3. Sauvegarder un fichier de config
    config_file = output_path / "config.txt"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(f"VECTORISATION CONFIGURATION\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Modele: {EMBEDDING_MODEL}\n")
        f.write(f"Dimension: {EMBEDDING_DIM}\n")
        f.write(f"Nombre de chunks: {len(embeddings):,}\n")
        f.write(f"Shape embeddings: {embeddings.shape}\n")
        f.write(f"Batch size: {BATCH_SIZE}\n")
        f.write(f"Rate limit delay: {RATE_LIMIT_DELAY}s\n")
    print(f"[OK] Configuration sauvegardee: {config_file}")
    
    print(f"\n[OK] Tous les fichiers sauvegardes dans: {output_path}")


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """
    Orchestre le processus complet de vectorisation.
    """
    print("=" * 70)
    print("PHASE 3.1 - VECTORISATION AVEC MISTRAL EMBEDDINGS")
    print("=" * 70)
    
    # Chemins des fichiers
    chunks_path = "data/processed/evenements_chunks.parquet"
    output_dir = "data/vectorstore"
    
    try:
        # Etape 1: Charger la cle API
        api_key = load_api_key()
        client = Mistral(api_key=api_key)
        
        # Etape 2: Charger les chunks
        df_chunks = load_chunks(chunks_path)
        
        # Etape 3: Vectoriser les chunks
        embeddings, df_metadata = vectorize_chunks(df_chunks, client)
        
        # Etape 4: Verifier la qualite
        metrics = verify_embeddings(embeddings, df_metadata)
        
        # Etape 5: Sauvegarder
        save_embeddings(embeddings, df_metadata, output_dir)
        
        print("\n" + "=" * 70)
        print("[SUCCES] VECTORISATION TERMINEE AVEC SUCCES")
        print("=" * 70)
        print(f"\nFichiers generes:")
        print(f"  - {output_dir}/embeddings.npy ({embeddings.shape[0]:,} vecteurs)")
        print(f"  - {output_dir}/metadata.parquet ({len(df_metadata):,} lignes)")
        print(f"  - {output_dir}/config.txt")
        print(f"\nPret pour la creation de l'index FAISS (Phase 3.2)")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        raise


if __name__ == "__main__":
    main()
