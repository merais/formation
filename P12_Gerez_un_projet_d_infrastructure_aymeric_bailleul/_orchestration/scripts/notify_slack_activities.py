"""
notify_slack_activities.py – Notifications Slack par nouvelle activite Strava

Pour chaque activite inseree dans raw.activites_strava depuis le dernier
watermark (meta.pipeline_state), envoie un message Slack personnalise et
aleatoire sur le channel sport via un Incoming Webhook.

Les messages suivent les exemples de la note de cadrage :
  "Bravo Juliette ! Tu viens de courir 10.8 km en 46 min ! Quelle energie !"
  "Magnifique Laurence ! Une randonnee de 10 km terminee ! (commentaire...)"

Doit etre execute AVANT la mise a jour du watermark (update_strava_watermark)
pour pouvoir detecter les activites nouvellement inserees.

Variables d'environnement requises :
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  SLACK_WEBHOOK_URL : URL complete du webhook Slack (resolue par secret Kestra)
"""

import json
import os
import random
import urllib.request
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Charge .env si disponible (execution locale uniquement — sans effet dans Kestra)
load_dotenv(Path(__file__).parent.parent / ".env")

# ---------------------------------------------------------------------------
# Templates de messages par type de sport
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, list[str]] = {
    "Running": [
        "Bravo {prenom} {nom} ! Tu viens de courir {distance_km} km en {duree_min} min ! Quelle energie !",
        "Superbe course {prenom} {nom} ! {distance_km} km parcourus en {duree_min} min !",
        "Bien joue {prenom} ! Encore {distance_km} km de running aujourd'hui, impressionnant !",
    ],
    "Randonnée": [
        "Magnifique {prenom} {nom} ! Une randonnee de {distance_km} km terminee en {duree_min} min !",
        "Bravo {prenom} {nom} ! {distance_km} km en pleine nature, quelle aventure !",
        "Quelle balade {prenom} {nom} ! {distance_km} km de randonnee en {duree_min} min, chapeau !",
    ],
    "Tennis": [
        "Ace {prenom} {nom} ! Seance de tennis de {duree_min} min validee, bravo !",
        "Belle smash {prenom} {nom} ! {duree_min} min sur le court, continue !",
        "Bravo {prenom} {nom} ! {duree_min} min de tennis aujourd'hui, super seance !",
    ],
    "Natation": [
        "Splendide {prenom} {nom} ! {distance_km} km en natation en {duree_min} min, magnifique !",
        "Bravo {prenom} {nom} ! Belle seance de natation : {distance_km} km nages !",
        "Aquatique {prenom} {nom} ! {distance_km} km dans l'eau en {duree_min} min, superbe !",
    ],
    "Football": [
        "But {prenom} {nom} ! Match de foot : {distance_km} km parcourus en {duree_min} min !",
        "Bravo {prenom} {nom} ! Quelle seance de football, {distance_km} km sur le terrain !",
        "En forme {prenom} {nom} ! {duree_min} min de football, chapeau !",
    ],
    "Rugby": [
        "Essai transforme {prenom} {nom} ! {distance_km} km sur le terrain en {duree_min} min !",
        "Bravo {prenom} {nom} ! Solide seance de rugby de {duree_min} min !",
        "Plaquage parfait {prenom} {nom} ! {distance_km} km de rugby, formidable !",
    ],
    "Badminton": [
        "Smash {prenom} {nom} ! Seance de badminton : {duree_min} min d'effort intense !",
        "Bravo {prenom} {nom} ! {duree_min} min de badminton aujourd'hui !",
        "Volant rapide {prenom} {nom} ! {duree_min} min sur le terrain, super !",
    ],
    "Voile": [
        "Bon vent {prenom} {nom} ! {distance_km} km en voile, {duree_min} min sur l'eau !",
        "Bravo {prenom} {nom} ! Navigation de {distance_km} km terminee, chapeau marin !",
        "Cap maintenu {prenom} {nom} ! {duree_min} min de voile et {distance_km} km parcourus !",
    ],
    "Boxe": [
        "Uppercut {prenom} {nom} ! {duree_min} min de boxe intense, bravo !",
        "Bravo {prenom} {nom} ! Seance de boxe de {duree_min} min validee, au top !",
        "Sur le ring {prenom} {nom} ! {duree_min} min de boxe aujourd'hui, impressionnant !",
    ],
    "Judo": [
        "Ippon {prenom} {nom} ! {duree_min} min de judo au dojo, bravo !",
        "Bravo {prenom} {nom} ! Belle seance de judo, {duree_min} min de pur effort !",
        "Tatami {prenom} {nom} ! {duree_min} min de judo aujourd'hui, continue !",
    ],
    "Escalade": [
        "Sommet atteint {prenom} {nom} ! {duree_min} min de grimpe, magnifique !",
        "Bravo {prenom} {nom} ! Seance d'escalade de {duree_min} min terminee !",
        "En hauteur {prenom} {nom} ! {duree_min} min d'escalade, chapeau !",
    ],
    "Triathlon": [
        "Triple bravo {prenom} {nom} ! {distance_km} km de triathlon en {duree_min} min !",
        "Incroyable {prenom} {nom} ! Triathlon de {distance_km} km boucle en {duree_min} min !",
        "Titan {prenom} {nom} ! {distance_km} km de triathlon accomplis, quelle performance !",
    ],
    "Tennis de table": [
        "Ping-pong champion {prenom} {nom} ! {duree_min} min de tennis de table, bravo !",
        "Bravo {prenom} {nom} ! {duree_min} min a la table de ping-pong, super seance !",
        "Reflexes affutes {prenom} {nom} ! {duree_min} min de tennis de table !",
    ],
    "Équitation": [
        "En selle {prenom} {nom} ! {distance_km} km a cheval en {duree_min} min, magnifique !",
        "Bravo {prenom} {nom} ! Belle seance d'equitation de {duree_min} min !",
        "Galop {prenom} {nom} ! {distance_km} km d'equitation, bravo cavalier·e !",
    ],
    "Basketball": [
        "Panier {prenom} {nom} ! {duree_min} min de basketball, quelle energie !",
        "Bravo {prenom} {nom} ! {duree_min} min sur le parquet, super seance !",
        "Dunk {prenom} {nom} ! {distance_km} km parcourus sur le terrain en {duree_min} min !",
    ],
}

