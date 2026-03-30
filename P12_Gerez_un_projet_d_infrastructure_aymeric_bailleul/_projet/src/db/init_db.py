"""
init_db.py – Creation des schemas et tables PostgreSQL

Ce script cree (ou recree) l'ensemble de l'infrastructure de base de donnees
du projet Sport Data Solution selon l'architecture Medallion :
  - raw      : donnees brutes simulees (Strava uniquement)
  - staging  : donnees nettoyees et anonymisees (RH, sport, Strava)
  - gold     : tables metier calculees (eligibilites, impact financier)
  - rh_prive : identites nominatives (Nom, Prenom, DDN) – acces restreint RGPD

Gestion des droits PostgreSQL :
  - role_pipeline  : lecture/ecriture raw + staging + gold (pipeline ETL)
  - role_analytics : lecture seule gold (PowerBI, analyses)
  - role_rh_admin  : herite pipeline + acces rh_prive (nominatif)

Utilisation :
    python -m src.db.init_db          # creation des schemas et tables
    python -m src.db.init_db --reset  # suppression puis recreation complete
"""

import argparse
import logging
import os

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
-- Schema prive : identites nominatives (Nom, Prenom, DDN), acces restreint
CREATE SCHEMA IF NOT EXISTS rh_prive;
"""

# ---------------------------------------------------------------------------
# Definition SQL des tables – schema rh_prive
# Donnees nominatives RGPD : acces restreint via role_rh_admin uniquement
# FK vers staging.employes pour garantir la coherence referentielle
# ---------------------------------------------------------------------------

SQL_CREATE_RH_PRIVE_TABLES = """
CREATE TABLE IF NOT EXISTS rh_prive.identites (
    id_salarie      INTEGER PRIMARY KEY REFERENCES staging.employes(id_salarie),
    nom             VARCHAR(100) NOT NULL,
    prenom          VARCHAR(100) NOT NULL,
    date_naissance  DATE NOT NULL
);
"""

# Vue nominative cross-schema : agregation identite + primes + bien-etre
# Accessible uniquement via role_rh_admin
SQL_CREATE_RH_VIEW = """
CREATE OR REPLACE VIEW rh_prive.vue_primes_nominatives AS
SELECT
    i.nom,
    i.prenom,
    e.departement,
    ep.est_eligible         AS est_eligible_prime,
    ep.montant_prime        AS montant_prime_eur,
    eb.nb_activites_annee,
    eb.est_eligible         AS est_eligible_bien_etre,
    eb.nb_jours_bien_etre
FROM rh_prive.identites i
JOIN staging.employes e USING (id_salarie)
LEFT JOIN gold.eligibilite_prime ep USING (id_salarie)
LEFT JOIN gold.eligibilite_bien_etre eb USING (id_salarie);
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

# rh_prive dropped first : sa FK reference staging.employes
SQL_DROP_ALL = """
DROP SCHEMA IF EXISTS rh_prive CASCADE;
DROP SCHEMA IF EXISTS gold CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS raw CASCADE;
"""


# ---------------------------------------------------------------------------
# Fonctions principales
# ---------------------------------------------------------------------------

# Tables attendues apres une initialisation complete (8 tables + 1 vue)
TABLES_ATTENDUES = {
    ("raw", "activites_strava"),
    ("staging", "employes"),
    ("staging", "pratiques_declarees"),
    ("staging", "activites_strava"),
    ("gold", "eligibilite_prime"),
    ("gold", "eligibilite_bien_etre"),
    ("gold", "impact_financier"),
    ("rh_prive", "identites"),
}

