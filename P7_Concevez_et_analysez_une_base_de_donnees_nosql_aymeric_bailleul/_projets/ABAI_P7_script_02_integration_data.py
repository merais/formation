"""
Script d'intégration de données CSV dans MongoDB
Projet P7 - Analyse base de données NoSQL
Auteur: Aymeric Bailleul
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import polars as pl
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement (optionnel)
load_dotenv()


class MongoDBConnection:
    """Classe pour gérer la connexion à MongoDB (standalone ou cluster shardé)"""
    
    def __init__(self, connection_string: Optional[str] = None, 
                 host: str = "localhost", 
                 port: int = 27001,
                 mongos_hosts: list = None):
        """
        Initialise la connexion MongoDB
        
        Args:
            connection_string: Chaîne de connexion complète (prioritaire)
            host: Hôte MongoDB (pour connexion simple)
            port: Port MongoDB (pour connexion simple)
            mongos_hosts: Liste de tuples (host, port) pour cluster shardé
                         Ex: [("localhost", 27017), ("localhost", 27016)]
        """
        if connection_string:
            self.connection_string = connection_string
        elif mongos_hosts:
            # Connexion à un cluster shardé avec plusieurs mongos
            hosts_string = ",".join([f"{h}:{p}" for h, p in mongos_hosts])
            self.connection_string = f"mongodb://{hosts_string}/"
        else:
            # Connexion simple à un serveur MongoDB
            self.connection_string = f"mongodb://{host}:{port}/"
        
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Établit la connexion à la base de données (standalone ou cluster shardé)
        """
        try:
            print(f"\tConnexion à : {self.connection_string}")
            self.client = MongoClient(
                self.connection_string, 
                serverSelectionTimeoutMS=5000,
                directConnection=False  # Important pour les clusters shardés
            )
            # Test de la connexion
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            print(f"\t✅ Connexion réussie à la base de données '{database_name}'")
            
            # Afficher le type de connexion
            try:
                server_info = self.client.server_info()
                print(f"\tVersion MongoDB : {server_info.get('version', 'inconnue')}")
            except:
                pass
                
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


def creer_collection_short_location(db) -> bool:
    """
    Crée une collection nommée 'short_location' dans la base de données
    Si la collection existe déjà, elle est supprimée puis recréée
    
    Args:
        db: Objet database MongoDB
        
    Returns:
        bool: True si la création est réussie, False sinon
    """
    try:
        # Vérifier si la collection existe déjà
        if "short_location" in db.list_collection_names():
            print("\tLa collection 'short_location' existe déjà")
            response = input("\tVoulez-vous la supprimer et la recréer ? (o/n): ")
            if response.lower() == 'o':
                db.drop_collection("short_location")
                print("\tCollection 'short_location' supprimée")
            else:
                print("\tConservation de la collection existante")
                return True
        
        # Créer la collection
        db.create_collection("short_location")
        print("\tCollection 'short_location' créée avec succès")
        return True
        
    except Exception as e:
        print(f"\tErreur lors de la création de la collection: {e}")
        return False


def importer_donnees_csv(db, csv_folder_path: str = "data") -> bool:
    """
    Importe les données des fichiers CSV dans la collection 'short_location'
    Ajoute un champ 'csv_origin' contenant le nom du fichier source
    
    Args:
        db: Objet database MongoDB
        csv_folder_path: Chemin du dossier contenant les fichiers CSV
        
    Returns:
        bool: True si l'importation est réussie, False sinon
    """
    try:
        collection = db["short_location"]
        csv_folder = Path(csv_folder_path)
        
        # Vérifier que le dossier existe
        if not csv_folder.exists():
            print(f"\tLe dossier '{csv_folder_path}' n'existe pas")
            return False
        
        # Récupérer tous les fichiers CSV
        csv_files = list(csv_folder.glob("*.csv"))
        
        if not csv_files:
            print(f"\tAucun fichier CSV trouvé dans '{csv_folder_path}'")
            return False
        
        print(f"\t📁 {len(csv_files)} fichier(s) CSV trouvé(s)")
        
        total_documents = 0
        
        # Traiter chaque fichier CSV
        for csv_file in csv_files:
            print(f"\n\tTraitement du fichier: {csv_file.name}")
            
            try:
                # Lire le CSV avec Polars
                df = pl.read_csv(csv_file)
                print(f"\t   → {len(df)} lignes trouvées")
                
                # Ajouter la colonne csv_origin
                df = df.with_columns([
                    pl.lit(csv_file.name).alias("csv_origin")
                ])
                
                # Convertir en liste de dictionnaires
                documents = df.to_dicts()
                
                # Insérer dans MongoDB
                if documents:
                    result = collection.insert_many(documents, ordered=False)
                    inserted_count = len(result.inserted_ids)
                    total_documents += inserted_count
                    print(f"\t   ✓ {inserted_count} documents insérés")
                else:
                    print(f"\t   Aucun document à insérer")
                    
            except DuplicateKeyError as e:
                print(f"\t   Certains documents existent déjà (doublons ignorés)")
            except Exception as e:
                print(f"\t   Erreur lors du traitement de {csv_file.name}: {e}")
                continue
        
        print(f"\n\tImportation terminée: {total_documents} documents insérés au total")
        return True
        
    except Exception as e:
        print(f"\tErreur lors de l'importation: {e}")
        return False


