"""
distances.py – Calcul des distances domicile-bureau

Calcule la distance entre le domicile de chaque salarie et l'adresse
de l'entreprise, via l'API Google Maps Distance Matrix.
Fallback haversine si la cle API est absente ou en erreur.

Regles metier :
  - Marche / Running : distance max 15 km pour etre eligible
  - Velo / Trottinette / Autres : distance max 25 km pour etre eligible
  - vehicule thermique/electrique et transports en commun : non eligible a la prime sportive

Les resultats sont mis en cache dans une table temporaire pour eviter
les appels API repetitifs lors de re-executions.

Utilisation :
    python -m src.transformation.distances
"""

import logging
import math
import os
import time

import requests

from src.db.connexion import get_connection

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Cle API Google Maps (depuis .env, charge par connexion.py)
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Adresse de l'entreprise
ENTREPRISE_ADRESSE = os.getenv("ENTREPRISE_ADRESSE", "1362 Av. des Platanes, 34970 Lattes")

# URL de l'API Google Maps Distance Matrix
GOOGLE_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

# Seuils de distance par moyen de deplacement (en km)
SEUILS_DISTANCE = {
    "Marche/running": 15.0,
    "Vélo/Trottinette/Autres": 25.0,
}

# Moyens de deplacement eligibles a la prime sportive
MODES_ELIGIBLES = {"Marche/running", "Vélo/Trottinette/Autres"}

# Coordonnees de l'entreprise (pour le fallback haversine)
# 1362 Av. des Platanes, 34970 Lattes
ENTREPRISE_LAT = 43.5676
ENTREPRISE_LON = 3.9070

# Delai entre les appels API (secondes) pour respecter les limites
API_DELAY = 0.1


# ---------------------------------------------------------------------------
# Table de cache pour les distances calculees
# ---------------------------------------------------------------------------

SQL_CREATE_CACHE = """
CREATE TABLE IF NOT EXISTS staging.cache_distances (
    adresse_domicile    TEXT        PRIMARY KEY,
    distance_km         REAL,
    source_calcul       VARCHAR(20) NOT NULL  -- 'google_maps' ou 'haversine'
);
"""


def ensure_cache_table(cursor):
    """Cree la table de cache si elle n'existe pas."""
    cursor.execute(SQL_CREATE_CACHE)


def get_cached_distance(cursor, adresse):
    """
    Recupere une distance depuis le cache.

    Returns
    -------
    tuple (float, str) ou None
        (distance_km, source_calcul) si en cache, None sinon.
    """
    cursor.execute(
        "SELECT distance_km, source_calcul FROM staging.cache_distances WHERE adresse_domicile = %s;",
        (adresse,),
    )
    result = cursor.fetchone()
    return result if result else None


def save_to_cache(cursor, adresse, distance_km, source):
    """Enregistre une distance dans le cache."""
    cursor.execute(
        """
        INSERT INTO staging.cache_distances (adresse_domicile, distance_km, source_calcul)
        VALUES (%s, %s, %s)
        ON CONFLICT (adresse_domicile) DO UPDATE SET distance_km = %s, source_calcul = %s;
        """,
        (adresse, distance_km, source, distance_km, source),
    )


# ---------------------------------------------------------------------------
# Calcul de distance via Google Maps API
# ---------------------------------------------------------------------------

