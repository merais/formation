"""
main.py – Point d entree du projet dbt Sport Data

Lance le pipeline dbt complet (run + test) depuis la racine du projet.
Charge les variables d environnement depuis .env avant l execution.

Appel dbt :
    dbt run  --project-dir sport_data --profiles-dir .
    dbt test --project-dir sport_data --profiles-dir .

Venv attendu : C:/Users/aymer/.venvs/projet_dbt/Scripts/dbt.exe
(venv local cre via : python -m venv C:/Users/aymer/.venvs/projet_dbt)
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Charge le .env situe dans le meme dossier que main.py
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Repertoire du projet dbt (sport_data/) et du profiles.yml (repertoire courant)
PROJECT_DIR = Path(__file__).parent / "sport_data"
PROFILES_DIR = Path(__file__).parent

# Executable dbt (venv local hors Google Drive pour eviter les blocages Windows)
DBT_EXE = r"C:\Users\aymer\.venvs\projet_dbt\Scripts\dbt.exe"


def run_dbt(command: list[str]) -> int:
    """Execute une commande dbt et retourne le code de retour."""
    full_cmd = [
        DBT_EXE,
        *command,
        "--project-dir", str(PROJECT_DIR),
        "--profiles-dir", str(PROFILES_DIR),
    ]
    print(f"Execution : {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd)
    return result.returncode


def main():
    print("=== Pipeline dbt Sport Data ===")
    print(f"  Projet   : {PROJECT_DIR}")
    print(f"  Profiles : {PROFILES_DIR / 'profiles.yml'}")
    print()

    # 1. Execution des modeles (run)
    rc = run_dbt(["run"])
    if rc != 0:
        print(f"ERREUR dbt run (code {rc})")
        sys.exit(rc)

    # 2. Execution des tests (test)
    rc = run_dbt(["test"])
    if rc != 0:
        print(f"ERREUR dbt test (code {rc})")
        sys.exit(rc)

    print("\nPipeline dbt termine avec succes.")


if __name__ == "__main__":
    main()

