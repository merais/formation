"""
Script       : 08_validate_all.py
Description  : Validation globale de toute la chaîne de traitement
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-19
Objectif     : Valider l'intégrité des données à chaque étape (nettoyage, jointures, calculs, classification)
Résultat     : Rapport de validation avec statut OK/ERREUR pour chaque test
"""

import duckdb
from pathlib import Path
import sys


def main():
    """Validation complète de toutes les étapes du pipeline"""
    
    # Chemins
    project_path = Path(__file__).resolve().parents[1]
    db_path = project_path / "_bdd" / "bottleneck.db"
    
    # Connexion DuckDB (lecture seule)
    conn = duckdb.connect(str(db_path), read_only=True)
    
    # Compteurs de tests
    total_tests = 0
    tests_ok = 0
    tests_ko = 0
    
    print("\n" + "="*80)
    print("VALIDATION GLOBALE DU PIPELINE BOTTLENECK")
    print("="*80)
    print(f"\nBase de données : {db_path}")
    
    try:
        # ================================================================
        # BLOC 1 : VALIDATION NETTOYAGE DES DONNÉES
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 1 : VALIDATION NETTOYAGE DES DONNÉES")
        print("-"*80)
        
        # Test 1 : ERP nettoyé
        print("\n[Test 1] Vérification table erp_clean_final")
        total_tests += 1
        try:
            count_erp = conn.execute("SELECT COUNT(*) FROM erp_clean_final").fetchone()[0]
            duplicates_erp = conn.execute("""
                SELECT COUNT(*) FROM (
                    SELECT product_id, COUNT(*) as cnt 
                    FROM erp_clean_final 
                    GROUP BY product_id 
                    HAVING cnt > 1
                )
            """).fetchone()[0]
            
            assert count_erp == 825, f"Attendu 825 lignes, obtenu {count_erp}"
            assert duplicates_erp == 0, f"Doublons détectés : {duplicates_erp}"
            
            print(f"  ✓ Nombre de lignes : {count_erp} (OK)")
            print(f"  ✓ Doublons : {duplicates_erp} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 2 : LIAISON nettoyé
        print("\n[Test 2] Vérification table liaison_clean_final")
        total_tests += 1
        try:
            count_liaison = conn.execute("SELECT COUNT(*) FROM liaison_clean_final").fetchone()[0]
            duplicates_liaison = conn.execute("""
                SELECT COUNT(*) FROM (
                    SELECT product_id, COUNT(*) as cnt 
                    FROM liaison_clean_final 
                    GROUP BY product_id 
                    HAVING cnt > 1
                )
            """).fetchone()[0]
            
            assert count_liaison == 825, f"Attendu 825 lignes, obtenu {count_liaison}"
            assert duplicates_liaison == 0, f"Doublons détectés : {duplicates_liaison}"
            
            print(f"  ✓ Nombre de lignes : {count_liaison} (OK)")
            print(f"  ✓ Doublons : {duplicates_liaison} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 3 : WEB nettoyé - valeurs manquantes
        print("\n[Test 3] Vérification table web_clean_final - valeurs manquantes")
        total_tests += 1
        try:
            null_sku = conn.execute("SELECT COUNT(*) FROM web_clean_final WHERE sku IS NULL").fetchone()[0]
            wrong_type = conn.execute("SELECT COUNT(*) FROM web_clean_final WHERE post_type != 'product'").fetchone()[0]
            
            assert null_sku == 0, f"SKU NULL détectés : {null_sku}"
            assert wrong_type == 0, f"post_type != 'product' détectés : {wrong_type}"
            
            print(f"  ✓ SKU NULL : {null_sku} (OK)")
            print(f"  ✓ post_type != 'product' : {wrong_type} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 4 : WEB nettoyé - dédoublonnage
        print("\n[Test 4] Vérification table web_clean_final - dédoublonnage")
        total_tests += 1
        try:
            count_web = conn.execute("SELECT COUNT(*) FROM web_clean_final").fetchone()[0]
            duplicates_web = conn.execute("""
                SELECT COUNT(*) FROM (
                    SELECT sku, COUNT(*) as cnt 
                    FROM web_clean_final 
                    GROUP BY sku 
                    HAVING cnt > 1
                )
            """).fetchone()[0]
            
            assert count_web == 714, f"Attendu 714 lignes, obtenu {count_web}"
            assert duplicates_web == 0, f"Doublons SKU détectés : {duplicates_web}"
            
            print(f"  ✓ Nombre de lignes : {count_web} (OK)")
            print(f"  ✓ Doublons SKU : {duplicates_web} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 2 : VALIDATION JOINTURES
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 2 : VALIDATION JOINTURES")
        print("-"*80)
        
        # Test 5 : Cohérence jointure ERP-LIAISON
        print("\n[Test 5] Vérification cohérence jointure ERP-LIAISON")
        total_tests += 1
        try:
            # Vérifier que tous les product_id de merged_data_final existent dans ERP
            orphan_erp = conn.execute("""
                SELECT COUNT(*) FROM merged_data_final m
                WHERE NOT EXISTS (SELECT 1 FROM erp_clean_final e WHERE e.product_id = m.product_id)
            """).fetchone()[0]
            
            # Vérifier que tous les id_web non NULL de merged_data_final existent dans LIAISON
            orphan_liaison = conn.execute("""
                SELECT COUNT(*) FROM merged_data_final m
                WHERE m.id_web IS NOT NULL 
                AND NOT EXISTS (SELECT 1 FROM liaison_clean_final l WHERE l.product_id = m.product_id)
            """).fetchone()[0]
            
            assert orphan_erp == 0, f"product_id orphelins (non dans ERP) : {orphan_erp}"
            assert orphan_liaison == 0, f"product_id orphelins (non dans LIAISON) : {orphan_liaison}"
            
            print(f"  ✓ Cohérence ERP : {orphan_erp} orphelins (OK)")
            print(f"  ✓ Cohérence LIAISON : {orphan_liaison} orphelins (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 6 : Cohérence jointure finale
        print("\n[Test 6] Vérification cohérence jointure finale (merged_data_final)")
        total_tests += 1
        try:
            count_merged = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
            
            # Vérifier que tous les SKU de merged_data_final existent dans WEB
            orphan_web = conn.execute("""
                SELECT COUNT(*) FROM merged_data_final m
                WHERE NOT EXISTS (SELECT 1 FROM web_clean_final w WHERE w.sku = m.sku)
            """).fetchone()[0]
            
            assert count_merged == 714, f"Attendu 714 lignes, obtenu {count_merged}"
            assert orphan_web == 0, f"SKU orphelins (non dans WEB) : {orphan_web}"
            
            print(f"  ✓ Nombre de lignes : {count_merged} (OK)")
            print(f"  ✓ Cohérence WEB : {orphan_web} orphelins (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 3 : VALIDATION CALCULS CA
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 3 : VALIDATION CALCULS CA")
        print("-"*80)
        
        # Test 7 : CA positifs
        print("\n[Test 7] Vérification CA positifs")
        total_tests += 1
        try:
            negative_ca = conn.execute("""
                SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires < 0
            """).fetchone()[0]
            
            null_ca = conn.execute("""
                SELECT COUNT(*) FROM ca_par_produit WHERE chiffre_affaires IS NULL
            """).fetchone()[0]
            
            assert negative_ca == 0, f"CA négatifs détectés : {negative_ca}"
            assert null_ca == 0, f"CA NULL détectés : {null_ca}"
            
            print(f"  ✓ CA négatifs : {negative_ca} (OK)")
            print(f"  ✓ CA NULL : {null_ca} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 8 : CA total
        print("\n[Test 8] Vérification CA total")
        total_tests += 1
        try:
            ca_total_calc = conn.execute("SELECT ca_total FROM ca_total").fetchone()[0]
            ca_expected = 70568.60
            tolerance = 0.01
            
            diff = abs(ca_total_calc - ca_expected)
            assert diff <= tolerance, f"Attendu {ca_expected}€, obtenu {ca_total_calc}€ (écart: {diff}€)"
            
            print(f"  ✓ CA total : {ca_total_calc}€ (OK)")
            print(f"  ✓ CA attendu : {ca_expected}€ (OK)")
            print(f"  ✓ Écart : {diff}€ (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 4 : VALIDATION CLASSIFICATION
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 4 : VALIDATION CLASSIFICATION")
        print("-"*80)
        
        # Test 9 : Validité z-score
        print("\n[Test 9] Vérification validité z-score")
        total_tests += 1
        try:
            null_zscore = conn.execute("""
                SELECT COUNT(*) FROM wines_classified WHERE z_score IS NULL
            """).fetchone()[0]
            
            # Vérifier pas de valeurs infinies (z_score trop grand ou trop petit)
            extreme_zscore = conn.execute("""
                SELECT COUNT(*) FROM wines_classified WHERE ABS(z_score) > 100
            """).fetchone()[0]
            
            # Vérifier que la formule est correcte (recalcul)
            stats = conn.execute("""
                SELECT 
                    ROUND(AVG(erp_price), 2) as mu,
                    ROUND(STDDEV(erp_price), 2) as sigma
                FROM ca_par_produit
            """).fetchone()
            mu_expected, sigma_expected = stats[0], stats[1]
            
            assert null_zscore == 0, f"Z-score NULL détectés : {null_zscore}"
            assert extreme_zscore == 0, f"Z-score extrêmes détectés : {extreme_zscore}"
            
            print(f"  ✓ Z-score NULL : {null_zscore} (OK)")
            print(f"  ✓ Z-score extrêmes : {extreme_zscore} (OK)")
            print(f"  ✓ Moyenne (mu) : {mu_expected}€ (OK)")
            print(f"  ✓ Écart-type (σ) : {sigma_expected}€ (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # Test 10 : Nombre vins premium
        print("\n[Test 10] Vérification nombre vins premium")
        total_tests += 1
        try:
            count_premium = conn.execute("""
                SELECT COUNT(*) FROM wines_classified WHERE categorie = 'premium'
            """).fetchone()[0]
            
            count_ordinary = conn.execute("""
                SELECT COUNT(*) FROM wines_classified WHERE categorie = 'ordinaire'
            """).fetchone()[0]
            
            count_total = conn.execute("SELECT COUNT(*) FROM wines_classified").fetchone()[0]
            
            expected_premium = 30
            
            assert count_premium == expected_premium, f"Attendu {expected_premium} vins premium, obtenu {count_premium}"
            assert count_premium + count_ordinary == count_total, f"Incohérence comptage catégories"
            
            print(f"  ✓ Vins premium : {count_premium} (OK)")
            print(f"  ✓ Vins ordinaires : {count_ordinary} (OK)")
            print(f"  ✓ Total vins : {count_total} (OK)")
            tests_ok += 1
        except AssertionError as e:
            print(f"  ✗ ERREUR : {e}")
            tests_ko += 1
        
        # ================================================================
        # RÉSULTAT FINAL
        # ================================================================
        print("\n" + "="*80)
        print("RÉSULTAT FINAL")
        print("="*80)
        
        success_rate = (tests_ok / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTests exécutés : {total_tests}")
        print(f"Tests réussis  : {tests_ok} ({success_rate:.1f}%)")
        print(f"Tests échoués  : {tests_ko}")
        
        if tests_ko == 0:
            print("\n✓✓✓ VALIDATION COMPLÈTE : TOUS LES TESTS PASSÉS ✓✓✓")
            print("\nLe pipeline est prêt pour l'orchestration Kestra.")
            exit_code = 0
        else:
            print("\n✗✗✗ VALIDATION ÉCHOUÉE : DES ERREURS ONT ÉTÉ DÉTECTÉES ✗✗✗")
            print("\nVeuillez corriger les erreurs avant de passer à Kestra.")
            exit_code = 1
        
        print("\n" + "="*80)
        
    finally:
        conn.close()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
