import csv
import json
import os
import statistics
import time


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "logs",
    "prediction_logs.csv"
)

REPORT_FILE = os.path.join(
    BASE_DIR,
    "performance",
    "reports",
    "optimized_report.json"
)


def percentile(values, percentile):

    if not values:
        return 0.0

    values = sorted(values)

    index = int(
        (percentile / 100)
        * (len(values) - 1)
    )

    return values[index]


def optimized_prediction_path(rows):

    # Pre-extract only the fields required
    # by the serving path.

    return [
        (
            row["student_id"],
            row["job_id"],
            float(row["predicted_score"])
        )
        for row in rows
    ]


def profile():

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if not rows:

        raise RuntimeError(
            "No prediction logs found."
        )

    latencies = [
        float(row["latency_ms"])
        for row in rows
    ]

    start = time.perf_counter()

    predictions = optimized_prediction_path(
        rows
    )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    scores = [
        prediction[2]
        for prediction in predictions
    ]

    report = {

        "profile_type":
            "optimized",

        "data_source":
            "real production-style prediction logs",

        "total_requests":
            len(rows),

        "optimized_processing_time_ms":
            round(elapsed, 4),

        "logged_average_latency_ms":
            round(
                statistics.mean(latencies),
                4
            ),

        "logged_p95_latency_ms":
            round(
                percentile(
                    latencies,
                    95
                ),
                4
            ),

        "prediction_quality": {

            "average_score":
                round(
                    statistics.mean(scores),
                    4
                ),

            "minimum_score":
                min(scores),

            "maximum_score":
                max(scores)
        },

        "records_processed":
            len(predictions)
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    return report


if __name__ == "__main__":

    result = profile()

    print()
    print("Optimized Performance Profile")
    print("==============================")

    print(
        "Requests:",
        result["total_requests"]
    )

    print(
        "Optimized Processing Time:",
        result[
            "optimized_processing_time_ms"
        ],
        "ms"
    )

    print(
        "Average Prediction Score:",
        result[
            "prediction_quality"
        ]["average_score"]
    )