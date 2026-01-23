"""
Script pour uploader les fichiers sources vers S3/RAW/

Upload les 3 fichiers sources depuis le dossier sources/ vers le bucket S3
dans le dossier RAW/ pour être utilisés par le workflow Kestra.

Usage:
    cd _projet
    poetry run python _scripts/04_upload_sources_to_s3.py
"""

import os
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Configuration
BUCKET_NAME = "bottleneck-pipeline-p10"
AWS_REGION = "eu-west-3"
S3_PREFIX = "RAW"

# Fichiers sources à uploader
SOURCE_FILES = [
    "fichier_erp.xlsx",
    "fichier_liaison.xlsx",
    "fichier_web.xlsx",
]


def get_aws_credentials():
    """
    Récupère les credentials AWS depuis les variables d'environnement.
    
    Returns:
        tuple: (access_key_id, secret_access_key) ou (None, None) si non trouvés
    """
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not access_key or not secret_key:
        print("[ATTENTION] Variables d'environnement AWS non trouvées")
        print("            Tentative avec les credentials AWS par défaut (~/.aws/)")
        return None, None
    
    return access_key, secret_key


def upload_file_to_s3(s3_client, local_file: Path, s3_key: str):
    """
    Upload un fichier vers S3.
    
    Args:
        s3_client: Client boto3 S3
        local_file: Chemin local du fichier
        s3_key: Clé S3 de destination
    """
    try:
        print(f"  Uploading {local_file.name} -> s3://{BUCKET_NAME}/{s3_key}")
        s3_client.upload_file(str(local_file), BUCKET_NAME, s3_key)
        print(f"  [OK] Upload reussi")
        return True
    except FileNotFoundError:
        print(f"  [ERREUR] Fichier non trouve : {local_file}")
        return False
    except NoCredentialsError:
        print(f"  [ERREUR] Credentials AWS non trouvees")
        return False
    except ClientError as e:
        print(f"  [ERREUR] Erreur S3 : {e}")
        return False


def main():
    """Fonction principale."""
    print("=" * 80)
    print("UPLOAD DES FICHIERS SOURCES VERS S3")
    print("=" * 80)
    print(f"\nBucket S3  : {BUCKET_NAME}")
    print(f"Région     : {AWS_REGION}")
    print(f"Destination: s3://{BUCKET_NAME}/{S3_PREFIX}/")
    print()
    
    # Vérification du dossier sources/
    sources_dir = Path("sources")
    if not sources_dir.exists():
        print(f"[ERREUR] Dossier sources/ non trouve")
        print(f"   Chemin attendu : {sources_dir.absolute()}")
        sys.exit(1)
    
    # Configuration du client S3
    access_key, secret_key = get_aws_credentials()
    
    if access_key and secret_key:
        s3_client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
    else:
        # Utilise les credentials par défaut (~/.aws/credentials)
        s3_client = boto3.client("s3", region_name=AWS_REGION)
    
    # Test de connexion
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"[OK] Connexion au bucket {BUCKET_NAME} reussie\n")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            print(f"[ERREUR] Bucket {BUCKET_NAME} non trouve")
        elif error_code == "403":
            print(f"[ERREUR] Acces refuse au bucket {BUCKET_NAME}")
        else:
            print(f"[ERREUR] Erreur de connexion : {e}")
        sys.exit(1)
    except NoCredentialsError:
        print("[ERREUR] Credentials AWS non configurees")
        print("   Configurez AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY")
        sys.exit(1)
    
    # Upload des fichiers
    success_count = 0
    failed_count = 0
    
    for filename in SOURCE_FILES:
        local_file = sources_dir / filename
        s3_key = f"{S3_PREFIX}/{filename}"
        
        if upload_file_to_s3(s3_client, local_file, s3_key):
            success_count += 1
        else:
            failed_count += 1
        print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Fichiers uploadés  : {success_count}/{len(SOURCE_FILES)}")
    print(f"Fichiers en erreur : {failed_count}/{len(SOURCE_FILES)}")
    
    if failed_count == 0:
        print("\n[OK] Tous les fichiers ont ete uploades avec succes")
        print(f"\nVerification : aws s3 ls s3://{BUCKET_NAME}/{S3_PREFIX}/")
        sys.exit(0)
    else:
        print(f"\n[ATTENTION] {failed_count} fichier(s) non uploade(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
