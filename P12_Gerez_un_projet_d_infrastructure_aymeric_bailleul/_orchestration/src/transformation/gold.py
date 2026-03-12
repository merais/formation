"""
gold.py – Alimentation des tables gold (metriques metier)

Calcule les eligibilites et l'impact financier a partir des donnees staging
et des distances calculees :
  - gold.eligibilite_prime      : prime sportive (5 % du salaire brut)
  - gold.eligibilite_bien_etre  : 5 journees bien-etre si >= 15 activites/an
  - gold.impact_financier       : agregation par departement

Note : seuls les employes actifs (actif = TRUE) sont pris en compte.

Utilisation :
    python -m src.transformation.gold
"""

import logging

from src.db.connexion import get_connection
from src.transformation.distances import calculate_all_distances

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SEUIL_ACTIVITES_BIEN_ETRE = 15
NB_JOURS_BIEN_ETRE = 5


# ---------------------------------------------------------------------------
# Alimentation de gold.eligibilite_prime
# ---------------------------------------------------------------------------

def insert_eligibilite_prime(cursor, results):
    """Insere les resultats d'eligibilite a la prime dans gold.eligibilite_prime."""
    cursor.execute("TRUNCATE TABLE gold.eligibilite_prime;")
    logger.info("Table gold.eligibilite_prime videe.")

    sql = """
        INSERT INTO gold.eligibilite_prime
            (id_salarie, departement, moyen_deplacement, adresse_domicile,
             distance_km, seuil_km, est_eligible, montant_prime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    rows = [
        (
            r["id_salarie"],
            r["departement"],
            r["moyen_deplacement"],
            r["adresse_domicile"],
            r["distance_km"],
            r["seuil_km"],
            r["est_eligible"],
            r["montant_prime"],
        )
        for r in results
    ]

    cursor.executemany(sql, rows)
    nb_eligible = sum(1 for r in results if r["est_eligible"])
    logger.info(
        f"gold.eligibilite_prime : {len(rows)} lignes inserees "
        f"({nb_eligible} eligibles, {len(rows) - nb_eligible} non eligibles)"
    )


# ---------------------------------------------------------------------------
# Alimentation de gold.eligibilite_bien_etre
# ---------------------------------------------------------------------------

def insert_eligibilite_bien_etre(cursor):
    """
    Calcule l'eligibilite aux 5 journees bien-etre (>= 15 activites Strava/an)
    pour les employes actifs uniquement.
    """
    cursor.execute("TRUNCATE TABLE gold.eligibilite_bien_etre;")
    logger.info("Table gold.eligibilite_bien_etre videe.")

    # Seuls les employes actifs sont pris en compte
    cursor.execute("""
        SELECT e.id_salarie, e.departement, COUNT(a.id_activite) AS nb_activites
        FROM staging.employes e
        LEFT JOIN staging.activites_strava a ON e.id_salarie = a.id_salarie
        WHERE e.actif = TRUE
        GROUP BY e.id_salarie, e.departement
        ORDER BY e.id_salarie;
    """)
    employes = cursor.fetchall()

    sql = """
        INSERT INTO gold.eligibilite_bien_etre
            (id_salarie, departement, nb_activites_annee, est_eligible, nb_jours_bien_etre)
        VALUES (%s, %s, %s, %s, %s);
    """

    rows = []
    nb_eligible = 0
    for id_salarie, departement, nb_activites in employes:
        est_eligible = nb_activites >= SEUIL_ACTIVITES_BIEN_ETRE
        nb_jours = NB_JOURS_BIEN_ETRE if est_eligible else 0
        rows.append((id_salarie, departement, nb_activites, est_eligible, nb_jours))
        if est_eligible:
            nb_eligible += 1

    cursor.executemany(sql, rows)
    logger.info(
        f"gold.eligibilite_bien_etre : {len(rows)} lignes inserees "
        f"({nb_eligible} eligibles, {len(rows) - nb_eligible} non eligibles)"
    )


# ---------------------------------------------------------------------------
# Alimentation de gold.impact_financier
# ---------------------------------------------------------------------------

def insert_impact_financier(cursor):
    """Agrege l'impact financier par departement."""
    cursor.execute("TRUNCATE TABLE gold.impact_financier;")
    logger.info("Table gold.impact_financier videe.")

    cursor.execute("""
        WITH primes AS (
            SELECT
                departement,
                COUNT(*) FILTER (WHERE est_eligible) AS nb_primes,
                COALESCE(SUM(montant_prime) FILTER (WHERE est_eligible), 0) AS total_primes
            FROM gold.eligibilite_prime
            GROUP BY departement
        ),
        bien_etre AS (
            SELECT
                departement,
                COUNT(*) FILTER (WHERE est_eligible) AS nb_bien_etre,
                COALESCE(SUM(nb_jours_bien_etre) FILTER (WHERE est_eligible), 0) AS total_jours
            FROM gold.eligibilite_bien_etre
            GROUP BY departement
        )
        INSERT INTO gold.impact_financier
            (departement, nb_primes, total_primes, nb_bien_etre, total_jours_bien_etre)
        SELECT
            COALESCE(p.departement, b.departement) AS departement,
            COALESCE(p.nb_primes, 0),
            COALESCE(p.total_primes, 0),
            COALESCE(b.nb_bien_etre, 0),
            COALESCE(b.total_jours, 0)
        FROM primes p
        FULL OUTER JOIN bien_etre b ON p.departement = b.departement
        ORDER BY departement;
    """)

    cursor.execute("""
        SELECT departement, nb_primes, total_primes, nb_bien_etre, total_jours_bien_etre
        FROM gold.impact_financier
        ORDER BY departement;
    """)
    rows = cursor.fetchall()
    logger.info(f"gold.impact_financier : {len(rows)} departements")
    for dept, nb_p, tot_p, nb_be, tot_j in rows:
        logger.info(
            f"  {dept} : {nb_p} primes ({tot_p:.2f} EUR), "
            f"{nb_be} bien-etre ({tot_j} jours)"
        )


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run_gold_pipeline(skip_api=False):
    """
    Execute le pipeline complet gold :
    1. Calcul des distances (avec cache) – employes actifs
    2. Alimentation gold.eligibilite_prime
    3. Alimentation gold.eligibilite_bien_etre
    4. Alimentation gold.impact_financier

    Parameters
    ----------
    skip_api : bool
        Si True, ne pas appeler l'API Google Maps (reutilise le cache).
    """
    logger.info("=" * 60)
    logger.info("PHASE 4 – Pipeline Gold")
    logger.info("=" * 60)

    logger.info("Etape 1/4 : Calcul des distances domicile-bureau...")
    if skip_api:
        logger.info("  Mode --skip-api : seul le cache sera utilise (pas d'appel API)")
    results_distances = calculate_all_distances(skip_api=skip_api)

    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        logger.info("Etape 2/4 : Alimentation gold.eligibilite_prime...")
        insert_eligibilite_prime(cursor, results_distances)

        logger.info("Etape 3/4 : Alimentation gold.eligibilite_bien_etre...")
        insert_eligibilite_bien_etre(cursor)

        logger.info("Etape 4/4 : Alimentation gold.impact_financier...")
        insert_impact_financier(cursor)

        cursor.execute("SELECT COUNT(*) FROM gold.eligibilite_prime WHERE est_eligible;")
        nb_prime = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM gold.eligibilite_bien_etre WHERE est_eligible;")
        nb_bien_etre = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(total_primes) FROM gold.impact_financier;")
        total = cursor.fetchone()[0] or 0

        logger.info("=" * 60)
        logger.info(f"RECAP : {nb_prime} eligibles prime, {nb_bien_etre} eligibles bien-etre")
        logger.info(f"RECAP : cout total primes = {total:.2f} EUR")
        logger.info("=" * 60)

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee. Pipeline gold termine.")


if __name__ == "__main__":
    run_gold_pipeline()
