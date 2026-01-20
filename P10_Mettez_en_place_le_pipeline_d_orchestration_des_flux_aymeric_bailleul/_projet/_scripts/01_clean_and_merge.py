"""
Script       : 01_clean_and_merge.py
Description  : Nettoyage et fusion des donnees (traitement local)
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-20
Version      : 1.0 - Traitement local

Objectif     : 
  1. Lire les 3 fichiers sources locaux (dossier sources/)
  2. Nettoyer les données ERP, LIAISON et WEB
  3. Fusionner les 3 sources via jointures
  4. Stocker la table merged_data_final dans DuckDB

Résultat     : Table merged_data_final (714 lignes) dans DuckDB
"""

import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import sys

# Paths
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"

# Créer les répertoires si nécessaire
sources_path.mkdir(exist_ok=True)
db_path.parent.mkdir(exist_ok=True)

print("=" * 80)
print("PIPELINE BOTTLENECK - PHASE 1 : NETTOYAGE ET FUSION")
print("=" * 80)
print(f"Date d'execution : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base de donnees  : {db_path}")
print(f"Dossier sources  : {sources_path}")

# ============================================================================
# ÉTAPE 1 : VÉRIFICATION DES FICHIERS SOURCES
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 1/3 : VERIFICATION DES FICHIERS SOURCES")
print("-" * 80)

# Vérification de l'existence des fichiers sources
fichiers_requis = [
    ("fichier_erp.xlsx", "ERP"),
    ("fichier_liaison.xlsx", "LIAISON"),
    ("fichier_web.xlsx", "WEB")
]

fichiers_manquants = []
for filename, label in fichiers_requis:
    file_path = sources_path / filename
    if file_path.exists():
        file_size = file_path.stat().st_size / 1024  # KB
        print(f"  [OK] {label}: {filename} ({file_size:.2f} KB)")
    else:
        fichiers_manquants.append(f"{label}: {filename}")

if fichiers_manquants:
    print(f"\n[ERREUR] Fichiers manquants dans {sources_path}:")
    for f in fichiers_manquants:
        print(f"  - {f}")
    sys.exit(1)

print("\n[OK] Tous les fichiers sources sont presents")

# ============================================================================
# ÉTAPE 2 : NETTOYAGE DES DONNÉES
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 2/3 : NETTOYAGE DES DONNEES")
print("-" * 80)

# Connexion DuckDB
conn = duckdb.connect(str(db_path))
print(f"[OK] Connexion DuckDB etablie")

# --- NETTOYAGE ERP ---
print("\n[2.1] Nettoyage ERP")
fichier_erp = sources_path / "fichier_erp.xlsx"
erp_raw = pd.read_excel(fichier_erp)
print(f"  Lignes chargées : {len(erp_raw)}")

# Statistiques brutes
nb_null_erp = erp_raw.isna().sum().sum()
nb_duplicates_erp = erp_raw.duplicated().sum()
print(f"  Valeurs manquantes : {nb_null_erp}")
print(f"  Doublons : {nb_duplicates_erp}")

# Nettoyage
erp_clean = erp_raw.dropna().drop_duplicates()

# Renommer les colonnes pour éviter les conflits
erp_clean = erp_clean.rename(columns={
    'price': 'erp_price'
})

print(f"  [OK] Apres nettoyage : {len(erp_clean)} lignes")

# Stockage dans DuckDB
conn.execute("DROP TABLE IF EXISTS erp_clean_final")
conn.execute("CREATE TABLE erp_clean_final AS SELECT * FROM erp_clean")
print(f"  [OK] Table erp_clean_final creee")

# --- NETTOYAGE LIAISON ---
print("\n[2.2] Nettoyage LIAISON")
fichier_liaison = sources_path / "fichier_liaison.xlsx"
liaison_raw = pd.read_excel(fichier_liaison)
print(f"  Lignes chargées : {len(liaison_raw)}")

# Statistiques brutes (on garde les NULL sur id_web)
nb_null_id_web = liaison_raw['id_web'].isna().sum()
nb_duplicates_liaison = liaison_raw.duplicated().sum()
print(f"  NULL sur id_web : {nb_null_id_web} (conservés volontairement)")
print(f"  Doublons : {nb_duplicates_liaison}")

# Nettoyage (seulement dédoublonnage, on garde les NULL sur id_web)
liaison_clean = liaison_raw.drop_duplicates()
print(f"  [OK] Apres nettoyage : {len(liaison_clean)} lignes")

# Stockage dans DuckDB
conn.execute("DROP TABLE IF EXISTS liaison_clean_final")
conn.execute("CREATE TABLE liaison_clean_final AS SELECT * FROM liaison_clean")
print(f"  [OK] Table liaison_clean_final creee")

# --- NETTOYAGE WEB ---
print("\n[2.3] Nettoyage WEB")
fichier_web = sources_path / "fichier_web.xlsx"
web_raw = pd.read_excel(fichier_web)
print(f"  Lignes chargées : {len(web_raw)}")

