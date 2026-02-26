"""
Génération du dataset de test pour l'évaluation Ragas.

Ce script régénère les réponses et contextes pour chaque question du dataset,
en utilisant le système RAG Puls-Events. Il préserve les questions et ground_truths
définis manuellement, et écrase les answers + contexts avec le système RAG actuel.

Usage :
    poetry run python src/evaluation/generate_test_dataset.py

Auteur : Aymeric Bailleul
Date   : Février 2026
"""

import json
import re
from pathlib import Path

# Ajouter le répertoire racine au path
import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.rag_system import RAGSystem, RETRIEVER_K

# Chemins
DATASET_PATH = PROJECT_ROOT / "data" / "evaluation" / "test_dataset_ragas.json"


# =============================================================================
# NETTOYAGE DU DATASET
# =============================================================================

# Plages Unicode des emojis et symboles à supprimer
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symboles & pictogrammes
    "\U0001F680-\U0001F6FF"  # transport & cartographie
    "\U0001F1E0-\U0001F1FF"  # drapeaux
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols extended-A
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "\U0000200D"             # zero-width joiner
    "\U0000FE0F"             # variation selector-16
    "\U0000FFFD"             # caractère de remplacement (?)
    "]+",
    flags=re.UNICODE,
)

# Tirets typographiques → tiret simple ASCII
_DASH_MAP = str.maketrans({
    "\u2013": "-",   # en dash –
    "\u2014": "-",   # em dash —
    "\u2015": "-",   # horizontal bar ―
    "\u2212": "-",   # minus sign −
    "\u2010": "-",   # hyphen ‐
    "\u2011": "-",   # non-breaking hyphen ‑
    "\u2012": "-",   # figure dash ‒
})

# Guillemets typographiques → guillemets droits
_QUOTE_MAP = str.maketrans({
    "\u00AB": '"',   # «
    "\u00BB": '"',   # »
    "\u2018": "'",   # '
    "\u2019": "'",   # '
    "\u201C": '"',   # "
    "\u201D": '"',   # "
    "\u201E": '"',   # „
    "\u201F": '"',   # ‟
    "\u2039": "'",   # ‹
    "\u203A": "'",   # ›
})

# Caractères typographiques divers
_MISC_MAP = str.maketrans({
    "\u2026": "...", # ellipse … → ...
    "\u00A0": " ",   # espace insécable → espace normale
    "\u202F": " ",   # espace fine insécable
    "\u2009": " ",   # thin space
    "\u200B": "",    # zero-width space (invisible, à supprimer)
    "\u00B7": "*",   # point médian ·
    "\u2022": "-",   # bullet •
    "\u25CF": "-",   # cercle plein ●
})


def _remove_emojis(text: str) -> str:
    """Supprime tous les emojis et symboles Unicode non textuels."""
    return _EMOJI_PATTERN.sub("", text)


def _fix_special_chars(text: str) -> str:
    """Remplace les caractères typographiques par leurs équivalents ASCII."""
    text = text.translate(_DASH_MAP)
    text = text.translate(_QUOTE_MAP)
    text = text.translate(_MISC_MAP)
    return text


def _remove_markdown(text: str) -> str:
    """
    Supprime le formatage Markdown.
    Conserve le texte brut uniquement.
    """
    # **gras** et __gras__
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # *italique* et _italique_
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    # Astérisques orphelins (ex : "texte**" ou "** texte")
    text = re.sub(r"\*+", "", text)
    # ## Titres → texte simple
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    # Liens [texte](url) → texte
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Retours à la ligne multiples → un seul
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def _normalize_whitespace(text: str) -> str:
    """Supprime les espaces multiples et les espaces de début/fin."""
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _clean_text(text: str, remove_markdown: bool = False) -> str:
    """Pipeline de nettoyage complet sur un texte."""
    text = _remove_emojis(text)
    text = _fix_special_chars(text)
    if remove_markdown:
        text = _remove_markdown(text)
    text = _normalize_whitespace(text)
    return text


def _deduplicate_contexts(contexts: list) -> list:
    """
    Supprime les contextes dupliqués en préservant l'ordre d'apparition.
    Deux contextes sont considérés identiques si leur texte normalisé est le même.
    """
    seen = set()
    unique = []
    for ctx in contexts:
        key = re.sub(r"\s+", " ", ctx).strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(ctx)
    return unique


def _fix_stuck_words(text: str) -> str:
    """
    Corrige les mots collés issus d'erreurs de concaténation.
    Ex : "laconférence" → "la conférence".
    """
    text = re.sub(
        r"\b(la|le|les|un|une|des|du|de|à|au|aux|en|sur|dans|par|pour|avec|ce|cette|ces)"
        r"((?=[A-ZÀÂÇÉÈÊËÎÏÔÙÛÜ])[^ ])",
        r"\1 \2",
        text,
    )
    return text


