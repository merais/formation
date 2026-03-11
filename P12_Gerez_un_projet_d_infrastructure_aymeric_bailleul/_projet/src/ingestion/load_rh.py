"""
load_rh.py – Ingestion des donnees RH (XLSX -> staging.employes + rh_prive.identites)

Lit le fichier Donnees+RH.xlsx, puis :
  1. Extrait les donnees nominatives (Nom, Prenom, Date de naissance)
     et les insere dans rh_prive.identites (acces restreint RGPD)
  2. Supprime les colonnes personnelles en memoire (anonymisation)
  3. Insere les 8 colonnes anonymisees dans staging.employes

Architecture (Privacy by Design) :
  - Le XLSX fait office de couche raw (jamais copie tel quel en base)
  - Les donnees nominatives sont isolees dans rh_prive, accessible uniquement
    via role_rh_admin (principe du moindre privilege)
  - staging.employes ne contient aucune donnee permettant l'identification directe

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

    # --- Extraction des identites AVANT anonymisation ---
    # On conserve Nom/Prenom/DDN pour rh_prive.identites avant de les supprimer
    df_identites = df[["ID salarié", "Nom", "Prénom", "Date de naissance"]].copy()
    df_identites = df_identites.rename(columns={
        "ID salarié":        "id_salarie",
        "Nom":               "nom",
        "Prénom":            "prenom",
        "Date de naissance": "date_naissance",
    })
    df_identites["date_naissance"] = pd.to_datetime(df_identites["date_naissance"]).dt.date

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
        # Vider les deux tables en une seule instruction :
        # PostgreSQL bloque TRUNCATE de la table parent (employes) si la FK enfant (identites)
        # n'est pas videe dans le meme statement. TRUNCATE multi-tables resout le probleme.
        cursor.execute("TRUNCATE TABLE rh_prive.identites, staging.employes;")
        logger.info("  Tables rh_prive.identites et staging.employes videes (TRUNCATE)")

        # Insertion dans staging.employes (donnees anonymisees)
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
        logger.info(f"  {nb_inserts} lignes inserees dans staging.employes")

        # Insertion dans rh_prive.identites (nominatif, apres staging pour respecter la FK)
        insert_identites_sql = """
            INSERT INTO rh_prive.identites (id_salarie, nom, prenom, date_naissance)
            VALUES (%s, %s, %s, %s);
        """
        nb_identites = 0
        for _, row in df_identites.iterrows():
            cursor.execute(insert_identites_sql, (
                int(row["id_salarie"]),
                row["nom"],
                row["prenom"],
                row["date_naissance"],
            ))
            nb_identites += 1
        logger.info(f"  {nb_identites} identites inserees dans rh_prive.identites")

        conn.commit()
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
