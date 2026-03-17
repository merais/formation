"""
reload_rh.py – Rechargement incremental RH (Kestra standalone script)

Lit Donnees+RH.xlsx et effectue un UPSERT dans staging.employes et
rh_prive.identites. Les salaries absents du fichier sont marques inactifs
(soft-delete sur actif = FALSE). Met a jour meta.pipeline_state avec le hash
du fichier.

Variables d'environnement requises :
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
  DATA_DIR (dossier contenant les fichiers XLSX)
"""

import hashlib
import os
from pathlib import Path

import pandas as pd
import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def compute_file_hash(path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------

UPSERT_EMPLOYES = """
INSERT INTO staging.employes
    (id_salarie, departement, date_embauche, salaire_brut,
     type_contrat, nb_jours_cp, adresse_domicile, moyen_deplacement, actif)
VALUES
    %s
ON CONFLICT (id_salarie) DO UPDATE SET
    departement       = EXCLUDED.departement,
    date_embauche     = EXCLUDED.date_embauche,
    salaire_brut      = EXCLUDED.salaire_brut,
    type_contrat      = EXCLUDED.type_contrat,
    nb_jours_cp       = EXCLUDED.nb_jours_cp,
    adresse_domicile  = EXCLUDED.adresse_domicile,
    moyen_deplacement = EXCLUDED.moyen_deplacement,
    actif             = EXCLUDED.actif;
"""

UPSERT_IDENTITES = """
INSERT INTO rh_prive.identites (id_salarie, nom, prenom, date_naissance)
VALUES %s
ON CONFLICT (id_salarie) DO UPDATE SET
    nom            = EXCLUDED.nom,
    prenom         = EXCLUDED.prenom,
    date_naissance = EXCLUDED.date_naissance;
"""

SOFT_DELETE = """
UPDATE staging.employes
SET actif = FALSE
WHERE id_salarie != ALL(%s) AND actif = TRUE;
"""

UPDATE_PIPELINE_STATE = """
INSERT INTO meta.pipeline_state (file_name, file_hash, updated_at)
VALUES (%s, %s, NOW())
ON CONFLICT (file_name) DO UPDATE SET
    file_hash  = EXCLUDED.file_hash,
    updated_at = EXCLUDED.updated_at;
"""


def reload_rh(path: Path) -> dict:
    """
    Charge le fichier RH dans la base.

    Retourne un dict avec inserts, updates, deactivated, hash.
    """
    df = pd.read_excel(path)

    # --- Extraction des identités AVANT anonymisation ---
    df_identites = df[["ID salarié", "Nom", "Prénom", "Date de naissance"]].copy()
    df_identites = df_identites.rename(columns={
        "ID salarié":        "id_salarie",
        "Nom":               "nom",
        "Prénom":            "prenom",
        "Date de naissance": "date_naissance",
    })
    df_identites["id_salarie"] = df_identites["id_salarie"].astype(int)
    df_identites["nom"] = df_identites["nom"].astype(str).str.strip()
    df_identites["prenom"] = df_identites["prenom"].astype(str).str.strip()
    df_identites["date_naissance"] = pd.to_datetime(df_identites["date_naissance"]).dt.date

    # --- Anonymisation : suppression des colonnes personnelles ---
    df = df.drop(columns=["Nom", "Prénom", "Date de naissance"])

    # --- Renommage et nettoyage ---
    df = df.rename(columns={
        "ID salarié":              "id_salarie",
        "BU":                      "departement",
        "Date d'embauche":         "date_embauche",
        "Salaire brut":            "salaire_brut",
        "Type de contrat":         "type_contrat",
        "Nombre de jours de CP":   "nb_jours_cp",
        "Adresse du domicile":     "adresse_domicile",
        "Moyen de déplacement":    "moyen_deplacement",
    })
    df["id_salarie"] = df["id_salarie"].astype(int)
    df["date_embauche"] = pd.to_datetime(df["date_embauche"]).dt.date
    df["salaire_brut"] = df["salaire_brut"].astype(float)
    df["nb_jours_cp"] = df["nb_jours_cp"].astype(int)
    for col in ["departement", "type_contrat", "adresse_domicile", "moyen_deplacement"]:
        df[col] = df[col].astype(str).str.strip()

    ids = [int(x) for x in df["id_salarie"].unique()]
    file_hash = compute_file_hash(path)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Employes (anonymises)
        employes_rows = [
            (
                int(row["id_salarie"]),
                row["departement"],
                row["date_embauche"],
                float(row["salaire_brut"]),
                row["type_contrat"],
                int(row["nb_jours_cp"]),
                row["adresse_domicile"],
                row["moyen_deplacement"],
                True,
            )
            for _, row in df.iterrows()
        ]
        psycopg2.extras.execute_values(cursor, UPSERT_EMPLOYES, employes_rows)

        # Soft-delete absents
        cursor.execute(SOFT_DELETE, (ids,))
        deactivated = cursor.rowcount

        # Identites nominatives (rh_prive)
        identite_rows = [
            (
                int(row["id_salarie"]),
                row["nom"],
                row["prenom"],
                row["date_naissance"],
            )
            for _, row in df_identites.iterrows()
        ]
        psycopg2.extras.execute_values(cursor, UPSERT_IDENTITES, identite_rows)

        # Suppression RGPD des identites des employes retires du XLSX
        cursor.execute(
            "DELETE FROM rh_prive.identites WHERE id_salarie != ALL(%s)",
            (ids,)
        )

        # Mise a jour watermark
        cursor.execute(UPDATE_PIPELINE_STATE, (path.name, file_hash))

        conn.commit()
        print(f"[reload_rh] {len(employes_rows)} employes upserted, {deactivated} desactives — hash={file_hash[:12]}...")
        return {"rows": len(employes_rows), "deactivated": deactivated, "hash": file_hash}

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_dir = Path(os.environ.get("DATA_DIR", "/opt/data/RAW"))
    path = data_dir / "Données+RH.xlsx"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    reload_rh(path)


if __name__ == "__main__":
    main()
