"""
connexion.py – Gestion de la connexion PostgreSQL

Charge les parametres de connexion depuis le fichier .env
et fournit une fonction pour obtenir une connexion psycopg2.
"""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Charger le fichier .env situe a la racine du projet
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


def get_connection(role=None):
    """
    Cree et retourne une connexion PostgreSQL a partir des variables d'environnement.

    Parameters
    ----------
    role : str or None
        Identifiant du role de connexion :
          - None (defaut) : compte superuser pipeline (POSTGRES_USER / POSTGRES_PASSWORD)
          - "rh_admin"    : role_rh_admin (DB_USER_RH / DB_PASS_RH) – acces rh_prive
          - "analytics"   : role_analytics (DB_USER_ANALYTICS / DB_PASS_ANALYTICS) – gold lecture
          - "pipeline"    : role_pipeline (DB_USER_PIPELINE / DB_PASS_PIPELINE) – sans rh_prive

    Returns
    -------
    psycopg2.extensions.connection
        Connexion active vers la base PostgreSQL.

    Raises
    ------
    psycopg2.OperationalError
        Si la connexion echoue (mauvais parametres, conteneur arrete, etc.).
    """
    required_base = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB"]
    missing = [var for var in required_base if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Variables d'environnement manquantes : {', '.join(missing)}. "
            f"Verifiez votre fichier .env a la racine du projet."
        )

    role_map = {
        "rh_admin":  ("DB_USER_RH",        "DB_PASS_RH"),
        "analytics": ("DB_USER_ANALYTICS",  "DB_PASS_ANALYTICS"),
        "pipeline":  ("DB_USER_PIPELINE",   "DB_PASS_PIPELINE"),
    }

    if role is not None and role not in role_map:
        raise ValueError(f"Role inconnu : '{role}'. Valeurs acceptees : {list(role_map)}")

    if role is not None:
        user_var, pass_var = role_map[role]
        user = os.getenv(user_var)
        password = os.getenv(pass_var)
        if not user or not password:
            raise EnvironmentError(
                f"Variables manquantes pour le role '{role}' : {user_var}, {pass_var}. "
                f"Verifiez votre fichier .env."
            )
    else:
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        if not user or not password:
            raise EnvironmentError(
                "Variables POSTGRES_USER et POSTGRES_PASSWORD manquantes dans .env."
            )

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        dbname=os.getenv("POSTGRES_DB"),
        user=user,
        password=password,
    )
    return connection


def test_connection():
    """Teste la connexion a la base de donnees."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Connexion reussie. PostgreSQL : {version}")
    finally:
        if conn:
            conn.close()
