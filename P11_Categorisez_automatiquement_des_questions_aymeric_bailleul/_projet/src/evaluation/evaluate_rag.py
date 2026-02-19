"""
Évaluation du système RAG avec Ragas.

Ce script évalue les performances du système RAG Puls-Events en utilisant
le framework Ragas avec 4 métriques clés, en suivant la structure du cours
OpenClassrooms "Mettez en place un RAG pour un LLM".

Structure du script (conforme au cours OC) :
    1. Charger les données de test (question, answer, contexts, ground_truth)
    2. Formater le dataset pour Ragas (avec `datasets.Dataset`)
    3. Initialiser le LLM et les embeddings Mistral (via LangChain)
    4. Lancer l'évaluation Ragas avec les 4 métriques
    5. Afficher et sauvegarder les résultats

Métriques évaluées :
    - faithfulness          : La réponse est-elle fidèle au contexte ? (anti-hallucination)
    - answer_relevancy      : La réponse répond-elle à la question ?
    - context_precision     : Le contexte récupéré est-il exempt de bruit ?
    - context_recall        : Toutes les infos nécessaires ont-elles été récupérées ?

Usage :
    poetry run python src/evaluation/evaluate_rag.py

    # Limiter le nombre de questions (pour un test rapide) :
    $env:MAX_EVAL_QUESTIONS="3"; poetry run python src/evaluation/evaluate_rag.py

Auteur : Aymeric Bailleul
Date   : Février 2026
"""

# =============================================================================
# IMPORTS
# =============================================================================

import os
import json
import warnings
import traceback
from pathlib import Path
from datetime import datetime

# Désactiver le tracking Ragas (évite les timeouts réseau)
os.environ["RAGAS_DO_NOT_TRACK"] = "true"

# Masquer les warnings de dépendances tierces non maîtrisées
# Note : les warnings Ragas utilisent stacklevel=2 → ils pointent vers ce fichier,
# donc on filtre par message plutôt que par module.
warnings.filterwarnings("ignore", category=FutureWarning, module="instructor")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*Importing.*ragas\\.metrics.*deprecated.*",
)

import pandas as pd
from datasets import Dataset
import nest_asyncio
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

# Appliquer nest_asyncio pour éviter les conflits d'event loop
nest_asyncio.apply()


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Charger les variables d'environnement (.env)
load_dotenv(PROJECT_ROOT / ".env")

# Chemins des données
DATASET_PATH = PROJECT_ROOT / "data" / "evaluation" / "test_dataset_ragas.json"
RESULTS_DIR  = PROJECT_ROOT / "data" / "evaluation"

# Modèle Mistral API pour l'évaluation
EVAL_LLM_MODEL       = "mistral-large-latest"
EVAL_EMBED_MODEL     = "mistral-embed"
EVAL_TEMPERATURE     = 0.1
MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY")

# Nombre maximum de questions à évaluer (None = toutes)
# Peut être surchargé via la variable d'environnement MAX_EVAL_QUESTIONS
MAX_QUESTIONS = os.getenv("MAX_EVAL_QUESTIONS")
MAX_QUESTIONS = int(MAX_QUESTIONS) if MAX_QUESTIONS else None

# Configuration du timeout et du parallélisme pour Ragas
# max_workers=4  : 4 workers en parallèle (Mistral API, rate limit géré par max_wait)
# timeout=120    : 2 minutes max par opération
# max_retries=3  : 3 tentatives en cas d'erreur réseau
# max_wait=60    : 60s max entre les tentatives (backoff API)
RUN_CONFIG = RunConfig(
    max_workers=1,
    timeout=120,
    max_retries=3,
    max_wait=60,
)


# =============================================================================
# 1. CHARGEMENT DES DONNÉES DE TEST
# =============================================================================

