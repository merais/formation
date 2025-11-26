"""
Script de connexion et requêtes MongoDB avec Python
Projet P7 - Analyse base de données NoSQL
Auteur: Aymeric Bailleul
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import polars as pl
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Charger les variables d'environnement (optionnel)
load_dotenv()


class MongoDBConnection:
    """Classe pour gérer la connexion à MongoDB"""
    
    def __init__(self, connection_string: Optional[str] = None, 
                 host: str = "localhost", 
                 port: int = 27001):
        """
        Initialise la connexion MongoDB
        """
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = f"mongodb://{host}:{port}/"
        
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Établit la connexion à la base de données
        """
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            # Test de la connexion
            self.client.admin.command('ping')
            self.db = self.client[database_name]
            print(f"\tConnexion réussie à la base de données '{database_name}'")
            return True
        except ConnectionFailure as e:
            print(f"\tÉchec de connexion à MongoDB: {e}")
            return False
        except Exception as e:
            print(f"\tErreur inattendue: {e}")
            return False
    
    def close(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            print("\tConnexion fermée")

def query_to_polars(collection, query: Dict = {}, projection: Dict = None, 
                    limit: int = 0) -> pl.DataFrame:
    """
    Exécute une requête MongoDB et retourne un DataFrame Polars
    """
    cursor = collection.find(query, projection)
    if limit > 0:
        cursor = cursor.limit(limit)
    
    data = list(cursor)
    
    if not data:
        return pl.DataFrame()
    
    return pl.DataFrame(data)

def aggregate_to_polars(collection, pipeline: List[Dict]) -> pl.DataFrame:
    """
    Exécute une agrégation MongoDB et retourne un DataFrame Polars
    """
    result = list(collection.aggregate(pipeline))
    
    if not result:
        return pl.DataFrame()
    
    return pl.DataFrame(result)

def calculer_taux_reservation_moyen_par_type_polars(collection) -> pl.DataFrame:
    """
    Calcule le taux de réservation moyen par mois et par type de logement
    Version Polars : utilise Polars pour les calculs au lieu de l'agrégation MongoDB
    Mode lazy pour optimiser les performances
    """
    # Récupérer les données brutes depuis MongoDB
    query = {
        "availability_365": {"$exists": True, "$ne": None},
        "room_type": {"$exists": True, "$ne": None}
    }
    projection = {"room_type": 1, "availability_365": 1, "_id": 0}
    
    df_logements = query_to_polars(collection, query=query, projection=projection)
    
    if df_logements.is_empty():
        return pl.DataFrame()
    
    # Effectuer les calculs avec Polars en mode lazy
    df_taux_par_type = (
        df_logements.lazy()
        .group_by("room_type")
        .agg(pl.col("availability_365").mean().alias("disponibilite_moyenne"))
        .with_columns([
            (
                ((365 - pl.col("disponibilite_moyenne")) / 365 * 100) / 12
            ).round(2).alias("taux_reservation_mensuel_moyen")
        ])
        .select(["room_type", "taux_reservation_mensuel_moyen"])
        .sort("taux_reservation_mensuel_moyen", descending=True)
        .collect()
    )
    
    return df_taux_par_type

def calculer_médiane_nombre_avis_all_logements_polars(collection) -> pl.DataFrame:
    """
    Calcule la médiane des nombre d'avis pour tous les logements
    Version Polars : utilise Polars pour les calculs au lieu de l'agrégation MongoDB
    Mode lazy pour optimiser les performances
    """
    # Récupérer les données brutes depuis MongoDB
    query = {"number_of_reviews": {"$exists": True, "$ne": None}}
    projection = {"number_of_reviews": 1, "_id": 0}
    
    df_avis = query_to_polars(collection, query=query, projection=projection)
    
    if df_avis.is_empty():
        return pl.DataFrame()
    
    # Calculer la médiane avec Polars en mode lazy
    df_mediane = (
        df_avis.lazy()
        .select(pl.col("number_of_reviews").median().alias("mediane_nombre_avis"))
        .collect()
    )
    
    return df_mediane

def calculer_médiane_nombre_avis_categorie_hote_polars(collection) -> pl.DataFrame:
    """
    Calcule la médiane des nombre d'avis par catégorie d'hôte
    Version Polars : utilise Polars pour les calculs au lieu de l'agrégation MongoDB
    Mode lazy pour optimiser les performances
    """
    # Récupérer les données brutes depuis MongoDB
    query = {
        "number_of_reviews": {"$exists": True, "$ne": None},
        "host_is_superhost": {"$exists": True, "$ne": None}
    }
    projection = {"number_of_reviews": 1, "host_is_superhost": 1, "_id": 0}
    
    df_avis_hotes = query_to_polars(collection, query=query, projection=projection)
    
    if df_avis_hotes.is_empty():
        return pl.DataFrame()
    
    # Calculer la médiane par catégorie avec Polars en mode lazy
    df_mediane_par_categorie = (
        df_avis_hotes.lazy()
        .group_by("host_is_superhost")
        .agg(pl.col("number_of_reviews").median().alias("mediane_nombre_avis"))
        .sort("host_is_superhost")
        .collect()
    )
    
    return df_mediane_par_categorie

def calculer_densite_logements_par_quartier(collection) -> pl.DataFrame:
    """
    Calcule la densité de logements par arrondissement de Paris
    Utilise les 20 arrondissements officiels de Paris avec leurs surfaces réelles
    """
    # Surface approximative en km² de chaque arrondissement de Paris
    arrondissements_surface = {
        "Louvre": 1.83,
        "Bourse": 0.99,
        "Temple": 1.17,
        "Hôtel-de-Ville": 1.60,
        "Panthéon": 2.54,
        "Luxembourg": 2.15,
        "Palais-Bourbon": 4.09,
        "Élysée": 3.88,
        "Opéra": 2.18,
        "Entrepôt": 2.89,
        "Popincourt": 3.67,
        "Reuilly": 6.38,
        "Gobelins": 7.15,
        "Observatoire": 5.64,
        "Vaugirard": 8.50,
        "Passy": 7.91,
        "Batignolles-Monceau": 5.67,
        "Buttes-Montmartre": 6.01,
        "Buttes-Chaumont": 6.79,
        "Ménilmontant": 5.98
    }
    
    pipeline = [
        {
            "$match": {
                "neighbourhood_cleansed": {"$exists": True, "$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$neighbourhood_cleansed",
                "nombre_logements": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "arrondissement": "$_id",
                "nombre_logements": 1
            }
        }
    ]
    
    # Récupérer les données depuis MongoDB
    df_quartiers_brut = aggregate_to_polars(collection, pipeline)
    
    if df_quartiers_brut.is_empty():
        return df_quartiers_brut
    
    # Effectuer les transformations en mode lazy
    df_quartiers_densite = (
        df_quartiers_brut.lazy()
        # Ajouter les surfaces avec un mapping explicite
        .with_columns([
            pl.col("arrondissement").replace_strict(arrondissements_surface, default=None, return_dtype=pl.Float64).alias("surface_km2")
        ])
        # Calculer la densité
        .with_columns([
            (pl.col("nombre_logements") / pl.col("surface_km2")).round(2).alias("densite_logements_par_km2")
        ])
        # Sélectionner et trier
        .select([
            "arrondissement",
            "nombre_logements",
            "surface_km2",
            "densite_logements_par_km2"
        ])
        .sort("densite_logements_par_km2", descending=True)
        .collect()
    )
    
    return df_quartiers_densite

def identifier_quartiers_plus_fort_taux_reservation_par_mois(collection) -> pl.DataFrame:
    """
    Identifie les quartiers avec le plus fort taux de réservation par mois
    """
    pipeline = [
        {
            "$match": {
                "availability_365": {"$exists": True, "$ne": None},
                "neighbourhood_cleansed": {"$exists": True, "$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$neighbourhood_cleansed",
                "disponibilite_moyenne": {"$avg": "$availability_365"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "quartier": "$_id",
                "taux_reservation_mensuel_moyen": {
                    "$round": [
                        {"$divide": [
                            {"$multiply": [
                                {"$divide": [
                                    {"$subtract": [365, "$disponibilite_moyenne"]},
                                    365
                                ]},
                                100
                            ]},
                            12
                        ]},
                        2
                    ]
                }
            }
        },
        {
            "$sort": {"taux_reservation_mensuel_moyen": -1}
        }
    ]
    
    return aggregate_to_polars(collection, pipeline)

# ============================================================================
# APPEL DE LA MAIN FONCTION > Début 
# ============================================================================

if __name__ == "__main__":
    
    # Configuration de la connexion
    mongo = MongoDBConnection(host="localhost", port=27001)

    # Connexion à la base de données
    if mongo.connect("listings"):  
        print("\tConnexion établie --> Les requêtes peuvent commencer.")
        
        # Récupérer la collection
        collection = mongo.db["short_location"]  # Remplacer "paris" par le nom de votre collection
        if collection is None:
            print("\tLa collection n'existe pas dans la base de données.")
            mongo.close()
            exit(1)
        else:
            print(f"\tLa collection '{collection.name}' est chargée avec succès.")
        
        # Taux de réservation moyen par type de logement
        print("\n" + "="*100)
        print("TAUX DE RÉSERVATION MOYEN PAR TYPE DE LOGEMENT")
        print("="*100)
        df_taux = calculer_taux_reservation_moyen_par_type_polars(collection)
        print(df_taux)

        # Médiane des nombre d’avis pour tous les logements
        print("\n" + "="*100)
        print("MÉDIANE DES NOMBRE D’AVIS POUR TOUS LES LOGEMENTS")
        print("="*100)
        df_mediane_all_logement = calculer_médiane_nombre_avis_all_logements_polars(collection)
        print(df_mediane_all_logement)

        # Médiane des nombres d’avis par catégorie d’hôte
        print("\n" + "="*100)
        print("MÉDIANE DES NOMBRE D’AVIS PAR CATÉGORIE D’HÔTE")
        print("="*100)
        df_mediane_categorie_hote = calculer_médiane_nombre_avis_categorie_hote_polars(collection)
        print(df_mediane_categorie_hote)

        # Densité de logements par quartier de Paris
        print("\n" + "="*100)
        print("DENSITÉ DE LOGEMENTS PAR QUARTIER DE PARIS")
        print("="*100)
        df_densite_quartier = calculer_densite_logements_par_quartier(collection)
        # Configurer Polars pour afficher toutes les lignes
        with pl.Config(tbl_rows=-1):
            print(df_densite_quartier)

        # Identifier les quartiers avec le plus fort taux de réservation par mois
        print("\n" + "="*100)
        print("IDENTIFIER LES QUARTIERS AVEC LE PLUS FORT TAUX DE RÉSERVATION PAR MOIS")
        print("="*100)
        df_resa_par_quartier_par_mois = identifier_quartiers_plus_fort_taux_reservation_par_mois(collection)
        with pl.Config(tbl_rows=-1):
            print(df_resa_par_quartier_par_mois)

        # Fermer la connexion
        mongo.close()
    else:
        print("Impossible de se connecter à MongoDB")
