"""
reload_sport.py – Rechargement incremental pratiques sportives (Kestra standalone script)

Lit Donnees+Sportive.xlsx et effectue un UPSERT dans staging.pratiques_declarees.
Les lignes absentes du fichier sont supprimees (delete-absent). Met a jour
meta.pipeline_state avec le hash du fichier.

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

UPSERT_SPORT = """
INSERT INTO staging.pratiques_declarees
    (id_salarie, pratique_sport)
VALUES
    %s
ON CONFLICT (id_salarie) DO UPDATE SET
    pratique_sport = EXCLUDED.pratique_sport;
"""

DELETE_ABSENTS = """
DELETE FROM staging.pratiques_declarees
WHERE id_salarie != ALL(%s);
"""

UPDATE_PIPELINE_STATE = """
INSERT INTO meta.pipeline_state (file_name, file_hash, updated_at)
VALUES (%s, %s, NOW())
ON CONFLICT (file_name) DO UPDATE SET
    file_hash  = EXCLUDED.file_hash,
    updated_at = EXCLUDED.updated_at;
"""


def reload_sport(path: Path) -> dict:
    """
    Charge le fichier sportif dans la base.

    Retourne un dict avec rows, deleted, hash.
    """
    df = pd.read_excel(path)
    df = df.rename(columns={"ID salarié": "id_salarie", "Pratique d'un sport": "pratique_sport"})
    df["id_salarie"] = df["id_salarie"].astype(int)
    df["pratique_sport"] = df["pratique_sport"].fillna("Non déclaré").astype(str).str.strip()
    df["pratique_sport"] = df["pratique_sport"].replace({"Runing": "Running"})

    ids = list(df["id_salarie"].unique())
    file_hash = compute_file_hash(path)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        rows = [
            (
                int(row["id_salarie"]),
                row["pratique_sport"],
            )
            for _, row in df.iterrows()
        ]
        psycopg2.extras.execute_values(cursor, UPSERT_SPORT, rows)

        # Suppression des absents
        cursor.execute(DELETE_ABSENTS, (ids,))
        deleted = cursor.rowcount

        # Mise a jour watermark
        cursor.execute(UPDATE_PIPELINE_STATE, (path.name, file_hash))

        conn.commit()
        print(f"[reload_sport] {len(rows)} pratiques upserted, {deleted} supprimees — hash={file_hash[:12]}...")
        return {"rows": len(rows), "deleted": deleted, "hash": file_hash}

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
    path = data_dir / "Données+Sportive.xlsx"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    reload_sport(path)


if __name__ == "__main__":
    main()
