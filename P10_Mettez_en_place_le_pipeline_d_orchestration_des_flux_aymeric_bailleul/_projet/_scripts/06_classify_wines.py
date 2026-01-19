"""
Script       : 06_classify_wines.py
Description  : Classification des vins selon le z-score des prix
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Classifier les vins en premium (z-score > 2) ou ordinaire
Résultat     : 30 vins premium
"""

from pathlib import Path
import duckdb

# Chemins
project_path = Path(__file__).resolve().parents[1]
db_path = project_path / "_bdd" / "bottleneck.db"

print("=" * 80)
print("CLASSIFICATION DES VINS (Z-SCORE)")
print("=" * 80)

# Connexion à DuckDB persistante
print(f"Base de données : {db_path}")
conn = duckdb.connect(str(db_path))

# Étape 1 : Vérification de la table source
print("\nÉtape 1 : Vérification de la table source...")
nb_ca = conn.execute("SELECT COUNT(*) FROM ca_par_produit").fetchone()[0]
print(f"  Table ca_par_produit : {nb_ca} lignes")

# Vérification des prix
prix_stats = conn.execute("""
    SELECT 
        MIN(erp_price) AS prix_min,
        MAX(erp_price) AS prix_max,
        COUNT(CASE WHEN erp_price IS NULL THEN 1 END) AS nb_null
    FROM ca_par_produit
""").fetchone()
print(f"  Prix - min: {prix_stats[0]:.2f}€, max: {prix_stats[1]:.2f}€, NULL: {prix_stats[2]}")

# Étape 2 : Calcul des statistiques (moyenne et écart-type)
print("\nÉtape 2 : Calcul des statistiques...")

stats = conn.execute("""
    SELECT 
        AVG(erp_price) AS mu,
        STDDEV(erp_price) AS sigma
    FROM ca_par_produit
""").fetchone()

mu = stats[0]
sigma = stats[1]

print(f"  Moyenne des prix (mu)    : {mu:.2f} €")
print(f"  Écart-type des prix (σ)  : {sigma:.2f} €")

# Étape 3 : Calcul du z-score et classification
print("\nÉtape 3 : Calcul du z-score et classification...")
print(f"  Formule : z-score = (prix - {mu:.2f}) / {sigma:.2f}")
print("  Classification : premium si z-score > 2, sinon ordinaire")

conn.execute(f"""
    CREATE OR REPLACE TABLE wines_classified AS
    SELECT 
        product_id,
        sku,
        post_title,
        onsale_web,
        stock_status,
        erp_price,
        total_sales,
        chiffre_affaires,
        ROUND((erp_price - {mu}) / {sigma}, 3) AS z_score,
        CASE 
            WHEN (erp_price - {mu}) / {sigma} > 2 THEN 'premium'
            ELSE 'ordinaire'
        END AS categorie
    FROM ca_par_produit
    ORDER BY z_score DESC
""")

nb_classified = conn.execute("SELECT COUNT(*) FROM wines_classified").fetchone()[0]
print(f"  Résultat : {nb_classified} vins classifiés")

# Répartition par catégorie
repartition = conn.execute("""
    SELECT 
        categorie,
        COUNT(*) AS nb_vins,
        ROUND(AVG(erp_price), 2) AS prix_moyen,
        ROUND(AVG(z_score), 2) AS z_score_moyen
    FROM wines_classified
    GROUP BY categorie
    ORDER BY categorie DESC
""").fetchall()

print("\n  Répartition par catégorie :")
for row in repartition:
    print(f"    - {row[0]:10s} : {row[1]:3d} vins (prix moyen: {row[2]:6.2f}€, z-score moyen: {row[3]:5.2f})")

# Étape 4 : Vérifications finales
print("\nÉtape 4 : Vérifications finales...")

# Vérifier z-score valides (pas de NaN ou Inf)
nb_invalid = conn.execute("""
    SELECT COUNT(*) 
    FROM wines_classified 
    WHERE z_score IS NULL OR z_score = 'inf' OR z_score = '-inf' OR z_score = 'nan'
""").fetchone()[0]
print(f"  Z-scores invalides (NULL/NaN/Inf) : {nb_invalid} (doit être 0)")

# Nombre de vins premium
nb_premium = conn.execute("""
    SELECT COUNT(*) FROM wines_classified WHERE categorie = 'premium'
""").fetchone()[0]
nb_ordinaire = conn.execute("""
    SELECT COUNT(*) FROM wines_classified WHERE categorie = 'ordinaire'
""").fetchone()[0]
print(f"  Vins premium    : {nb_premium}")
print(f"  Vins ordinaires : {nb_ordinaire}")

# Comparaison avec valeur attendue
premium_attendu = 30
ecart = abs(nb_premium - premium_attendu)

print(f"\n  Comparaison avec attendu :")
print(f"    - Premium calculé : {nb_premium} vins")
print(f"    - Premium attendu : {premium_attendu} vins")
print(f"    - Écart           : {ecart} vins")
print(f"    - Statut          : {'OK' if ecart <= 2 else 'ATTENTION - Écart détecté'}")

# Aperçu des vins premium (TOP 10)
print("\n  TOP 10 vins premium (z-score le plus élevé) :")
top_premium = conn.execute("""
    SELECT product_id, post_title, erp_price, z_score
    FROM wines_classified
    WHERE categorie = 'premium'
    ORDER BY z_score DESC
    LIMIT 10
""").fetchall()

for idx, row in enumerate(top_premium, 1):
    print(f"    {idx:2d}. {row[1][:50]:50s} - {row[2]:6.2f}€ (z={row[3]:5.2f})")

# Résumé final
print("\n" + "=" * 80)
print("RÉSULTAT FINAL")
print("=" * 80)
print(f"\nVins classifiés       : {nb_classified}")
print(f"Vins premium          : {nb_premium}")
print(f"Vins ordinaires       : {nb_ordinaire}")
print(f"Moyenne prix (mu)     : {mu:.2f} €")
print(f"Écart-type (sigma)    : {sigma:.2f} €")
print(f"Z-scores valides      : {'OK' if nb_invalid == 0 else 'ERREUR'}")
print(f"Conformité attendu    : {'OK' if ecart <= 2 else 'ATTENTION - Écart détecté'}")

# Fermeture de la connexion
conn.close()
print("\nDonnées classifiées disponibles dans la table 'wines_classified' de bottleneck.db")
print("\n" + "=" * 80)
print("CLASSIFICATION TERMINÉE")
print("=" * 80)
