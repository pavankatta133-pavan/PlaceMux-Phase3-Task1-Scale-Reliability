import csv
import json
import math
import os
from statistics import mean


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(
    BASE_DIR,
    "post_launch_health",
    "logs",
    "prediction_logs.csv"
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "slo_config.json"
)

REPORT_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "slo_report.json"
)


def load_config():

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def load_logs():

    if not os.path.exists(LOG_FILE):
        return []

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return list(csv.DictReader(file))


def percentile(values, percentile_value):

    if not values:
        return 0.0

    values = sorted(values)

    position = (
        percentile_value / 100
    ) * (len(values) - 1)

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return float(values[int(position)])

    weight = position - lower

    return (
        values[lower]
        +
        (
            values[upper]
            -
            values[lower]
        )
        * weight
    )


def calculate_metrics(logs):

    total = len(logs)

    if total == 0:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "availability_percent": 0.0,
            "p95_latency_ms": 0.0,
            "average_latency_ms": 0.0,
            "average_score": 0.0,
            "minimum_score": 0.0,
            "maximum_score": 0.0,
            "unique_scores": 0
        }

    successful = [
        row
        for row in logs
        if row.get("prediction_status") == "success"
    ]

    latencies = [
        float(row["latency_ms"])
        for row in successful
        if row.get("latency_ms")
    ]

    scores = [
        float(row["predicted_score"])
        for row in successful
        if row.get("predicted_score")
    ]

    availability = (
        len(successful) / total
    ) * 100

    return {
        "total_requests": total,
        "successful_requests": len(successful),
        "availability_percent": round(
            availability,
            2
        ),
        "p95_latency_ms": round(
            percentile(latencies, 95),
            2
        ),
        "average_latency_ms": round(
            mean(latencies),
            2
        ) if latencies else 0.0,
        "average_score": round(
            mean(scores),
            2
        ) if scores else 0.0,
        "minimum_score": round(
            min(scores),
            2
        ) if scores else 0.0,
        "maximum_score": round(
            max(scores),
            2
        ) if scores else 0.0,
        "unique_scores": len(
            set(scores)
        )
    }


def evaluate_slos(metrics, config):

    slo = config["slo"]

    latency_pass = (
        metrics["p95_latency_ms"]
        <= slo["p95_latency_ms"]
    )

    availability_pass = (
        metrics["availability_percent"]
        >= slo["availability_percent"]
    )

    quality_pass = (
        metrics["minimum_score"]
        >= slo["minimum_quality_score"]
    )

    return {
        "latency_slo": {
            "target_ms": slo["p95_latency_ms"],
            "actual_p95_ms":
                metrics["p95_latency_ms"],
            "status":
                "PASS" if latency_pass else "BREACH"
        },

        "availability_slo": {
            "target_percent":
                slo["availability_percent"],
            "actual_percent":
                metrics["availability_percent"],
            "status":
                "PASS"
                if availability_pass
                else "BREACH"
        },

        "quality_slo": {
            "minimum_score":
                slo["minimum_quality_score"],
            "observed_minimum":
                metrics["minimum_score"],
            "status":
                "PASS"
                if quality_pass
                else "BREACH"
        }
    }


def generate_report():

    config = load_config()

    logs = load_logs()

    metrics = calculate_metrics(logs)

    slo_results = evaluate_slos(
        metrics,
        config
    )

    report = {
        "service":
            config["service"],

        "model_version":
            config["model_version"],

        "metrics":
            metrics,

        "slo_results":
            slo_results,

        "overall_status":
            (
                "HEALTHY"
                if all(
                    item["status"] == "PASS"
                    for item in slo_results.values()
                )
                else "SLO_BREACH"
            )
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

    report = generate_report()

    print("\nObservability SLO Report")
    print("========================")

    print(
        "Total Requests:",
        report["metrics"]["total_requests"]
    )

    print(
        "Availability:",
        report["metrics"]["availability_percent"],
        "%"
    )

    print(
        "P95 Latency:",
        report["metrics"]["p95_latency_ms"],
        "ms"
    )

    print(
        "Average Score:",
        report["metrics"]["average_score"]
    )

    print(
        "Minimum Score:",
        report["metrics"]["minimum_score"]
    )

    print(
        "Unique Scores:",
        report["metrics"]["unique_scores"]
    )

    print(
        "Overall Status:",
        report["overall_status"]
    )