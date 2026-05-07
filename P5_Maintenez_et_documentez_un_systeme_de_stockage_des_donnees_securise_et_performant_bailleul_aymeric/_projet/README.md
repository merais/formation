# Projet P5 - Maintenance et documentation d'un système de stockage MongoDB

Ce projet contient les scripts de création, maintenance et tests pour une base de données MongoDB sécurisée.

## 📦 Dépendances

Le projet utilise les bibliothèques Python suivantes :
- **pandas** : Manipulation de données pour import CSV
- **pymongo** : Client MongoDB pour Python
- **pytest** : Framework de tests unitaires
- **python-dotenv** : Gestion des variables d'environnement

## 🚀 Utilisation de l'environnement virtuel

### Option 1 : Activation manuelle de l'environnement
```powershell
cd "G:\Mon Drive\_formation_over_git\P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric"
.\.venv\Scripts\Activate.ps1
```

### Option 2 : Exécution directe avec Python
```powershell
cd "G:\Mon Drive\_formation_over_git\P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric"
.\.venv\Scripts\python.exe _projet\script_bdd.py
```

## 🧪 Exécuter les tests

```powershell
# Avec l'environnement activé
.\.venv\Scripts\Activate.ps1
pytest _projet\test_bdd.py -v

# Ou directement
.\.venv\Scripts\python.exe -m pytest _projet\test_bdd.py -v
```

## 📋 Scripts disponibles

| Script | Description |
|--------|-------------|
| `_projet/script_bdd.py` | Création de la base de données et import des données CSV |
| `_projet/script_create_users.py` | Création des utilisateurs MongoDB avec rôles |
| `_projet/test_bdd.py` | Tests unitaires de la base de données |
| `_projet/test_readonly_security.py` | Tests de sécurité pour utilisateur lecture seule |
| `_projet/test_readwrite_security.py` | Tests de sécurité pour utilisateur lecture/écriture |
| `_projet/local/local_script_bdd.py` | Script de test en local (sans Docker) |

## 🐳 Configuration Docker

Les scripts utilisent des variables d'environnement pour la connexion MongoDB :
- `MONGODB_URI` : URI complète de connexion
- `MONGODB_DB` : Nom de la base de données (défaut: `healthcare_db`)
- `COLLECTION_NAME` : Nom de la collection (défaut: `patients`)
- `SOURCE_CSV` : Chemin du fichier CSV à importer

## 📁 Structure du projet

```
P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric/
├── _projet/
│   ├── script_bdd.py              # Script principal d'import
│   ├── script_create_users.py     # Gestion des utilisateurs
│   ├── test_bdd.py                # Tests unitaires
│   ├── test_readonly_security.py  # Tests sécurité lecture
│   ├── test_readwrite_security.py # Tests sécurité écriture
│   ├── local/                     # Scripts de test local
│   └── sources/                   # Fichiers CSV sources
├── .venv/                         # Environnement virtuel
├── pyproject.toml                 # Configuration Poetry
└── README.md                      # Ce fichier
```
