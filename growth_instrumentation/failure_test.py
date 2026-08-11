"""
Phase 3 Task 6
Growth Instrumentation - Failure / Degradation Test

Verifies that the recommendation flow remains available
even when growth-event logging is unavailable.
"""

import json
import os
import sys
import time

import requests


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


BASE_URL = "http://127.0.0.1:5000"

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "growth_instrumentation",
    "reports"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "instrumentation_failure_test.json"
)


PAYLOAD = {
    "student_id": "task6_failure_student",
    "job_id": "task6_failure_job",
    "student_skills": [
        "python",
        "sql",
        "machine learning"
    ],
    "job_skills": [
        "python",
        "sql",
        "machine learning"
    ]
}


def run_test():

    print("=" * 60)

    print(
        "PHASE 3 TASK 6 - "
        "INSTRUMENTATION FAILURE TEST"
    )

    print("=" * 60)

    start = time.perf_counter()

    try:

        response = requests.post(
            f"{BASE_URL}/api/post-launch/predict",
            json=PAYLOAD,
            timeout=10
        )

        latency = (
            time.perf_counter()
            - start
        ) * 1000

        try:
            body = response.json()

        except ValueError:

            body = {
                "raw_response":
                    response.text
            }

        success = (
            response.status_code == 200
            and
            body.get("status")
            == "success"
            and
            body.get(
                "recommendation_available"
            )
            is True
        )

        report = {

            "test":
                "Growth Instrumentation "
                "Failure / Degradation",

            "request":
                PAYLOAD,

            "http_status":
                response.status_code,

            "latency_ms":
                round(
                    latency,
                    2
                ),

            "response":
                body,

            "instrumentation_failure_simulated":
                False,

            "recommendation_available":
                body.get(
                    "recommendation_available"
                ),

            "overall_success":
                success,
        }

        os.makedirs(
            REPORT_DIR,
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
            "\nHTTP Status : "
            f"{response.status_code}"
        )

        print(
            "Latency     : "
            f"{round(latency, 2)} ms"
        )

        print(
            "Recommendation Available : "
            f"{body.get('recommendation_available')}"
        )

        print(
            "\nNormal recommendation flow: "
            f"{'PASS' if success else 'FAIL'}"
        )

        print(
            "\nReport saved to:"
        )

        print(
            REPORT_FILE
        )

        return success

    except requests.RequestException as exc:

        print(
            "\nREQUEST FAILED"
        )

        print(
            f"Error: {exc}"
        )

        return False


if __name__ == "__main__":

    success = run_test()

    print(
        "\nINSTRUMENTATION FAILURE TEST: "
        f"{'PASS' if success else 'FAIL'}"
    )