#!/bin/bash

# Script de travail WSL pour le projet P9
# Ce script active l'environnement virtuel et navigue vers le projet

cd ~/projet_p9
source venv/bin/activate
cd projet_source

echo "Environnement Python 3.14 activé"
echo "Projet: $(pwd)"
echo "Python: $(python --version)"
echo ""
echo "Commandes utiles:"
echo "  python _projet/votre_script.py    - Exécuter un script"
echo "  pytest _projet/                    - Lancer les tests"
echo "  black _projet/                     - Formater le code"
echo "  flake8 _projet/                    - Vérifier le style"
echo ""

# Lancer un bash interactif
exec bash
