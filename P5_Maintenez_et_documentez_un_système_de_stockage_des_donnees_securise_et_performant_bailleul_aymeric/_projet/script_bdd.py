# Script de création de la base de données MongoDB et d'importation des données depuis un fichier CSV.
# Importer les bibliothèques nécessaires a l'utilisation de mongodb
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Variables globales (utilisé pour les tests locaux)
#DB_NAME = "healthcare_db"
#URI = "mongodb://localhost:27017/"
#COLLECTION_NAME = "patients"
#SOURCE_CSV = "./sources/healthcare_dataset.csv"

# Variables globales (pour la dockerisation)
DB_NAME = os.getenv("MONGODB_DB", "healthcare_db")
URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "patients")
SOURCE_CSV = os.getenv("SOURCE_CSV", "./sources/healthcare_dataset.csv")

# Fonction de connexion a la base de données
def connect_to_mongodb(uri, db_name):
    try:
        # Créer une instance de MongoClient
        client = MongoClient(uri)
        
        # Vérifier la connexion
        client.admin.command('ping')
        print("Connexion à MongoDB réussie")
        
        # Accéder à la base de données spécifiée
        db = client[db_name]
        return db
    except ConnectionFailure as e:
        print(f"Échec de la connexion à MongoDB: {e}")
        return None

# Fonction d'importation de données depuis un fichier csv
def import_data_from_csv(db, collection_name, file_path):
    import pandas as pd
    
    # Lire les données depuis le fichier CSV
    try:
        data = pd.read_csv(file_path)
        print(f"Données lues depuis {file_path}")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return
    
    # Convertir les données en dictionnaire
    data_dict = data.to_dict(orient='records')
    
    # Insérer les données dans la collection MongoDB
    try:
        collection = db[collection_name]
        collection.insert_many(data_dict)
        print(f"{len(data_dict)} documents insérés dans la collection '{collection_name}'")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans la collection '{collection_name}': {e}")

# Main
if __name__ == "__main__":
    # Connexion à la base de données
    try:
        db = connect_to_mongodb(URI, DB_NAME)
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        db = None

    # # Création d'une collection et importation de données depuis un fichier CSV si la collection n'existe pas déjà
    if db != None:
        if COLLECTION_NAME in db.list_collection_names():
            print(f"La collection '{COLLECTION_NAME}' existe déjà.")
            collection = db[COLLECTION_NAME]
            print(f"Il y a {collection.count_documents({})} documents dans la collection déjà existante '{COLLECTION_NAME}'.") # Afficher le nombre de documents dans la collection
        else:
            print(f"La collection '{COLLECTION_NAME}' n'existe pas et va donc être créée.") 
            import_data_from_csv(db, COLLECTION_NAME, SOURCE_CSV)
    else:
        print("La base de données n'est pas disponible.")