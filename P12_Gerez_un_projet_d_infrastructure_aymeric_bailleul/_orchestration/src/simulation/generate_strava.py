"""
generate_strava.py – Generation de donnees Strava simulees

Genere des activites sportives fictives sur les 12 derniers mois
pour chaque salarie ayant declare une pratique sportive.
Les activites sont inserees dans raw.activites_strava.

Logique de simulation :
  - Seuls les salaries ayant une pratique declaree (hors "Non declare") generent des activites
  - Le nombre d'activites par salarie varie aleatoirement (5 a 40 par an)
  - Chaque sport a des parametres realistes (distance, duree, commentaires)
  - Les dates sont reparties sur les 12 derniers mois

Utilisation :
    python -m src.simulation.generate_strava
    python -m src.simulation.generate_strava --seed 42  # reproductibilite
"""

import argparse
import logging
import random
from datetime import datetime, timedelta

from src.db.connexion import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SPORTS_CONFIG = {
    "Running": {
        "distance_range": (3000, 15000),
        "vitesse_range": (2.0, 4.5),
        "commentaires": [
            "Sortie matinale", "Footing du dimanche", "Entrainement fractionne",
            "Course tranquille", "Seance tempo", "Sortie entre collegues", None,
        ],
    },
    "Randonnée": {
        "distance_range": (5000, 25000),
        "vitesse_range": (1.0, 1.8),
        "commentaires": [
            "Randonnee en garrigue", "Balade en montagne", "Sentier du littoral",
            "Sortie nature", "Boucle avec denivelé", None,
        ],
    },
    "Tennis": {
        "distance_range": (1500, 4000),
        "vitesse_range": (0.8, 1.5),
        "commentaires": [
            "Match en simple", "Double avec collegues", "Entrainement au club",
            "Tournoi interne", None,
        ],
    },
    "Natation": {
        "distance_range": (500, 3000),
        "vitesse_range": (0.8, 1.5),
        "commentaires": [
            "Seance en piscine", "Nage en eau libre", "Entrainement crawl",
            "Seance technique", None,
        ],
    },
    "Football": {
        "distance_range": (5000, 12000),
        "vitesse_range": (1.2, 2.5),
        "commentaires": [
            "Match du mercredi", "Entrainement collectif", "Tournoi inter-entreprises",
            "Petit match 5 contre 5", None,
        ],
    },
    "Rugby": {
        "distance_range": (4000, 10000),
        "vitesse_range": (1.0, 2.2),
        "commentaires": [
            "Entrainement au club", "Match amical", "Seance de touche",
            "Preparation physique", None,
        ],
    },
    "Badminton": {
        "distance_range": (1000, 3000),
        "vitesse_range": (0.6, 1.2),
        "commentaires": [
            "Seance en salle", "Tournoi interne", "Double mixte",
            "Entrainement libre", None,
        ],
    },
    "Voile": {
        "distance_range": (5000, 20000),
        "vitesse_range": (1.5, 4.0),
        "commentaires": [
            "Sortie en mer", "Regate du week-end", "Navigation cotiere",
            "Entrainement catamaran", None,
        ],
    },
    "Boxe": {
        "distance_range": (1000, 3000),
        "vitesse_range": (0.5, 1.0),
        "commentaires": [
            "Seance de sparring", "Entrainement au sac", "Shadow boxing",
            "Cours collectif", None,
        ],
    },
    "Judo": {
        "distance_range": (500, 2000),
        "vitesse_range": (0.4, 0.8),
        "commentaires": [
            "Cours au dojo", "Seance de randori", "Preparation competition",
            "Entrainement technique", None,
        ],
    },
    "Escalade": {
        "distance_range": (200, 1500),
        "vitesse_range": (0.1, 0.4),
        "commentaires": [
            "Seance en salle", "Bloc entre amis", "Voie en falaise",
            "Entrainement endurance", None,
        ],
    },
    "Triathlon": {
        "distance_range": (10000, 40000),
        "vitesse_range": (2.5, 5.0),
        "commentaires": [
            "Entrainement enchaine", "Seance natation + velo", "Sortie longue triathlon",
            "Preparation course", None,
        ],
    },
    "Tennis de table": {
        "distance_range": (500, 1500),
        "vitesse_range": (0.3, 0.8),
        "commentaires": [
            "Seance au club", "Tournoi du midi", "Entrainement libre", None,
        ],
    },
    "Équitation": {
        "distance_range": (3000, 15000),
        "vitesse_range": (1.5, 4.0),
        "commentaires": [
            "Balade a cheval", "Cours de dressage", "Sortie en exterieur",
            "Seance d'obstacle", None,
        ],
    },
    "Basketball": {
        "distance_range": (3000, 8000),
        "vitesse_range": (1.0, 2.0),
        "commentaires": [
            "Match entre collegues", "Entrainement au gymnase", "Tournoi inter-services",
            "Seance de tirs", None,
        ],
    },
}

