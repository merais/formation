"""
Tests d'intégration pour MongoDB - Vérification CRUD et droits d'accès
Exécuté automatiquement avant chaque import pour valider la connexion et les permissions
"""
import os
import pytest
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


@pytest.fixture
def mongo_client():
    """Fixture pour créer un client MongoDB"""
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017/')
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    yield client
    client.close()


@pytest.fixture
def db_collection(mongo_client):
    """Fixture pour accéder à la collection de test"""
    db_name = os.getenv('MONGODB_DATABASE', 'weather_data')
    collection_name = os.getenv('MONGODB_COLLECTION', 'measurements')
    db = mongo_client[db_name]
    collection = db[collection_name]
    return collection


class TestMongoDBConnection:
    """Tests de connexion à MongoDB"""
    
    def test_connection_availability(self, mongo_client):
        """Vérifier que MongoDB est disponible"""
        try:
            # Envoyer un ping pour vérifier la connexion
            mongo_client.admin.command('ping')
        except ConnectionFailure as e:
            pytest.fail(f"Impossible de se connecter à MongoDB: {e}")
    
    def test_database_exists(self, mongo_client):
        """Vérifier que la base de données existe"""
        db_name = os.getenv('MONGODB_DATABASE', 'weather_data')
        db_list = mongo_client.list_database_names()
        assert db_name in db_list, f"La base de données '{db_name}' n'existe pas"
    
    def test_collection_exists(self, mongo_client):
        """Vérifier que la collection existe"""
        db_name = os.getenv('MONGODB_DATABASE', 'weather_data')
        collection_name = os.getenv('MONGODB_COLLECTION', 'measurements')
        db = mongo_client[db_name]
        collections = db.list_collection_names()
        assert collection_name in collections, f"La collection '{collection_name}' n'existe pas"


class TestMongoDBCRUD:
    """Tests des opérations CRUD"""
    
    def test_create_document(self, db_collection):
        """Test CREATE - Insertion d'un document"""
        test_doc = {
            'unique_key': f'TEST_CREATE_{datetime.now().timestamp()}',
            'id_station': 'TEST99999',
            'dh_utc': datetime.now().isoformat(),
            'temperature': 20.5,
            'humidite': 65.0,
            'test_flag': True
        }
        
        try:
            result = db_collection.insert_one(test_doc)
            assert result.inserted_id is not None, "Échec de l'insertion"
            
            # Nettoyer
            db_collection.delete_one({'_id': result.inserted_id})
        except OperationFailure as e:
            pytest.fail(f"Pas de permission d'écriture (CREATE): {e}")
    
    def test_read_documents(self, db_collection):
        """Test READ - Lecture de documents"""
        try:
            # Tenter de lire des documents
            count = db_collection.count_documents({})
            assert count >= 0, "Impossible de compter les documents"
            
            # Tenter de lire un document
            doc = db_collection.find_one()
            # Pas d'erreur même si aucun document n'existe
        except OperationFailure as e:
            pytest.fail(f"Pas de permission de lecture (READ): {e}")
    
    def test_update_document(self, db_collection):
        """Test UPDATE - Mise à jour d'un document"""
        # Créer un document de test
        test_doc = {
            'unique_key': f'TEST_UPDATE_{datetime.now().timestamp()}',
            'id_station': 'TEST99999',
            'dh_utc': datetime.now().isoformat(),
            'temperature': 20.5,
            'test_flag': True
        }
        
        try:
            # Insérer
            result = db_collection.insert_one(test_doc)
            doc_id = result.inserted_id
            
            # Mettre à jour
            update_result = db_collection.update_one(
                {'_id': doc_id},
                {'$set': {'temperature': 25.0, 'updated': True}}
            )
            assert update_result.modified_count == 1, "Échec de la mise à jour"
            
            # Vérifier la mise à jour
            updated_doc = db_collection.find_one({'_id': doc_id})
            assert updated_doc['temperature'] == 25.0, "La température n'a pas été mise à jour"
            assert updated_doc.get('updated') is True, "Le flag updated n'a pas été ajouté"
            
            # Nettoyer
            db_collection.delete_one({'_id': doc_id})
        except OperationFailure as e:
            pytest.fail(f"Pas de permission de mise à jour (UPDATE): {e}")
    
    def test_upsert_document(self, db_collection):
        """Test UPSERT - Insertion ou mise à jour"""
        unique_key = f'TEST_UPSERT_{datetime.now().timestamp()}'
        
        try:
            # Premier upsert (insertion)
            result1 = db_collection.update_one(
                {'unique_key': unique_key},
                {'$set': {
                    'unique_key': unique_key,
                    'id_station': 'TEST99999',
                    'temperature': 20.5
                }},
                upsert=True
            )
            assert result1.upserted_id is not None, "Échec de l'upsert (insertion)"
            
            # Deuxième upsert (mise à jour)
            result2 = db_collection.update_one(
                {'unique_key': unique_key},
                {'$set': {'temperature': 25.0}},
                upsert=True
            )
            assert result2.modified_count == 1, "Échec de l'upsert (mise à jour)"
            
            # Vérifier
            doc = db_collection.find_one({'unique_key': unique_key})
            assert doc['temperature'] == 25.0, "La température n'a pas été mise à jour"
            
            # Nettoyer
            db_collection.delete_one({'unique_key': unique_key})
        except OperationFailure as e:
            pytest.fail(f"Pas de permission d'upsert: {e}")
    
    def test_delete_document(self, db_collection):
        """Test DELETE - Suppression d'un document"""
        # Créer un document de test
        test_doc = {
            'unique_key': f'TEST_DELETE_{datetime.now().timestamp()}',
            'id_station': 'TEST99999',
            'dh_utc': datetime.now().isoformat(),
            'test_flag': True
        }
        
        try:
            # Insérer
            result = db_collection.insert_one(test_doc)
            doc_id = result.inserted_id
            
            # Supprimer
            delete_result = db_collection.delete_one({'_id': doc_id})
            assert delete_result.deleted_count == 1, "Échec de la suppression"
            
            # Vérifier la suppression
            deleted_doc = db_collection.find_one({'_id': doc_id})
            assert deleted_doc is None, "Le document n'a pas été supprimé"
        except OperationFailure as e:
            pytest.fail(f"Pas de permission de suppression (DELETE): {e}")


