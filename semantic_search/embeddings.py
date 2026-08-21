"""
Phase 3 Task 13
Semantic Search - Embedding Generation
"""

import json
import os

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "data",
    "search_documents.json"
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "models"
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

    if not os.path.exists(DATA_FILE):

        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def main():

    print(
        "\n========== TASK 13 EMBEDDINGS =========="
    )

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    documents = load_documents()

    print(
        "Documents:",
        len(documents)
    )

    print(
        "Loading model:",
        MODEL_NAME
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        document["text"]
        for document in documents
    ]

    print(
        "Generating embeddings..."
    )

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    print(
        "Embedding shape:",
        embeddings.shape
    )

    import numpy as np

    np.save(
        EMBEDDINGS_FILE,
        embeddings
    )

    metadata = {

        "model_name":
            MODEL_NAME,

        "document_count":
            len(documents),

        "embedding_dimension":
            int(embeddings.shape[1]),

        "document_ids":
            [
                document["document_id"]
                for document in documents
            ],

        "job_ids":
            [
                document["job_id"]
                for document in documents
            ]
    }

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2
        )

    print(
        "\nEmbeddings saved to:"
    )

    print(
        EMBEDDINGS_FILE
    )

    print(
        "Metadata saved to:"
    )

    print(
        METADATA_FILE
    )

    print(
        "\nTASK 13 EMBEDDINGS: PASS"
    )


if __name__ == "__main__":
    main()