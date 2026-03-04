"""
conftest.py – Fixtures partagees pour les tests pytest

Fournit une connexion PostgreSQL reutilisable et des jeux de donnees
de reference pour l'ensemble de la suite de tests.
"""

import pytest

from src.db.connexion import get_connection


@pytest.fixture(scope="session")
def db_connection():
    """
    Connexion PostgreSQL ouverte pour toute la session de test.
    Le rollback est implicite : les tests ne modifient pas la base.
    """
    conn = get_connection()
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def db_cursor(db_connection):
    """Curseur PostgreSQL reutilisable sur toute la session."""
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()


# ---------------------------------------------------------------------------
# Jeux de donnees de reference (charges une seule fois)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def employes(db_cursor):
    """Charge tous les employes depuis staging.employes."""
    db_cursor.execute("""
        SELECT id_salarie, departement, date_embauche, salaire_brut,
               type_contrat, nb_jours_cp, adresse_domicile, moyen_deplacement
        FROM staging.employes
        ORDER BY id_salarie;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def pratiques(db_cursor):
    """Charge toutes les pratiques depuis staging.pratiques_declarees."""
    db_cursor.execute("""
        SELECT id_salarie, pratique_sport
        FROM staging.pratiques_declarees
        ORDER BY id_salarie;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def activites_raw(db_cursor):
    """Charge toutes les activites depuis raw.activites_strava."""
    db_cursor.execute("""
        SELECT id_activite, id_salarie, date_debut, type_sport, distance_m, duree_s
        FROM raw.activites_strava;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def activites_staging(db_cursor):
    """Charge toutes les activites depuis staging.activites_strava."""
    db_cursor.execute("""
        SELECT id_activite, id_salarie, date_debut, type_sport, distance_m, duree_s
        FROM staging.activites_strava;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def eligibilite_prime(db_cursor):
    """Charge gold.eligibilite_prime."""
    db_cursor.execute("""
        SELECT id_salarie, departement, moyen_deplacement, adresse_domicile,
               distance_km, seuil_km, est_eligible, montant_prime
        FROM gold.eligibilite_prime
        ORDER BY id_salarie;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def eligibilite_bien_etre(db_cursor):
    """Charge gold.eligibilite_bien_etre."""
    db_cursor.execute("""
        SELECT id_salarie, departement, nb_activites_annee, est_eligible, nb_jours_bien_etre
        FROM gold.eligibilite_bien_etre
        ORDER BY id_salarie;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def impact_financier(db_cursor):
    """Charge gold.impact_financier."""
    db_cursor.execute("""
        SELECT departement, nb_primes, total_primes, nb_bien_etre, total_jours_bien_etre
        FROM gold.impact_financier
        ORDER BY departement;
    """)
    return db_cursor.fetchall()


@pytest.fixture(scope="session")
def salaires_par_id(db_cursor):
    """Dictionnaire {id_salarie: salaire_brut} pour les verifications de primes."""
    db_cursor.execute("SELECT id_salarie, salaire_brut FROM staging.employes;")
    return {row[0]: float(row[1]) for row in db_cursor.fetchall()}
