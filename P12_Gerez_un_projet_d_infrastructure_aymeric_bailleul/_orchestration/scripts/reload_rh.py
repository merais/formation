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
    (id_salarie, nom, prenom, poste, departement, salaire, date_embauche, actif)
VALUES
    %s
ON CONFLICT (id_salarie) DO UPDATE SET
    nom           = EXCLUDED.nom,
    prenom        = EXCLUDED.prenom,
    poste         = EXCLUDED.poste,
    departement   = EXCLUDED.departement,
    salaire       = EXCLUDED.salaire,
    date_embauche = EXCLUDED.date_embauche,
    actif         = EXCLUDED.actif;
"""

UPSERT_IDENTITES = """
INSERT INTO rh_prive.identites (id_salarie, email, telephone, adresse)
VALUES %s
ON CONFLICT (id_salarie) DO UPDATE SET
    email     = EXCLUDED.email,
    telephone = EXCLUDED.telephone,
    adresse   = EXCLUDED.adresse;
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
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    df["id_salarie"] = df["id_salarie"].astype(str).str.strip()
    df["nom"] = df["nom"].astype(str).str.strip()
    df["prenom"] = df["prenom"].astype(str).str.strip()
    df["poste"] = df["poste"].fillna("").astype(str).str.strip()
    df["departement"] = df["departement"].fillna("").astype(str).str.strip()
    df["salaire"] = pd.to_numeric(df["salaire"], errors="coerce")
    df["date_embauche"] = pd.to_datetime(df["date_embauche"], errors="coerce").dt.date

    ids = list(df["id_salarie"].unique())
    file_hash = compute_file_hash(path)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Employes
        employes_rows = [
            (
                row["id_salarie"],
                row["nom"],
                row["prenom"],
                row["poste"],
                row["departement"],
                row["salaire"],
                row["date_embauche"],
                True,
            )
            for _, row in df.iterrows()
        ]
        psycopg2.extras.execute_values(cursor, UPSERT_EMPLOYES, employes_rows)

        # Soft-delete absents
        cursor.execute(SOFT_DELETE, (ids,))
        deactivated = cursor.rowcount

        # Identites (si colonnes presentes)
        identite_cols = {"email", "telephone", "adresse"}
        if identite_cols.issubset(set(df.columns)):
            identite_rows = [
                (row["id_salarie"], row.get("email"), row.get("telephone"), row.get("adresse"))
                for _, row in df.iterrows()
            ]
            psycopg2.extras.execute_values(cursor, UPSERT_IDENTITES, identite_rows)

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
