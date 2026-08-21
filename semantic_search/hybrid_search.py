"""
Phase 3 Task 13
Semantic Search - Hybrid Search
"""

from semantic_search.keyword_search import KeywordSearch
from semantic_search.semantic_search import SemanticSearch


class HybridSearch:

    def __init__(self):

        self.keyword_search = KeywordSearch()
        self.semantic_search = SemanticSearch()

    def search(
        self,
        query,
        top_k=5,
        keyword_weight=0.4,
        semantic_weight=0.6
    ):

        keyword_results = self.keyword_search.search(
            query,
            top_k=len(
                self.keyword_search.documents
            )
        )

        semantic_results = self.semantic_search.search(
            query,
            top_k=len(
                self.semantic_search.vector_store.documents
            )
        )

        combined = {}

        for result in keyword_results:

            combined[
                result["document_id"]
            ] = {
                **result,
                "keyword_score": result["score"],
                "semantic_score": 0.0
            }

        for result in semantic_results:

            document_id = result["document_id"]

            if document_id not in combined:

                combined[document_id] = {
                    **result,
                    "keyword_score": 0.0,
                    "semantic_score": result["score"]
                }

            else:

                combined[
                    document_id
                ]["semantic_score"] = result["score"]

        results = []

        for result in combined.values():

            hybrid_score = (
                keyword_weight
                * result["keyword_score"]
                +
                semantic_weight
                * result["semantic_score"]
            )

            result["score"] = float(
                hybrid_score
            )

            results.append(result)

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]


def main():

    print(
        "\n========== TASK 13 HYBRID SEARCH =========="
    )

    search_engine = HybridSearch()

    query = "Python backend developer FastAPI"

    print(
        "Test query:",
        query
    )

    results = search_engine.search(
        query,
        top_k=3
    )

    print(
        "\nTop hybrid results:"
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"{rank}. "
            f"{result['job_id']} - "
            f"{result['title']} "
            f"(hybrid={result['score']:.4f}, "
            f"keyword={result['keyword_score']:.4f}, "
            f"semantic={result['semantic_score']:.4f})"
        )

    if not results:

        raise RuntimeError(
            "Hybrid search returned no results."
        )

    print(
        "\nTASK 13 HYBRID SEARCH: PASS"
    )


if __name__ == "__main__":
    main()