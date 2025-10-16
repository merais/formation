# Importer les bibliothèques nécessaires a l'utilisation de mongodb
import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

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
    
def verify_data():
    if COLLECTION_NAME in db.list_collection_names():
        #On affiche le nombre de documents dans la collection
        collection = db[COLLECTION_NAME]
        print(f"\n1- Nombre de documents dans la collection '{COLLECTION_NAME}': {collection.count_documents({})}")

        # On affiche un document pour vérifier la connexion
        print(f"\n2- Un document de la collection '{COLLECTION_NAME}': {collection.find_one()}")
    
        # On essaye de modifier un document pour vérifier que l'on peut écrire dans la base
        result_modif = collection.update_one({}, {"$set": {"test_field": "test_value"}})
        if result_modif.modified_count > 0:
            print("\n3- Modification réussie dans la collection existante :")
            print(f"Document modifié de la collection '{COLLECTION_NAME}': \n{collection.find_one({'test_field': 'test_value'})}") # On affiche le document modifié
        else:
            print("\n3- Aucun document modifié dans la collection existante.")

        # On supprime le champ de test pour revenir à l'état initial
        result_supp_modif = collection.update_many({}, {"$unset": {"test_field": ""}})
        if result_supp_modif.modified_count > 0:
            print("\n4- La suppression de la modification réussie dans la collection existante :")
            print(f"Document modifié de la collection '{COLLECTION_NAME}': \n{collection.find_one({'test_field': 'test_value'})}") # On affiche le document modifié
        else:
            print("\n4- Aucun document modifié dans la collection existante.")

        # On essaye d'insérer un nouveau document pour vérifier que l'on peut écrire dans la base
        new_document = {"test_field": "test_value_2"}
        result_insert = collection.insert_one(new_document)
        if result_insert.inserted_id:
            print("\n5- Insertion réussie d'un nouveau document dans la collection existante :")
            print(f"Document inséré dans la collection '{COLLECTION_NAME}': \n{collection.find_one({'test_field': 'test_value_2'})}") # On affiche le document inséré
        else:
            print("\n5- Échec de l'insertion d'un nouveau document dans la collection existante.")

        #On essaye de supprimer les documents de test pour nettoyer la base
        result_delete = collection.delete_many({"test_field": {"$in": ["test_value", "test_value_2"]}})
        if result_delete.deleted_count > 0:
            print(f"\n6- Suppression réussie de {result_delete.deleted_count} documents de test dans la collection existante.")
        else:
            print("\n6- Aucun document à supprimer dans la collection existante.")

    else:
        print(f"La collection '{COLLECTION_NAME}' n'existe pas encore.")

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
        verify_data()
    else:
        print("La base de données n'est pas disponible.")