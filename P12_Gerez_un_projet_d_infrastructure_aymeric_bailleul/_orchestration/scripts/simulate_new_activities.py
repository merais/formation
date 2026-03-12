"""
simulate_new_activities.py – Simulation d'un feed Strava incremental (Kestra standalone)

Insere N nouvelles activites aleatoires dans raw.activites_strava SANS tronquer
la table, simulant ainsi un flux Strava temps reel entre deux executions du pipeline.
La colonne inserted_at est renseignee automatiquement via DEFAULT NOW().

NE MET PAS A JOUR le watermark — c'est le flow Kestra qui le fait apres avoir
traite les donnees (dans la tache update_strava_watermark).

Variables d'environnement requises :
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

Variable optionnelle :
  NB_ACTIVITES : nombre d'activites a inserer (defaut : aleatoire entre 1 et 10)
"""

import os
import random
from datetime import date, timedelta

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


ACTIVITES = [
    "Running", "Randonnée", "Tennis", "Natation", "Football", "Rugby",
    "Badminton", "Voile", "Boxe", "Judo", "Escalade", "Triathlon",
    "Tennis de table", "Équitation", "Basketball",
]

INSERT_ACTIVITES = """
INSERT INTO raw.activites_strava
    (id_salarie, date_debut, type_sport, duree_s, distance_m)
SELECT
    e.id_salarie,
    %s::timestamp,
    %s,
    %s,
    %s
FROM staging.employes e
WHERE e.id_salarie = %s
  AND e.actif = TRUE;
"""



# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def get_ids_salaries_actifs(cursor) -> list:
    cursor.execute("SELECT id_salarie FROM staging.employes WHERE actif = TRUE")
    return [row[0] for row in cursor.fetchall()]


def random_date_recent(days_back: int = 30) -> date:
    return date.today() - timedelta(days=random.randint(0, days_back))


def simulate(nb_activites: int = 5) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    inserted = 0

    try:
        ids = get_ids_salaries_actifs(cursor)
        if not ids:
            print("[simulate] Aucun salarie actif dans staging.employes.")
            return 0

        for _ in range(nb_activites):
            id_salarie = random.choice(ids)
            date_activite = random_date_recent()
            type_activite = random.choice(ACTIVITES)
            duree = random.randint(20, 120) * 60        # minutes → secondes
            distance = round(random.uniform(1.0, 42.0) * 1000, 1)  # km → metres

            cursor.execute(
                INSERT_ACTIVITES,
                (date_activite, type_activite, duree, distance, id_salarie),
            )
            if cursor.rowcount > 0:
                inserted += 1

        conn.commit()
        print(f"[simulate] {inserted}/{nb_activites} activites inserees.")
        return inserted

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
    nb = int(os.environ.get("NB_ACTIVITES", random.randint(1, 10)))
    simulate(nb)


if __name__ == "__main__":
    main()
