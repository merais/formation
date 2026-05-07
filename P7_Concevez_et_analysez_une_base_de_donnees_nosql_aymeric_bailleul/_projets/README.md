# P7 - Conception et Analyse Base de Données NoSQL

Projet de conception et analyse d'une base de données MongoDB avec Python.

## Environnement

- **Python 3.14.0**
- **Gestionnaire de dépendances** : Poetry 2.2.1
- **Environnement virtuel** : `.venv` (géré par Poetry)

## Installation des dépendances

Si ce n'est pas déjà fait, installez les dépendances avec Poetry :

```powershell
# Aller dans le dossier du projet
cd "G:\Mon Drive\_formation_over_git\P7_Concevez_et_analysez_une_base_de_donnees_nosql_aymeric_bailleul"

# Installer les dépendances (crée automatiquement le .venv)
py -3.14 -m poetry install
```

## Utilisation de l'environnement virtuel

### Option 1 : Avec Poetry Shell (Recommandé)

```powershell
# Activer l'environnement Poetry
py -3.14 -m poetry shell

# Vous êtes maintenant dans le shell Poetry (.venv activé)
# Exécuter vos scripts normalement
python _projets\ABAI_P7_script_01_polars_requests.py
python _projets\ABAI_P7_script_02_integration_data.py

# Pour quitter le shell Poetry
exit
```

### Option 2 : Exécution directe avec Poetry

Sans activer le shell, exécutez directement :

```powershell
# Exécuter un script Python via Poetry
py -3.14 -m poetry run python _projets\ABAI_P7_script_01_polars_requests.py
```

### Option 3 : Activation manuelle du venv

```powershell
# Activer l'environnement virtuel manuellement
.\.venv\Scripts\Activate.ps1

# Exécuter vos scripts
python _projets\ABAI_P7_script_01_polars_requests.py

# Désactiver l'environnement
deactivate
```

## Dépendances installées

- **pymongo** (4.15.4) : Client Python officiel pour MongoDB
- **polars** (1.35.2) : Manipulation de données ultra-performante
- **python-dotenv** (1.2.1) : Gestion des variables d'environnement
- **dnspython** (2.8.0) : Support DNS pour MongoDB (dépendance de pymongo)

## Scripts du projet

| Script | Description |
|--------|-------------|
| `ABAI_P7_script_01_polars_requests.py` | Connexion et requêtes MongoDB |
| `ABAI_P7_script_02_integration_data.py` | Intégration de données CSV dans MongoDB |
| `ABAI_P7_script_03_test_replication.py` | Tests de réplication MongoDB |
| `ABAI_P7_script_04_test_sharding.py` | Tests de sharding MongoDB |

## Commandes Poetry utiles

```powershell
# Afficher les informations sur l'environnement
py -3.14 -m poetry env info

# Lister les dépendances installées
py -3.14 -m poetry show

# Ajouter une nouvelle dépendance
py -3.14 -m poetry add nom-du-package

# Mettre à jour les dépendances
py -3.14 -m poetry update

# Vérifier le fichier pyproject.toml
py -3.14 -m poetry check
```
