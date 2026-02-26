"""
Script de decoupage (chunking) des textes pour la vectorisation.

Ce script decoupe les textes longs en chunks plus petits pour optimiser
la vectorisation et la recherche semantique. Il preserve les metadonnees
essentielles pour chaque chunk.

Auteur: Aymeric Bailleul
Date: 11/02/2026
"""

import pandas as pd
from pathlib import Path
import tiktoken
from typing import List, Dict


# ============================================================================
# CONSTANTES
# ============================================================================

CHUNK_SIZE = 250  # Taille d'un chunk en tokens
CHUNK_OVERLAP = 75  # Chevauchement entre chunks en tokens
ENCODING_NAME = "cl100k_base"  # Encodage compatible avec Mistral


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def load_cleaned_data(data_path: str) -> pd.DataFrame:
    """
    Charge les donnees nettoyees depuis un fichier Parquet.
    
    Args:
        data_path: Chemin vers le fichier Parquet nettoye
        
    Returns:
        DataFrame avec les donnees nettoyees
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    path = Path(data_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Le fichier {data_path} n'existe pas.")
    
    print(f"Chargement des donnees depuis {data_path}...")
    df = pd.read_parquet(data_path)
    print(f"[OK] {len(df):,} evenements charges avec {len(df.columns)} colonnes")
    
    return df


def count_tokens(text: str, encoding) -> int:
    """
    Compte le nombre de tokens dans un texte.
    
    Args:
        text: Texte a analyser
        encoding: Objet tiktoken.Encoding
        
    Returns:
        Nombre de tokens
    """
    if pd.isna(text) or text == "":
        return 0
    
    return len(encoding.encode(str(text)))


def split_text_into_chunks(
    text: str,
    encoding,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Decoupe un texte en chunks avec overlap.
    
    Args:
        text: Texte a decouper
        encoding: Objet tiktoken.Encoding
        chunk_size: Taille maximale d'un chunk en tokens
        overlap: Nombre de tokens de chevauchement entre chunks
        
    Returns:
        Liste des chunks de texte
    """
    if pd.isna(text) or text == "":
        return []
    
    text = str(text)
    
    # Encoder le texte en tokens
    tokens = encoding.encode(text)
    
    # Si le texte est deja court, retourner tel quel
    if len(tokens) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        # Definir la fin du chunk
        end = start + chunk_size
        
        # Extraire les tokens du chunk
        chunk_tokens = tokens[start:end]
        
        # Decoder les tokens en texte
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Avancer avec overlap
        start = end - overlap
        
        # Si on est proche de la fin, inclure tout le reste
        if start + chunk_size >= len(tokens) and start < len(tokens):
            chunk_tokens = tokens[start:]
            chunk_text = encoding.decode(chunk_tokens)
            if chunk_text.strip():  # Eviter les chunks vides
                chunks.append(chunk_text)
            break
    
    return chunks


