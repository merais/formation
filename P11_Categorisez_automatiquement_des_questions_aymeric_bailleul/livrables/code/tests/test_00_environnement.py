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
    
    # Assertion pytest (pas de return)
    assert tests_passed == tests_total, f"Seulement {tests_passed}/{tests_total} imports reussis"


def test_mistral_api():
    """Teste la connexion a l'API Mistral"""
    
    print("\nTest de l'API Mistral AI...")
    
    # Recuperer la cle API
    api_key = os.getenv("MISTRAL_API_KEY")
    
    assert api_key is not None, "MISTRAL_API_KEY non trouvee dans le fichier .env"
    
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
        
        # Assertion pytest (pas de return)
        assert result is not None, "Aucune reponse de l'API Mistral"
        
    except Exception as e:
        print(f"  [ERREUR] Appel API : {str(e)}")
        raise AssertionError(f"Echec de l'appel API Mistral : {str(e)}")


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
        
        # Assertion pytest (pas de return)
        assert index.ntotal == 10, f"Nombre de vecteurs incorrect: {index.ntotal}"
        assert len(indices[0]) == 3, "Recherche n'a pas retourne 3 resultats"
        
    except Exception as e:
        print(f"  [ERREUR] Faiss : {str(e)}")
        raise AssertionError(f"Echec du test Faiss : {str(e)}")


def main():
    """Fonction principale du script de test"""
    
    print("=" * 70)
    print("TESTS DE L'ENVIRONNEMENT P11 - RAG CHATBOT")
    print("=" * 70)
    print()
    
    all_tests_passed = True
    
    # Test des imports
    try:
        test_imports()
        imports_status = "OK"
    except AssertionError as e:
        imports_status = f"ERREUR: {str(e)}"
        all_tests_passed = False
    
    # Test de l'API Mistral
    try:
        test_mistral_api()
        api_status = "OK"
    except AssertionError as e:
        api_status = f"ERREUR: {str(e)}"
        all_tests_passed = False
    
    # Test de Faiss
    try:
        test_faiss_functionality()
        faiss_status = "OK"
    except AssertionError as e:
        faiss_status = f"ERREUR: {str(e)}"
        all_tests_passed = False
    
    # Resume final
    print("\n" + "=" * 70)
    print("RESUME DES TESTS")
    print("=" * 70)
    print(f"Imports        : {imports_status}")
    print(f"API Mistral    : {api_status}")
    print(f"Faiss          : {faiss_status}")
    print()
    
    # Statut global
    if all_tests_passed:
        print("STATUT GLOBAL  : ENVIRONNEMENT OPERATIONNEL")
        print("=" * 70)
        return 0
    else:
        print("STATUT GLOBAL  : ERREURS DETECTEES")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
