# Script de création des utilisateurs MongoDB avec rôles depuis la configuration .env

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, DuplicateKeyError


def load_env_variables():
    """Charger les variables d'environnement depuis le fichier .env"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\tErreur: fichier .env introuvable!")
        print("\tVeuillez créer un fichier .env avec les credentials MongoDB.")
        sys.exit(1)
    
    load_dotenv()
    
    # Vérifier les variables requises
    required_vars = [
        "MONGO_INITDB_ROOT_USERNAME",
        "MONGO_INITDB_ROOT_PASSWORD",
        "MONGO_APP_USERNAME",
        "MONGO_APP_PASSWORD",
        "MONGO_READONLY_USERNAME",
        "MONGO_READONLY_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\tErreur: Variables d'environnement manquantes: {', '.join(missing_vars)}")
        sys.exit(1)
    
    return {
        "admin_user": os.getenv("MONGO_INITDB_ROOT_USERNAME"),
        "admin_pwd": os.getenv("MONGO_INITDB_ROOT_PASSWORD"),
        "app_user": os.getenv("MONGO_APP_USERNAME"),
        "app_pwd": os.getenv("MONGO_APP_PASSWORD"),
        "readonly_user": os.getenv("MONGO_READONLY_USERNAME"),
        "readonly_pwd": os.getenv("MONGO_READONLY_PASSWORD")
    }


def create_user(db, username, password, role):
    """Créer un utilisateur MongoDB avec le rôle spécifié"""
    try:
        db.command(
            "createUser",
            username,
            pwd=password,
            roles=[{"role": role, "db": "healthcare_db"}]
        )
        print(f"\t{username} créé avec succès (permissions {role})")
        return True
    except OperationFailure as e:
        if "already exists" in str(e) or e.code == 51003:
            print(f"\t{username} existe déjà")
            return True
        else:
            print(f"\tErreur lors de la création de {username}: {e}")
            return False
    except Exception as e:
        print(f"\tErreur inattendue lors de la création de {username}: {e}")
        return False


def create_users(credentials):
    """Créer les utilisateurs MongoDB avec les rôles appropriés via PyMongo"""
    print("\tCréation des utilisateurs MongoDB...")
    
    # Essayer de se connecter à MongoDB (fonctionne si exécuté dans Docker ou si MongoDB est accessible)
    mongo_hosts = [
        "mongodb",  # Nom du réseau Docker
        "localhost",  # Exécution locale
        "127.0.0.1"  # Alternative locale
    ]
    
    client = None
    connection_host = None
    
    for host in mongo_hosts:
        try:
            print(f"\tTentative de connexion à {host}...")
            mongo_uri = f"mongodb://{credentials['admin_user']}:{credentials['admin_pwd']}@{host}:27017/?authSource=admin"
            test_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            
            # Tester la connexion
            test_client.admin.command('ping')
            print(f"\tConnecté à MongoDB sur {host}")
            client = test_client
            connection_host = host
            break
        except Exception as e:
            print(f"\tÉchec de connexion à {host}: {type(e).__name__}")
            continue
    
    if not client:
        print(f"\tImpossible de se connecter à MongoDB sur aucun hôte")
        return False
    
    try:
        # Obtenir la base de données healthcare_db
        db = client.healthcare_db
        
        # Créer app_user (readWrite)
        success_app = create_user(
            db, 
            credentials['app_user'], 
            credentials['app_pwd'], 
            'readWrite'
        )
        
        # Créer readonly_user (read)
        success_readonly = create_user(
            db, 
            credentials['readonly_user'], 
            credentials['readonly_pwd'], 
            'read'
        )
        
        client.close()
        return success_app and success_readonly
        
    except Exception as e:
        print(f"\tErreur lors de la création des utilisateurs: {e}")
        if client:
            client.close()
        return False


def verify_users(credentials):
    """Vérifier que les utilisateurs ont été créés avec succès via PyMongo"""
    print("\n\tVérification des utilisateurs...")
    
    # Essayer plusieurs hôtes
    mongo_hosts = ["mongodb", "localhost", "127.0.0.1"]
    client = None
    
    for host in mongo_hosts:
        try:
            mongo_uri = f"mongodb://{credentials['admin_user']}:{credentials['admin_pwd']}@{host}:27017/?authSource=admin"
            test_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            test_client.admin.command('ping')
            client = test_client
            break
        except:
            continue
    
    if not client:
        print("\tImpossible de se connecter à MongoDB pour la vérification")
        return False
    
    try:
        
        # Obtenir les utilisateurs de healthcare_db
        db = client.healthcare_db
        users_info = db.command("usersInfo")
        
        if users_info and 'users' in users_info:
            users = users_info['users']
            
            if len(users) == 0:
                print("\tAucun utilisateur trouvé dans healthcare_db")
                client.close()
                return False

            print(f"\tTrouvé {len(users)} utilisateur(s) dans healthcare_db:")

            app_user_found = False
            readonly_user_found = False
            
            for user in users:
                username = user['user']
                roles = [role['role'] for role in user['roles']]
                print(f"\t- {username}: {', '.join(roles)}")
                
                if username == credentials['app_user']:
                    app_user_found = True
                if username == credentials['readonly_user']:
                    readonly_user_found = True
            
            client.close()
            
            if app_user_found and readonly_user_found:
                print("\n\tTous les utilisateurs vérifiés avec succès!")
                return True
            else:
                print("\n\tAttention: Certains utilisateurs sont manquants")
                return False
        else:
            print("\tImpossible de récupérer les informations utilisateurs")
            client.close()
            return False
            
    except Exception as e:
        print(f"\tErreur de vérification: {e}")
        return False


def main():
    """Fonction principale"""
    print("=" * 60)
    print("Script de Création des Utilisateurs MongoDB")
    print("=" * 60)
    
    # Charger les credentials depuis .env
    credentials = load_env_variables()
    
    # Créer les utilisateurs
    if create_users(credentials):
        # Vérifier les utilisateurs
        verify_users(credentials)
        print("\n" + "=" * 60)
        print("\tCréation des utilisateurs terminée!")
        print("=" * 60)
    else:
        print("\n\tÉchec de la création des utilisateurs")
        sys.exit(1)


if __name__ == "__main__":
    main()
