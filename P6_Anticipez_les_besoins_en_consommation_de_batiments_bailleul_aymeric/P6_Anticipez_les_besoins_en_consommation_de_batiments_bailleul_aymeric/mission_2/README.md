# Seattle Energy Prediction API - BentoML

## Description

API de prédiction de consommation énergétique pour les bâtiments de Seattle basée sur le **modèle Linear Regression** gagnant du projet P6.

## Utilisation

### 1. Sauvegarder le modèle

Exécutez d'abord le script `save_model_SeattleEnergyPredictor.py` pour entraîner et sauvegarder le modèle BentoML :

```bash
# Dans le dossier app/
python save_model_SeattleEnergyPredictor.py
```

Le script va automatiquement :
- Se placer dans le bon répertoire de travail
- Charger les données depuis `../sources/2016_Building_Energy_Benchmarking_03_encoded.csv`
- Entraîner le modèle Linear Regression
- Sauvegarder le modèle dans BentoML avec les métadonnées
- Vérifier que la sauvegarde est réussie

### 2. Démarrer le service

```bash
# Dans le dossier app/
bentoml serve service.py:SeattleEnergyPredictor --port 3000

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
1. **`POST /predict_single`** - Prédiction pour un bâtiment
2. **`POST /predict_batch`** - Prédictions multiples
3. **`POST /validate_data`** - Validation seule sans prédiction
4. **`GET /get_feature_info`** - Documentation des features
5. **`GET /health`** - Statut du service

### Comment utiliser Swagger UI
1. Ouvrez `http://localhost:3000` dans votre navigateur
2. Cliquez sur un endpoint pour l'expandre
3. Cliquez sur **"Try it out"**
4. Modifiez les données d'exemple si nécessaire
5. Cliquez sur **"Execute"**
6. Consultez la réponse dans la section "Response"

**Endpoints disponibles :**

#### `/predict_single` - Prédiction pour un bâtiment
```bash
# Avec curl (ajustez le port selon votre configuration)
curl -X POST "http://localhost:3000/predict_single" \
     -H "Content-Type: application/json" \
     -d '{
       "PropertyGFATotal": 50000,
       "NumberofFloors": 5,
       "Electricity_kWh": 800000,
       "NaturalGas_kWh": 200000,
       "PrimaryPropertyType_Large_Office": 1,
       "PrimaryPropertyType_Other": 0,
       "PrimaryPropertyType_Retail_Store": 0,
       "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
       "PrimaryPropertyType_Warehouse": 0
     }'

# Avec PowerShell (Windows)
$body = @{
    PropertyGFATotal = 50000
    NumberofFloors = 5
    Electricity_kWh = 800000
    NaturalGas_kWh = 200000
    PrimaryPropertyType_Large_Office = 1
    PrimaryPropertyType_Other = 0
    PrimaryPropertyType_Retail_Store = 0
    PrimaryPropertyType_Small_and_Mid_Sized_Office = 0
    PrimaryPropertyType_Warehouse = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:3000/predict_single" -Method Post -ContentType "application/json" -Body $body
```

**Réponse :**
```json
{
  "predicted_energy_kwh": 1450000,
  "predicted_energy_formatted": "1,450,000 kWh",
  "model_info": {
    "algorithm": "Linear Regression",
    "r2_score": "0.9343 (93.43%)",
    "mae_test": "90,144 kWh",
    "rmse_test": "261,530 kWh"
  },
  "status": "success",
  "warnings": []
}
```

#### `/predict_batch` - Prédictions multiples
```bash
curl -X POST "http://localhost:3000/predict_batch" \
     -H "Content-Type: application/json" \
     -d '[
       {"PropertyGFATotal": 30000, "NumberofFloors": 3, "Electricity_kWh": 500000, "NaturalGas_kWh": 100000, "PrimaryPropertyType_Large_Office": 0, "PrimaryPropertyType_Other": 1, "PrimaryPropertyType_Retail_Store": 0, "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0, "PrimaryPropertyType_Warehouse": 0},
       {"PropertyGFATotal": 75000, "NumberofFloors": 8, "Electricity_kWh": 1200000, "NaturalGas_kWh": 300000, "PrimaryPropertyType_Large_Office": 1, "PrimaryPropertyType_Other": 0, "PrimaryPropertyType_Retail_Store": 0, "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0, "PrimaryPropertyType_Warehouse": 0}
     ]'
```

#### `/get_feature_info` - Informations sur les features
```bash
curl "http://localhost:3000/get_feature_info"
```

#### `/validate_data` - Validation seule
```bash
curl -X POST "http://localhost:3000/validate_data" \
     -H "Content-Type: application/json" \
     -d '{
       "PropertyGFATotal": 50000,
       "NumberofFloors": 5,
       "Electricity_kWh": 800000,
       "NaturalGas_kWh": 200000,
       "PrimaryPropertyType_Large_Office": 1,
       "PrimaryPropertyType_Other": 0,
       "PrimaryPropertyType_Retail_Store": 0,
       "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
       "PrimaryPropertyType_Warehouse": 0
     }'
```