TEMPLATE_DEFAUT = [
    "Bravo {prenom} {nom} ! Seance de {sport} terminee : {duree_min} min d'effort !",
    "Bien joue {prenom} {nom} ! {duree_min} min de {sport} aujourd'hui !",
]


def get_connection():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def get_watermark(cursor) -> str | None:
    cursor.execute(
        "SELECT watermark FROM meta.pipeline_state WHERE file_name = '_strava_watermark'"
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_new_activities(cursor, watermark) -> list[dict]:
    if watermark is None:
        print("[INFO] Pas de watermark — aucun message envoye.")
        return []

    cursor.execute(
        """
        SELECT
            a.type_sport,
            a.duree_s,
            a.distance_m,
            a.commentaire,
            COALESCE(i.prenom, 'Sportif') AS prenom,
            COALESCE(i.nom,    '')        AS nom
        FROM raw.activites_strava a
        LEFT JOIN rh_prive.identites i ON i.id_salarie = a.id_salarie
        WHERE a.inserted_at > %s
        ORDER BY a.inserted_at
        """,
        (watermark,),
    )
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def format_message(activity: dict) -> str:
    sport = activity["type_sport"]
    prenom = activity["prenom"]
    nom = activity["nom"]
    duree_min = round(activity["duree_s"] / 60) if activity["duree_s"] else 0
    distance_km = round(activity["distance_m"] / 1000, 1) if activity["distance_m"] else 0.0
    commentaire = (activity.get("commentaire") or "").strip()

    templates = TEMPLATES.get(sport, TEMPLATE_DEFAUT)
    template = random.choice(templates)

    try:
        message = template.format(
            prenom=prenom,
            nom=nom,
            sport=sport,
            duree_min=duree_min,
            distance_km=f"{distance_km:.1f}",
        )
    except KeyError:
        message = TEMPLATE_DEFAUT[0].format(prenom=prenom, nom=nom, sport=sport, duree_min=duree_min)

    if commentaire:
        message += f' ("{commentaire}")'

    return message


def send_slack_message(webhook_url: str, text: str) -> None:
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.getcode()
        if status != 200:
            print(f"[WARN] Slack a repondu HTTP {status}")


def main() -> None:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("[WARN] SLACK_WEBHOOK_URL non definie — notifications ignorees.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            watermark = get_watermark(cur)
            activities = get_new_activities(cur, watermark)
    finally:
        conn.close()

    if not activities:
        print("[INFO] Aucune nouvelle activite — aucun message Slack envoye.")
        return

    print(f"[INFO] {len(activities)} nouvelle(s) activite(s) — envoi des messages Slack...")
    for i, activity in enumerate(activities, 1):
        message = format_message(activity)
        try:
            send_slack_message(webhook_url, message)
            print(f"  [{i}/{len(activities)}] {activity['prenom']} ({activity['type_sport']}) → OK")
        except Exception as exc:
            print(f"  [{i}/{len(activities)}] Erreur Slack : {exc}")

    print("[INFO] Notifications Slack terminees.")


if __name__ == "__main__":
    main()
