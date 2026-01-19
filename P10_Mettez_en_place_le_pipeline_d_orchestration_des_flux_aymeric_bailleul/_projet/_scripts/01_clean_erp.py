"""
Script       : 01_clean_erp.py
Description  : Nettoyage des donnees du fichier ERP
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, nettoyer et dedoublonner les donnees ERP
Resultat     : 825 lignes propres
"""

import pandas as pd
import duckdb
from pathlib import Path

# Paths
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_erp = sources_path / "fichier_erp.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNEES ERP")
print("=" * 80)

# Connexion a DuckDB persistante
print(f"Base de donnees : {db_path}")
conn = duckdb.connect(str(db_path))

# Etape 1 : Chargement du fichier Excel ERP avec pandas
print("\nEtape 1 : Chargement du fichier ERP...")
erp_raw = pd.read_excel(fichier_erp)
print(f"  Nombre de lignes chargees : {len(erp_raw)}")
print(f"  Colonnes : {list(erp_raw.columns)}")

# Affichage de quelques statistiques sur les donnees brutes
print("\n  Valeurs manquantes par colonne :")
for col in erp_raw.columns:
    nb_null = erp_raw[col].isna().sum()
    if nb_null > 0:
        print(f"    - {col} : {nb_null}")
print(f"  Nombre de doublons complets : {erp_raw.duplicated().sum()}")

# Etape 2 : suppression des valeurs manquantes
print("\nEtape 2 : suppression des valeurs manquantes...")
erp_sans_null = erp_raw.dropna()
print(f"  Nombre de lignes apres suppression : {len(erp_sans_null)}")

# Etape 3 : dedoublonnage complet
print("\nEtape 3 : dedoublonnage des donnees...")
erp_clean = erp_sans_null.drop_duplicates()
print(f"  Nombre de lignes apres dedoublonnage : {len(erp_clean)}")
print(f"  Nombre de product_id uniques : {erp_clean['product_id'].nunique()}")

# Verification que product_id est bien une cle primaire
doublons_product_id = erp_clean['product_id'].duplicated().sum()
if doublons_product_id > 0:
    print(f"  ATTENTION : {doublons_product_id} doublons sur product_id detectes !")
else:
    print("  Verification OK : product_id est une cle primaire unique")

# Etape 4 : insertion dans DuckDB pour utilisation ulterieure
print("\nEtape 4 : creation de la table dans DuckDB...")
conn.register('erp_clean', erp_clean)
conn.execute("CREATE OR REPLACE TABLE erp_clean_final AS SELECT * FROM erp_clean")
print("  Table erp_clean_final creee avec succes")

# Affichage des premieres lignes
print("\n" + "=" * 80)
print("RESULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(erp_clean)}")
print(f"Resultat attendu : 825 lignes")
print(f"Statut : {'OK' if len(erp_clean) == 825 else 'ATTENTION - Ecart detecte'}")

print("\nPremieres lignes du fichier nettoye :")
print(erp_clean.head())

print("\nStatistiques sur les prix :")
print(erp_clean['price'].describe())

# Fermeture de la connexion
conn.close()
print("\nDonnees ERP disponibles dans la table 'erp_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE ERP TERMINE")
print("=" * 80)
