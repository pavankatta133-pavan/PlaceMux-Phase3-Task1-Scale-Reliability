import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

BASELINE_REPORT = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "baseline_report.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "bottleneck_report.json"
)


def analyze():

    with open(
        BASELINE_REPORT,
        "r",
        encoding="utf-8"
    ) as file:

        baseline = json.load(file)

    logged_average = baseline[
        "logged_latency"
    ]["average_ms"]

    logged_p95 = baseline[
        "logged_latency"
    ]["p95_ms"]

    processing_time = baseline[
        "baseline_processing_time_ms"
    ]

    if processing_time > logged_average:
        bottleneck = "Inference processing"
    else:
        bottleneck = "Prediction serving latency"

    report = {

        "analysis": "Baseline bottleneck analysis",

        "baseline": {
            "average_latency_ms":
                logged_average,

            "p95_latency_ms":
                logged_p95,

            "processing_time_ms":
                processing_time
        },

        "identified_bottleneck":
            bottleneck,

        "optimization_strategy": [
            "Reduce unnecessary repeated processing",
            "Use efficient in-memory data structures",
            "Avoid unnecessary file operations in the request path",
            "Keep prediction output format unchanged",
            "Validate optimized latency against baseline"
        ],

        "quality_constraint": {
            "average_prediction_score":
                baseline[
                    "prediction_quality"
                ]["average_score"],

            "minimum_prediction_score":
                baseline[
                    "prediction_quality"
                ]["minimum_score"],

            "maximum_prediction_score":
                baseline[
                    "prediction_quality"
                ]["maximum_score"]
        }
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print()
    print("Bottleneck Analysis")
    print("===================")

    print(
        "Identified Bottleneck:",
        bottleneck
    )

    print(
        "Baseline Average:",
        logged_average,
        "ms"
    )

    print(
        "Baseline P95:",
        logged_p95,
        "ms"
    )

    print(
        "Processing Time:",
        processing_time,
        "ms"
    )


if __name__ == "__main__":
    analyze()