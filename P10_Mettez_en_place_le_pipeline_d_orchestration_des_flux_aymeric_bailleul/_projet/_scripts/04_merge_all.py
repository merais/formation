"""
Script       : 04_merge_all.py
Description  : Fusion complete des donnees ERP, LIAISON et WEB
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Realiser les jointures entre les 3 tables nettoyees
Resultat     : 714 lignes completes avec price et total_sales
"""

from pathlib import Path
import duckdb

# Paths
project_path = Path(__file__).resolve().parents[1]
db_path = project_path / "_bdd" / "bottleneck.db"

print("=" * 80)
print("FUSION DES DONNEES ERP + LIAISON + WEB")
print("=" * 80)

# Connexion a DuckDB persistante
print(f"Base de donnees : {db_path}")
conn = duckdb.connect(str(db_path))

# Etape 1 : jointure ERP + LIAISON
print("\nEtape 1 : jointure ERP + LIAISON...")
print("  Jointure sur erp.product_id = liaison.product_id")

# Verification des tables source
nb_erp = conn.execute("SELECT COUNT(*) FROM erp_clean_final").fetchone()[0]
nb_liaison = conn.execute("SELECT COUNT(*) FROM liaison_clean_final").fetchone()[0]
print(f"  Tables source : erp_clean_final ({nb_erp} lignes), liaison_clean_final ({nb_liaison} lignes)")

# Jointure ERP + LIAISON
conn.execute("""
    CREATE OR REPLACE TABLE erp_liaison_merged AS
    SELECT 
        e.product_id,
        e.onsale_web,
        e.price AS erp_price,
        e.stock_quantity,
        e.stock_status,
        l.id_web
    FROM erp_clean_final e
    LEFT JOIN liaison_clean_final l ON e.product_id = l.product_id
""")

nb_erp_liaison = conn.execute("SELECT COUNT(*) FROM erp_liaison_merged").fetchone()[0]
print(f"  Resultat jointure ERP + LIAISON : {nb_erp_liaison} lignes")

# Etape 2 : filtrage des produits avec id_web NULL
print("\nEtape 2 : filtrage des produits sans reference web (id_web NULL)...")

nb_null = conn.execute("SELECT COUNT(*) FROM erp_liaison_merged WHERE id_web IS NULL").fetchone()[0]
print(f"  Nombre de lignes avec id_web NULL : {nb_null}")

conn.execute("""
    CREATE OR REPLACE TABLE erp_liaison_filtered AS
    SELECT *
    FROM erp_liaison_merged
    WHERE id_web IS NOT NULL
""")

nb_filtered = conn.execute("SELECT COUNT(*) FROM erp_liaison_filtered").fetchone()[0]
print(f"  Resultat apres filtrage : {nb_filtered} lignes")

# Etape 3 : jointure avec WEB
print("\nEtape 3 : jointure avec WEB...")

nb_web = conn.execute("SELECT COUNT(*) FROM web_clean_final").fetchone()[0]
print(f"  Table web_clean_final : {nb_web} lignes")
print("  Jointure sur erp_liaison.id_web = web.sku")

conn.execute("""
    CREATE OR REPLACE TABLE merged_data_final AS
    SELECT 
        el.product_id,
        el.onsale_web,
        el.erp_price,
        el.stock_quantity,
        el.stock_status,
        el.id_web,
        w.sku,
        w.post_title,
        w.post_type,
        w.total_sales,
        w.rating_count,
        w.average_rating
    FROM erp_liaison_filtered el
    INNER JOIN web_clean_final w ON CAST(el.id_web AS VARCHAR) = CAST(w.sku AS VARCHAR)
""")

nb_merged = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
print(f"  Resultat jointure finale : {nb_merged} lignes")

# Etape 4 : verifications finales
print("\nEtape 4 : verifications finales...")

# Verification valeurs NULL sur colonnes critiques
null_checks = conn.execute("""
    SELECT 
        SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS null_product_id,
        SUM(CASE WHEN erp_price IS NULL THEN 1 ELSE 0 END) AS null_price,
        SUM(CASE WHEN total_sales IS NULL THEN 1 ELSE 0 END) AS null_total_sales
    FROM merged_data_final
""").fetchone()

print(f"  Valeurs NULL dans colonnes critiques :")
print(f"    - product_id : {null_checks[0]}")
print(f"    - erp_price : {null_checks[1]}")
print(f"    - total_sales : {null_checks[2]}")

# Apercu des donnees
print("\n  Apercu des donnees fusionnees (5 premieres lignes) :")
sample = conn.execute("""
    SELECT product_id, post_title, erp_price, total_sales
    FROM merged_data_final
    LIMIT 5
""").df()
print(sample.to_string(index=False))

# Resume final
print("\n" + "=" * 80)
print("RESULTAT FINAL")
print("=" * 80)
print(f"\nERP + LIAISON         : {nb_erp_liaison} lignes")
print(f"Apres filtrage NULL   : {nb_filtered} lignes")
print(f"Apres jointure WEB    : {nb_merged} lignes")
print(f"Resultat attendu      : 714 lignes")
print(f"Statut                : {'OK' if nb_merged == 714 else 'ATTENTION - ecart detecte'}")

# Fermeture de la connexion
conn.close()
print("\nDonnees fusionnees disponibles dans la table 'merged_data_final' de bottleneck.db")
print("\n" + "=" * 80)
print("FUSION TERMINEE")
print("=" * 80)