def verifier_donnees(db) -> dict:
    """
    Vérifie les données importées dans la collection 'short_location'
    
    Args:
        db: Objet database MongoDB
        
    Returns:
        dict: Statistiques sur les données importées
    """
    try:
        collection = db["short_location"]

        # Nombre total de documents
        total_docs = collection.count_documents({})
        print(f"\nNombre total de documents: {total_docs}")
        
        # Répartition par fichier source
        print("\nRépartition par fichier source:")
        pipeline_source = [
            {
                "$group": {
                    "_id": "$csv_origin",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        sources = list(collection.aggregate(pipeline_source))
        for source in sources:
            print(f"\t- {source['_id']}: {source['count']} documents")
        
        # Liste des champs disponibles (sur le premier document)
        sample_doc = collection.find_one()
        if sample_doc:
            print(f"\nNombre de champs dans les documents: {len(sample_doc.keys())}")
            print(f"\nExemple des premiers champs:")
            for i, key in enumerate(list(sample_doc.keys())[:10]):
                print(f"\t- {key}")
            if len(sample_doc.keys()) > 10:
                print(f"\t... et {len(sample_doc.keys()) - 10} autres champs")
        
        # Vérifier la présence du champ csv_origin
        docs_with_origin = collection.count_documents({"csv_origin": {"$exists": True}})
        print(f"\nDocuments avec champ 'csv_origin': {docs_with_origin}/{total_docs}")
        
        stats = {
            "total_documents": total_docs,
            "sources": sources,
            "docs_with_origin": docs_with_origin
        }
        
        return stats
        
    except Exception as e:
        print(f"\nErreur lors de la vérification: {e}")
        return {}


# ============================================================================
# APPEL DE LA MAIN FONCTION > Début 
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*100)
    print("SCRIPT D'INTÉGRATION DE DONNÉES CSV DANS MONGODB")
    print("="*100)
    
    # ====================================================================
    # CONFIGURATION DE LA CONNEXION
    # ====================================================================
    # OPTION 1: Connexion à un serveur MongoDB simple (standalone)
    # mongo = MongoDBConnection(host="localhost", port=27017)
    
    # OPTION 2: Connexion à un cluster MongoDB shardé avec 2 mongos
    mongo = MongoDBConnection(
        mongos_hosts=[
            ("localhost", 27001),  # Mongos 1
            ("localhost", 27002)   # Mongos 2
        ]
    )
    # ====================================================================

    # Connexion à la base de données
    if mongo.connect("listings"):
        print("\tConnexion établie --> L'intégration peut commencer.\n")
        
        # Étape 1: Créer la collection short_location
        print("="*100)
        print("ÉTAPE 1: CRÉATION DE LA COLLECTION 'short_location'")
        print("="*100)
        if creer_collection_short_location(mongo.db):
            
            # Étape 2: Importer les données des fichiers CSV
            print("\n" + "="*100)
            print("ÉTAPE 2: IMPORTATION DES DONNÉES CSV")
            print("="*100)
            if importer_donnees_csv(mongo.db, csv_folder_path="./data"):
                
                # Étape 3: Vérifier les données importées
                print("\n" + "="*100)
                print("ÉTAPE 3: VÉRIFICATION DES DONNÉES")
                print("="*100)
                stats = verifier_donnees(mongo.db)
                
                print("\n" + "="*100)
                print("INTÉGRATION TERMINÉE AVEC SUCCÈS")
                print("="*100)
            else:
                print("\nÉchec de l'importation des données")
        else:
            print("\nÉchec de la création de la collection")
        
        # Fermer la connexion
        print("\n")
        mongo.close()
    else:
        print("\nImpossible de se connecter à MongoDB")
