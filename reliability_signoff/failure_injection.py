import json
import os
import sys
from datetime import datetime

from fallback import generate_fallback_response


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "reliability_signoff",
    "reports"
)


def simulate_model_failure():
    """
    Deliberately simulate a model/service failure.

    This is a controlled reliability test. It does not modify
    the production prediction endpoint.
    """

    student_id = "task5_failure_student"
    job_id = "task5_failure_job"

    try:
        # Deliberately trigger a controlled failure.
        raise RuntimeError(
            "SYNTHETIC_MODEL_FAILURE"
        )

    except Exception as exc:

        fallback_response = generate_fallback_response(
            student_id=student_id,
            job_id=job_id,
            reason=str(exc)
        )

        return {
            "test": "forced_model_failure",
            "failure_injected": True,
            "failure_type": type(exc).__name__,
            "fallback_activated": (
                fallback_response["status"] == "fallback"
            ),
            "recommendation_available": (
                fallback_response[
                    "recommendation_available"
                ]
            ),
            "fallback_response": fallback_response,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def main():

    print("=" * 60)
    print("PHASE 3 TASK 5 - FAILURE INJECTION TEST")
    print("=" * 60)

    result = simulate_model_failure()

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    report_path = os.path.join(
        REPORT_DIR,
        "failure_injection_report.json"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print("\nFailure injected        :",
          result["failure_injected"])

    print("Fallback activated      :",
          result["fallback_activated"])

    print("Recommendation available:",
          result["recommendation_available"])

    print("\nFallback response:")
    print(
        json.dumps(
            result["fallback_response"],
            indent=4
        )
    )

    print("\nReport saved to:")
    print(report_path)

    if (
        result["failure_injected"]
        and result["fallback_activated"]
        and not result["recommendation_available"]
    ):
        print("\nFAILURE INJECTION TEST: PASS")
    else:
        print("\nFAILURE INJECTION TEST: FAIL")


if __name__ == "__main__":
    main()