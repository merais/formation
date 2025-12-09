"""
Script de nettoyage du bucket S3
Supprime les fichiers raw et archive les fichiers cleaned après vérification MongoDB
"""
import os
import time
from dotenv import load_dotenv
import boto3
from pymongo import MongoClient
from botocore.exceptions import ClientError
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
    
    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
    return MongoClient(mongo_uri)


def verify_data_in_mongodb(mongo_client, file_key):
    """
    Vérifier que les données d'un fichier ont bien été importées dans MongoDB
    Retourne True si le fichier est dans import_metadata, False sinon
    """
    try:
        db_name = os.getenv('MONGODB_DATABASE', 'weather_data')
        db = mongo_client[db_name]
        metadata_collection = db['import_metadata']
        
        # Chercher le fichier dans les métadonnées
        metadata = metadata_collection.find_one({'file_key': file_key})
        
        if metadata:
            print(f"[OK] Fichier {file_key} vérifié dans MongoDB")
            print(f"     - Importé le: {metadata.get('imported_at')}")
            print(f"     - Enregistrements: {metadata.get('record_count')}")
            print(f"     - Insérés: {metadata.get('inserted')}, Mis à jour: {metadata.get('updated')}")
            return True
        else:
            print(f"[AVERTISSEMENT] Fichier {file_key} non trouvé dans les métadonnées MongoDB")
            return False
            
    except Exception as e:
        print(f"[ERREUR] Impossible de vérifier les données MongoDB: {e}")
        return False


def list_s3_files(s3_client, bucket, prefix):
    """Lister tous les fichiers dans un préfixe S3"""
    try:
        files = []
        paginator = s3_client.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Ignorer les "dossiers" (clés se terminant par /)
                    if not obj['Key'].endswith('/'):
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified']
                        })
        
        return files
        
    except ClientError as e:
        print(f"[ERREUR] Impossible de lister les fichiers S3: {e}")
        return []


def delete_s3_file(s3_client, bucket, file_key):
    """Supprimer un fichier dans S3"""
    try:
        s3_client.delete_object(Bucket=bucket, Key=file_key)
        print(f"[OK] Fichier supprimé: {file_key}")
        return True
    except ClientError as e:
        print(f"[ERREUR] Impossible de supprimer {file_key}: {e}")
        return False


def move_s3_file(s3_client, bucket, source_key, destination_key):
    """Déplacer un fichier dans S3 (copie + suppression)"""
    try:
        # Copier le fichier
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': source_key},
            Key=destination_key
        )
        print(f"[OK] Fichier copié: {source_key} → {destination_key}")
        
        # Supprimer l'original
        s3_client.delete_object(Bucket=bucket, Key=source_key)
        print(f"[OK] Fichier original supprimé: {source_key}")
        
        return True
        
    except ClientError as e:
        print(f"[ERREUR] Impossible de déplacer {source_key}: {e}")
        return False


