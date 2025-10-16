#Tests de sécurité avec pytest - Utilisateur en lecture seule (readonly_user)
#Ce script teste que l'utilisateur readonly_user peut uniquement lire les données.

import os
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure


@pytest.fixture(scope="module")
def mongodb_connection():
    #Fixture pour la connexion MongoDB avec l'utilisateur readonly.
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB", "healthcare_db")
    
    print(f"\n  Connexion en lecture seule à MongoDB...")
    print(f"   URI: {mongodb_uri}")
    print(f"   Database: {db_name}")
    
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    
    yield db
    
    client.close()


@pytest.fixture(scope="module")
def collection(mongodb_connection):
    #Fixture pour accéder à la collection patients.
    collection_name = os.getenv("COLLECTION_NAME", "patients")
    return mongodb_connection[collection_name]


class TestReadOnlyPermissions:
    #Tests de permissions en lecture seule.
    
    def test_connection_success(self, mongodb_connection):
        #Test que la connexion à MongoDB réussit.
        assert mongodb_connection is not None
        print("    Connexion réussie")
    
    def test_read_count_documents(self, collection):
        #Test que l'utilisateur peut lire le nombre de documents.
        count = collection.count_documents({})
        assert count > 0, "La collection devrait contenir des documents"
        print(f"    Lecture réussie: {count} documents trouvés")
    
    def test_read_find_one(self, collection):
        #Test que l'utilisateur peut lire un document.
        document = collection.find_one()
        assert document is not None, "Un document devrait être trouvé"
        assert "_id" in document, "Le document devrait avoir un _id"
        print(f"    Document lu avec succès: {document.get('Name', 'N/A')}")
    
    def test_read_find_multiple(self, collection):
        #Test que l'utilisateur peut lire plusieurs documents.
        documents = list(collection.find().limit(5))
        assert len(documents) > 0, "Des documents devraient être trouvés"
        print(f"    {len(documents)} documents lus avec succès")
    
    def test_insert_should_fail(self, collection):
        #Test que l'insertion est refusée (readonly).
        with pytest.raises(OperationFailure) as exc_info:
            collection.insert_one({"test": "Cette insertion devrait échouer"})
        
        assert "not authorized" in str(exc_info.value).lower() or \
               "unauthorized" in str(exc_info.value).lower()
        print(" Insertion correctement refusée")
    
    def test_update_should_fail(self, collection):
        #Test que la mise à jour est refusée (readonly).
        with pytest.raises(OperationFailure) as exc_info:
            collection.update_one({}, {"$set": {"test": "modification"}})
        
        assert "not authorized" in str(exc_info.value).lower() or \
               "unauthorized" in str(exc_info.value).lower()
        print(" Mise à jour correctement refusée")
    
    def test_delete_should_fail(self, collection):
        #Test que la suppression est refusée (readonly).
        with pytest.raises(OperationFailure) as exc_info:
            collection.delete_one({})
        
        assert "not authorized" in str(exc_info.value).lower() or \
               "unauthorized" in str(exc_info.value).lower()
        print(" Suppression correctement refusée")
    
    def test_drop_collection_should_fail(self, collection):
        #Test que la suppression de la collection est refusée (readonly).
        with pytest.raises(OperationFailure) as exc_info:
            collection.drop()
        
        assert "not authorized" in str(exc_info.value).lower() or \
               "unauthorized" in str(exc_info.value).lower()
        print(" Suppression de collection correctement refusée")


class TestReadOnlyQueries:
    #Tests de requêtes en lecture seule.
    
    def test_filter_by_gender(self, collection):
        #Test de filtrage par genre.
        count_male = collection.count_documents({"Gender": "Male"})
        count_female = collection.count_documents({"Gender": "Female"})
        total = count_male + count_female
        
        assert total > 0, "Des documents devraient être trouvés"
        print(f" Filtrage réussi: {count_male} hommes, {count_female} femmes")
    
    def test_aggregation_pipeline(self, collection):
        #Test de pipeline d'agrégation.
        pipeline = [
            {"$group": {"_id": "$Blood Type", "count": {"$sum": 1}}},
            {"$limit": 5}
        ]
        results = list(collection.aggregate(pipeline))
        
        assert len(results) > 0, "Des résultats d'agrégation devraient être trouvés"
        print(f" Agrégation réussie: {len(results)} groupes de types sanguins")
    
    def test_sort_and_limit(self, collection):
        #Test de tri et limitation.
        documents = list(collection.find().sort("Age", 1).limit(3))
        
        assert len(documents) > 0, "Des documents devraient être trouvés"
        print(f"    Tri et limitation réussis: {len(documents)} documents")