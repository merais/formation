"""
Tests unitaires pour le module de pre-processing.

Teste les fonctions de nettoyage et de structuration des donnees
Open Agenda.

Auteur: Aymeric Bailleul
Date: 09/02/2026
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta
import sys

# Ajout du chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessing.clean_data import (
    load_raw_data,
    filter_by_region_and_time,
    remove_empty_columns,
    clean_html,
    clean_html_descriptions,
    create_rag_text_field,
    verify_data_quality,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """
    Cree un DataFrame de test avec des donnees representatives.
    """
    today = pd.Timestamp.now(tz='Europe/Paris')
    
    data = {
        'title_fr': ['Evenement 1', 'Evenement 2', 'Evenement 3', 'Evenement 4'],
        'description_fr': ['Description 1', 'Description 2', 'Description 3', 'Description 4'],
        'longdescription_fr': [
            '<p>Longue description avec <strong>HTML</strong></p>',
            'Description simple sans HTML',
            '<div>HTML &eacute;galement</div>',
            None
        ],
        'keywords_fr': ['mot1, mot2', 'mot3', None, 'mot4'],
        'location_city': ['Toulouse', 'Montpellier', 'Perpignan', 'Toulouse'],
        'location_region': ['Occitanie', 'Occitanie', 'Occitanie', 'Nouvelle-Aquitaine'],
        'firstdate_begin': [
            today - timedelta(days=30),
            today + timedelta(days=10),
            today - timedelta(days=400),  # Plus d'1 an
            today - timedelta(days=180)
        ],
        'empty_col_1': [None, None, None, None],
        'empty_col_2': [np.nan, np.nan, np.nan, np.nan]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def cleaned_dataframe(sample_dataframe):
    """
    DataFrame nettoye pour tests.
    """
    df = sample_dataframe.copy()
    df = filter_by_region_and_time(df, region="Occitanie")
    df = remove_empty_columns(df)
    df = clean_html_descriptions(df)
    df = create_rag_text_field(df)
    return df


# ============================================================================
# TESTS - FILTRAGE GEOGRAPHIQUE
# ============================================================================

def test_filter_by_region_occitanie(sample_dataframe):
    """
    Test: Verifie que seuls les evenements d'Occitanie sont conserves.
    """
    df_filtered = filter_by_region_and_time(sample_dataframe, region="Occitanie")
    
    # Verification: tous les evenements doivent etre en Occitanie
    assert all(df_filtered['location_region'].str.contains('Occitanie', case=False, na=False))
    
    # Verification: au moins un evenement est exclu (Nouvelle-Aquitaine)
    assert len(df_filtered) < len(sample_dataframe)


def test_filter_by_region_case_insensitive(sample_dataframe):
    """
    Test: Verifie que le filtrage geographique est insensible a la casse.
    """
    df_lower = filter_by_region_and_time(sample_dataframe, region="occitanie")
    df_upper = filter_by_region_and_time(sample_dataframe, region="OCCITANIE")
    df_mixed = filter_by_region_and_time(sample_dataframe, region="Occitanie")
    
    # Tous les filtrages doivent donner le meme resultat
    assert len(df_lower) == len(df_upper) == len(df_mixed)


# ============================================================================
# TESTS - FILTRAGE TEMPOREL
# ============================================================================

def test_filter_by_time_past_year(sample_dataframe):
    """
    Test: Verifie que les evenements de plus d'un an sont exclus.
    """
    df_filtered = filter_by_region_and_time(sample_dataframe, region="Occitanie")
    
    today = pd.Timestamp.now(tz='Europe/Paris')
    one_year_ago = today - timedelta(days=365)
    
    # Tous les evenements doivent etre dans la periode valide
    for date in df_filtered['firstdate_begin']:
        # Soit passe recent (moins d'1 an), soit futur
        assert date >= one_year_ago or date >= today


def test_filter_by_time_future_events(sample_dataframe):
    """
    Test: Verifie que tous les evenements futurs sont conserves.
    """
    df_filtered = filter_by_region_and_time(sample_dataframe, region="Occitanie")
    
    today = pd.Timestamp.now(tz='Europe/Paris')
    
    # Compter les evenements futurs dans le DataFrame filtre
    future_events_filtered = df_filtered[df_filtered['firstdate_begin'] >= today]
    
    # Compter les evenements futurs Occitanie dans le DataFrame original
    future_events_original = sample_dataframe[
        (sample_dataframe['firstdate_begin'] >= today) & 
        (sample_dataframe['location_region'].str.contains('Occitanie', case=False, na=False))
    ]
    
    # Tous les evenements futurs d'Occitanie doivent etre conserves
    assert len(future_events_filtered) == len(future_events_original)


# ============================================================================
# TESTS - SUPPRESSION DES COLONNES VIDES
# ============================================================================

def test_remove_empty_columns_removes_all_empty(sample_dataframe):
    """
    Test: Verifie que toutes les colonnes vides sont supprimees.
    """
    df_clean = remove_empty_columns(sample_dataframe)
    
    # Verifier qu'aucune colonne n'est completement vide
    for col in df_clean.columns:
        assert df_clean[col].notna().sum() > 0


def test_remove_empty_columns_preserves_data(sample_dataframe):
    """
    Test: Verifie que les colonnes avec donnees sont conservees.
    """
    df_clean = remove_empty_columns(sample_dataframe)
    
    # Les colonnes importantes doivent etre conservees
    assert 'title_fr' in df_clean.columns
    assert 'description_fr' in df_clean.columns
    assert 'location_city' in df_clean.columns
    
    # Les colonnes vides doivent etre supprimees
    assert 'empty_col_1' not in df_clean.columns
    assert 'empty_col_2' not in df_clean.columns


# ============================================================================
# TESTS - NETTOYAGE HTML
# ============================================================================

def test_clean_html_removes_tags():
    """
    Test: Verifie que les balises HTML sont supprimees.
    """
    html_text = "<p>Texte avec <strong>HTML</strong> et <a href='#'>lien</a></p>"
    clean_text = clean_html(html_text)
    
    # Aucune balise HTML ne doit rester
    assert '<' not in clean_text
    assert '>' not in clean_text
    assert 'Texte avec HTML et lien' in clean_text


def test_clean_html_decodes_entities():
    """
    Test: Verifie que les entites HTML sont decodees.
    """
    html_text = "Texte avec &eacute;l&eacute;ments sp&eacute;ciaux &amp; symboles"
    clean_text = clean_html(html_text)
    
    # Les entites doivent etre decodees
    assert '&eacute;' not in clean_text
    assert '&amp;' not in clean_text
    assert 'é' in clean_text
    assert '&' in clean_text


def test_clean_html_handles_none():
    """
    Test: Verifie que la fonction gere les valeurs None.
    """
    result = clean_html(None)
    assert pd.isna(result)


def test_clean_html_descriptions_removes_all_html(sample_dataframe):
    """
    Test: Verifie que tout le HTML est supprime de longdescription_fr.
    """
    df_clean = clean_html_descriptions(sample_dataframe.copy())
    
    # Compter les balises HTML restantes
    html_count = df_clean['longdescription_fr'].fillna('').str.contains('<[^>]+>', regex=True).sum()
    
    assert html_count == 0, "Des balises HTML sont encore presentes"


# ============================================================================
# TESTS - CREATION DU CHAMP RAG
# ============================================================================

def test_create_rag_text_field_creates_column(sample_dataframe):
    """
    Test: Verifie que la colonne text_for_rag est creee.
    """
    df = create_rag_text_field(sample_dataframe.copy())
    
    assert 'text_for_rag' in df.columns


def test_create_rag_text_field_not_empty(cleaned_dataframe):
    """
    Test: Verifie que le champ text_for_rag n'est pas vide.
    """
    # Tous les textes doivent avoir une longueur minimale
    assert all(cleaned_dataframe['text_for_rag'].str.len() > 20)


def test_create_rag_text_field_contains_title(sample_dataframe):
    """
    Test: Verifie que le titre est inclus dans text_for_rag.
    """
    df = create_rag_text_field(sample_dataframe.copy())
    
    # Verifier que le titre apparait dans le texte RAG
    for idx, row in df.iterrows():
        if pd.notna(row['title_fr']):
            assert row['title_fr'] in row['text_for_rag']


def test_create_rag_text_field_contains_description(sample_dataframe):
    """
    Test: Verifie que la description est incluse dans text_for_rag.
    """
    df = create_rag_text_field(sample_dataframe.copy())
    
    # Verifier que la description apparait dans le texte RAG
    for idx, row in df.iterrows():
        if pd.notna(row['description_fr']):
            assert row['description_fr'] in row['text_for_rag']


# ============================================================================
# TESTS - VERIFICATION DE LA QUALITE
# ============================================================================

def test_verify_data_quality_returns_metrics(cleaned_dataframe):
    """
    Test: Verifie que verify_data_quality retourne des metriques.
    """
    metrics = verify_data_quality(cleaned_dataframe)
    
    # Les metriques doivent etre presentes
    assert isinstance(metrics, dict)
    assert 'text_for_rag_valides' in metrics
    assert 'text_for_rag_invalides' in metrics


def test_verify_data_quality_text_for_rag_validity(cleaned_dataframe):
    """
    Test: Verifie que la plupart des textes RAG sont valides.
    """
    metrics = verify_data_quality(cleaned_dataframe)
    
    total = metrics['text_for_rag_valides'] + metrics['text_for_rag_invalides']
    pourcentage_valides = (metrics['text_for_rag_valides'] / total) * 100
    
    # Au moins 80% des textes doivent etre valides
    assert pourcentage_valides >= 80.0


def test_verify_data_quality_essential_fields(cleaned_dataframe):
    """
    Test: Verifie la completude des champs essentiels.
    """
    metrics = verify_data_quality(cleaned_dataframe)
    
    # Les champs essentiels doivent avoir une bonne completude
    assert metrics['title_fr_completude'] >= 90.0
    assert metrics['description_fr_completude'] >= 80.0
    assert metrics['firstdate_begin_completude'] == 100.0


def test_verify_data_quality_no_html_remains(cleaned_dataframe):
    """
    Test: Verifie qu'il ne reste pas de HTML apres nettoyage.
    """
    metrics = verify_data_quality(cleaned_dataframe)
    
    if 'html_restant' in metrics:
        assert metrics['html_restant'] == 0


# ============================================================================
# TESTS - CHARGEMENT DES DONNEES
# ============================================================================

def test_load_raw_data_file_not_found():
    """
    Test: Verifie que FileNotFoundError est levee si le fichier n'existe pas.
    """
    with pytest.raises(FileNotFoundError):
        load_raw_data("fichier_inexistant.parquet")


def test_load_raw_data_returns_dataframe():
    """
    Test: Verifie que load_raw_data retourne un DataFrame.
    
    Note: Ce test necessite le fichier reel.
    """
    data_path = Path("data/RAW/evenements-publics-openagenda.parquet")
    
    if data_path.exists():
        df = load_raw_data(str(data_path))
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    else:
        pytest.skip("Fichier de donnees non disponible")


# ============================================================================
# TESTS D'INTEGRATION
# ============================================================================

def test_full_pipeline_with_sample_data(sample_dataframe):
    """
    Test d'integration: Execute le pipeline complet sur des donnees de test.
    """
    # Pipeline complet
    df = sample_dataframe.copy()
    df = filter_by_region_and_time(df, region="Occitanie")
    df = remove_empty_columns(df)
    df = clean_html_descriptions(df)
    df = create_rag_text_field(df)
    metrics = verify_data_quality(df)
    
    # Verifications finales
    assert len(df) > 0, "Le DataFrame ne doit pas etre vide"
    assert 'text_for_rag' in df.columns, "Le champ text_for_rag doit exister"
    assert 'empty_col_1' not in df.columns, "Les colonnes vides doivent etre supprimees"
    assert all(df['location_region'].str.contains('Occitanie', case=False, na=False))
    assert isinstance(metrics, dict), "Les metriques doivent etre retournees"


def test_real_data_pipeline_if_available():
    """
    Test d'integration sur les donnees reelles si disponibles.
    
    Ce test execute le pipeline complet sur le fichier reel et verifie
    que le fichier nettoye est bien genere.
    """
    raw_path = Path("data/RAW/evenements-publics-openagenda.parquet")
    processed_path = Path("data/processed/evenements_occitanie_clean.parquet")
    
    if not raw_path.exists():
        pytest.skip("Fichier de donnees brutes non disponible")
    
    # Charger et verifier le fichier nettoye
    if processed_path.exists():
        df_clean = pd.read_parquet(processed_path)
        
        # Verifications
        assert len(df_clean) > 0, "Le DataFrame nettoye ne doit pas etre vide"
        assert 'text_for_rag' in df_clean.columns
        assert all(df_clean['location_region'].str.contains('Occitanie', case=False, na=False))
        
        # Verification temporelle: le fichier clean a ete cree avec une logique de
        # 1 an en arriere + futurs. Verifions simplement qu'il n'y a pas d'evenements
        # tres anciens (plus de 2 ans) ni trop eloignes dans le futur (plus de 10 ans)
        today = pd.Timestamp.now(tz='Europe/Paris')
        two_years_ago = today - timedelta(days=730)
        ten_years_future = today + timedelta(days=3650)
        
        dates_min = df_clean['firstdate_begin'].min()
        dates_max = df_clean['firstdate_begin'].max()
        
        assert dates_min >= two_years_ago, \
            f"Des evenements trop anciens sont presents: {dates_min}"
        assert dates_max <= ten_years_future, \
            f"Des evenements trop eloignes dans le futur: {dates_max}"
        
        print(f"\n✓ Test sur donnees reelles: {len(df_clean):,} evenements valides")
    else:
        pytest.skip("Fichier de donnees nettoyees non disponible")


# ============================================================================
# EXECUTION DES TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