class TestMongoDBIndexes:
    """Tests des index MongoDB"""
    
    def test_unique_key_index(self, db_collection):
        """Vérifier que l'index unique sur unique_key fonctionne"""
        unique_key = f'TEST_INDEX_{datetime.now().timestamp()}'
        
        test_doc = {
            'unique_key': unique_key,
            'id_station': 'TEST99999',
            'temperature': 20.5
        }
        
        try:
            # Première insertion
            db_collection.insert_one(test_doc.copy())
            
            # Deuxième insertion avec la même unique_key (devrait échouer)
            with pytest.raises(Exception):
                db_collection.insert_one(test_doc.copy())
            
            # Nettoyer
            db_collection.delete_one({'unique_key': unique_key})
        except Exception as e:
            # Nettoyer en cas d'erreur
            db_collection.delete_one({'unique_key': unique_key})
            pytest.fail(f"L'index unique ne fonctionne pas correctement: {e}")
    
    def test_indexes_exist(self, db_collection):
        """Vérifier que tous les index requis existent"""
        indexes = db_collection.index_information()
        
        required_indexes = {
            'idx_unique_key': ['unique_key'],
            'idx_station_date': ['id_station', 'dh_utc'],
            'idx_date': ['dh_utc'],
            'idx_station': ['id_station'],
            'idx_processed_at': ['processed_at']
        }
        
        for index_name, expected_keys in required_indexes.items():
            assert index_name in indexes, f"Index manquant: {index_name}"


class TestMongoDBMetadata:
    """Tests de la collection de métadonnées"""
    
    def test_metadata_collection_crud(self, mongo_client):
        """Tester les opérations CRUD sur la collection de métadonnées"""
        db_name = os.getenv('MONGODB_DATABASE', 'weather_data')
        db = mongo_client[db_name]
        metadata_collection = db['import_metadata']
        
        test_metadata = {
            'file_key': f'test/TEST_{datetime.now().timestamp()}.json',
            'imported_at': datetime.now().isoformat(),
            'record_count': 100,
            'inserted': 100,
            'updated': 0
        }
        
        try:
            # CREATE
            result = metadata_collection.insert_one(test_metadata)
            assert result.inserted_id is not None
            
            # READ
            doc = metadata_collection.find_one({'_id': result.inserted_id})
            assert doc is not None
            assert doc['record_count'] == 100
            
            # UPDATE
            metadata_collection.update_one(
                {'_id': result.inserted_id},
                {'$set': {'updated': 5}}
            )
            
            updated_doc = metadata_collection.find_one({'_id': result.inserted_id})
            assert updated_doc['updated'] == 5
            
            # DELETE
            metadata_collection.delete_one({'_id': result.inserted_id})
            
            deleted_doc = metadata_collection.find_one({'_id': result.inserted_id})
            assert deleted_doc is None
        except Exception as e:
            # Nettoyer
            metadata_collection.delete_one({'file_key': test_metadata['file_key']})
            pytest.fail(f"Erreur dans les opérations CRUD sur metadata: {e}")


def run_database_tests():
    """
    Fonction principale pour exécuter tous les tests
    Retourne True si tous les tests passent, False sinon
    """
    print("[INFO] Exécution des tests de connexion MongoDB...")
    
    # Exécuter pytest programmatiquement
    result = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    if result == 0:
        print("[OK] Tous les tests MongoDB ont réussi")
        return True
    else:
        print("[ERREUR] Certains tests MongoDB ont échoué")
        return False


if __name__ == "__main__":
    success = run_database_tests()
    exit(0 if success else 1)
