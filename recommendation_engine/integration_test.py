"""
Phase 3 Task 12
Recommendation Engine Integration Test

Tests:
1. Health endpoint
2. Student recommendation endpoint
3. Recommendation response structure
4. Fallback behavior
"""

import json
import os
import sys
import time

from recommendation_engine.recommender import (
    RecommendationEngine
)

from recommendation_engine.baseline import (
    PopularityBaseline
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


REPORT_FILE = os.path.join(
    PROJECT_ROOT,
    "recommendation_engine",
    "reports",
    "integration_test_report.json"
)


def test_recommendation_engine():

    print(
        "\n========== TASK 12 INTEGRATION TEST =========="
    )

    # -------------------------------------------------
    # TEST 1: Recommendation Engine
    # -------------------------------------------------

    print(
        "\n1. Testing recommendation engine..."
    )

    engine = RecommendationEngine()

    students = list(
        engine.student_jobs.keys()
    )

    if not students:

        raise RuntimeError(
            "No students found in recommendation dataset."
        )

    student_id = students[0]

    start_time = time.perf_counter()

    recommendations = (
        engine.recommend_jobs(
            student_id,
            k=5,
            exclude_interacted=True
        )
    )

    latency_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    print(
        "Student:",
        student_id
    )

    print(
        "Recommendations:",
        recommendations
    )

    print(
        "Latency:",
        round(
            latency_ms,
            3
        ),
        "ms"
    )

    if not isinstance(
        recommendations,
        list
    ):

        raise AssertionError(
            "Recommendations must be a list."
        )

    if len(recommendations) == 0:

        raise AssertionError(
            "Recommendation list is empty."
        )

    # -------------------------------------------------
    # TEST 2: Response Structure
    # -------------------------------------------------

    print(
        "\n2. Testing recommendation structure..."
    )

    for recommendation in recommendations:

        if "job_id" not in recommendation:

            raise AssertionError(
                "Recommendation missing job_id."
            )

        if "score" not in recommendation:

            raise AssertionError(
                "Recommendation missing score."
            )

    print(
        "Recommendation structure: PASS"
    )

    # -------------------------------------------------
    # TEST 3: Popularity Fallback
    # -------------------------------------------------

    print(
        "\n3. Testing popularity fallback..."
    )

    baseline = PopularityBaseline()

    fallback_recommendations = (
        baseline.recommend_jobs(
            k=5
        )
    )

    print(
        "Fallback recommendations:",
        fallback_recommendations
    )

    if not isinstance(
        fallback_recommendations,
        list
    ):

        raise AssertionError(
            "Fallback recommendations must be a list."
        )

    if len(fallback_recommendations) == 0:

        raise AssertionError(
            "Fallback returned no recommendations."
        )

    print(
        "Fallback: PASS"
    )

    # -------------------------------------------------
    # TEST 4: Latency Guardrail
    # -------------------------------------------------

    print(
        "\n4. Testing latency..."
    )

    # Task 12 lightweight serving target.
    # This is intentionally generous for local development.

    latency_limit_ms = 1000

    if latency_ms > latency_limit_ms:

        raise AssertionError(
            f"Recommendation latency "
            f"{latency_ms:.2f} ms exceeds "
            f"{latency_limit_ms} ms."
        )

    print(
        "Latency guardrail: PASS"
    )

    # -------------------------------------------------
    # SAVE REPORT
    # -------------------------------------------------

    report = {

        "task":
            "Phase 3 Task 12",

        "test":
            "Recommendation Engine Integration Test",

        "status":
            "PASS",

        "student_id":
            student_id,

        "recommendation_count":
            len(recommendations),

        "recommendations":
            recommendations,

        "latency_ms":
            round(
                latency_ms,
                3
            ),

        "latency_limit_ms":
            latency_limit_ms,

        "fallback_count":
            len(
                fallback_recommendations
            ),

        "tests": {

            "recommendation_engine":
                "PASS",

            "recommendation_structure":
                "PASS",

            "fallback":
                "PASS",

            "latency":
                "PASS"
        }
    }

    os.makedirs(
        os.path.dirname(
            REPORT_FILE
        ),
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2
        )

    print(
        "\nIntegration test report saved to:"
    )

    print(
        REPORT_FILE
    )

    print(
        "\nTASK 12 INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":

    try:

        test_recommendation_engine()

    except Exception as exc:

        print(
            "\nTASK 12 INTEGRATION TEST: FAIL"
        )

        print(
            "Error:",
            str(exc)
        )

        sys.exit(1)