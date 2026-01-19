"""
Script       : 03_clean_web.py
Description  : Nettoyage des données du fichier WEB (CMS)
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, filtrer, nettoyer et dédoublonner les données WEB
Résultat     : 714 lignes propres (post_type='product', sans NULL sku)
"""

import pandas as pd
import duckdb
from pathlib import Path

# Chemins
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_web = sources_path / "fichier_web.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNÉES WEB (CMS)")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {db_path}")
conn = duckdb.connect(str(db_path))

# Étape 1 : Chargement du fichier Excel WEB avec pandas
print("\nÉtape 1 : Chargement du fichier WEB...")
web_raw = pd.read_excel(fichier_web)
print(f"  Nombre de lignes chargées : {len(web_raw)}")
print(f"  Colonnes : {len(web_raw.columns)} colonnes")

# Affichage des types de contenu
print("\n  Types de contenu (post_type) :")
types_contenu = web_raw['post_type'].value_counts()
for type_post, count in types_contenu.items():
    print(f"    - {type_post} : {count} lignes")

# Affichage des statistiques sur les valeurs manquantes
print("\n  Valeurs manquantes sur les colonnes clés :")
colonnes_cles = ['sku', 'post_type', 'total_sales', 'post_title']
for col in colonnes_cles:
    nb_null = web_raw[col].isna().sum()
    print(f"    - {col} : {nb_null} ({nb_null/len(web_raw)*100:.1f}%)")

# Étape 2 : Filtrage pour ne conserver que les produits
print("\nÉtape 2 : Filtrage sur post_type = 'product'...")
web_products_only = web_raw[web_raw['post_type'] == 'product'].copy()
print(f"  Nombre de lignes après filtrage : {len(web_products_only)}")
print(f"  Lignes supprimées (non-products) : {len(web_raw) - len(web_products_only)}")

# Étape 3 : Suppression des lignes avec sku NULL
print("\nÉtape 3 : Suppression des lignes avec sku NULL...")
nb_null_sku = web_products_only['sku'].isna().sum()
print(f"  Nombre de lignes avec sku NULL : {nb_null_sku}")
web_sans_null = web_products_only.dropna(subset=['sku'])
print(f"  Nombre de lignes après suppression : {len(web_sans_null)}")

# Statistiques sur les doublons avant dédoublonnage
print("\n  Statistiques avant dédoublonnage :")
print(f"    - Nombre de doublons complets : {web_sans_null.duplicated().sum()}")
print(f"    - Nombre de sku uniques : {web_sans_null['sku'].nunique()}")
print(f"    - Nombre de doublons sur sku : {web_sans_null['sku'].duplicated().sum()}")

# Étape 4 : Dédoublonnage intelligent sur sku
# En cas de doublons, on garde la ligne avec le total_sales le plus élevé
print("\nÉtape 4 : Dédoublonnage sur sku (priorité aux ventes élevées)...")
print("  Stratégie : En cas de doublons, conservation de la ligne avec :")
print("    1. Le total_sales le plus élevé")
print("    2. La date la plus récente (post_date)")

# Tri par sku, total_sales décroissant et post_date décroissant
web_trie = web_sans_null.sort_values(
    by=['sku', 'total_sales', 'post_date'],
    ascending=[True, False, False],
    na_position='last'
)

# Garde uniquement la première occurrence de chaque sku
web_clean = web_trie.drop_duplicates(subset=['sku'], keep='first')

print(f"  Nombre de lignes après dédoublonnage : {len(web_clean)}")
print(f"  Nombre de sku uniques : {web_clean['sku'].nunique()}")

# Vérification qu'il n'y a plus de doublons sur sku
doublons_sku = web_clean['sku'].duplicated().sum()
if doublons_sku > 0:
    print(f"  ATTENTION : {doublons_sku} doublons sur sku encore présents !")
else:
    print("  Vérification OK : sku est une clé primaire unique")

# Étape 5 : Insertion dans DuckDB pour utilisation ultérieure
print("\nÉtape 5 : Création de la table dans DuckDB...")
conn.register('web_clean', web_clean)
conn.execute("CREATE OR REPLACE TABLE web_clean_final AS SELECT * FROM web_clean")
print("  Table web_clean_final créée avec succès")

# Affichage des résultats
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(web_clean)}")
print(f"Résultat attendu : 714 lignes")
print(f"Statut : {'OK' if len(web_clean) == 714 else 'ATTENTION - Écart détecté'}")

print("\nStatistiques sur les ventes (total_sales) :")
print(web_clean['total_sales'].describe())

print("\nTop 5 des produits les plus vendus :")
top_ventes = web_clean.nlargest(5, 'total_sales')[['sku', 'post_title', 'total_sales']]
print(top_ventes.to_string(index=False))

# Fermeture de la connexion
conn.close()
print("\nDonnées WEB disponibles dans la table 'web_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE WEB TERMINÉ")
print("=" * 80)
