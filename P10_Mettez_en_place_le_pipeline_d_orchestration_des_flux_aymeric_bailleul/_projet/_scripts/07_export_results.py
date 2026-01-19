"""
Script       : 07_export_results.py
Description  : Export des resultats finaux vers fichiers Excel et CSV
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-16
Objectif     : Exporter les donnees finales (CA + classification) dans des formats exploitables
Resultat     : 3 fichiers - rapport_ca.xlsx (2 feuilles), vins_premium.csv, vins_ordinaires.csv
"""

import duckdb
from pathlib import Path
import pandas as pd
from datetime import datetime


def main():
    """Export des resultats finaux (CA + vins classifies)"""
    
    # Paths
    project_path = Path(__file__).resolve().parents[1]
    db_path = project_path / "_bdd" / "bottleneck.db"
    exports_path = project_path / "_exports"
    exports_path.mkdir(exist_ok=True)
    
    # Timestamp pour les noms de fichiers (format YYYYmmDD_)
    timestamp = datetime.now().strftime("%Y%m%d_")
    
    # Fichiers de sortie avec timestamp
    excel_output_path = exports_path / f"{timestamp}rapport_ca.xlsx"
    premium_csv_path = exports_path / f"{timestamp}vins_premium.csv"
    ordinary_csv_path = exports_path / f"{timestamp}vins_ordinaires.csv"
    
    # Connexion DuckDB (lecture seule)
    conn = duckdb.connect(str(db_path), read_only=False)
    
    try:
        print("\n" + "="*70)
        print("EXPORT DES RESULTATS FINAUX")
        print("="*70)
        
        # ============================================================
        # Etape 1 : verification des tables sources
        # ============================================================
        print("\nEtape 1 : verification des tables sources")
        
        # Verifier ca_par_produit
        count_ca = conn.execute("SELECT COUNT(*) FROM ca_par_produit").fetchone()[0]
        print(f"  [OK] Table ca_par_produit trouvee : {count_ca} lignes")
        
        # Verifier ca_total
        count_total = conn.execute("SELECT COUNT(*) FROM ca_total").fetchone()[0]
        print(f"  [OK] Table ca_total trouvee : {count_total} ligne(s)")
        
        # Verifier wines_classified
        count_classified = conn.execute("SELECT COUNT(*) FROM wines_classified").fetchone()[0]
        print(f"  [OK] Table wines_classified trouvee : {count_classified} lignes")
        
        # ============================================================
        # Etape 2 : export Excel (rapport CA complet)
        # ============================================================
        print("\nEtape 2 : export du rapport CA vers Excel")
        
        # Recuperer CA par produit
        df_ca_produit = conn.execute("""
            SELECT 
                product_id,
                sku,
                post_title,
                erp_price,
                total_sales,
                chiffre_affaires,
                ROUND((chiffre_affaires * 100.0 / (SELECT SUM(chiffre_affaires) FROM ca_par_produit)), 2) as pct_ca_total
            FROM ca_par_produit
            ORDER BY chiffre_affaires DESC
        """).df()
        
        # Recuperer CA total
        df_ca_total = conn.execute("""
            SELECT 
                ca_total,
                nb_produits,
                ca_moyen_produit
            FROM ca_total
        """).df()
        
        # Creer le fichier Excel avec 2 feuilles
        with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
            df_ca_produit.to_excel(writer, sheet_name='CA_par_produit', index=False)
            df_ca_total.to_excel(writer, sheet_name='CA_total', index=False)
        
        print(f"  [OK] Fichier Excel cree : {excel_output_path.name}")
        print(f"    - Feuille 1 : CA_par_produit ({len(df_ca_produit)} produits)")
        print(f"    - Feuille 2 : CA_total (CA total : {df_ca_total['ca_total'].iloc[0]:.2f} euros)")
        
        # ============================================================
        # Etape 3 : export CSV vins premium
        # ============================================================
        print("\nEtape 3 : export des vins premium vers CSV")
        
        # Recuperer vins premium avec details CA
        df_premium = conn.execute("""
            SELECT 
                w.product_id,
                w.sku,
                w.post_title,
                w.erp_price,
                w.total_sales,
                w.z_score,
                w.categorie,
                c.chiffre_affaires,
                ROUND((c.chiffre_affaires * 100.0 / (SELECT SUM(chiffre_affaires) FROM ca_par_produit)), 2) as pct_ca_total
            FROM wines_classified w
            JOIN ca_par_produit c ON w.product_id = c.product_id
            WHERE w.categorie = 'premium'
            ORDER BY w.z_score DESC
        """).df()
        
        # Export CSV
        df_premium.to_csv(premium_csv_path, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"  [OK] Fichier CSV cree : {premium_csv_path.name}")
        print(f"    - Nombre de vins premium : {len(df_premium)}")
        if len(df_premium) > 0:
            print(f"    - Z-score moyen : {df_premium['z_score'].mean():.2f}")
            print(f"    - Prix moyen : {df_premium['erp_price'].mean():.2f} euros")
            print(f"    - CA total premium : {df_premium['chiffre_affaires'].sum():.2f} euros")
        
        # ============================================================
        # Etape 4 : export CSV vins ordinaires
        # ============================================================
        print("\nEtape 4 : export des vins ordinaires vers CSV")
        
        # Recuperer vins ordinaires avec details CA
        df_ordinary = conn.execute("""
            SELECT 
                w.product_id,
                w.sku,
                w.post_title,
                w.erp_price,
                w.total_sales,
                w.z_score,
                w.categorie,
                c.chiffre_affaires,
                ROUND((c.chiffre_affaires * 100.0 / (SELECT SUM(chiffre_affaires) FROM ca_par_produit)), 2) as pct_ca_total
            FROM wines_classified w
            JOIN ca_par_produit c ON w.product_id = c.product_id
            WHERE w.categorie = 'ordinaire'
            ORDER BY c.chiffre_affaires DESC
        """).df()
        
        # Export CSV
        df_ordinary.to_csv(ordinary_csv_path, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"  [OK] Fichier CSV cree : {ordinary_csv_path.name}")
        print(f"    - Nombre de vins ordinaires : {len(df_ordinary)}")
        if len(df_ordinary) > 0:
            print(f"    - Z-score moyen : {df_ordinary['z_score'].mean():.2f}")
            print(f"    - Prix moyen : {df_ordinary['erp_price'].mean():.2f} euros")
            print(f"    - CA total ordinaire : {df_ordinary['chiffre_affaires'].sum():.2f} euros")
        
        # ============================================================
        # RESULTAT FINAL
        # ============================================================
        print("\n" + "="*70)
        print("RESULTAT FINAL")
        print("="*70)
        print(f"\n[OK] Export termine avec succes")
        print(f"\nFichiers crees dans : {exports_path}")
        print(f"  1. {excel_output_path.name} (2 feuilles)")
        print(f"  2. {premium_csv_path.name} ({len(df_premium)} vins premium)")
        print(f"  3. {ordinary_csv_path.name} ({len(df_ordinary)} vins ordinaires)")
        
        # Statistiques globales
        total_products = len(df_premium) + len(df_ordinary)
        pct_premium = (len(df_premium) / total_products * 100) if total_products > 0 else 0
        
        print(f"\nStatistiques globales :")
        print(f"  - Total produits : {total_products}")
        print(f"  - Vins premium : {len(df_premium)} ({pct_premium:.1f}%)")
        print(f"  - Vins ordinaires : {len(df_ordinary)} ({100-pct_premium:.1f}%)")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
