"""
config.py – Constantes metier et parametres centraux du projet

Centralise toutes les valeurs qui pourraient etre modifiees sans
toucher au code metier (seuils, taux, chemins, parametres de simulation).
Les modules importent ces constantes au lieu de les definir localement.

Utilisation :
    from src.config import TAUX_PRIME, SEUILS_DISTANCE, ...
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins du projet
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Fichiers sources (couche raw sur disque, jamais copies en base)
RAW_RH_PATH = PROJECT_ROOT / "data" / "RAW" / "Données+RH.xlsx"
RAW_SPORT_PATH = PROJECT_ROOT / "data" / "RAW" / "Données+Sportive.xlsx"

# Repertoire d'exports
EXPORT_DIR = PROJECT_ROOT / "data" / "exports"
SLACK_EXPORT_PATH = EXPORT_DIR / "slack_messages.json"

# ---------------------------------------------------------------------------
# Parametres de connexion (charges depuis .env par connexion.py)
# Documentes ici pour reference
# ---------------------------------------------------------------------------

# POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
# GOOGLE_MAPS_API_KEY, ENTREPRISE_ADRESSE

# ---------------------------------------------------------------------------
# Adresse de l'entreprise
# ---------------------------------------------------------------------------

ENTREPRISE_ADRESSE = "1362 Av. des Platanes, 34970 Lattes"

# Coordonnees GPS de l'entreprise (fallback haversine)
ENTREPRISE_LAT = 43.5676
ENTREPRISE_LON = 3.9070

# ---------------------------------------------------------------------------
# Regles metier – Prime sportive
# ---------------------------------------------------------------------------

# Taux de la prime : 5 % du salaire brut annuel
TAUX_PRIME = 0.05

# Seuils de distance domicile-bureau par moyen de deplacement (en km)
# Seuls ces moyens sont eligibles a la prime sportive
SEUILS_DISTANCE = {
    "Marche/running": 15.0,
    "Vélo/Trottinette/Autres": 25.0,
}

# Moyens de deplacement ouvrant droit a la prime
MODES_ELIGIBLES = set(SEUILS_DISTANCE.keys())

# ---------------------------------------------------------------------------
# Regles metier – Bien-etre
# ---------------------------------------------------------------------------

# Nombre minimum d'activites sportives sur 12 mois pour etre eligible
SEUIL_ACTIVITES_BIEN_ETRE = 15

# Nombre de jours bien-etre accordes si le seuil est atteint
NB_JOURS_BIEN_ETRE = 5

# ---------------------------------------------------------------------------
# Parametres de simulation Strava
# ---------------------------------------------------------------------------

# Plage du nombre d'activites par salarie sur 12 mois
NB_ACTIVITES_MIN = 5
NB_ACTIVITES_MAX = 40

# Graine aleatoire par defaut (reproductibilite)
DEFAULT_SEED = 42

# ---------------------------------------------------------------------------
# Colonnes RGPD a supprimer lors de l'ingestion RH
# ---------------------------------------------------------------------------

COLONNES_RGPD_A_SUPPRIMER = ["Nom", "Prénom", "Date de naissance"]

# Mapping colonnes XLSX -> colonnes staging
MAPPING_COLONNES_RH = {
    "ID salarié": "id_salarie",
    "BU": "departement",
    "Date d'embauche": "date_embauche",
    "Salaire brut": "salaire_brut",
    "Type de contrat": "type_contrat",
    "Nombre de jours de CP": "nb_jours_cp",
    "Adresse du domicile": "adresse_domicile",
    "Moyen de déplacement": "moyen_deplacement",
}

# Corrections de typos connues dans les donnees sportives
TYPOS_SPORT = {
    "Runing": "Running",
}

# ---------------------------------------------------------------------------
# Liste des 15 sports valides (coherent avec generate_strava.py)
# ---------------------------------------------------------------------------

SPORTS_VALIDES = {
    "Running", "Randonnée", "Tennis", "Natation", "Football", "Rugby",
    "Badminton", "Voile", "Boxe", "Judo", "Escalade", "Triathlon",
    "Tennis de table", "Équitation", "Basketball",
}
