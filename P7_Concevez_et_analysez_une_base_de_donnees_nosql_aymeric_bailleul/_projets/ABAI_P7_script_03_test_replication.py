"""
Script de test de réplication MongoDB
Projet P7 - Analyse base de données NoSQL
Auteur: Aymeric Bailleul
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement (optionnel)
load_dotenv()

class MongoDBConnection:
    """Classe pour gérer la connexion à MongoDB avec support du replica set"""
    
    def __init__(self, connection_string: Optional[str] = None, 
                 replica_set_name: str = "rs_airbnb",
                 hosts: list = None):
        """
        Initialise la connexion MongoDB avec replica set
        
        Args:
            connection_string: URI de connexion complète (optionnel)
            replica_set_name: Nom du replica set
            hosts: Liste des hôtes du replica set [(host, port), ...]
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            # Configuration par défaut pour votre replica set
            if hosts is None:
                hosts = [
                    ("localhost", 27018),  # Primary
                    ("localhost", 27019),  # Secondary
                    ("localhost", 30000)   # Arbiter
                ]
            
            # Construire la chaîne de connexion pour le replica set
            hosts_string = ",".join([f"{host}:{port}" for host, port in hosts])
            self.connection_string = f"mongodb://{hosts_string}/?replicaSet={replica_set_name}"
        
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Établit la connexion à la base de données via le replica set
        MongoDB gérera automatiquement le basculement en cas de panne
        """
        try:
            self.client = MongoClient(
                self.connection_string, 
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            # Test de la connexion
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            print(f"\tConnexion reussie a la base de donnees : '{database_name}'")
            
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

def test_serveur_actuel(collection, client):
    """Affiche les informations sur le serveur qui a répondu à la requête"""
    
    # Exécuter une requête et voir sur quel serveur elle a été exécutée
    result = collection.find_one()
    print(f"\tTest de lecture d'un document (host_id) : {result['host_id']}")

    # Donne le nombre de documents
    count = collection.count_documents({}) 
    print(f"\tNombre total de documents dans la collection : {count}")

    # Obtenir les informations sur le serveur actuel
    server_info = client.address
    server_actuel = f"{server_info[0]}:{server_info[1]}"
    print(f"\tServeur qui a repondu: {server_actuel}")

# ============================================================================
# APPEL DE LA MAIN FONCTION > Début 
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("SCRIPT DE TEST DE RÉPLICATION MONGODB")
    print("="*100)
    
    # Configuration de la connexion au replica set
    # MongoDB basculera automatiquement vers le secondaire si le primaire tombe
    mongo = MongoDBConnection(
        replica_set_name="rs_airbnb",  # Nom de votre replica set
        hosts=[
            ("localhost", 27018),  # Primary
            ("localhost", 27019),  # Secondary
        ]
    )

    # Connexion à la base de données
    if mongo.connect("listings"):
        # Récupérer la collection après connexion
        collection = mongo.db["short_location"]
        print(f"\tConnexion etablie a la collection : '{collection.name}'")
        
        print("="*42 + " TEST : LECTURE " + "="*42)
        test_serveur_actuel(collection, mongo.client)
        print("="*43 + " FIN DU TEST " + "="*44)
        # Fermer la connexion
        mongo.close()
    else:
        print("\nImpossible de se connecter à MongoDB")