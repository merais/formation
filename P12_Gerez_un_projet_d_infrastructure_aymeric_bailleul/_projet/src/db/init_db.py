"""
init_db.py – Creation des schemas et tables PostgreSQL

Ce script cree (ou recree) l'ensemble de l'infrastructure de base de donnees
du projet Sport Data Solution selon l'architecture Medallion :
  - raw     : donnees brutes simulees (Strava uniquement)
  - staging : donnees nettoyees et anonymisees (RH, sport, Strava)
  - gold    : tables metier calculees (eligibilites, impact financier)

Utilisation :
    python -m src.db.init_db          # creation des schemas et tables
    python -m src.db.init_db --reset  # suppression puis recreation complete
"""

import argparse
import logging

from src.db.connexion import get_connection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Definition SQL des schemas
# ---------------------------------------------------------------------------

SQL_CREATE_SCHEMAS = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS gold;
"""

# ---------------------------------------------------------------------------
# Definition SQL des tables – schema raw
# Uniquement les donnees simulees Strava (aucune donnee personnelle)
# ---------------------------------------------------------------------------

SQL_CREATE_RAW_TABLES = """
CREATE TABLE IF NOT EXISTS raw.activites_strava (
    id_activite     SERIAL      PRIMARY KEY,
    id_salarie      INTEGER     NOT NULL,
    date_debut      TIMESTAMP   NOT NULL,
    type_sport      VARCHAR(50) NOT NULL,
    distance_m      REAL        NOT NULL,
    duree_s         INTEGER     NOT NULL,
    commentaire     TEXT
);
"""

# ---------------------------------------------------------------------------
# Definition SQL des tables – schema staging
# Premier niveau en base, donnees anonymisees (RGPD) et nettoyees
# ---------------------------------------------------------------------------

SQL_CREATE_STAGING_TABLES = """
-- Employes : 8 colonnes anonymisees (pas de Nom, Prenom, Date de naissance)
CREATE TABLE IF NOT EXISTS staging.employes (
    id_salarie          INTEGER         PRIMARY KEY,
    departement         VARCHAR(100)    NOT NULL,
    date_embauche       DATE            NOT NULL,
    salaire_brut        NUMERIC(10, 2)  NOT NULL,
    type_contrat        VARCHAR(50)     NOT NULL,
    nb_jours_cp         INTEGER         NOT NULL,
    adresse_domicile    TEXT            NOT NULL,
    moyen_deplacement   VARCHAR(50)     NOT NULL
);

-- Pratiques sportives declarees (nettoyees : NaN -> 'Non declare')
CREATE TABLE IF NOT EXISTS staging.pratiques_declarees (
    id_salarie      INTEGER     PRIMARY KEY,
    pratique_sport  VARCHAR(50) NOT NULL
);

-- Activites Strava nettoyees (types corriges, coherence verifiee)
CREATE TABLE IF NOT EXISTS staging.activites_strava (
    id_activite     SERIAL      PRIMARY KEY,
    id_salarie      INTEGER     NOT NULL,
    date_debut      TIMESTAMP   NOT NULL,
    type_sport      VARCHAR(50) NOT NULL,
    distance_m      REAL        NOT NULL,
    duree_s         INTEGER     NOT NULL,
    commentaire     TEXT
);
"""

# ---------------------------------------------------------------------------
# Definition SQL des tables – schema gold
# Tables metier calculees a partir de staging
# ---------------------------------------------------------------------------

SQL_CREATE_GOLD_TABLES = """
-- Eligibilite a la prime sportive (5 % du salaire brut)
CREATE TABLE IF NOT EXISTS gold.eligibilite_prime (
    id_salarie          INTEGER         PRIMARY KEY,
    departement         VARCHAR(100)    NOT NULL,
    moyen_deplacement   VARCHAR(50)     NOT NULL,
    adresse_domicile    TEXT            NOT NULL,
    distance_km         REAL,
    seuil_km            REAL            NOT NULL,
    est_eligible        BOOLEAN         NOT NULL DEFAULT FALSE,
    montant_prime       NUMERIC(10, 2)  NOT NULL DEFAULT 0
);

-- Eligibilite aux 5 journees bien-etre (>= 15 activites / an)
CREATE TABLE IF NOT EXISTS gold.eligibilite_bien_etre (
    id_salarie              INTEGER         PRIMARY KEY,
    departement             VARCHAR(100)    NOT NULL,
    nb_activites_annee      INTEGER         NOT NULL DEFAULT 0,
    est_eligible            BOOLEAN         NOT NULL DEFAULT FALSE,
    nb_jours_bien_etre      INTEGER         NOT NULL DEFAULT 0
);

