"""
Phase 3 Task 13
Semantic Search - Integration Test
"""

import json
import os
import urllib.request


BASE_URL = "http://127.0.0.1:8000"


def get_health():

    request = urllib.request.Request(
        f"{BASE_URL}/health",
        method="GET"
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def search(query, top_k=3):

    payload = json.dumps({
        "query": query,
        "top_k": top_k
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{BASE_URL}/search",
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=10
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def main():

    print(
        "\n========== TASK 13 INTEGRATION TEST =========="
    )

    health = get_health()

    print(
        "Health response:",
        health
    )

    if health.get("status") != "ok":

        raise RuntimeError(
            "Health check failed."
        )

    test_queries = [
        "Python backend developer FastAPI",
        "machine learning model training",
        "data analysis SQL Pandas"
    ]

    for query in test_queries:

        result = search(
            query,
            top_k=3
        )

        print(
            f"\nQuery: {query}"
        )

        print(
            "Result count:",
            result["count"]
        )

        for rank, item in enumerate(
            result["results"],
            start=1
        ):

            print(
                f"{rank}. "
                f"{item['job_id']} - "
                f"{item['title']} "
                f"(score={item['score']:.4f})"
            )

        if result["count"] == 0:

            raise RuntimeError(
                f"No results returned for: {query}"
            )

    print(
        "\nTASK 13 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()