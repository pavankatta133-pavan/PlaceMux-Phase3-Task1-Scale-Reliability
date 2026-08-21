"""
Phase 3 Task 13
Semantic Search - Evaluation
"""

import json
import os

from semantic_search.keyword_search import KeywordSearch
from semantic_search.semantic_search import SemanticSearch
from semantic_search.hybrid_search import HybridSearch


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

QUERY_FILE = os.path.join(
    PROJECT_ROOT,
    "semantic_search",
    "data",
    "search_queries.json"
)


def load_queries():

    with open(
        QUERY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def precision_at_k(results, relevant_ids, k):

    returned_ids = [
        result["job_id"]
        for result in results[:k]
    ]

    relevant_count = sum(
        1
        for job_id in returned_ids
        if job_id in relevant_ids
    )

    return relevant_count / k


def recall_at_k(results, relevant_ids, k):

    returned_ids = [
        result["job_id"]
        for result in results[:k]
    ]

    relevant_count = sum(
        1
        for job_id in returned_ids
        if job_id in relevant_ids
    )

    if not relevant_ids:
        return 0.0

    return relevant_count / len(relevant_ids)


def evaluate_search(search_engine, queries, name):

    precision_scores = []
    recall_scores = []

    print(
        f"\n--- {name} ---"
    )

    for query_data in queries:

        query = query_data["query"]
        relevant_ids = query_data["relevant_job_ids"]

        results = search_engine.search(
            query,
            top_k=3
        )

        precision = precision_at_k(
            results,
            relevant_ids,
            3
        )

        recall = recall_at_k(
            results,
            relevant_ids,
            3
        )

        precision_scores.append(
            precision
        )

        recall_scores.append(
            recall
        )

        print(
            f"{query_data['query_id']}: "
            f"Precision@3={precision:.4f}, "
            f"Recall@3={recall:.4f}"
        )

    average_precision = (
        sum(precision_scores)
        / len(precision_scores)
    )

    average_recall = (
        sum(recall_scores)
        / len(recall_scores)
    )

    print(
        f"{name} Average Precision@3: "
        f"{average_precision:.4f}"
    )

    print(
        f"{name} Average Recall@3: "
        f"{average_recall:.4f}"
    )

    return {
        "precision_at_3": average_precision,
        "recall_at_3": average_recall
    }


def main():

    print(
        "\n========== TASK 13 EVALUATION =========="
    )

    queries = load_queries()

    print(
        "Evaluation queries:",
        len(queries)
    )

    keyword_search = KeywordSearch()
    semantic_search = SemanticSearch()
    hybrid_search = HybridSearch()

    keyword_metrics = evaluate_search(
        keyword_search,
        queries,
        "Keyword Search"
    )

    semantic_metrics = evaluate_search(
        semantic_search,
        queries,
        "Semantic Search"
    )

    hybrid_metrics = evaluate_search(
        hybrid_search,
        queries,
        "Hybrid Search"
    )

    report = {
        "query_count": len(queries),
        "keyword_search": keyword_metrics,
        "semantic_search": semantic_metrics,
        "hybrid_search": hybrid_metrics
    }

    report_dir = os.path.join(
        PROJECT_ROOT,
        "semantic_search",
        "reports"
    )

    os.makedirs(
        report_dir,
        exist_ok=True
    )

    report_file = os.path.join(
        report_dir,
        "evaluation_report.json"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    print(
        "\nEvaluation report saved to:"
    )

    print(
        report_file
    )

    print(
        "\nTASK 13 EVALUATION: PASS"
    )


if __name__ == "__main__":
    main()