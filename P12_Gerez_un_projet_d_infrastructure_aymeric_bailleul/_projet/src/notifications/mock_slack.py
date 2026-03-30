"""
mock_slack.py – Simulation des notifications Slack

Genere un message de felicitation pour chaque activite sportive
enregistree dans staging.activites_strava, au format demande par
Juliette (responsable RH / bien-etre).

Acces aux donnees :
  - Les activites sont lues depuis staging.activites_strava
  - Les prenoms/noms sont joints depuis rh_prive.identites
    via role_rh_admin (acces nominal autorise pour les notifications internes)
  - Les messages sont exportes dans data/exports/slack_messages.json

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
        "Bravo {prenom} ! Tu viens de courir {distance_km} km en {duree_min} min !",
        "Superbe course {prenom} {nom} ! {distance_km} km parcourus en {duree_min} min !",
        "Bien joue {prenom} ! Encore {distance_km} km de running aujourd'hui !",
    ],
    "Randonnée": [
        "Magnifique {prenom} ! Une randonnee de {distance_km} km terminee !",
        "Bravo {prenom} {nom} ! {distance_km} km en pleine nature en {duree_min} min !",
        "Quelle balade {prenom} ! {distance_km} km de randonnee, chapeau !",
    ],
    "Tennis": [
        "Ace {prenom} ! Seance de tennis de {duree_min} min validee !",
        "Bravo {prenom} {nom} ! {distance_km} km parcourus sur le court en {duree_min} min !",
    ],
    "Natation": [
        "Splendide {prenom} ! {distance_km} km en natation, {duree_min} min dans l'eau !",
        "Bravo {prenom} {nom} ! Belle seance de natation : {distance_km} km nages !",
    ],
    "Football": [
        "Goal {prenom} ! Match de foot : {distance_km} km parcourus en {duree_min} min !",
        "Bravo {prenom} {nom} ! Quelle seance de football aujourd'hui !",
    ],
    "Rugby": [
        "Essai transforme {prenom} ! {distance_km} km sur le terrain en {duree_min} min !",
        "Bravo {prenom} {nom} ! Solide seance de rugby !",
    ],
    "Badminton": [
        "Smash {prenom} ! Seance de badminton : {duree_min} min d'effort !",
        "Bravo {prenom} {nom} ! {distance_km} km de courts en badminton !",
    ],
    "Voile": [
        "Bon vent {prenom} ! {distance_km} km en voile, {duree_min} min sur l'eau !",
        "Bravo {prenom} {nom} ! Navigation de {distance_km} km terminee !",
    ],
    "Boxe": [
        "Uppercut {prenom} ! {duree_min} min de boxe intense !",
        "Bravo {prenom} {nom} ! Seance de boxe de {duree_min} min validee !",
    ],
    "Judo": [
        "Ippon {prenom} ! {duree_min} min de judo au dojo !",
        "Bravo {prenom} {nom} ! Belle seance de judo aujourd'hui !",
    ],
    "Escalade": [
        "Sommet atteint {prenom} ! {distance_km} km de grimpe en {duree_min} min !",
        "Bravo {prenom} {nom} ! Seance d'escalade de {duree_min} min terminee !",
    ],
    "Triathlon": [
        "Triple bravo {prenom} ! {distance_km} km de triathlon en {duree_min} min !",
        "Incroyable {prenom} {nom} ! Triathlon de {distance_km} km boucle !",
    ],
    "Tennis de table": [
        "Top spin {prenom} ! {duree_min} min de tennis de table !",
        "Bravo {prenom} {nom} ! Seance de ping-pong validee !",
    ],
    "Équitation": [
        "Au galop {prenom} ! {distance_km} km en equitation, {duree_min} min en selle !",
        "Bravo {prenom} {nom} ! Belle balade equestre de {distance_km} km !",
    ],
    "Basketball": [
        "Panier {prenom} ! {distance_km} km parcourus en basketball, {duree_min} min !",
        "Bravo {prenom} {nom} ! Seance de basket de {duree_min} min terminee !",
    ],
}

# Template generique si le sport n'est pas dans la liste
MESSAGES_GENERIQUES = [
    "Bravo {prenom} ! {distance_km} km de {sport} en {duree_min} min !",
    "Bien joue {prenom} {nom} ! Seance de {sport} terminee : {distance_km} km, {duree_min} min !",
]


# ---------------------------------------------------------------------------
# Generation des messages
# ---------------------------------------------------------------------------

def format_message(prenom, nom, type_sport, distance_m, duree_s, commentaire=None, seed=None):
    """
    Genere un message de felicitation pour une activite sportive.

    Parameters
    ----------
    prenom : str
    nom : str
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
        prenom=prenom,
        nom=nom,
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
    # Connexion role_rh_admin : necessaire pour joindre rh_prive.identites (noms/prenoms)
    conn = get_connection(role="rh_admin")
    cursor = conn.cursor()

    try:
        # Lecture des activites + identites nominatives en une seule requete
        # La jointure LEFT JOIN garantit qu'une activite sans identite (cas improbable)
        # ne serait pas silencieusement exclue — le nom serait alors "Inconnu"
        query = """
            SELECT a.id_activite, a.id_salarie, a.date_debut, a.type_sport,
                   a.distance_m, a.duree_s, a.commentaire,
                   COALESCE(i.prenom, 'Inconnu') AS prenom,
                   COALESCE(i.nom, 'Inconnu')   AS nom
            FROM staging.activites_strava a
            LEFT JOIN rh_prive.identites i USING (id_salarie)
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
        for id_activite, id_salarie, date_debut, type_sport, distance_m, duree_s, commentaire, prenom, nom in activites:
            msg_text = format_message(
                prenom=prenom,
                nom=nom,
                type_sport=type_sport,
                distance_m=distance_m,
                duree_s=duree_s,
                commentaire=commentaire,
            )

            messages.append({
                "channel": "#sport-avantages",
                "id_activite": id_activite,
                "id_salarie": id_salarie,
                "prenom": prenom,
                "nom": nom,
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
    logger.info(f"Termine : {len(messages)} messages generes au total")
