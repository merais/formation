"""
mock_slack.py – Simulation des notifications Slack

Genere un message de felicitation pour chaque activite sportive
enregistree dans staging.activites_strava, au format demande par
Juliette (responsable RH / bien-etre).

Conformite RGPD :
  - Utilise uniquement l'ID salarie (jamais de Nom/Prenom)
  - Les messages sont loggues dans data/exports/slack_messages.json

Utilisation :
    python -m src.notifications.mock_slack
    python -m src.notifications.mock_slack --limit 10   # 10 derniers messages
"""

import argparse
import json
import logging
import random
from datetime import datetime
from pathlib import Path

from src.db.connexion import get_connection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Chemin de sortie
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXPORT_DIR = _PROJECT_ROOT / "data" / "exports"
EXPORT_PATH = EXPORT_DIR / "slack_messages.json"

# ---------------------------------------------------------------------------
# Templates de messages par type de sport
# Placeholders : {id}, {distance_km}, {duree_min}, {sport}, {commentaire}
# ---------------------------------------------------------------------------

MESSAGES_TEMPLATES = {
    "Running": [
        "Bravo salarie ID {id} ! Tu viens de courir {distance_km} km en {duree_min} min !",
        "Superbe course salarie ID {id} ! {distance_km} km parcourus en {duree_min} min !",
        "Bien joue salarie ID {id} ! Encore {distance_km} km de running aujourd'hui !",
    ],
    "Randonnée": [
        "Magnifique salarie ID {id} ! Une randonnee de {distance_km} km terminee !",
        "Bravo salarie ID {id} ! {distance_km} km en pleine nature en {duree_min} min !",
        "Quelle balade salarie ID {id} ! {distance_km} km de randonnee, chapeau !",
    ],
    "Tennis": [
        "Ace salarie ID {id} ! Seance de tennis de {duree_min} min validee !",
        "Bravo salarie ID {id} ! {distance_km} km parcourus sur le court en {duree_min} min !",
    ],
    "Natation": [
        "Splendide salarie ID {id} ! {distance_km} km en natation, {duree_min} min dans l'eau !",
        "Bravo salarie ID {id} ! Belle seance de natation : {distance_km} km nages !",
    ],
    "Football": [
        "Goal salarie ID {id} ! Match de foot : {distance_km} km parcourus en {duree_min} min !",
        "Bravo salarie ID {id} ! Quelle seance de football aujourd'hui !",
    ],
    "Rugby": [
        "Essai transforme salarie ID {id} ! {distance_km} km sur le terrain en {duree_min} min !",
        "Bravo salarie ID {id} ! Solide seance de rugby !",
    ],
    "Badminton": [
        "Smash salarie ID {id} ! Seance de badminton : {duree_min} min d'effort !",
        "Bravo salarie ID {id} ! {distance_km} km de courts en badminton !",
    ],
    "Voile": [
        "Bon vent salarie ID {id} ! {distance_km} km en voile, {duree_min} min sur l'eau !",
        "Bravo salarie ID {id} ! Navigation de {distance_km} km terminee !",
    ],
    "Boxe": [
        "Uppercut salarie ID {id} ! {duree_min} min de boxe intense !",
        "Bravo salarie ID {id} ! Seance de boxe de {duree_min} min validee !",
    ],
    "Judo": [
        "Ippon salarie ID {id} ! {duree_min} min de judo au dojo !",
        "Bravo salarie ID {id} ! Belle seance de judo aujourd'hui !",
    ],
    "Escalade": [
        "Sommet atteint salarie ID {id} ! {distance_km} km de grimpe en {duree_min} min !",
        "Bravo salarie ID {id} ! Seance d'escalade de {duree_min} min terminee !",
    ],
    "Triathlon": [
        "Triple bravo salarie ID {id} ! {distance_km} km de triathlon en {duree_min} min !",
        "Incroyable salarie ID {id} ! Triathlon de {distance_km} km boucle !",
    ],
    "Tennis de table": [
        "Top spin salarie ID {id} ! {duree_min} min de tennis de table !",
        "Bravo salarie ID {id} ! Seance de ping-pong validee !",
    ],
    "Équitation": [
        "Au galop salarie ID {id} ! {distance_km} km en equitation, {duree_min} min en selle !",
        "Bravo salarie ID {id} ! Belle balade equestre de {distance_km} km !",
    ],
    "Basketball": [
        "Panier salarie ID {id} ! {distance_km} km parcourus en basketball, {duree_min} min !",
        "Bravo salarie ID {id} ! Seance de basket de {duree_min} min terminee !",
    ],
}

