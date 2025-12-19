"""
Script de test pour vérifier l'environnement WSL Python 3.14
"""

import sys
import pandas as pd
from dotenv import load_dotenv

def main():
    print("Test de l'environnement WSL Python 3.14")
    print("=" * 50)
    print(f"Version Python: {sys.version}")
    print(f"Exécutable: {sys.executable}")
    print(f"Version Pandas: {pd.__version__}")
    print("=" * 50)
    print("Environnement configuré correctement !")
    
    # Test simple avec pandas
    df = pd.DataFrame({
        'nom': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    })
    print("\nTest DataFrame Pandas:")
    print(df)

if __name__ == "__main__":
    main()
