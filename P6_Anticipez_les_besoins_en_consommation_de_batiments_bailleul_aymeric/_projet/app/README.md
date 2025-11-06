# Seattle Energy Prediction API - BentoML

## Description

API de prédiction de consommation énergétique pour les bâtiments de Seattle basée sur un **Random Forest Regressor** (pipeline sans fuite). Le service attend une entrée minimale et reconstruit les features complètes attendues par le modèle.

## Utilisation

### 1. Sauvegarder le modèle

Exécutez le script `save_model_SeattleEnergyPredictor.py` pour entraîner et sauvegarder le modèle BentoML :

```bash
# Dans le dossier app/
python save_model_SeattleEnergyPredictor.py
```

Ce script :
- Se place dans le bon répertoire de travail
- Charge X/y depuis `../sources/2016_Building_Energy_Benchmarking_03X_building_consumption.csv` et `../sources/2016_Building_Energy_Benchmarking_03y_building_consumption.csv`
- Applique une regex anti-fuite (exclut toute colonne liée à consommation/énergie)
- Entraîne un RandomForest avec des hyperparamètres fournis
- Sauvegarde le modèle dans BentoML avec métadonnées et objets personnalisés (`feature_names`, `sample_input`)
- Vérifie la sauvegarde

### 2. Démarrer le service

```bash
# Dans le dossier app/
bentoml serve service.py:SeattleEnergyPredictor --port 3000

# Windows (PowerShell) – chemin absolu
cd "g:\Mon Drive\_formation_over_git\P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric\_projet\app" ; bentoml serve service.py:SeattleEnergyPredictor --port 3000
```

### 3. Tester l'API

L'API sera disponible sur `http://localhost:3000`

## Interface Swagger UI Interactive

BentoML génère automatiquement une **interface Swagger UI** complète et interactive :

### Accéder à l'interface
```
http://localhost:3000
```

### Fonctionnalités de l'interface Swagger
- **Documentation interactive** : Descriptions détaillées des endpoints
- **Exemples prêts à l'emploi** : Données de test pré-remplies
- **Test en direct** : Bouton "Try it out" pour chaque endpoint
- **Validation automatique** : Vérification des types et contraintes
- **Réponses formatées** : Résultats JSON bien structurés

### Endpoints disponibles dans Swagger
1. **`POST /predict_single`** – Prédiction (entrée minimale et sans fuite)
2. **`POST /predict_batch`** – Prédictions multiples (entrée minimale)
3. **`POST /validate_data`** – Validation seule sans prédiction
4. **`GET /get_feature_info`** – Documentation dynamique (features, types, exemples)
5. **`GET /get_group_map`** – Mapping PrimaryPropertyType → Building_Group
6. **`GET /health`** – Statut du service

### Comment utiliser Swagger UI
1. Ouvrez `http://localhost:3000` dans votre navigateur
2. Cliquez sur un endpoint pour l'expandre
3. Cliquez sur **"Try it out"**
4. Modifiez les données d'exemple si nécessaire
5. Cliquez sur **"Execute"**
6. Consultez la réponse dans la section "Response"

**Endpoints disponibles :**

#### `/predict_single` – Prédiction
```bash
# curl
curl -X POST "http://localhost:3000/predict_single" \
     -H "Content-Type: application/json" \
     -d '{
       "PropertyGFATotal": 50000,
       "NumberofFloors": 5,
       "PrimaryPropertyType": "Large Office",
       "YearBuilt": 1995
     }'

# PowerShell (Windows)
$body = @{
  PropertyGFATotal = 50000
  NumberofFloors = 5
  PrimaryPropertyType = "Large Office"
  YearBuilt = 1995
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:3000/predict_single" -Method Post -ContentType "application/json" -Body $body
```

