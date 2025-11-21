# Projet P8 - Construction et test d'une infrastructure de données

Ce projet contient la configuration et les tests d'une infrastructure de données avec Airbyte.

## 📦 Dépendances

Le projet utilise les bibliothèques Python suivantes :
- **airbyte** : SDK Python pour Airbyte (gestion des pipelines de données)
- **duckdb** : Base de données analytique embarquée
- **pandas** : Manipulation et analyse de données
- **sqlalchemy** : ORM et toolkit SQL

## 🚀 Utilisation de l'environnement virtuel

### Option 1 : Activation manuelle de l'environnement
```powershell
cd "G:\Mon Drive\_formation_over_git\P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul"
.\.venv\Scripts\Activate.ps1
```

### Option 2 : Exécution directe avec Python 3.10
```powershell
cd "G:\Mon Drive\_formation_over_git\P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul"
.\.venv\Scripts\python.exe _cours\tuto_airbyte_main.py
```

## 📊 Utiliser Airbyte

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Lister les connecteurs disponibles
python -c "import airbyte as ab; print(ab.get_available_connectors())"

# Exécuter le script de test
python _cours\tuto_airbyte_main.py
```

## 🔧 Configuration Airbyte

Airbyte est un outil d'intégration de données open-source qui permet de :
- Extraire des données de diverses sources (API, bases de données, fichiers, etc.)
- Transformer les données selon vos besoins
- Charger les données vers des destinations (data warehouses, lacs de données, etc.)

### Connecteurs supportés
Le SDK Airbyte Python supporte de nombreux connecteurs :
- Sources : GitHub, Stripe, Postgres, MySQL, MongoDB, etc.
- Destinations : Snowflake, BigQuery, DuckDB, Postgres, etc.

## 📋 Scripts disponibles

| Script | Description |
|--------|-------------|
| `_cours/tuto_airbyte_main.py` | Script de test des fonctionnalités Airbyte |

## 🐳 Intégration Docker

Pour utiliser Airbyte en production, vous pouvez :
1. Utiliser Docker Compose pour déployer Airbyte localement
2. Configurer vos sources et destinations via l'interface web
3. Utiliser le SDK Python pour orchestrer vos pipelines

```powershell
# Démarrer Airbyte avec Docker Compose
docker-compose up -d

# L'interface web sera disponible sur http://localhost:8000
```

## ⚙️ Version Python

Ce projet nécessite **Python 3.10** (ou 3.11, 3.12) car la bibliothèque `airbyte` n'est pas compatible avec Python 3.13+.

## 📁 Structure du projet

```
P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul/
├── _cours/
│   └── tuto_airbyte_main.py      # Script de test Airbyte
├── .venv/                         # Environnement virtuel Python 3.10
├── pyproject.toml                 # Configuration Poetry
└── README.md                      # Ce fichier
```

## 🔗 Ressources

- [Documentation Airbyte](https://docs.airbyte.com/)
- [SDK Python Airbyte](https://pypi.org/project/airbyte/)
- [Airbyte GitHub](https://github.com/airbytehq/airbyte)
