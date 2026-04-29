"""
Script de nettoyage des donnees Open Agenda

Ce script effectue le nettoyage complet des donnees d'evenements :
- Filtrage geographique (Occitanie) et temporel (1 an + futurs)
- Suppression des colonnes vides
- Nettoyage du HTML dans les descriptions
- Creation d'un champ texte consolide pour le RAG
- Sauvegarde des donnees nettoyees

Auteur: Aymeric Bailleul
Date: 09/02/2026
"""

import pandas as pd
from pathlib import Path
import re
from html import unescape
from datetime import timedelta


def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Charge les donnees brutes depuis un fichier Parquet.
    
    Args:
        file_path: Chemin vers le fichier Parquet
        
    Returns:
        DataFrame contenant les donnees brutes
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    data_path = Path(file_path)
    if not data_path.exists():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
    
    print(f"Chargement des donnees depuis {file_path}...")
    df = pd.read_parquet(data_path)
    print(f"  {len(df):,} evenements charges")
    print(f"  {len(df.columns)} colonnes")
    return df


def filter_by_region_and_time(df: pd.DataFrame, region: str = "Occitanie") -> pd.DataFrame:
    """
    Filtre les evenements par region et periode temporelle.
    
    Conserve les evenements :
    - De la region specifiee
    - Des 12 derniers mois + tous les evenements futurs
    
    Args:
        df: DataFrame source
        region: Nom de la region a conserver (defaut: "Occitanie")
        
    Returns:
        DataFrame filtre
    """
    print(f"\nFiltrage geographique et temporel...")
    print(f"  Region cible: {region}")
    
    # Filtrage geographique
    df_region = df[df['location_region'].str.contains(region, case=False, na=False)].copy()
    print(f"  Evenements dans {region}: {len(df_region):,}")
    
    # Filtrage temporel
    today = pd.Timestamp.now(tz='Europe/Paris')
    one_year_ago = today - timedelta(days=365)
    
    # Evenements du passe (1 an)
    df_past = df_region[
        (df_region['firstdate_begin'] >= one_year_ago) & 
        (df_region['firstdate_begin'] < today)
    ]
    
    # Evenements futurs
    df_future = df_region[df_region['firstdate_begin'] >= today]
    
    # Concatenation
    df_filtered = pd.concat([df_past, df_future])
    
    print(f"  Periode: {one_year_ago.strftime('%Y-%m-%d')} a aujourd'hui + futurs")
    print(f"  Evenements passes (1 an): {len(df_past):,}")
    print(f"  Evenements futurs: {len(df_future):,}")
    print(f"  Total filtre: {len(df_filtered):,}")
    
    return df_filtered


def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les colonnes totalement vides du DataFrame.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame sans les colonnes vides
    """
    print("\nSuppression des colonnes vides...")
    
    colonnes_a_supprimer = [
        nom_colonne for nom_colonne in df.columns 
        if df[nom_colonne].notna().sum() == 0
    ]
    
    if colonnes_a_supprimer:
        print(f"  Colonnes a supprimer ({len(colonnes_a_supprimer)}):")
        for nom_colonne in colonnes_a_supprimer:
            print(f"    - {nom_colonne}")
        df_clean = df.drop(columns=colonnes_a_supprimer)
        print(f"  Dataset: {df.shape} -> {df_clean.shape}")
        return df_clean
    else:
        print("  Aucune colonne vide a supprimer")
        return df


def clean_html(text: str) -> str:
    """
    Nettoie le HTML d'un texte.
    
    - Decode les entites HTML
    - Supprime les balises HTML
    - Normalise les espaces
    
    Args:
        text: Texte a nettoyer
        
    Returns:
        Texte nettoye
    """
    if pd.isna(text):
        return text
    
    # Decode HTML entities
    text = unescape(str(text))
    
    # Suppression des balises HTML
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Suppression des espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Suppression des espaces en debut/fin
    text = text.strip()
    
    return text


def clean_html_descriptions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le HTML dans la colonne longdescription_fr.
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame avec descriptions nettoyees
    """
    print("\nNettoyage du HTML dans longdescription_fr...")
    
    if 'longdescription_fr' in df.columns:
        # Comptage avant nettoyage
        html_avant = df['longdescription_fr'].fillna('').str.contains('<[^>]+>', regex=True).sum()
        
        # Nettoyage
        df['longdescription_fr'] = df['longdescription_fr'].apply(clean_html)
        
        # Comptage apres nettoyage
        html_apres = df['longdescription_fr'].fillna('').str.contains('<[^>]+>', regex=True).sum()
        
        print(f"  Textes avec HTML avant: {html_avant}")
        print(f"  Textes avec HTML apres: {html_apres}")
        print(f"  [OK] Nettoyage HTML termine")
    else:
        print("  Colonne longdescription_fr non trouvee")
    
    return df


