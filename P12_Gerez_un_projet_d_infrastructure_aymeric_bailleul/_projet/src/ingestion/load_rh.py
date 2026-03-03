"""
load_rh.py – Ingestion des donnees RH (XLSX -> staging.employes)

Lit le fichier Donnees+RH.xlsx, anonymise en memoire (suppression
des colonnes Nom, Prenom, Date de naissance conformement au RGPD),
puis insere les 8 colonnes restantes dans staging.employes.

Architecture (Privacy by Design) :
  - Le XLSX fait office de couche raw (jamais copie en base)
  - Le pipeline lit, anonymise en memoire, insere directement dans staging

Utilisation :
    python -m src.ingestion.load_rh
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
RAW_RH_PATH = _PROJECT_ROOT / "data" / "RAW" / "Données+RH.xlsx"

# Colonnes personnelles a supprimer (anonymisation RGPD)
COLONNES_A_SUPPRIMER = ["Nom", "Prénom", "Date de naissance"]

# Mapping colonnes XLSX -> colonnes staging (renommage pour la base)
MAPPING_COLONNES = {
    "ID salarié": "id_salarie",
    "BU": "departement",
    "Date d'embauche": "date_embauche",
    "Salaire brut": "salaire_brut",
    "Type de contrat": "type_contrat",
    "Nombre de jours de CP": "nb_jours_cp",
    "Adresse du domicile": "adresse_domicile",
    "Moyen de déplacement": "moyen_deplacement",
}


def load_rh_to_staging():
    """
    Charge les donnees RH depuis le XLSX, anonymise en memoire,
    puis insere dans staging.employes.

    Returns
    -------
    int
        Nombre de lignes inserees.
    """
    # --- Lecture du fichier source ---
    logger.info(f"Lecture du fichier : {RAW_RH_PATH.name}")
    df = pd.read_excel(RAW_RH_PATH)
    logger.info(f"  {len(df)} lignes lues, {len(df.columns)} colonnes")

    # --- Anonymisation : suppression des colonnes personnelles ---
    df = df.drop(columns=COLONNES_A_SUPPRIMER)
    logger.info(f"  Anonymisation : colonnes supprimees ({', '.join(COLONNES_A_SUPPRIMER)})")

    # --- Renommage des colonnes pour correspondre au schema staging ---
    df = df.rename(columns=MAPPING_COLONNES)
    logger.info(f"  Colonnes renommees : {list(df.columns)}")

    # --- Conversion des types ---
    df["date_embauche"] = pd.to_datetime(df["date_embauche"]).dt.date
    df["salaire_brut"] = df["salaire_brut"].astype(float)
    df["nb_jours_cp"] = df["nb_jours_cp"].astype(int)

    # --- Nettoyage des chaines (strip + standardisation) ---
    for col in ["departement", "type_contrat", "adresse_domicile", "moyen_deplacement"]:
        df[col] = df[col].str.strip()

    # --- Insertion en base ---
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Vider la table avant insertion (idempotence du pipeline)
        cursor.execute("TRUNCATE TABLE staging.employes;")
        logger.info("  Table staging.employes videe (TRUNCATE)")

        # Insertion ligne par ligne
        insert_sql = """
            INSERT INTO staging.employes
                (id_salarie, departement, date_embauche, salaire_brut,
                 type_contrat, nb_jours_cp, adresse_domicile, moyen_deplacement)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        nb_inserts = 0
        for _, row in df.iterrows():
            cursor.execute(insert_sql, (
                int(row["id_salarie"]),
                row["departement"],
                row["date_embauche"],
                float(row["salaire_brut"]),
                row["type_contrat"],
                int(row["nb_jours_cp"]),
                row["adresse_domicile"],
                row["moyen_deplacement"],
            ))
            nb_inserts += 1

        conn.commit()
        logger.info(f"  {nb_inserts} lignes inserees dans staging.employes")
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
    load_rh_to_staging()