NB_ACTIVITES_MIN = 5
NB_ACTIVITES_MAX = 40


def get_sportifs():
    """
    Recupere la liste des salaries actifs ayant une pratique sportive declaree.

    Returns
    -------
    list of tuple
        Liste de (id_salarie, pratique_sport) pour les sportifs actifs.
    """
    conn = get_connection()
    cursor = conn.cursor()
    # Jointure avec staging.employes pour ne prendre que les actifs
    cursor.execute("""
        SELECT p.id_salarie, p.pratique_sport
        FROM staging.pratiques_declarees p
        JOIN staging.employes e ON p.id_salarie = e.id_salarie
        WHERE p.pratique_sport != 'Non déclaré'
          AND e.actif = TRUE
        ORDER BY p.id_salarie;
    """)
    sportifs = cursor.fetchall()
    cursor.close()
    conn.close()
    return sportifs


def generate_activities(sportifs, seed=None):
    """
    Genere les activites Strava simulees pour chaque sportif.

    Parameters
    ----------
    sportifs : list of tuple
        Liste de (id_salarie, pratique_sport).
    seed : int, optional
        Graine pour le generateur aleatoire (reproductibilite).

    Returns
    -------
    list of tuple
        Liste de (id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire).
    """
    if seed is not None:
        random.seed(seed)

    date_fin = datetime.now()
    date_debut_periode = date_fin - timedelta(days=365)

    activites = []

    for id_salarie, sport in sportifs:
        config = SPORTS_CONFIG.get(sport, {
            "distance_range": (2000, 10000),
            "vitesse_range": (1.0, 3.0),
            "commentaires": ["Activite sportive", None],
        })

        nb_activites = random.randint(NB_ACTIVITES_MIN, NB_ACTIVITES_MAX)

        for _ in range(nb_activites):
            jours_offset = random.randint(0, 364)
            heure = random.randint(6, 20)
            minute = random.randint(0, 59)
            date_activite = date_debut_periode + timedelta(
                days=jours_offset, hours=heure, minutes=minute
            )

            dist_min, dist_max = config["distance_range"]
            distance_m = round(random.uniform(dist_min, dist_max), 1)

            vit_min, vit_max = config["vitesse_range"]
            vitesse = random.uniform(vit_min, vit_max)
            duree_s = int(distance_m / vitesse)

            commentaire = random.choice(config["commentaires"])

            activites.append((
                id_salarie,
                date_activite,
                sport,
                distance_m,
                duree_s,
                commentaire,
            ))

    logger.info(f"{len(activites)} activites generees pour {len(sportifs)} sportifs")
    return activites


def insert_activities(activites):
    """
    Insere les activites generees dans raw.activites_strava.
    Vide la table avant insertion (idempotence de la charge initiale).

    Parameters
    ----------
    activites : list of tuple
        Liste de (id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire).

    Returns
    -------
    int
        Nombre de lignes inserees.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("TRUNCATE TABLE raw.activites_strava RESTART IDENTITY;")
        logger.info("Table raw.activites_strava videe (TRUNCATE)")

        # inserted_at est rempli automatiquement par DEFAULT NOW()
        insert_sql = """
            INSERT INTO raw.activites_strava
                (id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        for activite in activites:
            cursor.execute(insert_sql, activite)

        conn.commit()
        logger.info(f"{len(activites)} lignes inserees dans raw.activites_strava")
        return len(activites)

    except Exception as err:
        conn.rollback()
        logger.error(f"Erreur lors de l'insertion : {err}")
        raise

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


def generate_and_load(seed=None):
    """
    Point d'entree principal : genere les activites et les charge en base.

    Parameters
    ----------
    seed : int, optional
        Graine pour le generateur aleatoire (reproductibilite).

    Returns
    -------
    int
        Nombre d'activites inserees.
    """
    sportifs = get_sportifs()
    logger.info(f"{len(sportifs)} salaries actifs avec pratique sportive declaree")

    if not sportifs:
        logger.warning("Aucun sportif trouve. Verifiez que staging.pratiques_declarees est charge.")
        return 0

    activites = generate_activities(sportifs, seed=seed)
    nb_inserts = insert_activities(activites)

    sports_uniques = set(a[2] for a in activites)
    logger.info(f"Recapitulatif : {nb_inserts} activites, {len(sportifs)} sportifs, {len(sports_uniques)} sports")

    return nb_inserts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generation de donnees Strava simulees (12 derniers mois)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Graine aleatoire pour la reproductibilite",
    )
    args = parser.parse_args()
    generate_and_load(seed=args.seed)
