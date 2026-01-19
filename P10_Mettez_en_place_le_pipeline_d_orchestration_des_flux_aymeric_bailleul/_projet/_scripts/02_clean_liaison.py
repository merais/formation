"""
Script       : 02_clean_liaison.py
Description  : Nettoyage des données du fichier LIAISON
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, nettoyer et dédoublonner les données LIAISON
Résultat     : 825 lignes propres (NULL sur id_web conservés)
"""

import pandas as pd
import duckdb
from pathlib import Path

# Chemins
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_liaison = sources_path / "fichier_liaison.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNÉES LIAISON")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {db_path}")
conn = duckdb.connect(str(db_path))

# Étape 1 : Chargement du fichier Excel LIAISON avec pandas
print("\nÉtape 1 : Chargement du fichier LIAISON...")
liaison_raw = pd.read_excel(fichier_liaison)
print(f"  Nombre de lignes chargées : {len(liaison_raw)}")
print(f"  Colonnes : {list(liaison_raw.columns)}")

# Affichage de quelques statistiques sur les données brutes
print("\n  Valeurs manquantes par colonne :")
for col in liaison_raw.columns:
    nb_null = liaison_raw[col].isna().sum()
    if nb_null > 0:
        print(f"    - {col} : {nb_null} ({nb_null/len(liaison_raw)*100:.1f}%)")
    else:
        print(f"    - {col} : 0")
print(f"  Nombre de doublons complets : {liaison_raw.duplicated().sum()}")

# Étape 2 : Suppression des valeurs manquantes UNIQUEMENT sur product_id
# IMPORTANT : On conserve les lignes avec id_web NULL
print("\nÉtape 2 : Suppression des valeurs manquantes sur product_id uniquement...")
print("  ATTENTION : Les valeurs NULL sur id_web sont CONSERVÉES")
print("  Ces lignes représentent des produits ERP non encore référencés sur le web")
liaison_sans_null = liaison_raw.dropna(subset=['product_id'])
print(f"  Nombre de lignes après suppression : {len(liaison_sans_null)}")
nb_null_id_web = liaison_sans_null['id_web'].isna().sum()
print(f"  Nombre de NULL conservés sur id_web : {nb_null_id_web}")

# Étape 3 : Dédoublonnage des données
print("\nÉtape 3 : Dédoublonnage des données...")
nb_doublons_avant = liaison_sans_null.duplicated().sum()
print(f"  Nombre de doublons détectés : {nb_doublons_avant}")
liaison_clean = liaison_sans_null.drop_duplicates()
print(f"  Nombre de lignes après dédoublonnage : {len(liaison_clean)}")
print(f"  Nombre de product_id uniques : {liaison_clean['product_id'].nunique()}")

# Vérification que product_id est bien une clé primaire
doublons_product_id = liaison_clean['product_id'].duplicated().sum()
if doublons_product_id > 0:
    print(f"  ATTENTION : {doublons_product_id} doublons sur product_id détectés !")
else:
    print("  Vérification OK : product_id est une clé primaire unique")

# Statistiques sur id_web
print("\n  Statistiques sur id_web :")
nb_produits_avec_web = liaison_clean['id_web'].notna().sum()
nb_produits_sans_web = liaison_clean['id_web'].isna().sum()
print(f"    - Produits AVEC référence web : {nb_produits_avec_web}")
print(f"    - Produits SANS référence web : {nb_produits_sans_web}")

# Étape 4 : Insertion dans DuckDB pour utilisation ultérieure
print("\nÉtape 4 : Création de la table dans DuckDB...")
conn.register('liaison_clean', liaison_clean)
conn.execute("CREATE OR REPLACE TABLE liaison_clean_final AS SELECT * FROM liaison_clean")
print("  Table liaison_clean_final créée avec succès")

# Affichage des résultats
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(liaison_clean)}")
print(f"Résultat attendu : 825 lignes")
print(f"Statut : {'OK' if len(liaison_clean) == 825 else 'ATTENTION - Écart détecté'}")

print("\nExemples de lignes AVEC référence web :")
print(liaison_clean[liaison_clean['id_web'].notna()].head(3))

print("\nExemples de lignes SANS référence web (NULL conservés) :")
print(liaison_clean[liaison_clean['id_web'].isna()].head(3))

# Fermeture de la connexion
conn.close()
print("\nDonnées LIAISON disponibles dans la table 'liaison_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE LIAISON TERMINÉ")
print("=" * 80)