def load_test_dataset(path: Path, max_questions: int = None) -> dict:
    """
    Charge le jeu de données de test depuis le fichier JSON.

    Le dataset contient des entrées pré-calculées par le pipeline RAG :
        - question    : Question posée à l'assistant
        - answer      : Réponse générée par le système RAG
        - contexts    : Chunks récupérés par le retriever FAISS
        - ground_truth: Réponse idéale définie manuellement

    Args:
        path         : Chemin vers le fichier JSON
        max_questions: Nombre maximum de questions à charger (None = toutes)

    Returns:
        Dictionnaire avec les listes questions, answers, contexts, ground_truths
    """
    print(f"\nChargement du dataset : {path.name}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = raw["data"]

    if max_questions:
        data = data[:max_questions]
        print(f"   Mode test : {max_questions} question(s) chargée(s)")
    else:
        print(f"   {len(data)} questions chargées")

    questions    = [item["question"]    for item in data]
    answers      = [item["answer"]      for item in data]
    contexts     = [item["contexts"]    for item in data]
    ground_truths = [item["ground_truth"] for item in data]

    return {
        "question":     questions,
        "answer":       answers,
        "contexts":     contexts,
        "ground_truth": ground_truths,
    }


# =============================================================================
# 2. FORMATAGE DU DATASET POUR RAGAS
# =============================================================================

def build_ragas_dataset(evaluation_data: dict) -> Dataset:
    """
    Formate les données en objet Dataset Hugging Face, format attendu par Ragas.

    Args:
        evaluation_data: Dictionnaire avec les clés question, answer, contexts, ground_truth

    Returns:
        Dataset Hugging Face prêt pour Ragas
    """
    evaluation_dataset = Dataset.from_dict(evaluation_data)

    print(f"\n--- Aperçu du Dataset formaté pour Ragas ---")
    print(evaluation_dataset)

    return evaluation_dataset


# =============================================================================
# 3. INITIALISATION DU LLM ET DES EMBEDDINGS MISTRAL
# =============================================================================

def initialize_models() -> tuple:
    """
    Initialise le LLM et les embeddings Mistral API via LangChain.

    Le LLM est utilisé par Ragas pour juger certaines métriques (faithfulness,
    answer_relevancy). Les embeddings sont utilisés pour les métriques sémantiques.
    Nécessite la variable d'environnement MISTRAL_API_KEY définie dans .env.

    Returns:
        Tuple (mistral_llm, mistral_embeddings)
    """
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY non trouvée. Vérifiez le fichier .env.")

    print(f"\nInitialisation LLM et Embeddings Mistral API...")
    print(f"   Modèle LLM        : {EVAL_LLM_MODEL}")
    print(f"   Modèle Embeddings : {EVAL_EMBED_MODEL}")
    print(f"   Temperature      : {EVAL_TEMPERATURE}")

    mistral_llm = ChatMistralAI(
        model=EVAL_LLM_MODEL,
        api_key=MISTRAL_API_KEY,
        temperature=EVAL_TEMPERATURE,
    )

    mistral_embeddings = MistralAIEmbeddings(
        model=EVAL_EMBED_MODEL,
        api_key=MISTRAL_API_KEY,
    )

    print("   LLM et Embeddings initialisés.")

    return mistral_llm, mistral_embeddings


# =============================================================================
# 4. CONFIGURATION DES PROMPTS EN FRANÇAIS
# =============================================================================

def configure_french_prompts() -> None:
    """
    Traduit les prompts internes de Ragas en français.

    En Ragas 0.4+, chaque métrique expose ses prompts via des attributs
    PydanticPrompt dont on peut modifier l'attribut `instruction` directement.
    Sans cette configuration, Ragas génère ses requêtes au LLM juge en anglais,
    ce qui crée un biais de langue — notamment pour `answer_relevancy` qui génère
    des questions en anglais depuis des réponses françaises, entraînant une faible
    similarité cosinus avec les questions originales en français.

    Métriques concernées :
        - faithfulness           : 2 prompts (extraction + NLI)
        - answer_relevancy       : 1 prompt (génération de question)
        - context_precision      : 1 prompt (vérification d'utilité)
        - context_recall         : 1 prompt (classification phrase par phrase)
    """
    print("\nConfiguration des prompts Ragas en français...")

    # --- Faithfulness : extraction des affirmations ---
    faithfulness.statement_generator_prompt.instruction = (
        "Étant donné une question et une réponse, analysez la complexité de chaque "
        "phrase de la réponse. Décomposez chaque phrase en une ou plusieurs "
        "affirmations autonomes et compréhensibles. Assurez-vous qu'aucun pronom "
        "n'est utilisé dans les affirmations (remplacez les pronoms par les noms "
        "explicites). Formatez les résultats en JSON."
    )

    # --- Faithfulness : jugement NLI (Natural Language Inference) ---
    faithfulness.nli_statements_prompt.instruction = (
        "Votre tâche est de juger la fidélité d'une série d'affirmations par rapport "
        "à un contexte donné. Pour chaque affirmation, retournez verdict=1 si "
        "l'affirmation peut être directement déduite du contexte, ou verdict=0 si "
        "elle ne peut pas être directement déduite du contexte. "
        "RÈGLE ABSOLUE : verdict doit être EXACTEMENT 0 ou 1, jamais une valeur "
        "décimale comme 0.5 ou 0.8. Toute valeur intermédiaire est interdite."
    )

    # --- Answer Relevancy : génération de la question inverse ---
    answer_relevancy.question_generation.instruction = (
        "Génère une question en français pour la réponse donnée et identifie si "
        "la réponse est évasive. "
        "RÈGLE ABSOLUE : noncommittal doit être EXACTEMENT 0 ou 1. "
        "Donne noncommittal=1 si la réponse est évasive, vague ou ambiguë "
        "(ex : 'je ne sais pas', 'je ne suis pas sûr'). "
        "Donne noncommittal=0 si la réponse est claire et précise. "
        "Jamais de valeur décimale."
    )

    # NOTE : context_precision utilise le prompt natif anglais de Ragas.
    # Le prompt FR personnalisé empêchait mistral-large-latest de retourner le
    # champ 'verdict' attendu → score 0 sur ~80% des questions. Le prompt anglais
    # natif est correctement parsé par Ragas + mistral-large-latest.

    # --- Context Recall : attribution phrase par phrase ---
    context_recall.context_recall_prompt.instruction = (
        "Étant donné un contexte et une réponse de référence, analysez chaque phrase "
        "de la réponse et indiquez si la phrase peut être attribuée au contexte donné. "
        "RÈGLE ABSOLUE : le champ 'attributed' doit être EXACTEMENT 1 (oui) ou 0 (non). "
        "Les valeurs décimales comme 0.5, 0.8 ou toute autre fraction sont INTERDITES. "
        "En cas de doute, choisissez 0 ou 1 selon que l'attribution est majoritairement "
        "vraie ou fausse. Fournissez une raison en français. Sortie JSON."
    )

    print("   [OK] Prompts FR configurés : faithfulness (x2), answer_relevancy, context_recall.")
    print("   [OK] context_precision : prompt anglais natif Ragas (parsing plus fiable).")


# =============================================================================
# 5. LANCEMENT DE L'ÉVALUATION RAGAS
# =============================================================================

def run_evaluation(
    evaluation_dataset: Dataset,
    eval_llm,
    eval_embeddings,
) -> pd.DataFrame:
    """
    Lance l'évaluation Ragas avec les 4 métriques clés.

    Métriques de génération (Le "G" de RAG) :
        - faithfulness      : La réponse est-elle ancrée dans les contextes ?
        - answer_relevancy  : La réponse correspond-elle à la question ?

    Métriques de récupération (Le "R" de RAG) :
        - context_precision : Les contextes récupérés sont-ils pertinents (peu de bruit) ?
        - context_recall    : Toutes les informations nécessaires ont-elles été récupérées ?

    Args:
        evaluation_dataset : Dataset Ragas
        eval_llm           : LLM Ollama pour juger les métriques
        eval_embeddings    : Embeddings Ollama pour les comparaisons sémantiques

    Returns:
        DataFrame Pandas avec les scores par question et par métrique
    """
    # FIX : strictness=3 (défaut) génère 3 requêtes en parallèle → LangChain/Mistral
    # tente de fusionner les llm_output dicts avec += → TypeError. strictness=1 évite ce bug.
    answer_relevancy.strictness = 1

    # Adapter les prompts des 4 métriques au français
    configure_french_prompts()

    metrics_to_evaluate = [
        faithfulness,       # Génération : fidèle au contexte ?
        answer_relevancy,   # Génération : réponse pertinente à la question ?
        context_precision,  # Récupération : contexte précis (peu de bruit) ?
        context_recall,     # Récupération : infos clés récupérées (nécessite ground_truth) ?
    ]

    print(f"\nMétriques sélectionnées : {[m.name for m in metrics_to_evaluate]}")
    print(f"RunConfig : max_workers={RUN_CONFIG.max_workers}, timeout={RUN_CONFIG.timeout}s, max_retries={RUN_CONFIG.max_retries}")
    print("\nLancement de l'évaluation Ragas (peut prendre du temps)...")

    results = evaluate(
        dataset=evaluation_dataset,
        metrics=metrics_to_evaluate,
        llm=eval_llm,
        embeddings=eval_embeddings,
        run_config=RUN_CONFIG,
    )

    print("\n--- Évaluation Ragas terminée ---")

    results_df = results.to_pandas()

    return results_df


# =============================================================================
# 6. AFFICHAGE ET SAUVEGARDE DES RÉSULTATS
# =============================================================================

def display_results(results_df: pd.DataFrame) -> None:
    """
    Affiche les résultats par question et les scores moyens.

    Args:
        results_df: DataFrame avec les scores Ragas
    """
    pd.set_option("display.max_rows",    None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width",       1000)
    pd.set_option("display.max_colwidth", 150)

    print("\n--- Résultats de l'évaluation (DataFrame) ---")
    print(results_df)

    print("\n--- Scores Moyens (sur tout le dataset) ---")
    average_scores = results_df.mean(numeric_only=True)
    print(average_scores)


def save_results(results_df: pd.DataFrame, nb_questions: int) -> None:
    """
    Sauvegarde les résultats dans un fichier JSON daté.

    Args:
        results_df   : DataFrame avec les scores Ragas
        nb_questions : Nombre de questions évaluées
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"ragas_results_{timestamp}.json"

    average_scores = results_df.mean(numeric_only=True).to_dict()

    output = {
        "metadata": {
            "date":           datetime.now().isoformat(),
            "nb_questions":   nb_questions,
            "llm_model":      EVAL_LLM_MODEL,
            "embed_model":    EVAL_EMBED_MODEL,
            "prompts_lang":   "french",
            "metrics":        ["faithfulness", "answer_relevancy", "context_precision", "context_recall"],
        },
        "average_scores": average_scores,
        "detailed_results": results_df.to_dict(orient="records"),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nRésultats sauvegardés : {output_path.name}")


# =============================================================================
# 7. POINT D'ENTRÉE PRINCIPAL
# =============================================================================

def main():
    print("\n" + "=" * 70)
    print(" ÉVALUATION DU SYSTÈME RAG PULS-EVENTS AVEC RAGAS ".center(70, "="))
    print("=" * 70)

    try:
        # 1. Charger les données
        evaluation_data = load_test_dataset(DATASET_PATH, max_questions=MAX_QUESTIONS)

        # 2. Formater pour Ragas
        evaluation_dataset = build_ragas_dataset(evaluation_data)

        # 3. Initialiser LLM et embeddings (Ollama local, pas de clé API)
        ollama_llm, ollama_embeddings = initialize_models()

        # 4. Lancer l'évaluation
        results_df = run_evaluation(evaluation_dataset, eval_llm=ollama_llm, eval_embeddings=ollama_embeddings)

        # 5. Afficher et sauvegarder
        display_results(results_df)
        save_results(results_df, nb_questions=len(evaluation_data["question"]))

    except Exception as e:
        print(f"\nERREUR lors de l'évaluation Ragas : {e}")
        print("\nTraceback :")
        traceback.print_exc()


if __name__ == "__main__":
    main()