**Réponse :**
```json
{
  "validation_status": "valid",
  "warnings": ["Intensité énergétique élevée: 120.5 kWh/sq ft"],
  "warning_count": 1,
  "data_summary": {
    "PropertyGFATotal": 50000,
    "NumberofFloors": 5,
    "total_energy": 1000000,
    "energy_intensity": 20.0,
    "building_type": "Grand Bureau"
  },
  "status": "warning"
}
```

#### `/health` - Statut du service
```bash
curl "http://localhost:3000/health"
```

## Tests Recommandés via Swagger UI

### Test 1: Grand Bureau (Large Office)
```json
{
  "PropertyGFATotal": 75000,
  "NumberofFloors": 10,
  "Electricity_kWh": 1200000,
  "NaturalGas_kWh": 300000,
  "PrimaryPropertyType_Large_Office": 1,
  "PrimaryPropertyType_Other": 0,
  "PrimaryPropertyType_Retail_Store": 0,
  "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
  "PrimaryPropertyType_Warehouse": 0
}
```

### Test 2: Magasin (Retail Store)
```json
{
  "PropertyGFATotal": 25000,
  "NumberofFloors": 2,
  "Electricity_kWh": 600000,
  "NaturalGas_kWh": 150000,
  "PrimaryPropertyType_Large_Office": 0,
  "PrimaryPropertyType_Other": 0,
  "PrimaryPropertyType_Retail_Store": 1,
  "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
  "PrimaryPropertyType_Warehouse": 0
}
```

### Test 3: Entrepôt (Warehouse)
```json
{
  "PropertyGFATotal": 100000,
  "NumberofFloors": 3,
  "Electricity_kWh": 500000,
  "NaturalGas_kWh": 80000,
  "PrimaryPropertyType_Large_Office": 0,
  "PrimaryPropertyType_Other": 0,
  "PrimaryPropertyType_Retail_Store": 0,
  "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
  "PrimaryPropertyType_Warehouse": 1
}
```

### Test 4: Validation seule (sans prédiction)
```json
{
  "PropertyGFATotal": 25000,
  "NumberofFloors": 50,
  "Electricity_kWh": 2000000,
  "NaturalGas_kWh": 500000,
  "PrimaryPropertyType_Large_Office": 0,
  "PrimaryPropertyType_Other": 1,
  "PrimaryPropertyType_Retail_Store": 0,
  "PrimaryPropertyType_Small_and_Mid_Sized_Office": 0,
  "PrimaryPropertyType_Warehouse": 0
}
```
*Ce test générera des avertissements sur l'intensité énergétique élevée et le nombre d'étages excessif.*

## Features Requises

Le modèle attend ces **9 features** :

1. **PropertyGFATotal** - Surface totale (pieds carrés)
2. **NumberofFloors** - Nombre d'étages
3. **Electricity_kWh** - Consommation électrique
4. **NaturalGas_kWh** - Consommation gaz naturel
5. **PrimaryPropertyType_Large_Office** (0 ou 1)
6. **PrimaryPropertyType_Other** (0 ou 1)
7. **PrimaryPropertyType_Retail_Store** (0 ou 1)
8. **PrimaryPropertyType_Small_and_Mid_Sized_Office** (0 ou 1)
9. **PrimaryPropertyType_Warehouse** (0 ou 1)

> **Note :** Une seule des variables `PrimaryPropertyType_*` doit être à 1, les autres à 0.

## Déploiement Docker

### 1. Construire le Bento
```bash
# Dans le dossier app/
bentoml build
```

### 2. Containeriser avec le tag exact
```bash
# Utilisez le tag généré lors du build (exemple récent)
# Le tag change à chaque build - utilisez celui affiché après 'bentoml build'
bentoml containerize seattle-energy-predictor:z5ctjo5wkgv3ypak
```

### 3. Lancer le container
```bash
# Utilisez le même tag que pour la containerisation
# Le flag --rm supprime automatiquement le container à l'arrêt
docker run --rm -p 3000:3000 seattle-energy-predictor:z5ctjo5wkgv3ypak
```

### 4. Accéder au service containerisé
- **API** : `http://localhost:3000`

## Utiliser l'image depuis Docker Hub

Vous pouvez directement récupérer l'image déjà publiée sur Docker Hub et l'exécuter localement.

### Récupérer l'image
```powershell
# Dernière version (latest)
docker pull merais/seattle-energy-predictor:latest

# Version figée (reproductible)
docker pull merais/seattle-energy-predictor:z5ctjo5wkgv3ypak
```

### Lancer l'image
```powershell
# Port mapping 3000:3000 (BentoML écoute sur 3000)
docker run --rm -p 3000:3000 merais/seattle-energy-predictor:latest

# Ou avec le tag spécifique
docker run --rm -p 3000:3000 merais/seattle-energy-predictor:z5ctjo5wkgv3ypak
```

### Accéder à l'API
- **Swagger UI / API** : `http://localhost:3000`

Note:
- Si le dépôt Docker Hub est privé, connectez-vous avant le pull: `docker login`
- Les tags changent à chaque build automatisé; utilisez toujours le tag affiché après `bentoml build` pour rester cohérent.