def cleanup_bucket(dry_run=False):
    """
    Nettoyer le bucket S3:
    1. Vérifier que les fichiers cleaned sont dans MongoDB
    2. Déplacer les fichiers cleaned vers archive
    3. Supprimer les fichiers raw correspondants
    
    Args:
        dry_run: Si True, affiche les actions sans les exécuter
    """
    s3_client = get_s3_client()
    mongo_client = get_mongo_client()
    
    bucket = os.getenv('S3_BUCKET_NAME')
    prefix_source = os.getenv('S3_PREFIX_SOURCE', '01_raw/')
    prefix_cleaned = os.getenv('S3_PREFIX_DESTINATION', '02_cleaned/')
    prefix_archive = os.getenv('S3_PREFIX_ARCHIVE', '03_archived/')
    
    print(f"\n{'='*70}")
    print(f"NETTOYAGE DU BUCKET S3: {bucket}")
    print(f"{'='*70}")
    if dry_run:
        print("[MODE TEST] Aucune modification ne sera effectuée\n")
    else:
        print("[MODE PRODUCTION] Les fichiers seront modifiés\n")
    
    # 1. Lister les fichiers cleaned
    print(f"[INFO] Recherche des fichiers dans {prefix_cleaned}...")
    cleaned_files = list_s3_files(s3_client, bucket, prefix_cleaned)
    
    if not cleaned_files:
        print(f"[INFO] Aucun fichier à nettoyer dans {prefix_cleaned}")
        return
    
    print(f"[INFO] {len(cleaned_files)} fichier(s) trouvé(s) dans {prefix_cleaned}\n")
    
    # 2. Pour chaque fichier cleaned
    archived_count = 0
    deleted_raw_count = 0
    
    for file_info in cleaned_files:
        file_key = file_info['key']
        filename = os.path.basename(file_key)
        
        print(f"\n{'-'*70}")
        print(f"Traitement de: {filename}")
        print(f"{'-'*70}")
        
        # Vérifier que le fichier est dans MongoDB
        if not verify_data_in_mongodb(mongo_client, file_key):
            print(f"[SKIP] Fichier non importé dans MongoDB - Passage au suivant")
            continue
        
        # Déplacer vers archive
        archive_key = os.path.join(prefix_archive, filename)
        
        if dry_run:
            print(f"[DRY-RUN] Déplacement vers archive: {file_key} → {archive_key}")
        else:
            if move_s3_file(s3_client, bucket, file_key, archive_key):
                archived_count += 1
        
        # Supprimer les fichiers raw correspondants
        print(f"\n[INFO] Recherche des fichiers raw associés...")
        raw_files = list_s3_files(s3_client, bucket, prefix_source)
        
        if raw_files:
            print(f"[INFO] {len(raw_files)} fichier(s) trouvé(s) dans {prefix_source}")
            
            for raw_file in raw_files:
                raw_key = raw_file['key']
                
                if dry_run:
                    print(f"[DRY-RUN] Suppression: {raw_key}")
                else:
                    if delete_s3_file(s3_client, bucket, raw_key):
                        deleted_raw_count += 1
        else:
            print(f"[INFO] Aucun fichier raw à supprimer")
    
    # Résumé
    print(f"\n{'='*70}")
    print(f"RÉSUMÉ DU NETTOYAGE")
    print(f"{'='*70}")
    if dry_run:
        print(f"[DRY-RUN] Fichiers qui seraient archivés: {len([f for f in cleaned_files if verify_data_in_mongodb(mongo_client, f['key'])])}")
        raw_files = list_s3_files(s3_client, bucket, prefix_source)
        print(f"[DRY-RUN] Fichiers raw qui seraient supprimés: {len(raw_files)}")
    else:
        print(f"[OK] Fichiers archivés: {archived_count}")
        print(f"[OK] Fichiers raw supprimés: {deleted_raw_count}")
    print(f"{'='*70}\n")
    
    mongo_client.close()


def watch_and_cleanup(interval=3600, dry_run=False):
    """
    Surveiller et nettoyer automatiquement le bucket S3
    
    Args:
        interval: Intervalle en secondes entre chaque nettoyage (défaut: 1 heure)
        dry_run: Si True, mode test sans modifications
    """
    print(f"[INFO] Démarrage du service de nettoyage automatique")
    print(f"[INFO] Intervalle: {interval} secondes ({interval//60} minutes)")
    print(f"[INFO] Mode: {'TEST (dry-run)' if dry_run else 'PRODUCTION'}\n")
    
    while True:
        try:
            print(f"\n[INFO] Nettoyage planifié à {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            cleanup_bucket(dry_run=dry_run)
            
            print(f"[INFO] Prochain nettoyage dans {interval//60} minutes...")
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n[INFO] Arrêt du service de nettoyage")
            break
        except Exception as e:
            print(f"[ERREUR] Erreur dans la boucle de nettoyage: {e}")
            print(f"[INFO] Nouvelle tentative dans 5 minutes...")
            time.sleep(300)


if __name__ == "__main__":
    import sys
    
    # Vérifier les arguments
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    watch = '--watch' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Usage: python ABAI_P8_script_04_cleanup_s3.py [OPTIONS]

Options:
  --dry-run, --test    Mode test: affiche les actions sans les exécuter
  --watch              Mode surveillance: nettoyage automatique toutes les heures
  --help, -h           Affiche cette aide

Exemples:
  # Nettoyage unique en mode test
  python ABAI_P8_script_04_cleanup_s3.py --dry-run
  
  # Nettoyage unique en mode production
  python ABAI_P8_script_04_cleanup_s3.py
  
  # Surveillance continue (mode production)
  python ABAI_P8_script_04_cleanup_s3.py --watch
  
  # Surveillance continue (mode test)
  python ABAI_P8_script_04_cleanup_s3.py --watch --dry-run
""")
        sys.exit(0)
    
    if watch:
        # Mode surveillance
        interval = int(os.getenv('CLEANUP_INTERVAL', '3600'))  # 1 heure par défaut
        watch_and_cleanup(interval=interval, dry_run=dry_run)
    else:
        # Nettoyage unique
        cleanup_bucket(dry_run=dry_run)
