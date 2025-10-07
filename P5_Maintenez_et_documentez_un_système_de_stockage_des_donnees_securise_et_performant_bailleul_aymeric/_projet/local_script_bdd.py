# Script de création de la base de données MongoDB et d'importation des données depuis un fichier CSV.
# Importer les bibliothèques nécessaires a l'utilisation de mongodb
import os
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# On place le terminal au bon endroit
os.chdir("G:\\Mon Drive\\_formation_over_git\\P5_Maintenez_et_documentez_un_système_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric\\_projet")

# Variables globales (locales)
DB_NAME = "healthcare_db"
URI = "mongodb://localhost:27017/"
COLLECTION_NAME = "patients"
SOURCE_CSV = "./sources/healthcare_dataset.csv"

# Fonction de connexion a la base de données
def connect_to_mongodb(uri, db_name):
    try:
        # Créer une instance de MongoClient
        client = MongoClient(uri)
        
        # Vérifier la connexion
        client.admin.command('ping')
        print("Connexion à MongoDB réussie")
        
        # Accéder à la base de données spécifiée
        db = client[db_name]
        return db
    except ConnectionFailure as e:
        print(f"Échec de la connexion à MongoDB: {e}")
        return None

# Fonction d'importation de données depuis un fichier csv
def import_data_from_csv(db, collection_name, file_path):

    # Lire les données depuis le fichier CSV
    try:
        data = pd.read_csv(file_path)
        print(f"Import : Données lues depuis {file_path}")
    except Exception as e:
        print(f"Import : Erreur lors de la lecture du fichier {file_path}: {e}")
        return
    
    # Convertir les données en dictionnaire
    data_dict = data.to_dict(orient='records')
    
    # Insérer les données dans la collection MongoDB
    try:
        collection = db[collection_name]
        collection.insert_many(data_dict)
        print(f"Import : {len(data_dict)} documents insérés dans la collection '{collection_name}'\n")
    except Exception as e:
        print(f"Import : Erreur lors de l'insertion des données dans la collection '{collection_name}': {e}\n")

# Fonction de nettoyage des données avant importation
def clean_data(data):
    # On affiche le nombre de lignes et de colonnes
    print(f"Le fichier contient {data.shape[0]} lignes et {data.shape[1]} colonnes avant le nettoyage.")

    # Conversion des dates pour une typologie correcte
    data['Date of Admission'] = pd.to_datetime(data['Date of Admission'])
    data['Discharge Date'] = pd.to_datetime(data['Discharge Date'])
    print("1- Champs 'Date of Admission' et 'Discharge Date' convertis en type datetime.")

    # On modifie le champ name pour que les majuscules soient au début de chaque mot
    data['Name'] = data['Name'].str.lower() # On met tout en minuscule
    data['Name'] = data['Name'].str.title() # On met une majuscule au début de chaque mot
    print("2- Champ 'Name' modifié pour que les majuscules soient au début de chaque mot.")

    # Valeurs manquantes
    if data.isnull().sum().sum() == 0: 
        print("3- Aucune valeur manquante détectée (NaN).")
    else:
        print("3- Des valeurs manquantes ont été détectées.")

    # Doublons
    duplicate_count = data.duplicated().sum()
    print(f"4- Doublons (Lignes Complètement Identiques) : {duplicate_count}")
    if duplicate_count > 0:
        print("   -> Les doublons vont être supprimés.")
        data_cleaned = data.drop_duplicates()
    else:
        print("4- Aucun doublon détecté.")
        data_cleaned = data
    
    return data_cleaned

# Fonction de vérification des données avant importation
def verify_data(df):
    # On lit le fichier CSV
    data = pd.read_csv(df)

    # On nettoie les données
    cleaned_df = clean_data(data)

    # On définit le chemin de sortie du fichier nettoyé en récupérant le nom du fichier d'entrée pour le placer correctement
    output_path = df.replace('.csv', '_cleaned.csv')

    # On ajoute a chaque document un champ identifiant unique
    if 'id_patient' not in cleaned_df.columns:
        cleaned_df.insert(0, 'id_patient', range(1, len(cleaned_df) + 1))
        print("5- Le champ 'id_patient' a été ajouté comme identifiant unique pour chaque document.")

    # On écrit le fichier CSV nettoyé
    cleaned_df.to_csv(output_path, index=False)

    return output_path

# Main
if __name__ == "__main__":
    # Connexion à la base de données
    try:
        db = connect_to_mongodb(URI, DB_NAME)
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        db = None

    # # Création d'une collection et importation de données depuis un fichier CSV si la collection n'existe pas déjà
    if db != None:
        if COLLECTION_NAME in db.list_collection_names():
            print(f"La collection '{COLLECTION_NAME}' existe déjà.")
            collection = db[COLLECTION_NAME]
            print(f"La collection '{COLLECTION_NAME}' existe déjà le nettoyage va être relancé.") # Afficher le nombre de documents dans la collection

            # On transforme la collection en DataFrame pandas pour relancer le nettoyage des données
            data = pd.DataFrame(list(collection.find()))
            # On relance le nettoyage des données du fichier CSV même si la collection existe déjà
            data_already_cleaned = clean_data(data)
            print(f"Il y a {data_already_cleaned.shape[0]} documents dans la collection déjà existante.\n")
        else:
            print(f"La collection '{COLLECTION_NAME}' n'existe pas et va donc être créée.")
            import_data_from_csv(db, COLLECTION_NAME, verify_data(SOURCE_CSV))
    else:
        print("La base de données n'est pas disponible.")