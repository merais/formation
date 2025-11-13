"""
Script de connexion et requêtes MongoDB avec Python
Projet P7 - Analyse base de données NoSQL
Auteur: Aymeric Bailleul
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import polars as pl
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (optionnel)
load_dotenv()


class MongoDBConnection:
    """Classe pour gérer la connexion à MongoDB"""
    
    def __init__(self, connection_string: Optional[str] = None, 
                 host: str = "localhost", 
                 port: int = 27017):
        """
        Initialise la connexion MongoDB
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = f"mongodb://{host}:{port}/"
        
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Établit la connexion à la base de données
        """
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test de la connexion
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            print(f"\tConnexion réussie à la base de données '{database_name}'")
            return True
        except ConnectionFailure as e:
            print(f"\tÉchec de connexion à MongoDB: {e}")
            return False
        except Exception as e:
            print(f"\tErreur inattendue: {e}")
            return False
    
    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("\tConnexion fermée")


def query_to_polars(collection, query: Dict = {}, projection: Dict = None, 
                    limit: int = 0) -> pl.DataFrame:
    """
    Exécute une requête MongoDB et retourne un DataFrame Polars
    """
    cursor = collection.find(query, projection)
    if limit > 0:
        cursor = cursor.limit(limit)
    
    data = list(cursor)
    
    if not data:
        return pl.DataFrame()
    
    return pl.DataFrame(data)


def aggregate_to_polars(collection, pipeline: List[Dict]):
    """
    Exécute une agrégation MongoDB et retourne un DataFrame Polars
    """
    result = list(collection.aggregate(pipeline))
    
    if not result:
        return pl.DataFrame()
    
    return pl.DataFrame(result)


def calculer_taux_reservation_moyen_par_type(collection):
    """
    Calcule le taux de réservation moyen par mois et par type de logement
    """
    pipeline = [
        {
            "$match": {
                "availability_365": {"$exists": True, "$ne": None},
                "room_type": {"$exists": True, "$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$room_type",
                "disponibilite_moyenne": {"$avg": "$availability_365"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "room_type": "$_id",
                "taux_reservation_mensuel_moyen": {
                    "$round": [
                        {"$divide": [
                            {"$multiply": [
                                {"$divide": [
                                    {"$subtract": [365, "$disponibilite_moyenne"]},
                                    365
                                ]},
                                100
                            ]},
                            12
                        ]},
                        2
                    ]
                }
            }
        },
        {
            "$sort": {"taux_reservation_mensuel_moyen": -1}
        }
    ]
    
    return aggregate_to_polars(collection, pipeline)

# ============================================================================
# APPEL DE LA MAIN FONCTION > Début 
# ============================================================================

if __name__ == "__main__":
    
    # Configuration de la connexion
    mongo = MongoDBConnection(host="localhost", port=27017)

    # Connexion à la base de données
    if mongo.connect("listings"):  
        print("\tConnexion établie --> Les requêtes peuvent commencer.")
        
        # Récupérer la collection
        collection = mongo.db["paris"]  # Remplacer "paris" par le nom de votre collection
        if collection is None:
            print("\tLa collection n'existe pas dans la base de données.")
            mongo.close()
            exit(1)
        else:
            print(f"\tLa collection '{collection.name}' est chargée avec succès.")

        # ============================================================================
        # DÉBUT DU CODE A FAIRE AVEC POLARS
        # ============================================================================
        
        # Taux de réservation moyen par type de logement
        print("\n" + "="*100)
        print("TAUX DE RÉSERVATION MOYEN PAR TYPE DE LOGEMENT")
        print("="*100)
        df_taux = calculer_taux_reservation_moyen_par_type(collection)
        print(df_taux)
        
        # ============================================================================
        # FIN DU CODE AVEC POLARS
        # ============================================================================

        # Fermer la connexion
        mongo.close()
    else:
        print("Impossible de se connecter à MongoDB")
