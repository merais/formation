"""
check_changes.py – Detection des changements (Kestra standalone script)

Verifie si les fichiers XLSX sources ont change (via hash SHA-256 stocke dans
meta.pipeline_state) et si de nouvelles activites Strava ont ete inserees
(via watermark sur inserted_at).

Outputs Kestra (::{ "outputs": ... }::) :
  - rh_changed    : bool
  - sport_changed : bool
  - new_activities_count : int
  - should_run    : bool (True si au moins un changement)

Variables d'environnement requises :
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
  DATA_DIR (dossier contenant les fichiers XLSX)
"""

import hashlib
import json
import os
import sys
from pathlib import Path

import psycopg2

# ---------------------------------------------------------------------------
# Connexion PostgreSQL (standalone, sans le package src/)
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


def get_stored_hash(cursor, file_name: str):
    cursor.execute(
        "SELECT file_hash FROM meta.pipeline_state WHERE file_name = %s",
        (file_name,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_watermark(cursor) -> str:
    """Recupere le watermark de la derniere execution (max inserted_at traite)."""
    cursor.execute("SELECT watermark FROM meta.pipeline_state WHERE file_name = '_strava_watermark'")
    row = cursor.fetchone()
    return row[0] if row else None


def count_new_activities(cursor, watermark) -> int:
    """Compte les activites inserees apres le watermark."""
    if watermark is None:
        cursor.execute("SELECT COUNT(*) FROM raw.activites_strava")
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM raw.activites_strava WHERE inserted_at > %s",
            (watermark,)
        )
    return cursor.fetchone()[0]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data_dir = Path(os.environ.get("DATA_DIR", "/opt/data/RAW"))
    rh_path = data_dir / "Données+RH.xlsx"
    sport_path = data_dir / "Données+Sportive.xlsx"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Hash des fichiers XLSX
        rh_hash = compute_file_hash(rh_path) if rh_path.exists() else None
        sport_hash = compute_file_hash(sport_path) if sport_path.exists() else None

        stored_rh = get_stored_hash(cursor, rh_path.name)
        stored_sport = get_stored_hash(cursor, sport_path.name)

        rh_changed = (rh_hash != stored_rh) if rh_hash else False
        sport_changed = (sport_hash != stored_sport) if sport_hash else False

        # Nouvelles activites Strava
        watermark = get_watermark(cursor)
        new_activities_count = count_new_activities(cursor, watermark)

        should_run = rh_changed or sport_changed or (new_activities_count > 0)

        print(f"rh_changed={rh_changed}, sport_changed={sport_changed}, "
              f"new_activities={new_activities_count}, should_run={should_run}")

        # Output Kestra
        outputs = {
            "rh_changed": rh_changed,
            "sport_changed": sport_changed,
            "new_activities_count": new_activities_count,
            "should_run": should_run,
        }
        print(f'::{{"outputs": {json.dumps(outputs)}}}::')

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
