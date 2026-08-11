"""
Phase 3 Task 7
Never-Empty Fallback Test
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)

from cold_start.fallback import (
    fallback_recommendations
)


def main():

    jobs = [
        {
            "job_id": "task7_job_001",
            "title": "AI Engineer",
            "skills": [
                "Python",
                "Machine Learning"
            ],
            "active": True
        },
        {
            "job_id": "task7_job_002",
            "title": "Data Analyst",
            "skills": [
                "SQL",
                "Excel"
            ],
            "active": True
        }
    ]

    recommendations = fallback_recommendations(
        jobs,
        top_k=5
    )

    print(
        "\n========== TASK 7 FALLBACK TEST =========="
    )

    print(
        "Recommendations returned:",
        len(recommendations)
    )

    for recommendation in recommendations:
        print(recommendation)

    if recommendations:

        print(
            "\nFallback Test: PASS"
        )

    else:

        print(
            "\nFallback Test: FAIL"
        )

        raise SystemExit(1)


if __name__ == "__main__":
    main()