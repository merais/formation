"""
load_sport.py – Ingestion des donnees sportives (XLSX -> staging.pratiques_declarees)

Lit le fichier Donnees+Sportive.xlsx, nettoie les valeurs manquantes
(NaN -> "Non declare"), corrige les typos connues, puis insere
les 2 colonnes dans staging.pratiques_declarees.

Architecture Option B (Privacy by Design) :
  - Le XLSX fait office de couche raw (sur disque, jamais copie en base)
  - Le pipeline lit, nettoie en memoire, insere directement dans staging

Utilisation :
    python -m src.ingestion.load_sport
"""

import logging
from pathlib import Path

import pandas as pd

from src.db.connexion import get_connection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Chemin vers le fichier source
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_SPORT_PATH = _PROJECT_ROOT / "data" / "RAW" / "Données+Sportive.xlsx"

# Corrections de typos connues (detectees dans l'analyse exploratoire)
TYPOS_SPORT = {
    "Runing": "Running",
}


def load_sport_to_staging():
    """
    Charge les donnees sportives depuis le XLSX, nettoie les NaN
    et les typos, puis insere dans staging.pratiques_declarees.

    Returns
    -------
    int
        Nombre de lignes inserees.
    """
    # --- Lecture du fichier source ---
    logger.info(f"Lecture du fichier : {RAW_SPORT_PATH.name}")
    df = pd.read_excel(RAW_SPORT_PATH)
    logger.info(f"  {len(df)} lignes lues, {len(df.columns)} colonnes")

    # --- Renommage des colonnes ---
    df = df.rename(columns={
        "ID salarié": "id_salarie",
        "Pratique d'un sport": "pratique_sport",
    })

    # --- Deduplication sur id_salarie (garder la premiere occurrence) ---
    nb_avant = len(df)
    df = df.drop_duplicates(subset=["id_salarie"], keep="first")
    nb_doublons = nb_avant - len(df)
    if nb_doublons > 0:
        logger.info(f"  {nb_doublons} doublons supprimes (sur id_salarie)")

    # --- Nettoyage des valeurs manquantes ---
    nb_nan = df["pratique_sport"].isna().sum()
    df["pratique_sport"] = df["pratique_sport"].fillna("Non déclaré")
    logger.info(f"  {nb_nan} NaN remplaces par 'Non declare'")

    # --- Correction des typos ---
    df["pratique_sport"] = df["pratique_sport"].replace(TYPOS_SPORT)
    df["pratique_sport"] = df["pratique_sport"].str.strip()
    logger.info(f"  Typos corrigees et chaines nettoyees")

    # --- Insertion en base ---
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Vider la table avant insertion (idempotence du pipeline)
        cursor.execute("TRUNCATE TABLE staging.pratiques_declarees;")
        logger.info("  Table staging.pratiques_declarees videe (TRUNCATE)")

        # Insertion ligne par ligne
        insert_sql = """
            INSERT INTO staging.pratiques_declarees
                (id_salarie, pratique_sport)
            VALUES (%s, %s);
        """
        nb_inserts = 0
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                int(row["id_salarie"]),
                row["pratique_sport"],
            ))
            nb_inserts += 1

        conn.commit()
        logger.info(f"  {nb_inserts} lignes inserees dans staging.pratiques_declarees")
        return nb_inserts

    except Exception as err:
        conn.rollback()
        logger.error(f"Erreur lors de l'insertion : {err}")
        raise

    finally:
        cursor.close()
        conn.close()
        logger.info("  Connexion fermee.")


if __name__ == "__main__":
    load_sport_to_staging()
