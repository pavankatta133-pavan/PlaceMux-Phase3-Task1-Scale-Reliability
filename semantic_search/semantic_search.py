"""
Phase 3 Task 13
Semantic Search
"""

from semantic_search.vector_store import VectorStore


class SemanticSearch:

    def __init__(self):
        self.vector_store = VectorStore()

    def search(self, query, top_k=5):
        return self.vector_store.search(
            query,
            top_k=top_k
        )


def main():

    print(
        "\n========== TASK 13 SEMANTIC SEARCH =========="
    )

    search_engine = SemanticSearch()

    query = "machine learning Python model training"

    print(
        "Test query:",
        query
    )

    results = search_engine.search(
        query,
        top_k=3
    )

    print(
        "\nTop semantic results:"
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
            "Semantic search returned no results."
        )

    print(
        "\nTASK 13 SEMANTIC SEARCH: PASS"
    )


if __name__ == "__main__":
    main()