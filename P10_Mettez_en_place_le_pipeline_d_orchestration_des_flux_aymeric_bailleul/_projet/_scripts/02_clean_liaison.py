"""
Script       : 02_clean_liaison.py
Description  : Nettoyage des donnees du fichier LIAISON
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, nettoyer et dedoublonner les donnees LIAISON
Resultat     : 825 lignes propres (NULL sur id_web conserves)
"""

import pandas as pd
import duckdb
from pathlib import Path

# Paths
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_liaison = sources_path / "fichier_liaison.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNEES LIAISON")
print("=" * 80)

# Connexion a DuckDB persistante
print(f"Base de donnees : {db_path}")
conn = duckdb.connect(str(db_path))

# Etape 1 : Chargement du fichier Excel LIAISON avec pandas
print("\nEtape 1 : Chargement du fichier LIAISON...")
liaison_raw = pd.read_excel(fichier_liaison)
print(f"  Nombre de lignes chargees : {len(liaison_raw)}")
print(f"  Colonnes : {list(liaison_raw.columns)}")

# Affichage de quelques statistiques sur les donnees brutes
print("\n  Valeurs manquantes par colonne :")
for col in liaison_raw.columns:
    nb_null = liaison_raw[col].isna().sum()
    if nb_null > 0:
        print(f"    - {col} : {nb_null} ({nb_null/len(liaison_raw)*100:.1f}%)")
    else:
        print(f"    - {col} : 0")
print(f"  Nombre de doublons complets : {liaison_raw.duplicated().sum()}")

# Etape 2 : suppression des valeurs manquantes UNIQUEMENT sur product_id
# IMPORTANT : on conserve les lignes avec id_web NULL
print("\nEtape 2 : suppression des valeurs manquantes sur product_id uniquement...")
print("  ATTENTION : les valeurs NULL sur id_web sont CONSERVEES")
print("  Ces lignes representent des produits ERP non encore references sur le web")
liaison_sans_null = liaison_raw.dropna(subset=['product_id'])
print(f"  Nombre de lignes apres suppression : {len(liaison_sans_null)}")
nb_null_id_web = liaison_sans_null['id_web'].isna().sum()
print(f"  Nombre de NULL conserves sur id_web : {nb_null_id_web}")

# Etape 3 : dedoublonnage des donnees
print("\nEtape 3 : dedoublonnage des donnees...")
nb_doublons_avant = liaison_sans_null.duplicated().sum()
print(f"  Nombre de doublons detectes : {nb_doublons_avant}")
liaison_clean = liaison_sans_null.drop_duplicates()
print(f"  Nombre de lignes apres dedoublonnage : {len(liaison_clean)}")
print(f"  Nombre de product_id uniques : {liaison_clean['product_id'].nunique()}")

# Verification que product_id est bien une cle primaire
doublons_product_id = liaison_clean['product_id'].duplicated().sum()
if doublons_product_id > 0:
    print(f"  ATTENTION : {doublons_product_id} doublons sur product_id detectes !")
else:
    print("  Verification OK : product_id est une cle primaire unique")

# Statistiques sur id_web
print("\n  Statistiques sur id_web :")
nb_produits_avec_web = liaison_clean['id_web'].notna().sum()
nb_produits_sans_web = liaison_clean['id_web'].isna().sum()
print(f"    - Produits AVEC reference web : {nb_produits_avec_web}")
print(f"    - Produits SANS reference web : {nb_produits_sans_web}")

# Etape 4 : insertion dans DuckDB pour utilisation ulterieure
print("\nEtape 4 : creation de la table dans DuckDB...")
conn.register('liaison_clean', liaison_clean)
conn.execute("CREATE OR REPLACE TABLE liaison_clean_final AS SELECT * FROM liaison_clean")
print("  Table liaison_clean_final creee avec succes")

# Affichage des resultats
print("\n" + "=" * 80)
print("RESULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(liaison_clean)}")
print(f"Resultat attendu : 825 lignes")
print(f"Statut : {'OK' if len(liaison_clean) == 825 else 'ATTENTION - ecart detecte'}")

print("\nExemples de lignes AVEC reference web :")
print(liaison_clean[liaison_clean['id_web'].notna()].head(3))

print("\nExemples de lignes SANS reference web (NULL conserves) :")
print(liaison_clean[liaison_clean['id_web'].isna()].head(3))

# Fermeture de la connexion
conn.close()
print("\nDonnees LIAISON disponibles dans la table 'liaison_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE LIAISON TERMINE")
print("=" * 80)
