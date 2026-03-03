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


def get_connection():
    """
    Cree et retourne une connexion PostgreSQL
    a partir des variables d'environnement.

    Returns
    -------
    psycopg2.extensions.connection
        Connexion active vers la base PostgreSQL.

    Raises
    ------
    psycopg2.OperationalError
        Si la connexion echoue (mauvais parametres, conteneur arrete, etc.).
    """
    # On verifie que toutes les variables d'environnement necessaires sont presentes dans le .env avant d'essayer de se connecter
    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Variables d'environnement manquantes : {', '.join(missing)}. "
            f"Verifiez votre fichier .env a la racine du projet."
        )

    # Creation de la connexion
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=int(os.getenv("POSTGRES_PORT")),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    return connection

# Exemple de test de connexion et affichage de la version de PostgreSQL
def test_connection():
    """
    Teste la connexion a la base de donnees.
    Affiche la version de PostgreSQL si la connexion reussit.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Connexion reussie. PostgreSQL : {version}")
        cursor.close()
    except psycopg2.OperationalError as err:
        print(f"Erreur de connexion : {err}")
    finally:
        if conn is not None:
            conn.close()


# Permet de tester la connexion en lancant ce fichier directement :
#   python -m src.db.connexion
if __name__ == "__main__":
    test_connection()
