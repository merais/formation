"""
Script d'évaluation Ragas pour le système RAG Puls-Events.

Auteur: Aymeric Bailleul
Date: 2026-02-17
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datasets import Dataset
import asyncio
import nest_asyncio
import traceback
import logging
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv

# Configuration des logs pour debug
logging.basicConfig(level=logging.WARNING)
logging.getLogger("ragas").setLevel(logging.DEBUG)

# Chargement des variables d'environnement depuis .env
load_dotenv()

# Désactivation de la télémétrie Ragas (évite les timeouts réseau)
os.environ["RAGAS_DO_NOT_TRACK"] = "true"

# Configuration pour permettre asyncio dans Jupyter/interactive
nest_asyncio.apply()

# Imports LangChain pour Mistral
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings

# Imports Ragas
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)


def load_test_dataset(json_path: str, max_questions: int = None) -> Dict[str, List]:
    """
    Charge le fichier JSON de test et le transforme au format attendu par Ragas :

        "question": ["Q1", "Q2", ...],
        "answer": ["A1", "A2", ...],
        "contexts": [["ctx1", "ctx2"], ["ctx3"], ...],
        "ground_truth": ["GT1", "GT2", ...]
    
    Args:
        json_path: Chemin vers le fichier JSON de test
        max_questions: Nombre maximum de questions à évaluer (None = toutes)
        
    Returns:
        Dictionnaire au format Ragas (listes parallèles)
    """
    print(f"\nChargement du jeu de données de test : {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Transformation du format {"data": [...]} vers le format Ragas
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    items = data.get("data", [])
    if max_questions:
        items = items[:max_questions]
        print(f"ATTENTION : Limitation à {max_questions} questions pour éviter les timeouts")
    
    for item in items:
        questions.append(item["question"])
        answers.append(item["answer"])
        contexts.append(item["contexts"])
        ground_truths.append(item["ground_truth"])
    
    print(f"-> {len(questions)} questions chargées")
    
    return {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }


def create_ragas_dataset(evaluation_data: Dict[str, List]) -> Dataset:
    """
    Crée un objet Dataset Hugging Face à partir des données d'évaluation.
    
    evaluation_dataset = Dataset.from_dict(evaluation_data)
    
    Args:
        evaluation_data: Dictionnaire avec les listes parallèles
        
    Returns:
        Dataset Hugging Face prêt pour Ragas
    """
    print("\nCréation du Dataset Hugging Face...")
    
    # Création du Dataset
    evaluation_dataset = Dataset.from_dict(evaluation_data)
    
    print(f"-> Dataset créé avec {len(evaluation_dataset)} exemples")
    print("\n--- Aperçu du Dataset formaté pour Ragas ---")
    print(evaluation_dataset)
    
    return evaluation_dataset


def initialize_llm_and_embeddings(api_key: str) -> tuple:
    """
    Initialise le LLM et les embeddings Mistral :
    
    - ChatMistralAI avec model="mistral-small-latest"
    - MistralAIEmbeddings
    
    Args:
        api_key: Clé API Mistral
        
    Returns:
        (mistral_llm, mistral_embeddings)
    """
    print("\nInitialisation LLM et Embeddings Mistral...")
    
    # Configuration du LLM 
    mistral_llm = ChatMistralAI(
        mistral_api_key=api_key,
        model="mistral-small-latest",  # Temporaire: test pour answer_relevancy
        #model="mistral-large-latest",
        temperature=0.2,
        timeout=300,  # Timeout de 5 minutes par appel pour éviter les timeouts API (Ragas peut être long)
        max_retries=2
    )
    
    mistral_embeddings = MistralAIEmbeddings(
        mistral_api_key=api_key
    )
    
    print("-> LLM et Embeddings initialisés (mistral-large-latest).")
    return mistral_llm, mistral_embeddings


def run_ragas_evaluation(dataset: Dataset, llm, embeddings, metrics_to_evaluate: List) -> Dict:
    """
    Lance l'évaluation Ragas QUESTION PAR QUESTION (séquentiel).
    
    Args:
        dataset: Dataset Hugging Face
        llm: Modèle ChatMistralAI
        embeddings: MistralAIEmbeddings
        metrics_to_evaluate: Liste des métriques Ragas
        
    Returns:
        Résultats de l'évaluation
    """
    print("\nLancement de l'évaluation Ragas SÉQUENTIELLE...")
    print(f"Métriques sélectionnées: {[m.name for m in metrics_to_evaluate]}")
    
    # Récupération des données du dataset
    num_questions = len(dataset)
    all_results = []
    
    # Boucle sur chaque question INDIVIDUELLEMENT
    for i in range(num_questions):
        print(f"\n{'─'*60}")
        print(f"Question {i+1}/{num_questions}")
        print(f"{'─'*60}")
        
        # Créer un mini-dataset avec UNE SEULE question
        single_question_data = {
            "question": [dataset[i]["question"]],
            "answer": [dataset[i]["answer"]],
            "contexts": [dataset[i]["contexts"]],
            "ground_truth": [dataset[i]["ground_truth"]]
        }
        single_dataset = Dataset.from_dict(single_question_data)
        
        try:
            # Évaluation d'UNE SEULE question
            result = evaluate(
                dataset=single_dataset,
                metrics=metrics_to_evaluate,
                llm=llm,
                embeddings=embeddings
            )
            
            # Convertir en dict et stocker
            result_dict = result.to_pandas().iloc[0].to_dict()
            all_results.append(result_dict)
            
            # Afficher les scores de cette question
            metrics_scores = {k: v for k, v in result_dict.items() 
                            if k in [m.name for m in metrics_to_evaluate]}
            print(f"-> Scores: {metrics_scores}")
            
        except Exception as e:
            print(f"ERREUR sur question {i+1}: {e}")
            # Ajouter des NaN pour cette question
            result_dict = {
                "question": dataset[i]["question"],
                "answer": dataset[i]["answer"],
                "contexts": dataset[i]["contexts"],
                "ground_truth": dataset[i]["ground_truth"]
            }
            for metric in metrics_to_evaluate:
                result_dict[metric.name] = None
            all_results.append(result_dict)
    
    print("\n" + "="*60)
    print("-> Évaluation Ragas terminée")
    
    # Reconstruire un objet ressemblant au résultat Ragas
    results_df = pd.DataFrame(all_results)
    
    # Créer un objet avec méthode to_pandas() pour compatibilité
    class RagasResults:
        def __init__(self, df):
            self.df = df
        def to_pandas(self):
            return self.df
    
    return RagasResults(results_df)


def display_results(results) -> pd.DataFrame:
    """
    Affiche les résultats de l'évaluation.
    
    - Affichage du DataFrame complet
    - Calcul et affichage des scores moyens
    
    Args:
        results: Résultats Ragas
        
    Returns:
        DataFrame pandas avec les résultats
    """
    print("\n" + "="*80)
    print("RÉSULTATS DE L'ÉVALUATION RAGAS")
    print("="*80)
    
    # Conversion en DataFrame selon le cours
    results_df = results.to_pandas()
    
    print("\n--- Résultats de l'évaluation (DataFrame) ---")
    print(results_df)
    
    # Calcul et affichage des scores moyens
    print("\n" + "="*80)
    print("SCORES MOYENS (sur tout le dataset)")
    print("="*80)
    average_scores = results_df.mean(numeric_only=True)
    print(average_scores)
    
    return results_df


def save_results(results_df: pd.DataFrame, output_path: str):
    """
    Sauvegarde les résultats au format JSON.
    
    Args:
        results_df: DataFrame avec les résultats
        output_path: Chemin de base pour les fichiers de sortie
    """
    print(f"\nSauvegarde des résultats...")
    
    # Préparation des métadonnées
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calcul des scores moyens
    average_scores = results_df.mean(numeric_only=True).to_dict()
    
    # Sauvegarde JSON
    json_output = {
        "meta": {
            "evaluation_date": timestamp,
            "questions_evaluated": len(results_df),
            "model": "mistral-large-latest",
            "temperature": 0.2,
            "note": "Évaluation séquentielle avec mistral-large-latest"
        },
        "scores": average_scores,
        "details": results_df.to_dict(orient='records')
    }
    
    json_path = output_path.replace('.json', '_detailed.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"-> Résultats JSON sauvegardés : {json_path}")


def main():
    """
    Fonction principale d'évaluation Ragas.
    """
    print("="*80)
    print("ÉVALUATION RAGAS - SYSTÈME RAG PULS-EVENTS")
    print("="*80)
    print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # --- Configuration et Exécution de l'Évaluation ---
    
    # Vérification de la clé API Mistral
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    if not MISTRAL_API_KEY:
        print("ERREUR : Clé API Mistral non trouvée.")
        print("ATTENTION : Définissez la variable d'environnement MISTRAL_API_KEY")
        sys.exit(1)
    
    try:
        # Chemins des fichiers
        project_root = Path(__file__).parent.parent.parent
        test_dataset_path = project_root / "data" / "evaluation" / "test_dataset_ragas.json"
        output_path = project_root / "data" / "evaluation" / "ragas_evaluation_results.json"
        
        # 1. Chargement et transformation des données
        MAX_QUESTIONS = int(os.getenv("MAX_EVAL_QUESTIONS", "10"))
        evaluation_data = load_test_dataset(str(test_dataset_path), max_questions=MAX_QUESTIONS)
        
        # 2. Création du Dataset Hugging Face
        evaluation_dataset = create_ragas_dataset(evaluation_data)
        
        # 3. Initialisation du LLM et des Embeddings
        mistral_llm, mistral_embeddings = initialize_llm_and_embeddings(MISTRAL_API_KEY)
        
        # 4. Définition des métriques à calculer
        # Évaluation séquentielle permet d'utiliser les 4 métriques sans timeout
        # LIMITATION: answer_relevancy cause des timeouts avec mistral-small-latest (Ragas 0.4.3)
        # Temporairement désactivée pour obtenir des résultats fonctionnels
        metrics_to_evaluate = [
            faithfulness,       # Génération: fidèle au contexte ? (anti-hallucinations)
            # answer_relevancy,   # DÉSACTIVÉ: timeout avec mistral-small-latest + Ragas 0.4.3
            context_precision,  # Récupération: contexte précis (peu de bruit) ?
            context_recall,     # Récupération: infos clés récupérées ? (qualité retriever)
        ]
        
        # DEBUG: Vérification des métriques
        print(f"\n>>> DEBUG: Nombre de métriques définies = {len(metrics_to_evaluate)}")
        print(f">>> DEBUG: Noms des métriques = {[m.name for m in metrics_to_evaluate]}")
        print(f">>> DEBUG: answer_relevancy temporairement désactivée (timeout mitral-small + Ragas 0.4.3)")
        
        # 5. Lancement de l'évaluation Ragas
        results = run_ragas_evaluation(
            evaluation_dataset,
            mistral_llm,
            mistral_embeddings,
            metrics_to_evaluate
        )
        
        # 6. Affichage des résultats
        results_df = display_results(results)
        
        # 7. Sauvegarde des résultats
        save_results(results_df, str(output_path))
        
        print("\n" + "="*80)
        print("ÉVALUATION TERMINÉE AVEC SUCCÈS")
        print("="*80)
        
    except Exception as e:
        print(f"\nERREUR lors de l'évaluation Ragas : {e}")
        print("\nTraceback:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
