"""
Script pour lire le contenu d'un bucket S3 avec boto3
"""
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import pandas as pd
from io import StringIO
from datetime import datetime


# =============================================================================
# FONCTIONS DE NETTOYAGE DES DONNÉES
# =============================================================================

def clean_temperature_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne de température : enlève l'unité °F et convertit en °C.
    (°F - 32) × 5/9
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('°F', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df[col_name] = (df[col_name] - 32) * 5 / 9
        df[col_name] = df[col_name].round(1)
    return df


def clean_speed_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne de vitesse : enlève l'unité mph et convertit en km/h.
    1 mph = 1.60934 km/h
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('mph', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df[col_name] = df[col_name] * 1.60934
        df[col_name] = df[col_name].round(1)
    return df


def clean_pressure_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne de pression : enlève l'unité in et convertit en hPa.
    1 inHg = 33.8639 hPa
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('in', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df[col_name] = df[col_name] * 33.8639
        df[col_name] = df[col_name].round(2)
    return df


def clean_precipitation_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne de précipitation : enlève l'unité in et convertit en mm.
    1 in = 25.4 mm
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('in', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df[col_name] = df[col_name] * 25.4
        df[col_name] = df[col_name].round(3)
    return df


def clean_solar_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne de rayonnement solaire : enlève l'unité w/m².
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('w/m²', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
        df[col_name] = df[col_name].round(1)
    return df


def clean_humidity_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Nettoie une colonne d'humidité : enlève le symbole %.
    """
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.replace('%', '', regex=False).str.strip()
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
    return df


def clean_wind_direction_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Convertit la direction du vent textuelle en degrés (0-360).
    Nord = 0°, Est = 90°, Sud = 180°, Ouest = 270°
    """
    if col_name in df.columns:
        wind_directions = {
            'NORTH': 0, 'N': 0,
            'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
            'EAST': 90, 'E': 90,
            'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'SOUTH': 180, 'S': 180,
            'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'WEST': 270, 'W': 270,
            'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        
        mask = df[col_name].notna()
        df.loc[mask, col_name] = df.loc[mask, col_name].astype(str).str.strip().str.upper()
        df[col_name] = df[col_name].map(wind_directions)
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
    
    return df


def merge_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fusionne les colonnes dupliquées en conservant les valeurs non-nulles.
    """
    # Créer une copie pour éviter les problèmes
    df = df.copy()
    
    # Identifier les colonnes dupliquées
    duplicated_cols = df.columns[df.columns.duplicated()].unique()
    
    for col in duplicated_cols:
        # Récupérer les indices des colonnes avec ce nom
        col_indices = [i for i, c in enumerate(df.columns) if c == col]
        
        if len(col_indices) > 1:
            # Fusionner en gardant la première valeur non-nulle
            merged_col = df.iloc[:, col_indices[0]].copy()
            for idx in col_indices[1:]:
                # Remplir les NaN avec les valeurs de la colonne suivante
                mask = merged_col.isna()
                merged_col[mask] = df.iloc[:, idx][mask]
            
            # Remplacer la première colonne avec les valeurs fusionnées
            df.iloc[:, col_indices[0]] = merged_col
    
    # Supprimer les colonnes dupliquées (garder la première)
    df = df.loc[:, ~df.columns.duplicated()]
    
    return df


def apply_data_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique toutes les transformations de nettoyage sur le DataFrame.
    """
    # Températures (°F → °C)
    df = clean_temperature_column(df, 'Temperature')
    df = clean_temperature_column(df, 'Dew Point')
    
    # Vitesses (mph → km/h)
    df = clean_speed_column(df, 'Speed')
    df = clean_speed_column(df, 'Gust')
    df = clean_speed_column(df, 'Wind Speed')
    
    # Pression (in → hPa)
    df = clean_pressure_column(df, 'Pressure')
    
    # Précipitations (in → mm)
    df = clean_precipitation_column(df, 'Precip. Rate.')
    df = clean_precipitation_column(df, 'Precip. Accum.')
    
    # Rayonnement solaire
    df = clean_solar_column(df, 'Solar')
    
    # Humidité
    df = clean_humidity_column(df, 'Humidity')
    
    # Direction du vent (texte → degrés)
    df = clean_wind_direction_column(df, 'Wind')
    
    # Renommer les colonnes pour standardiser (français)
    df = df.rename(columns={
        'Temperature': 'temperature',
        'Dew Point': 'point_de_rosee',
        'Humidity': 'humidite',
        'Wind': 'vent_direction',
        'Speed': 'vent_moyen',
        'Gust': 'vent_rafales',
        'Wind Speed': 'vent_moyen',
        'Pressure': 'pression',
        'Precip. Rate.': 'precip_rate',
        'Precip. Accum.': 'precip_accum',
        'UV': 'uv',
        'Solar': 'solar',
        'Time': 'time'
    })
    
    # Supprimer les colonnes temporaires si présentes
    columns_to_drop = ['Time']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
    
    # Fusionner les colonnes dupliquées
    df = merge_duplicate_columns(df)
    
    return df


def prepare_for_mongodb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare le DataFrame pour l'intégration dans MongoDB.
    - Convertit les types de données appropriés
    - Convertit les dates en format ISO
    - Remplace NaN/None par None (null en JSON)
    - Assure que les champs numériques sont bien typés
    """
    df = df.copy()
    
    # Convertir dh_utc en datetime puis en ISO format string
    if 'dh_utc' in df.columns:
        df['dh_utc'] = pd.to_datetime(df['dh_utc'], errors='coerce')
        # Convertir en ISO format pour MongoDB
        df['dh_utc'] = df['dh_utc'].dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    # Convertir les colonnes numériques
    numeric_columns = [
        'temperature', 'pression', 'humidite', 'point_de_rosee',
        'visibilite', 'vent_moyen', 'vent_rafales', 'vent_direction',
        'pluie_3h', 'pluie_1h', 'neige_au_sol', 'nebulosite',
        'precip_rate', 'precip_accum', 'uv', 'solar'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remplacer les NaN par None (null en JSON/MongoDB)
    df = df.where(pd.notna(df), None)
    
    # Ajouter un timestamp de traitement
    df['processed_at'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    
    # Ajouter un identifiant unique si nécessaire (pour MongoDB _id)
    # MongoDB générera automatiquement _id lors de l'insertion, mais on peut créer une clé composite
    if 'id_station' in df.columns and 'dh_utc' in df.columns:
        df['unique_key'] = df['id_station'].astype(str) + '_' + df['dh_utc'].astype(str)
    
    return df

def main():
    """Fonction principale pour lire les données depuis S3"""
    
    # Charger les variables d'environnement depuis le fichier .env
    load_dotenv()
    
    # Récupérer les informations de configuration depuis .env
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    s3_prefix = os.getenv("S3_PREFIX_SOURCE", "")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    
    # Vérifier que les informations essentielles sont présentes
    if not all([aws_access_key_id, aws_secret_access_key, s3_bucket]):
        print("❌ Erreur: Veuillez configurer les variables AWS dans le fichier .env")
        return
    
    print(f"📦 Configuration de la connexion S3...")
    print(f"   Bucket: {s3_bucket}")
    print(f"   Région: {aws_region}")
    if s3_prefix:
        print(f"   Préfixe: {s3_prefix}")
    
    try:
        # Créer une session boto3
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        # Créer un client S3
        s3_client = session.client('s3')
        
        # Vérifier la connexion en listant les objets
        print("\n🔍 Vérification de la connexion...")
        s3_client.head_bucket(Bucket=s3_bucket)
        print("✅ Connexion réussie!")
        
        # Lister TOUS les fichiers et dossiers dans le bucket
        print(f"\n📋 Listing de tous les fichiers et dossiers dans '{s3_bucket}/{s3_prefix}'...")
        
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix)
        
        all_objects = []
        folders = set()
        files = []
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    key = obj['Key']
                    all_objects.append({
                        'key': key,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
                    
                    # Détecter les dossiers (objets se terminant par /)
                    if key.endswith('/'):
                        folders.add(key)
                    else:
                        # Extraire le dossier parent
                        parent = '/'.join(key.split('/')[:-1])
                        if parent:
                            folders.add(parent + '/')
                        files.append({
                            'key': key,
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'],
                            'extension': key.split('.')[-1] if '.' in key else 'sans extension'
                        })
        
        # Afficher les dossiers
        if folders:
            print(f"\n📁 Dossiers trouvés ({len(folders)}):")
            for folder in sorted(folders):
                print(f"   📂 {folder}")
        
        # Afficher les fichiers groupés par extension
        if not files:
            print(f"\n⚠️  Aucun fichier trouvé dans '{s3_bucket}/{s3_prefix}'")
            return
        
        # Grouper par extension
        files_by_ext = {}
        for file in files:
            ext = file['extension']
            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file)
        
        print(f"\n📄 Fichiers trouvés (total: {len(files)}):")
        for ext, ext_files in sorted(files_by_ext.items()):
            print(f"\n   📌 Type: .{ext} ({len(ext_files)} fichier(s))")
            for file in ext_files[:10]:  # Afficher max 10 fichiers par type
                size_mb = file['size'] / (1024 * 1024)
                if size_mb < 1:
                    size_str = f"{file['size'] / 1024:.2f} KB"
                else:
                    size_str = f"{size_mb:.2f} MB"
                print(f"      • {file['key']} ({size_str})")
            if len(ext_files) > 10:
                print(f"      ... et {len(ext_files) - 10} autre(s) fichier(s)")
        
        # Filtrer les fichiers supportés (CSV, JSON, JSONL)
        supported_extensions = ['.csv', '.json', '.jsonl']
        supported_files = [f for f in files if any(f['key'].endswith(ext) for ext in supported_extensions)]
        
        if not supported_files:
            print(f"\n⚠️  Aucun fichier supporté trouvé pour le traitement")
            print(f"   Extensions supportées: {', '.join(supported_extensions)}")
            
            # Proposer de lire d'autres types de fichiers
            available_exts = list(files_by_ext.keys())
            if available_exts:
                print(f"\n💡 Types de fichiers disponibles: {', '.join(available_exts)}")
            return
        
        files = supported_files
        
        # Traiter les fichiers en fonction de leur extension
        print(f"\n✅ {len(files)} fichier(s) trouvé(s) pour traitement:")
        for i, file in enumerate(files, 1):
            size_mb = file['size'] / (1024 * 1024)
            print(f"   {i}. {file['key']} ({size_mb:.2f} MB) - {file['last_modified']}")
        
        # Déterminer le type de fichier
        file_extension = files[0]['key'].split('.')[-1].lower()
        
        # Lire le premier fichier
        print(f"\n📥 Lecture du premier fichier: {files[0]['key']}...")
        
        response = s3_client.get_object(Bucket=s3_bucket, Key=files[0]['key'])
        content = response['Body'].read().decode('utf-8')
        
        # Charger dans un DataFrame pandas selon le type
        if file_extension == 'csv':
            df = pd.read_csv(StringIO(content))
        elif file_extension in ['json', 'jsonl']:
            # JSONL = JSON Lines (un objet JSON par ligne)
            import json
            records = []
            for line in content.strip().split('\n'):
                if line.strip():  # Ignorer les lignes vides
                    records.append(json.loads(line))
            df = pd.DataFrame(records)
            
            # Si c'est un format Airbyte, extraire les données réelles
            if '_airbyte_data' in df.columns:
                print("\n   🔍 Détection du format Airbyte - extraction des données...")
                # Extraire et parser la colonne _airbyte_data
                data_records = []
                for idx, row in df.iterrows():
                    airbyte_data = row['_airbyte_data']
                    if isinstance(airbyte_data, str):
                        airbyte_data = json.loads(airbyte_data)
                    
                    # Extraire les données météo si disponibles
                    if isinstance(airbyte_data, dict):
                        # Cas 1: Les données sont dans un tableau 'data'
                        if 'data' in airbyte_data and isinstance(airbyte_data['data'], list) and len(airbyte_data['data']) > 0:
                            for weather_record in airbyte_data['data']:
                                data_records.append(weather_record)
                        # Cas 2: Les données horaires sont dans 'hourly' (format API Infoclimat)
                        elif 'hourly' in airbyte_data and isinstance(airbyte_data['hourly'], dict):
                            hourly_data = airbyte_data['hourly']
                            # Pour chaque station dans hourly
                            for station_id, station_records in hourly_data.items():
                                if station_id != '_params' and isinstance(station_records, list):
                                    # Ajouter tous les enregistrements de cette station
                                    data_records.extend(station_records)
                        # Cas 3: Les données météo sont directement dans l'objet (pas de sous-clé 'data')
                        elif any(key in airbyte_data for key in ['Temperature', 'Humidity', 'Pressure', 'Time']):
                            data_records.append(airbyte_data)
                        # Cas 4: Objet vide ou autre structure
                        else:
                            data_records.append(airbyte_data)
                
                if data_records:
                    df = pd.DataFrame(data_records)
                    print(f"   ✅ {len(data_records)} enregistrements météo extraits")
                else:
                    print(f"   ⚠️  Aucune donnée météo trouvée dans ce fichier")
        else:
            print(f"⚠️  Type de fichier non supporté: .{file_extension}")
            return
        
        # Appliquer le nettoyage des données
        print("\n🧹 Application du nettoyage des données...")
        df = apply_data_cleaning(df)
        print("   ✅ Nettoyage terminé!")
        
        print(f"\n📊 Données chargées avec succès!")
        print(f"   Shape: {df.shape} (lignes, colonnes)")
        print(f"   Colonnes: {list(df.columns)}")
        print(f"   Mémoire utilisée: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        print(f"\n📈 Aperçu des données (5 premières lignes):")
        print(df.head())
        
        print(f"\n📉 Statistiques descriptives:")
        print(df.describe())
        
        print(f"\n🔍 Informations sur les colonnes:")
        print(df.info())
        
        # Lire tous les fichiers automatiquement
        if len(files) > 1:
            print(f"\n📚 Lecture de tous les {len(files)} fichiers...")
            if True:
                all_dataframes = []
                for file in files:
                    print(f"   📖 Lecture de {file['key']}...")
                    response = s3_client.get_object(Bucket=s3_bucket, Key=file['key'])
                    content = response['Body'].read().decode('utf-8')
                    
                    # Lire selon le type de fichier
                    if file_extension == 'csv':
                        df_temp = pd.read_csv(StringIO(content))
                    elif file_extension in ['json', 'jsonl']:
                        import json
                        records = []
                        for line in content.strip().split('\n'):
                            if line.strip():
                                records.append(json.loads(line))
                        df_temp = pd.DataFrame(records)
                        
                        # Extraire les données Airbyte si présentes
                        if '_airbyte_data' in df_temp.columns:
                            data_records = []
                            for idx, row in df_temp.iterrows():
                                airbyte_data = row['_airbyte_data']
                                if isinstance(airbyte_data, str):
                                    airbyte_data = json.loads(airbyte_data)
                                
                                if isinstance(airbyte_data, dict):
                                    # Cas 1: données dans 'data'
                                    if 'data' in airbyte_data and isinstance(airbyte_data['data'], list) and len(airbyte_data['data']) > 0:
                                        data_records.extend(airbyte_data['data'])
                                    # Cas 2: données horaires dans 'hourly'
                                    elif 'hourly' in airbyte_data and isinstance(airbyte_data['hourly'], dict):
                                        for station_id, station_records in airbyte_data['hourly'].items():
                                            if station_id != '_params' and isinstance(station_records, list):
                                                data_records.extend(station_records)
                                    # Cas 3: données directes
                                    elif any(key in airbyte_data for key in ['Temperature', 'Humidity', 'Pressure', 'Time']):
                                        data_records.append(airbyte_data)
                                    else:
                                        data_records.append(airbyte_data)
                                else:
                                    data_records.append({})
                            
                            if data_records:
                                df_temp = pd.DataFrame(data_records)
                    
                    all_dataframes.append(df_temp)
                
                # Concaténer tous les DataFrames
                combined_df = pd.concat(all_dataframes, ignore_index=True)
                
                # Appliquer le nettoyage sur le DataFrame combiné
                print("\n🧹 Application du nettoyage sur le DataFrame combiné...")
                combined_df = apply_data_cleaning(combined_df)
                print("   ✅ Nettoyage terminé!")
                
                # Préparer les données pour MongoDB
                print("\n🔧 Préparation des données pour MongoDB...")
                combined_df = prepare_for_mongodb(combined_df)
                print("   ✅ Données prêtes pour MongoDB!")
                
                print(f"\n✅ Tous les fichiers combinés!")
                print(f"   Shape finale: {combined_df.shape}")
                print(f"   Aperçu:")
                print(combined_df.head())
                
                # Sauvegarder automatiquement dans S3
                print(f"\n💾 Sauvegarde du résultat dans S3...")
                if True:
                    
                    # Récupérer le préfixe de destination
                    s3_prefix_dest = os.getenv("S3_PREFIX_DESTINATION", "02_cleaned/")
                    
                    # Générer le nom du fichier avec horodatage
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_weather_data.json"
                    s3_key = f"{s3_prefix_dest}{filename}"
                    
                    # Convertir le DataFrame en JSON (format MongoDB-ready)
                    json_data = combined_df.to_json(orient='records', date_format='iso', force_ascii=False)
                    
                    # Upload vers S3
                    print(f"\n📤 Upload vers S3: s3://{s3_bucket}/{s3_key}...")
                    s3_client.put_object(
                        Bucket=s3_bucket,
                        Key=s3_key,
                        Body=json_data.encode('utf-8'),
                        ContentType='application/json'
                    )
                    print(f"   ✅ Fichier sauvegardé dans S3: {filename}")
                    print(f"   📍 Chemin complet: s3://{s3_bucket}/{s3_key}")
                    print(f"   📋 Format: JSON compatible MongoDB (orient='records')")
        
    except NoCredentialsError:
        print("\n❌ Erreur: Credentials AWS non trouvés ou invalides")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print("\n❌ Erreur: Accès refusé - Vérifiez vos permissions IAM")
        elif error_code == '404':
            print(f"\n❌ Erreur: Bucket '{s3_bucket}' non trouvé")
        else:
            print(f"\n❌ Erreur AWS: {e}")
    except Exception as e:
        print(f"\n❌ Erreur lors de la lecture du bucket S3: {e}")
        print("\nAssurez-vous que:")
        print("  - Les credentials AWS sont corrects")
        print("  - Le bucket existe et est accessible")
        print("  - Les permissions IAM sont configurées correctement")

if __name__ == "__main__":
    main()
