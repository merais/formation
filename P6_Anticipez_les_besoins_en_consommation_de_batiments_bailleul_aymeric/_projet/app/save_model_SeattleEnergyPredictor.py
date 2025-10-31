# Script de sauvegarde du modèle Seattle Energy Predictor avec BentoML

import os
import sys
import pandas as pd
import numpy as np
import bentoml
from datetime import datetime

# Import Scikit-learn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Se placer dans le répertoire du script (garantit les chemins relatifs)
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Répertoire de travail: {os.getcwd()}")

# Chemin vers le fichier de données (modifiable selon votre structure)
DATA_PATH = "../sources/2016_Building_Energy_Benchmarking_03_encoded.csv"

# Nom du modèle BentoML
MODEL_NAME = "seattle_energy_predictor"

def print_section(title, char="=", width=100):
    # Affiche une section avec formatage
    print(f"\n{char * width}")
    print(f"{title}")
    print(f"{char * width}\n")

def clean_old_models(model_name=MODEL_NAME):
    # Nettoie les anciens modèles BentoML
    print_section("Nettoyage des anciens modèles...")
    
    try:
        # Lister tous les modèles existants avec le même nom
        existing_models = [m for m in bentoml.models.list() if m.tag.name == model_name]
        
        if existing_models:
            print(f"Trouvé {len(existing_models)} ancien modèle à supprimer:")
            for old_model in existing_models:
                try:
                    print(f"  Suppression: {old_model.tag}")
                    bentoml.models.delete(old_model.tag)
                    print(f"  Supprimé: {old_model.tag}")
                except Exception as e:
                    print(f"  Échec suppression {old_model.tag}: {str(e)}")
        else:
            print("Aucun ancien modèle à nettoyer")
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")
        return None

def load_and_prepare_data(data_path=DATA_PATH):
    # Charge et prépare les données d'entraînement
    print_section("Chargement des données...")
    
    # Vérifier l'existence du fichier
    if not os.path.exists(data_path):
        print(f"Fichier non trouvé: {data_path}")
        print("Veuillez vous assurer que les données sont disponibles dans le dossier sources/")
        sys.exit(1)
    
    # Charger les données
    data = pd.read_csv(data_path)
    print(f"Données chargées: {data.shape[0]} lignes, {data.shape[1]} colonnes")
    
    # Features et target
    features = [
        'PropertyGFATotal', 'NumberofFloors', 
        'Electricity(kWh)', 'NaturalGas(kWh)',
        'PrimaryPropertyType_Large Office', 'PrimaryPropertyType_Other',
        'PrimaryPropertyType_Retail Store', 'PrimaryPropertyType_Small- and Mid-Sized Office',
        'PrimaryPropertyType_Warehouse'
    ]
    
    target = 'SiteEnergyUse(kWh)'
    
    print_section("Préparation des données d'entraînement...")
    print(f"Features utilisées: {len(features)}")
    print(f"Target: {target}")
    
    # Vérification des colonnes disponibles
    available_features = [f for f in features if f in data.columns]
    missing_features = [f for f in features if f not in data.columns]
    
    if missing_features:
        print(f"Features manquantes: {missing_features}")
    
    print(f"Features disponibles: {len(available_features)}")
    for i, feature in enumerate(available_features, 1):
        print(f"  {i:2d}. {feature}")
    
    # Extraction des données
    X = data[available_features].copy()
    y = data[target].copy()
    
    print_section("Nettoyage des données...")
    print(f"Valeurs manquantes X: {X.isnull().sum().sum()}")
    print(f"Valeurs manquantes y: {y.isnull().sum()}")
    
    # Suppression des valeurs manquantes
    mask = ~(X.isnull().any(axis=1) | y.isnull())
    X_clean = X[mask]
    y_clean = y[mask]
    
    print(f"Données nettoyées: {len(X_clean)} échantillons")
    print(f"Forme finale X: {X_clean.shape}")
    print(f"Forme finale y: {y_clean.shape}")
    
    return X_clean, y_clean, available_features