def create_chunks_dataframe(
    df: pd.DataFrame,
    text_column: str = 'text_for_rag',
    metadata_columns: List[str] = None
) -> pd.DataFrame:
    """
    Cree un DataFrame de chunks a partir des donnees nettoyees.
    
    Args:
        df: DataFrame avec les evenements nettoyees
        text_column: Nom de la colonne contenant le texte a chunker
        metadata_columns: Colonnes de metadonnees a preserver
        
    Returns:
        DataFrame avec les chunks et leurs metadonnees
    """
    if metadata_columns is None:
        metadata_columns = [
            'uid',
            'title_fr',
            'firstdate_begin',
            'location_city',
            'location_region'
        ]
    
    # Verifier que les colonnes existent
    missing_cols = [col for col in metadata_columns + [text_column] 
                    if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonnes manquantes: {missing_cols}")
    
    print(f"\nDecoupage de {len(df):,} evenements en chunks...")
    print(f"Parametres: chunk_size={CHUNK_SIZE} tokens, overlap={CHUNK_OVERLAP} tokens")
    
    # Charger l'encodeur tiktoken
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    
    # Liste pour stocker les chunks
    chunks_data = []
    
    # Statistiques
    total_chunks = 0
    events_with_multiple_chunks = 0
    skipped_events = 0
    
    # Traiter chaque evenement
    for idx, row in df.iterrows():
        text = row[text_column]
        
        # Skip si texte vide
        if pd.isna(text) or str(text).strip() == "":
            skipped_events += 1
            continue
        
        # Decouper le texte en chunks
        chunks = split_text_into_chunks(text, encoding, CHUNK_SIZE, CHUNK_OVERLAP)
        
        if len(chunks) > 1:
            events_with_multiple_chunks += 1
        
        # Creer une entree pour chaque chunk
        for chunk_idx, chunk_text in enumerate(chunks):
            chunk_entry = {col: row[col] for col in metadata_columns}
            chunk_entry['chunk_index'] = chunk_idx
            chunk_entry['chunk_text'] = chunk_text
            chunk_entry['chunk_tokens'] = count_tokens(chunk_text, encoding)
            chunks_data.append(chunk_entry)
            total_chunks += 1
        
        # Afficher la progression tous les 1000 evenements
        if (idx + 1) % 1000 == 0:
            print(f"  Traite {idx + 1:,}/{len(df):,} evenements...")
    
    # Creer le DataFrame final
    df_chunks = pd.DataFrame(chunks_data)
    
    # Afficher les statistiques
    print(f"\n[OK] Decoupage termine:")
    print(f"  - Evenements traites: {len(df) - skipped_events:,}")
    print(f"  - Evenements ignores (texte vide): {skipped_events}")
    print(f"  - Total chunks crees: {total_chunks:,}")
    print(f"  - Evenements avec plusieurs chunks: {events_with_multiple_chunks:,}")
    print(f"  - Moyenne chunks/evenement: {total_chunks / (len(df) - skipped_events):.2f}")
    
    return df_chunks


def verify_chunks_quality(df_chunks: pd.DataFrame) -> Dict:
    """
    Verifie la qualite des chunks generes.
    
    Args:
        df_chunks: DataFrame des chunks
        
    Returns:
        Dictionnaire de metriques de qualite
    """
    print("\n=== Verification de la qualite des chunks ===")
    
    metrics = {}
    
    # Nombre total de chunks
    metrics['total_chunks'] = len(df_chunks)
    print(f"Total chunks: {metrics['total_chunks']:,}")
    
    # Nombre d'evenements uniques
    metrics['unique_events'] = df_chunks['uid'].nunique()
    print(f"Evenements uniques: {metrics['unique_events']:,}")
    
    # Statistiques sur les tokens
    metrics['tokens_mean'] = df_chunks['chunk_tokens'].mean()
    metrics['tokens_median'] = df_chunks['chunk_tokens'].median()
    metrics['tokens_min'] = df_chunks['chunk_tokens'].min()
    metrics['tokens_max'] = df_chunks['chunk_tokens'].max()
    
    print(f"\nStatistiques tokens:")
    print(f"  - Moyenne: {metrics['tokens_mean']:.1f}")
    print(f"  - Mediane: {metrics['tokens_median']:.1f}")
    print(f"  - Min: {metrics['tokens_min']}")
    print(f"  - Max: {metrics['tokens_max']}")
    
    # Distribution des chunks par evenement
    chunks_per_event = df_chunks.groupby('uid').size()
    metrics['chunks_per_event_mean'] = chunks_per_event.mean()
    metrics['chunks_per_event_max'] = chunks_per_event.max()
    
    print(f"\nChunks par evenement:")
    print(f"  - Moyenne: {metrics['chunks_per_event_mean']:.2f}")
    print(f"  - Maximum: {metrics['chunks_per_event_max']}")
    
    # Evenements avec 1 seul chunk vs plusieurs chunks
    single_chunk = (chunks_per_event == 1).sum()
    multiple_chunks = (chunks_per_event > 1).sum()
    
    print(f"\nDistribution:")
    print(f"  - Evenements avec 1 chunk: {single_chunk:,} ({single_chunk/len(chunks_per_event)*100:.1f}%)")
    print(f"  - Evenements avec plusieurs chunks: {multiple_chunks:,} ({multiple_chunks/len(chunks_per_event)*100:.1f}%)")
    
    # Completude des metadonnees
    for col in ['title_fr', 'firstdate_begin', 'location_city', 'location_region']:
        completude = (df_chunks[col].notna().sum() / len(df_chunks)) * 100
        metrics[f'{col}_completude'] = completude
        print(f"Completude {col}: {completude:.2f}%")
    
    return metrics


def save_chunks(df_chunks: pd.DataFrame, output_path: str):
    """
    Sauvegarde les chunks dans un fichier Parquet.
    
    Args:
        df_chunks: DataFrame des chunks
        output_path: Chemin du fichier de sortie
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSauvegarde des chunks dans {output_path}...")
    df_chunks.to_parquet(output_path, index=False)
    
    # Afficher la taille du fichier
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Fichier sauvegarde ({file_size_mb:.2f} MB)")


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """
    Orchestre le processus complet de chunking.
    """
    print("=" * 70)
    print("PHASE 2.6 - CHUNKING DES TEXTES")
    print("=" * 70)
    
    # Chemins des fichiers
    input_path = "data/processed/evenements_occitanie_clean.parquet"
    output_path = "data/processed/evenements_chunks.parquet"
    
    try:
        # Etape 1: Charger les donnees nettoyees
        df = load_cleaned_data(input_path)
        
        # Etape 2: Creer les chunks
        df_chunks = create_chunks_dataframe(df)
        
        # Etape 3: Verifier la qualite
        metrics = verify_chunks_quality(df_chunks)
        
        # Etape 4: Sauvegarder
        save_chunks(df_chunks, output_path)
        
        print("\n" + "=" * 70)
        print("[SUCCES] CHUNKING TERMINE AVEC SUCCES")
        print("=" * 70)
        print(f"\nFichier genere: {output_path}")
        print(f"Total chunks: {len(df_chunks):,}")
        print(f"Pret pour la vectorisation (Phase 3.1)")
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        raise


if __name__ == "__main__":
    main()