# Statistiques brutes
nb_total = len(web_raw)
nb_products = len(web_raw[web_raw['post_type'] == 'product'])
print(f"  Lignes avec post_type='product' : {nb_products}/{nb_total}")

# Filtrage sur post_type = 'product'
web_filtered = web_raw[web_raw['post_type'] == 'product'].copy()

# Suppression des NULL sur sku
nb_null_sku = web_filtered['sku'].isna().sum()
print(f"  NULL sur sku : {nb_null_sku}")
web_no_null = web_filtered.dropna(subset=['sku'])

# Dédoublonnage intelligent (garder les lignes avec le plus de ventes)
web_no_null_sorted = web_no_null.sort_values('total_sales', ascending=False)
web_clean = web_no_null_sorted.drop_duplicates(subset=['sku'], keep='first')
print(f"  [OK] Apres nettoyage : {len(web_clean)} lignes")

# Stockage dans DuckDB
conn.execute("DROP TABLE IF EXISTS web_clean_final")
conn.execute("CREATE TABLE web_clean_final AS SELECT * FROM web_clean")
print(f"  [OK] Table web_clean_final creee")

# ============================================================================
# ÉTAPE 3 : FUSION ET STOCKAGE
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 3/3 : FUSION ET STOCKAGE DES DONNEES")
print("-" * 80)

# Lecture des tables nettoyées
erp_df = conn.execute("SELECT * FROM erp_clean_final").df()
liaison_df = conn.execute("SELECT * FROM liaison_clean_final").df()
web_df = conn.execute("SELECT * FROM web_clean_final").df()

# Jointure 1 : ERP + LIAISON
print("\n[3.1] Jointure ERP + LIAISON sur product_id")
merged_1 = pd.merge(
    erp_df,
    liaison_df,
    on='product_id',
    how='left'
)
print(f"  Résultat jointure : {len(merged_1)} lignes")

# Filtrage : suppression des id_web NULL
print("\n[3.2] Suppression des lignes avec id_web NULL")
nb_null = merged_1['id_web'].isna().sum()
print(f"  Lignes avec id_web NULL : {nb_null}")
merged_1_filtered = merged_1.dropna(subset=['id_web'])
print(f"  [OK] Apres filtrage : {len(merged_1_filtered)} lignes")

# Jointure 2 : (ERP+LIAISON) + WEB
print("\n[3.3] Jointure (ERP+LIAISON) + WEB sur id_web = sku")
merged_final = pd.merge(
    merged_1_filtered,
    web_df,
    left_on='id_web',
    right_on='sku',
    how='inner'  # Changed from 'left' to 'inner' to avoid NULL total_sales
)
print(f"  Résultat jointure finale : {len(merged_final)} lignes")

# Vérification et suppression des NULL sur total_sales (sécurité)
print("\n[3.4] Nettoyage final des données")
nb_null_before = merged_final['total_sales'].isna().sum()
if nb_null_before > 0:
    print(f"  Suppression de {nb_null_before} lignes avec total_sales NULL")
    merged_final = merged_final.dropna(subset=['total_sales'])
    print(f"  [OK] Apres nettoyage : {len(merged_final)} lignes")
else:
    print(f"  [OK] Aucune valeur NULL sur total_sales")

# Vérification des colonnes essentielles
essential_cols = ['product_id', 'erp_price', 'total_sales']
all_ok = True
for col in essential_cols:
    nb_null = merged_final[col].isna().sum()
    if nb_null > 0:
        print(f"  [ATTENTION] : {nb_null} valeurs NULL sur {col}")
        all_ok = False

if all_ok:
    print(f"[OK] Fusion terminee : {len(merged_final)} lignes propres avec toutes les colonnes essentielles")

# Stockage dans DuckDB
print("\n[3.5] Stockage dans DuckDB")
conn.execute("DROP TABLE IF EXISTS merged_data_final")
conn.execute("CREATE TABLE merged_data_final AS SELECT * FROM merged_final")

# Vérification
count_final = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
print(f"[OK] Table merged_data_final creee : {count_final} lignes")

# ============================================================================
# RÉCAPITULATIF
# ============================================================================
print("\n" + "=" * 80)
print("RECAPITULATIF PHASE 1")
print("=" * 80)
print(f"[OK] ERP nettoye     : {len(erp_clean)} lignes")
print(f"[OK] LIAISON nettoye : {len(liaison_clean)} lignes")
print(f"[OK] WEB nettoye     : {len(web_clean)} lignes")
print(f"[OK] Donnees fusionnees : {count_final} lignes")
print(f"[OK] Table DuckDB    : merged_data_final")
print(f"[OK] Base de donnees : {db_path}")
print("=" * 80)
print("[OK] PHASE 1 TERMINEE AVEC SUCCES")
print("=" * 80)

conn.close()
