"""
Script de test pour verifier l'environnement complet du projet P11
Tests de tous les imports et de l'acces a l'API Mistral
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def test_imports():
    """Teste tous les imports necessaires au projet"""
    
    print("Test des imports...")
    tests_passed = 0
    tests_total = 0
    
    # Test LangChain
    tests_total += 1
    try:
        import langchain
        from langchain_core.documents import Document
        print(f"  [OK] LangChain {langchain.__version__}")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] LangChain : {str(e)}")
    
    # Test LangChain-Mistralai
    tests_total += 1
    try:
        from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
        print(f"  [OK] LangChain-Mistralai")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] LangChain-Mistralai : {str(e)}")
    
    # Test Faiss
    tests_total += 1
    try:
        import faiss
        print(f"  [OK] Faiss")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] Faiss : {str(e)}")
    
    # Test Mistral
    tests_total += 1
    try:
        from mistralai import Mistral
        print(f"  [OK] Mistral AI SDK")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] Mistral : {str(e)}")
    
    # Test Pandas
    tests_total += 1
    try:
        import pandas as pd
        print(f"  [OK] Pandas {pd.__version__}")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] Pandas : {str(e)}")
    
    # Test NumPy
    tests_total += 1
    try:
        import numpy as np
        print(f"  [OK] NumPy {np.__version__}")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] NumPy : {str(e)}")
    
    # Test Tiktoken
    tests_total += 1
    try:
        import tiktoken
        print(f"  [OK] Tiktoken")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] Tiktoken : {str(e)}")
    
    # Test Pytest
    tests_total += 1
    try:
        import pytest
        print(f"  [OK] Pytest {pytest.__version__}")
        tests_passed += 1
    except Exception as e:
        print(f"  [ERREUR] Pytest : {str(e)}")
    
    return tests_passed, tests_total


def test_mistral_api():
    """Teste la connexion a l'API Mistral"""
    
    print("\nTest de l'API Mistral AI...")
    
    # Recuperer la cle API
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key:
        print("  [ERREUR] MISTRAL_API_KEY non trouvee dans le fichier .env")
        return False
    
    print(f"  [OK] Cle API chargee : {api_key[:8]}...")
    
    try:
        # Initialiser le client Mistral
        from mistralai import Mistral
        client = Mistral(api_key=api_key)
        print("  [OK] Client Mistral initialise")
        
        # Faire un appel simple a l'API
        print("  [TEST] Appel API en cours...")
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "user",
                    "content": "Reponds simplement 'OK' si tu recois ce message."
                }
            ]
        )
        
        # Verifier la reponse
        result = response.choices[0].message.content
        print(f"  [OK] Reponse de l'API : {result}")
        return True
        
    except Exception as e:
        print(f"  [ERREUR] Appel API : {str(e)}")
        return False


def test_faiss_functionality():
    """Teste les fonctionnalites de base de Faiss"""
    
    print("\nTest des fonctionnalites Faiss...")
    
    try:
        import faiss
        import numpy as np
        
        # Creer un index simple
        dimension = 128
        index = faiss.IndexFlatL2(dimension)
        print(f"  [OK] Index Faiss cree (dimension={dimension})")
        
        # Ajouter des vecteurs de test
        vectors = np.random.random((10, dimension)).astype('float32')
        index.add(vectors)
        print(f"  [OK] Vecteurs ajoutes a l'index (total={index.ntotal})")
        
        # Effectuer une recherche
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, k=3)
        print(f"  [OK] Recherche effectuee (k=3)")
        
        return True
        
    except Exception as e:
        print(f"  [ERREUR] Faiss : {str(e)}")
        return False


def main():
    """Fonction principale du script de test"""
    
    print("=" * 70)
    print("TESTS DE L'ENVIRONNEMENT P11 - RAG CHATBOT")
    print("=" * 70)
    print()
    
    # Test des imports
    imports_passed, imports_total = test_imports()
    
    # Test de l'API Mistral
    api_ok = test_mistral_api()
    
    # Test de Faiss
    faiss_ok = test_faiss_functionality()
    
    # Resume final
    print("\n" + "=" * 70)
    print("RESUME DES TESTS")
    print("=" * 70)
    print(f"Imports        : {imports_passed}/{imports_total} reussis")
    print(f"API Mistral    : {'OK' if api_ok else 'ERREUR'}")
    print(f"Faiss          : {'OK' if faiss_ok else 'ERREUR'}")
    print()
    
    # Statut global
    all_ok = (imports_passed == imports_total) and api_ok and faiss_ok
    
    if all_ok:
        print("STATUT GLOBAL  : ENVIRONNEMENT OPERATIONNEL")
        print("=" * 70)
        return 0
    else:
        print("STATUT GLOBAL  : ERREURS DETECTEES")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
