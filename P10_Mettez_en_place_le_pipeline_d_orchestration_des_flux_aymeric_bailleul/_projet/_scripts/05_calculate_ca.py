"""
Script       : 05_calculate_ca.py
Description  : Calcul du chiffre d'affaires (CA)
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : calculer le CA par produit et le CA total
Resultat     : CA total de 70 568,60 euros
"""

from pathlib import Path
import duckdb

# Paths
project_path = Path(__file__).resolve().parents[1]
db_path = project_path / "_bdd" / "bottleneck.db"

print("=" * 80)
print("CALCUL DU CHIFFRE D'AFFAIRES (CA)")
print("=" * 80)

# Connexion a DuckDB persistante
print(f"Base de donnees : {db_path}")
conn = duckdb.connect(str(db_path))

# Etape 1 : verification de la table source
print("\nEtape 1 : verification de la table source...")
nb_merged = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
print(f"  Table merged_data_final : {nb_merged} lignes")

# Verification des valeurs NULL sur colonnes necessaires
null_check = conn.execute("""
    SELECT 
        SUM(CASE WHEN erp_price IS NULL THEN 1 ELSE 0 END) AS null_price,
        SUM(CASE WHEN total_sales IS NULL THEN 1 ELSE 0 END) AS null_sales
    FROM merged_data_final
""").fetchone()
print(f"  Valeurs NULL - erp_price : {null_check[0]}, total_sales : {null_check[1]}")

# Etape 2 : calcul CA par produit
print("\nEtape 2 : calcul du CA par produit...")
print("  Formule : CA = erp_price × total_sales")

conn.execute("""
    CREATE OR REPLACE TABLE ca_par_produit AS
    SELECT 
        product_id,
        sku,
        post_title,
        onsale_web,
        stock_status,
        erp_price,
        total_sales,
        ROUND(erp_price * total_sales, 2) AS chiffre_affaires
    FROM merged_data_final
    ORDER BY chiffre_affaires DESC
""")

nb_ca = conn.execute("SELECT COUNT(*) FROM ca_par_produit").fetchone()[0]
print(f"  Resultat : {nb_ca} lignes avec CA calcule")

# Statistiques CA par produit
stats_ca = conn.execute("""
    SELECT 
        MIN(chiffre_affaires) AS ca_min,
        MAX(chiffre_affaires) AS ca_max,
        ROUND(AVG(chiffre_affaires), 2) AS ca_moyen,
        ROUND(median(chiffre_affaires), 2) AS ca_median
    FROM ca_par_produit
""").fetchone()

print(f"\n  Statistiques CA par produit :")
print(f"    - CA minimum  : {stats_ca[0]:.2f} euros")
print(f"    - CA maximum  : {stats_ca[1]:.2f} euros")
print(f"    - CA moyen    : {stats_ca[2]:.2f} euros")
print(f"    - CA median   : {stats_ca[3]:.2f} euros")

# Apercu TOP 10 produits par CA
print("\n  TOP 10 produits par CA :")
top10 = conn.execute("""
    SELECT product_id, post_title, erp_price, total_sales, chiffre_affaires
    FROM ca_par_produit
    ORDER BY chiffre_affaires DESC
    LIMIT 10
""").df()
for idx, row in top10.iterrows():
    print(f"    {idx+1}. {row['post_title'][:50]:50s} - {row['chiffre_affaires']:8.2f} euros")

# Etape 3 : calcul CA total
print("\nEtape 3 : calcul du CA total...")

conn.execute("""
    CREATE OR REPLACE TABLE ca_total AS
    SELECT 
        COUNT(*) AS nb_produits,
        ROUND(SUM(chiffre_affaires), 2) AS ca_total,
        ROUND(AVG(chiffre_affaires), 2) AS ca_moyen_produit
    FROM ca_par_produit
""")

result_ca_total = conn.execute("SELECT * FROM ca_total").fetchone()
nb_produits = result_ca_total[0]
ca_total = result_ca_total[1]
ca_moyen = result_ca_total[2]

print(f"  Nombre de produits : {nb_produits}")
print(f"  CA total           : {ca_total:.2f} euros")
print(f"  CA moyen/produit   : {ca_moyen:.2f} euros")

# Etape 4 : verifications finales
print("\nEtape 4 : verifications finales...")

# Verifier qu'aucun CA n'est negatif
nb_negatif = conn.execute("""
    SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires < 0
""").fetchone()[0]
print(f"  CA negatifs : {nb_negatif} (doit etre 0)")

# Verifier qu'aucun CA n'est NULL
nb_null_ca = conn.execute("""
    SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires IS NULL
""").fetchone()[0]
print(f"  CA NULL : {nb_null_ca} (doit etre 0)")

# Comparaison avec valeur attendue
ca_attendu = 70568.60
ecart = abs(ca_total - ca_attendu)
tolerance = 0  # Aucune tolerance acceptee

print(f"\n  Comparaison avec attendu :")
print(f"    - CA calcule  : {ca_total:.2f} euros")
print(f"    - CA attendu  : {ca_attendu:.2f} euros")
print(f"    - Ecart       : {ecart:.2f} euros")
print(f"    - Statut      : {'OK' if ecart <= tolerance else 'ATTENTION - ecart detecte'}")

# Distribution CA par stock status
print("\n  CA par stock status :")
ca_stock = conn.execute("""
    SELECT 
        stock_status,
        COUNT(*) AS nb_produits,
        ROUND(SUM(chiffre_affaires), 2) AS ca_total,
        ROUND(AVG(chiffre_affaires), 2) AS ca_moyen
    FROM ca_par_produit
    GROUP BY stock_status
    ORDER BY ca_total DESC
""").df()
for idx, row in ca_stock.iterrows():
    print(f"    - {row['stock_status']:12s} : {row['nb_produits']:3d} produits, CA = {row['ca_total']:10.2f} euros")

# Resume final
print("\n" + "=" * 80)
print("RESULTAT FINAL")
print("=" * 80)
print(f"\nProduits analyses     : {nb_ca}")
print(f"CA total calcule      : {ca_total:.2f} euros")
print(f"CA attendu            : {ca_attendu:.2f} euros")
print(f"Validite donnees      : {'OK' if nb_negatif == 0 and nb_null_ca == 0 else 'ERREUR'}")
print(f"Conformite attendu    : {'OK' if ecart <= tolerance else 'ATTENTION - ecart detecte'}")

# Fermeture de la connexion
conn.close()
print("\nDonnees CA disponibles dans les tables 'ca_par_produit' et 'ca_total' de bottleneck.db")
print("\n" + "=" * 80)
print("CALCUL CA TERMINE")
print("=" * 80)
