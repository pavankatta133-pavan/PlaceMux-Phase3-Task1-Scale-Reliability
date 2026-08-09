import json
import os
import sys
import time

import requests


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

BASE_URL = "http://127.0.0.1:5000"

PREDICTION_ENDPOINT = (
    f"{BASE_URL}/api/post-launch/predict"
)

TEST_REQUEST = {
    "student_id": "task5_failure_student_001",
    "job_id": "task5_failure_job_001",
    "student_skills": [
        "Python",
        "Machine Learning",
        "SQL"
    ],
    "job_skills": [
        "Python",
        "Machine Learning",
        "SQL"
    ]
}


def main():

    print("=" * 60)
    print("PHASE 3 TASK 5 - FAILURE INJECTION TEST")
    print("=" * 60)

    start = time.perf_counter()

    try:

        response = requests.post(
            PREDICTION_ENDPOINT,
            json=TEST_REQUEST,
            timeout=10
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        try:
            response_data = response.json()
        except ValueError:
            response_data = {}

        print("\nFailure Injection Test")
        print("-------------------------")
        print(
            "HTTP Status :",
            response.status_code
        )
        print(
            "Latency     :",
            round(latency_ms, 2),
            "ms"
        )
        print(
            "Response    :",
            json.dumps(
                response_data,
                indent=4
            )
        )

        # Expected behavior during controlled failure:
        #
        # HTTP 503
        # status = fallback
        # fallback = true
        # recommendation_available = false
        # error_code = SYNTHETIC_MODEL_FAILURE

        failure_injection_pass = (
            response.status_code == 503
            and response_data.get(
                "status"
            ) == "fallback"
            and response_data.get(
                "fallback"
            ) is True
            and response_data.get(
                "recommendation_available"
            ) is False
            and response_data.get(
                "error_code"
            ) == "SYNTHETIC_MODEL_FAILURE"
        )

        report = {

            "task":
                "Phase 3 Task 5",

            "test_type":
                "controlled_failure_injection",

            "http_status":
                response.status_code,

            "latency_ms":
                round(latency_ms, 2),

            "fallback_response":
                response_data,

            "failure_injection_pass":
                failure_injection_pass,

            "interpretation":
                (
                    "Controlled model failure returned "
                    "a safe fallback response without "
                    "making a recommendation."
                )
        }

        report_path = os.path.join(
            PROJECT_ROOT,
            "reliability_signoff",
            "reports",
            "failure_injection_report.json"
        )

        os.makedirs(
            os.path.dirname(report_path),
            exist_ok=True
        )

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print("\nFailure injection report saved to:")
        print(report_path)

        print(
            "\nFAILURE INJECTION TEST:",
            "PASS"
            if failure_injection_pass
            else "FAIL"
        )

        if failure_injection_pass:
            sys.exit(0)
        else:
            sys.exit(1)

    except requests.RequestException as exc:

        print("\nREQUEST FAILED")
        print("Error:", exc)

        sys.exit(1)


if __name__ == "__main__":
    main()