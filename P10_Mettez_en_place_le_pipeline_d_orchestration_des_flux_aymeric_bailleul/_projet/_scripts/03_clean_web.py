"""
Script       : 03_clean_web.py
Description  : Nettoyage des donnees du fichier WEB (CMS)
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Charger, filtrer, nettoyer et dedoublonner les donnees WEB
Resultat     : 714 lignes propres (post_type='product', sans NULL sku)
"""

import pandas as pd
import duckdb
from pathlib import Path

# Paths
project_path = Path(__file__).resolve().parents[1]
sources_path = project_path / "sources"
db_path = project_path / "_bdd" / "bottleneck.db"
fichier_web = sources_path / "fichier_web.xlsx"

print("=" * 80)
print("NETTOYAGE DES DONNEES WEB (CMS)")
print("=" * 80)

# Connexion a DuckDB persistante
print(f"Base de donnees : {db_path}")
conn = duckdb.connect(str(db_path))

# Etape 1 : Chargement du fichier Excel WEB avec pandas
print("\nEtape 1 : Chargement du fichier WEB...")
web_raw = pd.read_excel(fichier_web)
print(f"  Nombre de lignes chargees : {len(web_raw)}")
print(f"  Colonnes : {len(web_raw.columns)} colonnes")

# Affichage des types de contenu
print("\n  Types de contenu (post_type) :")
types_contenu = web_raw['post_type'].value_counts()
for type_post, count in types_contenu.items():
    print(f"    - {type_post} : {count} lignes")

# Affichage des statistiques sur les valeurs manquantes
print("\n  Valeurs manquantes sur les colonnes cles :")
colonnes_cles = ['sku', 'post_type', 'total_sales', 'post_title']
for col in colonnes_cles:
    nb_null = web_raw[col].isna().sum()
    print(f"    - {col} : {nb_null} ({nb_null/len(web_raw)*100:.1f}%)")

# Etape 2 : Filtrage pour ne conserver que les produits
print("\nEtape 2 : Filtrage sur post_type = 'product'...")
web_products_only = web_raw[web_raw['post_type'] == 'product'].copy()
print(f"  Nombre de lignes apres filtrage : {len(web_products_only)}")
print(f"  Lignes supprimees (non-products) : {len(web_raw) - len(web_products_only)}")

# Etape 3 : Suppression des lignes avec sku NULL
print("\nEtape 3 : Suppression des lignes avec sku NULL...")
nb_null_sku = web_products_only['sku'].isna().sum()
print(f"  Nombre de lignes avec sku NULL : {nb_null_sku}")
web_sans_null = web_products_only.dropna(subset=['sku'])
print(f"  Nombre de lignes apres suppression : {len(web_sans_null)}")

# Statistiques sur les doublons avant dedoublonnage
print("\n  Statistiques avant dedoublonnage :")
print(f"    - Nombre de doublons complets : {web_sans_null.duplicated().sum()}")
print(f"    - Nombre de sku uniques : {web_sans_null['sku'].nunique()}")
print(f"    - Nombre de doublons sur sku : {web_sans_null['sku'].duplicated().sum()}")

# Etape 4 : dedoublonnage intelligent sur sku
# En cas de doublons, on garde la ligne avec le total_sales le plus eleve
print("\nEtape 4 : dedoublonnage sur sku (priorite aux ventes elevees)...")
print("  Strategie : en cas de doublons, conservation de la ligne avec :")
print("    1. Le total_sales le plus eleve")
print("    2. La date la plus recente (post_date)")

# Tri par sku, total_sales decroissant et post_date decroissant
web_trie = web_sans_null.sort_values(
    by=['sku', 'total_sales', 'post_date'],
    ascending=[True, False, False],
    na_position='last'
)

# Garde uniquement la premiere occurrence de chaque sku
web_clean = web_trie.drop_duplicates(subset=['sku'], keep='first')

print(f"  Nombre de lignes apres dedoublonnage : {len(web_clean)}")
print(f"  Nombre de sku uniques : {web_clean['sku'].nunique()}")

# Verification qu'il n'y a plus de doublons sur sku
doublons_sku = web_clean['sku'].duplicated().sum()
if doublons_sku > 0:
    print(f"  ATTENTION : {doublons_sku} doublons sur sku encore presents !")
else:
    print("  Verification OK : sku est une cle primaire unique")

# Etape 5 : insertion dans DuckDB pour utilisation ulterieure
print("\nEtape 5 : creation de la table dans DuckDB...")
conn.register('web_clean', web_clean)
conn.execute("CREATE OR REPLACE TABLE web_clean_final AS SELECT * FROM web_clean")
print("  Table web_clean_final creee avec succes")

# Affichage des resultats
print("\n" + "=" * 80)
print("RESULTAT FINAL")
print("=" * 80)
print(f"\nNombre final de lignes : {len(web_clean)}")
print(f"Resultat attendu : 714 lignes")
print(f"Statut : {'OK' if len(web_clean) == 714 else 'ATTENTION - ecart detecte'}")

print("\nStatistiques sur les ventes (total_sales) :")
print(web_clean['total_sales'].describe())

print("\nTop 5 des produits les plus vendus :")
top_ventes = web_clean.nlargest(5, 'total_sales')[['sku', 'post_title', 'total_sales']]
print(top_ventes.to_string(index=False))

# Fermeture de la connexion
conn.close()
print("\nDonnees WEB disponibles dans la table 'web_clean_final' de bottleneck.db")
print("\n" + "=" * 80)
print("NETTOYAGE WEB TERMINE")
print("=" * 80)