NB_TABLES = len(TABLES_ATTENDUES)  # 8


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
        WHERE table_schema IN ('raw', 'staging', 'gold', 'rh_prive')
          AND table_type = 'BASE TABLE'
        ORDER BY table_schema, table_name;
    """)
    tables_trouvees = {(row[0], row[1]) for row in cursor.fetchall()}
    tables_manquantes = TABLES_ATTENDUES - tables_trouvees
    all_present = len(tables_manquantes) == 0
    return all_present, tables_trouvees, tables_manquantes


def create_schemas(cursor):
    """Cree les schemas raw, staging, gold et rh_prive."""
    logger.info("Creation des schemas (raw, staging, gold, rh_prive)...")
    cursor.execute(SQL_CREATE_SCHEMAS)
    logger.info("Schemas crees avec succes.")


def create_tables(cursor):
    """Cree toutes les tables dans les quatre schemas."""
    logger.info("Creation des tables du schema raw...")
    cursor.execute(SQL_CREATE_RAW_TABLES)

    logger.info("Creation des tables du schema staging...")
    cursor.execute(SQL_CREATE_STAGING_TABLES)

    logger.info("Creation des tables du schema gold...")
    cursor.execute(SQL_CREATE_GOLD_TABLES)

    # rh_prive apres staging : la FK identites -> staging.employes doit exister
    logger.info("Creation des tables du schema rh_prive (donnees nominatives RGPD)...")
    cursor.execute(SQL_CREATE_RH_PRIVE_TABLES)
    cursor.execute(SQL_CREATE_RH_VIEW)

    logger.info("Toutes les tables ont ete creees avec succes.")


def build_roles_sql():
    """
    Construit le SQL de creation des roles et droits en lisant
    les mots de passe depuis les variables d'environnement.

    Les roles sont idempotents (IF NOT EXISTS) : sans effet si deja presents.
    """
    pipeline_pass  = os.getenv("DB_PASS_PIPELINE",  "pipeline_secret")
    analytics_pass = os.getenv("DB_PASS_ANALYTICS", "analytics_secret")
    rh_pass        = os.getenv("DB_PASS_RH",        "rh_secret")

    return f"""
    -- Creation des roles (idempotent)
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_pipeline') THEN
            CREATE ROLE role_pipeline LOGIN PASSWORD '{pipeline_pass}';
        ELSE
            ALTER ROLE role_pipeline PASSWORD '{pipeline_pass}';
        END IF;

        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_analytics') THEN
            CREATE ROLE role_analytics LOGIN PASSWORD '{analytics_pass}';
        ELSE
            ALTER ROLE role_analytics PASSWORD '{analytics_pass}';
        END IF;

        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'role_rh_admin') THEN
            CREATE ROLE role_rh_admin LOGIN PASSWORD '{rh_pass}';
        ELSE
            ALTER ROLE role_rh_admin PASSWORD '{rh_pass}';
        END IF;
    END$$;

    -- role_pipeline : lecture/ecriture raw + staging, lecture gold
    GRANT USAGE ON SCHEMA raw, staging, gold TO role_pipeline;
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
        ON ALL TABLES IN SCHEMA raw TO role_pipeline;
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
        ON ALL TABLES IN SCHEMA staging TO role_pipeline;
    GRANT SELECT ON ALL TABLES IN SCHEMA gold TO role_pipeline;
    GRANT USAGE ON ALL SEQUENCES IN SCHEMA raw TO role_pipeline;
    GRANT USAGE ON ALL SEQUENCES IN SCHEMA staging TO role_pipeline;

    -- role_analytics : lecture seule gold (PowerBI, analyst)
    GRANT USAGE ON SCHEMA gold TO role_analytics;
    GRANT SELECT ON ALL TABLES IN SCHEMA gold TO role_analytics;

    -- role_rh_admin : herite de pipeline + acces exclusif rh_prive
    GRANT role_pipeline TO role_rh_admin;
    GRANT USAGE ON SCHEMA rh_prive TO role_rh_admin;
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
        ON rh_prive.identites TO role_rh_admin;
    GRANT SELECT ON rh_prive.vue_primes_nominatives TO role_rh_admin;
    """


def create_roles_and_grants(cursor):
    """Cree les roles PostgreSQL et configure les droits d'acces."""
    logger.info("Configuration des roles et droits PostgreSQL...")
    cursor.execute(build_roles_sql())
    logger.info("Roles configures : role_pipeline, role_analytics, role_rh_admin.")


def reset_database(cursor):
    """Supprime tous les schemas puis les recree (roles conserves)."""
    logger.warning("Suppression de tous les schemas (CASCADE)...")
    cursor.execute(SQL_DROP_ALL)
    logger.info("Schemas supprimes. Les roles PostgreSQL sont conserves.")
    create_schemas(cursor)
    create_tables(cursor)
    create_roles_and_grants(cursor)


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
            logger.info(f"La base est deja initialisee ({NB_TABLES}/{NB_TABLES} tables presentes).")
            logger.info("Aucune action effectuee. Utilisez --reset pour reinitialiser.")
            return

        if tables_trouvees and not reset:
            # Initialisation partielle : on cree uniquement ce qui manque
            logger.warning(
                f"Base partiellement initialisee : {len(tables_trouvees)}/{NB_TABLES} tables presentes."
            )
            logger.info(
                f"Tables manquantes : {', '.join(f'{s}.{t}' for s, t in sorted(tables_manquantes))}"
            )

        if reset:
            reset_database(cursor)
        else:
            create_schemas(cursor)
            create_tables(cursor)
            create_roles_and_grants(cursor)

        # Verification : lister les tables creees
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema IN ('raw', 'staging', 'gold', 'rh_prive')
              AND table_type = 'BASE TABLE'
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
