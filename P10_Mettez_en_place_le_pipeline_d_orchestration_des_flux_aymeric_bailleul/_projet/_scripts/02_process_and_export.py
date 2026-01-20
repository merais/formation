"""
Script       : 02_process_and_export.py
Description  : Calcul CA, classification et export local
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-20
Version      : 1.0 - Traitement local

Objectif     : 
  1. Calculer le chiffre d'affaires par produit et global
  2. Classifier les vins (premium/ordinaire) via z-score
  3. Exporter les résultats en Excel et CSV (dossier _exports/)

Résultat     : 
  - rapport_ca.xlsx (2 feuilles)
  - vins_premium.csv (30 vins)
  - vins_ordinaires.csv (684 vins)
"""

import pandas as pd
import duckdb
from pathlib import Path
from datetime import datetime
import sys

# Paths
project_path = Path(__file__).resolve().parents[1]
exports_path = project_path / "_exports"
db_path = project_path / "_bdd" / "bottleneck.db"

# Créer le répertoire exports si nécessaire
exports_path.mkdir(exist_ok=True)

# Timestamp pour nommer les fichiers
timestamp = datetime.now().strftime('%Y%m%d')

print("=" * 80)
print("PIPELINE BOTTLENECK - PHASE 2 : TRAITEMENT ET EXPORT")
print("=" * 80)
print(f"Date d'execution : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base de donnees  : {db_path}")
print(f"Dossier exports  : {exports_path}")

# Vérification de la base de données
if not db_path.exists():
    print(f"\n[ERREUR] : Base de donnees introuvable : {db_path}")
    print("  -> Executez d'abord 01_clean_and_merge.py")
    sys.exit(1)

# Connexion DuckDB (lecture seule)
conn = duckdb.connect(str(db_path))

# Vérification de la table merged_data_final
try:
    count = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
    print(f"[OK] Table merged_data_final trouvee : {count} lignes")
except:
    print("\n[ERREUR] : Table merged_data_final introuvable")
    print("  → Exécutez d'abord 01_clean_and_merge.py")
    conn.close()
    sys.exit(1)

# ============================================================================
# ÉTAPE 1 : CALCUL DU CHIFFRE D'AFFAIRES
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 1/3 : CALCUL DU CHIFFRE D'AFFAIRES")
print("-" * 80)

# Lecture des données fusionnées
merged_data = conn.execute("SELECT * FROM merged_data_final").df()
print(f"Données chargées : {len(merged_data)} lignes")

# Calcul du CA par produit
print("\n[1.1] Calcul du CA par produit")
merged_data['ca'] = merged_data['erp_price'] * merged_data['total_sales']
print(f"  Formule : CA = erp_price × total_sales")

# Vérification des CA négatifs ou NULL
nb_ca_null = merged_data['ca'].isna().sum()
nb_ca_negatif = (merged_data['ca'] < 0).sum()
print(f"  CA NULL : {nb_ca_null}")
print(f"  CA negatifs : {nb_ca_negatif}")

if nb_ca_null > 0 or nb_ca_negatif > 0:
    print("  [ATTENTION] : Anomalies detectees dans les CA")

# Calcul du CA total
ca_total = merged_data['ca'].sum()
print(f"\n[1.2] Calcul du CA total")
print(f"  [OK] CA total : {ca_total:,.2f} €")

# Stockage dans DuckDB
print("\n[1.3] Stockage dans DuckDB")
conn.execute("DROP TABLE IF EXISTS ca_par_produit")
conn.execute("CREATE TABLE ca_par_produit AS SELECT * FROM merged_data")
print(f"  [OK] Table ca_par_produit creee")

conn.execute("DROP TABLE IF EXISTS ca_total")
conn.execute(f"CREATE TABLE ca_total AS SELECT {ca_total} as ca_total")
print(f"  [OK] Table ca_total creee")

# ============================================================================
# ÉTAPE 2 : CLASSIFICATION DES VINS
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 2/3 : CLASSIFICATION DES VINS (Z-SCORE)")
print("-" * 80)

# Calcul des statistiques
mu = merged_data['erp_price'].mean()
sigma = merged_data['erp_price'].std()

print(f"\nStatistiques des prix :")
print(f"  Moyenne (μ)      : {mu:.2f} €")
print(f"  Écart-type (σ)   : {sigma:.2f} €")
print(f"  Prix min         : {merged_data['erp_price'].min():.2f} €")
print(f"  Prix max         : {merged_data['erp_price'].max():.2f} €")

# Calcul du z-score
print(f"\n[2.1] Calcul du z-score")
merged_data['z_score'] = (merged_data['erp_price'] - mu) / sigma
print(f"  Formule : z = (prix - μ) / σ")

# Vérification des z-scores invalides
nb_z_null = merged_data['z_score'].isna().sum()
nb_z_inf = merged_data['z_score'].isin([float('inf'), float('-inf')]).sum()
print(f"  Z-scores NULL : {nb_z_null}")
print(f"  Z-scores infinis : {nb_z_inf}")

