#Tests de sécurité avec pytest - Utilisateur avec droits d'écriture (app_user)
#Ce script teste que l'utilisateur app_user peut lire et écrire les données.


import os
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from datetime import datetime


@pytest.fixture(scope="module")
def mongodb_connection():
    #Fixture pour la connexion MongoDB avec l'utilisateur app_user.
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DB", "healthcare_db")
    
    print(f"\n📝 Connexion avec droits d'écriture à MongoDB...")
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


@pytest.fixture(scope="module")
def test_collection(mongodb_connection):
    #Fixture pour une collection de test temporaire.
    test_collection_name = "test_temp_collection"
    collection = mongodb_connection[test_collection_name]
    
    yield collection
    
    # Nettoyage : supprimer la collection de test après les tests
    try:
        collection.drop()
        print(f"    Collection de test '{test_collection_name}' supprimée")
    except Exception as e:
        print(f"    Erreur lors de la suppression de la collection de test: {e}")


class TestReadWritePermissions:
    #Tests de permissions en lecture/écriture.
    def test_connection_success(self, mongodb_connection):
        #Test que la connexion à MongoDB réussit.
        assert mongodb_connection is not None
        print(" Connexion réussie avec app_user")
    
    def test_read_permissions(self, collection):
        #Test que l'utilisateur peut lire les données.
        count = collection.count_documents({})
        assert count > 0, "La collection devrait contenir des documents"
        print(f"    Lecture autorisée: {count} documents trouvés")
    
    def test_insert_document(self, test_collection):
        #Test que l'utilisateur peut insérer un document.
        test_doc = {
            "test_id": 1,
            "test_name": "Test Insert",
            "created_at": datetime.now(),
            "description": "Document de test pour vérifier les droits d'insertion"
        }
        
        result = test_collection.insert_one(test_doc)
        assert result.inserted_id is not None, "L'insertion devrait retourner un ID"
        
        # Vérifier que le document a bien été inséré
        inserted = test_collection.find_one({"test_id": 1})
        assert inserted is not None, "Le document devrait être trouvé"
        assert inserted["test_name"] == "Test Insert"
        print("    Insertion autorisée et réussie")
    
    def test_update_document(self, test_collection):
        #Test que l'utilisateur peut mettre à jour un document.
        # Insérer un document de test
        test_collection.insert_one({"test_id": 2, "value": "original"})
        
        # Mettre à jour
        result = test_collection.update_one(
            {"test_id": 2},
            {"$set": {"value": "updated", "modified_at": datetime.now()}}
        )
        
        assert result.modified_count == 1, "Un document devrait être modifié"
        
        # Vérifier la modification
        updated = test_collection.find_one({"test_id": 2})
        assert updated["value"] == "updated"
        print("    Mise à jour autorisée et réussie")
    
    def test_delete_document(self, test_collection):
        #Test que l'utilisateur peut supprimer un document.
        # Insérer un document de test
        test_collection.insert_one({"test_id": 3, "to_delete": True})
        
        # Supprimer
        result = test_collection.delete_one({"test_id": 3})
        
        assert result.deleted_count == 1, "Un document devrait être supprimé"
        
        # Vérifier la suppression
        deleted = test_collection.find_one({"test_id": 3})
        assert deleted is None, "Le document ne devrait plus exister"
        print("    Suppression autorisée et réussie")
    
    def test_create_index(self, test_collection):
        #Test que l'utilisateur peut créer un index.
        index_name = test_collection.create_index([("test_id", 1)])
        assert index_name is not None, "L'index devrait être créé"
        
        # Vérifier que l'index existe
        indexes = list(test_collection.list_indexes())
        index_names = [idx["name"] for idx in indexes]
        assert "test_id_1" in index_names
        print("    Création d'index autorisée")
    
    def test_drop_collection(self, mongodb_connection):
        #Test que l'utilisateur peut supprimer une collection.
        # Créer une collection temporaire
        temp_collection = mongodb_connection["temp_to_drop"]
        temp_collection.insert_one({"temp": "data"})
        
        # Supprimer la collection
        temp_collection.drop()
        
        # Vérifier que la collection n'existe plus
        collections = mongodb_connection.list_collection_names()
        assert "temp_to_drop" not in collections
        print("    Suppression de collection autorisée")


class TestBulkOperations:
    #Tests des opérations en masse.

    def test_bulk_insert(self, test_collection):
        #Test d'insertion en masse.
        documents = [
            {"bulk_id": i, "value": f"bulk_{i}"}
            for i in range(10, 20)
        ]
        
        result = test_collection.insert_many(documents)
        assert len(result.inserted_ids) == 10, "10 documents devraient être insérés"
        print("    Insertion en masse réussie: 10 documents")
    
    def test_bulk_update(self, test_collection):
        #Test de mise à jour en masse.
        # Préparer les données
        test_collection.insert_many([
            {"bulk_update": True, "status": "pending"}
            for _ in range(5)
        ])
        
        # Mise à jour en masse
        result = test_collection.update_many(
            {"bulk_update": True},
            {"$set": {"status": "completed"}}
        )
        
        assert result.modified_count >= 5, "Au moins 5 documents devraient être modifiés"
        print(f"    Mise à jour en masse réussie: {result.modified_count} documents")
    
    def test_bulk_delete(self, test_collection):
        #Test de suppression en masse.
        # Préparer les données
        test_collection.insert_many([
            {"bulk_delete": True}
            for _ in range(5)
        ])
        
        # Suppression en masse
        result = test_collection.delete_many({"bulk_delete": True})
        
        assert result.deleted_count >= 5, "Au moins 5 documents devraient être supprimés"
        print(f"    Suppression en masse réussie: {result.deleted_count} documents")


class TestAggregationAndQueries:
    #Tests des requêtes et agrégations.

    def test_complex_query(self, collection):
        #Test de requête complexe.
        results = list(collection.find({
            "Age": {"$gte": 30, "$lte": 40},
            "Gender": "Male"
        }).limit(10))
        
        assert len(results) > 0, "Des résultats devraient être trouvés"
        print(f"    Requête complexe réussie: {len(results)} documents")
    
    def test_aggregation_pipeline(self, collection):
        #Test de pipeline d'agrégation complexe.
        pipeline = [
            {"$group": {
                "_id": "$Medical Condition",
                "count": {"$sum": 1},
                "avg_age": {"$avg": "$Age"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        assert len(results) > 0, "Des résultats d'agrégation devraient être trouvés"
        print(f"    Agrégation complexe réussie: {len(results)} groupes")