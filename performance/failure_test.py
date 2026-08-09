import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "failure_test_report.json"
)


def unavailable_model_response():

    return {
        "status": "degraded",
        "recommendation_available": False,
        "error_code": "MODEL_UNAVAILABLE",
        "message": (
            "Recommendation model is temporarily "
            "unavailable. Please retry later."
        ),
        "fallback": "safe_response"
    }


if __name__ == "__main__":

    result = unavailable_model_response()

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print()
    print("Model Unavailable Failure Test")
    print("==============================")

    print(
        "Status:",
        result["status"]
    )

    print(
        "Recommendation Available:",
        result[
            "recommendation_available"
        ]
    )

    print(
        "Error Code:",
        result["error_code"]
    )

    print(
        "Fallback:",
        result["fallback"]
    )