"""
Exercice 2 : Comparaison d'embeddings et visualisation

- Compare Mistral embeddings, Sentence-BERT et FastText
- Calcule la similarité cosinus entre documents
- Visualise les embeddings en 2D (PCA)
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()


def load_texts(input_dir: Path, max_docs: int, min_chars: int) -> Tuple[List[str], List[str]]:
    md_files = sorted(p for p in input_dir.rglob("*.md") if p.is_file())
    texts = []
    labels = []

    for path in md_files:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception:
            continue

        if len(content) < min_chars:
            continue

        texts.append(content)
        labels.append(path.stem)

        if max_docs and len(texts) >= max_docs:
            break

    return texts, labels


def embed_with_mistral(texts: List[str]) -> Optional[np.ndarray]:
    api_key = os.environ.get("MISTRAL_API_KEY")  # MISTRAL_API_KEY
    if not api_key:
        print("Mistral: variable MISTRAL_API_KEY absente, embeddings ignorés.")
        return None

    try:
        from mistralai import Mistral
    except Exception as exc:
        print(f"Mistral: package 'mistralai' indisponible ({exc}).")
        return None

    try:
        client = Mistral(api_key=api_key)
        response = client.embeddings.create(
            model="mistral-embed",
            inputs=texts,
        )
        vectors = [item.embedding for item in response.data]
        return np.array(vectors, dtype=np.float32)
    except Exception as exc:
        print(f"Mistral: erreur lors du calcul des embeddings ({exc}).")
        return None


def embed_with_sentence_bert(texts: List[str], model_name: str) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, normalize_embeddings=True)
    return np.array(vectors, dtype=np.float32)


def tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)


def embed_with_fasttext(texts: List[str], model_name: str) -> np.ndarray:
    import gensim.downloader as api

    print("FastText: téléchargement/chargement du modèle, cela peut être long...")
    ft_model = api.load(model_name)

    vectors = []
    for text in texts:
        tokens = tokenize(text)
        token_vectors = [ft_model[word] for word in tokens if word in ft_model]
        if token_vectors:
            vec = np.mean(token_vectors, axis=0)
        else:
            vec = np.zeros(ft_model.vector_size, dtype=np.float32)
        vectors.append(vec)

    vectors = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms


def save_similarity_matrix(
    vectors: np.ndarray,
    labels: List[str],
    output_path: Path,
) -> None:
    sim = cosine_similarity(vectors)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["document"] + labels)
        for label, row in zip(labels, sim):
            writer.writerow([label] + [f"{value:.4f}" for value in row])


def plot_embeddings(
    vectors: np.ndarray,
    labels: List[str],
    output_path: Path,
    title: str,
    random_state: int,
) -> None:
    reducer = PCA(n_components=2, random_state=random_state)
    coords = reducer.fit_transform(vectors)

    plt.figure(figsize=(10, 7))
    plt.scatter(coords[:, 0], coords[:, 1], alpha=0.8)

    for x, y, label in zip(coords[:, 0], coords[:, 1], labels):
        plt.annotate(label, (x, y), fontsize=8, alpha=0.9)

    plt.title(title)
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare les embeddings de documents municipaux et visualise leur distribution."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("sources/convert"),
        help="Répertoire des fichiers Markdown convertis",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Répertoire de sortie pour les graphiques et matrices",
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        default=25,
        help="Nombre maximum de documents à comparer",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=200,
        help="Nombre minimum de caractères pour retenir un document",
    )
    parser.add_argument(
        "--sbert-model",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Modèle Sentence-BERT",
    )
    parser.add_argument(
        "--fasttext-model",
        type=str,
        default="fasttext-wiki-news-subwords-300",
        help="Modèle FastText pour gensim",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Graine aléatoire pour la réduction PCA",
    )

    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(
            f"Répertoire introuvable: {args.input_dir}. Exécutez d'abord convert_documents.py"
        )

    texts, labels = load_texts(args.input_dir, args.max_docs, args.min_chars)
    if not texts:
        raise ValueError("Aucun document valide trouvé dans le dossier convert.")

    print(f"Documents sélectionnés : {len(texts)}")

    results = []

    mistral_vectors = embed_with_mistral(texts)
    if mistral_vectors is not None:
        results.append(("mistral", mistral_vectors))

    sbert_vectors = embed_with_sentence_bert(texts, args.sbert_model)
    results.append(("sbert", sbert_vectors))

    fasttext_vectors = embed_with_fasttext(texts, args.fasttext_model)
    results.append(("fasttext", fasttext_vectors))

    for name, vectors in results:
        print(f"\n==> {name.upper()} : calcul des similarités et visualisation")
        sim_path = args.output_dir / f"similarity_{name}.csv"
        plot_path = args.output_dir / f"embeddings_{name}.png"

        save_similarity_matrix(vectors, labels, sim_path)
        plot_embeddings(vectors, labels, plot_path, f"Embeddings - {name}", args.seed)

        print(f"Matrice de similarité : {sim_path}")
        print(f"Graphique : {plot_path}")


if __name__ == "__main__":
    main()
