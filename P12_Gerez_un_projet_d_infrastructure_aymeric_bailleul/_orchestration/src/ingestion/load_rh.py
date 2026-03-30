"""
load_rh.py – Ingestion des donnees RH (XLSX -> staging.employes + rh_prive.identites)

Lit le fichier Donnees+RH.xlsx, puis :
  1. Calcule le hash SHA-256 du fichier (pour detection de changements)
  2. Extrait les donnees nominatives (Nom, Prenom, Date de naissance)
     et les UPSERT dans rh_prive.identites (acces restreint RGPD)
  3. Supprime les colonnes personnelles en memoire (anonymisation)
  4. UPSERT les 9 colonnes anonymisees dans staging.employes (incl. actif)
  5. Soft-delete des employes absents du fichier (actif = FALSE)
  6. Met a jour le hash dans meta.pipeline_state

Architecture (Privacy by Design) :
  - staging.employes.actif gere les departs sans supprimer l historique
  - meta.pipeline_state stocke le hash pour Kestra (detection changements)

Utilisation :
    python -m src.ingestion.load_rh
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
RAW_RH_PATH = _xlsx_dir / "Données+RH.xlsx"

COLONNES_A_SUPPRIMER = ["Nom", "Prénom", "Date de naissance"]

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


def compute_file_hash(path: Path) -> str:
    """Calcule le hachage SHA-256 d un fichier (pour detection de modifications)."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_rh_to_staging():
    """
    Charge les donnees RH depuis le XLSX, anonymise en memoire,
    puis UPSERT dans staging.employes + soft-delete des absents.

    Returns
    -------
    dict
        Statistiques : inserts, updates, deactivated, hash.
    """
    # --- Lecture du fichier source ---
    logger.info(f"Lecture du fichier : {RAW_RH_PATH.name}")
    df = pd.read_excel(RAW_RH_PATH)
    logger.info(f"  {len(df)} lignes lues, {len(df.columns)} colonnes")

    # --- Hachage SHA-256 du fichier source ---
    current_hash = compute_file_hash(RAW_RH_PATH)
    logger.info(f"  Hash SHA-256 : {current_hash[:12]}...")

    # --- Extraction des identites AVANT anonymisation ---
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

    # --- Renommage et nettoyage ---
    df = df.rename(columns=MAPPING_COLONNES)
    df["date_embauche"] = pd.to_datetime(df["date_embauche"]).dt.date
    df["salaire_brut"] = df["salaire_brut"].astype(float)
    df["nb_jours_cp"] = df["nb_jours_cp"].astype(int)
    for col in ["departement", "type_contrat", "adresse_domicile", "moyen_deplacement"]:
        df[col] = df[col].str.strip()

    # --- Insertion en base ---
    conn = get_connection()
    cursor = conn.cursor()

    try:
        ids_in_xlsx = [int(row["id_salarie"]) for _, row in df.iterrows()]

        # 1. UPSERT staging.employes (actif = TRUE pour tous les employes du XLSX)
        upsert_employes_sql = """
            INSERT INTO staging.employes
                (id_salarie, departement, date_embauche, salaire_brut,
                 type_contrat, nb_jours_cp, adresse_domicile, moyen_deplacement, actif)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (id_salarie) DO UPDATE SET
                departement         = EXCLUDED.departement,
                date_embauche       = EXCLUDED.date_embauche,
                salaire_brut        = EXCLUDED.salaire_brut,
                type_contrat        = EXCLUDED.type_contrat,
                nb_jours_cp         = EXCLUDED.nb_jours_cp,
                adresse_domicile    = EXCLUDED.adresse_domicile,
                moyen_deplacement   = EXCLUDED.moyen_deplacement,
                actif               = TRUE
            RETURNING (xmax = 0) AS was_inserted;
        """
        nb_inserts = 0
        nb_updates = 0
        for _, row in df.iterrows():
            cursor.execute(upsert_employes_sql, (
                int(row["id_salarie"]),
                row["departement"],
                row["date_embauche"],
                float(row["salaire_brut"]),
                row["type_contrat"],
                int(row["nb_jours_cp"]),
                row["adresse_domicile"],
                row["moyen_deplacement"],
            ))
            was_inserted = cursor.fetchone()[0]
            if was_inserted:
                nb_inserts += 1
            else:
                nb_updates += 1
        logger.info(f"  staging.employes : {nb_inserts} inseres, {nb_updates} mis a jour")

        # 2. UPSERT rh_prive.identites (apres staging : respecte la FK)
        upsert_identites_sql = """
            INSERT INTO rh_prive.identites (id_salarie, nom, prenom, date_naissance)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_salarie) DO UPDATE SET
                nom            = EXCLUDED.nom,
                prenom         = EXCLUDED.prenom,
                date_naissance = EXCLUDED.date_naissance;
        """
        for _, row in df_identites.iterrows():
            cursor.execute(upsert_identites_sql, (
                int(row["id_salarie"]),
                row["nom"],
                row["prenom"],
                row["date_naissance"],
            ))
        logger.info(f"  rh_prive.identites : {len(df_identites)} upserts")

        # 3. Suppression des identites des employes retires du XLSX (RGPD)
        cursor.execute(
            "DELETE FROM rh_prive.identites WHERE id_salarie != ALL(%s)",
            (ids_in_xlsx,)
        )
        nb_deleted = cursor.rowcount
        if nb_deleted > 0:
            logger.info(f"  {nb_deleted} identite(s) supprimee(s) (employes retires du fichier)")

        # 4. Soft-delete des employes absents du XLSX (actif = FALSE)
        cursor.execute(
            "UPDATE staging.employes SET actif = FALSE WHERE id_salarie != ALL(%s)",
            (ids_in_xlsx,)
        )
        nb_deactivated = cursor.rowcount
        if nb_deactivated > 0:
            logger.info(f"  {nb_deactivated} employe(s) desactive(s) (absents du fichier source)")

        # 5. Mise a jour du hachage dans meta.pipeline_state
        cursor.execute("""
            INSERT INTO meta.pipeline_state (file_name, file_hash, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (file_name) DO UPDATE SET
                file_hash  = EXCLUDED.file_hash,
                updated_at = NOW();
        """, (RAW_RH_PATH.name, current_hash))
        logger.info("  Hash enregistre dans meta.pipeline_state")

        conn.commit()
        return {
            "inserts": nb_inserts,
            "updates": nb_updates,
            "deactivated": nb_deactivated,
            "hash": current_hash,
        }

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
