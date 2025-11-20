"""
Script de test de cluster MongoDB shardé avec 2 mongos
Projet P7 - Analyse base de données NoSQL
Auteur: Aymeric Bailleul
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class MongoDBShardedConnection:
    """Classe pour gérer la connexion à un cluster MongoDB shardé avec 2 mongos"""
    
    def __init__(self, mongos_hosts: list = None):
        """
        Initialise la connexion aux routeurs mongos
        
        Args:
            mongos_hosts: Liste des hôtes mongos [(host, port), ...]
        """
        if mongos_hosts is None:
            mongos_hosts = [
                ("localhost", 27001),  # Mongos 1
                ("localhost", 27002)   # Mongos 2
            ]
        
        # Construire la chaîne de connexion avec les 2 mongos
        hosts_string = ",".join([f"{host}:{port}" for host, port in mongos_hosts])
        self.connection_string = f"mongodb://{hosts_string}/"
        self.mongos_hosts = mongos_hosts
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Établit la connexion à la base de données via les mongos
        MongoDB gérera automatiquement le basculement entre les mongos
        """
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            print(f"\tConnexion reussie au cluster sharde via mongos")
            print(f"\tBase de donnees : '{database_name}'")
            return True
        except ConnectionFailure as e:
            print(f"\tÉchec de connexion : {e}")
            return False
    
    def test_serveur_actuel(self, collection):
        """Affiche les informations sur le mongos qui a répondu à la requête"""
        
        # Exécuter une requête et voir quel mongos a répondu
        result = collection.find_one()
        if result:
            print(f"\tTest de lecture d'un document (host_id) : {result.get('host_id')}")
        else:
            print(f"\tAucun document trouvé dans la collection")
        
        # Donne le nombre de documents
        count = collection.count_documents({}) 
        print(f"\tNombre total de documents dans la collection : {count}")
        
        # Obtenir les informations sur les mongos disponibles
        try:
            # Avec plusieurs mongos, utiliser 'nodes' au lieu de 'address'
            nodes = self.client.nodes
            print(f"\tMongos disponibles : {', '.join([f'{node[0]}:{node[1]}' for node in nodes])}")
        except Exception as e:
            print(f"\tImpossible de récupérer les informations des mongos : {e}")
    
    def get_shard_distribution(self, collection_name: str):
        """Affiche la distribution des données sur les shards"""
        try:
            collection = self.db[collection_name]
            stats = self.db.command("collStats", collection_name)
            
            print("\n\tDistribution des shards:")
            if 'shards' in stats:
                for shard, info in stats['shards'].items():
                    print(f"\t  {shard}:")
                    print(f"\t    - Documents: {info.get('count', 0)}")
                    print(f"\t    - Taille: {info.get('size', 0)} bytes")
            else:
                print("\t  Collection non shardée ou pas encore de distribution")
                print(f"\t  Documents totaux: {stats.get('count', 0)}")
                
        except Exception as e:
            print(f"\tErreur lors de la récupération de la distribution: {e}")
    
    def get_cluster_status(self):
        """Affiche le statut du cluster"""
        try:
            config_db = self.client.config
            shards = list(config_db.shards.find())
            
            print("\n\tShards actifs dans le cluster:")
            for shard in shards:
                print(f"\t  - {shard['_id']}: {shard['host']}")
            
            # Afficher les mongos configurés
            print("\n\tMongos configures:")
            for host, port in self.mongos_hosts:
                print(f"\t  - {host}:{port}")
                
        except Exception as e:
            print(f"\tErreur lors de la récupération du statut: {e}")
    
    def test_mongos_failover(self, collection):
        """cd
        Teste le basculement entre les mongos
        Note: Pour un vrai test, il faudrait arrêter un mongos
        """
        print("\n\tTest de basculement entre mongos:")
        print("\tLes requêtes sont automatiquement routées vers les mongos disponibles")
        
        for i in range(3):
            try:
                result = collection.find_one()
                # Avec plusieurs mongos, afficher tous les nodes disponibles
                nodes = self.client.nodes
                nodes_str = ', '.join([f'{node[0]}:{node[1]}' for node in nodes])
                print(f"\t  Requête {i+1} - Mongos disponibles: {nodes_str}")
            except Exception as e:
                print(f"\t  Erreur sur la requête {i+1}: {e}")
    
    def close(self):
        """Ferme la connexion"""
        if self.client:
            self.client.close()
            print("\n\tConnexion fermée")

# ============================================================================
# APPEL DE LA MAIN FONCTION > Début 
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("SCRIPT DE TEST DE CLUSTER MONGODB SHARDÉ AVEC 2 MONGOS")
    print("="*100)
    
    # Connexion aux 2 routeurs mongos
    mongo = MongoDBShardedConnection(
        mongos_hosts=[
            ("localhost", 27001),  # Mongos 1
            ("localhost", 27002)   # Mongos 2
        ]
    )
    
    if mongo.connect("listings"):
        collection = mongo.db["short_location"]
        print(f"\tConnexion etablie a la collection : '{collection.name}'")
        
        print("\n" + "="*40 + " STATUT DU CLUSTER " + "="*40)
        mongo.get_cluster_status()
        
        print("\n" + "="*40 + " TEST : LECTURE " + "="*42)
        mongo.test_serveur_actuel(collection)
        
        print("\n" + "="*40 + " DISTRIBUTION DES DONNÉES " + "="*35)
        mongo.get_shard_distribution("short_location")
        
        print("\n" + "="*40 + " TEST BASCULEMENT MONGOS " + "="*35)
        mongo.test_mongos_failover(collection)
        
        print("\n" + "="*100)
        
        mongo.close()
    else:
        print("\nImpossible de se connecter au cluster MongoDB")