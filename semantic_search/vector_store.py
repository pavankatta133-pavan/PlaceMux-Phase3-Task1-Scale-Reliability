"""
Phase 3 Task 13
Semantic Search - Vector Store
"""

import json
import os

import numpy as np
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "data"
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "models"
)

DOCUMENT_FILE = os.path.join(
    DATA_DIR,
    "search_documents.json"
)

EMBEDDINGS_FILE = os.path.join(
    MODEL_DIR,
    "document_embeddings.npy"
)

METADATA_FILE = os.path.join(
    MODEL_DIR,
    "embedding_metadata.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def load_documents():
    with open(
        DOCUMENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_embeddings():
    return np.load(EMBEDDINGS_FILE)


def load_metadata():
    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


class VectorStore:

    def __init__(self):
        self.documents = load_documents()
        self.embeddings = load_embeddings()
        self.metadata = load_metadata()

        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def search(self, query, top_k=5):

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = np.dot(
            self.embeddings,
            query_embedding
        )

        ranked_indices = np.argsort(
            scores
        )[::-1]

        results = []

        for index in ranked_indices[:top_k]:

            document = self.documents[index]

            results.append({
                "document_id": document["document_id"],
                "job_id": document["job_id"],
                "title": document["title"],
                "score": float(scores[index]),
                "text": document["text"]
            })

        return results


def main():

    print(
        "\n========== TASK 13 VECTOR STORE =========="
    )

    store = VectorStore()

    print(
        "Documents loaded:",
        len(store.documents)
    )

    print(
        "Embedding shape:",
        store.embeddings.shape
    )

    query = "Python backend developer with FastAPI"

    print(
        "\nTest query:",
        query
    )

    results = store.search(
        query,
        top_k=3
    )

    print(
        "\nTop results:"
    )

    for rank, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{rank}. "
            f"{result['job_id']} - "
            f"{result['title']} "
            f"(score={result['score']:.4f})"
        )

    if not results:
        raise RuntimeError(
            "Vector search returned no results."
        )

    print(
        "\nTASK 13 VECTOR STORE: PASS"
    )


if __name__ == "__main__":
    main()