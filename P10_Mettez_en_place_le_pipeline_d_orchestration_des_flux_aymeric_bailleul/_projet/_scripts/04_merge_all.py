"""
Script : 04_merge_all.py
Description : Fusion complète des données ERP, LIAISON et WEB
Auteur : Aymeric Bailleul
Date : 19/01/2026

Objectif : Réaliser les jointures entre les 3 tables nettoyées
Résultat attendu : 714 lignes complètes avec price et total_sales
Flux : ERP + LIAISON (825) -> Filtrage NULL (734) -> + WEB (714)
"""

from pathlib import Path
import duckdb

# Path vers la base de données
path_db = Path("..") / "_bdd" / "bottleneck.db"

print("=" * 80)
print("FUSION DES DONNÉES ERP + LIAISON + WEB")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {path_db}")
conn = duckdb.connect(database=str(path_db))

# Étape 1 : Jointure ERP + LIAISON
print("\nÉtape 1 : Jointure ERP + LIAISON...")
print("  Jointure sur erp.product_id = liaison.product_id")

# Vérification des tables source
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
print(f"  Résultat jointure ERP + LIAISON : {nb_erp_liaison} lignes")

# Étape 2 : Filtrage des produits avec id_web NULL
print("\nÉtape 2 : Filtrage des produits sans référence web (id_web NULL)...")

nb_null = conn.execute("SELECT COUNT(*) FROM erp_liaison_merged WHERE id_web IS NULL").fetchone()[0]
print(f"  Nombre de lignes avec id_web NULL : {nb_null}")

conn.execute("""
    CREATE OR REPLACE TABLE erp_liaison_filtered AS
    SELECT *
    FROM erp_liaison_merged
    WHERE id_web IS NOT NULL
""")

nb_filtered = conn.execute("SELECT COUNT(*) FROM erp_liaison_filtered").fetchone()[0]
print(f"  Résultat après filtrage : {nb_filtered} lignes")

# Étape 3 : Jointure avec WEB
print("\nÉtape 3 : Jointure avec WEB...")

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
print(f"  Résultat jointure finale : {nb_merged} lignes")

# Étape 4 : Vérifications finales
print("\nÉtape 4 : Vérifications finales...")

# Vérification valeurs NULL sur colonnes critiques
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

# Aperçu des données
print("\n  Aperçu des données fusionnées (5 premières lignes) :")
sample = conn.execute("""
    SELECT product_id, post_title, erp_price, total_sales
    FROM merged_data_final
    LIMIT 5
""").df()
print(sample.to_string(index=False))

# Résumé final
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nERP + LIAISON         : {nb_erp_liaison} lignes")
print(f"Après filtrage NULL   : {nb_filtered} lignes")
print(f"Après jointure WEB    : {nb_merged} lignes")
print(f"Résultat attendu      : 714 lignes")
print(f"Statut                : {'OK' if nb_merged == 714 else 'ATTENTION - Écart détecté'}")

# Fermeture de la connexion
conn.close()
print("\nDonnées fusionnées disponibles dans la table 'merged_data_final' de bottleneck.db")
print("\n" + "=" * 80)
print("FUSION TERMINÉE")
print("=" * 80)
