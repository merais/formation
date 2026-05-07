# Projet P6 - Anticipation des besoins en consommation de bâtiments

Ce projet contient l'analyse et la modélisation prédictive de la consommation énergétique de bâtiments à Seattle.

## 📦 Dépendances

Le projet utilise les bibliothèques Python suivantes :
- **pandas** : Manipulation et analyse de données
- **numpy** : Calculs numériques
- **matplotlib** : Visualisations graphiques
- **seaborn** : Visualisations statistiques avancées
- **scikit-learn** : Machine Learning (RandomForestRegressor)
- **bentoml** : Serving et déploiement de modèles ML
- **pydantic** : Validation de données et API
- **ipython** : Interface interactive Python
- **jupyter** : Notebooks interactifs

## 🚀 Utilisation de l'environnement virtuel

### Option 1 : Activation manuelle de l'environnement
```powershell
cd "G:\Mon Drive\_formation_over_git\P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric"
.\.venv\Scripts\Activate.ps1
jupyter notebook
```

### Option 2 : Exécution directe avec Python
```powershell
cd "G:\Mon Drive\_formation_over_git\P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric"
.\.venv\Scripts\python.exe _projet\app\service.py
```

## 🤖 Entraînement et sauvegarde du modèle

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Sauvegarder le modèle avec BentoML
cd _projet\app
python save_model_SeattleEnergyPredictor.py

# Vérifier le modèle sauvegardé
bentoml models list
```

## 🌐 Lancer le service BentoML

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Lancer le service
cd _projet\app
bentoml serve service:svc --reload
```

Le service sera disponible sur `http://localhost:3000`

## 📊 Utiliser les notebooks

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Lancer Jupyter
cd _projet\notebooks
jupyter notebook
```

## 📋 Fichiers du projet

### Scripts Python
| Fichier | Description |
|---------|-------------|
| `_projet/app/service.py` | Service BentoML pour l'API de prédiction |
| `_projet/app/save_model_SeattleEnergyPredictor.py` | Script de sauvegarde du modèle |

### Notebooks
| Notebook | Description |
|----------|-------------|
| `ABAI_P6_notebook_01_analyse_exploratoire.ipynb` | Analyse exploratoire des données |
| `ABAI_P6_notebook_02_featuring.ipynb` | Ingénierie des features |
| `ABAI_P6_notebook_03_modeling_preparation.ipynb` | Préparation à la modélisation |
| `ABAI_P6_notebook_04_models_comparison.ipynb` | Comparaison de modèles |
| `ABAI_P6_notebook_05_interpretation_optimization.ipynb` | Interprétation et optimisation |
| `ABAI_P6_code06_save_with_bentoml.ipynb` | Sauvegarde avec BentoML |

## 🔧 Configuration

Le modèle est configuré avec les hyperparamètres suivants :
- `n_estimators`: 200
- `max_depth`: 20
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `random_state`: 42

## 📁 Structure du projet

```
P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric/
├── _projet/
│   ├── app/
│   │   ├── service.py                        # Service BentoML
│   │   └── save_model_SeattleEnergyPredictor.py  # Sauvegarde modèle
│   ├── notebooks/                            # Notebooks d'analyse
│   └── sources/                              # Données sources
├── .venv/                                    # Environnement virtuel
├── pyproject.toml                            # Configuration Poetry
└── README.md                                 # Ce fichier
```
