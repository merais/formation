"""
Script       : 01_clean_erp.py
Description  : Nettoyage des données du fichier ERP
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, nettoyer et dédoublonner les données ERP
Résultat     : 825 lignes propres
"""

import pandas as pd
import duckdb
from pathlib import Path

# Chemins
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_erp = sources_path / "fichier_erp.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNÉES ERP")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {db_path}")
conn = duckdb.connect(str(db_path))

# Étape 1 : Chargement du fichier Excel ERP avec pandas
print("\nÉtape 1 : Chargement du fichier ERP...")
erp_raw = pd.read_excel(fichier_erp)
print(f"  Nombre de lignes chargées : {len(erp_raw)}")
print(f"  Colonnes : {list(erp_raw.columns)}")

# Affichage de quelques statistiques sur les données brutes
print("\n  Valeurs manquantes par colonne :")
for col in erp_raw.columns:
    nb_null = erp_raw[col].isna().sum()
    if nb_null > 0:
        print(f"    - {col} : {nb_null}")
print(f"  Nombre de doublons complets : {erp_raw.duplicated().sum()}")

# Étape 2 : Suppression des valeurs manquantes
print("\nÉtape 2 : Suppression des valeurs manquantes...")
erp_sans_null = erp_raw.dropna()
print(f"  Nombre de lignes après suppression : {len(erp_sans_null)}")

# Étape 3 : Dédoublonnage complet
print("\nÉtape 3 : Dédoublonnage des données...")
erp_clean = erp_sans_null.drop_duplicates()
print(f"  Nombre de lignes après dédoublonnage : {len(erp_clean)}")
print(f"  Nombre de product_id uniques : {erp_clean['product_id'].nunique()}")

# Vérification que product_id est bien une clé primaire
doublons_product_id = erp_clean['product_id'].duplicated().sum()
if doublons_product_id > 0:
    print(f"  ATTENTION : {doublons_product_id} doublons sur product_id détectés !")
else:
    print("  Vérification OK : product_id est une clé primaire unique")

# Étape 4 : Insertion dans DuckDB pour utilisation ultérieure
print("\nÉtape 4 : Création de la table dans DuckDB...")
conn.register('erp_clean', erp_clean)
conn.execute("CREATE OR REPLACE TABLE erp_clean_final AS SELECT * FROM erp_clean")
print("  Table erp_clean_final créée avec succès")

# Affichage des premières lignes
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(erp_clean)}")
print(f"Résultat attendu : 825 lignes")
print(f"Statut : {'OK' if len(erp_clean) == 825 else 'ATTENTION - Écart détecté'}")

print("\nPremières lignes du fichier nettoyé :")
print(erp_clean.head())

print("\nStatistiques sur les prix :")
print(erp_clean['price'].describe())

# Fermeture de la connexion
conn.close()
print("\nDonnées ERP disponibles dans la table 'erp_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE ERP TERMINÉ")
print("=" * 80)