-- Impact financier agrege par departement
CREATE TABLE IF NOT EXISTS gold.impact_financier (
    departement             VARCHAR(100)    PRIMARY KEY,
    nb_primes               INTEGER         NOT NULL DEFAULT 0,
    total_primes            NUMERIC(12, 2)  NOT NULL DEFAULT 0,
    nb_bien_etre            INTEGER         NOT NULL DEFAULT 0,
    total_jours_bien_etre   INTEGER         NOT NULL DEFAULT 0
);
"""

# ---------------------------------------------------------------------------
# Definition SQL pour la suppression (option --reset)
# ---------------------------------------------------------------------------

SQL_DROP_ALL = """
DROP SCHEMA IF EXISTS gold CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS raw CASCADE;
"""


# ---------------------------------------------------------------------------
# Fonctions principales
# ---------------------------------------------------------------------------

# Tables attendues apres une initialisation complete
TABLES_ATTENDUES = {
    ("raw", "activites_strava"),
    ("staging", "employes"),
    ("staging", "pratiques_declarees"),
    ("staging", "activites_strava"),
    ("gold", "eligibilite_prime"),
    ("gold", "eligibilite_bien_etre"),
    ("gold", "impact_financier"),
}


def database_exists(cursor):
    """
    Verifie si la base est deja initialisee (schemas et tables presentes).

    Returns
    -------
    tuple (bool, set, set)
        - all_present : True si toutes les tables attendues existent
        - tables_trouvees : ensemble des tables presentes en base
        - tables_manquantes : ensemble des tables absentes
    """
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('raw', 'staging', 'gold')
        ORDER BY table_schema, table_name;
    """)
    tables_trouvees = {(row[0], row[1]) for row in cursor.fetchall()}
    tables_manquantes = TABLES_ATTENDUES - tables_trouvees
    all_present = len(tables_manquantes) == 0
    return all_present, tables_trouvees, tables_manquantes


def create_schemas(cursor):
    """Cree les schemas raw, staging et gold."""
    logger.info("Creation des schemas (raw, staging, gold)...")
    cursor.execute(SQL_CREATE_SCHEMAS)
    logger.info("Schemas crees avec succes.")


def create_tables(cursor):
    """Cree toutes les tables dans les trois schemas."""
    logger.info("Creation des tables du schema raw...")
    cursor.execute(SQL_CREATE_RAW_TABLES)

    logger.info("Creation des tables du schema staging...")
    cursor.execute(SQL_CREATE_STAGING_TABLES)

    logger.info("Creation des tables du schema gold...")
    cursor.execute(SQL_CREATE_GOLD_TABLES)

    logger.info("Toutes les tables ont ete creees avec succes.")


def reset_database(cursor):
    """Supprime tous les schemas puis les recree."""
    logger.warning("Suppression de tous les schemas (CASCADE)...")
    cursor.execute(SQL_DROP_ALL)
    logger.info("Schemas supprimes.")
    create_schemas(cursor)
    create_tables(cursor)


def init_database(reset: bool = False):
    """
    Point d'entree principal : initialise la base de donnees.

    Parameters
    ----------
    reset : bool
        Si True, supprime et recree tous les schemas et tables.
        Si False, cree uniquement les elements manquants (IF NOT EXISTS).
    """
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Verification prealable : la base est-elle deja initialisee ?
        all_present, tables_trouvees, tables_manquantes = database_exists(cursor)

        if all_present and not reset:
            logger.info("La base est deja initialisee (7/7 tables presentes).")
            logger.info("Aucune action effectuee. Utilisez --reset pour reinitialiser.")
            return

        if tables_trouvees and not reset:
            # Initialisation partielle : on cree uniquement ce qui manque
            logger.warning(
                f"Base partiellement initialisee : {len(tables_trouvees)}/7 tables presentes."
            )
            logger.info(
                f"Tables manquantes : {', '.join(f'{s}.{t}' for s, t in sorted(tables_manquantes))}"
            )

        if reset:
            reset_database(cursor)
        else:
            create_schemas(cursor)
            create_tables(cursor)

        # Verification : lister les tables creees
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema IN ('raw', 'staging', 'gold')
            ORDER BY table_schema, table_name;
        """)
        tables = cursor.fetchall()
        logger.info("Tables presentes en base :")
        for schema, table in tables:
            logger.info(f"  {schema}.{table}")

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


# ---------------------------------------------------------------------------
# Point d'entree en ligne de commande
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialisation de la base PostgreSQL (schemas + tables)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Supprimer et recreer tous les schemas et tables",
    )
    args = parser.parse_args()
    init_database(reset=args.reset)