#### `/predict_batch` – Prédictions multiples
```bash
curl -X POST "http://localhost:3000/predict_batch" \
     -H "Content-Type: application/json" \
     -d '[
       {"PropertyGFATotal": 30000, "NumberofFloors": 3, "PrimaryPropertyType": "Other", "YearBuilt": 1980},
       {"PropertyGFATotal": 75000, "NumberofFloors": 8, "PrimaryPropertyType": "Large Office", "YearBuilt": 2005}
     ]'
```

#### `/get_feature_info` – Informations dynamiques
```bash
curl "http://localhost:3000/get_feature_info"
# Retourne: algorithm, features_count, allowed_primary_property_types, example_payloads_by_type, primary_type_to_group_map, etc.
```

#### `/get_group_map` – Mapping PrimaryPropertyType → Building_Group
```bash
curl "http://localhost:3000/get_group_map"
# Retourne: group_map, allowed_primary_property_types, building_group_columns
```

#### `/validate_data` – Validation seule
```bash
curl -X POST "http://localhost:3000/validate_data" \
     -H "Content-Type: application/json" \
     -d '{
       "PropertyGFATotal": 25000,
       "NumberofFloors": 2,
       "PrimaryPropertyType": "Retail Store"
     }'
```

## Déploiement Docker

### 1. Construire le Bento
```bash
# Dans le dossier app/ (celui du bentofile.yaml)
bentoml build
```

### 2. Containeriser avec le tag exact
```bash
# Utilisez le tag généré lors du build (exemple)
# Le tag change à chaque build - utilisez celui affiché après 'bentoml build'
bentoml containerize seattle-energy-predictor:rgz23h5256v64pak
```

### 3. Lancer le container
```bash
# Utilisez le même tag que pour la containerisation
docker run --rm -p 3000:3000 seattle-energy-predictor:rgz23h5256v64pak
```

### 4. Accéder au service containerisé
- **API** : `http://localhost:3000`

## Publier l'image sur Docker Hub (mainteneur)

Vous pouvez publier l'image construite localement sur Docker Hub pour la partager.

Pré-requis: avoir construit et containerisé le Bento localement (image `seattle-energy-predictor:rgz23h5256v64pak`).

### Étapes (PowerShell)

```powershell
# 1) Connexion (si nécessaire)
docker login

# 2) Taguer l'image locale avec votre dépôt Docker Hub
docker tag seattle-energy-predictor:rgz23h5256v64pak merais/seattle-energy-predictor:rgz23h5256v64pak
docker tag seattle-energy-predictor:rgz23h5256v64pak merais/seattle-energy-predictor:latest

# 3) Pousser les tags vers Docker Hub
docker push merais/seattle-energy-predictor:rgz23h5256v64pak
docker push merais/seattle-energy-predictor:latest
```

Notes:
- Remplacez `merais` par votre propre namespace Docker Hub si vous forkiez le projet.
- Le tag long (`rgz23h5256v64pak`) est immuable et permet la reproductibilité; `latest` pointe vers la version actuelle.

## Utiliser l'image depuis Docker Hub

Vous pouvez directement récupérer l'image déjà publiée sur Docker Hub et l'exécuter localement.

### Récupérer l'image
```powershell
# Dernière version (latest)
docker pull merais/seattle-energy-predictor:latest

# Version figée (reproductible)
docker pull merais/seattle-energy-predictor:rgz23h5256v64pak
```

### Lancer l'image
```powershell
# Port mapping 3000:3000 (BentoML écoute sur 3000)
docker run --rm -p 3000:3000 merais/seattle-energy-predictor:latest

# Ou avec le tag spécifique
docker run --rm -p 3000:3000 merais/seattle-energy-predictor:rgz23h5256v64pak
```

### URL pour Google Cloud > Cloud Run 

docker.io/merais/seattle-energy-predictor:rgz23h5256v64pak

### Accéder à l'API
- **Swagger UI / API** : `http://localhost:3000`

Note:
- Si le dépôt Docker Hub est privé, connectez-vous avant le pull: `docker login`
- Les tags changent à chaque build automatisé; utilisez toujours le tag affiché après `bentoml build` pour rester cohérent.