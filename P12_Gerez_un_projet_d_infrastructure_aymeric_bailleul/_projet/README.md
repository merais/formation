# P12 – Gérez un projet d'infrastructure

**Auteur :** Aymeric Bailleul  
**Formation :** Data Engineer – OpenClassrooms  
**Période :** 10/03/2026 → 11/04/2026

---

## Objectif du projet

Gérer un projet d'infrastructure de données de bout en bout : planification, pilotage, communication et livraison. Ce projet met l'accent sur les compétences de gestion de projet (Agile/Scrum, JIRA, documentation, roadmap) appliquées à un contexte Data Engineering.

---

## Structure du dossier

```
_projet/
├── _docs/          # Documentation technique et fonctionnelle
├── analyses/       # Analyses, roadmap, retrospectives
├── data/           # Données de référence ou exemples
├── src/            # Code source (scripts, IaC, automatisations)
├── .venv/          # Environnement virtuel Python (non versionné)
├── README.md       # Ce fichier
├── pyproject.toml  # Configuration du projet et des dépendances (uv)
└── uv.lock         # Fichier de verrouillage des dépendances (versionné)
```

---

## Livrables attendus

- Rapport de gestion de projet (backlog, sprints, retrospective)
- Présentation de soutenance
- Documentation de l'infrastructure gérée

---

## Démarrage

Ce projet utilise [uv](https://docs.astral.sh/uv/) comme gestionnaire d'environnement et de dépendances.

```powershell
# Installer uv (si absent)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Créer l'environnement virtuel
uv venv .venv --python 3.14

# Activer l'environnement
.venv\Scripts\Activate.ps1

# Installer les dépendances (prod + dev)
uv sync --group dev
```

### Commandes uv utiles

```powershell
uv add pandas                 # Ajouter une dépendance principale
uv add --group dev pytest-cov # Ajouter une dépendance de développement
uv sync                       # Synchroniser l'environnement avec uv.lock
uv run python mon_script.py   # Exécuter un script sans activer le venv
```
