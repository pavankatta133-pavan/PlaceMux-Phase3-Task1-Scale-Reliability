"""
Phase 3 Task 13
Semantic Search - Keyword Search
"""

import json
import os
import re


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DOCUMENT_FILE = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "data",
    "search_documents.json"
)


def load_documents():

    with open(
        DOCUMENT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def tokenize(text):

    return re.findall(
        r"\b\w+\b",
        text.lower()
    )


class KeywordSearch:

    def __init__(self):

        self.documents = load_documents()

    def search(self, query, top_k=5):

        query_tokens = tokenize(
            query
        )

        results = []

        for document in self.documents:

            document_tokens = tokenize(
                document["text"]
            )

            matches = sum(
                1
                for token in query_tokens
                if token in document_tokens
            )

            score = matches / max(
                len(query_tokens),
                1
            )

            results.append({
                "document_id": document["document_id"],
                "job_id": document["job_id"],
                "title": document["title"],
                "score": float(score),
                "text": document["text"]
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]


def main():

    print(
        "\n========== TASK 13 KEYWORD SEARCH =========="
    )

    search_engine = KeywordSearch()

    print(
        "Documents loaded:",
        len(search_engine.documents)
    )

    query = "Python FastAPI backend SQL"

    print(
        "\nTest query:",
        query
    )

    results = search_engine.search(
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
            "Keyword search returned no results."
        )

    print(
        "\nTASK 13 KEYWORD SEARCH: PASS"
    )


if __name__ == "__main__":
    main()