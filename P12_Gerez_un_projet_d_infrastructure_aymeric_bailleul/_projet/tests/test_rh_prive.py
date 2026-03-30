"""
test_rh_prive.py – Tests de la table rh_prive.identites et des droits PostgreSQL

Verifie :
  - Volume et completude des identites (161 lignes, aucune valeur nulle)
  - Coherence referentielle : chaque id_salarie existe dans staging.employes
  - Separation des donnees : staging.employes ne contient pas de colonne nominative
  - Droits : role_analytics ne peut pas acceder a rh_prive (principe moindre privilege)
  - Vue nominative : vue_primes_nominatives retourne les bonnes colonnes
"""

import pytest
import psycopg2

from src.db.connexion import get_connection


# ---------------------------------------------------------------------------
# Volume et completude
# ---------------------------------------------------------------------------


def test_identites_volume(identites):
    """161 identites doivent etre chargees (une par salarie)."""
    assert len(identites) == 161, f"Attendu 161 identites, obtenu {len(identites)}"


def test_identites_pas_de_valeur_nulle(identites):
    """Aucun champ nom, prenom ou date_naissance ne doit etre NULL."""
    for row in identites:
        id_salarie, nom, prenom, date_naissance = row
        assert nom is not None and nom.strip() != "", f"Nom vide pour id_salarie={id_salarie}"
        assert prenom is not None and prenom.strip() != "", f"Prenom vide pour id_salarie={id_salarie}"
        assert date_naissance is not None, f"Date de naissance NULL pour id_salarie={id_salarie}"


def test_identites_ids_uniques(identites):
    """Chaque id_salarie est unique dans rh_prive.identites."""
    ids = [row[0] for row in identites]
    assert len(ids) == len(set(ids)), "Des id_salarie sont en double dans rh_prive.identites"


# ---------------------------------------------------------------------------
# Coherence referentielle
# ---------------------------------------------------------------------------


def test_identites_coherence_avec_employes(identites, employes):
    """
    Chaque id_salarie de rh_prive.identites doit exister dans staging.employes.
    Verifie l'integrite referentielle (FK).
    """
    ids_employes = {row[0] for row in employes}
    ids_identites = {row[0] for row in identites}
    orphelins = ids_identites - ids_employes
    assert len(orphelins) == 0, (
        f"{len(orphelins)} identites sans employe correspondant : {sorted(orphelins)[:5]}"
    )


def test_identites_couverture_complete(identites, employes):
    """
    Tous les salaries de staging.employes ont une identite dans rh_prive.
    """
    ids_employes = {row[0] for row in employes}
    ids_identites = {row[0] for row in identites}
    manquants = ids_employes - ids_identites
    assert len(manquants) == 0, (
        f"{len(manquants)} employes sans identite dans rh_prive : {sorted(manquants)[:5]}"
    )


# ---------------------------------------------------------------------------
# Separation des donnees (Privacy by Design)
# ---------------------------------------------------------------------------


def test_staging_employes_sans_colonne_nominative(db_cursor):
    """
    staging.employes ne doit contenir aucune colonne nominative (nom, prenom, date_naissance).
    Verifie que l'anonymisation est effective en base.
    """
    db_cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'staging'
          AND table_name = 'employes';
    """)
    colonnes = {row[0] for row in db_cursor.fetchall()}
    colonnes_interdites = {"nom", "prenom", "date_naissance", "name", "firstname"}
    trouvees = colonnes & colonnes_interdites
    assert len(trouvees) == 0, (
        f"Colonnes nominatives trouvees dans staging.employes : {trouvees}"
    )


# ---------------------------------------------------------------------------
# Controle des droits PostgreSQL
# ---------------------------------------------------------------------------


def test_role_analytics_ne_peut_pas_acceder_rh_prive():
    """
    role_analytics ne doit pas pouvoir lire rh_prive.identites.
    Principe du moindre privilege : acces gold uniquement.
    """
    try:
        conn = get_connection(role="analytics")
    except EnvironmentError:
        pytest.skip("Credentials role_analytics non configures dans .env")

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rh_prive.identites LIMIT 1;")
        # Si on arrive ici, le role a acces alors qu'il ne devrait pas
        pytest.fail("role_analytics peut acceder a rh_prive.identites (violation RGPD)")
    except psycopg2.errors.InsufficientPrivilege:
        # Comportement attendu : acces refuse
        pass
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Vue nominative
# ---------------------------------------------------------------------------


def test_vue_primes_nominatives_existe(db_cursor):
    """La vue rh_prive.vue_primes_nominatives doit exister."""
    db_cursor.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'rh_prive'
          AND table_name = 'vue_primes_nominatives';
    """)
    result = db_cursor.fetchone()
    assert result is not None, "La vue rh_prive.vue_primes_nominatives n'existe pas"


def test_vue_primes_nominatives_colonnes(db_cursor):
    """La vue doit exposer les colonnes nominatives + metier."""
    db_cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'rh_prive'
          AND table_name = 'vue_primes_nominatives'
        ORDER BY ordinal_position;
    """)
    colonnes = {row[0] for row in db_cursor.fetchall()}
    attendues = {"nom", "prenom", "departement", "est_eligible_prime", "montant_prime_eur"}
    manquantes = attendues - colonnes
    assert len(manquantes) == 0, f"Colonnes manquantes dans la vue : {manquantes}"
