"""
Script pour importer automatiquement les données JSON depuis S3 vers MongoDB
"""
import os
import time
from dotenv import load_dotenv
import boto3
from pymongo import MongoClient
from botocore.exceptions import ClientError
import json
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

def get_s3_client():
    """Créer un client S3"""
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'eu-west-1')
    )

def get_mongo_client():
    """Créer un client MongoDB"""
    # Construire l'URI MongoDB à partir des variables d'environnement
    mongo_host = os.getenv('MONGODB_HOST', 'mongodb.weather-pipeline.local')
    mongo_port = os.getenv('MONGODB_PORT', '27017')
    mongo_user = os.getenv('MONGODB_ROOT_USER', 'admin')
    mongo_password = os.getenv('MONGODB_ROOT_PASSWORD', '')
    
    if mongo_user and mongo_password:
        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
    else:
        mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/"
    
    print(f"[INFO] Connexion MongoDB: mongodb://{mongo_user}:****@{mongo_host}:{mongo_port}/")
    return MongoClient(mongo_uri)

def list_s3_files(s3_client, bucket, prefix):
    """Lister les fichiers JSON dans S3"""
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.json'):
                    files.append({
                        'key': obj['Key'],
                        'last_modified': obj['LastModified'],
                        'size': obj['Size']
                    })
        
        return sorted(files, key=lambda x: x['last_modified'], reverse=True)
    except ClientError as e:
        print(f"[ERREUR] Impossible de lister les fichiers S3: {e}")
        return []

def import_json_to_mongodb(s3_client, mongo_client, bucket, file_key):
    """Importer un fichier JSON depuis S3 vers MongoDB"""
    try:
        # Vérifier la connexion MongoDB avant chaque import
        print(f"[TEST] Vérification de la base de données avant import de {file_key}...")
        if not test_database_connection():
            print(f"[ERREUR] Import annulé - Base de données non disponible")
            return False
        
        # Télécharger le fichier depuis S3
        print(f"[INFO] Téléchargement de {file_key}...")
        response = s3_client.get_object(Bucket=bucket, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        
        print(f"[INFO] {len(data)} enregistrements trouvés")
        
        # Se connecter à la base de données
        db = mongo_client[os.getenv('MONGODB_DATABASE', 'weather_data')]
        collection = db[os.getenv('MONGODB_COLLECTION', 'measurements')]
        
        # Créer des index si nécessaire (avec gestion des erreurs)
        try:
            collection.create_index([('unique_key', 1)], unique=True, name='idx_unique_key')
        except Exception:
            pass  # Index déjà existant
        
        try:
            collection.create_index([('id_station', 1), ('dh_utc', 1)], name='idx_station_date')
        except Exception:
            pass
        
        try:
            collection.create_index([('dh_utc', 1)], name='idx_date')
        except Exception:
            pass
        
        # Insérer les données (upsert sur unique_key)
        inserted_count = 0
        updated_count = 0
        
        for record in data:
            result = collection.update_one(
                {'unique_key': record['unique_key']},
                {'$set': record},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
            elif result.modified_count > 0:
                updated_count += 1
        
        print(f"[OK] Import terminé: {inserted_count} insérés, {updated_count} mis à jour")
        
        # Enregistrer le fichier comme traité
        metadata_collection = db['import_metadata']
        metadata_collection.update_one(
            {'file_key': file_key},
            {
                '$set': {
                    'file_key': file_key,
                    'imported_at': datetime.now().isoformat(),
                    'record_count': len(data),
                    'inserted': inserted_count,
                    'updated': updated_count
                }
            },
            upsert=True
        )
        
        return True
        
    except Exception as e:
        print(f"[ERREUR] Impossible d'importer {file_key}: {e}")
        return False

def get_processed_files(mongo_client):
    """Récupérer la liste des fichiers déjà importés"""
    db = mongo_client[os.getenv('MONGODB_DATABASE', 'weather_data')]
    metadata_collection = db['import_metadata']
    
    processed = metadata_collection.find({}, {'file_key': 1, '_id': 0})
    return set(doc['file_key'] for doc in processed)

def test_database_connection():
    """
    Tester la connexion MongoDB et les permissions CRUD avant l'import
    Retourne True si tous les tests passent, False sinon
    """
    try:
        import subprocess
        import sys
        
        print("\n[TEST] Vérification de la connexion MongoDB et des permissions...")
        
        # Exécuter les tests pytest
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'ABAI_P8_script_03_test_mongodb.py', '-v', '--tb=short'],
            capture_output=True,
            text=True
        )
        
        # Afficher la sortie
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("[OK] Tests MongoDB réussis - Base de données prête\n")
            return True
        else:
            print("[ERREUR] Tests MongoDB échoués - Vérifier la connexion et les permissions\n")
            return False
            
    except Exception as e:
        print(f"[ERREUR] Impossible d'exécuter les tests: {e}")
        return False


def watch_and_import():
    """Surveiller S3 et importer automatiquement les nouveaux fichiers"""
    # Tester la connexion MongoDB au démarrage
    if not test_database_connection():
        print("[ERREUR] Arrêt du service - Base de données non disponible")
        return
    
    s3_client = get_s3_client()
    mongo_client = get_mongo_client()
    
    bucket = os.getenv('S3_BUCKET_NAME')
    prefix = os.getenv('S3_PREFIX_DESTINATION', '02_cleaned/')
    watch_interval = int(os.getenv('WATCH_INTERVAL', '300'))  # 5 minutes par défaut
    
    print(f"[INFO] Surveillance du bucket S3: s3://{bucket}/{prefix}")
    print(f"[INFO] Intervalle de vérification: {watch_interval} secondes")
    
    while True:
        try:
            # Lister les fichiers dans S3
            s3_files = list_s3_files(s3_client, bucket, prefix)
            
            # Récupérer les fichiers déjà traités
            processed_files = get_processed_files(mongo_client)
            
            # Identifier les nouveaux fichiers
            new_files = [f for f in s3_files if f['key'] not in processed_files]
            
            if new_files:
                print(f"\n[INFO] {len(new_files)} nouveau(x) fichier(s) détecté(s)")
                
                for file_info in new_files:
                    file_key = file_info['key']
                    print(f"\n[IMPORT] Traitement de {file_key}...")
                    
                    success = import_json_to_mongodb(s3_client, mongo_client, bucket, file_key)
                    
                    if success:
                        print(f"[OK] {file_key} importé avec succès")
                    else:
                        print(f"[ERREUR] Échec de l'import de {file_key}")
            else:
                print(f"[INFO] Aucun nouveau fichier à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Attendre avant la prochaine vérification
            time.sleep(watch_interval)
            
        except KeyboardInterrupt:
            print("\n[INFO] Arrêt du service de surveillance")
            break
        except Exception as e:
            print(f"[ERREUR] Erreur dans la boucle de surveillance: {e}")
            time.sleep(60)  # Attendre 1 minute avant de réessayer

if __name__ == "__main__":
    print("[INFO] Démarrage du service d'import automatique S3 → MongoDB")
    watch_and_import()
