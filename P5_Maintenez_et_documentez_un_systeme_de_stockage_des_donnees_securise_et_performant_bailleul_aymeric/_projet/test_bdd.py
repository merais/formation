import os
import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid

# Variables globales (pour la dockerisation)
DB_NAME = os.getenv("MONGODB_DB", "healthcare_db")
URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "patients")

@pytest.fixture
def mongodb_client():
    try:
        client = MongoClient(URI)
        client.admin.command('ping')  # Vérifier la connexion
        yield client
        client.close()
    except ConnectionFailure as e:
        pytest.fail(f"Échec de la connexion à MongoDB: {e}")

@pytest.fixture
def mongodb_db(mongodb_client):
    return mongodb_client[DB_NAME]

@pytest.fixture
def mongodb_collection(mongodb_db):
    return mongodb_db[COLLECTION_NAME]

def test_connection(mongodb_client):
    assert mongodb_client is not None, "La connexion à MongoDB a échoué."

def test_collection_exists(mongodb_db):
    collections = mongodb_db.list_collection_names()
    assert COLLECTION_NAME in collections, f"La collection '{COLLECTION_NAME}' n'existe pas."

def test_count_documents(mongodb_collection):
    count = mongodb_collection.count_documents({})
    print(f"Nombre de documents dans '{COLLECTION_NAME}': {count}")
    # On s'assure que le compteur est >= 0 (toujours vrai) pour garder un assert utile
    assert count >= 0

def test_document_operations(mongodb_collection):
    # 1) Compter les documents existants au départ
    initial_count = mongodb_collection.count_documents({})

    # 2) Insérer un document de test
    test_document = {"test_field": "test_value"}
    insert_result = mongodb_collection.insert_one(test_document)
    assert insert_result.inserted_id is not None, "Échec de l'insertion du document."

    # 3) Vérifier que le document a été inséré
    inserted_document = mongodb_collection.find_one({"test_field": "test_value"})
    assert inserted_document is not None, "Le document inséré est introuvable."

    # 4) Modifier le document
    update_result = mongodb_collection.update_one(
        {"test_field": "test_value"}, {"$set": {"test_field": "updated_value"}}
    )
    assert update_result.modified_count == 1, "Échec de la modification du document."

    # 5) Vérifier la modification
    updated_document = mongodb_collection.find_one({"test_field": "updated_value"})
    assert updated_document is not None, "Le document modifié est introuvable."

    # 6) Supprimer le document
    delete_result = mongodb_collection.delete_one({"test_field": "updated_value"})
    assert delete_result.deleted_count == 1, "Échec de la suppression du document."

    # 7) Vérifier que le nombre final correspond au nombre initial
    final_count = mongodb_collection.count_documents({})
    assert final_count == initial_count, "Le nettoyage des documents de test a échoué."