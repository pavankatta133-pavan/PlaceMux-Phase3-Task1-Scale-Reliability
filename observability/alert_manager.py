import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CONFIG_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "slo_config.json"
)

SLO_REPORT_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "slo_report.json"
)

ALERT_REPORT_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "reports",
    "alert_report.json"
)

ALERT_LOG_FILE = os.path.join(
    BASE_DIR,
    "observability",
    "logs",
    "observability_alerts.json"
)


def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def check_alerts():

    config = load_json(CONFIG_FILE)

    report = load_json(SLO_REPORT_FILE)

    metrics = report["metrics"]

    thresholds = config["alert_thresholds"]

    alerts = []

    # --------------------------------
    # Latency monitoring
    # --------------------------------

    p95_latency = metrics["p95_latency_ms"]

    if p95_latency >= thresholds["latency_critical_ms"]:

        alerts.append({
            "alert": "HIGH_LATENCY",
            "severity": "CRITICAL",
            "message":
                f"P95 latency {p95_latency} ms "
                f"exceeded critical threshold "
                f"{thresholds['latency_critical_ms']} ms."
        })

    elif p95_latency >= thresholds["latency_warning_ms"]:

        alerts.append({
            "alert": "HIGH_LATENCY",
            "severity": "WARNING",
            "message":
                f"P95 latency {p95_latency} ms "
                f"exceeded warning threshold "
                f"{thresholds['latency_warning_ms']} ms."
        })

    # --------------------------------
    # Availability monitoring
    # --------------------------------

    availability = metrics[
        "availability_percent"
    ]

    if availability < config["slo"][
        "availability_percent"
    ]:

        alerts.append({
            "alert": "AVAILABILITY_BREACH",
            "severity": "CRITICAL",
            "message":
                f"Availability {availability}% "
                f"is below the SLO target."
        })

    # --------------------------------
    # Quality monitoring
    # --------------------------------

    minimum_score = metrics[
        "minimum_score"
    ]

    if minimum_score < thresholds[
        "minimum_quality_score"
    ]:

        alerts.append({
            "alert": "LOW_PREDICTION_QUALITY",
            "severity": "CRITICAL",
            "message":
                f"Minimum prediction score "
                f"{minimum_score} is below the "
                f"quality threshold "
                f"{thresholds['minimum_quality_score']}."
        })

    # --------------------------------
    # Score distribution monitoring
    # --------------------------------

    unique_scores = metrics[
        "unique_scores"
    ]

    if unique_scores < thresholds[
        "score_distribution_min_unique"
    ]:

        alerts.append({
            "alert": "LOW_SCORE_DIVERSITY",
            "severity": "CRITICAL",
            "message":
                f"Only {unique_scores} unique "
                f"prediction score(s) detected. "
                "Possible score collapse."
        })

    # --------------------------------
    # Constant score detection
    # --------------------------------

    total_requests = metrics[
        "total_requests"
    ]

    if (
        total_requests >= 3
        and unique_scores == 1
    ):

        alerts.append({
            "alert": "DEGENERATE_SCORE_DISTRIBUTION",
            "severity": "CRITICAL",
            "message":
                "All recent predictions have "
                "the same score. Model output "
                "may be degenerate."
        })

    # --------------------------------
    # Final status
    # --------------------------------

    if alerts:

        overall_status = "ALERT"

    else:

        overall_status = "HEALTHY"

    result = {

        "timestamp":
            datetime.now().isoformat(),

        "model_version":
            config["model_version"],

        "overall_status":
            overall_status,

        "alert_count":
            len(alerts),

        "alerts":
            alerts
    }

    return result


def save_alert_report(result):

    os.makedirs(
        os.path.dirname(ALERT_REPORT_FILE),
        exist_ok=True
    )

    os.makedirs(
        os.path.dirname(ALERT_LOG_FILE),
        exist_ok=True
    )

    with open(
        ALERT_REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    with open(
        ALERT_LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file
        )

        file.write("\n")


if __name__ == "__main__":

    result = check_alerts()

    save_alert_report(result)

    print("\nObservability Alert Report")
    print("==========================")

    print(
        "Overall Status:",
        result["overall_status"]
    )

    print(
        "Alert Count:",
        result["alert_count"]
    )

    for alert in result["alerts"]:

        print(
            f"[{alert['severity']}] "
            f"{alert['alert']}: "
            f"{alert['message']}"
        )