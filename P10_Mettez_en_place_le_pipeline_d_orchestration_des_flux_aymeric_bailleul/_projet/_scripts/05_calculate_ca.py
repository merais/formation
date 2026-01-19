"""
Script       : 05_calculate_ca.py
Description  : Calcul du chiffre d'affaires (CA)
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Calculer le CA par produit et le CA total
Résultat     : CA total de 70 568,60 euros
"""

from pathlib import Path
import duckdb

# Chemins
project_path = Path(__file__).resolve().parents[1]
db_path = project_path / "_bdd" / "bottleneck.db"

print("=" * 80)
print("CALCUL DU CHIFFRE D'AFFAIRES (CA)")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {db_path}")
conn = duckdb.connect(str(db_path))

# Étape 1 : Vérification de la table source
print("\nÉtape 1 : Vérification de la table source...")
nb_merged = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
print(f"  Table merged_data_final : {nb_merged} lignes")

# Vérification des valeurs NULL sur colonnes nécessaires
null_check = conn.execute("""
    SELECT 
        SUM(CASE WHEN erp_price IS NULL THEN 1 ELSE 0 END) AS null_price,
        SUM(CASE WHEN total_sales IS NULL THEN 1 ELSE 0 END) AS null_sales
    FROM merged_data_final
""").fetchone()
print(f"  Valeurs NULL - erp_price : {null_check[0]}, total_sales : {null_check[1]}")

# Étape 2 : Calcul CA par produit
print("\nÉtape 2 : Calcul du CA par produit...")
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
print(f"  Résultat : {nb_ca} lignes avec CA calculé")

# Statistiques CA par produit
stats_ca = conn.execute("""
    SELECT 
        MIN(chiffre_affaires) AS ca_min,
        MAX(chiffre_affaires) AS ca_max,
        ROUND(AVG(chiffre_affaires), 2) AS ca_moyen,
        ROUND(MEDIAN(chiffre_affaires), 2) AS ca_median
    FROM ca_par_produit
""").fetchone()

print(f"\n  Statistiques CA par produit :")
print(f"    - CA minimum  : {stats_ca[0]:.2f} €")
print(f"    - CA maximum  : {stats_ca[1]:.2f} €")
print(f"    - CA moyen    : {stats_ca[2]:.2f} €")
print(f"    - CA médian   : {stats_ca[3]:.2f} €")

# Aperçu TOP 10 produits par CA
print("\n  TOP 10 produits par CA :")
top10 = conn.execute("""
    SELECT product_id, post_title, erp_price, total_sales, chiffre_affaires
    FROM ca_par_produit
    ORDER BY chiffre_affaires DESC
    LIMIT 10
""").df()
for idx, row in top10.iterrows():
    print(f"    {idx+1}. {row['post_title'][:50]:50s} - {row['chiffre_affaires']:8.2f} €")

# Étape 3 : Calcul CA total
print("\nÉtape 3 : Calcul du CA total...")

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
print(f"  CA total           : {ca_total:.2f} €")
print(f"  CA moyen/produit   : {ca_moyen:.2f} €")

# Étape 4 : Vérifications finales
print("\nÉtape 4 : Vérifications finales...")

# Vérifier qu'aucun CA n'est négatif
nb_negatif = conn.execute("""
    SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires < 0
""").fetchone()[0]
print(f"  CA négatifs : {nb_negatif} (doit être 0)")

# Vérifier qu'aucun CA n'est NULL
nb_null_ca = conn.execute("""
    SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires IS NULL
""").fetchone()[0]
print(f"  CA NULL : {nb_null_ca} (doit être 0)")

# Comparaison avec valeur attendue
ca_attendu = 70568.60
ecart = abs(ca_total - ca_attendu)
tolerance = 0  # Aucune tolérance acceptée

print(f"\n  Comparaison avec attendu :")
print(f"    - CA calculé  : {ca_total:.2f} €")
print(f"    - CA attendu  : {ca_attendu:.2f} €")
print(f"    - Écart       : {ecart:.2f} €")
print(f"    - Statut      : {'OK' if ecart <= tolerance else 'ATTENTION - Écart détecté'}")

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
    print(f"    - {row['stock_status']:12s} : {row['nb_produits']:3d} produits, CA = {row['ca_total']:10.2f} €")

# Résumé final
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nProduits analysés     : {nb_ca}")
print(f"CA total calculé      : {ca_total:.2f} €")
print(f"CA attendu            : {ca_attendu:.2f} €")
print(f"Validité données      : {'OK' if nb_negatif == 0 and nb_null_ca == 0 else 'ERREUR'}")
print(f"Conformité attendu    : {'OK' if ecart <= tolerance else 'ATTENTION - Écart détecté'}")

# Fermeture de la connexion
conn.close()
print("\nDonnées CA disponibles dans les tables 'ca_par_produit' et 'ca_total' de bottleneck.db")
print("\n" + "=" * 80)
print("CALCUL CA TERMINÉ")
print("=" * 80)