# Classification
print(f"\n[2.2] Classification des vins")
merged_data['categorie'] = merged_data['z_score'].apply(
    lambda z: 'premium' if z > 2 else 'ordinaire'
)

nb_premium = (merged_data['categorie'] == 'premium').sum()
nb_ordinaire = (merged_data['categorie'] == 'ordinaire').sum()

print(f"  [OK] Vins premium   : {nb_premium} (z-score > 2)")
print(f"  [OK] Vins ordinaires : {nb_ordinaire}")

# Statistiques par catégorie
print(f"\n[2.3] Chiffre d'affaires par catégorie")
ca_premium = merged_data[merged_data['categorie'] == 'premium']['ca'].sum()
ca_ordinaire = merged_data[merged_data['categorie'] == 'ordinaire']['ca'].sum()

print(f"  CA premium    : {ca_premium:,.2f} € ({ca_premium/ca_total*100:.1f}%)")
print(f"  CA ordinaire  : {ca_ordinaire:,.2f} € ({ca_ordinaire/ca_total*100:.1f}%)")

# Stockage dans DuckDB
conn.execute("DROP TABLE IF EXISTS wines_classified")
conn.execute("CREATE TABLE wines_classified AS SELECT * FROM merged_data")
print(f"\n  [OK] Table wines_classified creee")

# ============================================================================
# ÉTAPE 3 : EXPORT LOCAL DES RÉSULTATS
# ============================================================================
print("\n" + "-" * 80)
print("ETAPE 3/3 : EXPORT LOCAL DES RESULTATS")
print("-" * 80)

# Export 1 : Rapport CA en Excel
print("\n[3.1] Export rapport_ca.xlsx")
rapport_ca_path = exports_path / f"{timestamp}_rapport_ca.xlsx"

with pd.ExcelWriter(rapport_ca_path, engine='openpyxl') as writer:
    # Feuille 1 : CA par produit
    # Utiliser post_title au lieu de product_name
    ca_par_produit = merged_data[[
        'product_id', 'post_title', 'erp_price', 'total_sales', 'ca'
    ]].sort_values('ca', ascending=False)
    
    ca_par_produit.to_excel(writer, sheet_name='CA par produit', index=False)
    
    # Feuille 2 : CA total
    ca_total_df = pd.DataFrame({'ca_total': [ca_total]})
    ca_total_df.to_excel(writer, sheet_name='CA total', index=False)

file_size = rapport_ca_path.stat().st_size / 1024
print(f"  [OK] Fichier cree : {rapport_ca_path.name} ({file_size:.2f} KB)")
print(f"    - Feuille 1 : CA par produit ({len(ca_par_produit)} lignes)")
print(f"    - Feuille 2 : CA total (70 568,60 € attendu)")

# Export 2 : Vins premium en CSV
print("\n[3.2] Export vins_premium.csv")
vins_premium_path = exports_path / f"{timestamp}_vins_premium.csv"

vins_premium = merged_data[merged_data['categorie'] == 'premium'][[
    'product_id', 'post_title', 'erp_price', 'total_sales', 'ca', 'z_score'
]].sort_values('z_score', ascending=False)

vins_premium.to_csv(vins_premium_path, index=False, encoding='utf-8')

file_size = vins_premium_path.stat().st_size / 1024
print(f"  [OK] Fichier cree : {vins_premium_path.name} ({file_size:.2f} KB)")
print(f"    - {len(vins_premium)} vins premium")

# Export 3 : Vins ordinaires en CSV
print("\n[3.3] Export vins_ordinaires.csv")
vins_ordinaires_path = exports_path / f"{timestamp}_vins_ordinaires.csv"

vins_ordinaires = merged_data[merged_data['categorie'] == 'ordinaire'][[
    'product_id', 'post_title', 'erp_price', 'total_sales', 'ca', 'z_score'
]].sort_values('ca', ascending=False)

vins_ordinaires.to_csv(vins_ordinaires_path, index=False, encoding='utf-8')

file_size = vins_ordinaires_path.stat().st_size / 1024
print(f"  [OK] Fichier cree : {vins_ordinaires_path.name} ({file_size:.2f} KB)")
print(f"    - {len(vins_ordinaires)} vins ordinaires")

# ============================================================================
# RÉCAPITULATIF
# ============================================================================
print("\n" + "=" * 80)
print("RECAPITULATIF PHASE 2")
print("=" * 80)
print(f"[OK] CA total calcule        : {ca_total:,.2f} €")
print(f"[OK] Vins premium            : {nb_premium} (z-score > 2)")
print(f"[OK] Vins ordinaires         : {nb_ordinaire}")
print(f"[OK] Fichier Excel cree      : {rapport_ca_path.name}")
print(f"[OK] Fichier CSV premium     : {vins_premium_path.name}")
print(f"[OK] Fichier CSV ordinaires  : {vins_ordinaires_path.name}")
print(f"[OK] Dossier exports         : {exports_path}")
print("=" * 80)
print("[OK] PHASE 2 TERMINEE AVEC SUCCES")
print("=" * 80)

conn.close()