# Template generique si le sport n'est pas dans la liste
MESSAGES_GENERIQUES = [
    "Bravo salarie ID {id} ! {distance_km} km de {sport} en {duree_min} min !",
    "Bien joue salarie ID {id} ! Seance de {sport} terminee : {distance_km} km, {duree_min} min !",
]


# ---------------------------------------------------------------------------
# Generation des messages
# ---------------------------------------------------------------------------

def format_message(id_salarie, type_sport, distance_m, duree_s, commentaire=None, seed=None):
    """
    Genere un message de felicitation pour une activite sportive.

    Parameters
    ----------
    id_salarie : int
    type_sport : str
    distance_m : float
        Distance en metres.
    duree_s : int
        Duree en secondes.
    commentaire : str or None
    seed : int or None
        Graine pour le choix du template (reproductibilite).

    Returns
    -------
    str
        Message de felicitation formate.
    """
    distance_km = round(distance_m / 1000.0, 1)
    duree_min = round(duree_s / 60.0)

    templates = MESSAGES_TEMPLATES.get(type_sport, MESSAGES_GENERIQUES)

    if seed is not None:
        rng = random.Random(seed)
        template = rng.choice(templates)
    else:
        template = random.choice(templates)

    message = template.format(
        id=id_salarie,
        distance_km=distance_km,
        duree_min=duree_min,
        sport=type_sport,
        commentaire=commentaire or "",
    )

    return message


def generate_slack_messages(limit=None):
    """
    Genere les messages Slack pour toutes les activites staging
    et les exporte en JSON.

    Parameters
    ----------
    limit : int or None
        Si renseigne, ne traite que les N dernieres activites.

    Returns
    -------
    list of dict
        Liste des messages generes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Lecture des activites depuis staging
        query = """
            SELECT a.id_activite, a.id_salarie, a.date_debut, a.type_sport,
                   a.distance_m, a.duree_s, a.commentaire
            FROM staging.activites_strava a
            ORDER BY a.date_debut DESC
        """
        if limit:
            query += f" LIMIT {int(limit)}"
        query += ";"

        cursor.execute(query)
        activites = cursor.fetchall()
        logger.info(f"{len(activites)} activites lues depuis staging.activites_strava")

        # Generation des messages
        messages = []
        for id_activite, id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire in activites:
            msg_text = format_message(
                id_salarie=id_salarie,
                type_sport=type_sport,
                distance_m=distance_m,
                duree_s=duree_s,
                commentaire=commentaire,
            )

            messages.append({
                "channel": "#sport-avantages",
                "id_activite": id_activite,
                "id_salarie": id_salarie,
                "date_activite": date_debut.isoformat(),
                "type_sport": type_sport,
                "message": msg_text,
                "timestamp_envoi": datetime.now().isoformat(),
                "statut": "mock_envoye",
            })

        logger.info(f"{len(messages)} messages Slack generes")

        # Export JSON
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        with open(EXPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        logger.info(f"Messages exportes dans {EXPORT_PATH}")

        # Afficher quelques exemples
        for msg in messages[:5]:
            logger.info(f"  [SLACK] {msg['message']}")

        return messages

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


# ---------------------------------------------------------------------------
# Point d'entree CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generation des notifications Slack (mock)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nombre maximum d'activites a traiter (defaut : toutes)",
    )
    args = parser.parse_args()
    messages = generate_slack_messages(limit=args.limit)
    logger.info(f"Terminé : {len(messages)} messages generes au total")
