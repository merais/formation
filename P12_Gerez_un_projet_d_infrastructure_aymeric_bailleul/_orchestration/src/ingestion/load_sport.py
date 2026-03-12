"""
load_sport.py – Ingestion des donnees sportives (XLSX -> staging.pratiques_declarees)

Lit le fichier Donnees+Sportive.xlsx, nettoie les valeurs manquantes
(NaN -> "Non declare"), corrige les typos connues, puis UPSERT dans
staging.pratiques_declarees. Supprime les lignes absentes du XLSX.
Met a jour le hash dans meta.pipeline_state.

Utilisation :
    python -m src.ingestion.load_sport
"""

import hashlib
import logging
import os
from pathlib import Path

import pandas as pd

from src.db.connexion import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_xlsx_dir = Path(os.environ.get("XLSX_DIR", str(_PROJECT_ROOT / "data" / "RAW")))
RAW_SPORT_PATH = _xlsx_dir / "Données+Sportive.xlsx"

TYPOS_SPORT = {
    "Runing": "Running",
}


def compute_file_hash(path: Path) -> str:
    """Calcule le hachage SHA-256 d un fichier (pour detection de modifications)."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_sport_to_staging():
    """
    Charge les donnees sportives depuis le XLSX, nettoie les NaN
    et les typos, puis UPSERT dans staging.pratiques_declarees.
    Supprime les lignes absentes du fichier source.

    Returns
    -------
    int
        Nombre de lignes upsertees.
    """
    # --- Lecture du fichier source ---
    logger.info(f"Lecture du fichier : {RAW_SPORT_PATH.name}")
    df = pd.read_excel(RAW_SPORT_PATH)
    logger.info(f"  {len(df)} lignes lues, {len(df.columns)} colonnes")

    # --- Hachage SHA-256 du fichier source ---
    current_hash = compute_file_hash(RAW_SPORT_PATH)
    logger.info(f"  Hash SHA-256 : {current_hash[:12]}...")

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

    # --- Insertion en base ---
    conn = get_connection()
    cursor = conn.cursor()

    try:
        ids_in_xlsx = [int(row["id_salarie"]) for _, row in df.iterrows()]

        # 1. UPSERT staging.pratiques_declarees
        upsert_sql = """
            INSERT INTO staging.pratiques_declarees (id_salarie, pratique_sport)
            VALUES (%s, %s)
            ON CONFLICT (id_salarie) DO UPDATE SET
                pratique_sport = EXCLUDED.pratique_sport;
        """
        nb_inserts = 0
        for _, row in df.iterrows():
            cursor.execute(upsert_sql, (
                int(row["id_salarie"]),
                row["pratique_sport"],
            ))
            nb_inserts += 1

        # 2. Suppression des lignes absentes du XLSX (synchronisation complete)
        cursor.execute(
            "DELETE FROM staging.pratiques_declarees WHERE id_salarie != ALL(%s)",
            (ids_in_xlsx,)
        )
        nb_deleted = cursor.rowcount
        if nb_deleted > 0:
            logger.info(f"  {nb_deleted} pratique(s) supprimee(s) (absentes du fichier source)")

        # 3. Mise a jour du hachage dans meta.pipeline_state
        cursor.execute("""
            INSERT INTO meta.pipeline_state (file_name, file_hash, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (file_name) DO UPDATE SET
                file_hash  = EXCLUDED.file_hash,
                updated_at = NOW();
        """, (RAW_SPORT_PATH.name, current_hash))
        logger.info("  Hash enregistre dans meta.pipeline_state")

        conn.commit()
        logger.info(f"  {nb_inserts} lignes upsertees dans staging.pratiques_declarees")
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