def distance_google_maps(adresse_domicile, adresse_entreprise=None):
    """
    Calcule la distance routiere via l'API Google Maps Distance Matrix.

    Parameters
    ----------
    adresse_domicile : str
        Adresse du domicile du salarie.
    adresse_entreprise : str, optional
        Adresse de l'entreprise (defaut : depuis .env).

    Returns
    -------
    float ou None
        Distance en km, ou None si l'appel echoue.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    if adresse_entreprise is None:
        adresse_entreprise = ENTREPRISE_ADRESSE

    try:
        response = requests.get(
            GOOGLE_MAPS_URL,
            params={
                "origins": adresse_domicile,
                "destinations": adresse_entreprise,
                "key": GOOGLE_MAPS_API_KEY,
                "mode": "driving",
                "language": "fr",
            },
            timeout=10,
        )
        data = response.json()

        if data.get("status") != "OK":
            logger.warning(f"API Google Maps status: {data.get('status')} pour '{adresse_domicile}'")
            return None

        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            logger.warning(f"Itineraire non trouve pour '{adresse_domicile}' -> status: {element.get('status')}")
            return None

        distance_m = element["distance"]["value"]
        distance_km = round(distance_m / 1000.0, 2)
        return distance_km

    except (requests.RequestException, KeyError, IndexError) as err:
        logger.warning(f"Erreur API Google Maps pour '{adresse_domicile}': {err}")
        return None


# ---------------------------------------------------------------------------
# Fallback haversine
# ---------------------------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcule la distance a vol d'oiseau entre deux points GPS (en km).
    Formule de Haversine.
    """
    R = 6371.0  # Rayon de la Terre en km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def geocode_address(adresse):
    """
    Geocode une adresse via l'API Google Maps Geocoding.

    Returns
    -------
    tuple (float, float) ou None
        (latitude, longitude) ou None si le geocodage echoue.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    try:
        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": adresse, "key": GOOGLE_MAPS_API_KEY, "language": "fr"},
            timeout=10,
        )
        data = response.json()
        if data.get("status") != "OK" or not data.get("results"):
            return None
        location = data["results"][0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    except (requests.RequestException, KeyError, IndexError):
        return None


def distance_haversine(adresse_domicile):
    """
    Calcule la distance a vol d'oiseau entre le domicile et l'entreprise.
    Utilise le geocodage Google Maps si disponible, sinon retourne None.

    Returns
    -------
    float ou None
        Distance en km (vol d'oiseau), ou None si le geocodage echoue.
    """
    coords = geocode_address(adresse_domicile)
    if coords is None:
        return None
    lat, lon = coords
    return haversine(lat, lon, ENTREPRISE_LAT, ENTREPRISE_LON)


# ---------------------------------------------------------------------------
# Fonction principale : calcul des distances pour tous les salaries
# ---------------------------------------------------------------------------

def calculate_all_distances():
    """
    Calcule la distance domicile-bureau pour chaque salarie.
    Utilise le cache, puis Google Maps API, puis fallback haversine.

    Returns
    -------
    list of dict
        Liste de dictionnaires avec id_salarie, departement, moyen_deplacement,
        adresse_domicile, distance_km, seuil_km, est_eligible, source_calcul.
    """
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Creer la table de cache si necessaire
        ensure_cache_table(cursor)

        # Lire tous les employes
        cursor.execute("""
            SELECT id_salarie, departement, moyen_deplacement, adresse_domicile, salaire_brut
            FROM staging.employes
            ORDER BY id_salarie;
        """)
        employes = cursor.fetchall()
        logger.info(f"{len(employes)} employes a traiter")

        results = []
        nb_cache = 0
        nb_google = 0
        nb_haversine = 0
        nb_echec = 0

        for id_salarie, departement, moyen_deplacement, adresse_domicile, salaire_brut in employes:
            # Determiner le seuil selon le moyen de deplacement
            seuil_km = SEUILS_DISTANCE.get(moyen_deplacement, 0.0)
            est_mode_eligible = moyen_deplacement in MODES_ELIGIBLES

            # Chercher dans le cache
            cached = get_cached_distance(cursor, adresse_domicile)
            if cached:
                distance_km, source = cached
                nb_cache += 1
            else:
                # Essayer Google Maps Distance Matrix
                distance_km = distance_google_maps(adresse_domicile)
                if distance_km is not None:
                    source = "google_maps"
                    save_to_cache(cursor, adresse_domicile, distance_km, source)
                    nb_google += 1
                    time.sleep(API_DELAY)
                else:
                    # Fallback haversine
                    distance_km = distance_haversine(adresse_domicile)
                    if distance_km is not None:
                        source = "haversine"
                        save_to_cache(cursor, adresse_domicile, distance_km, source)
                        nb_haversine += 1
                        time.sleep(API_DELAY)
                    else:
                        source = "echec"
                        distance_km = None
                        nb_echec += 1

            # Determiner l'eligibilite a la prime
            if est_mode_eligible and distance_km is not None:
                est_eligible = distance_km <= seuil_km
            else:
                est_eligible = False

            # Calcul du montant de la prime (5 % du salaire brut si eligible)
            montant_prime = float(salaire_brut) * 0.05 if est_eligible else 0.0

            results.append({
                "id_salarie": id_salarie,
                "departement": departement,
                "moyen_deplacement": moyen_deplacement,
                "adresse_domicile": adresse_domicile,
                "distance_km": distance_km,
                "seuil_km": seuil_km,
                "est_eligible": est_eligible,
                "montant_prime": round(montant_prime, 2),
                "source_calcul": source,
            })

        logger.info(
            f"Distances calculees : {nb_cache} cache, {nb_google} Google Maps, "
            f"{nb_haversine} haversine, {nb_echec} echecs"
        )

        return results

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


if __name__ == "__main__":
    results = calculate_all_distances()
    eligible = [r for r in results if r["est_eligible"]]
    logger.info(f"Recapitulatif : {len(eligible)} eligibles sur {len(results)} salaries")
    total_primes = sum(r["montant_prime"] for r in results)
    logger.info(f"Montant total des primes : {total_primes:.2f} EUR")
