# P9 - Modélisez une infrastructure dans le cloud

**Dates :** 19/12/2025 → 15/01/2026

## 📋 Objectif du projet

Concevoir et modéliser une infrastructure cloud pour répondre aux besoins d'une application ou d'un système de données.

## 🛠️ Technologies utilisées

- Python 3.14
- Cloud Provider (AWS/Azure/GCP)
- Infrastructure as Code (Terraform/CloudFormation)

## 📂 Structure du projet

```
P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul/
├── _cours/                    # Notes et exercices de cours
├── _projet/                   # Fichiers du projet
├── P9_.../                    # Livrables finaux
├── .venv/                     # Environnement virtuel Python 3.14
├── README.md                  # Ce fichier
└── pyproject.toml            # Configuration des dépendances
```

## 🚀 Installation

### Activer l'environnement virtuel

#### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### WSL Ubuntu (Python 3.14) - Recommandé

```bash
# Option 1: Utiliser le script d'activation
wsl bash wsl_activate.sh

# Option 2: Commandes manuelles
wsl -e bash -c "cd ~/projet_p9 && source venv/bin/activate && cd projet_source && bash"

# Option 3: Exécuter directement un script
wsl -e bash -c "cd ~/projet_p9 && source venv/bin/activate && cd projet_source/_projet && python votre_script.py"
```

### Structure WSL

- Environnement virtuel: `/home/meraisfix/projet_p9/venv/`
- Lien vers projet: `/home/meraisfix/projet_p9/projet_source/` -> Lecteur G
- Python: 3.14.2
- Packages: pandas, python-dotenv, pytest, black, flake8

### Installer les dépendances

```powershell
pip install -r requirements.txt
# ou
pip install -e .
```

## Notes

- **Windows**: Environnement virtuel Python 3.14 dans `.venv/`
- **WSL**: Environnement virtuel Python 3.14 dans `~/projet_p9/venv/`
- Chemin Windows : `G:\Mon Drive\_formation_over_git\P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul\.venv\Scripts\python.exe`
- Les fichiers sont toujours synchronisés sur le lecteur G (Google Drive)

---

*Projet en cours de développement*
