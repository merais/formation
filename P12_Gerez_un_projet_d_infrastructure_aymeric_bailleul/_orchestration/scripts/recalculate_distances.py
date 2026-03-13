"""
recalculate_distances.py – Mise a jour du cache de distances domicile-bureau (Kestra standalone)

Calcule la distance entre le domicile de chaque salarie actif et l'adresse de l'entreprise
via l'API Google Maps Distance Matrix. Les resultats sont mis en cache dans
staging.cache_distances (cle = adresse_domicile) pour eviter les appels API repetitifs.

Logique :
  1. Recuperer toutes les adresses actives depuis staging.employes
  2. Ignorer les adresses deja en cache
  3. Appeler Google Maps API pour les nouvelles adresses
  4. Fallback haversine (geocodage Google) si l'API Distance Matrix echoue

Variables d'environnement requises :
  POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  GOOGLE_MAPS_API_KEY  (optionnel : fallback haversine si absent)
  ENTREPRISE_ADRESSE   (optionnel : defaut = 1362 Av. des Platanes, 34970 Lattes)
"""

import logging
import math
import os
import time

import psycopg2
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GOOGLE_MAPS_API_KEY  = os.environ.get("GOOGLE_MAPS_API_KEY", "")
ENTREPRISE_ADRESSE   = os.environ.get("ENTREPRISE_ADRESSE", "1362 Av. des Platanes, 34970 Lattes")
GOOGLE_MAPS_URL      = "https://maps.googleapis.com/maps/api/distancematrix/json"
ENTREPRISE_LAT       = 43.5676
ENTREPRISE_LON       = 3.9070
API_DELAY            = 0.1   # secondes entre chaque appel API


# ---------------------------------------------------------------------------
# Connexion PostgreSQL
# ---------------------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


# ---------------------------------------------------------------------------
# Cache staging.cache_distances
# ---------------------------------------------------------------------------

SQL_CREATE_CACHE = """
CREATE TABLE IF NOT EXISTS staging.cache_distances (
    adresse_domicile TEXT        PRIMARY KEY,
    distance_km      REAL,
    source_calcul    VARCHAR(20) NOT NULL
);
"""


def ensure_cache_table(cursor):
    cursor.execute(SQL_CREATE_CACHE)


def get_cached_addresses(cursor):
    """Retourne l'ensemble des adresses deja en cache."""
    cursor.execute("SELECT adresse_domicile FROM staging.cache_distances;")
    return {row[0] for row in cursor.fetchall()}


def save_to_cache(cursor, adresse, distance_km, source):
    cursor.execute(
        """
        INSERT INTO staging.cache_distances (adresse_domicile, distance_km, source_calcul)
        VALUES (%s, %s, %s)
        ON CONFLICT (adresse_domicile) DO UPDATE
            SET distance_km   = EXCLUDED.distance_km,
                source_calcul = EXCLUDED.source_calcul;
        """,
        (adresse, distance_km, source),
    )


# ---------------------------------------------------------------------------
# Google Maps Distance Matrix
# ---------------------------------------------------------------------------

def distance_google_maps(adresse_domicile):
    """Calcule la distance routiere via Google Maps. Retourne float ou None."""
    if not GOOGLE_MAPS_API_KEY:
        return None
    try:
        response = requests.get(
            GOOGLE_MAPS_URL,
            params={
                "origins":      adresse_domicile,
                "destinations": ENTREPRISE_ADRESSE,
                "key":          GOOGLE_MAPS_API_KEY,
                "mode":         "driving",
                "language":     "fr",
            },
            timeout=10,
        )
        data = response.json()
        if data.get("status") != "OK":
            logger.warning(f"Google Maps status={data.get('status')} pour '{adresse_domicile}'")
            return None
        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            logger.warning(f"Itineraire non trouve : '{adresse_domicile}' -> {element.get('status')}")
            return None
        return round(element["distance"]["value"] / 1000.0, 2)
    except (requests.RequestException, KeyError, IndexError) as err:
        logger.warning(f"Erreur Distance Matrix pour '{adresse_domicile}': {err}")
        return None


# ---------------------------------------------------------------------------
# Fallback haversine (geocodage + distance vol d'oiseau)
# ---------------------------------------------------------------------------

def geocode_address(adresse):
    """Geocode une adresse via Google Maps Geocoding. Retourne (lat, lon) ou None."""
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
        loc = data["results"][0]["geometry"]["location"]
        return (loc["lat"], loc["lng"])
    except (requests.RequestException, KeyError, IndexError):
        return None


def haversine(lat1, lon1, lat2, lon2):
    """Distance a vol d'oiseau entre deux points GPS (km)."""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def distance_haversine(adresse_domicile):
    """Geocode l'adresse puis calcule la distance haversine vers l'entreprise."""
    coords = geocode_address(adresse_domicile)
    if coords is None:
        return None
    return haversine(coords[0], coords[1], ENTREPRISE_LAT, ENTREPRISE_LON)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def recalculate_distances():
    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        ensure_cache_table(cursor)

        # Adresses distinctes des salaries actifs
        cursor.execute(
            "SELECT DISTINCT adresse_domicile FROM staging.employes WHERE actif = TRUE;"
        )
        all_addresses = {row[0] for row in cursor.fetchall()}

        # Adresses deja en cache → pas besoin de recalculer
        cached = get_cached_addresses(cursor)
        to_compute = all_addresses - cached

        logger.info(f"{len(all_addresses)} adresses actives, {len(cached)} en cache, {len(to_compute)} a calculer")

        if not to_compute:
            logger.info("Cache a jour — aucun appel API necessaire.")
            return

        nb_google    = 0
        nb_haversine = 0
        nb_echec     = 0

        for adresse in sorted(to_compute):
            distance_km = distance_google_maps(adresse)
            if distance_km is not None:
                save_to_cache(cursor, adresse, distance_km, "google_maps")
                nb_google += 1
                time.sleep(API_DELAY)
            else:
                distance_km = distance_haversine(adresse)
                if distance_km is not None:
                    save_to_cache(cursor, adresse, distance_km, "haversine")
                    nb_haversine += 1
                    time.sleep(API_DELAY)
                else:
                    logger.warning(f"Echec calcul distance pour : '{adresse}'")
                    nb_echec += 1

        logger.info(
            f"Calcul termine : {nb_google} Google Maps, {nb_haversine} haversine, {nb_echec} echec(s)"
        )

    finally:
        cursor.close()
        conn.close()
        logger.info("Connexion fermee.")


if __name__ == "__main__":
    recalculate_distances()