def train_model(X, y):
    # Entraîne le modèle Linear Regression
    print_section("Division des données...")
    
    # Division des données
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Train set: {X_train.shape[0]} échantillons")
    print(f"Test set: {X_test.shape[0]} échantillons")
    
    print_section("Entraînement du modèle Linear Regression...")
    
    # Entraînement
    model = LinearRegression()
    model.fit(X_train, y_train)
    print("Modèle entraîné avec succès!")
    
    print_section("Évaluation du modèle...")
    
    # Prédictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calcul des métriques
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    mae_train = mean_absolute_error(y_train, y_pred_train)
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    # Affichage des résultats
    print(f"Performance sur Train:")
    print(f"   R² Score: {r2_train:.4f} ({r2_train*100:.2f}%)")
    print(f"   MAE: {mae_train:,.0f} kWh")
    print(f"   RMSE: {rmse_train:,.0f} kWh")
    
    print(f"\nPerformance sur Test:")
    print(f"   R² Score: {r2_test:.4f} ({r2_test*100:.2f}%)")  
    print(f"   MAE: {mae_test:,.0f} kWh")
    print(f"   RMSE: {rmse_test:,.0f} kWh")
    
    # Stockage des métriques
    model_metrics = {
        "algorithm": "Linear Regression",
        "r2_train": float(r2_train),
        "r2_test": float(r2_test),
        "mae_train": float(mae_train),
        "mae_test": float(mae_test),
        "rmse_train": float(rmse_train),
        "rmse_test": float(rmse_test),
        "n_features": len(X.columns),
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test)
    }
    
    return model, model_metrics, X_test, y_test

def save_model_with_bentoml(model, model_metrics, available_features, X_test, target):
    # Sauvegarde le modèle avec BentoML
    print_section("Sauvegarde du modèle avec BentoML...")
    
    # Préparation des métadonnées
    metadata = {
        "project": "P6_Seattle_Energy_Prediction",
        "algorithm": "Linear Regression",
        "performance": {
            "r2_score": f"{model_metrics['r2_test']:.4f} ({model_metrics['r2_test']*100:.2f}%)",
            "mae_test": f"{model_metrics['mae_test']:,.0f} kWh",
            "rmse_test": f"{model_metrics['rmse_test']:,.0f} kWh"
        },
        "features": available_features,
        "target": target,
        "training_date": datetime.now().isoformat(),
        "model_version": "v1.0.0",
        "author": "ABAI_P6",
        "description": "Modèle Linear Regression pour prédiction énergétique bâtiments Seattle"
    }
    
    # Labels pour identification
    labels = {
        "project": "seattle_energy_prediction",
        "algorithm": "linear_regression", 
        "version": "1.0.0",
        "stage": "production",
        "framework": "scikit-learn"
    }
    
    # Sauvegarde avec BentoML
    bentoml_model = bentoml.sklearn.save_model(
        name="seattle_energy_predictor",
        model=model,
        labels=labels,
        metadata=metadata,
        custom_objects={
            "feature_names": available_features,
            "model_metrics": model_metrics,
            "sample_input": X_test.iloc[0].to_dict()
        }
    )
    
    print(f"Modèle sauvegardé avec succès!")
    print(f"Tag BentoML: {bentoml_model.tag}")
    print(f"Path: {bentoml_model.path}")
    print(f"Labels: {bentoml_model.info.labels}")
    
    return bentoml_model

def verify_saved_model(bentoml_model):
    # Vérifie le modèle sauvegardé
    print_section("Vérification du modèle sauvegardé...")
    
    try:
        # Vérification basique du modèle
        print(f"Vérification du modèle: {bentoml_model.tag}")
        loaded_model = bentoml.models.get(bentoml_model.tag)
        print("Modèle accessible dans le store BentoML!")
        
        print(f"Labels: {loaded_model.info.labels}")
        print(f"Créé le: {loaded_model.info.creation_time}")
        
        # Test de chargement du modèle ML
        ml_model = loaded_model.load_model()
        print(f"Modèle ML chargé: {type(ml_model).__name__}")
        
        print("\nLe modèle est correctement sauvegardé et accessible!")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la vérification: {str(e)}")
        return False

def main(data_path=DATA_PATH):
    # Fonction principale
    print_section("SAUVEGARDE MODÈLE SEATTLE ENERGY PREDICTOR", "=", 120)
    
    try:
        # 1. Nettoyage des anciens modèles
        clean_old_models()
        
        # 2. Chargement et préparation des données
        X, y, available_features = load_and_prepare_data(data_path)
        
        # 3. Entraînement du modèle
        model, model_metrics, X_test, y_test = train_model(X, y)
        
        # 4. Sauvegarde avec BentoML
        bentoml_model = save_model_with_bentoml(
            model, model_metrics, available_features, X_test, 'SiteEnergyUse(kWh)'
        )
        
        # 5. Vérification
        success = verify_saved_model(bentoml_model)
        
        if success:
            print_section("SAUVEGARDE TERMINÉE AVEC SUCCÈS!", "=", 120)
        else:
            print_section("ÉCHEC DE LA SAUVEGARDE", "=", 120)
            sys.exit(1)
            
    except Exception as e:
        print_section("ERREUR CRITIQUE", "=", 120)
        print(f"Erreur: {str(e)}")
        print("Veuillez vérifier les données et réessayer.")
        sys.exit(1)

if __name__ == "__main__":
    main(DATA_PATH)