def create_rag_text_field(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cree un champ texte consolide pour la vectorisation RAG.
    
    Combine:
    - Titre
    - Description courte
    - Description longue
    - Mots-cles
    - Lieu
    
    Args:
        df: DataFrame source
        
    Returns:
        DataFrame avec nouvelle colonne text_for_rag
    """
    print("\nCreation du champ text_for_rag...")
    
    def combine_text(row):
        """Combine les champs texte d'un evenement"""
        parts = []
        
        # Titre
        if pd.notna(row['title_fr']):
            parts.append(f"Titre: {row['title_fr']}")
        
        # Description courte
        if pd.notna(row['description_fr']):
            parts.append(f"Description: {row['description_fr']}")
        
        # Description longue
        if pd.notna(row['longdescription_fr']) and len(str(row['longdescription_fr'])) > 10:
            parts.append(f"Details: {row['longdescription_fr']}")
        
        # Mots-cles
        if pd.notna(row.get('keywords_fr')):
            parts.append(f"Mots-cles: {row['keywords_fr']}")
        
        # Localisation
        if pd.notna(row['location_city']):
            parts.append(f"Lieu: {row['location_city']}")
        
        return " | ".join(parts)
    
    df['text_for_rag'] = df.apply(combine_text, axis=1)
    
    longueur_moyenne = df['text_for_rag'].str.len().mean()
    print(f"  Longueur moyenne: {longueur_moyenne:.0f} caracteres")
    print(f"  [OK] Champ text_for_rag cree")
    
    return df


def verify_data_quality(df: pd.DataFrame) -> dict:
    """
    Verifie la qualite des donnees nettoyees.
    
    Args:
        df: DataFrame nettoye
        
    Returns:
        Dictionnaire avec les metriques de qualite
    """
    print("\nVerification de la qualite des donnees...")
    
    metrics = {}
    
    # Verification du champ RAG
    textes_invalides = (df['text_for_rag'].isna() | (df['text_for_rag'].str.len() < 20)).sum()
    textes_valides = len(df) - textes_invalides
    metrics['text_for_rag_valides'] = textes_valides
    metrics['text_for_rag_invalides'] = textes_invalides
    print(f"  Textes RAG valides: {textes_valides:,}/{len(df):,}")
    
    # Verification des champs essentiels
    champs_essentiels = ['title_fr', 'description_fr', 'firstdate_begin', 'location_city']
    for nom_champ in champs_essentiels:
        valeurs_manquantes = df[nom_champ].isna().sum()
        valeurs_valides = len(df) - valeurs_manquantes
        pourcentage = (valeurs_valides / len(df)) * 100
        metrics[f'{nom_champ}_completude'] = pourcentage
        print(f"  {nom_champ}: {pourcentage:.1f}% complet")
    
    # Verification HTML
    if 'longdescription_fr' in df.columns:
        html_restant = df['longdescription_fr'].fillna('').str.contains('<[^>]+>', regex=True).sum()
        metrics['html_restant'] = html_restant
        print(f"  Balises HTML restantes: {html_restant}")
    
    print("  [OK] Verification terminee")
    
    return metrics


def save_cleaned_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Sauvegarde les donnees nettoyees au format Parquet.
    
    Args:
        df: DataFrame nettoye
        output_path: Chemin du fichier de sortie
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nSauvegarde des donnees nettoyees...")
    df.to_parquet(output_file, index=False)
    
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"  Fichier: {output_file}")
    print(f"  Taille: {file_size:.2f} MB")
    print(f"  Lignes: {len(df):,}")
    print(f"  Colonnes: {len(df.columns)}")
    print("  [OK] Sauvegarde terminee")


def main():
    """
    Fonction principale du script de nettoyage.
    """
    print("="*70)
    print("NETTOYAGE DES DONNEES OPEN AGENDA")
    print("="*70)
    
    # Configuration des chemins
    raw_data_path = "data/RAW/evenements-publics-openagenda.parquet"
    processed_data_path = "data/processed/evenements_occitanie_clean.parquet"
    
    # Execution du pipeline de nettoyage
    try:
        # 1. Chargement
        df = load_raw_data(raw_data_path)
        
        # 2. Filtrage geographique et temporel
        df_filtered = filter_by_region_and_time(df, region="Occitanie")
        
        # 3. Suppression des colonnes vides
        df_clean = remove_empty_columns(df_filtered)
        
        # 4. Nettoyage HTML
        df_clean = clean_html_descriptions(df_clean)
        
        # 5. Creation du champ RAG
        df_clean = create_rag_text_field(df_clean)
        
        # 6. Verification de la qualite
        metrics = verify_data_quality(df_clean)
        
        # 7. Sauvegarde
        save_cleaned_data(df_clean, processed_data_path)
        
        print("\n" + "="*70)
        print("NETTOYAGE TERMINE AVEC SUCCES")
        print("="*70)
        
        return df_clean, metrics
        
    except Exception as e:
        print(f"\nERREUR: {str(e)}")
        raise


if __name__ == "__main__":
    df_clean, metrics = main()