def clean_dataset(data: dict) -> tuple[dict, dict]:
    """
    Nettoie le dataset de test Ragas pour ne conserver que du texte brut.

    Opérations appliquées :
        1. Suppression des emojis et symboles Unicode non textuels
        2. Remplacement des caractères typographiques (tirets, guillemets, ellipses)
        3. Suppression du formatage Markdown dans les answers (**gras**, ## titres, etc.)
        4. Normalisation des espaces (espaces multiples, insécables, tabs)
        5. Correction des mots collés (ex : "laconférence" -> "la conférence")
        6. Déduplication des contextes par question

    Args:
        data: Dictionnaire brut chargé depuis le JSON

    Returns:
        Tuple (data_nettoyé, rapport) où rapport détaille les corrections effectuées
    """
    items = data["data"]
    rapport = {
        "doublons_retirés":      0,
        "questions_nettoyées":   0,
        "questions_touchées":    [],
    }

    for i, item in enumerate(items, 1):
        q_label = f"Q{i} [{item['question'][:40]}]"
        modifié = False

        # ── 1. Nettoyage des contextes ───────────────────────────────────────
        ctxs_avant = len(item["contexts"])
        ctxs_nettoyés = [_clean_text(ctx, remove_markdown=True) for ctx in item["contexts"]]

        # Déduplication après nettoyage
        ctxs_nettoyés = _deduplicate_contexts(ctxs_nettoyés)
        nb_dupes = ctxs_avant - len(ctxs_nettoyés)

        if nb_dupes:
            rapport["doublons_retirés"] += nb_dupes
            print(f"   [{q_label}] {nb_dupes} doublon(s) supprimé(s)")

        if ctxs_nettoyés != item["contexts"]:
            item["contexts"] = ctxs_nettoyés
            modifié = True

        # ── 2. Nettoyage de la réponse (avec suppression Markdown) ──────────
        ans_nettoyé = _fix_stuck_words(_clean_text(item["answer"], remove_markdown=True))
        if ans_nettoyé != item["answer"]:
            item["answer"] = ans_nettoyé
            modifié = True

        # ── 3. Nettoyage du ground_truth ────────────────────────────────────
        gt_nettoyé = _fix_stuck_words(_clean_text(item["ground_truth"]))
        if gt_nettoyé != item["ground_truth"]:
            item["ground_truth"] = gt_nettoyé
            modifié = True

        if modifié:
            rapport["questions_nettoyées"] += 1
            rapport["questions_touchées"].append(q_label)
            print(f"   [{q_label}] Nettoyé")

    data["data"] = items
    return data, rapport


def regenerate_dataset(dataset_path: Path) -> None:
    """
    Régénère les answers et contexts du dataset en utilisant le RAGSystem actuel.
    Préserve les questions et ground_truths.
    """
    # Charger le dataset existant
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["data"]
    print(f"\nDataset chargé : {len(items)} questions")
    print(f"RAGSystem configuré avec k={RETRIEVER_K}")

    # Initialiser le RAGSystem
    rag = RAGSystem(verbose=False)

    updated_items = []

    for i, item in enumerate(items, 1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n[{i}/{len(items)}] {question[:60]}...")

        response = rag.query(question)

        # Extraire les textes des contextes (page_content des documents)
        docs = rag.retriever.invoke(question)
        contexts = [doc.page_content for doc in docs]

        print(f"   → {len(contexts)} contextes récupérés")
        print(f"   → Réponse : {response['answer'][:80]}...")

        updated_items.append({
            "question":    question,
            "answer":      response["answer"],
            "contexts":    contexts,
            "ground_truth": ground_truth,
        })

    # Nettoyer le dataset avant sauvegarde
    print("\n--- Nettoyage du dataset ---")
    raw_output = {"data": updated_items}
    raw_output, rapport = clean_dataset(raw_output)
    updated_items = raw_output["data"]

    if not rapport["questions_touchées"]:
        print("   Aucune correction nécessaire.")
    else:
        print(f"   Questions nettoyees   : {rapport['questions_nettoyées']}")
        print(f"   Doublons retirés      : {rapport['doublons_retirés']}")

    # Sauvegarder le dataset mis à jour (4 champs requis par Ragas uniquement)
    output = {"data": updated_items}

    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Dataset sauvegardé : {dataset_path.name}")
    print(f"     {len(updated_items)} questions, {RETRIEVER_K} contextes par question")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" GÉNÉRATION DU DATASET DE TEST RAGAS ".center(70, "="))
    print("=" * 70)

    regenerate_dataset(DATASET_PATH)

    print("\n" + "=" * 70)
    print("TERMINÉ".center(70))
    print("=" * 70)
