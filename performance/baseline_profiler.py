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
    "baseline_report.json"
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


def load_real_logs():

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return list(
            csv.DictReader(file)
        )


def profile():

    rows = load_real_logs()

    if not rows:

        raise RuntimeError(
            "No production prediction logs found."
        )

    latencies = [
        float(row["latency_ms"])
        for row in rows
        if row.get("latency_ms")
    ]

    scores = [
        float(row["predicted_score"])
        for row in rows
        if row.get("predicted_score")
    ]

    start = time.perf_counter()

    # Baseline processing path:
    # parse + validate + score aggregation
    processed = []

    for row in rows:

        score = float(
            row["predicted_score"]
        )

        processed.append({
            "student_id":
                row["student_id"],

            "job_id":
                row["job_id"],

            "score":
                score
        })

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    successful = sum(
        1
        for row in rows
        if row.get("prediction_status")
        == "success"
    )

    success_rate = (
        successful / len(rows)
    ) * 100

    report = {

        "profile_type":
            "baseline",

        "data_source":
            "real production-style prediction logs",

        "total_requests":
            len(rows),

        "successful_requests":
            successful,

        "success_rate_percent":
            round(success_rate, 2),

        "logged_latency": {

            "average_ms":
                round(
                    statistics.mean(latencies),
                    4
                ),

            "p95_ms":
                round(
                    percentile(latencies, 95),
                    4
                ),

            "minimum_ms":
                min(latencies),

            "maximum_ms":
                max(latencies)
        },

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

        "baseline_processing_time_ms":
            round(elapsed, 4),

        "records_processed":
            len(processed)
    }

    os.makedirs(
        os.path.dirname(REPORT_FILE),
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
            indent=4
        )

    return report


if __name__ == "__main__":

    result = profile()

    print()
    print("Baseline Performance Profile")
    print("=============================")

    print(
        "Requests:",
        result["total_requests"]
    )

    print(
        "Success Rate:",
        result["success_rate_percent"],
        "%"
    )

    print(
        "Logged Average Latency:",
        result["logged_latency"]["average_ms"],
        "ms"
    )

    print(
        "Logged P95 Latency:",
        result["logged_latency"]["p95_ms"],
        "ms"
    )

    print(
        "Baseline Processing Time:",
        result[
            "baseline_processing_time_ms"
        ],
        "ms"
    )

    print(
        "Average Prediction Score:",
        result[
            "prediction_quality"
        ]["average_score"]
    )