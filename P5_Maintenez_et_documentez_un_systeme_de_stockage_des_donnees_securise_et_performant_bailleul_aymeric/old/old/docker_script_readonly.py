"""
Script de lecture seule - Utilise le compte readonly_user
Ce script ne peut que lire les données, aucune modification n'est possible.
"""

import os
from pymongo import MongoClient
from pymongo.errors import OperationFailure

def main():
    # Récupération des variables d'environnement
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB", "healthcare_db")
    collection_name = os.getenv("COLLECTION_NAME", "patients")
    
    print(f"📖 Connexion en lecture seule à MongoDB...")
    print(f"   URI: {mongodb_uri.replace(os.getenv('MONGO_READONLY_PASSWORD', ''), '***')}")
    print(f"   Database: {db_name}")
    print(f"   Collection: {collection_name}")
    
    # Connexion à MongoDB
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    # Test 1: Lecture des données (doit fonctionner)
    print("\n✓ Test 1: Lecture des données")
    count = collection.count_documents({})
    print(f"   Nombre de documents: {count}")
    
    if count > 0:
        sample = collection.find_one()
        print(f"   Exemple de document: {sample}")
    
    # Test 2: Tentative d'insertion (doit échouer)
    print("\n✗ Test 2: Tentative d'insertion d'un document (doit échouer)")
    try:
        collection.insert_one({"test": "Cette insertion devrait échouer"})
        print("     ERREUR: L'insertion a réussi alors qu'elle devrait échouer!")
    except OperationFailure as e:
        print(f"   ✓ Insertion refusée comme prévu: {e}")
    
    # Test 3: Tentative de mise à jour (doit échouer)
    print("\n✗ Test 3: Tentative de mise à jour (doit échouer)")
    try:
        collection.update_one({}, {"$set": {"test": "modification"}})
        print("     ERREUR: La mise à jour a réussi alors qu'elle devrait échouer!")
    except OperationFailure as e:
        print(f"   ✓ Mise à jour refusée comme prévu: {e}")
    
    # Test 4: Tentative de suppression (doit échouer)
    print("\n✗ Test 4: Tentative de suppression (doit échouer)")
    try:
        collection.delete_one({})
        print("     ERREUR: La suppression a réussi alors qu'elle devrait échouer!")
    except OperationFailure as e:
        print(f"   ✓ Suppression refusée comme prévu: {e}")
    
    print("\n       Tests de lecture seule terminés avec succès!")
    print("   L'utilisateur readonly_user peut uniquement lire les données.")
    
    client.close()

if __name__ == "__main__":
    main()
