"""
staging.py – Nettoyage des activites Strava (raw -> staging)

Lit les activites depuis raw.activites_strava, applique des controles
de coherence (types, dates, distances, durees), puis insere les
donnees nettoyees dans staging.activites_strava.

Utilisation :
    python -m src.transformation.staging
"""

import logging
from datetime import datetime, timedelta

from src.db.connexion import get_connection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Liste des types de sport valides (coherent avec generate_strava.py)
SPORTS_VALIDES = {
    "Running", "Randonnée", "Tennis", "Natation", "Football", "Rugby",
    "Badminton", "Voile", "Boxe", "Judo", "Escalade", "Triathlon",
    "Tennis de table", "Équitation", "Basketball",
}


def clean_strava_to_staging():
    """
    Nettoie les activites Strava (raw -> staging).
    Filtre les lignes invalides et insere dans staging.activites_strava.

    Controles appliques :
      - distance_m > 0
      - duree_s > 0
      - date_debut dans les 13 derniers mois (marge de securite)
      - type_sport dans la liste des sports valides
      - id_salarie present dans staging.employes

    Returns
    -------
    dict
        Statistiques du nettoyage (total, valides, rejetes, motifs).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # --- Lecture des activites brutes ---
        cursor.execute("SELECT id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire FROM raw.activites_strava;")
        raw_activities = cursor.fetchall()
        logger.info(f"{len(raw_activities)} activites lues depuis raw.activites_strava")

        # --- Lecture des IDs salaries valides ---
        cursor.execute("SELECT id_salarie FROM staging.employes;")
        ids_valides = {row[0] for row in cursor.fetchall()}

        # --- Date limite : 13 mois en arriere (395 jours) ---
        # On prend 13 mois (et non 12) comme marge de securite :
        # les activites sont generees sur 365 jours, ce seuil plus large
        # evite de rejeter des activites en bordure de periode
        date_limite = datetime.now() - timedelta(days=395)

        # --- Nettoyage ---
        activites_valides = []
        stats_rejet = {"distance_invalide": 0, "duree_invalide": 0, "date_invalide": 0, "sport_invalide": 0, "salarie_inconnu": 0}

        for id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire in raw_activities:
            # Controle distance
            if distance_m <= 0:
                stats_rejet["distance_invalide"] += 1
                continue

            # Controle duree
            if duree_s <= 0:
                stats_rejet["duree_invalide"] += 1
                continue

            # Controle date
            if date_debut < date_limite:
                stats_rejet["date_invalide"] += 1
                continue

            # Controle type de sport
            if type_sport not in SPORTS_VALIDES:
                stats_rejet["sport_invalide"] += 1
                continue

            # Controle ID salarie
            if id_salarie not in ids_valides:
                stats_rejet["salarie_inconnu"] += 1
                continue

            activites_valides.append((id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire))

        nb_rejetes = sum(stats_rejet.values())
        logger.info(f"{len(activites_valides)} activites valides, {nb_rejetes} rejetees")
        if nb_rejetes > 0:
            for motif, count in stats_rejet.items():
                if count > 0:
                    logger.warning(f"  Rejet '{motif}' : {count}")

        # --- Insertion dans staging ---
        cursor.execute("TRUNCATE TABLE staging.activites_strava RESTART IDENTITY;")
        logger.info("Table staging.activites_strava videe (TRUNCATE)")

        insert_sql = """
            INSERT INTO staging.activites_strava
                (id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        for activite in activites_valides:
            cursor.execute(insert_sql, activite)

        conn.commit()
        logger.info(f"{len(activites_valides)} lignes inserees dans staging.activites_strava")

        return {
            "total_raw": len(raw_activities),
            "valides": len(activites_valides),
            "rejetes": nb_rejetes,
            "details_rejet": stats_rejet,
        }

    except Exception as err:
        conn.rollback()
        logger.error(f"Erreur lors du nettoyage : {err}")
        raise

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


if __name__ == "__main__":
    clean_strava_to_staging()
