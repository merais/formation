# Projet P2 - Analyse des données de systèmes éducatifs

Ce projet contient l'analyse exploratoire des données de systèmes éducatifs.

## 📦 Dépendances

Le projet utilise les bibliothèques Python suivantes :
- **pandas** : Manipulation et analyse de données
- **numpy** : Calculs numériques
- **matplotlib** : Visualisations graphiques
- **seaborn** : Visualisations statistiques avancées
- **ipython** : Interface interactive Python
- **jupyter** : Notebooks interactifs

## 🚀 Utilisation de l'environnement virtuel

### Option 1 : Utiliser Poetry shell (recommandé)
```powershell
cd "G:\Mon Drive\_formation_over_git\P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric"
py -3.14 -m poetry shell
jupyter notebook
```

### Option 2 : Exécution directe avec Poetry
```powershell
cd "G:\Mon Drive\_formation_over_git\P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric"
py -3.14 -m poetry run jupyter notebook
```

### Option 3 : Activation manuelle de l'environnement
```powershell
cd "G:\Mon Drive\_formation_over_git\P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric"
.\.venv\Scripts\Activate.ps1
jupyter notebook
```

## 📋 Commandes Poetry utiles

```powershell
# Afficher les dépendances installées
py -3.14 -m poetry show

# Afficher les informations de l'environnement
py -3.14 -m poetry env info

# Installer une nouvelle dépendance
py -3.14 -m poetry add <nom_package>

# Mettre à jour les dépendances
py -3.14 -m poetry update
```

## 📁 Fichiers du projet

| Fichier | Description |
|---------|-------------|
| `ABAI_P2_01_notebook.ipynb` | Notebook principal d'analyse exploratoire |
| `pyproject.toml` | Configuration Poetry et dépendances |
| `sources/` | Données sources CSV |
