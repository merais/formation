"""
Script       : 03_validate_all.py
Description  : Validation globale de toute la chaine de traitement
Auteur       : Aymeric BAILLEUL
Date         : 2025-01-20
Version      : 2.0 - Adapté pour la nouvelle architecture (3 scripts)

Objectif     : 
  Valider l'integrite des donnees a chaque etape :
  - BLOC 1 : Nettoyage (ERP, LIAISON, WEB)
  - BLOC 2 : Jointures (coherence)
  - BLOC 3 : Calculs CA
  - BLOC 4 : Classification des vins

Resultat     : 
  - 10 tests automatisés
  - Exit code 0 si tout OK, 1 si erreur
"""

import duckdb
from pathlib import Path
import sys


def main():
    """Validation complete de toutes les etapes du pipeline"""
    
    # Paths
    project_path = Path(__file__).resolve().parents[1]
    db_path = project_path / "_bdd" / "bottleneck.db"
    
    print("\n" + "="*80)
    print("PIPELINE BOTTLENECK - PHASE 3 : VALIDATION GLOBALE")
    print("="*80)
    print(f"Base de donnees : {db_path}")
    
    # Vérification de l'existence de la base
    if not db_path.exists():
        print(f"\n[ERREUR] CRITIQUE : Base de donnees introuvable")
        print(f"  -> Executez d'abord 01_clean_and_merge.py")
        sys.exit(1)
    
    # Connexion DuckDB (lecture seule)
    conn = duckdb.connect(str(db_path), read_only=True)
    
    # Compteurs de tests
    total_tests = 0
    tests_ok = 0
    tests_ko = 0
    
    try:
        # ================================================================
        # BLOC 1 : VALIDATION NETTOYAGE des donnees
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 1 : VALIDATION NETTOYAGE DES DONNÉES")
        print("-"*80)
        
        # Test 1 : ERP nettoye
        print("\n[Test 1] Verification table erp_clean_final")
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
            assert duplicates_erp == 0, f"Doublons detectes : {duplicates_erp}"
            
            print(f"  [OK] Nombre de lignes : {count_erp}")
            print(f"  [OK] Doublons : {duplicates_erp}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 2 : LIAISON nettoye
        print("\n[Test 2] Verification table liaison_clean_final")
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
            assert duplicates_liaison == 0, f"Doublons detectes : {duplicates_liaison}"
            
            print(f"  [OK] Nombre de lignes : {count_liaison}")
            print(f"  [OK] Doublons : {duplicates_liaison}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 3 : WEB nettoye - valeurs manquantes
        print("\n[Test 3] Verification table web_clean_final - valeurs manquantes")
        total_tests += 1
        try:
            null_sku = conn.execute("SELECT COUNT(*) FROM web_clean_final WHERE sku IS NULL").fetchone()[0]
            wrong_type = conn.execute("SELECT COUNT(*) FROM web_clean_final WHERE post_type != 'product'").fetchone()[0]
            
            assert null_sku == 0, f"SKU NULL detectes : {null_sku}"
            assert wrong_type == 0, f"post_type != 'product' detectes : {wrong_type}"
            
            print(f"  [OK] SKU NULL : {null_sku}")
            print(f"  [OK] post_type != 'product' : {wrong_type}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 4 : WEB nettoye - dedoublonnage
        print("\n[Test 4] Verification table web_clean_final - dedoublonnage")
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
            assert duplicates_web == 0, f"Doublons SKU detectes : {duplicates_web}"
            
            print(f"  [OK] Nombre de lignes : {count_web}")
            print(f"  [OK] Doublons SKU : {duplicates_web}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 2 : VALIDATION JOINTURES
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 2 : VALIDATION JOINTURES")
        print("-"*80)
        
        # Test 5 : coherence jointure ERP-LIAISON
        print("\n[Test 5] Verification coherence jointure ERP-LIAISON")
        total_tests += 1
        try:
            orphan_erp = conn.execute("""
                SELECT COUNT(*) FROM merged_data_final m
                WHERE NOT EXISTS (SELECT 1 FROM erp_clean_final e WHERE e.product_id = m.product_id)
            """).fetchone()[0]
            
            assert orphan_erp == 0, f"Produits orphelins detectes : {orphan_erp}"
            
            print(f"  [OK] Produits orphelins : {orphan_erp}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 6 : coherence finale
        print("\n[Test 6] Verification coherence finale")
        total_tests += 1
        try:
            count_merged = conn.execute("SELECT COUNT(*) FROM merged_data_final").fetchone()[0]
            
            assert count_merged == 714, f"Attendu 714 lignes, obtenu {count_merged}"
            
            print(f"  [OK] Nombre de lignes fusionnees : {count_merged}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 3 : VALIDATION CALCULS CA
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 3 : VALIDATION CALCULS CA")
        print("-"*80)
        
        # Test 7 : CA positifs
        print("\n[Test 7] Verification CA positifs et non NULL")
        total_tests += 1
        try:
            # Vérifier dans wines_classified (qui contient les CA calculés)
            ca_negatifs = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE ca < 0").fetchone()[0]
            ca_null = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE ca IS NULL").fetchone()[0]
            
            assert ca_negatifs == 0, f"CA negatifs detectes : {ca_negatifs}"
            assert ca_null == 0, f"CA NULL detectes : {ca_null}"
            
            print(f"  [OK] CA negatifs : {ca_negatifs}")
            print(f"  [OK] CA NULL : {ca_null}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 8 : CA total
        print("\n[Test 8] Verification CA total")
        total_tests += 1
        try:
            ca_total_db = conn.execute("SELECT ca_total FROM ca_total").fetchone()[0]
            ca_attendu = 70568.60
            # Conversion en float pour éviter les problèmes de type Decimal
            ca_total_float = float(ca_total_db)
            ecart = abs(ca_total_float - ca_attendu)
            
            # Tolérance de 0.01€
            assert ecart < 0.01, f"CA total incorrect : {ca_total_float:.2f} € (attendu {ca_attendu:.2f} €, ecart {ecart:.2f} €)"
            
            print(f"  [OK] CA total : {ca_total_float:,.2f} €")
            print(f"  [OK] Ecart avec attendu : {ecart:.4f} €")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # ================================================================
        # BLOC 4 : VALIDATION CLASSIFICATION
        # ================================================================
        print("\n" + "-"*80)
        print("BLOC 4 : VALIDATION CLASSIFICATION")
        print("-"*80)
        
        # Test 9 : Z-scores valides
        print("\n[Test 9] Verification z-scores valides")
        total_tests += 1
        try:
            z_null = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE z_score IS NULL").fetchone()[0]
            z_nan = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE z_score != z_score").fetchone()[0]  # NaN check
            z_inf = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE z_score = 'inf' OR z_score = '-inf'").fetchone()[0]
            
            assert z_null == 0, f"Z-scores NULL detectes : {z_null}"
            assert z_nan == 0, f"Z-scores NaN detectes : {z_nan}"
            assert z_inf == 0, f"Z-scores infinis detectes : {z_inf}"
            
            print(f"  [OK] Z-scores NULL : {z_null}")
            print(f"  [OK] Z-scores NaN : {z_nan}")
            print(f"  [OK] Z-scores infinis : {z_inf}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
        
        # Test 10 : Vins premium
        print("\n[Test 10] Verification nombre de vins premium")
        total_tests += 1
        try:
            nb_premium = conn.execute("SELECT COUNT(*) FROM wines_classified WHERE categorie = 'premium'").fetchone()[0]
            nb_attendu = 30
            
            assert nb_premium == nb_attendu, f"Nombre de vins premium incorrect : {nb_premium} (attendu {nb_attendu})"
            
            print(f"  [OK] Vins premium : {nb_premium}")
            tests_ok += 1
        except AssertionError as e:
            print(f"  [ERREUR] : {e}")
            tests_ko += 1
        except Exception as e:
            print(f"  [ERREUR] CRITIQUE : {e}")
            tests_ko += 1
    
    finally:
        conn.close()
    
    # ================================================================
    # BILAN FINAL
    # ================================================================
    print("\n" + "="*80)
    print("BILAN FINAL DE LA VALIDATION")
    print("="*80)
    print(f"Total de tests : {total_tests}")
    print(f"Tests réussis  : {tests_ok}")
    print(f"Tests échoués  : {tests_ko}")
    print(f"Taux de réussite : {tests_ok/total_tests*100:.1f}%")
    print("="*80)
    
    if tests_ko == 0:
        print("[OK] VALIDATION GLOBALE REUSSIE")
        print("  Le pipeline est pret pour la production")
        print("="*80)
        return 0
    else:
        print("[ERREUR] VALIDATION GLOBALE ECHOUEE")
        print(f"  {tests_ko} test(s) en erreur - Corrections necessaires")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
