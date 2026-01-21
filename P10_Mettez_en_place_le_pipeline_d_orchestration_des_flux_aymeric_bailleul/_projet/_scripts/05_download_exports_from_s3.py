"""
Script pour télécharger les exports depuis S3/EXPORTS/ vers _exports/

Télécharge le dossier d'exports le plus récent depuis S3/EXPORTS/YYYYMMDD_HHMMSS/
et le sauvegarde dans _exports/. Si exécuté plusieurs fois, met à jour avec
la version la plus récente.

Usage:
    cd _projet
    poetry run python _scripts/05_download_exports_from_s3.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Configuration
BUCKET_NAME = "bottleneck-pipeline-p10"
AWS_REGION = "eu-west-3"
S3_PREFIX = "EXPORTS"

# Fichiers exports attendus
EXPECTED_FILES = [
    "rapport_ca.xlsx",
    "vins_premium.csv",
    "vins_ordinaires.csv",
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


def list_export_folders(s3_client):
    """
    Liste tous les dossiers d'exports dans S3/EXPORTS/.
    
    Args:
        s3_client: Client boto3 S3
        
    Returns:
        list: Liste des dossiers d'exports triés par date (plus récent en dernier)
    """
    try:
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=f"{S3_PREFIX}/",
            Delimiter="/",
        )
        
        if "CommonPrefixes" not in response:
            return []
        
        folders = [
            prefix["Prefix"].rstrip("/").split("/")[-1]
            for prefix in response["CommonPrefixes"]
        ]
        
        # Tri par nom (format YYYYMMDD_HHMMSS permet tri chronologique)
        folders.sort()
        return folders
        
    except ClientError as e:
        print(f"[ERREUR] Erreur lors de la liste des dossiers : {e}")
        return []


def download_file_from_s3(s3_client, s3_key: str, local_file: Path):
    """
    Télécharge un fichier depuis S3.
    
    Args:
        s3_client: Client boto3 S3
        s3_key: Clé S3 source
        local_file: Chemin local de destination
    """
    try:
        print(f"  Downloading {s3_key.split('/')[-1]} -> {local_file.name}")
        s3_client.download_file(BUCKET_NAME, s3_key, str(local_file))
        print(f"  [OK] Download reussi")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            print(f"  [ATTENTION] Fichier non trouve sur S3")
        else:
            print(f"  [ERREUR] Erreur S3 : {e}")
        return False


def main():
    """Fonction principale."""
    print("=" * 80)
    print("DOWNLOAD DES EXPORTS DEPUIS S3")
    print("=" * 80)
    print(f"\nBucket S3  : {BUCKET_NAME}")
    print(f"Région     : {AWS_REGION}")
    print(f"Source     : s3://{BUCKET_NAME}/{S3_PREFIX}/")
    print()
    
    # Création du dossier _exports/ si inexistant
    exports_dir = Path("_exports")
    exports_dir.mkdir(exist_ok=True)
    
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
    
    # Liste des dossiers d'exports
    print("Recherche des dossiers d'exports...")
    export_folders = list_export_folders(s3_client)
    
    if not export_folders:
        print("[ERREUR] Aucun dossier d'export trouve dans S3/EXPORTS/")
        print("   Executez d'abord le workflow Kestra")
        sys.exit(1)
    
    # Sélection du dossier le plus récent
    latest_folder = export_folders[-1]
    print(f"\n[INFO] Dossier le plus recent : {latest_folder}")
    
    try:
        folder_date = datetime.strptime(latest_folder, "%Y%m%d_%H%M%S")
        print(f"   Date d'export : {folder_date.strftime('%d/%m/%Y à %H:%M:%S')}")
    except ValueError:
        pass
    
    print(f"\n{'='*80}")
    print("TÉLÉCHARGEMENT DES FICHIERS")
    print("=" * 80)
    print()
    
    # Download des fichiers
    success_count = 0
    failed_count = 0
    
    for filename in EXPECTED_FILES:
        s3_key = f"{S3_PREFIX}/{latest_folder}/{filename}"
        local_file = exports_dir / filename
        
        if download_file_from_s3(s3_client, s3_key, local_file):
            success_count += 1
            
            # Afficher la taille du fichier
            file_size = local_file.stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            print(f"  Taille : {size_str}")
        else:
            failed_count += 1
        print()
    
    # Résumé
    print("=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Fichiers téléchargés : {success_count}/{len(EXPECTED_FILES)}")
    print(f"Fichiers en erreur   : {failed_count}/{len(EXPECTED_FILES)}")
    print(f"Destination locale   : {exports_dir.absolute()}")
    
    if failed_count == 0:
        print("\n[OK] Tous les fichiers ont ete telecharges avec succes")
        print("\nFichiers disponibles :")
        for filename in EXPECTED_FILES:
            local_file = exports_dir / filename
            if local_file.exists():
                print(f"  - {local_file}")
        sys.exit(0)
    else:
        print(f"\n[ATTENTION] {failed_count} fichier(s) non telecharge(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
