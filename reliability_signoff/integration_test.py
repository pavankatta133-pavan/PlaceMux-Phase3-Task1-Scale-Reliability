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

EXPLANATION_ENDPOINT = (
    f"{BASE_URL}/api/post-launch/explanation"
)


TEST_REQUEST = {
    "student_id": "task5_student_001",
    "job_id": "task5_job_001",
    "student_skills": [
        "Python",
        "Machine Learning",
        "SQL",
        "TensorFlow"
    ],
    "job_skills": [
        "Python",
        "Machine Learning",
        "SQL"
    ]
}


def test_prediction():

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
            response_data = {
                "raw_response": response.text
            }

        print("\nPrediction Test")
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

        # Normal prediction must return HTTP 200
        successful = (
            response.status_code == 200
            and response_data.get("status") == "success"
            and response_data.get(
                "recommendation_available"
            ) is True
        )

        return {
            "status_code": response.status_code,
            "latency_ms": round(
                latency_ms,
                2
            ),
            "successful": successful,
            "response": response_data
        }

    except requests.RequestException as exc:

        print("\nPrediction request failed:")
        print(exc)

        return {
            "status_code": None,
            "latency_ms": None,
            "successful": False,
            "response": {
                "error": str(exc)
            }
        }


def test_explanation():

    try:

        response = requests.post(
            EXPLANATION_ENDPOINT,
            json=TEST_REQUEST,
            timeout=10
        )

        try:
            response_data = response.json()
        except ValueError:
            response_data = {
                "raw_response": response.text
            }

        print("\nExplanation Test")
        print("-------------------------")
        print(
            "HTTP Status :",
            response.status_code
        )
        print(
            "Response    :",
            json.dumps(
                response_data,
                indent=4
            )
        )

        successful = (
    response.status_code == 200
    and response_data.get("status") == "success"
)

        return {
            "status_code": response.status_code,
            "successful": successful,
            "response": response_data
        }

    except requests.RequestException as exc:

        print("\nExplanation request failed:")
        print(exc)

        return {
            "status_code": None,
            "successful": False,
            "response": {
                "error": str(exc)
            }
        }


def main():

    print("=" * 60)
    print(
        "PHASE 3 TASK 5 - NORMAL INTEGRATION TEST"
    )
    print("=" * 60)

    prediction = test_prediction()

    explanation = test_explanation()

    overall_success = (
        prediction["successful"]
        and explanation["successful"]
    )

    report = {

        "task":
            "Phase 3 Task 5",

        "test_type":
            "normal_integration",

        "normal_prediction":
            prediction,

        "explanation":
            explanation,

        "overall_success":
            overall_success
    }

    report_path = os.path.join(
        PROJECT_ROOT,
        "reliability_signoff",
        "reports",
        "integration_test_report.json"
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

    print("\nIntegration report saved to:")
    print(report_path)

    print("\nNormal Prediction:",
          "PASS" if prediction["successful"]
          else "FAIL")

    print("Explanation:",
          "PASS" if explanation["successful"]
          else "FAIL")

    print(
        "\nNORMAL INTEGRATION TEST:",
        "PASS" if overall_success
        else "FAIL"
    )


if __name__ == "__main__":
    main()